"""Nest franchise realms and big series as sub-islands on the island they belong to.

1. Franchise realms get a parent island (PARENT below). Works that belong to a franchise but sat on its
   parent (the Star Wars films on Lucasfilm Reach) move onto the franchise's sub-island.
2. A series of 4+ works on an island it doesn't own (Saint Seiya on Shonen Arena; Deadpool, Avengers,
   X-Men on Marvel) becomes a sub-island of its own.
3. Each parent island is laid out again on a hex grid with its sub-islands inside it: a sub-island
   bigger than the parent's own works sits in the middle with the rest around it; smaller ones sit on
   the rim, keeping the direction they had. Works keep their arrangement within their group.
4. The islands of each continent are pushed apart where they now overlap, staying near where they were.

usage: python3 subisles.py SITE_DIR
"""
import json, math, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}
provs = {p['id']: p for p in W['provinces']}
byname = {p['name']: p for p in W['provinces']}

PARENT = {
    # Capes & Shonen
    'Capsule Corp': 'Shōnen Arena', 'The Grand Line': 'Shōnen Arena', 'Hidden Leaf': 'Shōnen Arena',
    'Gotham': 'DC Universe', 'The Web': 'Marvel Universe',
    # Grimlands
    'Berserk': 'Seinen Darklands', 'Paradis Island': 'Seinen Darklands', 'Westeros': 'Grimdark',
    'Castlevania': 'Metroidvania Caverns', 'The Witcher': 'Open-World RPG',
    # High Fantasy Reach
    'Final Fantasy': 'JRPG Archipelago',
    # Starward Frontier
    'Galactic Heroes': 'Space Opera',
    'Arrakis': "Villeneuve's Desert", 'Night City': 'Cyberpunk & Dystopia', 'Robotech': 'Mecha & Space Opera',
    # Action Coast: one shooter island, the campaigns at its core and the series and sub-genres around it
    # Campaign Shooters holds the single-player-first sub-genre; Call of Duty, Battlefield and Halo live multiplayer
    # lives too, so they are islands of their own beside it
    'Boomer Shooters': 'Campaign Shooters',
    'Indiana Jones': 'Cinematic Adventures',
    # Underworld
    'The Corleone Family': 'The Seventies Auteurs', 'Albuquerque': 'Prestige Crime TV', 'Fargo': 'Prestige Crime TV',
    # Haunted Marsh
    'Raccoon City': 'Survival Horror', 'Silent Hill': 'Survival Horror', 'The Last of Us': 'Survival Horror',
    "Junji Ito's Spiral": 'Manga Horror', 'The Walking Dead': 'Dead Lands',
    'King Country': 'Horror Fiction', "R'lyeh": 'Horror Fiction',
    # Dreaming Coast
    'Rokkenjima': 'Thrillers & Mysteries',   # Umineko is a mystery first 'NERV Headquarters': 'Auteur Anime',
    'Twin Peaks & Lynch': 'Dreamers & Surrealists', 'The Underground': 'Art & Atmosphere',
    # elsewhere
    'Abbey Road': 'The Sixties', "Tomorrow's Joe": 'Sports Manga & Anime', 'Kamogawa Gym': 'Sports Manga & Anime',
    'Vinland': 'Historical Manga', 'Lonesome Dove Country': 'Revisionist West',
}
# works sitting on a parent that belong on the franchise's sub-island
ADOPT = {}
# series sub-islands are made on ordinary islands, and inside these franchise realms that hold many series
SERIES_IN_REALMS = {'Marvel Universe'}
SERIES_NAMES = {'saint seiya': 'Sanctuary', 'avengers': 'Avengers Tower', 'x men': "Xavier's School", 'deadpool': 'Deadpool'}

