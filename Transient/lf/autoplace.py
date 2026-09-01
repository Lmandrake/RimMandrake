import sys, pickle
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
X0, X1, Z0, Z1 = 85, 170, 120, 200
occ, sub, top = set(), {}, {}
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'rect': f'{X0},{Z0},{X1-X0+1},{Z1-Z0+1}', 'limit': 6000, 'includePawns': True})
    print('things:', r.get('countMatched'))
    for t in r.get('things', []):
        if t['def'] in ('HiddenConduit', 'PowerConduit', 'VGE_AstrofuelPipe'): continue
        occ.add((t['x'], t['z']))          # anchor; pad later for multicell
    for z in range(Z0, Z1+1, 10):
        h = min(10, Z1+1-z)
        fr = rb.call('jawa/get_terrain_layers', {'rect': f'{X0},{z},{X1-X0+1},{h}', 'limit': 5000})
        for c in fr.get('cells', []):
            sub[(c['x'], c['z'])] = bool(c.get('foundation')); top[(c['x'], c['z'])] = str(c.get('top'))
    pad_occ = {(x+dx, z+dz) for (x, z) in occ for dx in (-2,-1,0,1,2) for dz in (-2,-1,0,1,2)}
    def clear_patch(cx, cz, r_, need_deck):
        for x in range(cx-r_, cx+r_+1):
            for z in range(cz-r_, cz+r_+1):
                if (x, z) in pad_occ: return False
                if need_deck and not sub.get((x, z)): return False
                if not need_deck and (sub.get((x, z)) or 'Grassland' not in top.get((x, z), '')): return False
        return True
    def find(r_, need_deck, region):
        out = []
        for (xa, xb, za, zb) in [region]:
            for z in range(za, zb):
                for x in range(xa, xb):
                    if clear_patch(x, z, r_, need_deck): out.append((x, z))
        return out
    deck7 = find(3, True, (90, 168, 125, 198))
    deck3 = find(1, True, (90, 168, 125, 198))
    grass5 = find(2, False, (108, 158, 150, 195))
    print('7x7 deck spots:', len(deck7), deck7[:8])
    print('3x3 deck spots:', len(deck3), deck3[:12])
    print('5x5 courtyard grass spots:', len(grass5), grass5[:8])
    pickle.dump({'deck7': deck7, 'deck3': deck3, 'grass5': grass5}, open(r'D:\Luke\dev\Rimworld\Transient\lf\spots.pkl', 'wb'))
