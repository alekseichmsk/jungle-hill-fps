import pytest
from conftest import start
SETUP='''(()=>{const t=__test,v=__v51;t.god();t.freeze();t.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true});t.allies.forEach(a=>a.s.position.x+=200);
 const e=t.enemies.find(e=>e.type=='rifle'||e.type=='amb');e.s.position.set(t.P.x,e.h/2,t.P.z-DIST);e.dorm=true;e.cd=1e9;window.__E=e;t.P.yaw=0;return e.hp})()'''
AIM='''(frac=>{const t=__test,v=__v51,e=__E;e.s.position.x=t.P.x;e.s.position.z=t.P.z-5;t.P.yaw=0;v.cam.updateMatrixWorld();const cy=v.cam.position.y,ty=e.s.position.y-e.s.scale.y/2+e.s.scale.y*frac;t.P.pitch=Math.atan2(ty-cy,Math.abs(e.s.position.z-v.cam.position.z));return 1})'''
def prep(make,dist=5,m=1):
    g=start(make,m);g.T('(t.P.w=3,1)');hp=g.js('()=>'+SETUP.replace('DIST',str(dist)));g.wait(300);return g,hp
def shots_to_kill(g,frac):
    n=0
    while g.js('()=>__E.alive') and n<20:
        g.js('()=>{'+'('+AIM+')('+str(frac)+');__v51.setADS(true);__v51.bloom=0;return 1}');g.wait(80);g.T('(t.shoot(),1)');n+=1;g.wait(60)
    return n
def test_headshot_vs_body(make):
    g,hp=prep(make);assert hp==30
    nh=shots_to_kill(g,.9);assert nh==2,nh
    assert g.js('()=>document.getElementById("skull").style.display')=='flex' and g.js('()=>__v51.HS.burst>=1')
    assert g.js('()=>__E.headless')
    g2,_=prep(make);nb=shots_to_kill(g2,.5);assert 4<=nb<=6,nb
def test_falloff(make):
    g=start(make,1)
    for w in range(5):
        if w==2:continue
        assert g.js(f'()=>__v51.dmgCalc({w},3,false)>=__v51.dmgCalc({w},35,false)')
    sg=g.js('()=>__v51.dmgCalc(1,30,false)/__v51.dmgCalc(1,3,false)');pi=g.js('()=>__v51.dmgCalc(3,30,false)/__v51.dmgCalc(3,3,false)');ri=g.js('()=>__v51.dmgCalc(0,30,false)/__v51.dmgCalc(0,3,false)')
    assert sg<pi<ri<=1
def test_hip_spread_greater_than_ads(make):
    g=start(make,1);g.T('(t.P.w=0,1)')
    hip=g.js('()=>{__v51.setADS(false);__v51.bloom=1;return __v51.curSpread()}');ads=g.js('()=>{__v51.setADS(true);return __v51.curSpread()}');assert hip>ads*3
def test_rmb_ads(make):
    g=start(make,1);g.T('(t.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true}),1)')
    a=g.T('t.W[t.P.w].ammo');g.page.mouse.move(700,300);g.page.mouse.down(button='right');g.wait(400)
    assert g.js('()=>__test.P.ads') and g.js('()=>__v51.cam.fov')<65 and g.T('t.W[t.P.w].ammo')==a
    g.page.mouse.up(button='right');g.wait(400);assert not g.js('()=>__test.P.ads')
def test_boss_bar(make):
    g=start(make,5);g.T('(t.god(),t.freeze(),1)')
    g.js('()=>{const b=__test.enemies.find(e=>e.type=="boss");__test.teleport(b.s.position.x,b.s.position.z+10);__test.lookAt(b.s.position.x,b.s.position.z);return 1}');g.wait(600)
    assert g.page.is_visible('#bossbar') and 'ПОЛКОВНИК ТРАН' in g.page.inner_text('#bossbar')
    w0=g.js('()=>parseFloat(document.querySelector("#bossbar .bf").style.width)')
    g.js('()=>{const b=__test.enemies.find(e=>e.type=="boss");__test.hit(b,60,b.s.position.clone());return 1}');g.wait(50)
    assert g.js('()=>document.getElementById("bossbar").classList.contains("hit")');g.wait(300)
    assert g.js('()=>parseFloat(document.querySelector("#bossbar .bf").style.width)')<w0
    g.T('(t.killAll("boss"),1)');g.wait(300);assert not g.page.is_visible('#bossbar')
def test_menu_pauses_and_settings_persist(make):
    g=start(make,1);g.page.click('#menuB');assert g.T('t.paused') and g.page.is_visible('#pause')
    g.page.click('#pSet');assert g.page.is_visible('#setP')
    for b in ['#sShake','#sBlood','#sCs','#sSfx']:g.page.click(b)
    g.page.click('#sSens');assert g.page.is_visible('#gtog') and g.page.is_visible('#mtog') and g.page.is_visible('#vtog')
    s=g.js('()=>JSON.parse(localStorage.h937_set)');assert s['shake']==0 and s['blood']==0 and s['cs']==0 and s['sfx']==0 and s['sens']==1.25
    g.page.reload();g.page.wait_for_function('()=>window.__test&&__test.MC');assert g.js('()=>SET.blood')==0 and g.js('()=>SET.sens')==1.25
def test_cutscene_plays_and_skips(make):
    g=make('?m=1&cs=1&test=1');g.page.wait_for_function('window.__cs=="intro"')
    assert g.page.is_visible('#cs');i0=g.js('()=>__v51.CSR.i');g.page.mouse.click(640,360);g.wait(400);g.page.mouse.click(640,360);g.wait(300)
    assert g.js('()=>__v51.CSR.i')>i0;assert g.page.inner_text('#cs .cssub')!=''
    g.page.click('#csSkip');g.wait(300);assert not g.page.is_visible('#cs') and g.page.is_visible('#ov')
@pytest.mark.parametrize('cs',['intro','pre_2','pre_3','pre_4','pre_5','pre_6','pre_7','pre_8','ending'])
def test_cutscene_lines_exist(make,cs):
    g=make('?test=1');import urllib.request
    from conftest import BASE
    ids=g.js(f'()=>__v51.CS["{cs}"].map(s=>s.v)')
    for i in ids:
        r=urllib.request.urlopen(BASE+f'audio/voice/{i}.mp3');assert r.status==200 and len(r.read())>3000,i
def test_flare_night(make):
    g=start(make,4);g.T('(t.god(),t.freeze(),1)');g.wait(200)
    g.js('()=>{__v51.FLR.next=0;return 1}');g.page.wait_for_function('__v51.FLR.on',timeout=8000)
    i1=g.js('()=>__v51.FLR.light.intensity');g.wait(1200);i2=g.js('()=>__v51.FLR.light.intensity')
    assert i2>i1 and i2>200 and g.js('()=>__test.MC.night')
def test_intensity_rises_and_decays(make):
    g=start(make,1);assert g.js('()=>__v51.INT.lvl')==1
    g.js('()=>{for(let i=0;i<3;i++)__v51.onKill(false);return 1}');assert g.js('()=>__v51.INT.lvl')==2
    g.js('()=>{for(let i=0;i<3;i++)__v51.onKill(true);return 1}');assert g.js('()=>__v51.INT.lvl')==3
    g.js('()=>{__v51.INT.last-=9;return 1}');g.wait(200);assert g.js('()=>__v51.INT.lvl')==1
