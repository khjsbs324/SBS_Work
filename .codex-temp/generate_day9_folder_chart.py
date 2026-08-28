from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]

from PIL import Image, ImageDraw, ImageFont


DAY_DIR = WORKSPACE / "수업자료" / "AI에이전트" / "DAY9"
OUTPUT = DAY_DIR.parent / "폴더 구조 차트.png"

CANVAS_W = 2400
MARGIN_X = 88
COLUMN_GAP = 42
PANEL_W = (CANVAS_W - MARGIN_X * 2 - COLUMN_GAP) // 2

BG = "#FFFFFF"
INK = "#071B3A"
MUTED = "#60708D"
FAINT = "#93A2BC"
LINE = "#B8C3D4"
HAIRLINE = "#DCE3EC"
RED = "#F52E3C"
RED_DARK = "#B90F23"
RED_FILL = "#FFF5F6"
BLUE = "#009DDA"
BLUE_DARK = "#087AA7"
BLUE_FILL = "#F0F9FD"
PURPLE = "#4B4BE3"
PURPLE_DARK = "#3939C9"
PURPLE_FILL = "#F6F6FF"
BADGE_FILL = "#EDEDFF"
PANEL_BG = "#FBFCFE"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / filename), size=size)


TITLE_FONT = font(64, True)
SUBTITLE_FONT = font(27)
LEGEND_FONT = font(22, True)
ROOT_FONT = font(43, True)
ROOT_META_FONT = font(24)
PANEL_TITLE_FONT = font(29, True)
PANEL_META_FONT = font(20)
ROW_DIR_FONT = font(22, True)
ROW_FILE_FONT = font(21)
BADGE_FONT = font(17, True)
FOOTER_FONT = font(19)


@dataclass(frozen=True)
class Entry:
    path: Path
    depth: int
    ancestors_continue: tuple[bool, ...]
    is_last: bool


def sorted_children(path: Path) -> list[Path]:
    return sorted(
        path.iterdir(),
        key=lambda item: (not item.is_dir(), item.name.casefold()),
    )


def flatten_children(path: Path) -> list[Entry]:
    entries: list[Entry] = []

    def visit(parent: Path, depth: int, continuation: tuple[bool, ...]) -> None:
        children = sorted_children(parent)
        for index, child in enumerate(children):
            is_last = index == len(children) - 1
            entries.append(Entry(child, depth, continuation, is_last))
            if child.is_dir():
                visit(child, depth + 1, continuation + (not is_last,))

    visit(path, 0, ())
    return entries


def count_descendants(path: Path) -> tuple[int, int]:
    folder_count = 0
    file_count = 0
    for current_root, directories, files in os.walk(path):
        folder_count += len(directories)
        file_count += len(files)
    return folder_count, file_count


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill: str, outline: str, width: int = 3) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def folder_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str, width: int = 4) -> None:
    w = int(size * 1.25)
    h = int(size * 0.80)
    tab_w = int(size * 0.48)
    tab_h = int(size * 0.22)
    points = [
        (x, y + tab_h),
        (x + tab_w, y + tab_h),
        (x + tab_w + int(size * 0.14), y + int(size * 0.39)),
        (x + w, y + int(size * 0.39)),
        (x + w, y + h),
        (x, y + h),
    ]
    draw.line(points + [points[0]], fill=color, width=width, joint="curve")


def file_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str, width: int = 4) -> None:
    w = int(size * 0.78)
    h = size
    fold = int(size * 0.27)
    points = [
        (x, y),
        (x + w - fold, y),
        (x + w, y + fold),
        (x + w, y + h),
        (x, y + h),
        (x, y),
    ]
    draw.line(points, fill=color, width=width, joint="curve")
    draw.line([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)], fill=color, width=width)


def text_width(draw: ImageDraw.ImageDraw, value: str, use_font) -> int:
    box = draw.textbbox((0, 0), value, font=use_font)
    return box[2] - box[0]


