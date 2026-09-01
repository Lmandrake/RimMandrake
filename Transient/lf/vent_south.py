import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'defName': 'AncientHeatVent', 'limit': 20})
    vents = sorted(((t['x'], t['z']) for t in r.get('things', [])), key=lambda c: c[1])
    # filter out stale rows with the independent channel
    real = []
    for (x, z) in vents:
        ci = rb.call('rimworld/get_cell_info', {'x': x, 'z': z})
        defs = str(ci.get('solidThingDefs')) + str(ci.get('things'))
        if 'AncientHeatVent' in defs: real.append((x, z))
    print('vents listed:', vents, '| confirmed real:', real)
    if real:
        x, z = real[0]
        r = rb.call('jawa/destroy_batch', {'rects': f'{x-3},{z-3},7,7', 'categories': 'Building'})
        print('destroyed at', (x, z), '->', r.get('message'))
        ci = rb.call('rimworld/get_cell_info', {'x': x, 'z': z})
        print('cell after:', ci.get('solidThingDefs') or 'empty')
        rb.call('jawa/map_commit', {'redraw': True})
