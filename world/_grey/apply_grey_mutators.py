"""
Apply the Grey Sea's 18 mutator writes (passes 2, 4, 5 of world/_grey/BRIEF.md)
from grey_plan.json to the live planet, verify every intended tile by reading
it back, and run the marine-mutator audit restricted to genuinely coastal-
gated defs only.

WHY a script and not one-off calls: 18 distinct (def -> tile-list) writes, each
needing exactly one jawa/world_mutators_set call, followed by exactly ONE
jawa/world_commit at the end (never per-write - world-authoring.md's "the order
the engine forces"). Keeping it as a script makes the whole batch reproducible
from grey_plan.json without re-deriving tile lists by hand, and keeps the
verify step (read every intended tile back, never trust "added: N") in the
same run as the writes.

MUST run under python.exe (Windows loopback; python3 in WSL2 cannot reach the
bridge). Reads/writes Windows paths for the same reason.

Traps hit while writing this:
  - jawa/world_mutators_set takes ONE def-list applied to ONE tile-list per
    call and does not accept a tile->mutator dict, so the plan stays grouped
    by def (18 calls), never by tile.
  - AddMutator silently no-ops if the tile already carries that exact def, and
    silently displaces a same-category sibling if it carries one - neither is
    visible in the "added" counter, which is why the verify step below reads
    every intended tile back individually rather than trusting the write
    response.
  - jawa/world_mutators_audit's `marineMutators` parameter is a loaded gun: it
    is a plain string match against every mutator on the planet with NO check
    that the def you name is actually coastline-gated. The Twilight incident
    (see design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md) happened
    because VEE_SaltPlains - not coastal-gated at all - was put in that list
    and flagged 313 unrelated inland placements, 50 of which were then
    auto-removed before anyone noticed. This script passes ONLY the defs this
    plan itself gates on real coastline ranges: VEE_RisingWaters, Archipelago,
    Iceberg. It never runs an auto-remove loop - offenderCount is reported,
    nothing is deleted based on it.
  - The whole-planet BEFORE snapshot was taken separately by
    harvest_planet_mutators.py before this script ever ran (planet_mutators_
    before.json) - this script does not re-take it, to guarantee the BEFORE
    reading was captured before the very first write of the session, not
    "before this script's writes" which could already be too late if another
    write had happened in between.
  - This first run's own VEE_RisingWaters pool (flat_shore - has_landmark,
    nothing else) displaced 12 pre-existing CoastalIsland + 4 Archipelago
    tiles - a protected-def violation caught by the whole-planet diff, not by
    this script's own per-def verify (which reported 100% landed, exactly the
    failure mode the task brief warned about). Fixed live with a direct
    remove+re-add on those 16 tiles, and fixed at the source in
    plan_grey_mutators.py (PROTECTED_DEFS exclusion) so grey_plan.json now
    already reflects the corrected, smaller VEE_RisingWaters/Coast/Archipelago
    pools. grey_apply_report.json below is this FIRST run's numbers (kept as
    the historical record of the bug); verify_grey_mutators.py +
    grey_verify_final.json are the authoritative final check against the
    corrected plan and the live-fixed planet.
  - A SECOND agent was independently working this exact BRIEF.md on the same
    live planet during this session (evidenced by files under this same
    directory with different naming conventions - _bridge_check.py,
    repair_grey_protected.py - the latter fixing the identical 12+4 protected-
    def displacement independently). No coordination between agents is
    possible (project rule: agents do not message each other), so this script
    was verified against a fresh whole-planet read taken immediately before
    finishing, not against any cached "after" file, precisely because a
    concurrent writer could have changed the ground truth between runs.
"""
import sys, json

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

PLAN_PATH = r'D:\Luke\dev\Rimworld\world\_grey\grey_plan.json'
REPORT_PATH = r'D:\Luke\dev\Rimworld\world\_grey\grey_apply_report.json'

plan = json.load(open(PLAN_PATH))
groups = plan['groups']

