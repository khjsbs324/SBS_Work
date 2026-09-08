#!/usr/bin/env python3
"""Local NCS checks and arithmetic. Python 3.11+, standard library only.

All commands except `run` are read-only. `run` delegates an explicit request to
Codex and checks this workspace before and after the CLI exits.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = {"ncs-exam-production", "ncs-timetable", "student-interview"}
DATA_DIRS = {"채점 자료", "채점 완료", "학생_제출_산출물", "문제 코드", "정답", ".검증", ".harness-cache"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, f"{label}: integer >= {minimum} required")
    return value


def label(value, field):
    require(isinstance(value, str) and bool(value.strip()), f"{field}: nonempty string required")
    return value


def read_text(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    require("\ufffd" not in text, f"{path.name}: replacement character in text")
    return text


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path):
    return json.loads(read_text(path), object_pairs_hook=unique_object)


def inside(base, relative):
    """Resolve links/metadata paths without reading outside the selected root."""
    base = base.resolve()
    target = (base / relative).resolve()
    require(target.is_relative_to(base), f"Path escapes its root: {relative}")
    return target


def calculate_scores(data):
    require(isinstance(data, dict), "Score input must be an object")
    rows = data.get("rows")
    require(isinstance(rows, list) and bool(rows), "rows must be a nonempty list")
    ids, maxima, raw = [], [], []
    for row in rows:
        require(isinstance(row, dict), "Each score row must be an object")
        ident = label(row.get("id"), "row.id")
        require(ident not in ids, f"Duplicate score ID: {ident}")
        maximum = integer(row.get("max"), f"{ident}.max", 1)
        score = integer(row.get("raw"), f"{ident}.raw")
        require(score <= maximum, f"{ident}: raw exceeds max")
        ids.append(ident)
        maxima.append(maximum)
        raw.append(score)
    require(sum(maxima) == 100, "Common conversion requires max total 100")
    # Integer tenths avoid floating-point rounding and Python's ties-to-even round.
    target = (600 + 4 * sum(raw) + 5) // 10
    numerators = [6 * maximum + 4 * score for maximum, score in zip(maxima, raw)]
    registered = [number // 10 for number in numerators]
    order = sorted(range(len(rows)), key=lambda i: (-(numerators[i] % 10), i))
    for index in order[:target - sum(registered)]:
        registered[index] += 1
    return {
        "rawTotal": sum(raw), "registeredTotal": target,
        "rows": [{"id": ident, "max": maximum, "raw": score, "registered": result}
                 for ident, maximum, score, result in zip(ids, maxima, raw, registered)],
    }


def allocate_timetable(data):
    require(isinstance(data, dict), "Timetable input must be an object")
    tracks, totals = data.get("tracks"), data.get("unit_totals")
    require(isinstance(tracks, list) and bool(tracks), "tracks must be a nonempty list")
    require(isinstance(totals, dict) and bool(totals), "unit_totals must be a nonempty object")
    for ident, hours in totals.items():
        label(ident, "unit_totals ID")
        integer(hours, f"{ident}.total", 1)
    actual, seen_tracks, output = Counter(), set(), []
    for track in tracks:
        require(isinstance(track, dict), "Each track must be an object")
        track_id = label(track.get("id"), "track.id")
        require(track_id not in seen_tracks, f"Duplicate track: {track_id}")
        seen_tracks.add(track_id)
        slots, units = track.get("slots"), track.get("units")
        require(isinstance(slots, list) and bool(slots), f"{track_id}: slots required")
        require(isinstance(units, list), f"{track_id}: units must be a list")
        slot_ids, unit_ids, queue = set(), set(), []
        for slot in slots:
            require(isinstance(slot, dict), "Each slot must be an object")
            ident = label(slot.get("id"), "slot.id")
            require(ident not in slot_ids, f"{track_id}: duplicate slot {ident}")
            slot_ids.add(ident)
            integer(slot.get("hours"), f"{track_id}/{ident}.hours", 1)
        for unit in units:
            require(isinstance(unit, dict), "Each unit must be an object")
            ident = label(unit.get("id"), "unit.id")
            require(ident not in unit_ids, f"{track_id}: duplicate unit {ident}")
            require(ident in totals, f"Unknown unit: {ident}")
            unit_ids.add(ident)
            hours = integer(unit.get("hours"), f"{ident}.hours", 1)
            actual[ident] += hours
            queue.append([ident, hours])
        require(sum(u[1] for u in queue) <= sum(s["hours"] for s in slots),
                f"{track_id}: required hours exceed capacity")
        cursor, assigned = 0, []
        for slot in slots:
            remaining, allocations = slot["hours"], []
            while remaining and cursor < len(queue):
                ident, pending = queue[cursor]
                hours = min(remaining, pending)
                allocations.append({"id": ident, "hours": hours})
                queue[cursor][1] -= hours
                remaining -= hours
                if queue[cursor][1] == 0:
                    cursor += 1
            assigned.append({"id": slot["id"], "capacity": slot["hours"],
                             "allocations": allocations, "unallocated": remaining})
        output.append({"id": track_id, "slots": assigned})
    require(dict(actual) == totals, "Assigned unit totals differ from confirmed unit_totals")
    return {"tracks": output, "unit_totals": dict(actual)}


def parse_exam(path):
    text = read_text(path)
    pattern = (r"^###\s+([A-Z]{2,8}-\d{2,3})\.\s+([^\n]+?)\s+[—–-]\s+(\d+)점\s*\n"
               r"(.*?)(?=^#{1,3}\s|\Z)")
    matches = list(re.finditer(pattern, text, re.M | re.S))
    headings = re.findall(r"^###\s+([A-Z]{2,8}-\d+)\.", text, re.M)
    require(bool(matches) and len(matches) == len(headings), "Unsupported or malformed Exam headings")
    rows, seen = [], set()
    for match in matches:
        ident, title, weight, body = match.groups()
        maximum = int(weight)
        require(maximum > 0 and ident not in seen, f"Invalid/duplicate item: {ident}")
        seen.add(ident)
        tiers = re.findall(r"^- (\d+)(?:~(\d+))?점:", body, re.M)
        values = []
        previous = maximum + 1
        for low, high in tiers:
            low, high = int(low), int(high or low)
            require(0 <= low <= high <= maximum and high < previous, f"{ident}: tier order/range error")
            values.extend(range(low, high + 1))
            previous = low
        require(len(tiers) == 4 and sorted(values) == list(range(maximum + 1)),
                f"{ident}: four tiers must cover 0..{maximum} exactly once")
        rows.append({"id": ident, "name": title, "max": maximum})
    declared = re.search(r"총점\s*:\s*(\d+)점", text)
    require(declared is not None, "Exam must declare total points")
    require(sum(row["max"] for row in rows) == int(declared[1]), "Exam maximum total mismatch")
    sources = list(path.parent.glob("*수행준거.txt"))
    require(len(sources) == 1, "Exactly one criterion TXT is required")
    source_text = read_text(sources[0])
    source_ids = re.findall(r"^([A-Z]{2,8}-\d{2,3})(?:[ \t]|$)", source_text, re.M)
    require(source_ids == [r["id"] for r in rows], "Criterion TXT IDs/order differ from Exam")
    for match in matches:
        original = re.search(r"^- 원문: (.+)$", match[4], re.M)
        if original:
            source = re.search(r"^" + re.escape(match[1]) + r"[ \t]*\n([^\n]+)", source_text, re.M)
            require(source is not None and source[1].strip() == original[1].strip(),
                    f"{match[1]}: original text differs from criterion TXT")
    return rows


def submission_check(metadata, strict_hashes=False):
    meta = load_json(metadata)
    files = meta.get("files")
    require(isinstance(files, list) and bool(files), "Submission files required")
    warnings, seen = [], set()
    with ExitStack() as stack:
        archive = None
        if meta.get("archive"):
            archive_path = inside(metadata.parent, label(meta["archive"], "archive"))
            with archive_path.open("rb") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
            require(digest == meta.get("archive_sha256"), "Original ZIP checksum mismatch")
            try:
                package = zipfile.ZipFile(archive_path, metadata_encoding="cp949")
            except UnicodeDecodeError:
                package = zipfile.ZipFile(archive_path, metadata_encoding="utf-8")
            archive = stack.enter_context(package)
        for item in files:
            require(isinstance(item, dict), "Submission file entry must be an object")
            target = inside(metadata.parent, label(item.get("filename"), "submission filename"))
            require(target not in seen, "Duplicate submission path")
            seen.add(target)
            expected_size = integer(item.get("bytes"), "submission bytes")
            expected_hash = item.get("sha256")
            require(isinstance(expected_hash, str) and re.fullmatch(r"[a-f0-9]{64}", expected_hash),
                    "Invalid submission SHA-256")
            original = None
            if archive is not None:
                recorded_name = item.get("archive_filename")
                candidates = [info for info in archive.infolist() if
                              (info.filename == recorded_name if recorded_name is not None else
                               unicodedata.normalize("NFC", info.filename) == item["filename"])]
                require(len(candidates) == 1, f"Missing/ambiguous ZIP member: {item['filename']}")
                original = archive.read(candidates[0])
                require(len(original) == expected_size and hashlib.sha256(original).hexdigest() == expected_hash,
                        f"Original ZIP member checksum mismatch: {target.name}")
            blob = target.read_bytes()
            if len(blob) == expected_size and hashlib.sha256(blob).hexdigest() == expected_hash:
                continue
            newline_only = False
            if original is not None and target.suffix.lower() in {".md", ".txt", ".html", ".css", ".js", ".json", ".csv", ".svg"}:
                try:
                    newline_only = (blob.decode("utf-8").replace("\r\n", "\n") ==
                                    original.decode("utf-8").replace("\r\n", "\n"))
                except UnicodeDecodeError:
                    pass
            require(newline_only and not strict_hashes, f"Submission checksum mismatch: {target.name}" +
                    (" (verified ZIP matches; working copy differs only in CRLF/LF)" if newline_only else ""))
            warnings.append(f"{target.name}: working-copy bytes differ in CRLF/LF only; original ZIP and member SHA-256 verified")
    return warnings


def grade_check(path, exam, strict_hashes=False):
    data = load_json(path)
    expected = calculate_scores(data)
    require(data.get("student") == path.parent.name, "Student does not match folder")
    require(data.get("unit") == path.parent.parent.parent.name, "Unit does not match folder")
    require([(r["id"], r["max"]) for r in data["rows"]] == [(r["id"], r["max"]) for r in exam],
            "Grade IDs/maxima differ from selected Exam")
    for field in ("rawTotal", "registeredTotal"):
        integer(data.get(field), field)
        require(data[field] == expected[field], f"{field} mismatch")
    for row, ref in zip(data["rows"], expected["rows"]):
        integer(row.get("registered"), f"{row['id']}.registered")
        require(row["registered"] == ref["registered"], f"{row['id']}: allocation mismatch")
        label(row.get("evidence"), f"{row['id']}.evidence")
        label(row.get("judgement"), f"{row['id']}.judgement")
    metadata = path.with_name("제출물_확인.json")
    if metadata.exists():
        meta = load_json(metadata)
        for field in ("student", "unit", "Sid"):
            require(meta.get(field) == data.get(field), f"Submission {field} mismatch")
        return submission_check(metadata, strict_hashes)
    return []


def markdown_links(path, root):
    text = read_text(path)
    # Fenced examples are not live links/imports.
    text = re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)
    targets = re.findall(r"\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)", text)
    if path.name == "CLAUDE.md":
        targets += re.findall(r"^@(.+)$", text, re.M)
    for target in targets:
        target = target.strip().strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme in {"https", "http", "mailto", "app"} or target.startswith("#"):
            continue
        require(not parsed.scheme and not parsed.netloc, f"Use relative local links: {target}")
        resolved = (path.parent / unquote(parsed.path)).resolve()
        require(resolved.is_relative_to(root.resolve()), f"Link escapes 국비: {target}")
        require(resolved.exists(), f"Missing link/import: {target}")


def skill_metadata(path):
    """Validate this project's intentionally small, single-line YAML frontmatter."""
    text = read_text(path)
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    require(match is not None, "Missing Skill frontmatter")
    metadata = {}
    for line in match[1].splitlines():
        field = re.fullmatch(r"(name|description): ([^\n]+)", line)
        require(field is not None, "Use single-line name/description frontmatter in this harness")
        require(field[1] not in metadata, f"Duplicate Skill field: {field[1]}")
        metadata[field[1]] = field[2]
    name, description = metadata.get("name", ""), metadata.get("description", "")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is not None and len(name) <= 64,
            "Invalid Skill name")
    require(name == path.parent.name, "Skill folder/name mismatch")
    require(0 < len(description) <= 1024 and not any(c in description for c in "<>"),
            "Invalid Skill description")
    require(not re.search(r"\[TODO:", text), "Unfinished Skill placeholder")
    ui = path.parent / "agents/openai.yaml"
    if ui.exists():
        ui_text = read_text(ui)
        require(ui_text.startswith("interface:\n"), "Skill UI must declare interface")
        fields = re.findall(r'^  ([a-z_]+): ("[^\n]+")$', ui_text, re.M)
        parsed = {key: json.loads(value) for key, value in fields}
        require(len(parsed) == len(fields) == 3, "Unexpected/duplicate Skill UI fields")
        for key in ("display_name", "short_description", "default_prompt"):
            label(parsed.get(key), f"Skill UI {key}")
        require("$" + name in parsed["default_prompt"], "Skill UI prompt points to a different Skill")
    return name


