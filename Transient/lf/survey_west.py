import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

X0, X1, Z0, Z1 = 55, 115, 120, 200
sub, top, walls = {}, {}, set()
with RimBridge(host, port, token) as rb:
    # chunked layer read (stay under caps)
    for z in range(Z0, Z1+1, 10):
        h = min(10, Z1+1-z)
        fr = rb.call('jawa/get_terrain_layers', {'rect': f'{X0},{z},{X1-X0+1},{h}', 'limit': 5000})
        cells = fr.get('cells', [])
        if fr.get('truncated'): print('TRUNCATED at z', z, len(cells))
        for c in cells:
            sub[(c['x'], c['z'])] = c.get('foundation')
            top[(c['x'], c['z'])] = c.get('top')
    r = rb.call('jawa/list_things', {'defName': 'GravshipHull', 'rect': f'{X0},{Z0},{X1-X0+1},{Z1-Z0+1}', 'limit': 3000})
    print('hull matched', r.get('countMatched'), 'returned', r.get('countReturned'))
    for t in r.get('things', []):
        walls.add((t['x'], t['z']))

import pickle
pickle.dump({'sub': sub, 'top': top, 'walls': walls, 'box': (X0,X1,Z0,Z1)}, open(r'D:\Luke\dev\Rimworld\Transient\lf\west.pkl','wb'))
print('cells read:', len(sub))
# ASCII: # wall, X = XGrate floor, S = substructure w/ other floor, ' ' = nothing
for z in range(Z1, Z0-1, -1):
    row = ''
    for x in range(X0, X1+1):
        if (x,z) in walls: ch='#'
        elif 'XGrate' in str(top.get((x,z))): ch='X'
        elif sub.get((x,z)): ch='.'
        else: ch=' '
        row += ch
    print(f'{z:3d} {row}')
print('    ' + ''.join(str(x%10) for x in range(X0, X1+1)))
