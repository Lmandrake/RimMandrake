import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

X0, X1, Z0, Z1 = 110, 145, 132, 165
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'rect': f'{X0},{Z0},{X1-X0+1},{Z1-Z0+1}', 'limit': 3000})
    things = r.get('things', [])
    print('matched', r.get('countMatched'), 'returned', r.get('countReturned'))
    grid = {}
    others = set()
    for t in things:
        d, x, z = t['def'], t['x'], t['z']
        if 'Conduit' in d or 'Pipe' in d: continue
        if d == 'GravshipHull': c = '#'
        elif d == 'Door': c = 'D'
        elif 'Bed' in d.lower(): c = 'b'
        else:
            c = '?'; others.add((d,x,z))
        p = grid.get((x,z))
        if p is None or c in '#D': grid[(x,z)] = c
    for o in sorted(others): print('other:', o)
    fr = rb.call('jawa/get_terrain_layers', {'rect': f'{X0},{Z0},{X1-X0+1},{Z1-Z0+1}', 'limit': 2000})
    cells = fr.get('cells') or fr.get('rows') or []
    if not cells:
        import json; print('layers keys:', list(fr.keys()), json.dumps(fr, default=str)[:500])
    sub, top = {}, {}
    for c in cells:
        x, z = c.get('x'), c.get('z')
        sub[(x,z)] = c.get('foundation')
        top[(x,z)] = c.get('top')
    for z in range(Z1, Z0-1, -1):
        row = ''
        for x in range(X0, X1+1):
            ch = grid.get((x,z))
            if ch is None:
                ch = '.' if sub.get((x,z)) else (',' if top.get((x,z)) and 'Soil' not in str(top.get((x,z))) and 'Sand' not in str(top.get((x,z))) else ' ')
            row += ch
        print(f'{z:3d} {row}')
    print('    ' + ''.join(str(x%10) for x in range(X0, X1+1)))
    from collections import Counter
    print('top terrains:', Counter(top.values()).most_common(8))
