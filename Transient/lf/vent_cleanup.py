import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'rect': '30,24,72,34', 'defName': 'AncientHeatVent', 'limit': 5})
    for t in r.get('things', []):
        x, z = t['x'], t['z']
        r2 = rb.call('jawa/destroy_batch', {'rects': f'{x-3},{z-3},7,7', 'categories': 'Building'})
        print('vent at', (x, z), '->', r2.get('message'))
    r = rb.call('jawa/list_things', {'rect': '30,24,72,34', 'limit': 60})
    left = [t['def'] for t in r.get('things', []) if t['def'].startswith(('Ancient', 'Chunk'))]
    print('leftovers now:', left or 'none')
