import os

import fitz
from PIL import Image, ImageDraw


src = r".\본사 홈페이지\학생 포트폴리오\9.인테리어포폴북 PDF 작업파일_김민주_VMD.pdf"
out = r".\.codex-temp\kimminju_preview"
os.makedirs(out, exist_ok=True)

doc = fitz.open(src)
print(f"pages {doc.page_count}")
tiles = []

start = 20
end = min(36, doc.page_count)
for i in range(start, end):
    page = doc.load_page(i)
    pix = page.get_pixmap(matrix=fitz.Matrix(0.55, 0.55), alpha=False)
    path = os.path.join(out, f"page_{i + 1:02d}.jpg")
    pix.save(path)

    image = Image.open(path).convert("RGB")
    image.thumbnail((360, 260))
    tile = Image.new("RGB", (380, 300), "white")
    tile.paste(image, ((380 - image.width) // 2, 18))
    ImageDraw.Draw(tile).text((12, 278), f"PAGE {i + 1}", fill="black")
    tiles.append(tile)

sheet = Image.new("RGB", (760, 2400), (220, 220, 220))
for i, tile in enumerate(tiles):
    sheet.paste(tile, ((i % 2) * 380, (i // 2) * 300))

sheet_path = os.path.join(out, "contact_sheet_21_36.jpg")
sheet.save(sheet_path, quality=90)
print(sheet_path)