S = W.get('S', 7)
def _measure():
    import numpy as np
    inner, gaps = [], []
    for c in W['continents']:
        ps = [p for p in W['provinces'] if p['c'] == c['id'] and p['items']]
        arr = [np.array([[items[x]['px'], items[x]['py']] for x in p['items'] if not items[x].get('dl')]) for p in ps]
        for a in range(len(arr)):
            if len(arr[a]) > 1:
                d = np.sqrt(((arr[a][:, None] - arr[a][None]) ** 2).sum(-1)); np.fill_diagonal(d, 1e9); inner += list(d.min(1))
            others = [np.sqrt(((arr[a][:, None] - arr[b][None]) ** 2).sum(-1)).min() for b in range(len(arr)) if b != a]
            if others: gaps.append(min(others))
    inner.sort(); gaps.sort()
    return inner[len(inner) // 2], gaps[len(gaps) // 10]
SP, ISLAND_GAP = _measure()                  # spacing between works on an island, and between islands
HEX_A = math.sqrt(3) / 2 * SP * SP           # area each work takes on the hex grid

def move(iid, src, dst):
    i = items[iid]
    src['items'].remove(iid); dst['items'].append(iid); i['p'] = dst['id']
    for p, d in ((src, -1), (dst, 1)):
        p['media'][i['m']] = p['media'].get(i['m'], 0) + d
        if not p['media'][i['m']]: del p['media'][i['m']]

# 1. franchise realms onto their parents
for child, parent in PARENT.items():
    c, p = byname[child], byname[parent]
    c['parent'] = p['id']
    if c['c'] != p['c']: c['c'] = p['c']
    if child in ADOPT:
        for iid in [x for x in p['items'] if ADOPT[child](items[x])]: move(iid, p, c)

def series_name(g):
    # a Goodreads series tag names it best: "Dead Beat (The Dresden Files, #7)" -> "The Dresden Files"
    tags = Counter()
    for w in g:
        mm = re.search(r'\(([^()#]+?),?\s*#\s*[\d.]+[^()]*\)\s*$', w['t'])
        if mm: tags[mm.group(1).strip()] += 1
    if tags: return tags.most_common(1)[0][0]
    # otherwise the start the titles share, cut at a word: "Mission: Impossible", "The Lord of the Rings"
    ts = [re.sub(r'\s*\([^)]*\)\s*$', '', w['t']) for w in g]
    pre = ts[0]
    for t in ts[1:]:
        n = 0
        while n < min(len(pre), len(t)) and pre[n].lower() == t[n].lower(): n += 1
        pre = pre[:n]
    if not all(len(t) == len(pre) or not t[len(pre)].isalnum() for t in ts):
        pre = pre[:pre.rfind(' ')] if ' ' in pre else pre
    pre = re.sub(r'[\s:\-–—,.]+$', '', pre)
    return pre or min((re.split(r'[:(]', w['t'])[0].strip() for w in g), key=len)

# 2a. curated series: sub-islands gathered by title, with the volumes not yet read as landmarks in the fog
CURATED = [
    # (name, island it sits on, titles that belong, author, the full run in order)
    ('The Cosmere', 'Epic Fantasy', r'Mistborn|Well of Ascension|Hero of Ages|Warbreaker|Emperor.s Soul|Elantris|Stormlight|Alloy of Law|Shadows of Self|Bands of Mourning|Lost Metal|Tress of the Emerald|Yumi and the Nightmare|Sunlit Man',
     'Brandon Sanderson', ['Elantris', 'Mistborn: The Final Empire', 'The Well of Ascension', 'The Hero of Ages', 'Warbreaker', 'The Way of Kings',
     'The Alloy of Law', 'Words of Radiance', 'Shadows of Self', 'The Bands of Mourning', 'Oathbringer', 'Rhythm of War', 'The Lost Metal',
     'Tress of the Emerald Sea', 'Yumi and the Nightmare Painter', 'The Sunlit Man', 'Wind and Truth', 'The Emperor\'s Soul', 'Edgedancer', 'Dawnshard']),
    ('Realm of the Elderlings', 'Epic Fantasy', r'Farseer|Tawny Man|Liveship|Rain Wild|Fitz and the Fool|Assassin.s (Apprentice|Quest|Fate)|Royal Assassin|Fool.s (Errand|Fate|Quest|Assassin)|Golden Fool|Ship of (Magic|Destiny)|Mad Ship',
     'Robin Hobb', ["Assassin's Apprentice", 'Royal Assassin', "Assassin's Quest", 'Ship of Magic', 'The Mad Ship', 'Ship of Destiny',
     "Fool's Errand", 'The Golden Fool', "Fool's Fate", 'Dragon Keeper', 'Dragon Haven', 'City of Dragons', 'Blood of Dragons',
     "Fool's Assassin", "Fool's Quest", "Assassin's Fate"]),
    ('The Wheel of Time', 'Epic Fantasy', r'Wheel of Time', 'Robert Jordan', ['New Spring', 'The Eye of the World', 'The Great Hunt', 'The Dragon Reborn',
     'The Shadow Rising', 'The Fires of Heaven', 'Lord of Chaos', 'A Crown of Swords', 'The Path of Daggers', "Winter's Heart",
     'Crossroads of Twilight', 'Knife of Dreams', 'The Gathering Storm', 'Towers of Midnight', 'A Memory of Light']),
    ('The Dresden Files', 'Epic Fantasy', r'Dresden Files', 'Jim Butcher', ['Storm Front', 'Fool Moon', 'Grave Peril', 'Summer Knight', 'Death Masks',
     'Blood Rites', 'Dead Beat', 'Proven Guilty', 'White Night', 'Small Favor', 'Turn Coat', 'Changes', 'Ghost Story', 'Cold Days',
     'Skin Game', 'Peace Talks', 'Battle Ground']),
    ('The First Law', 'Grimdark', r'First Law|Age of Madness|Best Served Cold|The Heroes|Red Country|Sharp Ends', 'Joe Abercrombie',
     ['The Blade Itself', 'Before They Are Hanged', 'Last Argument of Kings', 'Best Served Cold', 'The Heroes', 'Red Country',
     'A Little Hatred', 'The Trouble with Peace', 'The Wisdom of Crowds']),
    ('Malazan', 'Grimdark', r'Malazan', 'Steven Erikson', ['Gardens of the Moon', 'Deadhouse Gates', 'Memories of Ice', 'House of Chains',
     'Midnight Tides', 'The Bonehunters', "Reaper's Gale", 'Toll the Hounds', 'Dust of Dreams', 'The Crippled God']),
    ('Red Rising Saga', 'Space Opera', r'Red Rising', 'Pierce Brown', ['Red Rising', 'Golden Son', 'Morning Star', 'Iron Gold', 'Dark Age', 'Light Bringer']),
    ('The Sun Eater', 'Space Opera', r'Sun Eater', 'Christopher Ruocchio', ['Empire of Silence', 'Howling Dark', 'Demon in White', 'Kingdoms of Death',
     'Ashes of Man', 'Disquiet Gods']),
    ('The Expanse', 'Space Opera', r'Leviathan Wakes|Caliban.s War|Abaddon.s Gate|Cibola Burn|Nemesis Games|Babylon.s Ashes|Persepolis Rising|Tiamat.s Wrath|Leviathan Falls|\(The Expanse',
     'James S. A. Corey', ['Leviathan Wakes', "Caliban's War", "Abaddon's Gate", 'Cibola Burn', 'Nemesis Games', "Babylon's Ashes",
     'Persepolis Rising', "Tiamat's Wrath", 'Leviathan Falls']),
    ('Hyperion Cantos', 'Space Opera', r'Hyperion|Endymion', 'Dan Simmons', ['Hyperion', 'The Fall of Hyperion', 'Endymion', 'The Rise of Endymion']),
    # games: a series sub-island on the military shooters (no reading list, so no progress count)
    ('Battlefield', 'Military Front', r'^Battlefield', None, []),
]
# volumes still to read, added to an existing franchise island (books only)
CANON_ADD = {
    'Arrakis': ('Frank Herbert', ['Dune', 'Dune Messiah', 'Children of Dune', 'God Emperor of Dune', 'Heretics of Dune', 'Chapterhouse: Dune']),
    'The Witcher': ('Andrzej Sapkowski', ['El último deseo', 'La espada del destino', 'La sangre de los elfos', 'Tiempo de odio',
                    'Bautismo de fuego', 'La torre de la golondrina', 'La dama del lago', 'Estación de tormentas']),
}
def tkey(t):
    t = re.sub(r'\([^)]*\)', ' ', t)
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'^(the|a|an|el|la|los|las) ', '', t.strip())
    return re.sub(r'[^a-z0-9]+', '', t)
