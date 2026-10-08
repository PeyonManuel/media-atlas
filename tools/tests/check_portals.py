import asyncio, functools, http.server, threading, sys, os
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8777),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8777/index.html'); await pg.wait_for_timeout(1300)
        # a portal is misplaced if the nearest work to it belongs to another island, or (sub-island) it's off its plateau
        r = await pg.evaluate("""() => { const bad = [];
          for (const pt of PORTALS) { const h = portalHome(pt); if (!h.ws.length) continue;
            if (!portalOk(pt, h)) { const near = qItems.find(pt.px, pt.py);
              bad.push(`${provById.get(pt.from).name}: ${pt.lbl.slice(0,40)} [near ${provById.get(near.p).name}]`); } }
          return [PORTALS.length, bad]; }""")
        print('portals', r[0], 'misplaced', len(r[1])); [print('  ', x) for x in r[1][:40]]
        print('errors', errs); await b.close()
asyncio.run(main())
