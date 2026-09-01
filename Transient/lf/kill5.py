import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for (x, z) in [(129,153),(129,154),(153,173),(148,176),(146,181)]:
        r = rb.call('jawa/list_things', {'rect': f'{x},{z},1,1', 'defName': 'VGE_AstrofuelPipe', 'limit': 5})
        things = r.get('things', [])
        if not things:
            print((x,z), 'no pipe found'); continue
        tid = things[0]['id']
        last = None
        for _ in range(6):
            last = rb.call('jawa/damage', {'thingId': tid, 'amount': 999, 'damageDef': 'Cut'})
            if last.get('destroyed') or not last.get('success'): break
        print('kill', (x,z), tid, '->', last.get('success'), 'destroyed:', last.get('destroyed'), last.get('message'))
