import asyncio, functools, http.server, threading, sys, os
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8769),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: m.type=='error' and 'ERR_FAILED' not in m.text and errs.append(m.text))
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8769/index.html'); await pg.wait_for_timeout(1500)
        # frame Marvel Universe, then click on its land away from works, then on a plateau
        await pg.evaluate("""() => { const p = W.provinces.find(p => p.name === 'Marvel Universe'); const k = 2.3; const r = stage.getBoundingClientRect();
            sel.call(zoom.transform, d3.zoomIdentity.translate(r.width/2 - p.lx*k, r.height/2 - (p.ly+70)*k).scale(k)); }""")
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=f'{OUT}/c_marvel.png')
        pts = await pg.evaluate("""() => { const sub = W.provinces.find(p => p.name === 'Deadpool'); const w = sub.works[0];
            const [sx, sy] = transform.apply([w.px + 4, w.py + 6]);
            const par = W.provinces.find(p => p.name === 'Marvel Universe'); const o = par.works[0];
            const [ox, oy] = transform.apply([o.px + 6, o.py + 7]);
            const r = canvas.getBoundingClientRect(); return [[r.left+sx, r.top+sy],[r.left+ox, r.top+oy]]; }""")
        await pg.mouse.click(*pts[0]); await pg.wait_for_timeout(1100)
        print('click plateau ->', await pg.evaluate("() => [state.selProv && provById.get(state.selProv).name, state.selItem]"), 'k', await pg.evaluate("transform.k.toFixed(2)"))
        await pg.screenshot(path=f'{OUT}/c_sub.png')
        await pg.mouse.click(*pts[1]); await pg.wait_for_timeout(1100)
        print('click land  ->', await pg.evaluate("() => [state.selProv && provById.get(state.selProv).name, state.selItem]"))
        # film / music / tv cards: any 'null' or 'undefined' in the panel?
        for q in ("i.m==='film'","i.m==='music'","i.m==='tv' && i.mins","i.m==='tv' && !i.mins","i.m==='books' && i.len>100"):
            txt = await pg.evaluate(f"() => {{ const i = W.items.find(i => {q} && i.r); selectItem(i.id, {{fly:false}}); const t = document.getElementById('panel-inner').innerText; return [i.t, /null|undefined|NaN/.test(t), (t.match(/Length\\n[^\\n]*/)||[''])[0].replace('\\n',': '), (t.match(/Your rating\\n[^\\n]*/)||[''])[0].replace('\\n',': ')]; }}")
            print(q, '->', txt)
        tip = await pg.evaluate("() => { const i = W.items.find(i => i.m==='film'); buildTip(i); return tip.innerText; }")
        print('film tooltip:', tip.replace('\n',' | '))
        print('errors', errs); await b.close()
asyncio.run(main())
