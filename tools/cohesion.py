"""Island-level layout for cohesion: continents reshape around what is related.

Every top-level island (with its sub-islands and landmarks) is a rigid piece. Starting from the continent
arrangement, the pieces move under four forces:
  - affinity: related islands are drawn together until their nearest works are an island-gap apart.
    Relations come from portals, genre neighbours, border preferences (an island toward a continent) and
    shared creators (the same author, director, studio or composer on both islands);
  - cohesion: each island is held toward the middle of its own continent, so continents stay one piece;
  - collision: islands never come closer than an island gap (more between unrelated continents);
  - inertia: small steps, so the overall arrangement of the continents is kept.
A continent's coastline is drawn from its works, so its shape follows its islands.
usage: python3 cohesion.py SITE_DIR
"""
import json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}
provs = {p['id']: p for p in W['provinces']}
byname = {p['name']: p for p in W['provinces']}
top = lambda pid: provs[pid].get('parent') or pid

sys.path.insert(0, str(Path(__file__).parent))
from continents_links import LINKS, NEIGHBOURS, BORDER

# --- pieces ---
tops = [p for p in W['provinces'] if not p.get('parent') and (p['items'] or any(q.get('parent') == p['id'] for q in W['provinces']))]
idx = {p['id']: n for n, p in enumerate(tops)}
fam = {p['id']: [p] + [q for q in W['provinces'] if q.get('parent') == p['id']] for p in tops}
works = {pid: [items[x] for q in fam[pid] for x in q['items']] for pid in idx}
ghosts = {pid: [g for q in fam[pid] for g in q['canon'] if g.get('px') is not None] for pid in idx}
pts = [np.array([[w['px'], w['py']] for w in works[p['id']] if not w.get('dl')] or [[p['x'], p['y']]]) for p in tops]
N = len(tops)
cont = [p['c'] for p in tops]
size = np.array([len(x) for x in pts], float)
off = np.zeros((N, 2))

# --- relations ---
aff = defaultdict(float)
def rel(a, b, w):
    if a in idx and b in idx and a != b:
        k = tuple(sorted((idx[a], idx[b]))); aff[k] = max(aff[k], w)
for pt in W.get('portals', []):
    dest = pt.get('to') or items[pt['item']]['p']
    rel(top(pt['from']), top(dest), 1.0)
for a, b in NEIGHBOURS:
    if a in byname and b in byname: rel(top(byname[a]['id']), top(byname[b]['id']), 1.4)
creators = {p['id']: Counter(w['c'] for w in works[p['id']] if w.get('c') and w['c'] not in ('Various Artists',)) for p in tops}
by_creator = defaultdict(set)
for pid, cs in creators.items():
    for c in cs: by_creator[c].add(pid)
shared = defaultdict(int)
for c, ps in by_creator.items():
    ps = sorted(ps)
    if len(ps) > 4: continue                       # prolific names spread everywhere tell us little
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)): shared[(ps[i], ps[j])] += 1
for (a, b), n in shared.items(): rel(a, b, min(0.9, 0.3 * n))
border = defaultdict(list)                          # island -> continents it should face
for name, c in BORDER:
    if name in byname: border[idx.get(top(byname[name]['id']))].append(c)
link = {tuple(sorted(l)) for l in LINKS}

ISL = 38.0          # island gap within a continent
GAP_LINKED, GAP_FAR = 30.0, 46.0

def nearest(a, b):
    pa, pb = pts[a] + off[a], pts[b] + off[b]
    d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1))
    k = np.unravel_index(d.argmin(), d.shape)
    return d[k]

def gap(a, b):
    if cont[a] == cont[b]: return ISL
    return GAP_LINKED if tuple(sorted((cont[a], cont[b]))) in link else GAP_FAR

rad = np.array([np.sqrt(((x - x.mean(0)) ** 2).sum(1)).max() for x in pts])
cen0 = np.array([x.mean(0) for x in pts])
cmid0 = {}; crad = {}
for c in set(cont):
    ids = [a for a in range(N) if cont[a] == c]
    w = size[ids]; mid = (cen0[ids] * w[:, None]).sum(0) / w.sum()
    cmid0[c] = mid
    crad[c] = max(math.hypot(*(cen0[a] - mid)) for a in ids) * 1.04 + 1
from continents_links import SKETCH
# Growth: each continent is rebuilt island by island around its biggest island. A new island is set at
# the free spot touching the land so far that costs least: distance to the islands it relates to (already
# placed), a pull toward the side facing continents it relates to, and a little toward the middle so the
# continent stays compact. Islands are treated as discs here; the settle pass below uses the real works.
nbr = defaultdict(list)
for (a_, b_), w in aff.items(): nbr[a_].append((b_, w)); nbr[b_].append((a_, w))
pull_dir = defaultdict(lambda: np.zeros(2))         # island -> preferred direction (toward related continents)
for a_ in range(N):
    for b_, w in nbr[a_]:
        if cont[b_] != cont[a_]:
            v = np.array(SKETCH[cont[b_]]) - np.array(SKETCH[cont[a_]]); n_ = math.hypot(*v)
            if n_: pull_dir[a_] += v / n_ * w * 0.08   # portals already bridge these; only a hint
