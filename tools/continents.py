"""Arrange the continents by how they relate, as whole pieces.

Each continent moves rigidly (its islands keep their shape). They start from a rough sketch of the
intended arrangement; then related continents are pulled together until their coasts nearly touch, and
any two continents are pushed apart where their works come closer than islands normally sit. With no
pull between unrelated ones, the map stays a loose archipelago rather than a line.
usage: python3 continents.py SITE_DIR
"""
import json, math, re, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}

# Rough sketch, in units of ~one continent across: the capes in the middle with fantasy, the grim and
# action around them; horror and sport off the action coast; space past fantasy; crime beside the grim;
# the dreamy and heartfelt to the west; history, swords and the frontier together to the south.
from continents_links import SKETCH, LINKS
UNIT = 560.0

# Islands that belong on a particular border of their continent: they swap places with whichever island
# of theirs sits frontmost toward that neighbour (direction from the sketch), then the continent's islands
# settle so none overlap.
from continents_links import BORDER
ISL_GAP = 38.0
provs = {q['id']: q for q in W['provinces']}
byname = {q['name']: q for q in W['provinces']}
def group(q):
    fam = [q] + [k for k in W['provinces'] if k.get('parent') == q['id']]
    ws = [items[x] for k in fam for x in k['items']]
    gh = [g for k in fam for g in k['canon'] if g.get('px') is not None]
    return fam, ws, gh
def shift(fam, ws, gh, dx, dy):
    for w in ws: w['px'] += dx; w['py'] += dy
    for g in gh: g['px'] += dx; g['py'] += dy
    for k in fam: k['x'] += dx; k['y'] += dy
for name, toward in BORDER:
    q = byname.get(name)
    if not q: continue
    q = provs[q['parent']] if q.get('parent') else q
    cont = q['c']
    d = np.array(SKETCH[toward]) - np.array(SKETCH[cont]); d = d / (np.hypot(*d) or 1)
    tops = [k for k in W['provinces'] if k['c'] == cont and not k.get('parent') and group(k)[1]]
    G = {k['id']: group(k) for k in tops}
    cen_ = {k: np.array([[w['px'], w['py']] for w in G[k][1]]).mean(0) for k in G}
    front = max(G, key=lambda k: cen_[k] @ d)
    if front != q['id']:
        delta = cen_[front] - cen_[q['id']]
        shift(*G[q['id']], *delta); shift(*G[front], *(-delta))
    # settle: rigid islands pushed apart where their works come closer than the island gap
    ids = list(G)
    for it in range(300):
        moved = 0
        P_ = {k: np.array([[w['px'], w['py']] for w in G[k][1]]) for k in ids}
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                pa, pb = P_[ids[a]], P_[ids[b]]
                if np.hypot(*(pa.mean(0) - pb.mean(0))) > 400: continue
                dd = np.sqrt(((pa[:, None] - pb[None]) ** 2).sum(-1)).min()
                if dd < ISL_GAP:
                    v = pb.mean(0) - pa.mean(0); v = v / (np.hypot(*v) or 1)
                    push = (ISL_GAP - dd) * 0.5 + 0.5
                    fa = len(pb) / (len(pa) + len(pb))
                    if ids[a] == q['id']: fa *= 0.3          # the island being placed holds its border spot
                    if ids[b] == q['id']: fa = 1 - (1 - fa) * 0.3
                    shift(*G[ids[a]], *(-v * push * fa)); shift(*G[ids[b]], *(v * push * (1 - fa)))
                    P_[ids[a]] = P_[ids[a]] - v * push * fa; P_[ids[b]] = P_[ids[b]] + v * push * (1 - fa)
                    moved += 1
        if not moved: break

conts = [c['id'] for c in W['continents']]
pts = {}
for c in conts:
    ws = [i for p in W['provinces'] if p['c'] == c for i in (items[x] for x in p['items'])]
    gh = [g for p in W['provinces'] if p['c'] == c for g in p['canon'] if g.get('px') is not None]
    pts[c] = np.array([[w['px'], w['py']] for w in ws] + [[g['px'], g['py']] for g in gh])
cen = {c: pts[c].mean(0) for c in conts}

# measured island gap (as in the island layout): the nearest works of two continents keep at least this
GAP = 44.0
off = {c: np.array(SKETCH[c]) * UNIT - cen[c] for c in conts}
link = {tuple(sorted(l)) for l in LINKS}
for it in range(500):
    moved = 0
    for a in range(len(conts)):
        for b in range(a + 1, len(conts)):
            A, B = conts[a], conts[b]
            pa, pb = pts[A] + off[A], pts[B] + off[B]
            ca, cb = pa.mean(0), pb.mean(0)
            v = cb - ca; n = np.hypot(*v) or 1e-6; v = v / n
            # cheap reject: far apart and not linked
            ra = np.sqrt(((pa - ca) ** 2).sum(1)).max(); rb = np.sqrt(((pb - cb) ** 2).sum(1)).max()
            if n > ra + rb + GAP * 3 and tuple(sorted((A, B))) not in link: continue
            d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1)).min()
            wa, wb = len(pb) / (len(pa) + len(pb)), len(pa) / (len(pa) + len(pb))   # small ones move more
            linked = tuple(sorted((A, B))) in link
            gap = GAP * 0.62 if linked else GAP          # related continents run into each other a little
            if d < gap:
                push = (gap - d) * 0.6
                off[A] -= v * push * wa; off[B] += v * push * wb; moved += 1
            elif linked and d > gap * 1.15:
                pull = min(40.0, (d - gap * 1.05) * 0.08)
                off[A] += v * pull * wa; off[B] -= v * pull * wb; moved += 1
    if not moved and it > 30: break

for c in conts:
    dx, dy = float(off[c][0]), float(off[c][1])
    for p in W['provinces']:
        if p['c'] != c: continue
        p['x'] = round(p['x'] + dx, 1); p['y'] = round(p['y'] + dy, 1)
        for x in p['items']: items[x]['px'] = round(items[x]['px'] + dx, 1); items[x]['py'] = round(items[x]['py'] + dy, 1)
        for g in p['canon']:
            if g.get('px') is not None: g['px'] = round(g['px'] + dx, 1); g['py'] = round(g['py'] + dy, 1)
for co in W['continents']:
    ws = [items[x] for p in W['provinces'] if p['c'] == co['id'] for x in p['items'] if not items[x].get('dl')]
    if not ws: continue
    x0, x1 = min(w['px'] for w in ws), max(w['px'] for w in ws); y0, y1 = min(w['py'] for w in ws), max(w['py'] for w in ws)
    co['x'], co['y'] = round((x0 + x1) / 2, 1), round((y0 + y1) / 2, 1)
    co['r'] = round(max(math.hypot(w['px'] - co['x'], w['py'] - co['y']) for w in ws) + 30, 1)
allx = [i['px'] for i in W['items']] + [g['px'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
ally = [i['py'] for i in W['items']] + [g['py'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
W['bounds'] = [round(min(allx), 1), round(min(ally), 1), round(max(allx), 1), round(max(ally), 1)]
print(f'continents arranged after {it + 1} rounds')
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
