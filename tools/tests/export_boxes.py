"""Write tools/boxes.json: each work's drawn footprint (cover, case and fanned expansions) relative to its
map point, measured in the page itself, for tools/spread.py. Rerun whenever cover sizes change in the page.
usage: python3 tools/tests/export_boxes.py SITE_DIR"""
import asyncio, functools, http.server, threading, sys, os, json
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8780),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860})
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8780/index.html'); await pg.wait_for_timeout(1300)
        boxes = await pg.evaluate("""() => { const out = {};
          for (const i of W.items) { if (i.dl || !i.sp) continue;
            const [x0, y0, x1, y1] = footprint(i);
            out[i.id] = [x0 - i.px, y0 - i.py, x1 - i.px, y1 - i.py].map(v => +v.toFixed(2)); }
          return out; }""")
        await b.close()
    json.dump(boxes, open(os.path.join(OUT, '..', 'boxes.json'), 'w'), separators=(',', ':'))
    print(len(boxes), 'boxes')
asyncio.run(main())
