"""
Apply THE BOIL / THE NINE MOUTHS / THE BRINE LADDER mutator layers to the Scald
(312-tile hypersaline lake, biome Lake, elev -350 m, the planet's only volcanic
province ring).

WHY this exists as a standalone script rather than one-off bridge calls: the
plan has ~11 distinct (def -> tile-list) writes plus a live probe for
VEE_MarineSanctuary's undocumented "coast sides" gate, and every write must be
followed by exactly one jawa/world_commit (never per-write - see
skills/rimbridge/references/world-authoring.md "the order the engine forces").
Keeping it as a script means the whole batch is reproducible from
scald_plan.json without re-deriving the tile lists by hand.

MUST run under python.exe (Windows loopback; python3 in WSL2 cannot reach the
bridge - NAT-mode network namespace). Reads scald_plan.json via a Windows path
for the same reason: a script talking to the bridge runs as python.exe, and
python.exe cannot resolve /mnt/d/... paths.

Traps hit while writing this:
  - jawa/world_mutators_set takes ONE def-list applied to ONE tile-list per
    call; it does not accept a tile->mutator dict. So the plan is grouped by
    def, not by tile, and each def gets exactly one call (readBack=0, since we
    verify separately with world_mutators_get afterwards - the inline readback
    is capped and would just be truncated noise here).
  - AddMutator (which world_mutators_set calls) silently displaces a mutator
    in the same category - RiverDelta on the 9 mouth tiles is EXPECTED to
    remove the River mutator that was there. That is correct, not a bug: the
    verification step checks "does this tile carry a mutator from the family
    written", never "does it still carry the exact original set".
  - VEE_MarineSanctuary's "coastline 1-5 coast sides" gate has no documented
    meaning for a water tile carrying its own coastline (a Lake tile's every
    land-adjacent side counts as "coast" by World.CoastDirectionAt, which is
    what jawa/world_mutators_audit's marineMutators check uses). So it is
    written to 2 probe tiles first, audited with marineMutators including
    VEE_MarineSanctuary, and only rolled out further if offenderCount stays 0
    against those 2 tiles.
"""
import sys, json, csv

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

PLAN_PATH = r'D:\Luke\dev\Rimworld\world\_scald\scald_plan.json'
REPORT_PATH = r'D:\Luke\dev\Rimworld\world\_scald\scald_apply_report.json'

plan = json.load(open(PLAN_PATH))
groups = plan['groups']
meta = plan['meta']
shallow = meta['shallow']

h = lambda t: (t * 2654435761) % 100

