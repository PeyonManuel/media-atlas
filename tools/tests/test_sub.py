import asyncio, functools, http.server, threading, sys, os
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8768),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: m.type=='error' and 'ERR_FAILED' not in m.text and errs.append(m.text))
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8768/index.html'); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{OUT}/sub_world.png')
        for name,k in (('Shōnen Arena',2.2),('Marvel Universe',2.0),('Survival Horror',2.6)):
            await pg.evaluate("""([n,k]) => { const p = W.provinces.find(p => p.name === n);
              selectProvince(p.id, {fly:false}); const r = stage.getBoundingClientRect();
              sel.call(zoom.transform, d3.zoomIdentity.translate(r.width/2 - p.lx*k, r.height/2 - (p.ly + 40)*k).scale(k)); }""", [name,k])
            await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f'{OUT}/sub_{name.split()[0].lower()}.png')
        # item card + length hover
        await pg.evaluate("() => selectItem(W.items.find(i => i.m==='game' && i.hl && i.r>=9).id)"); await pg.wait_for_timeout(1500)
        await pg.wait_for_timeout(800)
        box = await pg.evaluate("() => { const r = document.querySelector('.rug').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }")
        await pg.mouse.move(box[0]+box[2]*0.4, box[1]+box[3]*0.5); await pg.wait_for_timeout(200)
        cap = await pg.evaluate("() => document.querySelector('.lenviz .lineage-cap').textContent")
        tt = await pg.evaluate("() => document.querySelector('.hoverlen')?.title")
        print('rug hover:', cap); print('card title:', tt)
        await pg.screenshot(path=f'{OUT}/sub_card.png')
        print('errors', errs); await b.close()
asyncio.run(main())
