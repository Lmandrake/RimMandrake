import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
# index 22156, W=250 -> z=88, x=156
X0, X1, Z0, Z1 = 138, 175, 75, 125
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'rect': f'{X0},{Z0},{X1-X0+1},{Z1-Z0+1}', 'limit': 3000})
    grid, other = {}, []
    for t in r.get('things', []):
        d, x, z = t['def'], t['x'], t['z']
        c = {'GravshipHull':'#','Door':'D','HiddenConduit':None,'VGE_AstrofuelPipe':None,'PowerConduit':None}.get(d, '?')
        if c == '?': other.append((d,x,z))
        if c and (grid.get((x,z)) is None): grid[(x,z)] = c
    for o in other[:15]: print('other:', o)
    sub, top = {}, {}
    for z in range(Z0, Z1+1, 10):
        h = min(10, Z1+1-z)
        fr = rb.call('jawa/get_terrain_layers', {'rect': f'{X0},{z},{X1-X0+1},{h}', 'limit': 5000})
        for c in fr.get('cells', []):
            sub[(c['x'],c['z'])] = c.get('foundation'); top[(c['x'],c['z'])] = c.get('top')
    for z in range(Z1, Z0-1, -1):
        row = ''
        for x in range(X0, X1+1):
            ch = grid.get((x,z))
            if ch is None:
                t = str(top.get((x,z)))
                if 'XGrate' in t: ch='X'
                elif sub.get((x,z)): ch='.'
                else: ch=' '
            row += ch
        print(f'{z:3d} {row}')
    print('    ' + ''.join(str(x%10) for x in range(X0, X1+1)))
    from collections import Counter
    print('tops:', Counter(str(v) for v in top.values()).most_common(6))
