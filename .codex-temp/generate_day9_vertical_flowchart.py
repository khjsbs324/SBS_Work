from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

from generate_day9_folder_chart import (
    BADGE_FONT,
    BG,
    BLUE,
    BLUE_DARK,
    BLUE_FILL,
    DAY_DIR,
    FOOTER_FONT,
    HAIRLINE,
    INK,
    LEGEND_FONT,
    LINE,
    MUTED,
    PURPLE,
    PURPLE_DARK,
    PURPLE_FILL,
    RED,
    RED_DARK,
    RED_FILL,
    ROOT_FONT,
    ROOT_META_FONT,
    TITLE_FONT,
    count_descendants,
    draw_badge,
    draw_legend,
    file_icon,
    fit_font,
    flatten_children,
    folder_icon,
    rounded,
    text_width,
    font,
)


OUTPUT = DAY_DIR.parent / "플로우차트.png"

CANVAS_W = 2000
MARGIN_X = 86
BASE_CARD_X = 220
RIGHT_EDGE = CANVAS_W - MARGIN_X
INDENT = 82
ROW_H = 66
ROW_GAP = 14

SUBTITLE_FONT = font(27)
ROW_FOLDER_FONT = font(24, True)
ROW_FILE_FONT = font(23)
ROW_PATH_FONT = font(17)
SECTION_FONT = font(18, True)


@dataclass(frozen=True)
class NodeLayout:
    path: Path
    depth: int
    x: int
    y: int
    width: int
    height: int
    is_dir: bool


def draw_arrow_head(draw: ImageDraw.ImageDraw, x: int, y: int, color: str) -> None:
    draw.polygon([(x, y), (x - 13, y - 8), (x - 13, y + 8)], fill=color)


