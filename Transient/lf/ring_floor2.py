import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    sub, top = {}, {}
    for z0 in (75, 85, 95):
        fr = rb.call('jawa/get_terrain_layers', {'rect': f'138,{z0},38,10', 'limit': 5000})
        for c in fr.get('cells', []):
            sub[(c['x'], c['z'])] = c.get('foundation'); top[(c['x'], c['z'])] = str(c.get('top'))
    FLOORS = ('AG_RustedTile', 'XGrate', 'Doomgiver', 'UCScaffoldTile', 'MetalTile')
    keep_void = {(153, 91), (154, 91), (153, 90)}
    # 1. circular region = substructured cells x>=151 in the ring zone -> all XGrate
    circle = [c for c in sub if c[0] >= 151 and 79 <= c[1] <= 97 and sub[c] and c not in keep_void]
    ops = [f'guy762_FloorTiles_XGrate_iron:{x},{z},1,1' for (x, z) in sorted(circle) if 'XGrate' not in top.get((x, z), '')]
    print('circle cells:', len(circle), '| to grate:', len(ops))
    if ops:
        r = rb.call('jawa/set_terrain_batch', {'ops': ';'.join(ops)})
        print('grate:', r.get('success'), r.get('message'))
    # 2. floors with NO substructure in region -> strip back to natural
    orphans = sorted(c for c, t in top.items() if not sub.get(c) and any(f in t for f in FLOORS))
    print('orphan floor cells:', len(orphans), orphans[:12])
    for (x, z) in orphans:
        r = rb.call('jawa/set_terrain_layer', {'layer': 'removeTop', 'rect': f'{x},{z},1,1'})
        if not r.get('success'): print('  strip FAILED', (x, z), r.get('message'))
    r = rb.call('jawa/map_commit', {'redraw': True})
    print('commit:', r.get('success'))
    # verify
    fr = rb.call('jawa/get_terrain_layers', {'rect': '150,79,26,19', 'limit': 5000})
    bad = [(c['x'], c['z'], c.get('top')) for c in fr.get('cells', [])
           if c.get('foundation') and 'XGrate' not in str(c.get('top')) and (c['x'], c['z']) not in keep_void and c['x'] >= 151]
    print('circle cells not grate after pass:', len(bad), bad[:8])