report = {'writes': [], 'marine_probe': None, 'marine_rollout': None}

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:

    def set_mut(action, mutators, tiles, note):
        if not tiles:
            report['writes'].append({'def': mutators, 'note': note, 'intended': 0, 'skipped': True})
            return
        r = rb.call('jawa/world_mutators_set', {
            'action': action,
            'mutators': mutators,
            'tiles': ','.join(str(t) for t in tiles),
            'readBack': 0,
        })
        row = {
            'def': mutators, 'action': action, 'note': note,
            'intended': len(tiles),
            'success': r.get('success'), 'added': r.get('added'), 'removed': r.get('removed'),
            'unknownDefs': r.get('unknownDefs'), 'errors': r.get('errors'),
        }
        report['writes'].append(row)
        print(json.dumps(row)[:300])

    # ---- (2) THE BOIL ----
    set_mut('add', 'AB_GeothermalHotspots', groups['AB_GeothermalHotspots'],
             'pyroclastic rim only - biome-locked gate enforced in the plan builder')
    set_mut('add', 'SteamGeysers_Increased', groups['SteamGeysers_Increased'],
             'nearvolc lake tiles, ungated on Lake')
    set_mut('add', 'VEE_SulfuricLake', groups['VEE_SulfuricLake'],
             'nearvolc no-river subset UNION dead-heart lethal subset (needs no river; excluded from river tiles anyway by construction)')
    set_mut('add', 'ToxicLake', groups['ToxicLake'],
             'dead-heart lethal subset, disjoint from the VEE_SulfuricLake dead-heart half')
    set_mut('add', 'VEE_ToxicVents', groups['VEE_ToxicVents'],
             'volcanic rim land tiles, hash-split half')
    set_mut('add', 'VEE_SmokeVents', groups['VEE_SmokeVents'],
             'volcanic rim land tiles, other half of the hash split')

    # ---- (3) THE NINE MOUTHS ----
    set_mut('add', 'RiverDelta', groups['RiverDelta'],
             'the 9 mouth tiles - EXPECTED to displace the River mutator there (category conflict)')
    set_mut('add', 'Fish_Increased', groups['Fish_Increased'],
             'mouths + fan lake tiles + shallow zone (dist 1-2) - union, mouths are land tiles, rest are Lake')
    set_mut('add', 'AnimalLife_Increased', groups['AnimalLife_Increased'],
             'mouths + fan lake tiles only (not the whole shallow zone)')

    # ---- (4) THE BRINE LADDER ----
    # mid brine (dist 3-4) intentionally gets nothing - the bare gradient.
    set_mut('add', 'Fish_Decreased', groups['Fish_Decreased'],
             'dead heart (dist 5+), mouth-fan tiles already excluded when the plan was built')

    rb.call('jawa/world_commit', {})
    print('committed core writes')

    # ---- VEE_MarineSanctuary probe ----
    probe_tiles = sorted(shallow, key=h)[:2]
    rb.call('jawa/world_mutators_set', {
        'action': 'add', 'mutators': 'VEE_MarineSanctuary',
        'tiles': ','.join(str(t) for t in probe_tiles), 'readBack': 2,
    })
    rb.call('jawa/world_commit', {})
    audit = rb.call('jawa/world_mutators_audit', {
        'marineMutators': 'Coast,VEE_MarineSanctuary', 'limit': 50, 'histogram': False,
    })
    report['marine_probe'] = {
        'tiles': probe_tiles,
        'offenderCount': audit.get('offenderCount'),
        'offenders': audit.get('offenders'),
    }
    print('marine probe offenderCount:', audit.get('offenderCount'))

    if audit.get('offenderCount', 1) == 0:
        # roll out to a deterministic ~60% of the shallow zone (already includes the 2 probe tiles)
        rollout = sorted(t for t in shallow if h(t) < 60)
        r = rb.call('jawa/world_mutators_set', {
            'action': 'add', 'mutators': 'VEE_MarineSanctuary',
            'tiles': ','.join(str(t) for t in rollout), 'readBack': 0,
        })
        rb.call('jawa/world_commit', {})
        audit2 = rb.call('jawa/world_mutators_audit', {
            'marineMutators': 'Coast,VEE_MarineSanctuary', 'limit': 50, 'histogram': False,
        })
        report['marine_rollout'] = {
            'intended': len(rollout), 'added': r.get('added'),
            'offenderCount': audit2.get('offenderCount'),
            'offenders': audit2.get('offenders'),
        }
        print('marine rollout intended', len(rollout), 'offenderCount', audit2.get('offenderCount'))
    else:
        report['marine_rollout'] = {'skipped': True, 'reason': 'probe produced audit offenders'}
        print('VEE_MarineSanctuary DROPPED - probe produced offenders')

    # ---- final full audit ----
    final_audit = rb.call('jawa/world_mutators_audit', {
        'marineMutators': 'Coast,VEE_MarineSanctuary', 'limit': 50, 'histogram': True,
    })
    report['final_audit'] = {
        'offenderCount': final_audit.get('offenderCount'),
        'offenders': final_audit.get('offenders'),
        'tilesWithMutators': final_audit.get('tilesWithMutators'),
        'mutatorHistogram': final_audit.get('mutatorHistogram'),
    }
    print('FINAL offenderCount:', final_audit.get('offenderCount'))

json.dump(report, open(REPORT_PATH, 'w'), indent=1)
print('wrote', REPORT_PATH)
