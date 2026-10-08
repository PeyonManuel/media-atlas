"""Gather the works of one series into neighbouring spots on their island.

Series are found from titles: Goodreads' "(Series, #n)" tags, and shared title stems ("Dark Souls" /
"Dark Souls III", "Toy Story" / "Toy Story 2", "Attack on Titan" / "Attack on Titan: No Regrets").
Within each province (island) every work keeps one of the island's existing spots, so the coastline and
hills don't change; series members are moved onto a compact run of neighbouring spots, in release order,
and everything else keeps its own spot where it can. A series that makes up most of its island already
has the island to itself and is left alone. Music is left out (an artist's discography isn't a series).

usage: python3 series.py SITE_DIR [--dry]
"""
import json, math, re, sys, unicodedata
from collections import defaultdict
from pathlib import Path


ROMAN = r'(?:i{1,3}|iv|v|vi{0,3}|ix|x)'
STOP = {'the', 'a', 'an', 'of', 'and', 'in', 'to', 'part', 'vol', 'volume', 'season', 'chapter', 'book', 'episode'}

def norm(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    t = t.replace('&', ' and ')
    return re.sub(r'[^a-z0-9: ]+', ' ', t)

def tag_series(t):
    mm = re.search(r'\(([^()#]+?),?\s*#\s*[\d.]+[^()]*\)\s*$', t)
    return norm(mm.group(1)).strip() if mm else None

def stem_words(t):
    t = re.sub(r'\([^)]*\)', ' ', t)          # drop parentheticals (years, series tags, editions)
    t = norm(t).split(':')[0]                 # the part before a subtitle
    w = t.split()
    while w and (re.fullmatch(r'\d+|' + ROMAN, w[-1]) or w[-1] in STOP):  # trailing numbers / roman numerals
        w.pop()
    while w and w[0] in ('the', 'a', 'an'):
        w.pop(0)
    return w

def significant(words):
    # a stem worth matching on: two or more words, or one long distinctive word
    content = [x for x in words if x not in STOP]
    return len(content) >= 2 or (len(content) == 1 and len(content[0]) >= 5)

def series_key(i):
    t = tag_series(i['t'])
    return ('tag', t) if t else ('stem', tuple(stem_words(i['t'])))

def groups_in(works):
    """Union works of one province into series."""
    parent = {w['id']: w['id'] for w in works}
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def union(a, b): parent[find(a)] = find(b)
    keys = {w['id']: series_key(w) for w in works}
    stems = {w['id']: stem_words(w['t']) for w in works}
    ws = list(works)
    for x in range(len(ws)):
        for y in range(x + 1, len(ws)):
            a, b = ws[x], ws[y]
            ka, kb = keys[a['id']], keys[b['id']]
            same = False
            if ka[0] == 'tag' and kb[0] == 'tag': same = ka[1] == kb[1]
            else:
                sa, sb = stems[a['id']], stems[b['id']]
                short, long_ = (sa, sb) if len(sa) <= len(sb) else (sb, sa)
                # one title's stem starts the other's, and the shared part is distinctive
                if short and significant(short) and long_[:len(short)] == short: same = True
                # a tagged book and an untagged title that names the series
                for k, s_ in ((ka, sb), (kb, sa)):
                    if k[0] == 'tag' and significant(k[1].split()) and ' '.join(s_).startswith(k[1]): same = True
            if same: union(a['id'], b['id'])
    out = defaultdict(list)
    for w in works: out[find(w['id'])].append(w)
    return [g for g in out.values() if len(g) >= 2]

def main():
    SITE, DRY = Path(sys.argv[1]), '--dry' in sys.argv
    html = (SITE / 'index.html').read_text()
    m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
    W = json.loads(m.group(2))
    byid = {i['id']: i for i in W['items']}
    moved = 0
    report = []
    for p in W['provinces']:
        works = [byid[x] for x in p['items'] if not byid[x].get('dl') and byid[x]['m'] != 'music']
        if len(works) < 3: continue
        gs = [g for g in groups_in(works) if len(g) / len(works) < 0.5]  # a series that IS the island is left be
        if not gs: continue
        allw = [byid[x] for x in p['items'] if not byid[x].get('dl')]
        slots = {w['id']: (w['px'], w['py']) for w in allw}
        free = dict(slots)                       # spot owner id -> position, still unclaimed
        assign = {}
        for g in sorted(gs, key=len, reverse=True):
            g.sort(key=lambda w: (w.get('y') or 9999, w['t']))
            cx = sum(slots[w['id']][0] for w in g) / len(g); cy = sum(slots[w['id']][1] for w in g) / len(g)
            anchor = min(free.values(), key=lambda q: math.hypot(q[0] - cx, q[1] - cy))
            near = sorted(free.items(), key=lambda kv: math.hypot(kv[1][0] - anchor[0], kv[1][1] - anchor[1]))[:len(g)]
            # read in release order along the run's longer axis
            xs = [q[1][0] for q in near]; ys = [q[1][1] for q in near]
            ax = 0 if max(xs) - min(xs) >= max(ys) - min(ys) else 1
            near.sort(key=lambda kv: kv[1][ax])
            for w, (owner, q) in zip(g, near):
                assign[w['id']] = q; del free[owner]
            report.append((p['name'], [w['t'] for w in g]))
        # everyone else: their own spot if still free, else the nearest free one
        rest = [w for w in allw if w['id'] not in assign]
        for w in rest:
            if w['id'] in free: assign[w['id']] = free.pop(w['id'])
        for w in rest:
            if w['id'] in assign: continue
            own = slots[w['id']]
            owner, q = min(free.items(), key=lambda kv: math.hypot(kv[1][0] - own[0], kv[1][1] - own[1]))
            assign[w['id']] = q; del free[owner]
        for w in allw:
            q = assign[w['id']]
            if (w['px'], w['py']) != q: moved += 1
            if not DRY: w['px'], w['py'] = q

    for name, titles in report:
        print(f'{name}: ' + ' | '.join(titles))
    print(f'{len(report)} series gathered, {moved} works moved')
    if not DRY:
        js = json.dumps(W, ensure_ascii=False, separators=(',', ':'))
        (SITE / 'index.html').write_text(html[:m.start(2)] + js + html[m.end(2):])

if __name__ == '__main__':
    main()