def fog(owned, author, run):
    have = [tkey(items[x]['t']) for x in owned]
    out = []
    for t in run:
        k = tkey(t)
        if not any(h == k or h.startswith(k) or (len(h) > 6 and k.startswith(h)) for h in have):
            out.append({'t': t, 'by': author, 'y': None, 'seen': False, 'px': 0.0, 'py': 0.0})
    return out
made = []
for name, host, rx, author, run in CURATED:
    hp = byname[host]
    rx_ = re.compile(rx, re.I)
    hosts = [hp] + [q for q in W['provinces'] if q.get('parent') == hp['id']]
    ids = [x for q in hosts for x in q['items'] if rx_.search(items[x]['t']) and (items[x]['m'] in ('books', 'comics', 'manga') or not run)]
    # a series already made into its own sub-island folds in too (Stormlight into the Cosmere)
    for k in [q for q in W['provinces'] if q.get('parent') == hp['id'] and rx_.search(q['name'])]:
        ids += k['items']; k['items'] = []
    if len(ids) < 2: continue
    sid = 'sub-' + re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    sub = {'id': sid, 'name': name, 'c': hp['c'], 'realm': True, 'region': None, 'x': hp['x'], 'y': hp['y'], 'r': 10,
           'media': {}, 'items': [], 'canon': [], 'parent': hp['id'], 'series': True}
    W['provinces'].append(sub); provs[sid] = sub; byname[name] = sub
    for x in ids:
        src = provs[items[x]['p']]
        if x in src['items']: move(x, src, sub)
        else: sub['items'].append(x); items[x]['p'] = sid; sub['media'][items[x]['m']] = sub['media'].get(items[x]['m'], 0) + 1
    # how far through the series: shown as a small 4/15 rather than every missing book
    if run: sub['run'] = len(run); sub['have'] = len(run) - len(fog(sub['items'], author, run))
    made.append((host, name, len(ids)))
