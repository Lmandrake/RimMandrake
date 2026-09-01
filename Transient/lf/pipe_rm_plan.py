import sys, pickle
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
d = pickle.load(open(r'D:\Luke\dev\Rimworld\Transient\lf\net.pkl','rb'))
walls = {(x,z) for x,z,_ in d['GravshipHull']}
doors = {(x,z) for x,z,_ in d['Door']}
vis = [(x,z) for x,z,_ in d['VGE_AstrofuelPipe'] if (x,z) not in walls and (x,z) not in doors]
with RimBridge(host, port, token) as rb:
    clean, dirty = [], []
    for (x,z) in vis:
        r = rb.call('jawa/list_things', {'rect': f'{x},{z},1,1', 'limit': 20})
        others = [t['def'] for t in r.get('things', []) if t['def'] != 'VGE_AstrofuelPipe' and t.get('id','').startswith(('Building',''))]
        # keep only buildings/items that a Building-category destroy would take
        others = [o for o in others if o not in ('','Filth')]
        if others: dirty.append(((x,z), others))
        else: clean.append((x,z))
    print('clean cells (pipe only):', len(clean))
    print('dirty cells:', len(dirty))
    for c, o in dirty[:20]: print(c, o)
    pickle.dump({'clean': clean, 'dirty': dirty}, open(r'D:\Luke\dev\Rimworld\Transient\lf\rmplan.pkl','wb'))
