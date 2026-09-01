import sys, pickle, random
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
random.seed(41)
wrecks = {'AncientHeatVent': (111,158), 'AncientJetEngine': (138,150), 'AncientExcavator': (150,150),
          'AncientChemtruck': (143,161), 'AncientAPC': (119,167)}
ops = []
for (cx, cz) in wrecks.values():
    cells = random.sample([(cx+dx, cz+dz) for dx in range(-4,5) for dz in range(-4,5) if 2 < abs(dx)+abs(dz) <= 5], 7)
    for i, (x, z) in enumerate(cells):
        ops.append(f'{"ChunkSlagSteel" if i < 2 else "Filth_RubbleBuilding"}:{x},{z}')
lineup = pickle.load(open(r'D:\Luke\dev\Rimworld\Transient\lf\lineup.pkl', 'rb'))
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/spawn_batch', {'ops': ';'.join(ops)})
    print('scatter:', r.get('success'), r.get('message'))
    rects = ';'.join(f'{x},{z},1,1' for (x, z) in lineup.values())
    r = rb.call('jawa/destroy_batch', {'rects': rects, 'categories': 'Building,Item'})
    print('lineup cleanup:', r.get('success'), r.get('message'))
    r = rb.call('jawa/list_things', {'rect': '30,24,72,34', 'limit': 60})
    left = [t['def'] for t in r.get('things', []) if t['def'].startswith(('Ancient', 'Chunk'))]
    print('test area leftovers:', left or 'none')
    rb.call('jawa/map_commit', {'redraw': True})
    rb.call('jawa/clear_ui', {})
    rb.call('rimworld/frame_cell_rect', {'x': 100, 'z': 140, 'width': 75, 'height': 60})
    s = rb.call('rimworld/take_screenshot', {})
    print('final shot:', s.get('path'))