report = {'writes': [], 'verify': {}}

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:

    def set_mut(defname, tiles, note):
        if not tiles:
            report['writes'].append({'def': defname, 'note': note, 'intended': 0, 'skipped': True})
            print(defname, 'SKIPPED (0 eligible tiles) -', note)
            return
        r = rb.call('jawa/world_mutators_set', {
            'action': 'add',
            'mutators': defname,
            'tiles': ','.join(str(t) for t in tiles),
            'readBack': 0,
        })
        row = {
            'def': defname, 'note': note, 'intended': len(tiles),
            'success': r.get('success'), 'added': r.get('added'), 'removed': r.get('removed'),
            'unknownDefs': r.get('unknownDefs'), 'errors': r.get('errors'),
        }
        report['writes'].append(row)
        print(json.dumps(row)[:300])

    # ---- PASS 2: THE JUNKER COAST ----
    set_mut('Junkyard', groups['Junkyard'],
             'low_shore (hilliness<=SmallHills) minus has_landmark, weighted toward near_junk')
    set_mut('AncientRuins', groups['AncientRuins'],
             'ring minus has_landmark minus Junkyard tiles (no AB_MechanoidIntrusion biome present)')
    set_mut('AncientWarehouse', groups['AncientWarehouse'],
             'ring biome AridShrubland/Desert only, minus has_landmark/Junkyard/AncientRuins')
    set_mut('Stockpile', groups['Stockpile'],
             'low_shore minus has_landmark minus the 7 tiles that already had it, weighted toward near_junk')
    set_mut('VEE_MineralDevoid', groups['VEE_MineralDevoid'],
             'ring minus has_landmark minus the 8 tiles that already had it')
    set_mut('VEE_DeepOreDevoid', groups['VEE_DeepOreDevoid'],
             'identical hash gate to VEE_MineralDevoid so the pair stays co-located, as the existing 8 already are')

    # ---- PASS 4: THE WADING SEA ----
    set_mut('VEE_RisingWaters', groups['VEE_RisingWaters'],
             'flat_shore (hilliness Flat, coastline 1-5) minus has_landmark')
    set_mut('Coast', groups['Coast'],
             'ring minus has_landmark minus the 43 tiles that already had it')
    set_mut('Archipelago', groups['Archipelago'],
             'ring coastline 2-5, river_count 0, biome measured off the 11 tiles already live '
             '(AridShrubland/Desert/ZBiome_Badlands/Wasteland only), minus VEE_RisingWaters selection')
    set_mut('AnimalHabitat', groups['AnimalHabitat'],
             'body tiles at shore-distance 1-2, gradient-weighted (60% at d1, 35% at d2), minus existing holders')
    set_mut('Fish_Increased', groups['Fish_Increased'],
             'union of the d1-d2 gradient set and the mouth+fan set from pass 5')

    # ---- PASS 5: THE FOUR MOUTHS AND THE COLD END ----
    set_mut('RiverDelta', groups['RiverDelta'],
             'the 4 mouths minus 16898 (has_landmark - HARD RULE overrides the brief\'s literal list)')
    set_mut('AnimalLife_Increased', groups['AnimalLife_Increased'],
             'mouths (minus 16898) union the 5 water tiles adjacent to a mouth')
    set_mut('VEE_AlluvialFan', groups['VEE_AlluvialFan'],
             'measured: only tile 11503 is Flat among the 4 mouths and no Flat ring neighbour exists for the other 3')
    set_mut('Iceberg', groups['Iceberg'],
             'iceedge tiles at or below 0C only (26 of 52 iceedge tiles run above 0C and are excluded by the temp gate)')
    set_mut('IceDunes', groups['IceDunes'],
             'ice core (ice minus iceedge), even-hash-parity half, hilliness Flat confirmed on all 91 ice tiles')
    set_mut('VEE_DeepSnow', groups['VEE_DeepSnow'],
             'ice core, odd-hash-parity half (disjoint from IceDunes by construction)')
    set_mut('WindyMutator', groups['WindyMutator'],
             'all ice tiles union the colder half (arc>=90) of arid/desert ring tiles, minus existing holders')

    commit = rb.call('jawa/world_commit', {})
    print('world_commit:', json.dumps({k: v for k, v in commit.items() if k != 'operation'})[:200])
    report['commit'] = commit.get('success')

    # ---- per-def verify: read back every intended tile ----
    for defname, tiles in groups.items():
        if not tiles:
            report['verify'][defname] = {'intended': 0, 'landed': 0, 'missing': []}
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
        report['verify'][defname] = {
            'intended': len(tiles), 'landed': landed, 'missing': missing,
            'rowsReturned': r.get('count'), 'requestErrors': r.get('errors'),
        }
        print(defname, 'intended', len(tiles), 'landed', landed, 'missing', missing[:10])

    # ---- audit, restricted to defs this plan actually coastline-gates ----
    audit = rb.call('jawa/world_mutators_audit', {
        'marineMutators': 'VEE_RisingWaters,Archipelago,Iceberg',
        'limit': 500, 'histogram': False,
    })
    report['audit'] = {
        'marineMutators': 'VEE_RisingWaters,Archipelago,Iceberg',
        'offenderCount': audit.get('offenderCount'),
        'offenders': audit.get('offenders'),
    }
    print('audit offenderCount (VEE_RisingWaters,Archipelago,Iceberg only):', audit.get('offenderCount'))

json.dump(report, open(REPORT_PATH, 'w'), indent=1)
print('wrote', REPORT_PATH)
