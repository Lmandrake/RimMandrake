import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # everything on the cells we will touch
    r = rb.call('jawa/list_things', {'rect': '124,143,7,4', 'limit': 100})
    for t in sorted(r.get('things', []), key=lambda t: (t['z'], t['x'])):
        print('thing', t['def'], t['id'], t['x'], t['z'], 'stuff', t.get('stuff'), 'hp', t.get('hitPoints'), '/', t.get('maxHitPoints'))
    # roof over old interior, tip, door, outside
    ri = rb.call('rimworld/get_cells_info', {'x': 124, 'z': 143, 'width': 7, 'height': 5})
    cells = ri.get('cells', ri)
    if isinstance(cells, dict): print(list(ri.keys()))
    else:
        for c in cells:
            if c.get('roof'): print('roof', c.get('x'), c.get('z'), c.get('roof'))