for p_ in [q for q in W['provinces'] if q.get('parent') and not q['items']]:
    W['provinces'].remove(p_); del provs[p_['id']]
for island, (author, run) in CANON_ADD.items():
    p_ = byname[island]
    books = [x for x in p_['items'] if items[x]['m'] == 'books']
    p_['run'] = len(run); p_['have'] = len(run) - len(fog(books, author, run))

# 2b. big series become sub-islands
import series as SER
for p in list(W['provinces']):
    if p.get('parent') or (p['realm'] and p['name'] not in SERIES_IN_REALMS): continue
    works = [items[x] for x in p['items'] if not items[x].get('dl') and items[x]['m'] != 'music']
    if len(works) < 6: continue
    for g in SER.groups_in(works):
        if len(g) < 4 or len(g) / len(works) >= 0.5: continue
        stems = [' '.join(SER.stem_words(w['t'])) for w in g]
        key = min(stems, key=len)
        name = SERIES_NAMES.get(key) or series_name(g)
        sid = 'sub-' + re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()).strip('-')
        sub = {'id': sid, 'name': name, 'c': p['c'], 'realm': True, 'region': None, 'x': p['x'], 'y': p['y'], 'r': 10,
               'media': {}, 'items': [], 'canon': [], 'parent': p['id'], 'series': True}
        W['provinces'].append(sub); provs[sid] = sub; byname[name] = sub
        for w in g:
            move(w['id'], p, sub)
            for e in [x for x in p['items'] if items[x].get('dl') == w['id']]: move(e, p, sub)  # expansions follow
        made.append((p['name'], name, len(g)))


kids = defaultdict(list)
for p in W['provinces']:
    if p.get('parent'): kids[p['parent']].append(p)

def core(p):  # works that take a spot of their own (expansions fan out behind their game)
    return [items[x] for x in p['items'] if not items[x].get('dl')]

def centre(ws):
    return (sum(w['px'] for w in ws) / len(ws), sum(w['py'] for w in ws) / len(ws)) if ws else None

def hexgrid(n):
    """At least n hex-grid points in the smallest disc around (0, 0), nearest first."""
    R = math.sqrt(n * HEX_A / math.pi) * 0.9
    while True:
        pts = []
        rows = int(R / (SP * math.sqrt(3) / 2)) + 1
        for r in range(-rows, rows + 1):
            y = r * SP * math.sqrt(3) / 2
            off = SP / 2 if r % 2 else 0
            for c in range(-int(R / SP) - 2, int(R / SP) + 3):
                x = c * SP + off
                if x * x + y * y <= R * R: pts.append((x, y))
        if len(pts) >= n:
            pts.sort(key=lambda q: q[0] ** 2 + q[1] ** 2)
            return pts, R
        R += SP * 0.25

