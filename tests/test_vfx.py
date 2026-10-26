import pytest
from conftest import VPS,start
def calm(g):g.T('(t.freeze(),t.god(),t.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true}),t.allies.forEach(a=>a.s.position.x+=200),1)')

@pytest.mark.parametrize('vp',['desktop720','phone'])
def test_lowres_target_size(make,vp):
    g=start(make,1,VPS[vp]);W,H=g.T('[t.vfx.W,t.vfx.H]');w,h=VPS[vp]
    assert min(W,H)==270 and abs(W/H-w/(h-110))<0.02,(W,H)
    assert g.T('t.vfx.rt!==null')

def test_graphics_toggle_cycles_and_persists(make):
    g=start(make,1);assert 'ВЫСОКО' in g.T('t.gtext')
    g.page.click('#menuB');g.page.click('#pSet');g.page.click('#gtog');assert g.T('t.vfx.mode')=='dither'
    g.page.click('#gtog');assert g.T('t.vfx.mode')=='low' and g.T('t.vfx.rt===null')
    assert g.js('localStorage.h937_gfx')=='low'
    g.page.reload();g.page.wait_for_function('()=>window.__test&&window.__test.MC');assert g.T('t.vfx.mode')=='low' and 'НИЗКО' in g.T('t.gtext')
    g.page.click('#menuB');g.page.click('#gtog');assert g.T('t.vfx.mode')=='high' and g.T('t.vfx.rt!==null')
    assert g.errors==[]

def test_explosion_layers_light_and_cleanup(make):
    g=start(make,1);calm(g);base=g.T('t.vfx.smokes.length')
    g.T('(t.boom(t.P.x,t.P.z-25),1)');g.wait(100)
    assert g.T('t.vfx.lights.some(l=>l.intensity>0)'),'no explosion light'
    assert g.T('t.vfx.smokes.length')>base;assert g.T('t.ipAlive()')>20,'no debris'
    g.wait(900);assert g.T('t.vfx.lights.every(l=>l.intensity==0)'),'light not short-lived'
    assert g.T('t.vfx.smokes.length')>base,'smoke should linger'
    g.until('t.vfx.smokes.length<=%d&&t.ipAlive()==0'%base,timeout=10000)

def test_close_explosion_whiteout_far_none(make):
    g=start(make,1);calm(g)
    g.T('(t.boom(t.P.x,t.P.z-30),1)');g.wait(30);assert g.T('t.vfx.white')==0 and g.T('t.vfx.tear')==0
    w,te,ch,sh=g.T('(t.boom(t.P.x,t.P.z-3),[t.vfx.white,t.vfx.tear,t.vfx.chroma,t.vfx.shake])');assert w>0.5 and te>0.4 and ch>0.4 and sh>0.05
    g.until('t.vfx.white==0&&t.vfx.tear<0.1',timeout=1500)

def test_shot_shake_scaled_by_weapon(make):
    g=start(make,5);calm(g);vals={}
    for w in [3,1]:
        vals[w]=g.T(f'(t.P.w={w},t.vfx.shake=0,t.shoot(),t.vfx.shake)')
    assert vals[1]>vals[3]>0;g.until('t.vfx.shake==0',timeout=3000)

def test_blood_decals_capped(make):
    g=start(make,1);calm(g)
    g.T('(()=>{for(let i=0;i<400;i++)t.bloodDecal(t.P.x+Math.random()*4,t.P.z-3-Math.random()*4,1);return 1})()')
    assert g.T('t.vfx.decals.length')==g.T('t.vfx.DECAL_CAP')

def test_kill_spawns_gibs_and_decals_persist(make):
    g=start(make,1);calm(g);d0=g.T('t.vfx.decals.length')
    g.T('(()=>{const e=t.enemies[0];e.dorm=false;e.s.position.set(t.P.x,e.h/2,t.P.z-5);t.hit(e,9999,e.s.position.clone().setY(1));return 1})()')
    assert g.T('t.ipAlive()')>=10;g.wait(1500);assert g.T('t.vfx.decals.length')>d0
    g.until('t.ipAlive()==0',timeout=8000);assert g.T('t.vfx.decals.length')>d0

def test_bullet_impacts_and_brass(make):
    g=start(make,1);calm(g);g.T('(t.P.w=0,t.P.pitch=-.6,1)');g.wait(200)
    g.T('t.shoot()');assert g.T('t.ipAlive()')>0,'no dirt puff on ground hit';assert g.T('t.vfx.shells.length')==1
    g.wait(900);assert g.T('t.vfx.shells.length')==0
    g.T('(t.P.w=2,1)');g.T('t.shoot()');assert g.T('t.vfx.shells.length')==0,'flamethrower must not eject brass'

def test_muzzle_flash_light(make):
    g=start(make,1);calm(g);g.wait(300);g.T('(t.P.w=0,1)');g.T('t.shoot()')
    assert g.T('t.vfx.lights.some(l=>l.intensity>0)');g.wait(200);assert g.T('t.vfx.lights.every(l=>l.intensity==0)')

def test_damage_arrows(make):
    g=start(make,1);calm(g);g.T('(t.P.yaw=0,1)')
    g.T('(t.dmgArrow(t.P.x+10,t.P.z),1)');a=g.T('t.vfx.arrows[0].a');assert abs(a-1.5708)<0.05,a
    g.T('(t.dmgArrow(t.P.x,t.P.z+10),1)');assert abs(abs(g.T('t.vfx.arrows[1].a'))-3.1416)<0.05
    g.wait(1500);assert g.T('t.vfx.arrows.length')==0

def test_enemy_hit_creates_arrow(make):
    g=start(make,1);g.T('t.god()')
    g.T('(()=>{t.enemies.forEach((e,i)=>{if(i)e.s.position.x+=150});const e=t.enemies[0];e.dorm=false;e.seen=true;e.cd=0;e.s.position.set(t.P.x-6,e.h/2,t.P.z);t.allies.forEach(a=>a.s.position.x+=200);return 1})()')
    g.until('t.vfx.arrows.length>0',timeout=6000)

@pytest.mark.parametrize('mode',['high','dither','low'])
def test_modes_render_without_errors(make,mode):
    g=start(make,3,storage={'h937_gfx':mode});calm(g);g.T('(t.boom(t.P.x,t.P.z-6),1)');g.wait(700)
    assert g.T('t.vfx.mode')==mode and g.errors==[]
