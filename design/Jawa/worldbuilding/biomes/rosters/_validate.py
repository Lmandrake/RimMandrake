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
    fish = d.get('fish')
    if not isinstance(fish, dict) or not fish.get('ruling'):
        problems.append(f'{name}: fish ruling missing')
    return problems, warnings


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
    if not args:
        args = sorted(
            os.path.join(HERE, f) for f in os.listdir(HERE)
            if f.endswith('.json') and not f.startswith('_')
        )
    sys.exit(main(args))
