import asyncio, functools, http.server, threading, sys, os
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8772),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        errs=[]
        pg=await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8772/index.html'); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{OUT}/m_closed.png')
        await pg.tap('#panel-toggle'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'{OUT}/m_open.png')
        # desktop: portals and a paused work
        pd=await b.new_page(viewport={'width':1400,'height':860}); pd.on('pageerror',lambda e: errs.append(str(e)))
        await pd.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pd.route('**/fonts.g*/**',lambda r:r.abort())
        await pd.goto('http://127.0.0.1:8772/index.html'); await pd.wait_for_timeout(1300)
        await pd.evaluate("""() => { const p = W.provinces.find(p => p.name === 'Campaign Shooters'); selectProvince(p.id, {fly:false});
            const k = 2.0, r = stage.getBoundingClientRect(); sel.call(zoom.transform, d3.zoomIdentity.translate(r.width/2 - p.lx*k, r.height/2 - (p.ly+60)*k).scale(k)); }""")
        await pd.wait_for_timeout(1300)
        await pd.screenshot(path=f'{OUT}/portal.png')
        print('portals', await pd.evaluate("PORTALS.length"), await pd.evaluate("[...document.querySelectorAll('#panel-inner h3')].map(h=>h.textContent).join(', ')"))
        print('errors', errs); await b.close()
asyncio.run(main())
