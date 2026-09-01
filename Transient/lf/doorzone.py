import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'defName': 'GravshipHull,Door', 'rect': '118,138,20,12', 'limit': 500})
    walls = sorted((t['z'], t['x'], t['def']) for t in r.get('things', []))
    for z in range(149, 137, -1):
        row = [(x, d) for (zz, x, d) in walls if zz == z]
        print(z, ' '.join(f"{x}{'D' if d=='Door' else ''}" for x, d in sorted(row)))
    fr = rb.call('jawa/get_terrain_layers', {'rect': '118,138,20,12', 'limit': 400})
    cells = fr.get('cells') or fr.get('rows') or []
    print('cell keys:', list(cells[0].keys()) if cells else 'NONE', len(cells))
    subs = {}
    for c in cells:
        subs[(c.get('x'), c.get('z'))] = (c.get('foundation'), c.get('top'), c.get('under'))
    for z in range(149, 137, -1):
        line = ''
        for x in range(118, 138):
            f, t, u = subs.get((x, z), (None, None, None))
            line += ('S' if f else ('t' if (t and 'Soil' not in str(t) and 'Sand' not in str(t) and 'Grass' not in str(t)) else '.'))
        print(z, line)
    print('   ', ''.join(str(x % 10) for x in range(118, 138)))
    # what is the top/under exactly on the door cell and around it
    for (x, z) in [(127,143),(127,144),(127,145),(126,144),(128,144),(126,145),(128,145)]:
        print((x,z), subs.get((x,z)))
