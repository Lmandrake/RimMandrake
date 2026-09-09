#!/usr/bin/env python3
"""Validate roster JSONs (rosters/*.json) against _SCHEMA.md's rules.

Gate for the build lane: every file must pass before any generator consumes it.
Checks: JSON shape, defName existence (register for fauna, plant_pool.csv for
flora, case-exact), ruled bans (GRim*, the Earth five, Blizzarisk, mechanoid/
entity kinds), intra-file duplicates, numeric commonalities.

Exit 0 = all listed files pass; nonzero = problems printed, one per line.
A defName absent from the register is an ERROR unless the same def appears in
the file's new_defs (then it is a WARNING: authored-later def).
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
REGISTER = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'review',
                        'creature_register_rows.json')
PLANT_POOL = os.path.join(ROOT, 'design', 'Jawa', 'mods', 'plant_pool.csv')

EARTH_FIVE = {'Rat', 'Hare', 'WildBoar', 'Raccoon', 'Warg'}
RULED_CUTS = {'AA_Blizzarisk', 'AA_BlizzariskClutchMother'}  # freeze R20
PAINTED_DEFS = {
    'Desert', 'ExtremeDesert', 'AB_PropaneLakes', 'AB_MycoticJungle',
    'RUT_NightsideIce', 'AB_RockyCrags', 'Wasteland', 'BiomeGRimond',
    'ZBiome_Badlands', 'AridShrubland', 'PoisonForest', 'RUT_TwilightSea',
    'RUT_GreySea', 'RUT_TheScald', 'AB_MechanoidIntrusion', 'BiomeCypreJungle',
    'ZBiome_DesertOasis', 'ZBiome_Grasslands', 'AB_OcularForest',
    'AB_FeraliskInfestedJungle', 'AB_GelatinousSuperorganism',
    'AB_MiasmicMangrove', 'Scarlands', 'RUT_PropaneLake',
    'COMIGO_GreaterSwamp_Tropical', 'AB_TarPits', 'AB_PyroclasticConflagration',
    'LavaField', 'Volcano',
    # pending-switch targets a roster may legitimately name
    'RUT_BlueDesert',
}
REQUIRED_KEYS = {'sheet', 'defNames', 'fauna', 'evictions', 'flora', 'fish'}
# prep §9's 25 homogenizers — the owner-accepted ≤2-home trim binds THESE rows;
# other creatures get a zoo-effect warning at ≥4 homes, never an error.
UBIQUITY_25 = {
    'AA_PebbleMit', 'AA_FissionMouse', 'AA_Swarmling', 'AA_Aerofleet',
    'AA_CrystalMit', 'AA_MegaLouse', 'AA_AnimusVox', 'AA_LuciferBug',
    'AA_Bumbledrone', 'AA_AcanthamoebaGigantea', 'AA_PedigreedRaptor',
    'Boomalope', 'Rat', 'GraniteSlug', 'WildBoar', 'Warg', 'AA_Murkling',
    'Mynock', 'Hare', 'AA_AuroraSylph', 'AA_Drainer', 'Raccoon', 'Muffalo',
    'Neebray', 'Scavrat',
}


def load_register():
    with open(REGISTER) as f:
        rows = json.load(f)['rows']
    return {r['defName'] for r in rows if 'defName' in r}


def load_plants():
    with open(PLANT_POOL) as f:
        return {r['defName'] for r in csv.DictReader(f)}


def check(path, reg, plants):
    problems = []
    warnings = []
    name = os.path.basename(path)
    try:
        with open(path) as f:
            d = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return [f'{name}: UNREADABLE — {e}'], []

    missing = REQUIRED_KEYS - set(d)
    if missing:
        problems.append(f'{name}: missing keys {sorted(missing)}')
        return problems, warnings

    new_def_names = {nd.get('name', '') for nd in d.get('new_defs', [])}
    for dn in d.get('defNames', []):
        if dn not in PAINTED_DEFS:
            problems.append(f'{name}: defNames entry {dn!r} is not a painted/pending biome def')

    seen = set()
    for row in d.get('fauna', []):
        dn = row.get('def', '')
        if dn in seen:
            problems.append(f'{name}: duplicate fauna def {dn}')
        seen.add(dn)
        if dn.startswith('GRim'):
            problems.append(f'{name}: {dn} is Grindterra (GRim*) — homeless by owner ruling')
        if dn in EARTH_FIVE:
            # prep §9 carve-out: Rat is trimmed TO the Fall Line/settlements, not banned there
            if not (dn == 'Rat' and name == 'fall_line.json'):
                problems.append(f'{name}: {dn} is one of the Earth five — banned planet-wide')
        if dn in RULED_CUTS:
            problems.append(f'{name}: {dn} is cut by freeze R20')
        if dn not in reg:
            if dn in new_def_names:
                warnings.append(f'{name}: fauna {dn} not in register (declared in new_defs)')
            else:
                problems.append(f'{name}: fauna def {dn!r} not in the creature register (exact case)')
        c = row.get('commonality')
        if not isinstance(c, (int, float)) or c < 0:
            problems.append(f'{name}: fauna {dn} commonality {c!r} not a non-negative number')
        if not row.get('law'):
            problems.append(f'{name}: fauna {dn} has no law citation')
    for row in d.get('evictions', []):
        dn = row.get('def', '')
        if dn and dn not in reg and dn not in new_def_names:
            warnings.append(f'{name}: eviction def {dn!r} not in register (typo, or already gone?)')
        if not row.get('reason'):
            problems.append(f'{name}: eviction {dn} has no reason')
    for row in d.get('flora', []):
        pn = row.get('def', '')
        if pn not in plants:
            if pn in new_def_names:
                warnings.append(f'{name}: flora {pn} not in plant_pool (declared in new_defs)')
            else:
                problems.append(f'{name}: flora def {pn!r} not in plant_pool.csv (exact case)')
    # `flora_def_exclusions` — a roster covering several BiomeDefs may rule that one of
    # them grows nothing (the_propane_lakes: the fuel-snow shore has crystal flora, the
    # liquid-propane sea has none). It must name a def this file actually claims, and it
    # must carry a reason, or it is a silent no-op.
    for row in d.get('flora_def_exclusions', []):
        dn = row.get('def', '')
        if dn not in d.get('defNames', []):
            problems.append(f'{name}: flora_def_exclusions names {dn!r}, which is not in '
                            f'this file\'s defNames — it would exclude nothing')
        if not row.get('reason'):
            problems.append(f'{name}: flora_def_exclusions {dn} has no reason')

    fish = d.get('fish')
    if not isinstance(fish, dict) or not fish.get('ruling'):
        problems.append(f'{name}: fish ruling missing')
    return problems, warnings


def cross_check(paths, reg):
    """Cross-file consistency: move-target pairing, >2-home ubiquity breaches,
    cut collection. Prints findings; returns problem count."""
    homes = {}          # def -> [sheet, ...]
    moves = []          # (from_sheet, def, target_defname)
    cuts = []           # (sheet, def, ruling)
    sheets_by_defname = {}
    data = {}
    for p in paths:
        try:
            with open(p) as f:
                d = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        data[d.get('sheet', os.path.basename(p))] = d
        # injection layers list the defs they inject OVER — they must not claim them
        if d.get('sheet') in ('fall_line', 'wreck_fields', 'the_lantern_deeps'):
            continue
        for dn in d.get('defNames', []):
            sheets_by_defname[dn] = d.get('sheet')
    exceptions = {}     # def -> [(sheet, reason), ...]
    for sheet, d in data.items():
        injection = sheet in ('fall_line', 'wreck_fields', 'the_lantern_deeps')
        for row in d.get('fauna', []):
            homes.setdefault(row.get('def', ''), []).append(
                sheet + (' (injection)' if injection else ''))
            if row.get('ubiquity_exception'):
                exceptions.setdefault(row.get('def', ''), []).append(
                    (sheet, row['ubiquity_exception']))
        for row in d.get('evictions', []):
            disp = row.get('disposition', '') or ''
            if disp.startswith('move:'):
                target = disp[5:].strip().split('(')[0].strip()
                moves.append((sheet, row.get('def', ''), target))
            if disp.startswith('cut:'):
                cuts.append((sheet, row.get('def', ''), disp[4:].strip()))
    problems = 0
    for sheet, dn, target in moves:
        tsheet = sheets_by_defname.get(target)
        target_d = data.get(tsheet) if tsheet else data.get(target)
        if target_d is None:
            print(f'⚠️  cross: {sheet} moves {dn} -> {target}: target roster file not loaded')
            continue
        if dn not in {r.get('def') for r in target_d.get('fauna', [])}:
            print(f'🔴 cross: {sheet} evicts {dn} as move:{target}, but '
                  f'{target_d.get("sheet")} does not roster it')
            problems += 1
    for dn, hs in sorted(homes.items()):
        real = [h for h in hs if not h.endswith('(injection)')]
        n_exempt = len(exceptions.get(dn, []))
        if dn in UBIQUITY_25 and len(real) - n_exempt > 2:
            print(f'🔴 cross: {dn} (ubiquity-25) has {len(real)} home biomes {real} '
                  f'({n_exempt} excepted) — the owner-accepted trim is ≤2')
            problems += 1
        elif dn not in UBIQUITY_25 and len(real) >= 4:
            print(f'⚠️  cross: {dn} has {len(real)} home biomes {real} — zoo-effect watch (review-sheet material, not an error)')
    if cuts:
        print(f'ℹ️  cross: {len(cuts)} cut dispositions collected for _global.json:')
        for sheet, dn, ruling in sorted(cuts):
            print(f'   cut {dn} ({sheet}; {ruling})')
    return problems


def main(paths):
    reg = load_register()
    plants = load_plants()
    total_p = 0
    for p in paths:
        problems, warnings = check(p, reg, plants)
        for w in warnings:
            print(f'⚠️  {w}')
        for pr in problems:
            print(f'🔴 {pr}')
        total_p += len(problems)
        if not problems:
            print(f'✅ {os.path.basename(p)}: OK ({len(warnings)} warning(s))')
    return 1 if total_p else 0


if __name__ == '__main__':
    args = sys.argv[1:]
    do_cross = '--cross' in args
    args = [a for a in args if a != '--cross']
    if not args:
        args = sorted(
            os.path.join(HERE, f) for f in os.listdir(HERE)
            if f.endswith('.json') and not f.startswith('_')
        )
    rc = main(args)
    if do_cross:
        if cross_check(args, load_register()):
            rc = 1
    sys.exit(rc)
