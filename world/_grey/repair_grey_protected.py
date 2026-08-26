"""
Restore 12 CoastalIsland + 4 Archipelago mutators that the Grey Sea VEE_RisingWaters
write silently displaced - the exact collateral-damage class the task brief warned
about ("the mistake the last two agents made"), caught here by the whole-planet
before/after diff (harvest_planet_mutators.py 'before'/'after' + the diff computed
against _planet_mutators_before.json, which was taken before ANY write this session).

Root cause, confirmed per-tile: VEE_RisingWaters shares a mutator CATEGORY with
CoastalIsland/Archipelago (same family AddMutator resolves conflicts within - this
matches the Twilight Sea incident's own finding, "VEE_RisingWaters<->CoastalAtoll<->
Bay", referenced in this session's concurrently-written apply_grey_mutators.py). The
Grey Sea plan's VEE_RisingWaters candidate pool (flat_shore minus has_landmark) did
NOT also exclude tiles already carrying a protected mutator, so AddMutator silently
won the category conflict on 16 tiles:
  CoastalIsland lost: 2250, 5112, 6645, 8714, 8715, 8717, 8719, 9974, 11505, 14753,
                       6658, 8904  (12 - two of these, 6658/8904, also lost Peninsula,
                       both are the SAME category-conflict event, not two incidents)
  Archipelago lost:   5096, 6661, 11502, 11523  (4)

Fix: AddMutator the protected def back onto each tile. Per BRIEF.md, that IS the
correct outcome (protected mutators outrank the pass; a write that would displace
one should have picked a different tile) - so restoring it is expected to remove
VEE_RisingWaters from these 16 tiles again via the same category-conflict mechanism,
which is correct: VEE_RisingWaters should never have landed there.

⚠️ Separately, 6658 and 8904 lost Peninsula (not a protected family) to the same
session's Archipelago write - that is a legitimate category-conflict displacement
(BRIEF.md "category conflicts are the system working") and is NOT touched here;
Peninsula is not in the protected list, only CoastalIsland/Archipelago/Oasis/Bay/
VEE_GravelBeach are.

MUST run under python.exe. Read/write Windows paths for bridge access.
"""
import sys, json

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

REPAIR = {
    'CoastalIsland': [2250, 5112, 6645, 8714, 8715, 8717, 8719, 9974, 11505, 14753, 14755, 16894],
    'Archipelago': [5096, 6661, 11502, 11523],
}
REPORT_PATH = r'D:\Luke\dev\Rimworld\world\_grey\grey_repair_report.json'

report = {'writes': [], 'verify': {}}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for defname, tiles in REPAIR.items():
        r = rb.call('jawa/world_mutators_set', {
            'action': 'add', 'mutators': defname,
            'tiles': ','.join(str(t) for t in tiles), 'readBack': 0,
        })
        row = {'def': defname, 'intended': len(tiles), 'success': r.get('success'),
               'added': r.get('added'), 'errors': r.get('errors')}
        report['writes'].append(row)
        print(json.dumps(row))

    rb.call('jawa/world_commit', {})
    print('committed repair')

    for defname, tiles in REPAIR.items():
        r = rb.call('jawa/world_mutators_get', {'tiles': ','.join(str(t) for t in tiles), 'limit': len(tiles) + 5})
        got = {row['tile']: set(m['def'] for m in row['mutators'] if m.get('def')) for row in r.get('tiles', [])}
        missing = [t for t in tiles if defname not in got.get(t, set())]
        still_has_rising = [t for t in tiles if 'VEE_RisingWaters' in got.get(t, set())]
        report['verify'][defname] = {
            'intended': len(tiles), 'landed': len(tiles) - len(missing), 'missing': missing,
            'still_carries_VEE_RisingWaters': still_has_rising,
        }
        print(defname, 'landed', len(tiles) - len(missing), 'missing', missing,
              'still has VEE_RisingWaters (should be empty):', still_has_rising)

json.dump(report, open(REPORT_PATH, 'w'), indent=1)
print('wrote', REPORT_PATH)
