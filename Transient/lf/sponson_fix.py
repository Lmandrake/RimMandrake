import sys, collections
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'rect': '138,78,30,22', 'limit': 2000})
    walls, pipes, fences, conds = {}, {}, set(), set()
    for t in r.get('things', []):
        c = (t['x'], t['z'])
        if t['def'] == 'GravshipHull': walls[c] = t['id']
        elif t['def'] == 'VGE_AstrofuelPipe': pipes[c] = t['id']
        elif t['def'] == 'Fence': fences.add(c)
        elif t['def'] == 'HiddenConduit': conds.add(c)
    ring_zone = {(x, z) for x in range(151, 166) for z in range(79, 97)}
    spur = {(x, 88) for x in range(141, 151)} | {(140, 87), (140, 89)}
    rem_walls = sorted(c for c in walls if c in ring_zone or c in spur)
    rem_pipes = sorted(c for c in pipes if (c in ring_zone or c in spur) and c not in walls)
    print('walls still standing in zone:', len(rem_walls), rem_walls[:12])
    print('orphan visible pipes in zone:', len(rem_pipes), rem_pipes[:12])
    # nuke remaining converted cells wholesale, remember what to rebuild
    nuke = sorted(set(rem_walls) | set(rem_pipes))
    if nuke:
        rebuild_f = [c for c in nuke if c in fences]
        rebuild_c = [c for c in nuke if c in conds]
        r = rb.call('jawa/destroy_batch', {'rects': ';'.join(f'{x},{z},1,1' for x, z in nuke), 'category': 'Building'})
        print('nuke:', r.get('success'), r.get('message'))
        ops = [f'Fence:{x},{z}' for x, z in rebuild_f]
        if ops:
            r = rb.call('jawa/build_batch', {'ops': ';'.join(ops), 'stuff': 'Steel', 'faction': 'PlayerColony'})
            print('fence rebuild:', r.get('placed'))
        ops = [f'HiddenConduit:{x},{z}' for x, z in rebuild_c]
        if ops:
            r = rb.call('jawa/build_batch', {'ops': ';'.join(ops), 'faction': 'PlayerColony'})
            print('conduit rebuild:', r.get('placed'))
    # foundation repair: target set
    cx, cz = 157, 88
    interior = {(x, z) for x in range(151, 165) for z in range(81, 96) if (x-157)**2 + (z-88)**2 <= 36}
    plat = {(x, z) for x in range(141, 151) for z in range(86, 91)}
    target = sorted(plat | interior | set(nuke) | spur)
    tops, fnd = {}, {}
    for z0 in (78, 88):
        fr = rb.call('jawa/get_terrain_layers', {'rect': f'138,{z0},30,10', 'limit': 5000})
        for c in fr.get('cells', []):
            tops[(c['x'], c['z'])] = str(c.get('top')); fnd[(c['x'], c['z'])] = c.get('foundation')
    bad = sorted(c for c in target if not fnd.get(c))
    print('cells lacking substructure:', len(bad))
    if bad:
        want = {c: tops.get(c, 'None') for c in bad}
        r = rb.call('jawa/set_terrain_layer', {'layer': 'removeTop', 'rect': ';'.join(f'{x},{z},1,1' for x, z in bad)})
        if not r.get('success'):  # maybe same one-rect rule
            for (x, z) in bad: rb.call('jawa/set_terrain_layer', {'layer': 'removeTop', 'rect': f'{x},{z},1,1'})
        ok = fail = 0
        for (x, z) in bad:
            r = rb.call('jawa/set_substructure_batch', {'action': 'set', 'rect': f'{x},{z},1,1'})
            if r.get('success'): ok += 1
            else: fail += 1
        print('substructure set:', ok, 'fail:', fail)
        keep_void = {(153, 91), (154, 91), (153, 90)}
        ops = []
        for (x, z) in bad:
            if (x, z) in keep_void: continue
            t = want[(x, z)]
            if 'XGrate' in t: d = 'guy762_FloorTiles_XGrate_iron'
            elif 'Doomgiver' in t: d = 'guy762_FloorTiles_DoomgiverFoorMetal_dark'
            else: d = 'AG_RustedTile'
            ops.append(f'{d}:{x},{z},1,1')
        r = rb.call('jawa/set_terrain_batch', {'ops': ';'.join(ops)})
        print('floors repainted:', r.get('success'), r.get('message'))
    r = rb.call('jawa/map_commit', {'full': True})
    print('commit:', r.get('success'))
