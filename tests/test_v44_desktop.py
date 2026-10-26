from conftest import start
def test_keys_switch_weapons(make):
    g=start(make,5);al=g.T('t.ALLOW')
    for n in range(1,min(4,len(al))+1):
        g.page.keyboard.press(str(n));g.wait(60);assert g.T('t.P.w')==al[n-1]
    g.page.keyboard.press('q');g.wait(60);assert g.T('t.P.w') in al
def test_mouse_fires(make):
    g=start(make,1);g.T('(t.god(),t.enemies.forEach(e=>{e.s.position.x+=150;e.dorm=true}),1)')
    for b in ('left',):
        a=g.T('t.W[t.P.w].ammo');g.page.mouse.move(700,300);g.page.mouse.down(button=b);g.wait(500);g.page.mouse.up(button=b);g.wait(50)
        assert g.T('t.W[t.P.w].ammo')<a and not g.T('t.firing')
def test_esc_pause_freezes(make):
    g=start(make,1);g.page.keyboard.press('Escape');g.wait(100)
    assert g.T('t.paused') and g.page.is_visible('#pause')
    t0=g.T('t.time');g.wait(700);assert g.T('t.time')==t0
    g.page.keyboard.press('Escape');g.wait(100);assert not g.T('t.paused')
    g.page.keyboard.press('p');g.wait(100);assert g.T('t.paused');g.page.click('#pRes');assert not g.T('t.paused')
def test_contextmenu_prevented(make):
    g=start(make,1);assert g.js('()=>!document.dispatchEvent(new MouseEvent("contextmenu",{bubbles:true,cancelable:true}))')
def test_touch_buttons_hidden_on_desktop(make):
    g=start(make,1);assert not g.page.is_visible('#fire') and not g.page.is_visible('#joy')
