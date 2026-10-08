"""Portals: links from an island to another island or work that belongs there too.

A work has one home, but plenty belong in two places (Call of Duty is a war game and a campaign
shooter; Umineko is a visual novel and a mystery). Rather than duplicating them, the second island
gets a portal on its shore that leads to them. Stored as W['portals'] = [{from, to | item, label}].
usage: python3 portals.py SITE_DIR
"""
import json, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
byname = {p['name']: p for p in W['provinces']}
bytitle = {}
for i in W['items']: bytitle.setdefault(i['t'], i)

PORTALS = [
    # Where a game's game genre lives on a different island from its theme. (island it opens on,
    # destination: ('island', name) or ('work', title[, medium]), label, label in Spanish)
    # Story & Choice: narrative games whose theme took them elsewhere
    ('Story & Choice', ('work', 'Dispatch', 'game'), 'Dispatch', 'Dispatch'),
    ('Story & Choice', ('work', 'Batman: The Telltale Series', 'game'), 'Batman: The Telltale Series', 'Batman: The Telltale Series'),
    ('Story & Choice', ('work', 'The Walking Dead', 'game'), 'The Walking Dead', 'The Walking Dead'),
    ('Story & Choice', ('work', 'Detroit: Become Human', 'game'), 'Detroit: Become Human', 'Detroit: Become Human'),
    ('Story & Choice', ('island', 'Rokkenjima'), 'Umineko', 'Umineko'),
    ('Light & Visual Novels', ('island', 'Rokkenjima'), 'Umineko', 'Umineko'),
    # the Shōnen–Seinen border: manga and anime whose theme took them to other continents
    ('Shōnen Arena', ('island', 'Death Note'), 'Death Note', 'Death Note'),
    ('Shōnen Arena', ('island', "JoJo's Bizarre World"), "JoJo's Bizarre Adventure", "JoJo's Bizarre Adventure"),
    ('Shōnen Arena', ('island', "Fujimoto's Devils"), 'Chainsaw Man', 'Chainsaw Man'),
    ('Shōnen Arena', ('island', 'Fantasy Manga & Anime'), 'Fullmetal Alchemist & Frieren', 'Fullmetal Alchemist y Frieren'),
    ('Shōnen Arena', ('island', 'Sports Manga & Anime'), 'Slam Dunk & sports shōnen', 'Slam Dunk y shōnen deportivo'),
    ('Seinen Darklands', ('island', "Urasawa's Mysteries"), "Urasawa's Monster", 'Monster de Urasawa'),
    ('Seinen Darklands', ('island', 'Psychological Seinen'), 'Punpun & psychological seinen', 'Punpun y seinen psicológico'),
    ('Seinen Darklands', ('island', 'Vinland'), 'Vinland Saga', 'Vinland Saga'),
    ('Seinen Darklands', ('island', 'Samurai Manga & Anime'), 'Vagabond', 'Vagabond'),
    ('Seinen Darklands', ('island', 'Cyberpunk & Dystopia'), 'Akira & Ghost in the Shell', 'Akira y Ghost in the Shell'),
    ('Seinen Darklands', ('island', 'Gangsters & Gunsmoke'), 'Banana Fish & Black Lagoon', 'Banana Fish y Black Lagoon'),
    # shooters
    ('Campaign Shooters', ('island', 'Half-Life'), 'Half-Life', 'Half-Life'),
    ('Campaign Shooters', ('island', 'Immersive Sims'), 'BioShock & immersive sims', 'BioShock e immersive sims'),
    ('Campaign Shooters', ('work', 'Star Wars: Battlefront II', 'game'), 'Star Wars Battlefront', 'Star Wars Battlefront'),
    # role-playing
    ('CRPG Citadel', ('work', 'Star Wars: Knights of the Old Republic', 'game'), 'Knights of the Old Republic', 'Knights of the Old Republic'),
    ('Open-World RPG', ('island', 'Night City'), 'Cyberpunk 2077', 'Cyberpunk 2077'),
    ('Open-World RPG', ('island', 'The Wasteland'), 'Fallout: New Vegas', 'Fallout: New Vegas'),
    ('JRPG Archipelago', ('island', 'The Underground'), 'Undertale & Deltarune', 'Undertale y Deltarune'),
    # action
    ('Character Action', ('island', 'Gotham'), 'Batman: Arkham', 'Batman: Arkham'),
    ('Character Action', ('work', 'One Piece: Pirate Warriors 4', 'game'), 'One Piece: Pirate Warriors', 'One Piece: Pirate Warriors'),
    ('Character Action', ('work', 'Star Wars Jedi: Fallen Order', 'game'), 'Jedi: Fallen Order', 'Jedi: Fallen Order'),
    ('Cinematic Adventures', ('work', "Marvel's Spider-Man", 'game'), "Marvel's Spider-Man", "Marvel's Spider-Man"),
    ('Fighters\' Ring', ('work', 'Dragon Ball Z: Budokai Tenkaichi 3', 'game'), 'Budokai Tenkaichi 3', 'Budokai Tenkaichi 3'),
    # strategy, cards, arenas
    ('Strategy Marches', ('work', 'Star Wars: Empire at War', 'game'), 'Empire at War', 'Empire at War'),
    ('Card Tables', ('work', 'Legends of Runeterra', 'game'), 'Legends of Runeterra', 'Legends of Runeterra'),
    ('Card Tables', ('work', 'Inscryption', 'game'), 'Inscryption', 'Inscryption'),
    ('Roguelike Reef', ('work', 'Inscryption', 'game'), 'Inscryption', 'Inscryption'),
    ('Competitive Arenas', ('island', 'Runeterra'), 'League of Legends', 'League of Legends'),
    # horror
    ('Dead Lands', ('work', 'Project Zomboid', 'game'), 'Project Zomboid', 'Project Zomboid'),
    ('Dead Lands', ('work', 'Left 4 Dead 2', 'game'), 'Left 4 Dead', 'Left 4 Dead'),
    # a full pass over every game sitting on a theme island, linked from its game genre
    ('Cinematic Adventures', ('island', 'The Last of Us'), 'The Last of Us', 'The Last of Us'),
    ('Cinematic Adventures', ('work', 'Ghost of Tsushima', 'game'), 'Ghost of Tsushima', 'Ghost of Tsushima'),
    ('FromSoftware Peaks', ('work', 'Star Wars Jedi: Fallen Order', 'game'), 'Jedi: Fallen Order', 'Jedi: Fallen Order'),
    ('Open-World RPG', ('work', 'Elden Ring', 'game'), 'Elden Ring', 'Elden Ring'),
    ('Open-World RPG', ('island', 'The Witcher'), 'The Witcher', 'The Witcher'),
    ('Mecha & Space Opera', ('work', 'Armored Core VI: Fires of Rubicon', 'game'), 'Armored Core VI', 'Armored Core VI'),
    ('Mecha & Space Opera', ('work', 'Titanfall 2', 'game'), 'Titanfall 2', 'Titanfall 2'),
    ('Space Opera', ('work', 'Halo: Combat Evolved', 'game'), 'Halo', 'Halo'),
    ('Final Frontiers', ('work', 'Outer Wilds', 'game'), 'Outer Wilds', 'Outer Wilds'),
    ('Final Frontiers', ('work', 'Metroid Prime', 'game'), 'Metroid', 'Metroid'),
    ('Final Frontiers', ('work', 'Alien: Isolation', 'game'), 'Alien: Isolation', 'Alien: Isolation'),
    ('Final Frontiers', ('work', 'Dead Space', 'game'), 'Dead Space', 'Dead Space'),
    ('Jidaigeki', ('work', 'Sekiro: Shadows Die Twice', 'game'), 'Sekiro', 'Sekiro'),
    ('Jidaigeki', ('work', 'Onimusha: Way of the Sword', 'game'), 'Onimusha', 'Onimusha'),
    ('Hyrule', ('work', 'Tunic', 'game'), 'Tunic', 'Tunic'),
    ('Hyrule', ('work', 'Ōkami', 'game'), 'Ōkami', 'Ōkami'),
    ('Disney Castle', ('work', 'Kingdom Hearts II Final Mix', 'game'), 'Kingdom Hearts', 'Kingdom Hearts'),
    ('Indie Capes', ('work', 'Infamous 2', 'game'), 'Infamous 2', 'Infamous 2'),
    ('Sandbox Cities', ('island', 'The Web'), "Spider-Man's New York", 'La Nueva York de Spider-Man'),
    ('Sandbox Cities', ('work', 'The Incredible Hulk', 'game'), 'The Incredible Hulk', 'The Incredible Hulk'),
    ('Epic History', ('work', "Assassin's Creed II", 'game'), "Assassin's Creed", "Assassin's Creed"),
    ('Gangland & Heists', ('work', 'Hotline Miami', 'game'), 'Hotline Miami', 'Hotline Miami'),
    ('Strategy Marches', ('work', 'Teamfight Tactics', 'game'), 'Teamfight Tactics', 'Teamfight Tactics'),
    ('Art & Atmosphere', ('work', 'Portal 2', 'game'), 'Portal', 'Portal'),
    ('Party & Co-op', ('work', 'Left 4 Dead 2', 'game'), 'Left 4 Dead', 'Left 4 Dead'),
    ('Immersive Sims', ('island', 'Shadow Moses'), 'Metal Gear Solid', 'Metal Gear Solid'),
    # LEGO games, gathered from wherever their licence put them
    ('3D Mascot Meadows', ('work', 'LEGO DC Super-Villains', 'game'), 'LEGO DC Super-Villains', 'LEGO DC Super-Villains'),
    ('3D Mascot Meadows', ('work', 'LEGO Star Wars: The Complete Saga', 'game'), 'LEGO Star Wars', 'LEGO Star Wars'),
    ('3D Mascot Meadows', ('work', 'LEGO Batman: The Videogame', 'game'), 'LEGO Batman', 'LEGO Batman'),
    ('3D Mascot Meadows', ('work', 'LEGO Indiana Jones: The Original Adventures', 'game'), 'LEGO Indiana Jones', 'LEGO Indiana Jones'),
]
# Genre homes for works on islands grouped by director, era, country or studio (Seventies Auteurs, Kubrick,
# Golden Age Hollywood, Korean New Wave...). Each genre island gets portals to them, one per source island
# (naming the works). Titles are films unless marked "|medium".
GROUP_WORKS = {}
GENRE_HOMES = {
    # Only where the work IS that genre as much as anything else (Butch Cassidy is a western). A shared topic
    # isn't enough: Raging Bull is about boxing, not sports manga; Kung Fu Panda is not Hong Kong action.
    'Revisionist West': ['Butch Cassidy and the Sundance Kid', 'Killers of the Flower Moon', 'There Will Be Blood'],
    'Spaghetti Westerns': ['Django Unchained', 'The Hateful Eight', 'El Topo'],
    'Classic Westerns': ['The Treasure of the Sierra Madre'],
    'Twentieth-Century Wars': ['The Deer Hunter', 'Inglourious Basterds', 'Paths of Glory', 'Full Metal Jacket', 'Dunkirk', 'The Great Escape',
        'Judgment at Nuremberg', "The Human Condition I: No Greater Love", "The Human Condition II: Road to Eternity", "The Human Condition III: A Soldier's Prayer",
        'The Bridge on the River Kwai', 'The Battle of Algiers', 'Life Is Beautiful', 'Army of Shadows', 'All Quiet on the Western Front', 'Das Boot',
        'Come and See', 'The Cranes Are Flying', 'Grave of the Fireflies', "Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb"],
    'Epic History': ['Barry Lyndon', 'Oppenheimer', 'Ben-Hur', 'Gone with the Wind', 'Lawrence of Arabia', 'Aguirre, the Wrath of God', 'The Passion of Joan of Arc',
        'Andrei Rublev', 'Farewell My Concubine', 'Robin Hood', 'Malcolm X', 'Hamnet'],
    'Historical Fiction & Myth': ['The Odyssey', 'The Count of Monte Cristo|books'],
    'Gangland & Heists': ['Dog Day Afternoon', 'The Sting', 'The Godfather', 'The Godfather Part II', 'GoodFellas', 'The Departed', 'Casino', 'The Irishman',
        'Pulp Fiction', 'Reservoir Dogs', 'City of God', 'Nine Queens'],
    'Film Noir': ['Chinatown', 'High and Low', 'Vertigo', 'Witness for the Prosecution'],
    'Psychological Thrillers': ['Taxi Driver', 'Rear Window', 'Rope', 'Strangers on a Train', 'North by Northwest', 'The Prestige', 'Oldboy', 'The Handmaiden',
        'Parasite', 'Memories of Murder', 'Cure', 'Perfect Blue', 'The Secret in Their Eyes'],
    'Slashers & Splatter': ['Psycho', 'Jaws', 'The Birds'],
    'Haunted Houses': ['The Shining', 'Kwaidan', 'Ugetsu', 'Onibaba', 'When Evil Lurks'],
    'A24 Moors': ['Possession'],
    'Horror Fiction': ['Locke & Key, Vol. 1: Welcome to Lovecraft|comics', 'The Nice House on the Lake, Vol. 1|comics', 'Gideon Falls Omnibus|comics'],
    'King Country': ['The Shawshank Redemption', 'The Green Mile', 'The Shining', 'Stand by Me'],
    'Final Frontiers': ['2001: A Space Odyssey', 'Interstellar', 'Avatar', 'Avatar: The Way of Water', 'Avatar: Fire and Ash', 'Aliens', 'Arrival', 'E.T. the Extra-Terrestrial',
        'Back to the Future', 'Super 8', 'Ready Player One', 'Stalker', 'On the Silver Globe', 'Metropolis', 'Fantastic Planet', 'Star Trek', 'Star Trek Into Darkness', 'Star Trek Beyond'],
    'Sci-Fi Thrillers': ['Inception', 'Tenet', 'Donnie Darko'],
    'Cyberpunk & Dystopia': ['A Clockwork Orange', 'The Hunger Games', 'TRON: Legacy', 'Serial Experiments Lain|tv', 'V for Vendetta|comics',
        'Absolute Transmetropolitan Vol.  1|comics', 'Y: The Last Man Omnibus|comics'],
    'Space Opera': ['John Carter', 'Saga, Compendium One|comics'],
    'Mecha & Space Opera': ['Transformers'],
    'Action Heroes': ['The Terminator', 'Terminator 2: Judgment Day', 'Goldfinger', 'No Time to Die', 'Hard Boiled', 'Drunken Master II', 'Police Story'],
    'Spectacle Coast': ['Jurassic Park', 'Jurassic World', 'Godzilla Minus One'],
    'Swords & Sorcery': ['The Princess Bride', 'The NeverEnding Story', 'The Wizard of Oz', 'Die Nibelungen: Siegfried', "Pan's Labyrinth"],
    'Lovers\' Lane': ['Titanic', 'Casablanca', 'Roman Holiday', "Breakfast at Tiffany's", 'The Apartment', 'Brief Encounter', 'In the Mood for Love', 'Chungking Express',
        'Portrait of a Lady on Fire', 'La La Land', 'Eternal Sunshine of the Spotless Mind', 'Amélie', 'Pride and Prejudice|books'],
    'Comedy Coast': ['To Be or Not to Be', 'Modern Times', 'City Lights', 'Sherlock Jr.', 'The Grand Budapest Hotel', 'PlayTime'],
    'Jidaigeki': ['Lady Snowblood', 'Kill Bill: Vol. 1'],
    'Hong Kong Action': ['Kill Bill: Vol. 1', 'Kill Bill: Vol. 2', 'John Wick'],
}
# Clear, well-known inspiration that makes sense from both ends (each becomes a two-way portal).
INSPIRED = [
    # (island, destination, why — shown on the portal at both ends)
    ('Spaghetti Westerns', ('island', 'Kurosawa Range'), 'Yojimbo → A Fistful of Dollars'),
    ('A Galaxy Far, Far Away', ('work', 'The Hidden Fortress', 'film'), 'The Hidden Fortress → Star Wars'),
    ('FromSoftware Peaks', ('island', 'Berserk'), 'Berserk → Dark Souls'),
    ("R'lyeh", ('work', 'Bloodborne', 'game'), 'Lovecraft → Bloodborne'),
    ("R'lyeh", ('work', 'The Thing', 'film'), 'Lovecraft → The Thing'),
    ("R'lyeh", ('island', "Junji Ito's Spiral"), 'Lovecraft → Junji Ito'),
    ('Twin Peaks & Lynch', ('work', 'Alan Wake II', 'game'), 'Twin Peaks → Alan Wake'),
    ('Twin Peaks & Lynch', ('island', 'Silent Hill'), 'Twin Peaks → Silent Hill'),
    ('Amblin Suburbs', ('work', 'Stranger Things', 'tv'), 'Spielberg → Stranger Things'),
    ('The Wasteland', ('work', 'Mad Max 2', 'film'), 'Mad Max → Fallout'),
    ('Cyberpunk & Dystopia', ('work', 'Blade Runner', 'film'), 'Blade Runner → cyberpunk'),
    ('Night City', ('work', 'Blade Runner', 'film'), 'Blade Runner → Cyberpunk 2077'),
    ('Castlevania', ('work', "Bram Stoker's Dracula", 'film'), 'Dracula → Castlevania'),
    ('Boomer Shooters', ('work', 'Evil Dead II', 'film'), 'Evil Dead II → Doom'),
    ('Boomer Shooters', ('work', 'Aliens', 'film'), 'Aliens → Doom'),
    ('Indie Precision', ('work', 'Popeye the Sailor Meets Sindbad the Sailor', 'film'), 'Fleischer cartoons → Cuphead'),
    ('Mecha & Space Opera', ('island', 'NERV Headquarters'), 'Evangelion'),
]
WHY = {}
for frm, target, label in INSPIRED:
    PORTALS.append((frm, target, label, label)); WHY[(frm, target[1])] = label
