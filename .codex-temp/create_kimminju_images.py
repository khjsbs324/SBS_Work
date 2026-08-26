import os

import fitz
from PIL import Image, ImageFilter, ImageOps, ImageDraw


PDF_PATH = r".\본사 홈페이지\학생 포트폴리오\9.인테리어포폴북 PDF 작업파일_김민주_VMD.pdf"
OUTPUT_DIR = r".\.codex-temp\kimminju_crops"

# (output name, 1-based page, normalized crop rectangle, normalized blur rectangles)
CROPS = [
    ("kimminju_01", 4, (0.510, 0.000, 1.000, 1.000), []),
    ("kimminju_02", 10, (0.000, 0.230, 0.750, 0.785), []),
    ("kimminju_03", 7, (0.180, 0.400, 0.570, 0.960), []),
    ("kimminju_04", 13, (0.585, 0.735, 0.915, 0.990), []),
    ("kimminju_05", 22, (0.030, 0.340, 0.500, 0.775), []),
    ("kimminju_06", 28, (0.645, 0.635, 0.990, 0.945), []),
    ("kimminju_07", 32, (0.568, 0.245, 0.930, 0.745), []),
    ("kimminju_08", 34, (0.020, 0.060, 0.480, 0.515), []),
    ("kimminju_09", 35, (0.020, 0.060, 0.480, 0.515), []),
    ("kimminju_10", 35, (0.515, 0.060, 0.988, 0.515), []),
]


def blur_region(image, bounds):
    left = round(bounds[0] * image.width)
    top = round(bounds[1] * image.height)
    right = round(bounds[2] * image.width)
    bottom = round(bounds[3] * image.height)
    patch = image.crop((left, top, right, bottom))
    radius = max(10, min(patch.size) // 5)
    patch = patch.filter(ImageFilter.GaussianBlur(radius=radius))
    image.paste(patch, (left, top))


os.makedirs(OUTPUT_DIR, exist_ok=True)
document = fitz.open(PDF_PATH)

generated = []
for name, page_number, fractions, blur_regions in CROPS:
    page = document.load_page(page_number - 1)
    page_rect = page.rect
    clip = fitz.Rect(
        fractions[0] * page_rect.width,
        fractions[1] * page_rect.height,
        fractions[2] * page_rect.width,
        fractions[3] * page_rect.height,
    )
    scale = max(3.0, 1600 / clip.width)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

    for bounds in blur_regions:
        blur_region(image, bounds)

    if max(image.size) > 2000:
        ratio = 2000 / max(image.size)
        image = image.resize(
            (round(image.width * ratio), round(image.height * ratio)),
            Image.Resampling.LANCZOS,
        )
    elif image.width > 1800:
        height = round(image.height * 1800 / image.width)
        image = image.resize((1800, height), Image.Resampling.LANCZOS)

    output_path = os.path.join(OUTPUT_DIR, f"{name}.jpg")
    image.save(output_path, "JPEG", quality=92, optimize=True, progressive=True)
    generated.append((output_path, page_number, image.size))

thumbs = []
for output_path, page_number, _ in generated:
    image = Image.open(output_path).convert("RGB")
    image.thumbnail((400, 260), Image.Resampling.LANCZOS)
    tile = Image.new("RGB", (420, 310), "white")
    tile.paste(image, ((420 - image.width) // 2, 12))
    ImageDraw.Draw(tile).text(
        (12, 284), f"{os.path.basename(output_path)} / PDF p.{page_number}", fill="black"
    )
    thumbs.append(tile)

sheet = Image.new("RGB", (840, 1550), (225, 225, 225))
for index, thumb in enumerate(thumbs):
    sheet.paste(thumb, ((index % 2) * 420, (index // 2) * 310))

sheet_path = os.path.join(OUTPUT_DIR, "contact_sheet.jpg")
sheet.save(sheet_path, "JPEG", quality=90)

for output_path, page_number, size in generated:
    print(f"{output_path}\tpage={page_number}\tsize={size[0]}x{size[1]}")
print(sheet_path)
