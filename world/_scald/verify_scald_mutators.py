"""
Read back every tile apply_scald_mutators.py touched and diff against the
intended plan (scald_plan.json), def by def. This is the "verify by reading
the planet back" step the task demands - a `success: true` / `added: N` from
world_mutators_set is not proof, only jawa/world_mutators_get is.

Also explains the two "added < intended" lines apply_scald_mutators.py printed:
AddMutator (which world_mutators_set calls) is a no-op when the tile already
carries that def - so added < intended means "some of these tiles already had
it", not a failure. This script tells the two apart by reading the def back on
every intended tile and reporting PRESENT vs MISSING, not by trusting the
"added" counter.

Run under python.exe (bridge access). Reads/writes Windows paths for the same
reason as apply_scald_mutators.py.
"""
import sys, json

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

PLAN_PATH = r'D:\Luke\dev\Rimworld\world\_scald\scald_plan.json'
OUT_PATH = r'D:\Luke\dev\Rimworld\world\_scald\scald_verify_report.json'

plan = json.load(open(PLAN_PATH))
groups = dict(plan['groups'])
# marine sanctuary was dropped live (probe produced audit offenders) - not verified here.

host, port, token = resolve_endpoint()
report = {}
with RimBridge(host, port, token) as rb:
    for defname, tiles in groups.items():
        if not tiles:
            report[defname] = {'intended': 0, 'landed': 0, 'missing': []}
            continue
        got = {}
        # world_mutators_get caps rows at `limit` - always pass it explicitly.
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

    audit = rb.call('jawa/world_mutators_audit', {
        'marineMutators': 'Coast,VEE_MarineSanctuary', 'limit': 50, 'histogram': False,
    })
    report['_audit'] = {'offenderCount': audit.get('offenderCount'), 'offenders': audit.get('offenders')}
    print('audit offenderCount:', audit.get('offenderCount'))

json.dump(report, open(OUT_PATH, 'w'), indent=1)
print('wrote', OUT_PATH)
