"""Islands of different families that run into each other: pairs whose nearest works are closer than a gap.

usage: python3 tools/overlaps.py SITE_DIR [GAP]
"""
import json, re, sys
import numpy as np

W = json.loads(re.search(r'id="world">(.*?)</script>', open(sys.argv[1] + '/index.html').read(), re.S).group(1))
it = {i['id']: i for i in W['items']}; pv = {p['id']: p for p in W['provinces']}
top = lambda pid: pv[pid].get('parent') or pid
fam = {}
for p in W['provinces']:
    for x in p['items']:
        if not it[x].get('dl'): fam.setdefault(top(p['id']), []).append((it[x]['px'], it[x]['py']))
ids = list(fam); P = {k: np.array(v) for k, v in fam.items()}
gap = float(sys.argv[2]) if len(sys.argv) > 2 else 20
bad = []
for a in range(len(ids)):
    for b in range(a + 1, len(ids)):
        A, B = P[ids[a]], P[ids[b]]
        if np.abs(A.mean(0) - B.mean(0)).max() > 300: continue
        d = np.sqrt(((A[:, None] - B[None]) ** 2).sum(-1)).min()
        if d < gap: bad.append((round(float(d), 1), pv[ids[a]]['name'], pv[ids[a]]['c'], pv[ids[b]]['name'], pv[ids[b]]['c']))
for x in sorted(bad): print(x)
print(len(bad), 'pairs closer than', gap)
