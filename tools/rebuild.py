"""Rebuild the world data of the site (../index.html) from the original survey data.

The page's code is kept from index.html; only its embedded world data is replaced, starting each time
from the data in base-world.html, so every step can be rerun safely.
usage: python3 tools/rebuild.py
"""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
SITE = HERE.parent
pat = r'(<script type="application/json" id="world">)(.*?)(</script>)'
cur = (SITE / 'index.html').read_text()
orig = (HERE / 'base-world.html').read_text()
mo, mc = re.search(pat, orig, re.S), re.search(pat, cur, re.S)
(SITE / 'index.html').write_text(cur[:mc.start(2)] + mo.group(2) + cur[mc.end(2):])
# spread makes room for big covers; the last cohesion pass only keeps islands from running into each other
for step in ('fixes.py', 'subisles.py', 'series.py', 'media.py', 'spread.py', 'continents.py', 'portals.py', 'cohesion.py', 'continents.py',
             'pairs.py', 'spread.py', 'cohesion.py settle', 'blurbs.py'):
    script, *args = step.split()
    out = subprocess.run([sys.executable, str(HERE / script), str(SITE), *args], capture_output=True, text=True)
    if out.returncode: sys.exit(f'{step} failed:\n{out.stderr}')
    print(f'{step}: ' + (out.stdout.strip().splitlines() or [''])[-1])
