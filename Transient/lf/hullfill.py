import sys
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    fresh = {}
    for dn in ('GravshipHull', 'Door', 'PowerConduit', 'HiddenConduit', 'VGE_AstrofuelPipe'):
        r = rb.call('jawa/list_things', {'defName': dn, 'limit': 6000})
        fresh[dn] = {(t['x'], t['z']) for t in r.get('things', [])}
        print(dn, len(fresh[dn]))
    hull = fresh['GravshipHull'] | fresh['Door']
    cond = fresh['PowerConduit'] | fresh['HiddenConduit']
    need_cond = sorted(hull - cond)
    need_pipe = sorted(hull - fresh['VGE_AstrofuelPipe'])
    print('need conduit:', len(need_cond), '| need pipe:', len(need_pipe))
    ops = [f'HiddenConduit:{x},{z}' for (x, z) in need_cond] + \
          [f'VGE_AstrofuelPipe:{x},{z}' for (x, z) in need_pipe]
    total_placed, fails = 0, []
    for i in range(0, len(ops), 150):
        chunk = ops[i:i+150]
        r = rb.call('jawa/build_batch', {'ops': ';'.join(chunk), 'faction': 'PlayerColony', 'wipeExisting': False})
        total_placed += r.get('placed') or 0
        if r.get('failed'): fails.extend(r['failed'])
        if not r.get('success'): print('chunk', i, 'FAILED:', r.get('message'))
    print('placed:', total_placed, 'of', len(ops), '| failures:', fails[:10] if fails else 'none')
    r = rb.call('jawa/map_commit', {'full': True})
    print('commit:', r.get('success'))
    # read-back
    for dn in ('HiddenConduit', 'VGE_AstrofuelPipe', 'GravshipHull'):
        r = rb.call('jawa/list_things', {'defName': dn, 'limit': 6000})
        print('now:', dn, r.get('countMatched'))
