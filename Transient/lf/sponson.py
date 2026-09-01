import sys, collections
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    fd = rb.call('jawa/get_def', {'defName': 'Fence', 'defType': 'ThingDef'})
    print('Fence def ok:', fd.get('success'), (fd.get('def') or {}).get('label') if isinstance(fd.get('def'), dict) else fd.get('message'))

    # fresh survey of the region
    r = rb.call('jawa/list_things', {'rect': '138,78,30,22', 'limit': 2000})
    walls, pipes, conds = {}, {}, set()
    for t in r.get('things', []):
        c = (t['x'], t['z'])
        if t['def'] == 'GravshipHull': walls[c] = t['id']
        elif t['def'] == 'VGE_AstrofuelPipe': pipes[c] = t['id']
        elif t['def'] == 'HiddenConduit': conds.add(c)
    ring_walls = {c for c in walls if c[0] >= 151}
    spur_walls = {c for c in walls if 141 <= c[0] <= 150 and c[1] == 88}
    ship_open  = {c for c in ((140,87),(140,89)) if c in walls}
    to_remove = ring_walls | spur_walls | ship_open
    print('ring walls:', len(ring_walls), '| spur walls:', len(spur_walls), '| ship opening:', len(ship_open))

    # interior of ring: flood from (157,88) bounded by ring wall footprint, radius guard 8
    cx, cz = 157, 88
    interior, stack, seen = set(), [(cx,cz)], {(cx,cz)}
    while stack:
        x, z = stack.pop()
        if abs(x-cx) > 8 or abs(z-cz) > 8: continue
        interior.add((x,z))
        for dx, dz in ((1,0),(-1,0),(0,1),(0,-1)):
            n = (x+dx, z+dz)
            if n not in seen and n not in ring_walls:
                seen.add(n); stack.append(n)
    interior -= ring_walls
    print('ring interior cells:', len(interior))

    # phase 1: kill walls and pipes on converted cells (keep conduits)
    kills = 0
    for c in sorted(to_remove):
        for tid in (walls.get(c), pipes.get(c)):
            if not tid: continue
            last = None
            for _ in range(4):
                last = rb.call('jawa/damage', {'thingId': tid, 'amount': 2000, 'damageDef': 'Cut'})
                if last.get('destroyed') or not last.get('success'): break
            if last.get('destroyed'): kills += 1
            else: print('  kill FAILED', c, tid, last.get('message'))
    print('phase1 destroyed:', kills, 'of', sum(1 for c in to_remove for t in (walls.get(c), pipes.get(c)) if t))

    # phase 2: substructure (before any floor) - platform rows z86..90 x141..150 + ring interior
    plat = {(x, z) for x in range(141, 151) for z in range(86, 91)}
    need_sub = sorted(plat | interior | to_remove)
    ops = ';'.join(f'{x},{z},1,1' for (x, z) in need_sub)
    r = rb.call('jawa/set_substructure_batch', {'action': 'set', 'rect': ops})
    print('substructure:', r.get('success'), r.get('message'))

    # phase 3: floors. keep-void patch for "mostly restored"
    keep_void = {(153, 91), (154, 91), (153, 90)}
    keep_void &= interior
    # read current tops to preserve existing XGrate
    tops = {}
    for z0 in (78, 88):
        fr = rb.call('jawa/get_terrain_layers', {'rect': f'138,{z0},30,10', 'limit': 5000})
        for c in fr.get('cells', []): tops[(c['x'], c['z'])] = str(c.get('top'))
    floor_cells = (plat | interior | to_remove) - keep_void
    rust, keep = [], 0
    for c in sorted(floor_cells):
        if 'XGrate' in tops.get(c, ''): keep += 1; continue
        rust.append(c)
    # grate the neighbors of kept voids (the ship rule)
    grate = set()
    for (x, z) in keep_void:
        for dx in (-1,0,1):
            for dz in (-1,0,1):
                n = (x+dx, z+dz)
                if n in floor_cells: grate.add(n)
    rust = [c for c in rust if c not in grate]
    pad = {(x, z) for x in range(156, 159) for z in range(87, 90)} & floor_cells
    rust = [c for c in rust if c not in pad]
    ops = [f'AG_RustedTile:{x},{z},1,1' for (x,z) in rust] + \
          [f'guy762_FloorTiles_XGrate_iron:{x},{z},1,1' for (x,z) in sorted(grate)] + \
          [f'guy762_FloorTiles_DoomgiverFoorMetal_dark:{x},{z},1,1' for (x,z) in sorted(pad - grate)]
    r = rb.call('jawa/set_terrain_batch', {'ops': ';'.join(ops)})
    print('floors:', r.get('success'), r.get('message'))

    # phase 4: fences - platform rims z86/z90, ring circle on old wall cells minus west entry
    entry = {c for c in ring_walls if c[0] <= 152 and 86 <= c[1] <= 90}
    fence_cells = sorted(({(x, 86) for x in range(141, 151)} | {(x, 90) for x in range(141, 151)} | (ring_walls - entry)))
    ops = ';'.join(f'Fence:{x},{z}' for (x, z) in fence_cells)
    r = rb.call('jawa/build_batch', {'ops': ops, 'stuff': 'Steel', 'faction': 'PlayerColony', 'wipeExisting': False})
    print('fences:', r.get('success'), 'placed', r.get('placed'), 'failed', r.get('failed'))
    print('entry gap cells (no fence):', sorted(entry))

    # phase 5: hidden conduit into the ring center + pad
    need_cond = sorted(({(x, 88) for x in range(151, 158)} | pad | set(fence_cells)) - conds)
    ops = ';'.join(f'HiddenConduit:{x},{z}' for (x, z) in need_cond)
    if ops:
        r = rb.call('jawa/build_batch', {'ops': ops, 'faction': 'PlayerColony', 'wipeExisting': False})
        print('conduit:', r.get('success'), 'placed', r.get('placed'), 'failed', r.get('failed'))
    r = rb.call('jawa/map_commit', {'full': True})
    print('commit:', r.get('success'))
