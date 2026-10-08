"""Group works by medium inside each island: on an island that mixes media, each medium takes one wedge of
the island (the biggest first), so films sit with films, games with games, and so on. The island's spots
stay where they are; only who stands on which spot changes. Series stay together inside their medium's
wedge, read in release order. Runs after series.py, on every island and sub-island on its own.
usage: python3 tools/media.py SITE_DIR
"""
import json, math, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import series as SER

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}

def gather(works, slots):
    """Seat works on slots (a list of positions), series together, everyone else as near their spot as can be."""
    free = list(slots)
    assign = {}
    gs = [g for g in SER.groups_in([w for w in works if w['m'] != 'music']) if len(g) >= 2]
    for g in sorted(gs, key=len, reverse=True):
        if any(w['id'] in assign for w in g) or len(g) > len(free): continue
        g.sort(key=lambda w: (w.get('y') or 9999, w['t']))
        cx = sum(w['px'] for w in g) / len(g); cy = sum(w['py'] for w in g) / len(g)
        anchor = min(free, key=lambda q: math.hypot(q[0] - cx, q[1] - cy))
        near = sorted(free, key=lambda q: math.hypot(q[0] - anchor[0], q[1] - anchor[1]))[:len(g)]
        xs = [q[0] for q in near]; ys = [q[1] for q in near]
        ax = 0 if max(xs) - min(xs) >= max(ys) - min(ys) else 1
        near.sort(key=lambda q: q[ax])
        for w, q in zip(g, near): assign[w['id']] = q; free.remove(q)
    for w in sorted((w for w in works if w['id'] not in assign), key=lambda w: -(w.get('r') or 0)):
        q = min(free, key=lambda q: math.hypot(q[0] - w['px'], q[1] - w['py']))
        assign[w['id']] = q; free.remove(q)
    return assign

islands = moved = 0
kids = {}
for i in W['items']:
    if i.get('dl'): kids.setdefault(i['dl'], []).append(i)
for p in W['provinces']:
    works = [items[x] for x in p['items'] if not items[x].get('dl')]
    count = Counter(w['m'] for w in works)
    if len(works) < 4 or len(count) < 2: continue
    islands += 1
    slots = [(w['px'], w['py']) for w in works]
    cx = sum(q[0] for q in slots) / len(slots); cy = sum(q[1] for q in slots) / len(slots)
    order = [mm for mm, _ in count.most_common()]
    # start the wedges where the biggest medium already mostly is, so the island turns as little as possible
    big = [w for w in works if w['m'] == order[0]]
    a0 = math.atan2(sum(w['py'] for w in big) / len(big) - cy, sum(w['px'] for w in big) / len(big) - cx)
    span0 = math.pi * count[order[0]] / len(works)
    ang = lambda q: (math.atan2(q[1] - cy, q[0] - cx) - (a0 - span0)) % (2 * math.pi)
    ring = sorted(slots, key=ang)
    assign, n = {}, 0
    for mm in order:
        ws = [w for w in works if w['m'] == mm]
        part = ring[n:n + len(ws)]; n += len(ws)
        assign.update(gather(ws, part))
    for w in works:
        q = assign[w['id']]
        if (w['px'], w['py']) != q:
            moved += 1
            dx, dy = q[0] - w['px'], q[1] - w['py']
            for k in kids.get(w['id'], []): k['px'] = round(k['px'] + dx, 1); k['py'] = round(k['py'] + dy, 1)
            w['px'], w['py'] = q
print(f'{islands} mixed islands grouped by medium, {moved} works moved')
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