def check(root=ROOT, records=False, strict_hashes=False):
    errors, warnings, summary = [], [], {}

    def inspect(path, operation):
        try:
            return operation()
        except (ValueError, OSError, SyntaxError, KeyError, TypeError, RuntimeError, zipfile.BadZipFile) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            return None

    required = [root / p for p in ("AGENTS.md", "HARNESS.md", "scripts/harness.py", "scripts/test_harness.py")]
    required += [root / ".agents/skills" / name / "SKILL.md" for name in sorted(SKILL_NAMES)]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing harness file: {path.relative_to(root)}")
    docs = [p for p in root.rglob("*.md")
            if not DATA_DIRS.intersection(p.relative_to(root).parts)
            and (p.name in {"AGENTS.md", "CLAUDE.md", "HARNESS.md"} or ".agents" in p.parts)]
    for path in docs:
        inspect(path, lambda p=path: markdown_links(p, root))
    skills = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    names = [inspect(path, lambda p=path: skill_metadata(p)) for path in skills]
    valid_names = [name for name in names if name]
    if len(valid_names) != len(set(valid_names)):
        errors.append("Duplicate Skill names")
    base = root / "능력단위평가"
    # Only actual legacy automation locations are considered, never submissions.
    for path in (base / "skills", base / ".agents"):
        if path.exists() and any(p.is_file() for p in path.rglob("*")):
            errors.append(f"Legacy automation still present: {path.relative_to(root)}")
    for path in (root / "scripts").glob("*.py"):
        inspect(path, lambda p=path: ast.parse(read_text(p), filename=str(p)))
    # No project Hook/Agent config is installed. New configurations need an
    # explicit validator when introduced rather than silently passing this check.
    configs = [p for p in root.rglob("*") if p.is_file()
               and not DATA_DIRS.intersection(p.relative_to(root).parts)
               and any(part in {".codex", ".claude"} for part in p.relative_to(root).parts)]
    if configs:
        errors.append("New project Hook/Agent config requires validation integration: " +
                      ", ".join(str(p.relative_to(root)) for p in configs))
    summary.update(instruction_files=len(docs), skills=valid_names, custom_agents=0, hooks=0)
    if records:
        exams, grades = [], 0
        for path in sorted((root / "능력단위평가").glob("*/Exam.md")):
            rows = inspect(path, lambda p=path: parse_exam(p))
            if rows is None:
                continue
            exams.append({"unit": path.parent.name, "items": len(rows), "total": sum(r["max"] for r in rows)})
            for grade in sorted((path.parent / "채점 자료").glob("*/문항별_채점.json")):
                notices = inspect(grade, lambda p=grade, r=rows: grade_check(p, r, strict_hashes))
                warnings.extend(f"{grade.parent.relative_to(root)}: {notice}" for notice in (notices or []))
                grades += 1
        summary.update(exams=exams, grade_records=grades)
    return {"ok": not errors, "summary": summary, "errors": errors, "warnings": warnings}