def disc(R):
    pts = []
    rows = int(R / (SP * math.sqrt(3) / 2)) + 1
    for r in range(-rows, rows + 1):
        y = r * SP * math.sqrt(3) / 2
        off = SP / 2 if r % 2 else 0
        for c in range(-int(R / SP) - 2, int(R / SP) + 3):
            x = c * SP + off
            if x * x + y * y <= R * R: pts.append((x, y))
    return pts

def place(ws, pts, cx, cy, rad, old):
    """Give works ws the points pts, keeping their old arrangement (old = their previous centre)."""
    if not ws: return
    ox, oy = old
    far = max(math.hypot(w['px'] - ox, w['py'] - oy) for w in ws) or 1
    free = list(pts)
    for w in sorted(ws, key=lambda w: -(w.get('r') or 0)):
        tx = cx + (w['px'] - ox) / far * rad; ty = cy + (w['py'] - oy) / far * rad
        q = min(free, key=lambda q: (q[0] - tx) ** 2 + (q[1] - ty) ** 2)
        free.remove(q); w['_np'] = q

ghost_of = defaultdict(list)
for p in W['provinces']:
    for g in p['canon']:
        if g.get('px') is not None: ghost_of[p['id']].append(g)

# Before anything moves: how big each island (with its sub-islands) was and where, so the spacing step
# can keep every pair of islands as close as they were, and only push apart what has grown into a neighbour.
before = {}
for p in W['provinces']:
    if p.get('parent'): continue
    ws = core(p) + [w for k in kids[p['id']] for w in core(k)]
    c0 = centre(ws) or (p['x'], p['y'])
    r0 = max([math.hypot(w['px'] - c0[0], w['py'] - c0[1]) for w in ws] + [26 * S / 7]) + S * 0.9
    before[p['id']] = (c0, r0)

