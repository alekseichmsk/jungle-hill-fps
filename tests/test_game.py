import os,pytest,urllib.request,re
from conftest import BASE,VPS,start
ALLOW={1:[0,3],2:[0,1,3,4],3:[0,1,2,3,4],4:[0,1,2,3,4],5:[0,1,2,3,4],6:[0,1,2,3,4],7:[0,1,2,3,4],8:[0,1,2,3,4]}
TITLES={1:'ТРОПА',2:'ПЕРЕПРАВА',3:'ДЕРЕВНЯ',4:'НОЧЬ',5:'ВЫСОТА 937',6:'ХРЕБЕТ',7:'ЗОНА ВЫСАДКИ',8:'ДЕРЕВНЯ НА СВАЯХ'}
VOICE=['brief_m1','brief_m2','brief_m3','brief_m4','brief_m5','hank_start_m1','hank_start_m2','hank_start_m3','hank_start_m4','hank_start_m5','hq_start','obj_done_1','obj_done_2','obj_done_3','marty_found','mg_down','boss_down','hurt','squad_down','win','win_m5','fail','brief_m6','brief_m7','brief_m8','hank_start_m6','hank_start_m7','hank_start_m8','win_m8']
SPRITES=['m1_rifleman','m1_rifleman_aim','m1_death','mg_nest','river','m60_idle','m60_fire','enemy','palm','corpse']

def test_version_string():
    html=urllib.request.urlopen(BASE+'index.html?nc=1').read().decode()
    assert re.search(r'concept v\d\.\d',html),'version string missing'

@pytest.mark.parametrize('vp',list(VPS))
def test_menu_no_console_errors(make,vp):
    g=make('',VPS[vp]);g.wait(1500);assert g.errors==[]

@pytest.mark.parametrize('vp',list(VPS))
def test_menu_fits_screen(make,vp):
    g=make('',VPS[vp]);w,h=VPS[vp]
    for sel in['#logo','#start','#bMis','#bSq','#bSnd']:
        b=g.page.locator(sel).bounding_box();assert b and b['x']>=0 and b['y']>=0 and b['x']+b['width']<=w+1 and b['y']+b['height']<=h+1,(sel,b)

@pytest.mark.parametrize('vp',['desktop720','phone'])
def test_missions_screen(make,vp):
    g=make('',VPS[vp],{'h937_unlocked':'3'});g.page.click('#bMis');cards=g.page.locator('#panel .card')
    assert cards.count()==8;assert g.page.locator('#panel .card.lock').count()==5
    w,h=VPS[vp]
    for i in range(5):
        b=cards.nth(i).bounding_box();assert b['x']>=0 and b['x']+b['width']<=w+1
    cards.nth(1).click();g.page.wait_for_url(re.compile(r'\?m=2'))

def test_squad_screen(make):
    g=make();g.page.click('#bSq');assert g.page.locator('#panel > *').count()>=8;assert 'ХЭНК' in g.page.inner_text('#panel')

@pytest.mark.parametrize('m',[1,2,3,4,5,6,7,8])
def test_mission_briefing_and_objectives(make,m):
    g=make(f'?m={m}&test=1');g.until('t.MC!=null')
    assert g.page.is_visible('#ov');assert TITLES[m] in g.page.inner_text('#ovb h1')
    n=g.T('t.MC.obj.length');assert g.page.locator('#ovb li').count()==n
    g.page.click('#ovGo');g.until('t.started');assert not g.page.is_visible('#ov')
    g.wait(500);assert g.page.is_visible('#obj');assert TITLES[m] in g.page.inner_text('#obj').upper()
    assert g.errors==[]

@pytest.mark.parametrize('m',[1,2,3,4,5,6,7,8])
def test_playthrough_win_and_unlock(make,m):
    g=start(make,m);g.T('t.god()')
    for _ in range(12):
        if g.T('t.over'):break
        g.T('t.completeCurrent()');g.wait(500)
    assert g.T('t.over') and g.T('t.oi')==g.T('t.MC.obj.length')
    h1=g.page.inner_text('#ovb h1');assert h1==({5:'ВЫСОТА ВЗЯТА!',8:'КАМПАНИЯ ЗАВЕРШЕНА'}.get(m,'МИССИЯ ВЫПОЛНЕНА')),h1
    assert int(g.js('localStorage.h937_unlocked'))==min(8,m+1)
    if m<8:assert g.page.is_visible('#ovNext')
    assert g.errors==[]

