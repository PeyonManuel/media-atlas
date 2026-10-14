"""The canon: works Manuel holds closest, whatever their score (he sees himself in them; not a favourites list).
tools/canon.json maps each work id to the title as he named it. Sets `canon: 1` on those works.
usage: python3 canon.py SITE_DIR
"""
import json, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
CANON = json.loads((Path(__file__).parent / 'canon.json').read_text())
items = {i['id']: i for i in W['items']}
for i in W['items']: i.pop('canon', None)
missing = [k for k in CANON if k not in items]
for k in CANON:
    if k in items: items[k]['canon'] = 1
print(f'{len(CANON) - len(missing)} works in the canon' + (f', missing: {missing}' if missing else ''))
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
