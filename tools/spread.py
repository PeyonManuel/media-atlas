"""Make room on each island so no two works' objects overlap when zoomed in.

Each work's drawn footprint (cover, case, fanned expansions) comes from tools/boxes.json, measured in the
page by tools/tests/export_boxes.py. Within each island family (an island and its sub-islands), works that
run into each other are pushed apart along the shorter overlap, a little at a time, until every pair keeps a
small gap (a wider one between different sub-islands, so their moats stay). Islands grow outward as needed;
the island spacing steps that follow keep grown islands clear of their neighbours. Unexplored landmarks take
part as small boxes so covers don't land on them either.
usage: python3 tools/spread.py SITE_DIR
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
BOX = json.loads((Path(__file__).parent / 'boxes.json').read_text())
items = {i['id']: i for i in W['items']}
provs = {p['id']: p for p in W['provinces']}
top = lambda pid: provs[pid].get('parent') or pid

GAP_SAME, GAP_OTHER, GAP_GHOST = 1.0, 3.2, 0.6
GHOST = [-2.4, -2.4, 2.4, 2.4]
dflt = [-4.5, -6.5, 4.5, 6.5]

kids = defaultdict(list)
for i in W['items']:
    if i.get('dl'): kids[i['dl']].append(i)

moved_total, worst_left = 0.0, 0.0
fams = defaultdict(list)
for p in W['provinces']: fams[top(p['id'])].append(p)
for fid, fam in fams.items():
    ents = []   # (object, kind, province, box)
    for q in fam:
        for x in q['items']:
            w = items[x]
            if w.get('dl'): continue
            ents.append((w, 'w', q['id'], BOX.get(x, dflt)))
        for g in q['canon']:
            if g.get('px') is not None: ents.append((g, 'g', q['id'], GHOST))
    n = len(ents)
    if n < 2: continue
    P = np.array([[e[0]['px'], e[0]['py']] for e in ents], float)
    P0 = P.copy()
    R = np.array([e[3] for e in ents], float)
    prov = np.array([hash(e[2]) for e in ents])
    ghost = np.array([e[1] == 'g' for e in ents])
    G = np.where(prov[:, None] == prov[None, :], GAP_SAME, GAP_OTHER)
    G = np.where(ghost[:, None] | ghost[None, :], GAP_GHOST, G)
    np.fill_diagonal(G, 0)
    tie = np.sign(np.arange(n)[:, None] - np.arange(n)[None, :]).astype(float)
    for it in range(600):
        x0 = P[:, 0] + R[:, 0]; x1 = P[:, 0] + R[:, 2]; y0 = P[:, 1] + R[:, 1]; y1 = P[:, 1] + R[:, 3]
        ox = np.minimum(x1[:, None], x1[None]) - np.maximum(x0[:, None], x0[None]) + G
        oy = np.minimum(y1[:, None], y1[None]) - np.maximum(y0[:, None], y0[None]) + G
        hit = (ox > 0.02) & (oy > 0.02)
        np.fill_diagonal(hit, False)
        if not hit.any(): break
        cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
        sx = np.sign(cx[:, None] - cx[None]); sx = np.where(sx == 0, tie, sx)
        sy = np.sign(cy[:, None] - cy[None]); sy = np.where(sy == 0, tie, sy)
        alongx = hit & (ox <= oy); alongy = hit & (ox > oy)
        # each of the pair moves half the overlap; spread over many neighbours, so damp a little
        dx = (np.where(alongx, ox * sx, 0) * 0.5).sum(1)
        dy = (np.where(alongy, oy * sy, 0) * 0.5).sum(1)
        cnt = np.maximum(1, hit.sum(1))
        P[:, 0] += dx / np.sqrt(cnt) * 0.9; P[:, 1] += dy / np.sqrt(cnt) * 0.9
    else:
        worst_left = max(worst_left, float(np.minimum(ox, oy)[hit].max()))
    D = P - P0
    moved_total += float(np.hypot(D[:, 0], D[:, 1]).sum())
    for (o, kind, pid, _), (nx, ny), (ddx, ddy) in zip(ents, P, D):
        o['px'], o['py'] = round(float(nx), 1), round(float(ny), 1)
        if kind == 'w':
            for k in kids[o['id']]: k['px'] = round(k['px'] + ddx, 1); k['py'] = round(k['py'] + ddy, 1)

allx = [i['px'] for i in W['items']] + [g['px'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
ally = [i['py'] for i in W['items']] + [g['py'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
W['bounds'] = [round(min(allx), 1), round(min(ally), 1), round(max(allx), 1), round(max(ally), 1)]
print(f'works spread: {moved_total:.0f} units moved in all, largest overlap left {worst_left:.1f}')
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
