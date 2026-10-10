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

# How long a show really is: Serializd gives episodes only, so each show gets its typical episode length
# (minutes), and `mins` = episodes x that. Anime already carries its AniList runtime.
EP_MIN = {
    ('The Sopranos', 1999): 55, ('The Beatles: Get Back', 2021): 155, ('A Knight of the Seven Kingdoms', 2026): 35,
    ('Planet Earth III', 2023): 50, ('The Simpsons', 1989): 22, ('Planet Earth', 2006): 50, ('Fallout', 2024): 60,
    ('Samurai Jack', 2001): 22, ('Gravity Falls', 2012): 22, ('Severance', 2022): 50, ('Stranger Things', 2016): 62,
    ('The Offer', 2022): 55, ('MINDHUNTER', 2017): 55, ('Fleabag', 2016): 26, ('BoJack Horseman', 2014): 25,
    ('The Bear', 2022): 32, ('The Walking Dead', 2010): 43, ('The Office', 2005): 22, ('Succession', 2018): 60,
    ('Batman: The Animated Series', 1992): 22, ('House of the Dragon', 2022): 62, ('Mr. Robot', 2015): 48,
    ('Scavengers Reign', 2023): 25, ("X-Men '97", 2024): 32, ('Shōgun', 2024): 60, ('Wednesday', 2022): 50,
    ('The Last of Us', 2023): 55, ('Arcane', 2021): 40, ('The Owl House', 2020): 22, ('1899', 2022): 57,
    ('Primal', 2019): 22, ("The Queen's Gambit", 2020): 60, ('Chernobyl', 2019): 65, ('Andor', 2022): 45,
    ('The Mandalorian', 2019): 38, ('Avatar: The Last Airbender', 2024): 55, ('The Boys', 2019): 60,
    ('The Witcher', 2019): 60, ('Battlestar Galactica', 2003): 90, ('Anne with an E', 2017): 45, ('Dark', 2017): 55,
    ('Planet Earth II', 2016): 50, ("Marvel's The Punisher", 2017): 53, ('13 Reasons Why', 2017): 55, ('Narcos', 2015): 50,
    ("Marvel's Daredevil", 2015): 53, ('Over the Garden Wall', 2014): 11, ('Rick and Morty', 2013): 22, ('Fargo', 2014): 53,
    ('Peaky Blinders', 2013): 57, ('Better Call Saul', 2015): 47, ('True Detective', 2014): 58, ('Black Mirror', 2011): 60,
    ('Lonesome Dove', 1989): 95, ('Hannibal', 2013): 43, ('Shōgun', 1980): 108, ('Parks and Recreation', 2009): 22,
    ('Band of Brothers', 2001): 60, ('Star Wars: Clone Wars', 2003): 6, ("It's Always Sunny in Philadelphia", 2005): 22,
    ('Robotech', 1985): 22, ('Twin Peaks', 1990): 48, ('The Wire', 2002): 58, ('Seinfeld', 1989): 22,
    ('Game of Thrones', 2011): 57, ('Breaking Bad', 2008): 47, ('Spider-Man', 1994): 22, ('Avatar: The Last Airbender', 2005): 23,
}
for i in W['items']:
    if i['m'] == 'tv' and not i.get('mins') and i.get('len'):
        ep = EP_MIN.get((i['t'], i.get('y')))
        if ep: i['mins'] = i['len'] * ep
        else: print(f"no episode length for {i['t']} ({i.get('y')})")

# Piles: how many seasons a show has aired, how many volumes a manga has (looked up page by page, October 2026).
# The page stacks a card per season / per ten volumes under the work.
PILES = json.loads((Path(__file__).parent / 'piles.json').read_text())
for i in W['items']:
    n = PILES.get(i['id'])
    if n and i['m'] == 'tv': i['seasons'] = n
    elif n and i['m'] == 'manga': i['vols'] = n

# Cover links: a work's verified image address (looked up page by page; see tools/images.json).
IMAGES = json.loads((Path(__file__).parent / 'images.json').read_text())
for i in W['items']:
    if IMAGES.get(i['id']): i['img'] = IMAGES[i['id']]

# Ratings corrected by hand (out of 10): The Avengers (2012) is an 8.
RATINGS = {'fpo': 8, 'm6j': 8}
for i in W['items']:
    if i['id'] in RATINGS: i['r'] = RATINGS[i['id']]

# Goodreads books and comics are scored out of 10 like everything else (Oct 2026). Manuel's stars stood for
# 1★ ≤4, 2★ 4.5–6.5, 3★ 7–8, 4★ 8.5–9, 5★ 9.5–10; each book was placed on a whole number and he reviewed
# the list (tools/book_scores.json, id -> title and score).
BOOK_SCORES = json.loads((Path(__file__).parent / 'book_scores.json').read_text())
for i in W['items']:
    if i['src'] == 'goodreads':
        i['r'] = BOOK_SCORES[i['id']]['r'] if i['id'] in BOOK_SCORES else 0

# Fight Club is a 9 (Manuel's score; the base data had 10)
if 'fvb' in items: items['fvb']['r'] = 9

# the Westeros novels are shown under their English titles (the Spanish editions were linked by mistake)
ENGLISH_TITLES = {
    'bed': 'A Game of Thrones (A Song of Ice and Fire, #1)', 'bd8': 'A Clash of Kings (A Song of Ice and Fire, #2)',
    'bgy': 'A Storm of Swords (A Song of Ice and Fire, #3)', 'bd6': 'A Feast for Crows (A Song of Ice and Fire, #4)',
    'be7': 'A Dance with Dragons (A Song of Ice and Fire, #5)',
}
for k, t in ENGLISH_TITLES.items():
    if k in items: items[k]['t'] = t

# Blackwater was read as the one-volume Complete Saga: the six separate volumes go.
for x in ('bfj', 'bfi', 'bfe', 'bff', 'bfd', 'bfh'):
    if x in items:
        provs[items[x]['p']]['items'].remove(x); items.pop(x)
W['items'] = [i for i in W['items'] if i['id'] in items]
for rt in W.get('routes', []): rt['items'] = [x for x in rt['items'] if x in items]

MOVES = {'The Elephant Man': 'Twin Peaks & Lynch', 'Blood Meridian, or, the Evening Redness in the West': 'Revisionist West'}
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
