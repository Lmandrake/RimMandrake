import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/set_terrain_layer', {'layer': 'removeTop', 'rect': '125,144,5,1'})
    print('removeTop:', r.get('success'), r.get('message'))
    r = rb.call('jawa/set_substructure_batch', {'action': 'set', 'rect': '125,144,5,1'})
    print('substructure:', r.get('success'), r.get('message'))
    r = rb.call('jawa/set_terrain_batch', {'ops': 'UCScaffoldTile:125,144,5,1'})
    print('floor:', r.get('success'), r.get('message'))
    r = rb.call('jawa/build_batch', {'ops': 'GravshipHull:125,144;GravshipHull:126,144;GravshipHull:128,144;GravshipHull:129,144', 'stuff': 'MA_MegaBone', 'faction': 'PlayerColony'})
    print('build:', r.get('success'), r.get('message'), json.dumps({k: r.get(k) for k in ('placed','failed') if k in r}))
    r = rb.call('jawa/map_commit', {'full': True})
    print('commit:', r.get('success'))
