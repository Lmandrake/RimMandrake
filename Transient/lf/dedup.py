import sys, collections
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for dn in ('VGE_AstrofuelPipe', 'HiddenConduit'):
        r = rb.call('jawa/list_things', {'defName': dn, 'limit': 6000})
        by_cell = collections.defaultdict(list)
        for t in r.get('things', []):
            by_cell[(t['x'], t['z'])].append(t['id'])
        dups = {c: ids for c, ids in by_cell.items() if len(ids) > 1}
        print(dn, 'dup cells:', len(dups))
        killed = 0
        for c, ids in dups.items():
            for tid in ids[1:]:
                last = None
                for _ in range(4):
                    last = rb.call('jawa/damage', {'thingId': tid, 'amount': 999, 'damageDef': 'Cut'})
                    if last.get('destroyed') or not last.get('success'): break
                if last.get('destroyed'): killed += 1
                else: print('  FAILED to remove', tid, 'at', c, last.get('message'))
        print(dn, 'removed', killed, 'duplicates')
    for dn in ('VGE_AstrofuelPipe', 'HiddenConduit'):
        r = rb.call('jawa/list_things', {'defName': dn, 'limit': 6000})
        cnt = collections.Counter((t['x'], t['z']) for t in r.get('things', []))
        print('final:', dn, r.get('countMatched'), 'remaining dup cells:', sum(1 for v in cnt.values() if v > 1))
    r = rb.call('jawa/map_commit', {'power': True, 'redraw': True})
    print('commit:', r.get('success'))
