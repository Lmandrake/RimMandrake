import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def cell_defs(rb, x, z):
    r = rb.call('rimworld/get_cell_info', {'x': x, 'z': z})
    return [t.get('defName') for t in (r.get('cell') or {}).get('things', [])]
with RimBridge(host, port, token) as rb:
    for (x, z), why in [((168, 64), 'southern-most ship vent'), ((76, 48), 'my desert test leftover')]:
        before = cell_defs(rb, x, z)
        r = rb.call('jawa/destroy_batch', {'rects': f'{x-3},{z-3},7,7', 'categories': 'Building'})
        after = cell_defs(rb, x, z)
        print(f'({x},{z}) {why}: before={before} -> after={after or "empty"}')
    rb.call('jawa/map_commit', {'redraw': True})
    # confirm survivors
    r = rb.call('jawa/list_things', {'defName': 'AncientHeatVent', 'limit': 10})
    locs = [(t['x'], t['z']) for t in r.get('things', [])]
    print('vents remaining (verify each):', [(c, cell_defs(rb, *c)) for c in locs])
