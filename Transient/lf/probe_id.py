import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('rimworld/get_cell_info', {'x': 161, 'z': 90})
    print('cell (161,90) things:', json.dumps(r.get('things', r.get('solidThingDefs')), default=str)[:400])
    r2 = rb.call('jawa/list_things', {'rect': '161,90,1,1', 'limit': 10})
    for t in r2.get('things', []): print('list says:', t['def'], t['id'])
