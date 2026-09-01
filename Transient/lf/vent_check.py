import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('rimworld/get_cell_info', {'x': 76, 'z': 48})
    print('cell (76,48):', json.dumps(r.get('solidThingDefs'), default=str), '| things:', json.dumps(r.get('things'), default=str)[:200])
