#!/usr/bin/env python3
"""Bounded offline nursery combat source model; never launches the game.

Explicit installed-game and selected reflection-only IL inputs are mandatory.
XML inheritance handles only the selected scalar/named-child/list shapes. Output
is conditional source arithmetic, not loaded defs, actual hits or kill times.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time
import xml.etree.ElementTree as ET

SEA = 'src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml'
MOTHER = 'src/RimMandrake/Miasma/Defs/ThingDefs_Races/RM_WardenMother.xml'
MIASMA = 'src/RimMandrake/Miasma/Defs/BiomeDefs/RM_Miasma.xml'
GREY = 'src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml'
IDS = ('RM_ReefbackJuv', 'RM_Reefback', 'RM_WardenMother')
CORE_INPUTS = (
    'Data/Core/Defs/Misc/LifeStageDefs/LifeStages.xml',
    'Data/Core/Defs/ThingDefs_Races/Races_Animal_Base.xml',
    'Data/Core/Defs/Bodies/BodyParts_General.xml',
    'Data/Core/Defs/Bodies/BodyParts_Animal.xml',
    'Data/Core/Defs/Bodies/BodyParts_Organs.xml',
    'Data/Odyssey/Defs/Bodies/Bodies_Animal_Pinniped.xml',
)
EXCLUDE = {'FlowWorks', 'GSS', 'GimmeSomeSlack', 'GravShipSystems', 'obj', 'bin', 'art_source'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def merge(parent, child):
    """Selected XmlInheritance shapes; list entries append unless replaced."""
    result = copy.deepcopy(parent)
    result.attrib = {k: v for k, v in child.attrib.items() if k != 'Inherit'}
    if child.get('Inherit', '').lower() == 'false' or not len(child):
        result[:] = copy.deepcopy(list(child))
        result.text = child.text
    else:
        for node in child:
            old = result.find(node.tag)
            if node.tag == 'li' or old is None:
                result.append(copy.deepcopy(node))
            else:
                result[list(result).index(old)] = merge(old, node)
    return result


def resolve(node, named, stack=()):
    parent = node.get('ParentName')
    if not parent:
        return copy.deepcopy(node)
    if parent in stack:
        raise ValueError('cyclic parent: ' + parent)
    if parent not in named:
        raise ValueError('missing parent: ' + parent)
    return merge(resolve(named[parent], named, stack + (parent,)), node)


def stage_rows(race, stages, parts):
    rows = []
    for stage in race.findall('race/lifeStageAges/li'):
        name = stage.findtext('def')
        node = stages[name]
        factors = {field: float(node.findtext(field, '1'))
                   for field in ('bodySizeFactor', 'healthScaleFactor', 'meleeDamageFactor')}
        size = float(race.findtext('race/baseBodySize'))
        health = float(race.findtext('race/baseHealthScale'))
        health32 = f32(f32(health) * f32(factors['healthScaleFactor']))
        rows.append({
            'stage': name, 'minAge_xml': float(stage.findtext('minAge')),
            'factors': factors,
            'factor_provenance': {k: ('LifeStageDef XML/' + name + '/' + k
                                     if node.find(k) is not None else 'LifeStageDef constructor IL default 1')
                                  for k in factors},
            'bodySize_decimal': size * factors['bodySizeFactor'],
            'bodySize_float32': f32(f32(size) * f32(factors['bodySizeFactor'])),
            'healthScale_decimal': health * factors['healthScaleFactor'],
            'healthScale_float32': health32,
            'part_max_health': {p: math.ceil(f32(f32(hp) * health32)) for p, hp in parts.items()},
            'tools': [{'label': t.findtext('label'), 'power_xml': float(t.findtext('power')),
                       'cooldown_xml_seconds': float(t.findtext('cooldownTime')),
                       'chanceFactor_xml': t.findtext('chanceFactor', '1'),
                       'linked_group': t.findtext('linkedBodyPartsGroup'),
                       'nominal_damage_decimal': float(t.findtext('power')) * factors['meleeDamageFactor'],
                       'nominal_damage_float32': f32(f32(float(t.findtext('power'))) * f32(factors['meleeDamageFactor']))}
                      for t in race.findall('tools/li')],
        })
    return rows


def hunting(rows, armor):
    # Stipulated before tuning in independent design_prompt.txt. Even damage12
    # halves to6 exactly, so the armor branch's RoundRandom adds no error here.
    residual = max(armor - 0.15, 0)
    if not 0 <= residual <= 1:
        raise ValueError('hunting model only supports residual armor in [0,1]')
    remaining = 1 - 0.75 * residual
    dps = 2 * 12 * 0.60 / 3 * remaining
    return [{'stage': r['stage'], 'sharp_armor': armor, 'residual_armor': residual,
             'deflect_probability_given_hit': residual / 2,
             'half_damage_probability_given_hit': residual / 2,
             'full_damage_probability_given_hit': 1 - residual,
             'expected_damage_per_landed_hit': 12 * remaining,
             'team_expected_damage_per_second': dps,
             'expected_damage_30_seconds': dps * 30,
             'body_part_budget': r['part_max_health']['Body'],
             'body_part_budget_over_expected_DPS_seconds': r['part_max_health']['Body'] / dps}
            for r in rows]


def xpath_counts(selected, resolved, expressions, out):
    """Use .NET's XPath 1.0 reader, as the engine does; no game code runs.

    Windows PowerShell is found on PATH, never via a user/machine identity.
    The generated script reads only two selected documents and exact selectors.
    """
    powershell = shutil.which('powershell.exe')
    if not powershell:
        raise ValueError('powershell.exe on PATH required for offline .NET XPath audit')
    def windows(path):
        return subprocess.check_output(['wslpath', '-w', str(path.resolve())], text=True).strip()
    for name, node in [('xpath-raw.xml', selected), ('xpath-resolved.xml', resolved)]:
        ET.ElementTree(node).write(out/name, encoding='utf-8', xml_declaration=True)
    request = out/'xpath-request.json'
    request.write_text(json.dumps({'raw': windows(out/'xpath-raw.xml'),
        'resolved': windows(out/'xpath-resolved.xml'), 'expressions': sorted(expressions)}))
    script = out/'read-xpath.ps1'
    script.write_text('''param([string]$InputPath)
$ErrorActionPreference='Stop'
$r=Get-Content -Raw -LiteralPath $InputPath | ConvertFrom-Json
$raw=New-Object System.Xml.XmlDocument
$raw.Load($r.raw)
$resolved=New-Object System.Xml.XmlDocument
$resolved.Load($r.resolved)
$rows=@()
foreach($xp in $r.expressions){
 try {
  $rows += @{xpath=$xp;raw_hits=$raw.SelectNodes($xp).Count;resolved_hits=$resolved.SelectNodes($xp).Count}
 } catch { $rows += @{xpath=$xp;error=$_.Exception.Message} }
}
ConvertTo-Json -Depth 6 -Compress -InputObject @($rows)
''')
    cmd = [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', windows(script), '-InputPath', windows(request)]
    started = time.time()
    p = subprocess.run(cmd, capture_output=True, timeout=120)
    (out/'xpath.stdout.json').write_bytes(p.stdout)
    (out/'xpath.stderr.txt').write_bytes(p.stderr)
    (out/'xpath.receipt.json').write_text(json.dumps({'command': cmd, 'rc': p.returncode,
        'elapsed_seconds': time.time()-started, 'script_sha256':sha(script.read_bytes()),
        'stdout_sha256':sha(p.stdout), 'stderr_sha256':sha(p.stderr)}, indent=2)+'\n')
    if p.returncode:
        raise ValueError('offline XPath reader failed; see retained process streams')
    return {r['xpath']: r for r in json.loads(p.stdout.decode('utf-8-sig'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--game-dir', type=Path, required=True)
    parser.add_argument('--engine-il', type=Path, required=True)
    parser.add_argument('--baseline-root', type=Path, help='optional pre-edit source tree for direct comparison')
    parser.add_argument('--out', type=Path, required=True)
    a = parser.parse_args()
    repo, out = a.repo_root.resolve(), a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    snapshots = out / 'inputs'
    snapshots.mkdir(exist_ok=True)
    manifest = []

    def record(label, path, max_bytes=4_000_000):
        data = path.read_bytes()
        if len(data) > max_bytes:
            raise ValueError('oversized selected input: ' + label)
        dest = snapshots / label
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        manifest.append({'input': label, 'bytes': len(data), 'sha256': sha(data)})
        return data

    selected = ET.Element('Defs')
    definitions, named, stages, parts = {}, {}, {}, {}
    for rel in CORE_INPUTS:
        data = record('installed/' + rel, a.game_dir / rel)
        root = ET.fromstring(data)
        for n in root:
            name, identity = n.get('Name'), n.findtext('defName')
            wanted = name in ('BasePawn', 'AnimalThingBase', 'AnimalKindBase') or identity in (
                'AnimalBaby', 'AnimalJuvenile', 'AnimalAdult', 'Body', 'Brain', 'Heart', 'Pinniped')
            if not wanted:
                continue
            selected.append(copy.deepcopy(n))
            if name:
                named[name] = n
            if n.tag == 'LifeStageDef':
                stages[identity] = n
            if n.tag == 'BodyPartDef':
                parts[identity] = float(n.findtext('hitPoints'))
    for rel in (SEA, MOTHER):
        data = record(rel, repo / rel)
        for n in ET.fromstring(data):
            identity = n.findtext('defName')
            if identity not in (*IDS, 'RM_WardenMotherElder'):
                continue
            selected.append(copy.deepcopy(n))
            definitions[(n.tag, identity)] = n
            if n.get('Name'):
                named[n.get('Name')] = n
            if n.tag == 'LifeStageDef':
                stages[identity] = n
    il = record('engine-selected.il.txt', a.engine_il).decode('utf-8-sig')
    required = ('METHOD Verse.Pawn::get_HealthScale', 'Single healthScaleFactor', 'Single baseHealthScale',
                'METHOD Verse.BodyPartDef::GetMaxHealth', 'CeilToInt(Single)',
                'METHOD Verse.VerbProperties::GetDamageFactorFor', 'Single meleeDamageFactor',
                'StatDef MeleeDamageFactor', 'AdjustedBaseMeleeDamageAmount',
                'METHOD Verse.ArmorUtility::ApplyArmor', 'RoundRandom(Single)',
                'METHOD RimWorld.Verb_MeleeAttackDamage+<DamageInfosToApply>',
                'RecursiveNodeCopyOverwriteElements', '"Inherit"', '"false"')
    for fragment in required:
        if fragment not in il:
            raise ValueError('incomplete engine input: ' + fragment)
    constructor = il.split('METHOD RimWorld.LifeStageDef::.ctor', 1)[1].split('METHOD ', 1)[0]
    for field in ('bodySizeFactor', 'healthScaleFactor', 'meleeDamageFactor'):
        if not re.search(r'ldc.r4 1\s+IL_[0-9A-F]+: stfld RimWorld.LifeStageDef::Single ' + field, constructor):
            raise ValueError('unverified stage default: ' + field)
    for rel in ('Version.txt', 'RimWorldWin64_Data/Managed/Assembly-CSharp.dll'):
        p = a.game_dir / rel
        data = p.read_bytes()
        manifest.append({'input': 'installed/' + rel, 'bytes': len(data), 'sha256': sha(data)})
    resolved = ET.Element('Defs')
    result = {}
    for identity in IDS:
        race = resolve(definitions[('ThingDef', identity)], named)
        kind = resolve(definitions[('PawnKindDef', identity)], named)
        resolved.extend([copy.deepcopy(race), copy.deepcopy(kind)])
        rows = stage_rows(race, stages, parts)
        result[identity] = {
            'raw_parent': definitions[('ThingDef', identity)].get('ParentName'),
            'baseBodySize': float(race.findtext('race/baseBodySize')),
            'baseHealthScale': float(race.findtext('race/baseHealthScale')),
            'manhunterOnDamageChance': float(race.findtext('race/manhunterOnDamageChance')),
            'sharp_armor': float(race.findtext('statBases/ArmorRating_Sharp')),
            'blunt_armor': float(race.findtext('statBases/ArmorRating_Blunt')),
            'heat_armor': race.findtext('statBases/ArmorRating_Heat'),
            'stages': rows,
            'kind_stage_count': len(kind.find('lifeStages')),
            'kind_wildGroupSize': kind.findtext('wildGroupSize'),
            'kind_ecoSystemWeight': kind.findtext('ecoSystemWeight'),
            'kind_combatPower': kind.findtext('combatPower'),
            'kind_water_speed_factor': kind.findtext('moveSpeedFactorByTerrainTag/li/value'),
            'inherited_stats': {n.tag: n.text for n in race.find('statBases')},
            'race_fields': {field: race.findtext('race/' + field) for field in
                            ('body','leatherDef','waterSeeker','canBePredatorPrey','disableMating','manhunterOnDamageChance')},
            'comps': [ET.tostring(n,encoding='unicode') for n in race.findall('comps/li')],
            'hunting': hunting(rows, float(race.findtext('statBases/ArmorRating_Sharp'))),
        }
    biomes = {}
    for rel, identity in ((MIASMA, 'RM_Miasma'), (GREY, 'RM_GreySea')):
        data = record(rel, repo / rel)
        bd = next(n for n in ET.fromstring(data) if n.findtext('defName') == identity)
        biomes[identity] = {'animalDensity': bd.findtext('animalDensity'),
                            'wildAnimals': {n.tag: n.text for n in bd.find('wildAnimals')}}
    for rel in ('src/RimMandrake/Miasma/Defs/MapGeneration/RM_Miasma_CrecheScatterer.xml',
                'src/RimMandrake/Miasma/Patches/RM_AcousticPayload_Miasma.xml',
                'src/RimMandrake/EnvironmentalHazards/Source/RM_SetPieceElement_AnchoredPawn.cs',
                'src/RimMandrake/EnvironmentalHazards/Source/RM_CompTerritorialAnchor.cs',
                'src/RimMandrake/EnvironmentalHazards/Source/RM_CompWaterLocked.cs'):
        record(rel, repo / rel)

    controls = {}
    young = definitions[('ThingDef', IDS[0])]
    parent = resolve(definitions[('ThingDef', IDS[1])], named)
    for field in ('tools', 'race/lifeStageAges'):
        changed = copy.deepcopy(young)
        child = changed.find(field)
        if child is None:
            continue  # baseline has no local tools override
        child.attrib.pop('Inherit', None)
        mutated = merge(parent, changed)
        controls['without_replacement_' + field.replace('/', '_')] = {
            'fixture_xml': ET.tostring(changed, encoding='unicode'),
            'resolved_entries': [ET.tostring(n, encoding='unicode') for n in mutated.find(field)],
            'original_count': len(resolve(young, named).find(field)),
            'mutated_count': len(mutated.find(field)),
        }
    for field in ('tools', 'race/baseHealthScale', 'statBases/ArmorRating_Sharp'):
        changed = copy.deepcopy(young)
        path, _, leaf = field.rpartition('/')
        node = changed.find(field)
        if node is not None:
            (changed.find(path) if path else changed).remove(node)
        mutated = merge(parent, changed)
        rows = stage_rows(mutated, stages, parts)
        controls['removed_override_' + field.replace('/', '_')] = {
            'fixture_xml': ET.tostring(changed, encoding='unicode'), 'stages': rows,
            'sharp_armor': float(mutated.findtext('statBases/ArmorRating_Sharp')),
        }
    broken = copy.deepcopy(young)
    broken.set('ParentName', 'MISSING_REEFBACK_PARENT')
    try:
        resolve(broken, named)
        raise AssertionError('broken parent silently accepted')
    except ValueError as e:
        controls['broken_parent'] = {'fixture_xml': ET.tostring(broken, encoding='unicode'), 'exception': str(e)}
    yrows = result[IDS[0]]['stages']
    controls['omitted_factors'] = {
        'wrong_bodySize_as_healthScale': [r['bodySize_decimal'] for r in yrows],
        'wrong_bare_base_healthScale': result[IDS[0]]['baseHealthScale'],
        'wrong_unstaged_damage': [t['power_xml'] for t in yrows[0]['tools']],
        'correct_healthScale': [r['healthScale_decimal'] for r in yrows],
        'correct_damage': [[t['nominal_damage_decimal'] for t in r['tools']] for r in yrows],
        'wrong_part_max_health_without_race_multiplier': [math.ceil(40*r['factors']['healthScaleFactor']) for r in yrows],
        'wrong_part_max_health_without_stage_factor': math.ceil(40*result[IDS[0]]['baseHealthScale']),
    }
    changed_kind = copy.deepcopy(definitions[('PawnKindDef', IDS[0])])
    cp = changed_kind.find('combatPower')
    if cp is not None:
        changed_kind.remove(cp)
    controls['removed_combatPower_override'] = {
        'fixture_xml': ET.tostring(changed_kind, encoding='unicode'),
        'resolved_combatPower': resolve(changed_kind, named).findtext('combatPower')}
    changed_stats = copy.deepcopy(young)
    if changed_stats.find('statBases') is not None:
        changed_stats.find('statBases').set('Inherit','False')
        controls['statBases_replaced'] = {
            'fixture_xml': ET.tostring(changed_stats, encoding='unicode'),
            'resolved_statBases': ET.tostring(resolve(changed_stats,named).find('statBases'), encoding='unicode')}
    # Reverse search is only a stage-table sanity case, not engine age tracking.
    controls['final_stage_table_cases'] = [
        {'age_years': age, 'stage': next(r['stage'] for r in reversed(yrows) if age >= r['minAge_xml'])}
        for age in (0, .099, .1, .6, 25, 50, 499, 500)]
    controls['armor_boundaries'] = [{'armor': armor, 'rows': hunting(yrows, armor)} for armor in (0, .15, 1.15)]
    baseline = {}
    if a.baseline_root:
        original = ET.fromstring(record('before/' + SEA, a.baseline_root / SEA))
        bnamed = dict(named)
        for n in original:
            if n.get('Name') and n.findtext('defName') in IDS:
                bnamed[n.get('Name')] = n
        for identity in IDS[:2]:
            node = next(n for n in original if n.tag == 'ThingDef' and n.findtext('defName') == identity)
            race = resolve(node, bnamed)
            rows = stage_rows(race, stages, parts)
            baseline[identity] = {'stages': rows, 'hunting': hunting(rows, float(race.findtext('statBases/ArmorRating_Sharp')))}
        for rel in (MOTHER, MIASMA, GREY):
            before = record('before/' + rel, a.baseline_root / rel)
            baseline[rel] = {'before_sha256': sha(before), 'current_sha256': sha((repo/rel).read_bytes())}
        current_root = ET.parse(repo/SEA).getroot()
        diffs = []
        for n, b in zip(current_root, original):
            if ET.tostring(n) != ET.tostring(b):
                diffs.append({'tag': n.tag, 'defName': n.findtext('defName')})
        controls['changed_XML_nodes'] = {'before_count': len(original), 'current_count': len(current_root), 'different_nodes': diffs}

    # Audit selectors against both pre-inheritance and resolved selected nodes.
    # Full files are hashed; only matched operation fields are retained. This
    # excludes prohibited lanes and external mods; it is not post-patch loading.
    audit = {'scope': 'src/**/Patches/*.xml outside excluded lanes; selected raw/resolved XML only',
             'excluded': sorted(EXCLUDE), 'files': [], 'operations': [], 'xpath_errors': []}
    tokens = ('Reefback', 'WardenMother', 'AnimalBaby', 'AnimalJuvenile', 'AnimalAdult',
              'AnimalThingBase', 'BasePawn', 'AnimalKindBase', 'Pinniped')
    operations = []
    for p in sorted((repo/'src').rglob('*.xml')):
        if 'Patches' not in p.parts or any(x in EXCLUDE for x in p.parts):
            continue
        if p.stat().st_size > 64_000_000:
            raise ValueError('patch exceeds 64MB bound: ' + str(p))
        data = p.read_bytes()
        rel = p.relative_to(repo).as_posix()
        audit['files'].append({'file': rel, 'bytes': len(data), 'sha256': sha(data)})
        for _, n in ET.iterparse(p, events=('end',)):
            xp = n.findtext('xpath')
            if xp is None:
                continue
            xp = xp.strip()
            value = n.find('value')
            value_text = ET.tostring(value, encoding='unicode') if value is not None else ''
            operations.append({'file': rel, 'class': n.get('Class'), 'xpath': xp,
                               'value': value_text, 'attribute': n.findtext('attribute')})
            n.clear()
    counts = xpath_counts(selected, resolved, {r['xpath'] for r in operations}, out)
    for row in operations:
        hits = counts[row['xpath']]
        if 'error' in hits:
            audit['xpath_errors'].append(dict(file=row['file'], **hits))
        if hits.get('raw_hits',0) or hits.get('resolved_hits',0) or any(t in row['xpath']+row['value'] for t in tokens):
            audit['operations'].append(dict(row, **{k:v for k,v in hits.items() if k!='xpath'}))
    # Bound local Harmony consumer audit to exact relevant terms; retain source
    # context, never infer the state of external patches or an installed mod list.
    consumer_terms = re.compile(r'get_HealthScale|"HealthScale"|GetDamageFactorFor|AdjustedMeleeDamageAmount|meleeDamageFactor|healthScaleFactor|baseHealthScale|MeleeDamageFactor')
    audit['consumer_matches'] = []
    for p in sorted((repo/'src').rglob('*.cs')):
        if any(x in EXCLUDE for x in p.parts):
            continue
        if p.stat().st_size > 2_000_000:
            raise ValueError('C# input exceeds bound: ' + str(p))
        data = p.read_bytes()
        lines = data.decode('utf-8-sig').splitlines()
        matched = [i for i, line in enumerate(lines) if consumer_terms.search(line)]
        if matched:
            audit['consumer_matches'].append({'file': p.relative_to(repo).as_posix(), 'sha256': sha(data),
                'lines': [{'line': i+1, 'context': lines[max(0,i-3):i+4]} for i in matched]})

    for name, node in [('selected-source.xml', selected), ('resolved-source.xml', resolved)]:
        ET.indent(node)
        ET.ElementTree(node).write(out/name, encoding='utf-8', xml_declaration=True)
    record('instrument.py', Path(__file__))
    for name, value in [('measurement.json', {'species': result, 'biomes': biomes,
            'part_base_hitPoints': parts,
            'hunting_inputs': {'hunters': 2, 'damage': 12, 'AP': .15, 'cycle_seconds': 3, 'hit_probability': .6, 'window_seconds': 30},
            'assumptions': ['healthy natural linked parts; MeleeDamageFactor stat=1; no equipment/hediffs/genes/settings modifiers',
                'naked targets; natural armor only; nominal damage is before target armor',
                'Body is a shared part budget, not a whole-pawn hitpoint pool or predicted time to kill',
                'fixed hit probability and firing cadence; no range/pathing/retaliation or survival simulated',
                'selected XML and installed unpatched engine; no claim about external mods or loaded pawns']}),
            ('controls.json', controls), ('baseline.json', baseline), ('patch-audit.json', audit), ('inputs.json', manifest)]:
        (out/name).write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps({'species': {k: [{'stage': r['stage'], 'healthScale': r['healthScale_decimal'],
        'Body_maxHP': r['part_max_health']['Body'], 'damage': [t['nominal_damage_decimal'] for t in r['tools']]}
        for r in v['stages']] for k,v in result.items()}, 'audited_patch_files': len(audit['files']),
        'matched_operations': len(audit['operations']), 'xpath_errors': len(audit['xpath_errors'])}, indent=2))


if __name__ == '__main__':
    main()
