import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'defName': 'GravshipHull,Door', 'rect': '122,142,12,6', 'limit': 100})
    rows = {}
    for t in r.get('things', []):
        rows.setdefault(t['z'], []).append((t['x'], 'D' if t['def']=='Door' else '#', t.get('stuff')))
    for z in sorted(rows, reverse=True):
        print(z, sorted(rows[z]))
    fr = rb.call('jawa/get_terrain_layers', {'rect': '124,143,7,3', 'limit': 100})
    for c in fr.get('cells', []):
        if c['z'] in (144, 145):
            print(c['x'], c['z'], 'top', c.get('top'), 'fnd', c.get('foundation'))
    rb.call('jawa/clear_ui', {})
    r = rb.call('rimworld/jump_camera_to_cell', {'x': 127, 'z': 148})
    s = rb.call('rimworld/take_screenshot', {})
    print('shot:', s.get('path') or s)
