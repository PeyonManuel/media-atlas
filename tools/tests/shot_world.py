import asyncio, functools, http.server, threading, sys, os
from playwright.async_api import async_playwright
SITE=sys.argv[1]; OUTF=sys.argv[2]; OUT=os.path.dirname(os.path.abspath(__file__)); D3=os.path.join(OUT,'d3.min.js')
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8776),functools.partial(Q,directory=SITE)); threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':860})
        await pg.route('**/cdnjs.cloudflare.com/**',lambda r:r.fulfill(path=D3,content_type='text/javascript'))
        await pg.route('**/fonts.g*/**',lambda r:r.abort())
        await pg.goto('http://127.0.0.1:8776/index.html'); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=OUTF); await b.close()
asyncio.run(main())
