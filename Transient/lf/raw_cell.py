import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('rimworld/get_cell_info', {'x': 111, 'z': 158})
    print(json.dumps(r, default=str)[:900])
