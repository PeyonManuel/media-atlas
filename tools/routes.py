"""Connections: curated threads between works that sit apart on the map (W['routes']).

A portal says a work belongs on a second island too (Butch Cassidy is a western). A connection says works
in different places belong to one story: who inspired whom, one creator or composer across genres, one
author's world in several media. Each is traced across the map through its stops, in release order.
Keep to what is documented (said by the makers, credited, or widely reported), and only works on the map.
usage: python3 routes.py SITE_DIR
"""
import json, re, sys
from pathlib import Path

SITE = Path(sys.argv[1])
html = (SITE / 'index.html').read_text()
m = re.search(r'(<script type="application/json" id="world">)(.*?)(</script>)', html, re.S)
W = json.loads(m.group(2))
items = {i['id']: i for i in W['items']}

# (id, name, name in Spanish, blurb, blurb in Spanish, stop ids in order)
ROUTES = [
    # --- the three bests ---
    ('big3seinen', 'The Big Three of seinen', 'Los tres grandes del seinen',
     "The trio seinen readers most often name as the peak of the form: Miura's Berserk, Inoue's Vagabond and Urasawa's Monster.",
     'El trío que los lectores de seinen señalan como la cumbre del género: Berserk de Miura, Vagabond de Inoue y Monster de Urasawa.',
     ['m5h', 'm5v', 'm63']),
    ('big3shonen', 'The Big Three of Shōnen Jump', 'Los tres grandes de la Shōnen Jump',
     'The three series that carried Weekly Shōnen Jump through the 2000s.',
     'Las tres series que sostuvieron la Weekly Shōnen Jump durante los 2000.',
     ['m5i', 'm93', 'm68']),
    # --- inspiration ---
    ('kurosawa', "Kurosawa's descendants", 'Los herederos de Kurosawa',
     "George Lucas has said The Hidden Fortress shaped Star Wars, told through two squabbling peasants. Sergio Leone's A Fistful of Dollars is an unauthorised remake of Yojimbo.",
     'George Lucas ha dicho que La fortaleza escondida dio forma a Star Wars, contada por dos campesinos que se pelean. Por un puñado de dólares de Sergio Leone es un remake no autorizado de Yojimbo.',
     ['fkk', 'fzi', 'fk6', 'fjq']),
    ('berserksouls', "Berserk's long shadow", 'La larga sombra de Berserk',
     "Hidetaka Miyazaki has cited Kentaro Miura's Berserk as a key influence on FromSoftware's dark fantasy.",
     'Hidetaka Miyazaki ha citado el Berserk de Kentaro Miura como una influencia clave en la fantasía oscura de FromSoftware.',
     ['m5h', 'g179', 'g16f', 'g14z', 'g14c', 'g11t']),
    ('lovecraft', "Lovecraft's heirs", 'Los herederos de Lovecraft',
     "Cosmic horror after Lovecraft: John Carpenter's The Thing, Junji Ito (who cites Lovecraft among his influences) and FromSoftware's Bloodborne.",
     'El horror cósmico después de Lovecraft: La cosa de John Carpenter, Junji Ito (que cita a Lovecraft entre sus influencias) y Bloodborne de FromSoftware.',
     ['be9', 'fym', 'm5r', 'g14z']),
    ('killbill', "Kill Bill's ingredients", 'Los ingredientes de Kill Bill',
     "Tarantino built the Bride's revenge on Lady Snowblood and cast Gordon Liu, star of The 36th Chamber of Shaolin, in both volumes.",
     'Tarantino construyó la venganza de la Novia sobre Lady Snowblood y eligió a Gordon Liu, estrella de La cámara 36 de Shaolin, en los dos volúmenes.',
     ['f101', 'fzf', 'fu1', 'ftr']),
    ('doomroots', 'What Doom was made of', 'De qué está hecho Doom',
     "id Software has described Doom as Aliens meets Evil Dead II: marines, a chainsaw and a base overrun by demons.",
     'id Software ha descrito Doom como Aliens con Posesión infernal II: marines, una motosierra y una base invadida por demonios.',
     ['fy0', 'fxw', 'g19y', 'g19v']),
    ('twinpeaks', "Twin Peaks' long shadow", 'La larga sombra de Twin Peaks',
     "David Lynch's small-town dread is a named influence on Silent Hill and on Remedy's Alan Wake games.",
     'El inquietante pueblo de David Lynch es una influencia reconocida de Silent Hill y de los Alan Wake de Remedy.',
     ['t1dn', 'g19a', 'g191', 'g11h']),
    ('strangerthings', "Stranger Things' ingredients", 'Los ingredientes de Stranger Things',
     "The Duffer brothers built Stranger Things out of Spielberg's suburbs, Stephen King's kids on bikes and John Carpenter's The Thing, whose poster hangs in Mike's basement.",
     'Los hermanos Duffer construyeron Stranger Things con los barrios de Spielberg, los chavales en bici de Stephen King y La cosa de John Carpenter, cuyo póster cuelga en el sótano de Mike.',
     ['fyo', 'fym', 'fxz', 't1c4']),
    ('madmax', 'From Mad Max to Fallout', 'De Mad Max a Fallout',
     "Fallout's wasteland owes a lot to The Road Warrior: its dog Dogmeat and its leather-jacketed wanderer are nods to Mad Max 2.",
     'El yermo de Fallout le debe mucho a Mad Max 2: el perro Dogmeat y su vagabundo de chaqueta de cuero son guiños a la película.',
     ['fz8', 'fyr', 'g166', 'fo6', 't1bz']),
    ('cyberpunk', "Cyberpunk's family tree", 'El árbol del cyberpunk',
     'Blade Runner set the look of the neon future; Akira and Ghost in the Shell carried it into manga and anime, and the Wachowskis showed Ghost in the Shell to their producer to explain The Matrix. Night City carries the line on.',
     'Blade Runner fijó el aspecto del futuro de neón; Akira y Ghost in the Shell lo llevaron al manga y al anime, y las Wachowski enseñaron Ghost in the Shell a su productor para explicarle Matrix. Night City sigue la línea.',
     ['fyn', 'm5y', 'a1s', 'fvh', 'fn4', 'g124', 'a2d']),
    ('dracula', "Dracula's descendants", 'Los descendientes de Drácula',
     "Bram Stoker's count is the enemy the Belmonts face in Castlevania from the first game on; Coppola went back to the novel in 1992.",
     'El conde de Bram Stoker es el enemigo de los Belmont en Castlevania desde el primer juego; Coppola volvió a la novela en 1992.',
     ['bdd', 'g1ac', 'fwz']),
    ('cuphead', "Cuphead's 1930s", 'Los años treinta de Cuphead',
     "Studio MDHR drew Cuphead by hand in the style of the Fleischer brothers' 1930s cartoons.",
     'Studio MDHR dibujó Cuphead a mano al estilo de los dibujos de los hermanos Fleischer de los años treinta.',
     ['flx', 'g13l']),
    ('shakespeare', 'Shakespeare, retold', 'Shakespeare, contado de nuevo',
     "Kurosawa moved Macbeth and King Lear to feudal Japan, Disney's The Lion King takes its plot from Hamlet, and Hamnet imagines the grief behind it.",
     'Kurosawa llevó Macbeth y El rey Lear al Japón feudal, El rey león de Disney toma su trama de Hamlet y Hamnet imagina el duelo que hay detrás.',
     ['fkv', 'fy7', 'fwi', 'fi1']),
    ('dune', "Dune and Star Wars", 'Dune y Star Wars',
     "Frank Herbert's desert planet, its spice and its chosen son are often named among Star Wars' sources; Villeneuve's films go back to the novel.",
     'El planeta desierto de Frank Herbert, su especia y su elegido suelen citarse entre las fuentes de Star Wars; las películas de Villeneuve vuelven a la novela.',
     ['bap', 'fzi', 'fja', 'fic']),
    ('tolkien', "Tolkien's road", 'El camino de Tolkien',
     'Middle-earth, and The Wheel of Time, whose opening Robert Jordan modelled on The Fellowship of the Ring on purpose.',
     'La Tierra Media y La Rueda del Tiempo, cuyo comienzo Robert Jordan escribió a propósito como eco de La Comunidad del Anillo.',
     ['bhb', 'bd7', 'bdl']),
    ('christie', "Agatha Christie's islands", 'Las islas de Agatha Christie',
     "Christie's island of ten guests, Billy Wilder's film of her play, and Umineko, which sets its own island mystery against And Then There Were None by name.",
     'La isla de los diez invitados de Christie, la película de Billy Wilder sobre su obra de teatro y Umineko, que enfrenta su propio misterio en una isla a Diez negritos por su nombre.',
     ['bbn', 'fkm', 'm7g']),
    ('alice', 'Down the rabbit hole', 'Por la madriguera del conejo',
     "Lewis Carroll's Wonderland, Disney's two trips there, and The Matrix, which sends Neo after the white rabbit and down the rabbit hole.",
     'El País de las Maravillas de Lewis Carroll, los dos viajes de Disney allí y Matrix, que manda a Neo detrás del conejo blanco y madriguera abajo.',
     ['bez', 'flc', 'fvh', 'fqu']),
    ('kon', "Perfect Blue's echo", 'El eco de Perfect Blue',
     "Darren Aronofsky bought the rights to Satoshi Kon's Perfect Blue and restaged its bathtub shot in Requiem for a Dream.",
     'Darren Aronofsky compró los derechos de Perfect Blue de Satoshi Kon y recreó su plano de la bañera en Réquiem por un sueño.',
     ['a1t', 'fv3']),
    # --- one hand across the map ---
    ('toriyama', "Toriyama's children", 'Los hijos de Toriyama',
     'Akira Toriyama drew Dragon Ball and the characters of Dragon Quest and Chrono Trigger; Eiichiro Oda and Masashi Kishimoto have both named Dragon Ball as why they draw manga.',
     'Akira Toriyama dibujó Dragon Ball y los personajes de Dragon Quest y Chrono Trigger; Eiichiro Oda y Masashi Kishimoto han dicho que dibujan manga por Dragon Ball.',
     ['m6j', 'g17f', 'g19r', 'm5i', 'm93']),
    ('martin', "George R. R. Martin's worlds", 'Los mundos de George R. R. Martin',
     "Westeros on the page and on HBO, and the Lands Between, whose ancient history Martin wrote for FromSoftware's Elden Ring.",
     'Poniente en papel y en HBO, y las Tierras Intermedias, cuya historia antigua escribió Martin para Elden Ring de FromSoftware.',
     ['bed', 't1dq', 'g11t', 't1cg', 't1bv']),
    ('naughtydog', 'Naughty Dog', 'Naughty Dog',
     "Naughty Dog's run from Crash Bandicoot and Jak and Daxter to Uncharted and The Last of Us, which its co-creator Neil Druckmann also brought to HBO.",
     'La trayectoria de Naughty Dog, de Crash Bandicoot y Jak and Daxter a Uncharted y The Last of Us, que su cocreador Neil Druckmann también llevó a HBO.',
     ['g19m', 'g18y', 'g17l', 'g15o', 'g14b', 't1cm']),
    ('kamiya', 'Born from Resident Evil 4', 'Nacido de Resident Evil 4',
     "Hideki Kamiya directed Resident Evil 2; his prototype for Resident Evil 4 became Devil May Cry, and Capcom took Resident Evil 4 another way.",
     'Hideki Kamiya dirigió Resident Evil 2; su prototipo de Resident Evil 4 se convirtió en Devil May Cry, y Capcom llevó Resident Evil 4 por otro camino.',
     ['g19h', 'g18f', 'g185', 'g130']),
    ('insomniac', 'Insomniac Games', 'Insomniac Games',
     "Insomniac's games, from Ratchet & Clank's gadgets to Marvel's Spider-Man.",
     'Los juegos de Insomniac, de los artilugios de Ratchet & Clank a Marvel\'s Spider-Man.',
     ['g18m', 'g139']),
    ('coens', 'The Coen brothers', 'Los hermanos Coen',
     "Joel and Ethan Coen's crime stories, from Fargo to their Cormac McCarthy adaptation, and the Fargo series made with them as executive producers.",
     'Las historias criminales de Joel y Ethan Coen, de Fargo a su adaptación de Cormac McCarthy, y la serie Fargo, con ellos como productores ejecutivos.',
     ['fvw', 'fvn', 'fsb', 't1d8']),
    ('ridley', "Ridley Scott's worlds", 'Los mundos de Ridley Scott',
     "Ridley Scott's worlds: the Nostromo, Los Angeles 2019, Rome, Sherwood and Mars.",
     'Los mundos de Ridley Scott: la Nostromo, Los Ángeles 2019, Roma, Sherwood y Marte.',
     ['fz6', 'fyn', 'fv4', 'fqr', 'fnz']),
    ('watanabe', "Shinichirō Watanabe's anime", 'El anime de Shinichirō Watanabe',
     'Jazz among bounty hunters in space, then hip-hop in Edo.',
     'Jazz entre cazarrecompensas en el espacio, y luego hip-hop en Edo.',
     ['a1g', 'a4j', 'a1h']),
    ('urobuchi', 'Written by Gen Urobuchi', 'Escrito por Gen Urobuchi',
     'Gen Urobuchi wrote both Madoka Magica and the first Psycho-Pass.',
     'Gen Urobuchi escribió Madoka Magica y la primera temporada de Psycho-Pass.',
     ['a4b', 'a3p', 'a4f']),
    ('cosmere', 'The Cosmere', 'El Cosmere',
     "Brandon Sanderson's novels share one universe, tied together by worldhoppers like Hoid.",
     'Las novelas de Brandon Sanderson comparten un universo, unido por viajeros entre mundos como Hoid.',
     ['bbj', 'bf2', 'bh9', 'be8', 'bbi', 'bg3', 'be5', 'bf4', 'be6', 'bf3', 'bb8']),
    ('shooters', 'From Doom to Ultrakill', 'De Doom a Ultrakill',
     "The first-person shooters on the map, in release order: id's Doom, Valve's story shooters, Halo on console, and the retro revival.",
     'Los shooters en primera persona del mapa, en orden: el Doom de id, los shooters narrativos de Valve, Halo en consola y el revival retro.',
     ['g19y', 'g19v', 'g19d', 'g18z', 'g18i', 'g17u', 'g14a', 'g135', 'g12b']),
    ('square', "Square's golden age", 'La edad de oro de Square',
     "Square's run of role-playing games from 1994 to 2000, several of them scored by Nobuo Uematsu.",
     'Los juegos de rol de Square de 1994 a 2000, varios con música de Nobuo Uematsu.',
     ['g19w', 'm1g1', 'g19r', 'g19j', 'm1g2', 'g19g', 'g194']),
    ('hbo', "HBO's golden age", 'La edad de oro de HBO',
     "HBO's run of prestige drama, from The Sopranos to Chernobyl.",
     'Los dramas de prestigio de HBO, de Los Soprano a Chernobyl.',
     ['t1bs', 't1dj', 't1do', 't1dq', 't1cs']),
    # --- composers ---
    ('morricone', "Ennio Morricone's scores", 'Las bandas sonoras de Ennio Morricone',
     "Every Sergio Leone film on the map, and Morricone's scores beyond the West: The Battle of Algiers, The Thing, The Untouchables, Cinema Paradiso, and the Oscar at last for The Hateful Eight.",
     'Todas las películas de Sergio Leone del mapa y las bandas sonoras de Morricone más allá del Oeste: La batalla de Argel, La cosa, Los intocables, Cinema Paradiso y, por fin, el Óscar por Los odiosos ocho.',
     ['fjq', 'fjj', 'f10q', 'm1l4', 'fjh', 'f10h', 'fym', 'fyd', 'fxu', 'fxn', 'fnw']),
    ('zimmer', "Hans Zimmer's scores", 'Las bandas sonoras de Hans Zimmer',
     "Hans Zimmer's scores, alone or with collaborators, from Rain Man to Nolan's films and Villeneuve's Dune; The Lion King and Dune both won him the Oscar.",
     'Las bandas sonoras de Hans Zimmer, solo o con colaboradores, de Rain Man a las películas de Nolan y el Dune de Villeneuve; El rey león y Dune le dieron el Óscar.',
     ['fxm', 'fwi', 'fv4', 'fty', 'ftb', 'fsm', 'frl', 'fqk', 'fod', 'm1gm', 'fn8', 'fn4', 'fja', 'fic', 'm1gn']),
    ('williams', "John Williams' scores", 'Las bandas sonoras de John Williams',
     'John Williams scored nearly every Spielberg film and the Star Wars saga; Jaws, Star Wars, E.T. and Schindler\'s List all won him the Oscar.',
     'John Williams puso música a casi todas las películas de Spielberg y a la saga Star Wars; Tiburón, Star Wars, E.T. y La lista de Schindler le dieron el Óscar.',
     ['fzr', 'fzi', 'm1gd', 'fz1', 'fyu', 'fyo', 'fxe', 'fwu', 'fwp', 'fvi', 'fum', 'fiw']),
]

out, bad = [], []
for rid, name, name_es, blurb, blurb_es, stops in ROUTES:
    miss = [s for s in stops if s not in items]
    if miss: bad.append((rid, miss)); stops = [s for s in stops if s in items]
    if len(stops) < 2: continue
    out.append({'id': rid, 'name': name, 'name_es': name_es, 'blurb': blurb, 'blurb_es': blurb_es, 'items': stops})
W['routes'] = out
print(f'{len(out)} connections' + (f', missing works: {bad}' if bad else ''))
(SITE / 'index.html').write_text(html[:m.start(2)] + json.dumps(W, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):])
