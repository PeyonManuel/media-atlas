"""Data fixes applied to the original world data before the island layout.

- Anime is not its own medium: anime films are Film, everything else anime (series, OVAs, specials) is TV.
  Series keep their runtime as `mins` (for "about N hours") and get an episode estimate as `len`.
- TV and anime scores are whole numbers out of 10.
- Misfiled works go where they belong (The Elephant Man was on Marvel Universe).

usage: python3 fixes.py SITE_DIR
"""
import json, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}
provs = {p['id']: p for p in W['provinces']}
byname = {p['name']: p for p in W['provinces']}

def recount(p):
    p['media'] = {}
    for x in p['items']:
        mm = items[x]['m']; p['media'][mm] = p['media'].get(mm, 0) + 1

films = series = 0
for i in W['items']:
    if i['m'] != 'anime': continue
    i['was'] = 'anime'
    if (i.get('fmt') or '').upper() == 'MOVIE':
        i['m'] = 'film'; films += 1
        i.pop('len', None); i.pop('ss', None)          # films carry no length
    else:
        i['m'] = 'tv'; series += 1
        if i.get('len'):
            i['mins'] = i['len']; i['len'] = max(1, round(i['len'] / 24))   # ~24-minute episodes
for i in W['items']:
    if i['m'] == 'tv' or i['src'] == 'anilist':
        if i.get('r'): i['r'] = max(1, round(i['r']))

# Shows split into one entry per season become one show. The kept entry is the show-level one
# (Serializd rates whole shows); the others fold into it as seasons.
MERGES = [
    # keep, absorb, title, seasons, episodes, minutes, island
    ('t1dc', ['a2w'], 'Hajime no Ippo: The Fighting!', 2, 76 + 26, 76 * 23 + 598, 'Kamogawa Gym'),
    ('t1dg', ['a41'], "Tomorrow's Joe", 2, 79 + 47, (79 + 47) * 24, "Tomorrow's Joe"),
]
for keep, absorb, title, ss, eps, mins, dest in MERGES:
    k = items[keep]
    k['t'] = title; k['ss'] = ss; k['len'] = eps; k['mins'] = mins
    if k['src'] == 'serializd': k['rf'] = 'serializd'   # the score is the user's rating of the whole show
    for a in absorb:
        x = items.pop(a)
        provs[x['p']]['items'].remove(a)
        W['items'] = [i for i in W['items'] if i['id'] != a]
    if provs[k['p']]['name'] != dest:
        src, dst = provs[k['p']], byname[dest]
        src['items'].remove(keep); dst['items'].append(keep); k['p'] = dst['id']
        near = [items[x] for x in dst['items'] if x != keep]
        if near: k['px'], k['py'] = near[0]['px'] + 9, near[0]['py'] + 9

def new_island(pid, name, cont, near_name, realm=False):
    """A new island, placed beside an existing one (the island layout settles it later)."""
    near = byname[near_name]
    p = {'id': pid, 'name': name, 'c': cont, 'realm': realm, 'region': None, 'x': near['x'] + 70, 'y': near['y'] + 40,
         'r': 20, 'media': {}, 'items': [], 'canon': []}
    W['provinces'].append(p); provs[pid] = p; byname[name] = p
    return p

def move_item(iid, dest):
    i = items[iid]; src, dst = provs[i['p']], byname[dest]
    if src is dst: return
    src['items'].remove(iid); dst['items'].append(iid); i['p'] = dst['id']
    near = [items[x] for x in dst['items'] if x != iid]
    if near: i['px'], i['py'] = near[0]['px'] + 9, near[0]['py'] + 9
    else: i['px'], i['py'] = dst['x'], dst['y']

# Star Wars: every Star Wars work on the Star Wars island (the original-trilogy films lack "Star Wars" in
# their titles); Indiana Jones leaves the sci-fi continent for the treasure hunters of the Action Coast.
SW = re.compile(r'Star Wars|Empire Strikes Back|Return of the Jedi|Rogue One|Mandalorian|Andor|Clone Wars|Darth |Thrawn|Wraith Squadron|Lost Stars|Knights of the Old Republic', re.I)
for i in list(W['items']):
    if SW.search(i['t']) and i['m'] != 'music': move_item(i['id'], 'A Galaxy Far, Far Away')
new_island('indy', 'Indiana Jones', 'action', 'Cinematic Adventures', realm=True)
for i in list(W['items']):
    if re.search(r'Indiana Jones|Raiders of the Lost Ark', i['t']): move_item(i['id'], 'Indiana Jones')
for name in ('Lucasfilm Reach', 'LEGO & Licensed'):
    p = byname[name]
    if not p['items']:
        W['provinces'].remove(p); del provs[p['id']]
        print(f'removed empty island {name}')

# Samurai cinema beyond Kurosawa: its own island in The Way of the Sword.
new_island('jidaigeki', 'Jidaigeki', 'samurai', 'Kurosawa Range')
for t in ('Harakiri', 'Samurai Rebellion'):
    for i in list(W['items']):
        if i['t'] == t: move_item(i['id'], 'Jidaigeki')

# Thematic genre first: a game lives with its theme, its game genre is a neighbour or a portal.
# Series and adaptations kept together (found by an audit of titles split across islands).
for i in list(W['items']):
    if i['t'].startswith('Ninja Gaiden') and i['m'] == 'game': move_item(i['id'], 'Character Action')
for t, dest in (('Monster Hunter: World', 'Character Action'), ('Dispatch', 'Indie Capes'), ('Ghost of Tsushima', 'Jidaigeki'), ('Watchmen', 'DC Universe'),
                ('Project Hail Mary', 'Literary & Hard SF'), ('Blade Runner 2049', 'Final Frontiers'),
                ('Worm (Parahumans, #1)', 'Indie Capes')):
    for i in list(W['items']):
        if i['t'] == t: move_item(i['id'], dest)

# Military Front is the military-shooter island: it joins the shooters on the Action Coast, on the side
# that borders Fields of History.
byname['Military Front']['c'] = 'action'

# Halo is its own island beside the campaign shooters: campaign and multiplayer both.
new_island('halo', 'Halo', 'action', 'Campaign Shooters', realm=True)
for i in list(W['items']):
    if re.match(r'Halo\b', i['t']) and i['m'] == 'game': move_item(i['id'], 'Halo')

MOVES = {'The Elephant Man': 'Twin Peaks & Lynch'}
for t, dest in MOVES.items():
    for i in W['items']:
        if i['t'] == t and i['p'] != byname[dest]['id']:
            src = provs[i['p']]; dst = byname[dest]
            src['items'].remove(i['id']); dst['items'].append(i['id']); i['p'] = dst['id']
            near = [items[x] for x in dst['items'] if x != i['id']]
            if near: i['px'], i['py'] = near[0]['px'] + 9, near[0]['py'] + 9   # re-laid out later anyway
for p in W['provinces']: recount(p)

print(f'anime -> film: {films}, anime -> tv: {series}')
js = json.dumps(W, ensure_ascii=False, separators=(',', ':'))
(SITE / 'index.html').write_text(html[:m.start(2)] + js + html[m.end(2):])
