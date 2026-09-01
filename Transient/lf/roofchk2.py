import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ri = rb.call('rimworld/get_cells_info', {'x': 124, 'z': 143, 'width': 7, 'height': 8})
    for c in ri.get('cells', []):
        r = c.get('roofDefName')
        if r: print(c['x'], c['z'], r)
    print('--- done')
