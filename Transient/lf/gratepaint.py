import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
ops = open(r'D:\Luke\dev\Rimworld\Transient\lf\grate_ops.txt').read()
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/set_terrain_batch', {'ops': ops})
    print('paint:', r.get('success'), r.get('message'))
    r = rb.call('jawa/map_commit', {'redraw': True})
    print('commit:', r.get('success'))
    # read back
    fr = rb.call('jawa/get_terrain_layers', {'rect': '95,127,4,12', 'limit': 100})
    got = {(c['x'],c['z']): c.get('top') for c in fr.get('cells', [])}
    want = [tuple(map(int, o.split(':')[1].split(',')[:2])) for o in ops.split(';')]
    bad = [(c, got.get(c)) for c in want if 'XGrate' not in str(got.get(c))]
    print('read-back wrong:', bad if bad else 'NONE - all 23 are XGrate_iron')
    rb.call('jawa/clear_ui', {})
    rb.call('rimworld/jump_camera_to_cell', {'x': 93, 'z': 135})
    s = rb.call('rimworld/take_screenshot', {})
    print('shot:', s.get('path'))
