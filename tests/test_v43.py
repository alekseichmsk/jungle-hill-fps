import pytest
from conftest import start
TRACK='''(()=>{window.__loops=[];const o=AudioBufferSourceNode.prototype.start;AudioBufferSourceNode.prototype.start=function(...a){if(this.loop)window.__loops.push(this);return o.apply(this,a)}})()'''
@pytest.mark.parametrize('m',[1,2,3,4,5,6,7,8])
def test_ally_sprites_loaded(make,m):
    g=start(make,m)
    r=g.T('t.allies.map(a=>{const mt=a.s.material,im=mt.map&&mt.map.image;return {ok:!!im&&im.width>24&&im.height>24,vis:a.s.visible&&mt.opacity>0,inScene:!!a.s.parent}})')
    assert r and all(x['ok'] and x['vis'] and x['inScene'] for x in r),r
    # aim frame also a real sprite
    g.T('(()=>{const a=t.allies[0],e=t.enemies[0];e.dorm=false;e.s.position.set(a.s.position.x,e.h/2,a.s.position.z-8);return 1})()');g.wait(800)
    assert g.T('t.allies[0].s.material.map.image.width>24')
def test_no_continuous_noise(make):
    g=make('?m=1&test=1');g.page.evaluate(TRACK);g.until('t.MC!=null');g.page.click('#ovGo');g.until('t.started')
    g.T('t.say("obj_done_1")');g.wait(1500)
    assert g.T('t.vnoise')is None
    # only wind bed and gated flame loop allowed; insect hiss loop removed
    assert g.page.evaluate('window.__loops.length')<=2
