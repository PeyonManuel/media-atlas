import asyncio, functools, http.server, threading, sys, os
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8774),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8774/index.html'); await pg.wait_for_timeout(1300)
        await pg.screenshot(path=f'{OUT}/p_world.png')
        for name,k,tag in (('Shōnen Arena',1.25,'shonen'),('Twentieth-Century Wars',1.7,'story'),('Military Front',1.0,'military')):
            await pg.evaluate("""([n,k]) => { const p = W.provinces.find(p => p.name === n); selectProvince(p.id, {fly:false});
              const r = stage.getBoundingClientRect(); sel.call(zoom.transform, d3.zoomIdentity.translate(r.width/2 - p.lx*k, r.height/2 - (p.ly+50)*k).scale(k)); }""", [name,k])
            await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'{OUT}/p_{tag}.png')
        # which continents does Military Front's island border? nearest other-continent work distance
        print(await pg.evaluate("""() => { const out = {};
          for (const n of ['Military Front','Grimdark','Seinen Darklands','Shadow Moses']) {
            const p = W.provinces.find(p => p.name === n); const fam = p.family.flatMap(q => q.works);
            let best = [1e9, ''];
            for (const w of W.items) { const q = provById.get(w.p); if (q.c === p.c) continue;
              for (const f of fam) { const d = Math.hypot(w.px - f.px, w.py - f.py); if (d < best[0]) best = [d, contById.get(q.c).name]; } }
            out[n] = [Math.round(best[0]), best[1]]; }
          return JSON.stringify(out); }"""))
        print('errors', errs); await b.close()
asyncio.run(main())
