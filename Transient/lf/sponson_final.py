import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/build_batch', {'ops': 'Fence:151,86;Fence:151,90', 'stuff': 'Steel', 'faction': 'PlayerColony'})
    print('gap fences:', r.get('placed'), r.get('failed'))
    r = rb.call('jawa/map_commit', {'redraw': True})
    # final state map
    r = rb.call('jawa/list_things', {'rect': '138,78,30,22', 'limit': 2000})
    grid = {}
    for t in r.get('things', []):
        c = (t['x'], t['z'])
        ch = {'GravshipHull': '#', 'Fence': 'f', 'HiddenConduit': None, 'VGE_AstrofuelPipe': 'P'}.get(t['def'], None)
        if ch and grid.get(c) != '#': grid[c] = ch
    fr1 = rb.call('jawa/get_terrain_layers', {'rect': '138,78,30,10', 'limit': 5000})
    fr2 = rb.call('jawa/get_terrain_layers', {'rect': '138,88,30,10', 'limit': 5000})
    sub, top = {}, {}
    for fr in (fr1, fr2):
        for c in fr.get('cells', []):
            sub[(c['x'], c['z'])] = c.get('foundation'); top[(c['x'], c['z'])] = str(c.get('top'))
    for z in range(96, 79, -1):
        row = ''
        for x in range(138, 168):
            ch = grid.get((x, z))
            if ch is None:
                t = top.get((x, z), '')
                if 'XGrate' in t: ch = 'X'
                elif sub.get((x, z)): ch = '.'
                else: ch = ' '
            row += ch
        print(f'{z:3d} {row}')
    print('    ' + ''.join(str(x % 10) for x in range(138, 168)))
    rb.call('jawa/clear_ui', {})
    rb.call('rimworld/jump_camera_to_cell', {'x': 152, 'z': 88})
    s = rb.call('rimworld/take_screenshot', {})
    print('shot:', s.get('path'))
