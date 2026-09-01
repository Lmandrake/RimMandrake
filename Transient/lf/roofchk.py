import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ri = rb.call('rimworld/get_cells_info', {'x': 126, 'z': 146, 'width': 3, 'height': 5})
    cells = ri.get('cells') if isinstance(ri, dict) else None
    if cells is None:
        print(json.dumps(ri, default=str)[:600])
    else:
        print('keys of one cell:', list(cells[0].keys()))
        for c in cells:
            print(c.get('x'), c.get('z'), 'roof=', c.get('roof'), 'terrain=', c.get('terrain'))
