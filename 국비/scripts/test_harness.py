"""Regression checks for arithmetic, paths, read-only behavior and CLI gating."""

import copy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import harness


class ScoresTests(unittest.TestCase):
    def test_endpoints_and_remainder_tie(self):
        data = {"rows": [{"id": "A", "max": 1, "raw": 0},
                         {"id": "B", "max": 1, "raw": 0},
                         {"id": "C", "max": 98, "raw": 0}]}
        original = copy.deepcopy(data)
        result = harness.calculate_scores(data)
        self.assertEqual([r["registered"] for r in result["rows"]], [1, 0, 59])
        self.assertEqual(result["registeredTotal"], 60)
        self.assertEqual(data, original)
        for row in data["rows"]:
            row["raw"] = row["max"]
        result = harness.calculate_scores(data)
        self.assertEqual(result["registeredTotal"], 100)
        self.assertEqual([r["registered"] for r in result["rows"]], [1, 1, 98])

    def test_score_bounds_and_conservation(self):
        rng = random.Random(42)
        for _ in range(100):
            cuts = [0, *sorted(rng.sample(range(1, 100), 11)), 100]
            maxima = [b - a for a, b in zip(cuts, cuts[1:])]
            rows = [{"id": str(i), "max": maximum, "raw": rng.randint(0, maximum)}
                    for i, maximum in enumerate(maxima)]
            result = harness.calculate_scores({"rows": rows})
            self.assertEqual(sum(r["registered"] for r in result["rows"]), result["registeredTotal"])
            self.assertTrue(60 <= result["registeredTotal"] <= 100)
            self.assertTrue(all(0 <= r["registered"] <= r["max"] for r in result["rows"]))
            self.assertEqual(result, harness.calculate_scores({"rows": rows}))

    def test_invalid_or_pending_scores_rejected(self):
        for value in (None, True, -1, 1.5, 101, "50"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                harness.calculate_scores({"rows": [{"id": "A", "max": 100, "raw": value}]})
        for data in ({"rows": []}, {"rows": [{"id": "A", "max": 99, "raw": 5}]},
                     {"rows": [{"id": "A", "max": 50, "raw": 5}] * 2}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                harness.calculate_scores(data)


class TimetableTests(unittest.TestCase):
    def sample(self):
        return {"unit_totals": {"수정 보완": 70, "디자인 구성요소 설계": 40}, "tracks": [
            {"id": "오전", "slots": [{"id": "1월", "hours": 60}, {"id": "2월", "hours": 44}],
             "units": [{"id": "수정 보완", "hours": 70}, {"id": "디자인 구성요소 설계", "hours": 20}]},
            {"id": "오후", "slots": [{"id": "1월", "hours": 20}],
             "units": [{"id": "디자인 구성요소 설계", "hours": 20}]}]}

    def test_carry_forward_cross_track_totals_and_blank_capacity(self):
        data = self.sample()
        original = copy.deepcopy(data)
        result = harness.allocate_timetable(data)
        morning = result["tracks"][0]["slots"]
        self.assertEqual(morning[0]["allocations"], [{"id": "수정 보완", "hours": 60}])
        self.assertEqual(morning[1]["allocations"], [
            {"id": "수정 보완", "hours": 10}, {"id": "디자인 구성요소 설계", "hours": 20}])
        self.assertEqual(morning[1]["unallocated"], 14)
        self.assertEqual(result["unit_totals"], data["unit_totals"])
        for track in result["tracks"]:
            for slot in track["slots"]:
                self.assertEqual(sum(a["hours"] for a in slot["allocations"]) + slot["unallocated"], slot["capacity"])
        self.assertEqual(data, original)

    def test_insufficient_capacity(self):
        data = self.sample()
        data["tracks"][1]["slots"][0]["hours"] = 19
        with self.assertRaisesRegex(ValueError, "exceed capacity"):
            harness.allocate_timetable(data)

    def test_total_mismatch_and_duplicate_slots(self):
        data = self.sample()
        data["unit_totals"]["수정 보완"] = 71
        with self.assertRaisesRegex(ValueError, "totals differ"):
            harness.allocate_timetable(data)
        data = self.sample()
        data["tracks"][0]["slots"][1]["id"] = "1월"
        with self.assertRaisesRegex(ValueError, "duplicate slot"):
            harness.allocate_timetable(data)


class FilesAndRunnerTests(unittest.TestCase):
    def test_verified_archive_distinguishes_newlines_from_content_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = "학생 응답\n내용\n".encode("utf-8")
            archive = root / "제출.zip"
            with zipfile.ZipFile(archive, "w") as package:
                package.writestr("답안.md", original)
            meta = {"archive": archive.name, "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                    "files": [{"filename": "답안.md", "bytes": len(original), "sha256": hashlib.sha256(original).hexdigest()}]}
            metadata = root / "제출물_확인.json"
            metadata.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            answer = root / "답안.md"
            answer.write_bytes(original.replace(b"\n", b"\r\n"))
            self.assertEqual(len(harness.submission_check(metadata)), 1)
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                harness.submission_check(metadata, strict_hashes=True)
            answer.write_bytes(original + "추가 응답".encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                harness.submission_check(metadata)
            answer.write_bytes(original)
            self.assertEqual(harness.submission_check(metadata), [])
            archive.write_bytes(archive.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "Original ZIP checksum mismatch"):
                harness.submission_check(metadata)

    def test_json_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "입력.json"
            path.write_text('{"rows": [], "rows": [1]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                harness.load_json(path)

    def test_links_with_spaces_imports_and_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "자료 파일.md"
            target.write_text("원본", encoding="utf-8")
            source = root / "CLAUDE.md"
            source.write_text("[자료](<자료 파일.md>)\n[같은 자료](자료%20파일.md#제목)\n@자료 파일.md\n", encoding="utf-8")
            harness.markdown_links(source, root)
            source.write_text("[오류](없는파일.md)", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Missing link"):
                harness.markdown_links(source, root)

    def test_metadata_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "escapes"):
                harness.inside(Path(directory), "../outside.pdf")

    def test_exam_tier_gap_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exam = root / "Exam.md"
            (root / "평가 수행준거.txt").write_text("AA-01 내용", encoding="utf-8")
            good = "# 평가\n총점: 100점\n### AA-01. 항목 — 100점\n- 76~100점: 가\n- 51~75점: 나\n- 26~50점: 다\n- 0~25점: 라\n"
            exam.write_text(good, encoding="utf-8")
            self.assertEqual(harness.parse_exam(exam)[0]["max"], 100)
            exam.write_text(good.replace("26~50점", "27~50점"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cover"):
                harness.parse_exam(exam)

    def test_scores_cli_from_other_cwd_preserves_input(self):
        with tempfile.TemporaryDirectory(prefix="harness space ") as directory:
            path = Path(directory) / "한글 입력.json"
            path.write_text(json.dumps({"rows": [{"id": "A", "max": 100, "raw": 75}]}), encoding="utf-8")
            original = path.read_bytes()
            process = subprocess.run([sys.executable, "-B", str(harness.ROOT / "scripts/harness.py"), "scores", str(path)],
                                     cwd=directory, capture_output=True, encoding="utf-8")
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout)["registeredTotal"], 90)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    @patch.object(harness, "emit")
    @patch.object(harness, "codex_command", return_value=["codex"])
    @patch.object(harness.subprocess, "run")
    @patch.object(harness, "check")
    def test_runner_gates_and_propagates_exit_status(self, check, run, command, emit):
        check.return_value = {"ok": False}
        self.assertEqual(harness.run_codex([]), 1)
        run.assert_not_called()
        check.return_value = {"ok": True}
        run.return_value.returncode = 7
        self.assertEqual(harness.run_codex(["--", "exec", "질문 $() & 문자"]), 7)
        run.assert_called_once_with(["codex", "-C", str(harness.ROOT), "exec", "질문 $() & 문자"],
                                    cwd=harness.ROOT, shell=False)
        check.side_effect = [{"ok": True}, {"ok": False}]
        run.return_value.returncode = 0
        self.assertEqual(harness.run_codex([]), 1)

    def test_runner_cannot_change_scope(self):
        for args in (["-C", ".."], ["--cd=.."], ["-C.."]):
            with self.assertRaises(ValueError):
                harness.run_codex(args)


if __name__ == "__main__":
    unittest.main()
