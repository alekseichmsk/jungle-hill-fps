import pytest
from conftest import BASE
def mstart(browser):
    ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2)
    pg=ctx.new_page();pg.goto(BASE+'index.html?m=1&test=1');pg.wait_for_function('window.__test&&__test.MC',timeout=30000);pg.wait_for_timeout(500)
    pg.tap('#ovGo');pg.wait_for_function('__test.started');pg.evaluate('(__test.god(),__test.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true}),1)')
    cdp=ctx.new_cdp_session(pg);return ctx,pg,cdp
def c(pg,sel):
    b=pg.locator(sel).bounding_box();return b['x']+b['width']/2,b['y']+b['height']/2
def T(cdp,typ,pts):cdp.send('Input.dispatchTouchEvent',{'type':typ,'touchPoints':[{'x':x,'y':y,'id':i} for i,x,y in pts]})
def test_fire_drag_aims(browser):
    ctx,pg,cdp=mstart(browser);fx,fy=c(pg,'#fire');y0=pg.evaluate('__test.P.yaw');a0=pg.evaluate('__test.W[__test.P.w].ammo')
    T(cdp,'touchStart',[(1,fx,fy)]);pg.wait_for_timeout(200)
    for k in range(1,8):T(cdp,'touchMove',[(1,fx-k*10,fy-k*3)]);pg.wait_for_timeout(40)
    pg.wait_for_timeout(200);assert pg.evaluate('__test.firing')
    T(cdp,'touchEnd',[(1,fx-70,fy-21)]);pg.wait_for_timeout(100)
    assert pg.evaluate('__test.P.yaw')>y0+.2 and pg.evaluate('__test.W[__test.P.w].ammo')<a0 and not pg.evaluate('__test.firing');ctx.close()
def test_joystick_and_fire_multitouch(browser):
    ctx,pg,cdp=mstart(browser);fx,fy=c(pg,'#fire');jx,jy=c(pg,'#joy')
    p0=pg.evaluate('[__test.P.x,__test.P.z]');y0=pg.evaluate('__test.P.yaw')
    T(cdp,'touchStart',[(1,jx,jy)]);T(cdp,'touchMove',[(1,jx,jy-45)]);T(cdp,'touchStart',[(1,jx,jy-45),(2,fx,fy)])
    for k in range(1,6):T(cdp,'touchMove',[(1,jx,jy-45),(2,fx+k*10,fy)]);pg.wait_for_timeout(60)
    pg.wait_for_timeout(300);T(cdp,'touchEnd',[(2,fx+50,fy)]);pg.wait_for_timeout(100)  # lift fire only (CDP lists ended points)
    assert pg.evaluate('!__test.firing');p1=pg.evaluate('[__test.P.x,__test.P.z]')
    assert abs(p1[0]-p0[0])+abs(p1[1]-p0[1])>.3 and pg.evaluate('__test.P.yaw')<y0-.1
    pg.wait_for_timeout(300);p2=pg.evaluate('[__test.P.x,__test.P.z]');assert abs(p2[0]-p1[0])+abs(p2[1]-p1[1])>.1  # joystick still held
    T(cdp,'touchEnd',[(1,jx,jy-45)]);pg.wait_for_timeout(100);assert pg.evaluate('!__test.firing');ctx.close()
