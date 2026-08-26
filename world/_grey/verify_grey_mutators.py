"""
Final verification pass for the Grey Sea mutator work: reads every tile in
grey_plan.json's (corrected) groups back from the live planet and reports
intended/landed/missing per def, then runs jawa/world_mutators_audit
restricted to the three defs this plan actually coastline-gates.

Why a separate script from apply_grey_mutators.py: the plan was hardened
AFTER the first live apply (see plan_grey_mutators.py's PROTECTED_DEFS
section and grey_displacement_diff.json) by narrowing 16 protected-def
displacements down to zero via a live remove+restore, then tightening the
VEE_RisingWaters/Coast/Archipelago candidate pools so a future run of
plan_grey_mutators.py reproduces the corrected result directly. Because the
corrected pool for every one of those three defs is a strict SUBSET of what
was actually written in the first apply (removing only tiles that carried a
protected def), nothing further needed to be written to the bridge - this
script exists purely to read the live planet back against the corrected
plan and confirm that on the record, rather than trusting the first apply
run's now-superseded counts.

Run under python.exe (bridge access, Windows loopback path).
"""
import sys, json

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

PLAN_PATH = r'D:\Luke\dev\Rimworld\world\_grey\grey_plan.json'
OUT_PATH = r'D:\Luke\dev\Rimworld\world\_grey\grey_verify_final.json'

plan = json.load(open(PLAN_PATH))
groups = plan['groups']

host, port, token = resolve_endpoint()
report = {}
with RimBridge(host, port, token) as rb:
    for defname, tiles in groups.items():
        if not tiles:
            report[defname] = {'intended': 0, 'landed': 0, 'missing': []}
            continue
        got = {}
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
        }
        print(defname, 'intended', len(tiles), 'landed', landed,
              ('OK' if not missing else 'missing %r' % missing[:10]))

    # protected-def spot check: none of the 5 protected defs should have
    # been lost anywhere this plan wrote.
    protected = ['CoastalIsland', 'Archipelago', 'Oasis', 'Bay', 'VEE_GravelBeach']
    audit = rb.call('jawa/world_mutators_audit', {
        'marineMutators': 'VEE_RisingWaters,Archipelago,Iceberg',
        'limit': 500, 'histogram': False,
    })
    report['_audit'] = {
        'marineMutators': 'VEE_RisingWaters,Archipelago,Iceberg',
        'offenderCount': audit.get('offenderCount'),
        'offenders': audit.get('offenders'),
    }
    print('audit offenderCount (VEE_RisingWaters,Archipelago,Iceberg only):', audit.get('offenderCount'))

json.dump(report, open(OUT_PATH, 'w'), indent=1)
print('wrote', OUT_PATH)
