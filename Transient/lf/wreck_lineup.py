import sys, pickle
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CANDS = ['AncientEngine','AncientJetEngine','AncientDropshipEngine','AncientLargeRustedEngineBlock',
'AncientGravEngine','AncientTunnelerHusk','AncientExcavator','AncientGiantWheel',
'AncientAPC','AncientChemtruck','AncientIndustrialTruck','AncientCraneArm',
'AncientCraneBase','AncientBarrelAndPipes','AncientFuelNode','AncientGenerator',
'AncientGeneratorSingle','AncientMilitaryGeneratorSmall','AncientHeatVent','AncientDestroyedConsoleLarge',
'AncientEquipmentBlocks','ChunkSlagSteel','AncientBox_SteelSlag','AncientPallet_SteelSlag',
'AncientExostriderRemains','AncientAntenna']
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'rect': '30,24,72,34', 'limit': 50})
    print('test area occupancy:', r.get('countMatched'))
    grid = {}
    ops = []
    for i, d in enumerate(CANDS):
        x = 36 + (i % 7) * 10
        z = 30 + (i // 7) * 9
        grid[d] = (x, z)
        ops.append(f'{d}:{x},{z}')
    r = rb.call('jawa/spawn_batch', {'ops': ';'.join(ops)})
    print('spawn:', r.get('success'), r.get('message'))
    pickle.dump(grid, open(r'D:\Luke\dev\Rimworld\Transient\lf\lineup.pkl', 'wb'))
    r = rb.call('jawa/list_things', {'rect': '30,24,72,34', 'limit': 100})
    present = {t['def'] for t in r.get('things', [])}
    missing = [d for d in CANDS if d not in present]
    print('spawned:', len(present), '| missing:', missing)
    rb.call('jawa/clear_ui', {})
    rb.call('rimworld/jump_camera_to_cell', {'x': 66, 'z': 42})
    s = rb.call('rimworld/take_screenshot', {})
    print('shot:', s.get('path'))