def inventory(root=ROOT):
    result = {}
    for folder in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        files = [p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        result[folder.name] = {"files": len(files), "bytes": sum(p.stat().st_size for p in files),
                             "extensions": dict(sorted(Counter(p.suffix or "(none)" for p in files).items()))}
    return result


def codex_command():
    candidate = shutil.which("codex.cmd" if os.name == "nt" else "codex")
    if not candidate and os.name == "nt":
        candidate = shutil.which("codex.exe")
    require(candidate is not None, "Codex CLI is not installed/on PATH")
    path = Path(candidate)
    if path.suffix.lower() in {".cmd", ".bat", ".ps1"}:
        # Invoke the inspected npm entrypoint directly; never evaluate prompts
        # through cmd.exe or PowerShell's script execution policy.
        entry = path.parent / "node_modules/@openai/codex/bin/codex.js"
        adjacent = path.parent / "node.exe"
        node = str(adjacent) if adjacent.is_file() else shutil.which("node")
        require(entry.is_file() and node is not None, "Cannot resolve npm Codex entrypoint and Node")
        return [node, str(entry)]
    return [str(path)]


def run_codex(arguments, dry_run=False):
    arguments = arguments[1:] if arguments[:1] == ["--"] else arguments
    require(not any(a in {"-C", "--cd"} or a.startswith(("--cd=", "-C")) for a in arguments),
            "run fixes cwd to 국비; use Codex directly to select a different workspace")
    before = check()
    if not before["ok"]:
        emit(before)
        return 1
    command = codex_command() + ["-C", str(ROOT)] + arguments
    if dry_run:
        emit({"cwd": str(ROOT), "argv": command, "precheck": before["ok"]})
        return 0
    status = 1
    try:
        status = subprocess.run(command, cwd=ROOT, shell=False).returncode
    finally:
        after = check()
        emit(after)
    return status if status else (0 if after["ok"] else 1)


def emit(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inventory", help="Summarize local files without opening private document text")
    validation = commands.add_parser("check", help="Check automation links, skills and Python syntax")
    validation.add_argument("--records", action="store_true", help="Also check Exam rubrics, score records and supplied checksums")
    validation.add_argument("--strict-hashes", action="store_true", help="With --records, require byte-identical working copies too")
    for name in ("scores", "timetable"):
        sub = commands.add_parser(name, help=f"Read JSON, calculate {name}, print JSON without changing inputs")
        sub.add_argument("input", type=Path)
    runner = commands.add_parser("run", help="Run Codex in 국비 with automatic pre/post checks")
    runner.add_argument("--dry-run", action="store_true", help="Show argv and verify paths without starting Codex")
    runner.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            return run_codex(args.args, args.dry_run)
        if args.command == "check":
            require(not args.strict_hashes or args.records, "--strict-hashes requires --records")
            result = check(records=args.records, strict_hashes=args.strict_hashes)
            emit(result)
            return 0 if result["ok"] else 1
        if args.command == "inventory":
            emit(inventory())
        else:
            data = load_json(args.input)
            emit(calculate_scores(data) if args.command == "scores" else allocate_timetable(data))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        emit({"ok": False, "error": str(exc)})
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
