"""
Read back every tile apply_twilight_mutators.py wrote and diff against the
intended plan (twilight_plan.json), def by def. This is the "verify by
reading the planet back" step the task demands - a `success: true` /
`added: N` from world_mutators_set is not proof, only jawa/world_mutators_get
is (see world/_scald/verify_scald_mutators.py, which this mirrors).

Also explains "added < intended": AddMutator is a no-op when the tile
already carries that def (e.g. 19 pre-existing VEE_SaltPlains on the ring
overlapped this plan's candidates), so added < intended means "some tiles
already had it", not a failure. This script tells PRESENT vs MISSING apart
by reading every intended tile back directly, never by trusting `added`.

Run under python.exe (bridge access). Reads/writes Windows paths for the
same reason as apply_twilight_mutators.py.
"""
import sys, json

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

PLAN_PATH = r'D:\Luke\dev\Rimworld\world\_twilight\twilight_plan.json'
OUT_PATH = r'D:\Luke\dev\Rimworld\world\_twilight\twilight_verify_report.json'

plan = json.load(open(PLAN_PATH))
groups = dict(plan['groups'])

host, port, token = resolve_endpoint()
report = {}
with RimBridge(host, port, token) as rb:
    for defname, tiles in groups.items():
        if not tiles:
            report[defname] = {'intended': 0, 'landed': 0, 'missing': []}
            print(defname, 'intended 0 (measured empty -- see plan/apply script headers)')
            continue
        got = {}
        # world_mutators_get caps rows at `limit` -- always pass it explicitly.
        r = rb.call('jawa/world_mutators_get', {
            'tiles': ','.join(str(t) for t in tiles),
            'limit': len(tiles) + 5,
        })
        for row in r.get('tiles', []):
            got[row['tile']] = set(m['def'] for m in row['mutators'] if m.get('def'))
        missing = [t for t in tiles if defname not in got.get(t, set())]
        landed = len(tiles) - len(missing)
        report[defname] = {
            'intended': len(tiles), 'landed': landed, 'missing': missing,
            'rowsReturned': r.get('count'), 'requestErrors': r.get('errors'),
        }
        print(defname, 'intended', len(tiles), 'landed', landed, 'missing', missing[:10])

    # Sanity check for the fog probe cleanup: neither probe tile should
    # carry FoggyMutator any more.
    probe_tiles = plan['meta']['fog_probe_tiles']
    r = rb.call('jawa/world_mutators_get', {'tiles': ','.join(str(t) for t in probe_tiles), 'limit': 5})
    still_foggy = [row['tile'] for row in r.get('tiles', [])
                   if any(m['def'] == 'FoggyMutator' for m in row['mutators'])]
    report['_fog_probe_cleanup'] = {'probe_tiles': probe_tiles, 'still_carrying_FoggyMutator': still_foggy}
    print('fog probe cleanup check -- still carrying FoggyMutator:', still_foggy)

    # Final audit, restricted to genuinely coastal-gated defs (see apply
    # script's THE INCIDENT note -- never VEE_SaltPlains here).
    land_marine_defs = 'Iceberg,VEE_GravelBeach,VEE_RisingWaters,CoastalAtoll,VEE_LoneIsland,Bay'
    my_tiles_by_def = {d: set(groups.get(d, [])) for d in land_marine_defs.split(',')}
    audit = rb.call('jawa/world_mutators_audit', {
        'marineMutators': land_marine_defs, 'limit': 500, 'histogram': False,
    })
    offenders = audit.get('offenders', [])
    mine = [o for o in offenders if o['tile'] in my_tiles_by_def.get(o['mutator'], set())]
    report['_audit'] = {
        'marineMutators': land_marine_defs,
        'offenderCount': audit.get('offenderCount'),
        'offenders_mine': mine,
        'offenders_preexisting_elsewhere_on_planet': len(offenders) - len(mine),
    }
    print('audit offenderCount:', audit.get('offenderCount'), '-- mine:', len(mine))

json.dump(report, open(OUT_PATH, 'w'), indent=1)
print('wrote', OUT_PATH)
