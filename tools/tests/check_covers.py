"""Covers that run into each other when zoomed in: pairs of works whose drawn objects (cover + case) overlap.
usage: python3 tools/tests/check_covers.py SITE_DIR"""
import asyncio, functools, http.server, threading, sys, os, json
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8779),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8779/index.html'); await pg.wait_for_timeout(1300)
        r = await pg.evaluate("""() => {
          // each work's object box (cover plus its case), expansions included in their game's box
          const box = i => { const fr = frameOf(i), M = objMargins(i, fr.w, fr.h);
            let x0 = fr.cx - fr.w/2 - M.l, x1 = fr.cx + fr.w/2 + M.r, y0 = fr.cy - fr.h/2 - M.t, y1 = fr.cy + fr.h/2 + M.b;
            for (const k of (KIDS.get(i.id) || [])) { const f = frameOf(k); x1 = Math.max(x1, f.cx + f.w * 0.6); y0 = Math.min(y0, f.cy - f.h * 0.6); }
            return [x0, y0, x1, y1]; };
          const ws = W.items.filter(i => !i.dl && i.sp).map(i => [i, box(i)]);
          const q = d3.quadtree(ws, d => d[0].px, d => d[0].py);
          const bad = []; let worst = 0;
          for (const [i, a] of ws) {
            q.visit((nd, x0, y0, x1, y1) => {
              if (!nd.length) { let d = nd; do { const [j, b] = d.data;
                if (j.id > i.id) { const ox = Math.min(a[2], b[2]) - Math.max(a[0], b[0]), oy = Math.min(a[3], b[3]) - Math.max(a[1], b[1]);
                  if (ox > 0.3 && oy > 0.3) { const f = Math.min(ox, oy); bad.push([+f.toFixed(1), i.t, j.t, provById.get(i.p).name, provById.get(j.p).name]); worst = Math.max(worst, f); } } } while (d = d.next); }
              return x0 > a[2] + 30 || x1 < a[0] - 30 || y0 > a[3] + 30 || y1 < a[1] - 30; });
          }
          bad.sort((u, v) => v[0] - u[0]);
          return [ws.length, bad.length, worst, bad.slice(0, 15), SPACE];
        }""")
        print('works', r[0], 'overlapping pairs', r[1], 'worst', round(r[2],1), 'SPACE', r[4]); [print('  ', x) for x in r[3]]
        print('errors', errs); await b.close()
asyncio.run(main())
