"""Island colours from their covers: each island (and sub-island) is tinted by the colours of the art it holds.

For every cover in the sprite sheets (tiles/t<sheet>.webp, 8 columns of 108x160 cells; square cells for albums)
the colourful part is found: pixels are weighed by their chroma, so a dark cover with one red title reads red,
faintly, and a grey one reads grey. Each work gives a colour direction (hue) and a strength (how colourful the
cover is). An island's hue is the one its covers have more of than covers in general (they all share a warm
cast); its strength is how vivid its covers are and how much they agree, so clashing covers fade toward grey,
which is what a mixed island should look like, and grey covers stay grey.
Writes `tint: [hue in degrees (CIE LCh), strength 0-1]` on every province and continent.
usage: python3 palette.py SITE_DIR
"""
import json, math, re, sys
from pathlib import Path
import numpy as np
from PIL import Image

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
COLS, CW, CH = 8, 108, 160

def lab(rgb):
    # sRGB (0-255) -> CIE Lab (D65)
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

sheets = {}
def cover(sp):
    s, cell, sq = sp[0], sp[1], sp[2] if len(sp) > 2 else 0
    if s not in sheets:
        sheets[s] = np.asarray(Image.open(SITE / 'tiles' / f't{s}.webp').convert('RGB'), dtype=np.float64)
    x, y = (cell % COLS) * CW, (cell // COLS) * CH
    px = sheets[s][y:y + (CW if sq else CH), x:x + CW]
    return px[::3, ::3].reshape(-1, 3)          # every third pixel is plenty for a colour

BINS = 36                                         # hue histogram, 10 degrees a bin
def work_colour(i):
    L = lab(cover(i['sp']))
    a, b = L[:, 1], L[:, 2]
    C = np.hypot(a, b)
    w = C ** 2                                    # colourful pixels lead
    strength = min(1.0, np.percentile(C, 80) / 45.0)   # how colourful the cover is, 0 (grey) to 1 (vivid)
    if w.sum() < 1e-6: return np.zeros(BINS), np.zeros(2), strength
    hb = (np.degrees(np.arctan2(b, a)) % 360 / (360 / BINS)).astype(int) % BINS
    hist = np.bincount(hb, weights=w, minlength=BINS); hist /= hist.sum()
    d = np.array([(a * w).sum(), (b * w).sum()]); d /= (np.hypot(*d) or 1)
    return hist * strength, d * strength, strength

items = {i['id']: i for i in W['items']}
col = {i['id']: work_colour(i) for i in W['items'] if i.get('sp') and i['st'] != 'planned'}
GLOBAL = np.mean([c[0] for c in col.values()], 0)
def smooth(h):                                    # a little blur around the hue circle
    return (np.roll(h, 1) + 2 * h + np.roll(h, -1)) / 4
CENTRES = (np.arange(BINS) + 0.5) * (360 / BINS)
# Covers share a warm cast (faces, titles, posters), so the plain average colour of nearly every island is
# orange. The hue is instead the one an island's covers have more of than covers in general; its strength
# is how vivid those covers are and how much they agree, so an island of grey covers stays grey.
def tint(ids, raw=False):
    cs = [col[x] for x in ids if x in col]
    if not cs: return None
    H = smooth(np.mean([c[0] for c in cs], 0)); G = smooth(GLOBAL)
    score = H * np.log((H + 1e-3) / (G + 1e-3))
    k = int(np.argmax(score))
    win = [(k + j) % BINS for j in range(-3, 4)]  # the hue: weighted mean within 30 degrees of the peak
    ang = np.radians(CENTRES[win]); wts = H[win]
    hue = math.degrees(math.atan2((np.sin(ang) * wts).sum(), (np.cos(ang) * wts).sum())) % 360
    vivid = float(np.mean([c[2] for c in cs]))
    agree = float(np.hypot(*np.mean([c[1] for c in cs], 0)) / (np.mean([np.hypot(*c[1]) for c in cs]) or 1))
    n = len(cs)
    v = vivid * (0.4 + 0.6 * agree) * (n / (n + 2))   # a couple of covers say less than twenty
    if raw: return v
    return [round(hue, 1), round(min(1.0, v / SPREAD), 3)]

# strength is scaled so the most distinctive islands (top tenth) reach full colour
fams = [list(p['items']) + [x for q in W['provinces'] if q.get('parent') == p['id'] for x in q['items']] for p in W['provinces'] if not p.get('parent')]
SPREAD = float(np.percentile([t for t in (tint(f, raw=True) for f in fams) if t is not None], 90))
for p in W['provinces']:
    own = list(p['items'])
    fam = own + [x for q in W['provinces'] if q.get('parent') == p['id'] for x in q['items']]
    p['tint'] = tint(own if p.get('parent') else fam) or tint(fam)
for c in W['continents']:
    c['tint'] = tint([x for p in W['provinces'] if p['c'] == c['id'] for x in p['items']])

top = sorted((p for p in W['provinces'] if not p.get('parent') and p.get('tint')), key=lambda p: -p['tint'][1])
print(f"{len(col)} covers read; most colourful {top[0]['name']} {top[0]['tint']}, greyest {top[-1]['name']} {top[-1]['tint']}")
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
