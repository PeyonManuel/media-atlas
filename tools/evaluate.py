"""How cohesive is the layout: gaps between islands that should touch, and border islands' distance to their neighbour."""
import json, math, re, sys
import numpy as np
sys.path.insert(0, '.')
from continents_links import NEIGHBOURS, BORDER
W = json.loads(re.search(r'id="world">(.*?)</script>', open(sys.argv[1] + '/index.html' if len(sys.argv) > 1 else 'index.html').read(), re.S).group(1))
it = {i['id']: i for i in W['items']}; P = {p['id']: p for p in W['provinces']}; B = {p['name']: p for p in W['provinces']}
top = lambda pid: P[pid].get('parent') or pid
def pts(pid):
    return np.array([[it[x]['px'], it[x]['py']] for q in W['provinces'] if q['id'] == pid or q.get('parent') == pid for x in q['items']])
def gap(a, b):
    pa, pb = pts(a), pts(b)
    return np.sqrt(((pa[:, None] - pb[None]) ** 2).sum(-1)).min()
rows = []
for a, b in NEIGHBOURS: rows.append((f'{a} ~ {b}', gap(top(B[a]['id']), top(B[b]['id']))))
for pt in W.get('portals', []):
    dest = pt.get('to') or it[pt['item']]['p']
    a, b = top(pt['from']), top(dest)
    if a != b and P[a]['c'] == P[b]['c']: rows.append((f"portal {P[a]['name']} -> {P[b]['name']}", gap(a, b)))
for n, c in BORDER:
    a = top(B[n]['id']); others = [q['id'] for q in W['provinces'] if q['c'] == c and not q.get('parent') and q['items']]
    rows.append((f'{n} faces {c}', min(gap(a, o) for o in others)))
for name, d in rows: print(f'{d:7.1f}  {name}')
print(f'mean {np.mean([d for _, d in rows]):.1f}, touching (<60): {sum(d < 60 for _, d in rows)}/{len(rows)}')
