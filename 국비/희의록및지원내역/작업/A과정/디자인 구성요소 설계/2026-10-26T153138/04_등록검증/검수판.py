from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 22)
for group in 'ABC':
    sheet = Image.new('RGB', (1320, 1290), '#dce4ed')
    draw = ImageDraw.Draw(sheet)
    for i in range(6):
        im = Image.open(root / f'{group}_p{i + 1}.png').convert('RGB')
        im.thumbnail((415, 595))
        x, y = (i % 3) * 440 + 10, (i // 3) * 645 + 35
        sheet.paste(im, (x, y))
        draw.text((x, y - 30), f'{group} {i + 1}/6', font=font, fill='#17365a')
    sheet.save(root / f'{group}_contact.png', optimize=True)
