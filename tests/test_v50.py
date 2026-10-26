import pytest,urllib.request
from conftest import start,BASE
NEW=['us_rifleman.png','rpg.png','sandbags.png','sandbags_spr.png','hatch.png','crate.png','crate_spr.png','hut_stilts.png','tex_grass.jpg','tex_trail.jpg','sky_m6.jpg','sky_m7.jpg']
@pytest.mark.parametrize('f',NEW)
def test_new_sprite_served(f):
    r=urllib.request.urlopen(BASE+'sprites/'+f);assert r.status==200 and len(r.read())>1000
def test_new_sprites_loaded_in_game(make):
    g=start(make,7)
    assert g.js('()=>{const t=__test;return t.allies.every(a=>a.s.material.map.image.width>=100)}')
    assert g.js('()=>__test.enemies.filter(e=>e.type=="rpg").every(e=>e.T[0].image.width>=100)')
@pytest.mark.parametrize('m',[6,7,8])
def test_new_mission_layout(make,m):
    g=start(make,m);assert g.T('t.enemies.length')>=6 and g.T('t.solids.length')>10 and g.errors==[]
    if m==8:assert g.T("t.solids.filter(s=>s.kind=='stilt').length")==8
    if m==7:assert g.T('t.MC.caches.length')==4
