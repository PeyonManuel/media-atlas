"""Render the atlas as a printable poster: the whole world on one sheet, every work as its cover.

The page itself draws it (index.html?poster): the ledger and controls are put away, every work shows its cover,
names are lettered for print, and the title, key and compass sit in the margins. The site's typefaces come from
tools/poster_fonts (Fontsource builds of the same Google Fonts, under the SIL Open Font License), served in place of
Google Fonts, so the poster looks like the site even offline.

usage: python3 tools/poster.py SITE_DIR OUT_BASENAME [--paper A1|A0|A2] [--dpi 200] [--theme light|dark]
writes OUT_BASENAME.png (the full image), OUT_BASENAME.jpg (a lighter copy) and OUT_BASENAME.pdf (sized to the paper,
landscape).
"""
import argparse, asyncio, functools, http.server, os, threading, time
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

Image.MAX_IMAGE_PIXELS = None
PAPER = {'A0': (1189, 841), 'A1': (841, 594), 'A2': (594, 420)}   # landscape, mm
ap = argparse.ArgumentParser()
ap.add_argument('site'); ap.add_argument('out')
ap.add_argument('--paper', default='A1', choices=PAPER); ap.add_argument('--dpi', type=int, default=200)
ap.add_argument('--theme', default='light', choices=['light', 'dark']); ap.add_argument('--port', type=int, default=8790)
a = ap.parse_args()
SITE = os.path.abspath(a.site); HERE = Path(__file__).parent; FONTS = HERE / 'poster_fonts'; D3 = HERE / 'tests' / 'd3.min.js'
mm_w, mm_h = PAPER[a.paper]
px_w, px_h = round(mm_w / 25.4 * a.dpi), round(mm_h / 25.4 * a.dpi)
# The sheet is always laid out at 100 CSS pixels to the inch, so the composition is the same at every resolution;
# the dpi only sets how many device pixels each CSS pixel gets.
SCALE = a.dpi / 100
css_w, css_h = round(mm_w / 25.4 * 100), round(mm_h / 25.4 * 100)

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', a.port), functools.partial(Q, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-gpu-memory-buffer-video-frames'])
        c = await b.new_context(viewport={'width': css_w, 'height': css_h}, device_scale_factor=SCALE, color_scheme=a.theme)
        pg = await c.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route(lambda u: not u.startswith(f'http://127.0.0.1:{a.port}'), lambda r: r.abort())
        await pg.route('**/cdnjs.cloudflare.com/**', lambda r: r.fulfill(path=str(D3), content_type='text/javascript'))
        await pg.route('**/fonts.googleapis.com/**', lambda r: r.fulfill(path=str(FONTS / 'fonts.css'), content_type='text/css'))
        await pg.route('**/__fonts/**', lambda r: r.fulfill(path=str(FONTS / r.request.url.rsplit('/', 1)[1]), content_type='font/woff2'))
        await pg.goto(f'http://127.0.0.1:{a.port}/index.html?poster', wait_until='load')
        await pg.evaluate('document.fonts.ready')
        await pg.wait_for_timeout(1500)
        # wait until every tile and cover is drawn and stays drawn
        calm, t0 = 0, time.time()
        while calm < 6 and time.time() - t0 < 600:
            busy = await pg.evaluate('window.__posterBusy !== false')
            calm = 0 if busy else calm + 1
            await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'{a.out}.png', full_page=False)
        hid = await pg.evaluate('[...(window.__hid || [])]')   # island names with no room even after nudging
        print(f'{px_w}x{px_h} px for {a.paper} at {a.dpi} dpi ({a.theme}); waited {time.time() - t0:.0f}s; errors {errs}')
        print(f'island names left out for lack of room: {len(hid)} {hid}')
        await b.close()
asyncio.run(main())

im = Image.open(f'{a.out}.png').convert('RGB')
im.save(f'{a.out}.jpg', quality=92, optimize=True, dpi=(a.dpi, a.dpi))
im.save(f'{a.out}.pdf', resolution=a.dpi, quality=95)   # sized to the paper at this dpi
for ext in ('png', 'jpg', 'pdf'):
    print(f'{a.out}.{ext}: {os.path.getsize(f"{a.out}.{ext}") / 1e6:.1f} MB')