units = {}   # top-level island id -> {'r': radius incl. landmarks, 'x','y'}
for p in W['provinces']:
    if p.get('parent'): continue
    ch = sorted(kids[p['id']], key=lambda k: -len(core(k)))
    own = core(p)
    if not ch and not own:
        units[p['id']] = {'x': p['x'], 'y': p['y'], 'r': 26 * S / 7 + S * 0.9, 'members': [p]}
        continue
    # every island (with or without sub-islands) is laid out afresh on the even grid, keeping its works'
    # arrangement, so works moved in from elsewhere never pile up on one spot
    # 3. lay the parent out again with its sub-islands inside it
    N = len(own) + sum(len(core(k)) for k in ch)
    pts, R = hexgrid(N)
    pc = centre(own + [w for k in ch for w in core(k)])
    MOAT = SP * 1.1        # spots this close to a sub-island stay empty: a one-spot moat around each
    big = ch[0] if ch and len(core(ch[0])) >= len(own) else None
    rim = [k for k in ch if k is not big]
    # The island grows from its middle outward: its core first (the biggest sub-island, if it outweighs
    # the parent's own works, with the own works around it), then each rim sub-island snug against what is
    # already there, on the side it used to be. Every group keeps a one-spot moat from every other.
    pts = disc(R * 2.4)
    groups, taken, sub_pts = [], set(), []          # sub_pts: (group id, point) for the moat test
    def take(n, cx, cy, kid):
        def ok(q):
            if q in taken: return False
            return all((q[0] - t[0]) ** 2 + (q[1] - t[1]) ** 2 >= MOAT ** 2 for c, t in sub_pts if c != kid)
        cand = sorted((q for q in pts if ok(q)), key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)[:n]
        for q in cand: taken.add(q); sub_pts.append((kid, q))
        return cand
    if big:
        groups.append((core(big), take(len(core(big)), 0, 0, big['id']), (0, 0), centre(core(big))))
    groups.append((own, take(len(own), 0, 0, '__own'), (0, 0), centre(own) or pc))
    ang = {}
    for k in rim:
        kc = centre(core(k))
        ang[k['id']] = math.atan2(kc[1] - pc[1], kc[0] - pc[0]) if kc else 0
    rcs = {k['id']: math.sqrt(len(core(k)) * HEX_A / math.pi) for k in rim}
    r_mid = math.sqrt(len(taken) * HEX_A / math.pi)
    for _ in range(200):
        order = sorted(rim, key=lambda k: ang[k['id']])
        for a_, b_ in zip(order, order[1:] + order[:1]):
            if a_ is b_: continue
            d = r_mid + max(rcs[a_['id']], rcs[b_['id']])
            need = (rcs[a_['id']] + rcs[b_['id']] + SP * 1.6) / max(d, 1)
            gap = (ang[b_['id']] - ang[a_['id']]) % (2 * math.pi)
            if gap < need:
                push = (need - gap) / 2
                ang[a_['id']] -= push; ang[b_['id']] += push
    for k in sorted(rim, key=lambda k: -len(core(k))):
        # just outside the ground already taken in that direction, with room for the moat
        a_ = ang[k['id']]
        reach = max([q[0] * math.cos(a_) + q[1] * math.sin(a_) for q in taken] + [0])
        d = reach + MOAT + rcs[k['id']] * 0.8
        cx, cy = d * math.cos(a_), d * math.sin(a_)
        groups.append((core(k), take(len(core(k)), cx, cy, k['id']), (cx, cy), centre(core(k))))
    R = max(math.hypot(*q) for q in taken) + SP * 0.5
    for ws, gp, (cx, cy), old in groups:
        if not ws: continue
        gcx = sum(q[0] for q in gp) / len(gp); gcy = sum(q[1] for q in gp) / len(gp)
        rad = max(math.hypot(q[0] - gcx, q[1] - gcy) for q in gp) if len(gp) > 1 else 0
        place(ws, gp, gcx, gcy, rad, old)
    for ws, *_ in groups:
        for w in ws:
            nx, ny = w.pop('_np')
            w['px'], w['py'] = pc[0] + nx, pc[1] + ny
    # the group's landmarks in the fog: spread evenly round the island's actual shore (just past the
    # outermost works in each direction), in the order they had, so they don't pile up on one side
    # a sub-island's own unread volumes sit right beside it, on the free spots nearest to it
    for (ws, gp, (gx, gy), _old), k in zip(groups, [big] * bool(big) + [p] + sorted(rim, key=lambda k: -len(core(k)))):
        if k is p or not ghost_of[k['id']]: continue
        cx_ = sum(q[0] for q in gp) / len(gp); cy_ = sum(q[1] for q in gp) / len(gp)
        near = sorted((q for q in pts if q not in taken), key=lambda q: (q[0] - cx_) ** 2 + (q[1] - cy_) ** 2)
        for g, q in zip(ghost_of[k['id']], near):
            taken.add(q); g['px'], g['py'] = pc[0] + q[0], pc[1] + q[1]
    gh = list(ghost_of[p['id']])
    if gh:
        order = sorted(range(len(gh)), key=lambda n: math.atan2(gh[n]['py'] - pc[1], gh[n]['px'] - pc[0]))
        a0 = math.atan2(gh[order[0]]['py'] - pc[1], gh[order[0]]['px'] - pc[0])
        for j, n in enumerate(order):
            a = a0 + 2 * math.pi * j / len(gh)
            reach = max([q[0] * math.cos(a) + q[1] * math.sin(a) for q in taken] + [0])
            ring = reach + SP * 1.1
            gh[n]['px'], gh[n]['py'] = pc[0] + ring * math.cos(a), pc[1] + ring * math.sin(a)
    units[p['id']] = {'x': pc[0], 'y': pc[1], 'r': R + S * 1.0, 'members': [p] + ch}

# islands that belong side by side inside their continent (a game genre beside its thematic home)
from continents_links import NEIGHBOURS
neigh = {tuple(sorted((byname[a]['id'], byname[b]['id']))) for a, b in NEIGHBOURS if a in byname and b in byname}

