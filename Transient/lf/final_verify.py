import sys, collections
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call('rimworld/get_game_info')
    print('tick:', info.get('ticksGame'))
    fresh = {}
    for dn in ('GravshipHull','Door','VGE_AstrofuelPipe','HiddenConduit','VGE_AstrofuelPipeRupture'):
        r = rb.call('jawa/list_things', {'defName': dn, 'limit': 6000})
        fresh[dn] = [(t['x'], t['z']) for t in r.get('things', [])]
        print(dn, r.get('countMatched'))
    hull = set(fresh['GravshipHull']) | set(fresh['Door'])
    pipes = fresh['VGE_AstrofuelPipe']
    dup = [c for c, n in collections.Counter(pipes).items() if n > 1]
    print('duplicate pipe cells:', len(dup), dup[:5])
    hull_no_pipe = hull - set(pipes)
    hull_no_cond = hull - set(fresh['HiddenConduit'])
    print('hull cells missing pipe:', len(hull_no_pipe), '| missing hidden conduit (may have PowerConduit):', len(hull_no_cond))
    vis = [c for c in set(pipes) if c not in hull]
    print('pipes NOT under hull/door:', len(vis))
    east_vis = sorted(c for c in vis if c[0] >= 129)
    print('of those, eastern (x>=129):', len(east_vis), east_vis[:15])
    rb.call('jawa/clear_ui', {})
    rb.call('rimworld/jump_camera_to_cell', {'x': 150, 'z': 180})
    s = rb.call('rimworld/take_screenshot', {})
    print('shot:', s.get('path'))
