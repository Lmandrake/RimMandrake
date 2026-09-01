import sys, pickle
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
d = pickle.load(open(r'D:\Luke\dev\Rimworld\Transient\lf\net.pkl','rb'))
p = pickle.load(open(r'D:\Luke\dev\Rimworld\Transient\lf\rmplan.pkl','rb'))
clean = p['clean']
pipe_id = {(x,z): tid for x,z,tid in d['VGE_AstrofuelPipe']}
share_kill = [(129,153),(129,154),(153,173),(148,176),(146,181)]
with RimBridge(host, port, token) as rb:
    rects = ';'.join(f'{x},{z},1,1' for (x,z) in clean)
    r = rb.call('jawa/destroy_batch', {'rects': rects, 'category': 'Building'})
    print('rect destroy:', r.get('success'), r.get('message'))
    for c in share_kill:
        tid = pipe_id[c]
        ok = False
        for _ in range(5):
            r = rb.call('jawa/damage', {'thingId': tid, 'amount': 999})
            if r.get('destroyed') or not r.get('success'):
                ok = True; break
        print('kill', c, tid, '->', r.get('success'), r.get('destroyed'), r.get('message'))
    # read back: how many visible pipes remain?
    r = rb.call('jawa/list_things', {'defName': 'VGE_AstrofuelPipe', 'limit': 5000})
    walls = {(x,z) for x,z,_ in d['GravshipHull']}
    doors = {(x,z) for x,z,_ in d['Door']}
    left = [(t['x'],t['z']) for t in r.get('things',[]) if (t['x'],t['z']) not in walls and (t['x'],t['z']) not in doors]
    print('pipes remaining:', r.get('countMatched'), '| still visible (should be 2):', left)