def draw_node(draw: ImageDraw.ImageDraw, node: NodeLayout) -> None:
    x, y, w, h = node.x, node.y, node.width, node.height
    if node.is_dir:
        rounded(draw, (x, y, x + w, y + h), 17, BLUE_FILL, BLUE, 3)
        folder_icon(draw, x + 22, y + 19, 36, BLUE, 3)
        badge_left = draw_badge(draw, x + w - 18, y + h // 2, "DIR", "folder")
        name = node.path.name + "/"
        dirs, files = count_descendants(node.path)
        count_text = f"{dirs} folders · {files} files"
        name_x = x + 80
        max_name_w = min(610, badge_left - name_x - 260)
        use_font = fit_font(draw, name, max_name_w, 24, True)
        bbox = draw.textbbox((0, 0), name, font=use_font)
        draw.text((name_x, y + 14 - bbox[1]), name, font=use_font, fill=INK)
        count_x = max(name_x + text_width(draw, name, use_font) + 30, x + 620)
        if count_x + text_width(draw, count_text, ROW_PATH_FONT) < badge_left - 20:
            draw.text((count_x, y + 23), count_text, font=ROW_PATH_FONT, fill=MUTED)
    else:
        rounded(draw, (x, y, x + w, y + h), 17, PURPLE_FILL, PURPLE, 3)
        file_icon(draw, x + 24, y + 16, 34, PURPLE, 3)
        extension = node.path.suffix[1:].upper() if node.path.suffix else "FILE"
        badge_left = draw_badge(draw, x + w - 18, y + h // 2, extension, "file")
        name_x = x + 82
        available = badge_left - name_x - 24
        use_font = fit_font(draw, node.path.name, available, 23, False)
        bbox = draw.textbbox((0, 0), node.path.name, font=use_font)
        th = bbox[3] - bbox[1]
        draw.text((name_x, y + (h - th) / 2 - bbox[1]), node.path.name, font=use_font, fill=INK)


def main() -> None:
    entries = flatten_children(DAY_DIR)
    total_folders, total_files = count_descendants(DAY_DIR)

    header_y = 58
    root_y = 194
    root_h = 126
    flow_start_y = 420

    nodes: list[NodeLayout] = []
    for index, entry in enumerate(entries):
        x = BASE_CARD_X + entry.depth * INDENT
        width = RIGHT_EDGE - x
        y = flow_start_y + index * (ROW_H + ROW_GAP)
        nodes.append(NodeLayout(entry.path, entry.depth, x, y, width, ROW_H, entry.path.is_dir()))

    canvas_h = flow_start_y + len(nodes) * (ROW_H + ROW_GAP) + 94
    image = Image.new("RGB", (CANVAS_W, canvas_h), BG)
    draw = ImageDraw.Draw(image)

    draw.text((MARGIN_X, header_y), "DAY9 세로형 플로우차트", font=TITLE_FONT, fill=INK)
    subtitle = f"ROOT에서 하위 항목으로 내려가는 구조 · {total_folders} folders · {total_files} files"
    draw.text((MARGIN_X + 4, 132), subtitle, font=SUBTITLE_FONT, fill=MUTED)
    draw_legend(draw, CANVAS_W - 742, 76)

    root_w = 1080
    root_x = (CANVAS_W - root_w) // 2
    rounded(draw, (root_x, root_y, root_x + root_w, root_y + root_h), 28, RED_FILL, RED, 5)
    draw_badge(draw, root_x + 150, root_y + root_h // 2, "ROOT", "root")
    draw.text((root_x + 210, root_y + 31), "DAY9", font=ROOT_FONT, fill=RED_DARK)
    draw.text((root_x + 505, root_y + 49), "vertical flow · 77 items", font=ROOT_META_FONT, fill=MUTED)

    by_path = {node.path: node for node in nodes}
    root_trunk_x = BASE_CARD_X - 46
    connector_start_y = root_y + root_h + 34
    if nodes:
        last_root_node = next(node for node in reversed(nodes) if node.path.parent == DAY_DIR)
        last_root_center = last_root_node.y + last_root_node.height // 2
        draw.line((CANVAS_W // 2, root_y + root_h, CANVAS_W // 2, connector_start_y), fill=LINE, width=4)
        draw.line((CANVAS_W // 2, connector_start_y, root_trunk_x, connector_start_y), fill=LINE, width=4)
        draw.line((root_trunk_x, connector_start_y, root_trunk_x, last_root_center), fill=LINE, width=4)

    children_by_parent: dict[Path, list[NodeLayout]] = {}
    for node in nodes:
        children_by_parent.setdefault(node.path.parent, []).append(node)

    for node in nodes:
        center_y = node.y + node.height // 2
        parent = node.path.parent
        if parent == DAY_DIR:
            source_x = root_trunk_x
            draw.line((source_x, center_y, node.x - 2, center_y), fill=LINE, width=4)
            draw_arrow_head(draw, node.x - 1, center_y, LINE)
            continue

        parent_node = by_path[parent]
        siblings = children_by_parent[parent]
        last_child = siblings[-1]
        branch_x = parent_node.x + 38
        start_y = parent_node.y + parent_node.height
        end_y = last_child.y + last_child.height // 2
        if node == siblings[0]:
            draw.line((branch_x, start_y, branch_x, end_y), fill=LINE, width=3)
        draw.line((branch_x, center_y, node.x - 2, center_y), fill=LINE, width=3)
        draw_arrow_head(draw, node.x - 1, center_y, LINE)

    for node in nodes:
        draw_node(draw, node)

    top_level_positions = [node for node in nodes if node.path.parent == DAY_DIR]
    for index, node in enumerate(top_level_positions, start=1):
        marker_x = MARGIN_X
        marker_y = node.y + node.height // 2
        label = f"{index:02d}"
        rounded(draw, (marker_x, marker_y - 17, marker_x + 54, marker_y + 17), 17, "#F3F6FA", HAIRLINE, 2)
        draw.text((marker_x + 14, marker_y - 12), label, font=SECTION_FONT, fill=MUTED)

    footer_y = canvas_h - 56
    draw.line((MARGIN_X, footer_y - 22, CANVAS_W - MARGIN_X, footer_y - 22), fill=HAIRLINE, width=2)
    source = r"Source · 수업자료\AI에이전트\DAY9"
    draw.text((MARGIN_X, footer_y), source, font=FOOTER_FONT, fill="#93A2BC")
    validation = f"세로형 전체 트리 · {len(nodes)}/{total_folders + total_files} items · {date.today().strftime('%Y.%m.%d')}"
    validation_w = text_width(draw, validation, FOOTER_FONT)
    draw.text((CANVAS_W - MARGIN_X - validation_w, footer_y), validation, font=FOOTER_FONT, fill="#93A2BC")

    image.save(OUTPUT, format="PNG", optimize=True)
    if len(nodes) != total_folders + total_files:
        raise RuntimeError(f"Rendered {len(nodes)} items, expected {total_folders + total_files}")

    print(f"Created: {OUTPUT}")
    print(f"Canvas: {CANVAS_W} x {canvas_h}")
    print(f"Folders: {total_folders}")
    print(f"Files: {total_files}")
    print(f"Rendered items: {len(nodes)}/{total_folders + total_files}")


if __name__ == "__main__":
    main()
