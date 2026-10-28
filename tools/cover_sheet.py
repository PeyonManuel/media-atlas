"""Builds tiles/t32.webp from the covers in tools/covers_src (one image per work added after the first survey, named by
its id) and writes the sprite cells (`sp` = [32, cell, square]) into tools/additions.json. Cells are 108x160; albums
and games' square art takes the top 108x108 of its cell, posters the whole cell. Images are centre-cropped to fit.
usage: python3 cover_sheet.py   (from the repo root)"""
import json, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).parent
SRC = ROOT / 'covers_src'
SHEET = 32
add = json.loads((ROOT / 'additions.json').read_text())
sheet = Image.new('RGBA', (864, 1280), (0, 0, 0, 0))
cell = 0
for a in add:
    f = next(iter(SRC.glob(a['id'] + '.*')), None)
    if f is None: a.pop('sp', None); continue
    sq = a['m'] == 'music'
    w, h = 108, (108 if sq else 160)
    im = Image.open(f).convert('RGB')
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2 if sq or True else 0
    im = im.crop((x, y, x + w, y + h))
    sheet.paste(im, ((cell % 8) * 108, (cell // 8) * 160))
    a['sp'] = [SHEET, cell, 1 if sq else 0]
    cell += 1
sheet.save(ROOT.parent / 'tiles' / f't{SHEET}.webp', quality=88)
(ROOT / 'additions.json').write_text(json.dumps(add, indent=1, ensure_ascii=False))
print(cell, 'covers on sheet', SHEET)
