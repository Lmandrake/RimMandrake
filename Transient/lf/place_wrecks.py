import sys, pickle
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
sp = pickle.load(open(r'D:\Luke\dev\Rimworld\Transient\lf\spots.pkl', 'rb'))
g5 = set(sp['grass5'])
def pick(cands, taken, min_d):
    for c in cands:
        if all((c[0]-t[0])**2 + (c[1]-t[1])**2 >= min_d*min_d for t in taken): return c
    return None
taken = []
plan = {}
# vent needs extra margin: require all 4-neighborhood corners also in grass5
vent_c = [c for c in sp['grass5'] if all((c[0]+dx, c[1]+dz) in g5 for dx in (-2, 2) for dz in (-2, 2))]
for name, cands, d in [('AncientHeatVent', vent_c, 0), ('AncientJetEngine', sp['grass5'], 12),
                       ('AncientExcavator', sp['grass5'], 12), ('AncientChemtruck', sp['grass5'], 12),
                       ('AncientAPC', sp['grass5'], 12)]:
    c = pick(cands if d else cands[len(cands)//2:], taken, d or 14)
    plan[name] = c; taken.append(c)
deck = [('AncientLargeRustedEngineBlock', (162, 145)), ('AncientGenerator', (161, 171)),
        ('AncientPallet_SteelSlag', (116, 184)), ('AncientFuelNode', (122, 185)),
        ('ChunkSlagSteel', (125, 185)), ('ChunkSlagSteel', (158, 172)), ('ChunkSlagSteel', (160, 172))]
ops = [f'{d}:{x},{z}' for d, (x, z) in plan.items()] + [f'{d}:{x},{z}' for d, (x, z) in deck]
print('plan:', plan)
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/spawn_batch', {'ops': ';'.join(ops)})
    print('spawn:', r.get('success'), r.get('message'))
    rb.call('jawa/map_commit', {'redraw': True})
    rb.call('jawa/clear_ui', {})
    rb.call('rimworld/frame_cell_rect', {'x': 105, 'z': 148, 'width': 60, 'height': 50})
    s1 = rb.call('rimworld/take_screenshot', {})
    print('courtyard shot:', s1.get('path'))
