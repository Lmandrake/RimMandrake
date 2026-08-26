"""Repair two coastal-category displacements the Twilight pass caused and did not report.

🔴 Measured 2026-08-26 by diffing the whole planet's mutators before and after. The pass's
own verification was per-def against its OWN intent, so it could not see what its writes
DISPLACED elsewhere. Category conflicts are the system working — but they are still a loss
somebody has to look at.

1. **26 `CoastalIsland` mutators destroyed on the Twilight Sea**, 21 overwritten by
   `VEE_RisingWaters` (same `coastal` category). ⛔ That undoes the island scattering the
   owner asked for by name on 2026-08-25 ("add more 'meus isle' types ... just a scattering").
   The islands win: they were a specific instruction, and `VEE_RisingWaters` can sit on any
   flat shore, so it is RELOCATED rather than dropped.

2. **2 `Oasis` destroyed** on the Dew Horn shore (17209, 17211), overwritten by
   `VEE_SaltPlains`. ⛔ Canon is explicit that oasis tiles are not to be converted
   (ASHKARR_WORLD_DEFINITION §7c: "no oasis tile was converted, the Scald's seven are the only
   fresh water in the hottest country on the planet"). Restored.

⛔ No RNG. Relocation targets are chosen by tile-id hash.
"""
import sys, os, json, collections, csv
W = r'D:\Luke\dev\Rimworld' + os.sep
sys.path.insert(0, W + r'src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

R = W + r'world\_roads' + os.sep
def load(p):
    M = collections.defaultdict(set)
    for ch in json.load(open(p)):
        for l in ch['tiles']:
            for m in (l.get('mutators') or []): M[l['tile']].add(m if isinstance(m, str) else m.get('def'))
    return M
B, A = load(R + '_muts_now.json'), load(R + '_muts_final.json')
lost_isle = [t for t in B if 'CoastalIsland' in B[t] and 'CoastalIsland' not in A.get(t, set())]
lost_oasis = [t for t in B if 'Oasis' in B[t] and 'Oasis' not in A.get(t, set())]
COASTAL = {'VEE_RisingWaters', 'CoastalAtoll', 'Bay', 'VEE_LoneIsland', 'VEE_CoralReef',
           'Archipelago', 'Peninsula', 'VEE_GravelBeach', 'VEE_BasaltCape'}
print("to restore: %d CoastalIsland, %d Oasis" % (len(lost_isle), len(lost_oasis)))

now = {int(r['tile']): r for r in csv.DictReader(open(R + 'now_tiles.csv'))}
nb = {}
for r in csv.DictReader(open(W + r'world\world_neighbors_sub7b.csv')):
    nb[int(r['tile'])] = [int(r['n%d' % i]) for i in range(6) if int(r['n%d' % i]) >= 0]
water = {t for t in now if int(now[t]['water'])}
G = json.load(open(R + 'twilight_geom.json'))
ring = set(G['ring'])
h = lambda t: (t * 2654435761) % 100
sides = lambda t: sum(1 for n in nb[t] if n in water)

host, port, tok = resolve_endpoint()
with RimBridge(host, port, tok) as rb:
    # --- 1. clear the competing coastal mutator, restore the island -------
    moved = 0
    for t in lost_isle:
        comp = sorted(A.get(t, set()) & COASTAL)
        for c in comp:
            rb.call('jawa/world_mutators_set', {'action': 'remove', 'mutators': c,
                                                'tiles': str(t), 'readBack': 0})
            if c == 'VEE_RisingWaters': moved += 1
    rb.call('jawa/world_mutators_set', {'action': 'add', 'mutators': 'CoastalIsland',
                                        'tiles': ','.join(map(str, lost_isle)), 'readBack': 0})
    # --- 2. restore the oases --------------------------------------------
    for t in lost_oasis:
        rb.call('jawa/world_mutators_set', {'action': 'remove', 'mutators': 'VEE_SaltPlains',
                                            'tiles': str(t), 'readBack': 0})
    rb.call('jawa/world_mutators_set', {'action': 'add', 'mutators': 'Oasis',
                                        'tiles': ','.join(map(str, lost_oasis)), 'readBack': 0})
    # --- 3. relocate VEE_RisingWaters to flat shore with no coastal rival --
    cand = [t for t in ring
            if now[t]['hilliness'] in ('1', 'Flat') and 1 <= sides(t) <= 5
            and not (A.get(t, set()) & COASTAL) and 'CoastalIsland' not in A.get(t, set())
            and t not in lost_isle and t not in lost_oasis]
    cand.sort(key=h)
    take = cand[:moved]
    if take:
        rb.call('jawa/world_mutators_set', {'action': 'add', 'mutators': 'VEE_RisingWaters',
                                            'tiles': ','.join(map(str, take)), 'readBack': 0})
    print("removed %d VEE_RisingWaters, relocated %d of them (pool %d)" % (moved, len(take), len(cand)))
    rb.call('jawa/world_commit', {})
    # --- verify -----------------------------------------------------------
    chk = rb.call('jawa/world_mutators_get',
                  {'tiles': ','.join(map(str, lost_isle + lost_oasis + take)), 'limit': 200})
    got = {l['tile']: {m if isinstance(m, str) else m.get('def') for m in (l.get('mutators') or [])}
           for l in chk['tiles']}
    print("CoastalIsland restored: %d/%d" % (sum(1 for t in lost_isle if 'CoastalIsland' in got.get(t, set())), len(lost_isle)))
    print("Oasis restored:         %d/%d" % (sum(1 for t in lost_oasis if 'Oasis' in got.get(t, set())), len(lost_oasis)))
    print("RisingWaters relocated: %d/%d" % (sum(1 for t in take if 'VEE_RisingWaters' in got.get(t, set())), len(take)))
    a = rb.call('jawa/world_mutators_audit', {'limit': 5})
    print("AUDIT offenderCount", a.get('offenderCount'))