# 4. islands of a continent moved as solid pieces until the nearest works of any two islands are as far
#    apart as islands usually were before (measured from the original layout), drawn gently toward the
#    continent's middle so the gaps left by islands that moved onto their parents close up.
import numpy as np
for cont in W['continents']:
    us = [(pid, u) for pid, u in units.items() if provs[pid]['c'] == cont['id']]
    pts = []
    for pid, u in us:
        ws = [w for p in u['members'] for w in core(p)]
        pts.append(np.array([[w['px'], w['py']] for w in ws]) if ws else np.array([[u['x'], u['y']]]))
    off = np.zeros((len(us), 2))
    home = np.array([[u['x'], u['y']] for _, u in us])
    wt = np.array([max(1, len(p_)) for p_ in pts], float)
    for it in range(400):
        moved = 0
        cur = home + off
        cc = (cur * wt[:, None]).sum(0) / wt.sum()
        for a in range(len(us)):
            for b in range(a + 1, len(us)):
                if np.hypot(*(cur[a] - cur[b])) > us[a][1]['r'] + us[b][1]['r'] + ISLAND_GAP: continue
                pa, pb = pts[a] + off[a], pts[b] + off[b]
                d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1))
                k = np.unravel_index(d.argmin(), d.shape)
                if d[k] < ISLAND_GAP:
                    v = cur[b] - cur[a]; n = np.hypot(*v) or 1e-6; v = v / n
                    push = (ISLAND_GAP - d[k]) * 0.5
                    fa = wt[b] / (wt[a] + wt[b])                      # small islands give way to big ones
                    off[a] -= v * push * 2 * fa; off[b] += v * push * 2 * (1 - fa); moved += 1
        # neighbours are drawn together until they nearly touch
        for a in range(len(us)):
            for b in range(a + 1, len(us)):
                if tuple(sorted((us[a][0], us[b][0]))) not in neigh: continue
                pa, pb = pts[a] + off[a], pts[b] + off[b]
                d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1)).min()
                if d > ISLAND_GAP * 1.2:
                    v = (pb.mean(0) - pa.mean(0)); v = v / (np.hypot(*v) or 1e-6)
                    pull = min(SP, (d - ISLAND_GAP * 1.1) * 0.15)
                    off[a] += v * pull * 0.5; off[b] -= v * pull * 0.5; moved += 1
        cur = home + off
        off += (cc - cur) * 0.01                                     # cohesion
        if not moved and it > 60: break
    for (pid, u), o in zip(us, off):
        dx, dy = float(o[0]), float(o[1])
        for p in u['members']:
            for x in p['items']: items[x]['px'] += dx; items[x]['py'] += dy
            for g in ghost_of[p['id']]: g['px'] += dx; g['py'] += dy
            p['x'] += dx; p['y'] += dy

# 5. island and continent records follow their works
for p in W['provinces']:
    ws = core(p)
    if ws:
        cx, cy = centre(ws)
        p['x'], p['y'] = round(cx, 1), round(cy, 1)
        p['r'] = round(max(math.sqrt(len(ws) * HEX_A / math.pi), max(math.hypot(w['px'] - cx, w['py'] - cy) for w in ws)) + S, 1)
for c in W['continents']:
    ws = [w for p in W['provinces'] if p['c'] == c['id'] for w in core(p)]
    if not ws: continue
    x0, x1 = min(w['px'] for w in ws), max(w['px'] for w in ws)
    y0, y1 = min(w['py'] for w in ws), max(w['py'] for w in ws)
    c['x'], c['y'] = round((x0 + x1) / 2, 1), round((y0 + y1) / 2, 1)
    c['r'] = round(max(math.hypot(w['px'] - c['x'], w['py'] - c['y']) for w in ws) + S * 3, 1)
for w in W['items']: w['px'], w['py'] = round(w['px'], 1), round(w['py'], 1)
for p in W['provinces']:
    for g in p['canon']:
        if g.get('px') is not None: g['px'], g['py'] = round(g['px'], 1), round(g['py'], 1)

# continents that now touch each other are reported, not silently overlapped
cs = W['continents']
for a in range(len(cs)):
    for b in range(a + 1, len(cs)):
        d = math.hypot(cs[a]['x'] - cs[b]['x'], cs[a]['y'] - cs[b]['y'])
        if d < (cs[a]['r'] + cs[b]['r']) * 0.8:
            print(f"close: {cs[a]['name']} / {cs[b]['name']} ({d:.0f} < {(cs[a]['r'] + cs[b]['r']) * 0.8:.0f})")

allx = [w['px'] for w in W['items']] + [g['px'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
ally = [w['py'] for w in W['items']] + [g['py'] for p in W['provinces'] for g in p['canon'] if g.get('px') is not None]
W['bounds'] = [round(min(allx), 1), round(min(ally), 1), round(max(allx), 1), round(max(ally), 1)]

for parent, name, n in made: print(f'series sub-island: {name} ({n}) on {parent}')
print(f'{len(PARENT)} franchise sub-islands, {len(made)} series sub-islands')
js = json.dumps(W, ensure_ascii=False, separators=(',', ':'))
(SITE / 'index.html').write_text(html[:m.start(2)] + js + html[m.end(2):])
