# Working on Manu's Media Atlas

Owner: Manuel (writes in English or Spanish, casually). The site is deployed by GitHub Pages from `main`;
pushing is publishing. A copy is also published as a claude.ai artifact.

## How it's built
- `index.html` holds the page code and, in `<script type="application/json" id="world">`, the world data.
  Page code is edited directly. World data is **never** hand-edited: change the scripts in `tools/` and run
  `python3 tools/rebuild.py`, which restores `tools/base-world.html`'s data and runs, in order:
  fixes → subisles → series → continents → portals → cohesion → continents → pairs → blurbs.
- `fixes.py` data corrections and moves (anime folded into film/TV, merged seasons, misfiled works).
- `subisles.py` franchise realms as sub-islands (`PARENT`), curated book/game series (`CURATED`, with
  progress counts `run`/`have`), hex-grid island layout with moats.
- `series.py` title-based series detection within islands.
- `continents_links.py` continent sketch positions (`SKETCH`), which continents relate (`LINKS`), island
  neighbours and border preferences. Base relations on what the works actually share (portals, creators),
  not on guesses: an unfounded link (Underworld–Playgrounds) once put unrelated continents side by side.
- `portals.py` two-way portals: genuine double genres (`GENRE_HOMES`) and clear inspirations (`INSPIRED`).
- `cohesion.py` regrows each continent island by island so related islands touch; `pairs.py` seats works
  that share a portal together; `blurbs.json` EN/ES descriptions for every continent, island, sub-island.
- Spanish UI comes from the browser language (`ES` flag, phrase table; source in `tools/i18n.js`).
- Covers are final sprite sheets in `tiles/` (108×160 cells); hi-res covers were dropped on purpose.

## Checks before pushing
`python3 tools/evaluate.py .` (touching relations should not drop), `python3 tools/tests/check_portals.py .`
(must print `misplaced 0`), the `tools/tests/test_*.py` suite (all `errors []`), and look at screenshots
(`shot_island.py . "Island name" 2.2`, `shot_world.py . out.png`). Tests serve d3 from `tools/tests/d3.min.js`.

## Manuel's rules for the map
- Grouping is the priority. Series stay together; big franchises/series become sub-islands; unfinished
  series show progress (4/15), never the full missing list.
- Continents sit by relation and may be reshaped or collide. Islands sit on the border of related continents.
  Games go by theme first; their game genre is a neighbour or a portal.
- Campaign Shooters holds single-player shooters with Boomer Shooters inside; Call of Duty/milsims (Military
  Front, with Battlefield), and Halo are separate islands beside it because they also have multiplayer.
- Portals: always two-way; only for genuine double genres (Butch Cassidy is a western) or clear inspiration
  that makes sense from both ends (Tarantino ↔ westerns / Asian action), never mere topic overlap (Raging
  Bull is not sports manga). Each says concisely why. Works sharing a portal sit together with the portal
  beside them and a visual link. A portal stands among the works it speaks for: inside its own island, on its
  plateau if a sub-island, and clear of sub-islands it doesn't belong to.
- Scores: x/10 for everything, books x/5. 9s (and 4★ books) 1.25×, 10s (5★) 1.5×. No glow, no outlines,
  only a slight halo on the selection. Paused works in colour. Lengths rounded, detail on hover.
- Clicking an island selects it and glides there; sub-islands show in the sidebar only when clicked.
  On phones the sidebar starts closed and portal taps don't open it. Key/footer only when zoomed out.
- Never write "it belongs here too": use a portal.