def test_fail_screen(make):
    g=start(make,1);g.T('(t.P.hp=0,1)');g.until('t.over');assert g.page.inner_text('#ovb h1')=='ТЫ ПОГИБ'
    assert g.page.is_visible('#ovRe');assert (g.js('localStorage.h937_unlocked') or '1')=='1'

@pytest.mark.parametrize('m',[1,2,3,4,5,6,7,8])
def test_weapon_switching_allowed(make,m):
    g=start(make,m);g.T('t.freeze()')
    for k in range(5):
        before=g.T('t.P.w');g.page.keyboard.press(str(k+1));g.wait(60);after=g.T('t.P.w')
        assert after==(ALLOW[m][k] if k<len(ALLOW[m]) else before),(k,before,after)
    assert g.T('t.ALLOW')==ALLOW[m]

def test_firing_reduces_ammo(make):
    g=start(make,2);g.T('t.freeze()')
    for w in [0,1,4]:
        g.T(f'(t.P.w={w},1)');a=g.T(f't.W[{w}].ammo');g.T('t.setFiring(true)');g.wait(700);g.T('t.setFiring(false)');assert g.T(f't.W[{w}].ammo')<a,w
    g.T('(t.P.w=3,1)');g.T('t.setFiring(true)');g.wait(400);g.T('t.setFiring(false)');assert g.T('t.W[3].ammo===Infinity')

def test_flamethrower_grass_and_hut(make):
    g=start(make,3);g.T('t.freeze()');g.T('t.god()')
    g.T('(t.teleport(-8,14.6),t.lookAt(-8,10),t.P.w=2,t.setFiring(true),1)');g.wait(2500);g.T('t.setFiring(false)')
    assert g.T('t.fires.length')>0
    assert g.T('t.solids.some(s=>s.kind=="hut"&&(s.burning||s.burnt))')

def test_burning_enemy_becomes_charred_corpse(make):
    g=start(make,1);g.T('t.freeze()')
    g.T('(()=>{const e=t.enemies[0];t.igniteEnemy(e);e.burn=.05;window.__e=e;return 1})()');g.wait(1000)
    assert g.js('__e.corpse===true&&__e.alive===false')

def test_shooting_burning_enemy_kills_instantly(make):
    g=start(make,1);g.T('t.freeze()')
    r=g.T('(()=>{const e=t.enemies[1];t.igniteEnemy(e);const hp=e.hp;t.hit(e,1,e.s.position.clone());return [hp,e.alive]})()')
    assert r[0]>1 and r[1]==False

def test_enemies_aim_then_fire(make):
    g=start(make,1);g.T('t.god()')
    g.T('''(()=>{t.enemies.forEach((e,i)=>{if(i)e.s.position.x+=90});const e=t.enemies[0];e.type='rifle';e.dorm=false;e.seen=false;e.cd=0;e.flash=0;window.__e=e;
      t.teleport(e.s.position.x,e.s.position.z+12);t.lookAt(e.s.position.x,e.s.position.z);t.allies.forEach(a=>a.s.position.x+=200);return 1})()''')
    g.wait(250);n0=g.T('t.shots.filter(s=>!s.userData.fr).length')
    assert g.js('__e.aiming===true'),'not aiming';assert g.js('__e.s.material.map===__e.T[4]'),'aim frame not shown';assert n0==0,'fired without aim delay'
    g.wait(1400);assert g.js('__e.cd>0'),'never fired';assert g.T('t.shots.filter(s=>!s.userData.fr).length')>0 or g.js('__e.flash!==undefined')

def test_squad_follows_and_aims(make):
    g=start(make,1);g.T('t.freeze()');g.T('t.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true})')
    g.T('t.teleport(t.P.x,t.P.z-6)');g.until('Math.max(...t.allies.map(a=>Math.hypot(a.s.position.x-t.P.x,a.s.position.z-t.P.z)))<9',timeout=10000)
    g.T('(()=>{const a=t.allies[0],e=t.enemies[0];e.dorm=false;e.s.position.set(a.s.position.x,e.h/2,a.s.position.z-8);return 1})()');g.wait(1800)
    assert g.T('t.allies[0].aim>0');assert g.T('t.shots.some(s=>s.userData.fr)') or g.T('t.allies[0].cd>0')

