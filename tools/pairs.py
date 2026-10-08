"""Works that share a portal sit together, on the coast that faces where the portal leads.

For each portal made by several works of one island, those works trade places with their neighbours
(swaps between works of the same island, so the island's shape is kept) until they are a compact group
on the shore facing the portal's destination.
usage: python3 pairs.py SITE_DIR
"""
import json, math, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}
provs = {p['id']: p for p in W['provinces']}

def fam_works(pid):
    return [items[x] for q in W['provinces'] if q['id'] == pid or q.get('parent') == pid for x in q['items']]

done = 0
locked = set()        # works already seated in a group stay put
for o in W.get('portals', []):
    via = o.get('via') or []
    if len(via) < 2: continue
    ws = [items[v] for v in via if v in items]
    pid = ws[0]['p']
    if any(w['p'] != pid for w in ws): continue            # spread over sub-islands: leave them be
    spots = [items[x] for x in provs[pid]['items'] if not items[x].get('dl')]
    dest = provs[o['to']]
    dws = fam_works(dest['id'])
    tx = sum(w['px'] for w in dws) / len(dws); ty = sum(w['py'] for w in dws) / len(dws)
    cx = sum(w['px'] for w in spots) / len(spots); cy = sum(w['py'] for w in spots) / len(spots)
    ux, uy = tx - cx, ty - cy; n = math.hypot(ux, uy) or 1; ux /= n; uy /= n
    # the anchor: the island's spot furthest toward the destination; the group takes it and its nearest spots
    anchor = max(spots, key=lambda w: (w['px'] - cx) * ux + (w['py'] - cy) * uy)
    free_ = [w for w in spots if w['id'] not in locked or w['id'] in via]
    anchor = max(free_, key=lambda w: (w['px'] - cx) * ux + (w['py'] - cy) * uy)
    target = sorted(free_, key=lambda w: math.hypot(w['px'] - anchor['px'], w['py'] - anchor['py']))[:len(ws)]
    tpos = [(t['px'], t['py']) for t in target]
    group = set(v for v in via)
    for g, (px, py) in zip(sorted(ws, key=lambda w: (w['px'] - cx) * ux + (w['py'] - cy) * uy, reverse=True), tpos):
        if (g['px'], g['py']) == (px, py): continue
        occ = next((w for w in spots if (w['px'], w['py']) == (px, py)), None)
        if occ is not None and occ['id'] not in group and occ['id'] not in locked:
            occ['px'], occ['py'], g['px'], g['py'] = g['px'], g['py'], px, py
        elif occ is None:
            g['px'], g['py'] = px, py
    locked.update(via)
    done += 1
print(f'{done} groups gathered')
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
