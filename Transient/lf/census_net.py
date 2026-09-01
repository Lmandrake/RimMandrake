import sys, pickle
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
data = {}
with RimBridge(host, port, token) as rb:
    for d in ('GravshipHull', 'Door', 'PowerConduit', 'HiddenConduit', 'VGE_AstrofuelPipe'):
        r = rb.call('jawa/list_things', {'defName': d, 'limit': 5000})
        rows = [(t['x'], t['z'], t['id']) for t in r.get('things', [])]
        data[d] = rows
        print(d, r.get('countMatched'), 'returned', len(rows))
pickle.dump(data, open(r'D:\Luke\dev\Rimworld\Transient\lf\net.pkl', 'wb'))
