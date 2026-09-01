import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # 1. substructure under the new wall row (door cell already has it)
    r = rb.call('jawa/set_substructure_batch', {'action': 'add', 'rect': '125,144,5,1'})
    print('substructure:', r.get('success'), r.get('message'), {k: r.get(k) for k in ('cellsChanged','cellsFailedVerify','cellsSkipped') if k in r})
    # 2. floor under the new walls, matching the existing wall cells
    r = rb.call('jawa/set_terrain_batch', {'ops': 'UCScaffoldTile:125,144,5,1'})
    print('floor:', r.get('success'), r.get('message'), {k: r.get(k) for k in ('cellsChanged','cellsFailedVerify') if k in r})
    # 3. remove the four old tip walls (no conduits present - verified)
    r = rb.call('jawa/destroy_batch', {'rects': '125,145,2,1;128,145,2,1', 'category': 'Building'})
    print('destroy:', r.get('success'), r.get('message'), json.dumps({k: r.get(k) for k in ('destroyed','count','countDestroyed') if k in r}))
    # 4. new wall row embedding the door
    r = rb.call('jawa/build_batch', {'ops': 'GravshipHull:125,144;GravshipHull:126,144;GravshipHull:128,144;GravshipHull:129,144', 'stuff': 'MA_MegaBone', 'faction': 'player'})
    print('build:', r.get('success'), r.get('message'), json.dumps({k: r.get(k) for k in ('placed','failed') if k in r}))
    # 5. commit
    r = rb.call('jawa/map_commit', {'full': True})
    print('commit:', r.get('success'), r.get('message'))
