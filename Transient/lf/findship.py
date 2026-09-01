import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for d in ('GravEngine','PilotConsole','Door'):
        r = rb.call('jawa/list_things', {'defName': d, 'limit': 50})
        for t in r.get('things', []):
            print(t['def'], t['id'], t['x'], t['z'], 'rot', t['rot'])
    # bunks near the engine
    r = rb.call('jawa/list_things', {'group':'Bed', 'limit': 100})
    for t in r.get('things', []):
        print('BED', t['def'], t['x'], t['z'])
