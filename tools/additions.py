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
BOX = json.loads((Path(__file__).parent / 'boxes_apart.json').read_text())
dflt = [-6.0, -9.0, 6.0, 9.0]
DOT = [-3.0, -3.0, 3.0, 3.0]
GAP = 2.0

TIER = {9: 1.35, 10: 1.7}

def cover_box(i):
    k = TIER.get(i.get('r'), 1.0)               # a cover of its tier, unless the last export measured it larger
    sq = i['sp'][2]
    e = [-6 * k, -(6 if sq else 9) * k, 6 * k, (6 if sq else 9) * k]
    b = BOX.get(i['id'])
    return [min(e[0], b[0]), min(e[1], b[1]), max(e[2], b[2]), max(e[3], b[3])] if b else e

def box(i):
    b = cover_box(i) if i.get('sp') else DOT
    return [i['px'] + b[0], i['py'] + b[1], i['px'] + b[2], i['py'] + b[3]]

def free(x, y, me_box=DOT):
    me = [x + me_box[0] - GAP, y + me_box[1] - GAP, x + me_box[2] + GAP, y + me_box[3] + GAP]
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
    mybox = cover_box({'id': a['id'], 'r': a['r'], 'sp': a['sp']}) if a.get('sp') else DOT
    for k in range(0, 400):                    # outward spiral from the medium's centre
        r = 4 * math.sqrt(k); t = k * 2.399963
        x, y = cx + r * math.cos(t), cy + r * math.sin(t)
        if free(x, y, mybox): spot = (round(x, 1), round(y, 1)); break
    if spot is None: sys.exit(f"no free spot for {a['t']}")
    n = {'id': a['id'], 'm': a['m'], 't': a['t'], 'c': a['c'], 'y': a['y'], 'r': a['r'], 'crowd': None, 'st': a['st'],
         'p': a['p'], 'src': a['src'], 'sid': a['sid'], 'px': spot[0], 'py': spot[1]}
    for k in ('sp', 'len', 'mins', 'seasons'):
        if k in a: n[k] = a[k]
    for pr in W['provinces']:                  # a wanted-work placeholder for this title is now a real work
        pr['canon'] = [c for c in pr.get('canon', []) if not (c['t'].replace('Batman: ', '') == a['t'].replace('Batman: ', '') and not c.get('seen'))]
    W['items'].append(n); items[a['id']] = n; isle['items'].append(a['id']); added += 1
    mm = isle.setdefault('media', {}); mm[a['m']] = mm.get(a['m'], 0) + 1
js = json.dumps(W, ensure_ascii=False, separators=(',', ':'))
(SITE / 'index.html').write_text(html[:m.start(2)] + js + html[m.end(2):])
print(f'works added: {added}')