for genre, titles in GENRE_HOMES.items():
    if genre not in byname: print('no island', genre); continue
    g = byname[genre]; gfam = {g['id']} | {q['id'] for q in W['provinces'] if q.get('parent') == g['id']}
    by_src = {}
    for t in titles:
        title, _, med = t.partition('|'); med = med or 'film'
        hits = [i for i in W['items'] if i['t'] == title and i['m'] == med]
        if not hits: print('not found', title, med); continue
        for it in hits[:1]:
            if it['p'] in gfam: continue
            by_src.setdefault(it['p'], []).append(it)
    for src, its in by_src.items():
        its = list({i['t']: i for i in its}.values())
        if len(its) == 1:
            PORTALS.append((genre, ('work', its[0]['t'], its[0]['m']), its[0]['t'], its[0]['t']))
        else:
            names = ', '.join(i['t'] for i in its[:2]) + (f' +{len(its) - 2}' if len(its) > 2 else '')
            PORTALS.append((genre, ('island', next(q['name'] for q in W['provinces'] if q['id'] == src)), names, names))
            GROUP_WORKS[(genre, src)] = [i['id'] for i in its]
out, missing = [], []
for frm, target, label, label_es in PORTALS:
    kind, dest = target[0], target[1]; med = target[2] if len(target) > 2 else None
    if frm not in byname: missing.append(frm); continue
    if kind == 'island':
        if dest not in byname: missing.append(dest); continue
        o = {'from': byname[frm]['id'], 'to': byname[dest]['id'], 'label': label, 'label_es': label_es}
        if (frm, dest) in WHY: o['why'] = True
        if (frm, byname[dest]['id']) in GROUP_WORKS: o['works'] = GROUP_WORKS[(frm, byname[dest]['id'])]
        out.append(o)
    else:
        it = next((i for i in W['items'] if i['t'] == dest and (med is None or i['m'] == med)), None)
        if not it: missing.append(dest); continue
        if it['p'] == byname[frm]['id']: continue                     # already there: no portal needed
        o = {'from': byname[frm]['id'], 'item': it['id'], 'label': label, 'label_es': label_es}
        if (frm, dest) in WHY: o['why'] = True
        out.append(o)
# Every portal works both ways: the far end gets one leading back, named after the island it returns to.
P_ = {q['id']: q for q in W['provinces']}
have = {(o['from'], o.get('to')) for o in out}
back = []
for o in out:
    dest = o.get('to') or next(i['p'] for i in W['items'] if i['id'] == o['item'])
    if (dest, o['from']) in have: continue
    have.add((dest, o['from']))
    via = [o['item']] if o.get('item') else o.get('works')
    b = {'from': dest, 'to': o['from'], 'label': P_[o['from']]['name'], 'label_es': P_[o['from']]['name'], 'back': True}
    if o.get('why'): b['label'] = b['label_es'] = o['label']
    if via:
        titles = [next(i['t'] for i in W['items'] if i['id'] == v) for v in via]
        names = ', '.join(titles[:2]) + (f' +{len(titles) - 2}' if len(titles) > 2 else '')
        b['via'] = via
        if not o.get('why'): b['label'] = f"{names} → {P_[o['from']]['name']}"; b['label_es'] = b['label']
    back.append(b)
out += back
W['portals'] = out
print(f'{len(out)} portals' + (f', not found: {missing}' if missing else ''))
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
