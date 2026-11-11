"""Create a local visual index of the downloaded photo archive."""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'Photos' / 'From-current-site'
report = json.loads((DEST / 'photo-library.json').read_text(encoding='utf-8'))
output = DEST / 'Contact-sheets'
output.mkdir(exist_ok=True)

seen = set()
photos = []
for entry in report['images']:
    file = entry.get('file')
    if not file or file in seen or entry['status'] not in ('downloaded', 'already-present', 'duplicate'):
        continue
    if 'Other-assets' in file:
        continue
    seen.add(file)
    photos.append(entry)
photos.sort(key=lambda entry: ((entry['source_pages'] or ['~'])[0], entry['file'].lower()))
try:
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 15)
    heading_font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 26)
except OSError:
    font = heading_font = ImageFont.load_default()

columns, rows = 5, 6
cell_width, cell_height = 290, 235
per_sheet = columns * rows
total_sheets = math.ceil(len(photos) / per_sheet)
index = []
for batch_start in range(0, len(photos), per_sheet):
    number = batch_start // per_sheet + 1
    batch = photos[batch_start:batch_start + per_sheet]
    sheet = Image.new('RGB', (columns * cell_width + 40, rows * cell_height + 105), '#f7f4ec')
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 18), f'Critter Creek | Website photo archive | {number} of {total_sheets}', font=heading_font, fill='#254c3b')
    draw.text((20, 57), 'Reference thumbnails only. Original files are preserved in the parent folder.', font=font, fill='#526050')
    for offset, entry in enumerate(batch):
        path = ROOT / entry['file']
        x = 20 + (offset % columns) * cell_width
        y = 92 + (offset // columns) * cell_height
        try:
            with Image.open(path) as original:
                photo = ImageOps.exif_transpose(original)
                photo.thumbnail((274, 177))
                sheet.paste(photo.convert('RGB'), (x + (274 - photo.width) // 2, y + (177 - photo.height) // 2))
        except Exception as error:
            draw.text((x + 5, y + 20), 'Preview unavailable', font=font, fill='#994433')
        name = path.name
        if len(name) > 31:
            name = name[:28] + '...'
        reference = batch_start + offset + 1
        draw.text((x + 3, y + 183), f'{reference:03d}  {name}', font=font, fill='#253e31')
        draw.text((x + 3, y + 204), f"{entry['width']} x {entry['height']}", font=font, fill='#526050')
        index.append({'reference': reference, 'sheet': f'contact-sheet-{number:02d}.jpg', 'file': entry['file'], 'source_url': entry['url'], 'source_pages': entry['source_pages']})
    filename = f'contact-sheet-{number:02d}.jpg'
    sheet.save(output / filename, quality=87, optimize=True)
    print(f'Created {filename}: {len(batch)} images', flush=True)
(output / 'index.json').write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Indexed {len(photos)} unique photos across {total_sheets} contact sheets.', flush=True)
