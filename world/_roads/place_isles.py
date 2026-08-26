"""Place landmarks ONE AT A TIME, keeping only what the engine accepts.

🔴 Measured 2026-08-26. `world_landmarks_set action=add` reports `added: N` even for tiles
whose `isValidTile` is FALSE — `AddLandmark` does not enforce validity, exactly as the skill
warns. Worse, validity is evaluated PER TILE AS IT GOES, so a batch of 16 coastal landmarks
spaced 2 tiles apart has each one invalidate its neighbours, and the same batch returns a
different validity pattern on a second run. ⛔ A batch add is therefore unusable here.

✅ The pattern that works: add one tile, read its `isValidTile`, and REMOVE it again if false.
The engine is the arbiter and the map only ever keeps legal placements.
"""
import sys, json, collections
import os
# ⚠️ This one runs under python.exe (the bridge binds Windows loopback), so every path here
# must be the WINDOWS form - rcommon's /mnt/d default cannot be opened from Windows Python.
W = r'D:\Luke\dev\Rimworld' + os.sep
sys.path.insert(0, W + r'src\RimMandrake\Utils')
sys.path.insert(0, W + r'world\_roads')
from rimbridge_client import RimBridge, resolve_endpoint
import rcommon
rcommon.R = W + r'world\_roads' + os.sep
rcommon.B = W + 'world' + os.sep
from rcommon import load, gcdeg

tiles, nb, roads, rivers, setts, objs = load()
lmnow = json.load(open(rcommon.R + '_landmarks_now.json'))['landmarks']
have = collections.defaultdict(list)
for l in lmnow: have[l['tile']].append(l['def'])
water = {t for t in tiles if tiles[t]['water']}
sides = lambda t: sum(1 for n in nb[t] if n in water)
h = lambda t: (t * 2654435761) % 100000

# empirical biome sets: where each def ALREADY lives on this planet (the roster note is
# truncated with '...', so it is UNMEASURED, not permission)
ISLE_BIOMES = {'Wasteland','ZBiome_Badlands','AridShrubland','Desert','AB_MycoticJungle','ExtremeDesert'}
WADI_BIOMES = {'ZBiome_Badlands','ExtremeDesert','Desert','AridShrubland'}

def candidates(sea, lo, hi, biomes):
    S = {t for t in tiles if tiles[t]['region'] == sea and tiles[t]['water']}
    out = [t for t in tiles
           if not tiles[t]['water'] and lo <= sides(t) <= hi
           and any(n in S for n in nb[t]) and not rivers.get(t)
           and tiles[t]['biome'] in biomes and t not in have]
    return sorted(out, key=h)

placed = collections.defaultdict(list)

def try_place(rb, t, d, chosen, gap):
    if any(gcdeg(tiles, t, c) < gap for c in chosen): return False
    r = rb.call('jawa/world_landmarks_set',
                {'action': 'add', 'def': d, 'tiles': str(t), 'checkValid': True, 'forced': False})
    v = (r.get('validity') or [{}])[0]
    if v.get('isValidTile'):
        chosen.append(t); placed[d].append(t); return True
    rb.call('jawa/world_landmarks_set', {'action': 'remove', 'def': d, 'tiles': str(t), 'checkValid': False})
    return False

host, port, tok = resolve_endpoint()
with RimBridge(host, port, tok) as rb:
    all_chosen = []
    for sea, want_i, want_a in (('Twilight Sea', 8, 6), ('Grey Sea', 8, 6)):
        ci = candidates(sea, 3, 5, ISLE_BIOMES)
        n = 0
        for t in ci:
            if n >= want_i: break
            if try_place(rb, t, 'CoastalIsland', all_chosen, 3.2): n += 1
        ar = candidates(sea, 2, 5, ISLE_BIOMES)
        m = 0
        for t in ar:
            if m >= want_a: break
            if t in placed['CoastalIsland']: continue
            if try_place(rb, t, 'Archipelago', all_chosen, 3.2): m += 1
        print("%-13s CoastalIsland %d/%d   Archipelago %d/%d   (pools %d / %d)"
              % (sea, n, want_i, m, want_a, len(ci), len(ar)))

    # ---- dry beds where a river dies -----------------------------------
    dying = []
    for t in rivers:
        if len(rivers[t]) != 1: continue
        if any(x in water for x in nb[t]): continue
        nn = list(rivers[t])[0]
        if tiles[t]['elev'] > tiles[nn]['elev']: continue
        dying.append(t)
    beds = 0
    for t in sorted(dying):
        cur, laid = t, 0
        want = 2 + h(t) % 3
        while laid < want:
            cands = [x for x in nb[cur]
                     if x not in water and x not in rivers and x not in have
                     and x not in placed['VEE_DryRiver'] and sides(x) == 0
                     and tiles[x]['biome'] in WADI_BIOMES
                     and tiles[x]['elev'] <= tiles[cur]['elev'] + 60]
            if not cands: break
            nxt = min(cands, key=lambda x: (tiles[x]['elev'], h(x)))
            if not try_place(rb, nxt, 'VEE_DryRiver', [], 0.0): break
            laid += 1; cur = nxt
        if laid: beds += 1
        print("   wadi from %-6d %-14s %4dm -> %d tiles" % (t, tiles[t]['region'], tiles[t]['elev'], laid))
    print("\n%d dying rivers, %d given a bed" % (len(dying), beds))
    rb.call('jawa/world_commit', {})
    tot = rb.call('jawa/world_landmarks_get', {'limit': 4000})
    print("landmarks now %s (baseline 563, added %d)"
          % (tot.get('count'), sum(len(v) for v in placed.values())))
json.dump({k: v for k, v in placed.items()}, open(rcommon.R + 'placed.json', 'w'))
