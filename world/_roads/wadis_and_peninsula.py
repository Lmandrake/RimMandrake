"""Dry riverbeds where a river dies, and the removal of every Peninsula.

🔴 `VEE_DryRiver` must be written as a MUTATOR, not a landmark. Measured 2026-08-26: the
LandmarkDef's `IsValidTile` returned FALSE for every tile probed - across rings 1-3 from a
dying creek, across ZBiome_Badlands / AridShrubland / Desert / Wasteland / Grasslands, with
and without an adjacent river. It is unsatisfiable here, and the 23 existing dry-river
LANDMARKS must have been force-placed by an earlier pass. The MUTATOR form is live and legal
on 39 tiles with `world_mutators_audit` reporting offenderCount 0, so that is the instrument.

⚠️ The mutator setter does NOT enforce gates (skill: river-networks.md §1), so they are
enforced here: landlocked (0 coast sides) and a biome from the set where the mutator already
lives. The audit afterwards is the engine's own verdict.

⛔ Peninsula: owner, 2026-08-26 - *"Just get rid of the peninsula... it looks really stupid
rotated incorrectly."* All 12 removed. It exists only as a LandmarkDef here (0 as a mutator).
"""
import sys, os, json, collections
W = r'D:\Luke\dev\Rimworld' + os.sep
sys.path.insert(0, W + r'src\RimMandrake\Utils')
sys.path.insert(0, W + r'world\_roads')
import rcommon; rcommon.R = W + r'world\_roads' + os.sep; rcommon.B = W + 'world' + os.sep
from rcommon import load
from rimbridge_client import RimBridge, resolve_endpoint

tiles, nb, roads, rivers, setts, objs = load()
water = {t for t in tiles if tiles[t]['water']}
sides = lambda t: sum(1 for n in nb[t] if n in water)
h = lambda t: (t * 2654435761) % 100000
lmrows = json.load(open(rcommon.R + '_landmarks_now.json'))['landmarks']
lm = collections.defaultdict(list)
for l in lmrows: lm[l['tile']].append(l['def'])
M = collections.defaultdict(list)
for ch in json.load(open(rcommon.R + '_muts_now.json')):
    for l in ch['tiles']:
        for m in (l.get('mutators') or []):
            M[l['tile']].append(m if isinstance(m, str) else m.get('def'))

WADI_BIOMES = {'AridShrubland','ZBiome_Badlands','ExtremeDesert','Desert','AB_FeraliskInfestedJungle'}
dying = []
for t in rivers:
    if len(rivers[t]) != 1: continue
    if any(x in water for x in nb[t]): continue
    n = list(rivers[t])[0]
    if tiles[t]['elev'] > tiles[n]['elev']: continue
    dying.append(t)

laid, beds = [], 0
used = set()
for t in sorted(dying):
    cur, bed = t, []
    want = 2 + h(t) % 3
    while len(bed) < want:
        c = [x for x in nb[cur]
             if x not in water and x not in rivers and x not in used
             and 'VEE_DryRiver' not in M.get(x, ())
             and sides(x) == 0 and tiles[x]['biome'] in WADI_BIOMES
             and tiles[x]['elev'] <= tiles[cur]['elev'] + 60]
        if not c: break
        nxt = min(c, key=lambda x: (tiles[x]['elev'], h(x)))
        bed.append(nxt); used.add(nxt); cur = nxt
    if bed: beds += 1; laid += bed
    print("   wadi from %-6d %-14s %4dm -> %d tiles %s"
          % (t, tiles[t]['region'], tiles[t]['elev'], len(bed), bed))

pen = [t for t in lm if 'Peninsula' in lm[t]]
host, port, tok = resolve_endpoint()
with RimBridge(host, port, tok) as rb:
    if laid:
        r = rb.call('jawa/world_mutators_set',
                    {'action': 'add', 'mutators': 'VEE_DryRiver',
                     'tiles': ','.join(map(str, laid)), 'readBack': 0})
        print("\nVEE_DryRiver add: success=%s on %d tiles" % (r.get('success'), len(laid)))
    r = rb.call('jawa/world_landmarks_set',
                {'action': 'remove', 'def': 'Peninsula',
                 'tiles': ','.join(map(str, pen)), 'checkValid': False})
    print("Peninsula removed: %s of %d" % (r.get('removed'), len(pen)))
    rb.call('jawa/world_commit', {})
    a = rb.call('jawa/world_mutators_audit', {'limit': 20})
    print("AUDIT offenderCount %s ; VEE_DryRiver now %s ; tilesWithMutators %s"
          % (a.get('offenderCount'), (a.get('mutatorHistogram') or {}).get('VEE_DryRiver'),
             a.get('tilesWithMutators')))
    if a.get('offenderCount'):
        print("   offenders:", json.dumps(a.get('offenders'))[:400])
    lmn = rb.call('jawa/world_landmarks_get', {'limit': 4000})
    print("landmarks now %s" % lmn.get('count'))
json.dump({'wadis': laid, 'peninsula_removed': pen}, open(rcommon.R + 'wadis.json', 'w'))