def fit_font(draw: ImageDraw.ImageDraw, value: str, max_width: int, preferred: int, bold: bool = False):
    current = preferred
    while current > 15:
        candidate = font(current, bold)
        if text_width(draw, value, candidate) <= max_width:
            return candidate
        current -= 1
    return font(15, bold)


def draw_badge(draw: ImageDraw.ImageDraw, right: int, center_y: int, label: str, kind: str) -> int:
    label = label.upper() or "FILE"
    badge_font = BADGE_FONT
    badge_w = max(72, text_width(draw, label, badge_font) + 32)
    badge_h = 34
    left = right - badge_w
    if kind == "folder":
        fill, color = BLUE, "#FFFFFF"
    elif kind == "root":
        fill, color = RED, "#FFFFFF"
    else:
        fill, color = BADGE_FILL, PURPLE_DARK
    rounded(draw, (left, center_y - badge_h // 2, right, center_y + badge_h // 2), 17, fill, fill, 1)
    tw = text_width(draw, label, badge_font)
    draw.text((left + (badge_w - tw) / 2, center_y - 12), label, font=badge_font, fill=color)
    return left


def draw_file_card(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, item: Path, compact: bool = False) -> None:
    rounded(draw, (x, y, x + w, y + h), 16, PURPLE_FILL, PURPLE, 3)
    icon_size = 30 if compact else 34
    file_icon(draw, x + 22, y + (h - icon_size) // 2, icon_size, PURPLE, 3)
    ext = item.suffix[1:].upper() if item.suffix else "FILE"
    badge_left = draw_badge(draw, x + w - 18, y + h // 2, ext, "file")
    name_x = x + 72
    available = badge_left - name_x - 20
    use_font = fit_font(draw, item.name, available, 21 if compact else 24, False)
    bbox = draw.textbbox((0, 0), item.name, font=use_font)
    th = bbox[3] - bbox[1]
    draw.text((name_x, y + (h - th) / 2 - bbox[1]), item.name, font=use_font, fill=INK)


def draw_folder_card(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, item: Path) -> None:
    rounded(draw, (x, y, x + w, y + h), 16, BLUE_FILL, BLUE, 3)
    icon_size = 32
    folder_icon(draw, x + 20, y + (h - int(icon_size * 0.8)) // 2 - 3, icon_size, BLUE, 3)
    badge_left = draw_badge(draw, x + w - 18, y + h // 2, "DIR", "folder")
    name = item.name + "/"
    name_x = x + 74
    available = badge_left - name_x - 20
    use_font = fit_font(draw, name, available, 22, True)
    bbox = draw.textbbox((0, 0), name, font=use_font)
    th = bbox[3] - bbox[1]
    draw.text((name_x, y + (h - th) / 2 - bbox[1]), name, font=use_font, fill=INK)


ROW_H = 52
ROW_GAP = 8
PANEL_HEADER_H = 96
PANEL_PAD_TOP = 22
PANEL_PAD_BOTTOM = 24
PANEL_GAP = 28
INDENT = 27


def panel_height(entries: list[Entry]) -> int:
    return PANEL_HEADER_H + PANEL_PAD_TOP + len(entries) * (ROW_H + ROW_GAP) + PANEL_PAD_BOTTOM - ROW_GAP


def draw_panel(draw: ImageDraw.ImageDraw, x: int, y: int, folder: Path) -> int:
    entries = flatten_children(folder)
    height = panel_height(entries)
    rounded(draw, (x, y, x + PANEL_W, y + height), 24, PANEL_BG, HAIRLINE, 2)

    header_h = PANEL_HEADER_H
    rounded(draw, (x, y, x + PANEL_W, y + header_h), 24, BLUE_FILL, BLUE, 4)
    folder_icon(draw, x + 30, y + 29, 45, BLUE, 4)
    title = folder.name + "/"
    draw.text((x + 104, y + 20), title, font=PANEL_TITLE_FONT, fill=INK)
    dirs, files = count_descendants(folder)
    meta = f"하위 {dirs} folders · {files} files"
    draw.text((x + 104, y + 57), meta, font=PANEL_META_FONT, fill=MUTED)
    draw_badge(draw, x + PANEL_W - 26, y + header_h // 2, "DIR", "folder")

    start_y = y + header_h + PANEL_PAD_TOP
    trunk_x = x + 31
    if entries:
        draw.line((trunk_x, y + header_h, trunk_x, start_y + ROW_H // 2), fill=LINE, width=3)

    for index, entry in enumerate(entries):
        row_y = start_y + index * (ROW_H + ROW_GAP)
        center_y = row_y + ROW_H // 2
        node_x = trunk_x + entry.depth * INDENT
        card_x = node_x + 24
        card_right = x + PANEL_W - 22
        card_w = card_right - card_x

        for level, continues in enumerate(entry.ancestors_continue):
            if continues:
                ancestor_x = trunk_x + level * INDENT
                draw.line((ancestor_x, row_y - ROW_GAP // 2, ancestor_x, row_y + ROW_H + ROW_GAP // 2), fill=LINE, width=3)

        line_top = row_y - ROW_GAP // 2
        line_bottom = center_y if entry.is_last else row_y + ROW_H + ROW_GAP // 2
        draw.line((node_x, line_top, node_x, line_bottom), fill=LINE, width=3)
        draw.line((node_x, center_y, card_x, center_y), fill=LINE, width=3)

        if entry.path.is_dir():
            draw_folder_card(draw, card_x, row_y, card_w, ROW_H, entry.path)
        else:
            draw_file_card(draw, card_x, row_y, card_w, ROW_H, entry.path, compact=True)

    return height


def draw_legend(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    items = [(RED, "ROOT"), (BLUE, "FOLDER"), (PURPLE, "FILE")]
    cursor = x
    for color, label in items:
        draw.rounded_rectangle((cursor, y, cursor + 26, y + 26), radius=7, fill="#FFFFFF", outline=color, width=4)
        draw.text((cursor + 38, y - 1), label, font=LEGEND_FONT, fill="#33415C")
        cursor += 38 + text_width(draw, label, LEGEND_FONT) + 46


def main() -> None:
    if not DAY_DIR.is_dir():
        raise SystemExit(f"DAY9 directory not found: {DAY_DIR}")

    top_level = sorted_children(DAY_DIR)
    top_folders = [item for item in top_level if item.is_dir()]
    root_files = [item for item in top_level if item.is_file()]
    total_folders, total_files = count_descendants(DAY_DIR)

    expected_folders = {".claude", "presentation", "renderer", "scripts"}
    actual_folders = {item.name for item in top_folders}
    if actual_folders != expected_folders:
        print(f"Note: top-level folders changed: {sorted(actual_folders)}")

    panel_entries = {folder.name: flatten_children(folder) for folder in top_folders}
    left_folder = next((folder for folder in top_folders if folder.name == ".claude"), top_folders[0])
    right_folders = [folder for folder in top_folders if folder != left_folder]

    header_bottom = 182
    root_y = 198
    root_h = 126
    root_files_y = 390
    root_file_h = 72
    branch_y = 548

    left_height = panel_height(panel_entries[left_folder.name])
    right_height = sum(panel_height(panel_entries[f.name]) for f in right_folders)
    if right_folders:
        right_height += PANEL_GAP * (len(right_folders) - 1)
    content_bottom = branch_y + max(left_height, right_height)
    canvas_h = content_bottom + 128

    image = Image.new("RGB", (CANVAS_W, canvas_h), BG)
    draw = ImageDraw.Draw(image)

    draw.text((MARGIN_X, 58), "DAY9 폴더 구조", font=TITLE_FONT, fill=INK)
    subtitle = f"실제 디렉터리 기준 · {total_folders} folders · {total_files} files · 모든 하위 항목 포함"
    draw.text((MARGIN_X + 4, 132), subtitle, font=SUBTITLE_FONT, fill=MUTED)
    draw_legend(draw, CANVAS_W - 750, 76)

    root_w = 1320
    root_x = (CANVAS_W - root_w) // 2
    rounded(draw, (root_x, root_y, root_x + root_w, root_y + root_h), 28, RED_FILL, RED, 5)
    draw_badge(draw, root_x + 150, root_y + root_h // 2, "ROOT", "root")
    draw.text((root_x + 205, root_y + 31), "DAY9", font=ROOT_FONT, fill=RED_DARK)
    draw.text((root_x + 510, root_y + 49), "project root · 전체 구조", font=ROOT_META_FONT, fill=MUTED)

    root_center_x = CANVAS_W // 2
    draw.line((root_center_x, root_y + root_h, root_center_x, root_files_y - 28), fill=LINE, width=4)

    if root_files:
        available_w = CANVAS_W - MARGIN_X * 2
        gap = 24
        card_w = (available_w - gap * (len(root_files) - 1)) // len(root_files)
        centers = []
        for idx, item in enumerate(root_files):
            card_x = MARGIN_X + idx * (card_w + gap)
            centers.append(card_x + card_w // 2)
        connector_y = root_files_y - 28
        draw.line((centers[0], connector_y, centers[-1], connector_y), fill=LINE, width=4)
        for idx, item in enumerate(root_files):
            card_x = MARGIN_X + idx * (card_w + gap)
            draw.line((centers[idx], connector_y, centers[idx], root_files_y), fill=LINE, width=4)
            draw_file_card(draw, card_x, root_files_y, card_w, root_file_h, item)

    branch_connector_y = branch_y - 34
    left_x = MARGIN_X
    right_x = MARGIN_X + PANEL_W + COLUMN_GAP
    draw.line((root_center_x, root_files_y + root_file_h, root_center_x, branch_connector_y), fill=LINE, width=4)
    left_center = left_x + PANEL_W // 2
    right_center = right_x + PANEL_W // 2
    draw.line((left_center, branch_connector_y, right_center, branch_connector_y), fill=LINE, width=4)
    draw.line((left_center, branch_connector_y, left_center, branch_y), fill=LINE, width=4)
    draw.line((right_center, branch_connector_y, right_center, branch_y), fill=LINE, width=4)

    draw_panel(draw, left_x, branch_y, left_folder)
    cursor_y = branch_y
    for folder in right_folders:
        cursor_y += draw_panel(draw, right_x, cursor_y, folder) + PANEL_GAP

    footer_y = canvas_h - 74
    draw.line((MARGIN_X, footer_y - 28, CANVAS_W - MARGIN_X, footer_y - 28), fill=HAIRLINE, width=2)
    source = r"Source · 수업자료\AI에이전트\DAY9"
    draw.text((MARGIN_X, footer_y), source, font=FOOTER_FONT, fill=FAINT)
    date_label = date.today().strftime("%Y.%m.%d")
    validation = f"전체 항목 검증 · {total_folders + total_files} items · {date_label}"
    validation_w = text_width(draw, validation, FOOTER_FONT)
    draw.text((CANVAS_W - MARGIN_X - validation_w, footer_y), validation, font=FOOTER_FONT, fill=FAINT)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG", optimize=True)

    rendered_entries = len(root_files) + len(top_folders) + sum(len(items) for items in panel_entries.values())
    expected_entries = total_folders + total_files
    if rendered_entries != expected_entries:
        raise RuntimeError(f"Rendered {rendered_entries} items, expected {expected_entries}")

    print(f"Created: {OUTPUT}")
    print(f"Canvas: {CANVAS_W} x {canvas_h}")
    print(f"Folders: {total_folders}")
    print(f"Files: {total_files}")
    print(f"Rendered items: {rendered_entries}/{expected_entries}")


if __name__ == "__main__":
    main()