def test_mg_nests_destroyable(make):
    g=start(make,2);n=g.T('t.enemies.filter(e=>e.type=="mg").length');assert n==3
    g.T('t.killAll("mg")');g.wait(300)
    assert g.T('t.enemies.filter(e=>e.type=="mg").every(e=>!e.alive&&e.corpse)');assert g.T('t.oi')>=1

def test_boss_hp_and_death(make):
    g=start(make,5);g.T('t.god()');b='t.enemies.find(e=>e.type=="boss")'
    assert g.T(b+'.hp')==420;g.T(f'(t.hit({b},100,{b}.s.position.clone()),1)');assert g.T(b+'.hp')==320 and g.T(b+'.alive')
    g.T(f'(t.hit({b},9999,{b}.s.position.clone()),1)');assert not g.T(b+'.alive');g.wait(300);assert g.T('t.oi')>=1

def test_music_calm_combat_calm(make):
    g=start(make,4);g.T('t.freeze()');g.T('t.god()');g.T('t.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true})')
    g.until('t.mus&&t.mus.amb>0.5&&t.mus.act<0.3',timeout=20000)
    g.T('t.setFiring(true)');g.until('t.mus.act>0.6',timeout=6000);g.T('t.setFiring(false)')
    g.wait(4000);assert g.T('t.mus.act')>0.5,'faded too early'
    g.until('t.mus.act<0.3&&t.mus.amb>0.5',timeout=16000)

@pytest.mark.parametrize('f',VOICE)
def test_voice_file_200(f):
    r=urllib.request.urlopen(BASE+f'audio/voice/{f}.mp3');assert r.status==200 and int(r.headers.get('Content-Length') or len(r.read()))>2000

@pytest.mark.parametrize('f',SPRITES)
def test_sprite_200(f):
    assert urllib.request.urlopen(BASE+f'sprites/{f}.png').status==200

def test_subtitles_and_skip(make):
    g=start(make,1);g.wait(400)
    assert g.page.is_visible('#subs');t1=g.page.inner_text('#subs');assert 'ШТАБ' in t1 or 'ХЭНК' in t1
    assert g.page.is_visible('#vskip');id1=g.T('t.vcur');g.page.click('#vskip');g.wait(500)
    assert g.T('t.vcur')!=id1 or not g.page.is_visible('#subs')

def test_briefing_no_duplicate_subtitles(make):
    g=make('?m=1&test=1');g.until('t.MC!=null');g.wait(1200);assert not g.page.is_visible('#subs')

def test_toggles_persist(make):
    g=make('?m=1&test=1');g.until('t.MC!=null')
    g.page.click('#vtog');g.page.click('#mtog')
    assert g.js('localStorage.h937_vox')=='0' and g.js('localStorage.h937_mus')=='0'
    g.page.reload();g.page.wait_for_function('()=>window.__test&&window.__test.MC');assert 'ВЫКЛ' in g.page.inner_text('#vtog') and 'ВЫКЛ' in g.page.inner_text('#mtog')
    g.page.click('#bSnd') if g.page.is_visible('#bSnd') else None

@pytest.mark.parametrize('vp',list(VPS))
def test_weapon_never_over_crosshair(make,vp):
    g=start(make,5,VPS[vp]);g.T('t.freeze()')
    for w in range(5):
        for fire in [False,True]:
            g.T(f'(t.P.w={w},t.setFiring({str(fire).lower()}),1)');g.wait(250)
            bad=g.js('''()=>{const c=document.getElementById('gun'),r=c.getBoundingClientRect(),x=document.getElementById('cross').getBoundingClientRect();
              const cx=x.left+x.width/2,cy=x.top+x.height/2,pad=Math.max(x.width,x.height)/2+4;
              if(cx+pad<r.left||cx-pad>r.right||cy+pad<r.top||cy-pad>r.bottom)return 0;
              const g=c.getContext('2d'),sx=c.width/r.width,sy=c.height/r.height;let n=0;
              for(let yy=cy-pad;yy<=cy+pad;yy+=2)for(let xx=cx-pad;xx<=cx+pad;xx+=2){const px=Math.floor((xx-r.left)*sx),py=Math.floor((yy-r.top)*sy);if(px<0||py<0||px>=c.width||py>=c.height)continue;if(g.getImageData(px,py,1,1).data[3]>20)n++}return n}''')
            assert bad==0,(vp,w,fire,bad)
        g.T('t.setFiring(false)')
