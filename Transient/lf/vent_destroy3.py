import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def cell_defs(rb, x, z):
    r = rb.call('rimworld/get_cell_info', {'x': x, 'z': z})
    return [t.get('defName') for t in (r.get('cell') or {}).get('things', [])]
with RimBridge(host, port, token) as rb:
    ch = rb.call('rimworld/list_debug_action_children', {'path': 'Actions'})['children']
    cands = [c['path'] for c in ch if 'destroy' in c['path'].lower()]
    print('destroy actions:', cands)
    if cands:
        path = next((p for p in cands if 'T: Destroy' in p), cands[0])
        for (x, z) in [(168, 64), (76, 48)]:
            r = rb.call('rimworld/execute_debug_action', {'path': path, 'x': x, 'z': z})
            print((x, z), 'action:', r.get('success'), r.get('message'), '| cell now:', cell_defs(rb, x, z) or 'empty')
    rb.call('jawa/map_commit', {'redraw': True})
