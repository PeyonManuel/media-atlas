"""Attach the short island and sub-island descriptions (blurbs.json: id -> [English, Spanish])."""
import json, re, sys
from pathlib import Path
SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
B = json.loads((Path(__file__).parent / 'blurbs.json').read_text())
missing = []
for p in W['provinces']:
    if p['id'] in B: p['blurb'], p['blurb_es'] = B[p['id']]
    else: missing.append(p['name'])
print(f"{len(W['provinces']) - len(missing)} described" + (f", missing: {missing}" if missing else ''))
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
