# Manu's Media Atlas

A map of ~1,900 films, shows, books, manga, comics, games and albums from Letterboxd, Serializd, AniList,
Goodreads, Backloggd and RateYourMusic, drawn as continents, islands and sub-islands of related works.

**Live:** https://peyonmanuel.github.io/media-atlas/

## What's here

| Path | What it is |
| --- | --- |
| `index.html` | The whole site: a single canvas page (d3 7.9.0 from cdnjs) with the world data embedded as JSON |
| `tiles/` | Cover sprite sheets (WebP), loaded lazily as you zoom in |
| `tools/` | The Python pipeline that builds the world data (layout, sub-islands, series, portals, descriptions) |
| `tools/base-world.html` | The original surveyed data every rebuild starts from |
| `tools/tests/` | Headless-browser checks (Playwright + Chromium) and screenshot helpers |

## Rebuilding

```sh
pip install numpy playwright      # Chromium for Playwright as well
python3 tools/rebuild.py          # rewrites the world JSON inside index.html
python3 tools/evaluate.py .       # how well related islands sit together
python3 tools/tests/check_portals.py .   # every portal stands on its own island
```

The rebuild is deterministic: run on unchanged scripts it reproduces `index.html` byte for byte.
