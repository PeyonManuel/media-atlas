"""Works added after the first survey (Oct 2026), placed once the island layout is settled.

tools/additions.json lists them (Backloggd games, RateYourMusic albums), scored out of 10 (RYM stars: 5 = 10,
4.5 = 9, 4 = 8, 3.5 = 7). Adding them after the layout steps keeps the continents and islands where they were
(the layout depends on how many works each island holds). Each lands on its island next to works of its own
medium, on the nearest free spot. They have no cover sprite yet, so the page draws them as symbols.

usage: python3 additions.py SITE_DIR
"""
import json, math, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}
provs = {p['id']: p for p in W['provinces']}
BOX = json.loads((Path(__file__).parent / 'boxes.json').read_text())
dflt = [-6.0, -9.0, 6.0, 9.0]
DOT = [-3.0, -3.0, 3.0, 3.0]
GAP = 2.0

def box(i):
    b = BOX.get(i['id'], dflt) if i.get('sp') else DOT
    return [i['px'] + b[0], i['py'] + b[1], i['px'] + b[2], i['py'] + b[3]]

def free(x, y):
    me = [x + DOT[0] - GAP, y + DOT[1] - GAP, x + DOT[2] + GAP, y + DOT[3] + GAP]
    for o in W['items']:
        if abs(o['px'] - x) > 40 or abs(o['py'] - y) > 40: continue
        b = box(o)
        if min(me[2], b[2]) - max(me[0], b[0]) > 0 and min(me[3], b[3]) - max(me[1], b[1]) > 0: return False
    return True

added = 0
for a in json.loads((Path(__file__).parent / 'additions.json').read_text()):
    if a['id'] in items: continue
    isle = provs[a['p']]
    mine = [items[x] for x in isle['items'] if items[x]['m'] == a['m']] or [items[x] for x in isle['items']]
    cx = sum(i['px'] for i in mine) / len(mine); cy = sum(i['py'] for i in mine) / len(mine)
    spot = None
    for k in range(0, 400):                    # outward spiral from the medium's centre
        r = 4 * math.sqrt(k); t = k * 2.399963
        x, y = cx + r * math.cos(t), cy + r * math.sin(t)
        if free(x, y): spot = (round(x, 1), round(y, 1)); break
    if spot is None: sys.exit(f"no free spot for {a['t']}")
    n = {'id': a['id'], 'm': a['m'], 't': a['t'], 'c': a['c'], 'y': a['y'], 'r': a['r'], 'crowd': None, 'st': a['st'],
         'p': a['p'], 'src': a['src'], 'sid': a['sid'], 'px': spot[0], 'py': spot[1]}
    W['items'].append(n); items[a['id']] = n; isle['items'].append(a['id']); added += 1
    mm = isle.setdefault('media', {}); mm[a['m']] = mm.get(a['m'], 0) + 1
js = json.dumps(W, ensure_ascii=False, separators=(',', ':'))
(SITE / 'index.html').write_text(html[:m.start(2)] + js + html[m.end(2):])
print(f'works added: {added}')