for a_, cs in border.items():
    if a_ is None: continue
    for c in cs:
        v = np.array(SKETCH[c]) - np.array(SKETCH[cont[a_]]); n_ = math.hypot(*v)
        if n_: pull_dir[a_] += v / n_ * 1.3
R = rad + SP_ * 0.5 if 'SP_' in globals() else rad + 6
pos = cen0.copy()
for c in set(cont):
    ids = [a_ for a_ in range(N) if cont[a_] == c]
    if len(ids) < 2: continue
    mid = cmid0[c]
    order = [max(ids, key=lambda a_: size[a_])]
    placed = {order[0]: np.zeros(2)}
    rest = set(ids) - set(order)
    while rest:
        # next: the island most tied to what is placed, then the biggest
        nxt = max(rest, key=lambda a_: (sum(w for b_, w in nbr[a_] if b_ in placed), size[a_]))
        best, bc = None, 1e18
        span = math.sqrt(sum(size[b_] for b_ in placed))
        for b_, pb in placed.items():
            for k in range(24):
                ang = 2 * math.pi * k / 24
                d = R[b_] + R[nxt] + ISL * 0.75
                cand = pb + d * np.array([math.cos(ang), math.sin(ang)])
                if any(math.hypot(*(cand - q)) < R[o] + R[nxt] + ISL * 0.7 for o, q in placed.items()): continue
                cost = sum(w * math.hypot(*(cand - placed[o])) for o, w in nbr[nxt] if o in placed)
                cost += 0.35 * math.hypot(*cand)                                   # compact
                pd = pull_dir[nxt]
                if pd.any(): cost -= (cand @ pd) * 0.5                             # toward related continents
                if cost < bc: bc, best = cost, cand
        placed[nxt] = best; rest.discard(nxt)
    # the grown continent keeps its weighted middle where the arrangement put it
    wsum = sum(size[a_] for a_ in ids)
    shift = mid - sum(placed[a_] * size[a_] for a_ in ids) / wsum
    for a_ in ids: pos[a_] = placed[a_] + shift
off += pos - cen0
print('continents regrown', end='; ')

# Settle: the real works must keep an island gap; related islands in a continent ease together a little.
before = {k: nearest(*k) for k in aff}
for it in range(120):
    cen = cen0 + off
    step = np.zeros((N, 2))
    for a in range(N):
        for b in range(a + 1, N):
            if cont[a] != cont[b]: continue
            v = cen[b] - cen[a]; dc = math.hypot(*v)
            if dc > rad[a] + rad[b] + ISL: continue
            d = nearest(a, b)
            if d < ISL:
                u = v / (dc or 1e-6); push = (ISL - d) * 0.5 + 0.3
                fa = size[b] / (size[a] + size[b])
                step[a] -= u * push * fa; step[b] += u * push * (1 - fa)
    for (a, b), w in aff.items():
        if cont[a] != cont[b]: continue
        d = nearest(a, b)
        if d > ISL * 1.15:
            v = cen[b] - cen[a]; u = v / (math.hypot(*v) or 1e-6)
            pull = min(4.0, (d - ISL) * 0.05) * w
            fa = size[b] / (size[a] + size[b])
            step[a] += u * pull * fa; step[b] -= u * pull * (1 - fa)
    for c in set(cont):                               # keep each continent compact around its middle
        ids = [a for a in range(N) if cont[a] == c]
        w_ = size[ids]; mid = (cen[ids] * w_[:, None]).sum(0) / w_.sum()
        for a in ids: step[a] += (mid - cen[a]) * 0.01
    off += np.clip(step, -6, 6)

# report: how much closer related islands got
closer = sum(1 for k, w in aff.items() if before[k] is not None and nearest(*k) < before[k] - 1)
print(f'{len(aff)} relations, {closer} drawn closer; {N} islands')

for a, p in enumerate(tops):
    dx, dy = float(off[a][0]), float(off[a][1])
    for q in fam[p['id']]:
        q['x'] = round(q['x'] + dx, 1); q['y'] = round(q['y'] + dy, 1)
    for w in works[p['id']]: w['px'] = round(w['px'] + dx, 1); w['py'] = round(w['py'] + dy, 1)
    for g in ghosts[p['id']]: g['px'] = round(g['px'] + dx, 1); g['py'] = round(g['py'] + dy, 1)
for co in W['continents']:
    ws = [items[x] for p in W['provinces'] if p['c'] == co['id'] for x in p['items'] if not items[x].get('dl')]
    if not ws: continue
    x0, x1 = min(w['px'] for w in ws), max(w['px'] for w in ws); y0, y1 = min(w['py'] for w in ws), max(w['py'] for w in ws)
    co['x'], co['y'] = round((x0 + x1) / 2, 1), round((y0 + y1) / 2, 1)
    co['r'] = round(max(math.hypot(w['px'] - co['x'], w['py'] - co['y']) for w in ws) + 30, 1)
allx = [i['px'] for i in W['items']] + [g['px'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
ally = [i['py'] for i in W['items']] + [g['py'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
W['bounds'] = [round(min(allx), 1), round(min(ally), 1), round(max(allx), 1), round(max(ally), 1)]
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
