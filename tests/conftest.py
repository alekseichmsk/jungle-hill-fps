import os,pytest
from playwright.sync_api import sync_playwright
BASE=os.environ.get('BASE_URL','http://localhost:8931/').rstrip('/')+'/'
VPS={'desktop1080':(1920,1080),'desktop720':(1280,720),'tablet':(768,1024),'phone':(390,844)}
@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as p:
        b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required','--mute-audio'])
        yield b;b.close()
class G:
    def __init__(s,page):s.page=page;s.errors=[]
    def js(s,code,arg=None):return s.page.evaluate(code,arg)
    def T(s,expr):return s.page.evaluate('()=>{const t=window.__test;return '+expr+'}')
    def wait(s,ms):s.page.wait_for_timeout(ms)
    def until(s,expr,timeout=8000):s.page.wait_for_function('()=>{const t=window.__test;return '+expr+'}',timeout=timeout)
@pytest.fixture
def make(browser):
    ctxs=[]
    def _make(query='',vp=(1280,720),storage=None):
        ctx=browser.new_context(viewport={'width':vp[0],'height':vp[1]});ctxs.append(ctx)
        if storage:ctx.add_init_script('(s=>{if(!sessionStorage.__init){sessionStorage.__init=1;for(const k in s)localStorage.setItem(k,s[k])}})('+__import__('json').dumps(storage)+')')
        pg=ctx.new_page();g=G(pg)
        pg.on('pageerror',lambda e:g.errors.append('pageerror: '+str(e)))
        pg.on('console',lambda m:m.type=='error' and 'Failed to load resource' not in m.text and g.errors.append('console: '+m.text))
        pg.goto(BASE+'index.html'+query,wait_until='load');pg.wait_for_function('()=>document.getElementById("ver")&&(window.__test||!location.search.includes("test"))',timeout=30000);pg.wait_for_timeout(800)
        return g
    yield _make
    for c in ctxs:c.close()
def start(make,m,vp=(1280,720),storage=None):
    g=make(f'?m={m}&test=1',vp,storage);g.until('t.MC!=null');g.page.click('#ovGo');g.until('t.started');return g
