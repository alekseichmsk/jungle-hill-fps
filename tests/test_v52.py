from conftest import start
def test_pain_escalates(make):
    g=start(make,1);g.T('(t.freeze(),1)')
    idx=[]
    for k in range(5):
        g.js('()=>{__v52.PAIN.say=-99;__v52.painHit();return 1}');idx.append(g.js('()=>__v52.PAIN.i'))
    assert idx==[0,1,2,3,4]
    assert g.T('t.vcur') in ('pain_5_x','pain_5')
    g.js('()=>{__v52.PAIN.last-=10;__v52.painHit();return 1}');assert g.js('()=>__v52.PAIN.i')==0
def test_clean_lines_when_18_off(make):
    g=start(make,1,storage={'h937_set':'{"adult":0}'});g.js('()=>{__v52.PAIN.say=-99;__v52.painHit();return 1}');assert g.T('t.vcur')=='pain_1'
def test_medic_once_and_heal(make):
    g=start(make,1);g.T('(t.freeze(),t.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true}),1)')
    g.T('(t.P.hp=8,1)');g.wait(300)
    assert g.js('()=>__v52.MED.used&&__v52.MED.active') and g.js('()=>__v52.lowVis')
    g.page.wait_for_function('__test.P.hp==100',timeout=12000);assert not g.js('()=>__v52.MED.active')
    g.T('(t.P.hp=8,1)');g.wait(2500);assert g.T('t.P.hp')==8 and g.js('()=>__v52.lowVis') and not g.js('()=>__v52.MED.active')
def test_gore18_and_setting(make):
    g=start(make,1);g.T('(t.freeze(),1)');g0=g.js('()=>__v52.gore')
    g.T('(t.P.w=1,t.killAll("rifle"),1)');assert g.js('()=>__v52.gore')>g0
    g.page.click('#menuB');g.page.click('#pSet');g.page.click('#sAdult');assert g.js('()=>JSON.parse(localStorage.h937_set).adult')==0
def test_agegate(make):
    g=make('?agegate=1');assert g.page.is_visible('#agegate');g.page.click('#agClean');assert not g.page.is_visible('#agegate') and g.js('()=>SET.adult')==0 and g.js('()=>localStorage.h937_age')=='1'
