import asyncio, functools, http.server, threading, sys, os
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8773),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        errs=[]
        ctx=await b.new_context(locale='es-ES', viewport={'width':1400,'height':860})
        pg=await ctx.new_page(); pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8773/index.html'); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{OUT}/es_world.png')
        # collect panel text in several views, flag lines that look untranslated
        import re
        eng = re.compile(r"\b(the|works|regions|landmarks|your|of|and|hours|pages|rating|released|played|length|series|region|continent|crowd|stops|show all)\b", re.I)
        views = ["selectLedger({fly:false})",
                 "selectContinent('heroes',{fly:false})",
                 "selectProvince(W.provinces.find(p=>p.name==='Epic Fantasy').id,{fly:false})",
                 "selectProvince(W.provinces.find(p=>p.name==='The Cosmere').id,{fly:false})",
                 "selectItem(W.items.find(i=>i.m==='game'&&i.hl&&i.r>=9).id,{fly:false})",
                 "selectItem(W.items.find(i=>i.m==='books'&&i.len>200&&i.crowd).id,{fly:false})",
                 "selectItem(W.items.find(i=>i.m==='tv'&&i.mins).id,{fly:false})",
                 "selectRoute(W.routes[0].id)", "selectCreator(W.items.find(i=>i.m==='books'&&i.c).c)"]
        for v in views:
            txt = await pg.evaluate(f"() => {{ {v}; return document.getElementById('panel').innerText; }}")
            await pg.wait_for_timeout(150)
            txt = await pg.evaluate("() => document.getElementById('panel').innerText")
            lines=[l for l in txt.split('\n') if l.strip() and eng.search(l)]
            print('##', v[:50], '->', len(lines)); [print('   ', l[:120]) for l in lines[:12]]
        key = await pg.evaluate("() => document.getElementById('key').innerText"); print('KEY:', key.replace('\n',' | ')[:300])
        await pg.evaluate("selectProvince(W.provinces.find(p=>p.name==='Epic Fantasy').id,{fly:false})"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=f'{OUT}/es_panel.png')
        print('errors', errs); await b.close()
asyncio.run(main())
