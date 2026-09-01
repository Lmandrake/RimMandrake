import sys, pickle
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
d = pickle.load(open(r'D:\Luke\dev\Rimworld\Transient\lf\net.pkl','rb'))
walls = {(x,z) for x,z,_ in d['GravshipHull']}
test = (122, 147)
assert test in walls
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/build_batch', {'ops': f'HiddenConduit:{test[0]},{test[1]};VGE_AstrofuelPipe:{test[0]},{test[1]}', 'faction': 'PlayerColony', 'wipeExisting': False})
    print('build:', r.get('success'), r.get('message'), r.get('placed'), r.get('failed'))
    r = rb.call('jawa/list_things', {'rect': f'{test[0]},{test[1]},1,1', 'limit': 20})
    for t in r.get('things', []):
        print('cell holds:', t['def'], t['id'])
