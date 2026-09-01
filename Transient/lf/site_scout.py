import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
SITES = {
 'A_heatvent_eastdeck': (148, 183, 8, 8),
 'B_jetengine_westleg': (97, 180, 6, 6),
 'C_engineblock_ankle': (94, 130, 4, 4),
 'D_excavator_court': (122, 168, 5, 5),
 'E_chemtruck_court': (133, 174, 5, 5),
 'F_apc_court': (112, 174, 5, 5),
 'G_generator_eastdeck': (154, 158, 4, 4),
 'H_fuelnode_court': (128, 160, 3, 3),
}
with RimBridge(host, port, token) as rb:
    for name, (x, z, w, h) in SITES.items():
        r = rb.call('jawa/list_things', {'rect': f'{x},{z},{w},{h}', 'limit': 30})
        occ = [t['def'] for t in r.get('things', []) if t['def'] not in ('HiddenConduit','PowerConduit','VGE_AstrofuelPipe')]
        fr = rb.call('jawa/get_terrain_layers', {'rect': f'{x},{z},{w},{h}', 'limit': 100})
        cells = fr.get('cells', [])
        subs = sum(1 for c in cells if c.get('foundation'))
        tops = {str(c.get('top')) for c in cells}
        print(name, '| occupants:', occ[:6] or 'EMPTY', '| substructure:', f'{subs}/{len(cells)}', '| tops:', list(tops)[:3])
