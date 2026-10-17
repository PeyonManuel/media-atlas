"""Last layout step: works whose drawn footprints (tools/boxes.json) still overlap are nudged apart.

The island passes keep islands from touching, but two covers on facing coasts can still brush by a few units;
this moves just those works, half the overlap each, along the axis with the smaller overlap.
usage: python3 apart.py SITE_DIR
"""
import json, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
BOX = json.loads((Path(__file__).parent / 'boxes.json').read_text())
dflt = [-6.0, -9.0, 6.0, 9.0]
ws = [i for i in W['items'] if i.get('sp') and not i.get('dl')]
moved = 0
for _ in range(30):
    hit = 0
    ws.sort(key=lambda i: i['px'])
    for a_i, a in enumerate(ws):
        ba = BOX.get(a['id'], dflt)
        for b in ws[a_i + 1:]:
            if b['px'] - a['px'] > 60: break
            bb = BOX.get(b['id'], dflt)
            ox = min(a['px'] + ba[2], b['px'] + bb[2]) - max(a['px'] + ba[0], b['px'] + bb[0])
            oy = min(a['py'] + ba[3], b['py'] + bb[3]) - max(a['py'] + ba[1], b['py'] + bb[1])
            if ox <= 0.2 or oy <= 0.2: continue
            hit += 1; moved += 1
            if ox < oy:
                s = (ox / 2 + 0.6) * (1 if a['px'] <= b['px'] else -1)
                a['px'] = round(a['px'] - s, 1); b['px'] = round(b['px'] + s, 1)
            else:
                s = (oy / 2 + 0.6) * (1 if a['py'] <= b['py'] else -1)
                a['py'] = round(a['py'] - s, 1); b['py'] = round(b['py'] + s, 1)
    if not hit: break
js = json.dumps(W, ensure_ascii=False, separators=(',', ':'))
(SITE / 'index.html').write_text(html[:m.start(2)] + js + html[m.end(2):])
print(f'works nudged apart: {moved}')
