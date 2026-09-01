import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
want = {'jawa/list_things','jawa/get_terrain_layers','jawa/set_terrain_batch','jawa/build_batch','jawa/set_substructure_batch','jawa/map_commit','jawa/set_terrain_layer','rimworld/get_cells_info','jawa/destroy_batch','jawa/set_roof_batch'}
with RimBridge(host, port, token) as rb:
    listing = rb._request('tools/list', {})
    for t in listing.get('tools', []):
        if t['name'] in want:
            sch = t.get('inputSchema', {})
            props = sch.get('properties', {})
            print(t['name'], '->', {k: v.get('type','?') for k,v in props.items()})
