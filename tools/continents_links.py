"""Shared relations: where continents sit, which relate, which islands neighbour or face which continent."""
SKETCH = {
    'heroes': (0, 0), 'fantasy': (1.05, 0.1), 'grim': (0.35, -0.95), 'action': (1.35, -0.9),
    'horror': (2.3, -0.35), 'sports': (2.3, -1.45), 'space': (2.0, 0.9), 'crime': (-0.65, -1.05),
    'surreal': (-1.05, 0.1), 'heart': (-1.75, -0.7), 'play': (-0.35, 1.05), 'classic': (-1.2, -2.05),
    'build': (-0.3, -1.95), 'war': (0.85, -1.9), 'samurai': (1.65, -2.45), 'western': (0.3, -2.75),
}
LINKS = [
    ('heroes', 'fantasy'), ('heroes', 'grim'), ('heroes', 'action'), ('fantasy', 'grim'), ('fantasy', 'space'),
    ('grim', 'action'), ('action', 'horror'), ('action', 'sports'), ('grim', 'crime'), ('horror', 'space'),
    ('action', 'war'), ('war', 'samurai'), ('war', 'western'), ('samurai', 'western'), ('grim', 'war'),
    ('crime', 'surreal'), ('surreal', 'heart'), ('crime', 'heart'), ('classic', 'crime'), ('classic', 'heart'),
    ('play', 'heroes'), ('play', 'surreal'), ('play', 'fantasy'), ('build', 'grim'), ('build', 'crime'), ('surreal', 'heroes'), ('build', 'western'), ('samurai', 'action'),
]

NEIGHBOURS = [('Campaign Shooters', 'Military Front'), ('Campaign Shooters', 'Halo'), ('Military Front', 'Halo'), ('Military Front', 'Boomer Shooters'), ('Campaign Shooters', 'Boomer Shooters'), ('Campaign Shooters', 'Cinematic Adventures'),
              ('Kurosawa Range', 'Jidaigeki'), ('Samurai Manga & Anime', 'Jidaigeki'), ('Character Action', 'Cinematic Adventures'),
              ('Thrillers & Mysteries', 'Psychological Thrillers'), ('Epic Fantasy', 'Swords & Sorcery'), ('Grimdark', 'Seinen Darklands')]

BORDER = [('Military Front', 'war'), ('Grimdark', 'crime'), ('Shadow Moses', 'action'), ('Seinen Darklands', 'heroes'),
          ('Shōnen Arena', 'grim'), ('Hong Kong Action', 'action')]
