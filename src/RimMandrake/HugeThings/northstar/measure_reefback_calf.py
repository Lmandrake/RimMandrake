#!/usr/bin/env python3
"""Bounded, offline reefback source measurement. No game, dump, network or build.

Inputs are explicit: repository, installed game directory, selected engine IL receipt,
and optionally a Core archive. Only two exact Core XML members are read from tar;
no archive is extracted. The small inheritance resolver handles the selected XML
shapes only (scalar overwrite, named children, li append, Inherit=False replacement).
It is not a general RimWorld loader or a measurement of a running pawn.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tarfile
import xml.etree.ElementTree as ET

SEA = 'src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_SeaBeasts_Invented.xml'
MIASMA = 'src/RimMandrake/Miasma/Defs/BiomeDefs/RM_Miasma.xml'
GREY = 'src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml'
MOTHER = 'src/RimMandrake/Miasma/Defs/ThingDefs_Races/RM_WardenMother.xml'
HT = 'src/RimMandrake/HugeThings/'
CORE = ('Defs/Misc/LifeStageDefs/LifeStages.xml',
        'Defs/ThingDefs_Races/Races_Animal_Base.xml')
SKIP = {'FlowWorks', 'GSS', 'GravShipSystems', 'obj', 'bin', 'art_source'}
TOKENS = ('Reefback', 'AnimalBaby', 'AnimalJuvenile', 'AnimalAdult',
          'AnimalThingBase', 'AnimalKindBase', 'BasePawn', 'baseBodySize',
          'bodySizeFactor', 'lifeStageAges', 'forceEnabled', 'RM_TitanicTier',
          'ageGenerationCurve', 'lifeExpectancy', 'minGenerationAge', 'maxGenerationAge')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def f32(v):
    return struct.unpack('<f', struct.pack('<f', v))[0]


def merge(parent, child):
    """Selected shapes, following XmlInheritance. Never sort a stage list."""
    result = copy.deepcopy(parent)
    # RecursiveNodeCopyOverwriteElements removes parent attributes and copies
    # child attributes except Inherit. Name/Abstract must not leak into a child.
    result.attrib = {k:v for k,v in child.attrib.items() if k != 'Inherit'}
    if child.get('Inherit', '').lower() == 'false':
        result[:] = copy.deepcopy(list(child))
        result.text = child.text
    elif not len(child):
        result[:] = []
        result.text = child.text
    else:
        for node in child:
            existing = result.find(node.tag)
            if node.tag == 'li' or existing is None:
                result.append(copy.deepcopy(node))
            else:
                result[list(result).index(existing)] = merge(existing, node)
    return result


def tier(size, floors):
    return next((n for n in (3, 2, 1) if size >= floors[n-1]), 0)


def event_eligible(adult_tier, opted_out, sea_creature, sea_map, has_list, on_list, homed_here, season_ok, t3_on_map):
    """Source-model evaluation of the selected RM_TitanicKernel predicate."""
    if opted_out or adult_tier < 2 or sea_creature != sea_map or not season_ok:
        return False
    if not (on_list if has_list else homed_here):
        return False
    return not (adult_tier == 3 and t3_on_map)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[4])
    ap.add_argument('--game-dir', type=Path, required=True, help='Linux path to installed RimWorld')
    ap.add_argument('--engine-il', type=Path, required=True, help='read_engine.ps1 selected IL output')
    ap.add_argument('--core-archive', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    repo, out = a.repo_root.resolve(), a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    snapshots = out / 'snapshots'
    snapshots.mkdir(exist_ok=True)
    manifest = []
    selections = ET.Element('SelectedSources',
        scope='Selected baseline inheritance only; unrelated patches may alter other fields. No loaded-def or runtime snapshot.')

    def record(label, data, selected=None):
        row = {'input': label, 'bytes': len(data), 'sha256': sha(data)}
        if selected is not None:
            node = ET.SubElement(selections, 'Source', input=label, sha256=sha(data))
            node.extend(copy.deepcopy(selected))
        manifest.append(row)

    def read(rel):
        p = repo / rel
        data = p.read_bytes()
        if len(data) > 4_000_000:
            raise ValueError('bounded input too large: ' + rel)
        record(rel, data)
        return data

    core_data = {}
    if a.core_archive:
        # Iterate names only; select unique exact suffixes, then read only those.
        listing = []
        with tarfile.open(a.core_archive, 'r:*') as archive:
            for member in archive:
                if member.isfile() and any(member.name.endswith('/' + p) or member.name == p for p in CORE):
                    listing.append({'name': member.name, 'size': member.size})
            for rel in CORE:
                names = [x['name'] for x in listing if x['name'].endswith(rel)]
                if len(names) != 1:
                    raise ValueError(f'Core member must be unique: {rel}: {names}')
                member = archive.getmember(names[0])
                if member.size > 1_000_000:
                    raise ValueError('oversized Core member')
                core_data[rel] = (archive.extractfile(member).read(), str(a.core_archive) + '::' + member.name)
        (out/'archive-selected-listing.json').write_text(json.dumps(listing, indent=2)+'\n')
    else:
        for rel in CORE:
            p = a.game_dir / 'Data/Core' / rel
            core_data[rel] = (p.read_bytes(), str(p))

    definitions = {}
    named = {}
    for rel, (data, label) in core_data.items():
        root = ET.fromstring(data)
        (snapshots/('Core-'+Path(rel).name)).write_bytes(data)
        wanted = [n for n in root if n.get('Name') in ('BasePawn', 'AnimalThingBase', 'AnimalKindBase')
                  or n.findtext('defName') in ('AnimalBaby', 'AnimalJuvenile', 'AnimalAdult')]
        record(label, data, wanted)
        for node in wanted:
            if node.get('Name'):
                named[node.get('Name')] = node
            if node.findtext('defName'):
                definitions[(node.tag, node.findtext('defName'))] = node

    for rel, ids in ((SEA, {'RM_Reefback', 'RM_ReefbackJuv'}),
                     (MOTHER, {'RM_WardenMother', 'RM_WardenMotherElder'})):
        data = read(rel)
        selected = [n for n in ET.fromstring(data) if n.findtext('defName') in ids]
        record(rel + ':selected nodes', data, selected)
        for node in selected:
            definitions[(node.tag, node.findtext('defName'))] = node
            if node.get('Name'):
                named[node.get('Name')] = node

    def resolve(node):
        parent = node.get('ParentName')
        return merge(resolve(named[parent]), node) if parent else copy.deepcopy(node)

    # Preserve exact source inputs for consumer review, including the sole local
    # BodySize postfix, whose registry is populated by Dhoggur's own comp.
    consumers = [HT+'Source/Titanic/Tiering/TitanicTierUtility.cs',
                 HT+'Source/Kernel/RM_TitanicKernel.cs',
                 HT+'Source/Titanic/Events/TitanPassage.cs',
                 HT+'Source/Titanic/CorpseSite/CorpseSiteVisitors.cs',
                 HT+'Source/Titanic/RM_TitanicCreaturesMod.cs',
                 HT+'Source/Titanic/Footprint/LargePawnsBridge.cs',
                 'src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_StrandingPools.cs',
                 'src/RimMandrake/EnvironmentalHazards/Source/RM_SetPieceElement_AnchoredPawn.cs',
                 'src/RimMandrake/TheForge/Source/RM_ForgeDhoggurSwell.cs']
    for rel in consumers:
        data = read(rel)
        (snapshots/Path(rel).name).write_bytes(data)
    il = a.engine_il.read_bytes()
    record(str(a.engine_il), il)
    (snapshots/'engine-selected.il.txt').write_bytes(il)
    for fragment in (b'METHOD Verse.Pawn::get_BodySize', b'Single bodySizeFactor',
                     b'Single baseBodySize', b'RecursiveNodeCopyOverwriteElements', b'"Inherit"',
                     b'"false"', b'RemoveChild', b'AppendChild', b'CalculateInitialGrowth'):
        if fragment not in il:
            raise ValueError('incomplete engine input: ' + repr(fragment))
    for rel in ('Version.txt', 'RimWorldWin64_Data/Managed/Assembly-CSharp.dll'):
        p = a.game_dir / rel
        record(str(p), p.read_bytes())
    ladder = HT+'Defs/TitanicTierDefs/RM_TitanicTierDef.xml'
    data = read(ladder)
    record(ladder+':selected node', data, list(ET.fromstring(data)))
    t = ET.fromstring(data)[0]
    floors = [float(t.findtext(f't{i}MinBodySize')) for i in (1, 2, 3)]

    results = {}
    for species in ('RM_ReefbackJuv', 'RM_Reefback', 'RM_WardenMother'):
        race = resolve(definitions[('ThingDef', species)])
        kind = resolve(definitions[('PawnKindDef', species)])
        stages = list(race.find('race/lifeStageAges'))
        base = float(race.findtext('race/baseBodySize'))
        rows = []
        for i, stage in enumerate(stages):
            name = stage.findtext('def')
            factor_text = definitions[('LifeStageDef', name)].findtext('bodySizeFactor')
            # AnimalAdult omits this; the constructor IL explicitly sets 1.
            factor = float(factor_text) if factor_text is not None else 1.0
            size = f32(f32(base)*f32(factor))
            rows.append({'stage': name, 'minAge_years_xml': float(stage.findtext('minAge')),
                         'factor': factor, 'factor_source':
                             ('Miasma RM_WardenMother.xml' if name == 'RM_WardenMotherElder' else 'Core XML')
                             if factor_text else 'LifeStageDef constructor IL default',
                         'body_size_decimal': base*factor, 'body_size_float32': size,
                         'default_GetTier': tier(size, floors),
                         'kind_drawSize': kind.findtext(f'lifeStages/li[{i+1}]/bodyGraphicData/drawSize')})
        results[species] = {'baseBodySize': base, 'stages': rows,
                            'lifeExpectancy': float(race.findtext('race/lifeExpectancy')),
                            'ageGenerationCurve_xml': race.findtext('race/ageGenerationCurve'),
                            'wildGroupSize': kind.findtext('wildGroupSize'),
                            'ecoSystemWeight': kind.findtext('ecoSystemWeight'),
                            'predator': race.findtext('race/predator'),
                            'kind_stage_count': len(kind.find('lifeStages')),
                            'AdultTier_classifier': tier(base*max(1, *[r['factor'] for r in rows]), floors),
                            'max_supported_GetTier': max(r['default_GetTier'] for r in rows),
                            'inherited_tools': [ET.tostring(x, encoding='unicode') for x in race.findall('tools/li')],
                            'force_extensions': [ET.tostring(x, encoding='unicode') for x in race.findall('modExtensions/li')
                                                 if 'Titanic' in x.get('Class', '')]}
        ET.SubElement(selections, 'Resolved', species=species).extend([race, kind])

    biome_rows = {}
    for rel, defname, animal in ((MIASMA,'RM_Miasma','RM_ReefbackJuv'), (GREY,'RM_GreySea','RM_Reefback')):
        data = read(rel)
        node = next(n for n in ET.fromstring(data) if n.findtext('defName') == defname)
        record(rel+':selected biome', data, [node])
        biome_rows[defname] = {'animal': animal, 'commonality': float(node.findtext('wildAnimals/'+animal)),
                               'animalDensity': node.findtext('animalDensity')}
    for rel in ('src/RimMandrake/Miasma/Patches/RM_AcousticPayload_Miasma.xml',):
        data=read(rel); record(rel+':nodes', data, list(ET.fromstring(data)))
    rel='src/RimMandrake/Miasma/Defs/MapGeneration/RM_Miasma_CrecheScatterer.xml'
    data=read(rel); record(rel+':nodes',data,list(ET.fromstring(data)))
    for name in ('the_miasma', 'the_grey_sea'):
        rel = 'design/Jawa/worldbuilding/biomes/rosters/'+name+'.json'
        data=read(rel); d=json.loads(data)
        rows={k: [r for r in v if any(s in json.dumps(r).lower() for s in ('reefback','nursery','warden'))]
              for k,v in d.items() if isinstance(v,list)}
        rows['notes']=d.get('notes')
        (snapshots/(name+'-selected.json')).write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')

    # Bounded audit: project patch XML only, excluding the user's prohibited lanes.
    # Record all selectors and hashes, plus candidate direct values, so a reviewer
    # can check broad selectors and unrelated named-species exclusions independently.
    patch_files=[]; candidates=[]
    for p in sorted((repo/'src').rglob('*.xml')):
        if 'Patches' not in p.parts or SKIP.intersection(p.parts):
            continue
        if p.stat().st_size>64_000_000:
            raise ValueError('patch exceeds bound: '+str(p))
        digest=hashlib.sha256()
        with p.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1_000_000),b''):
                digest.update(chunk)
        selectors=[]
        # Stream generated patch collections; retain only selected operations,
        # never print or snapshot the giant ThoughtDef etc. collections.
        for _,node in ET.iterparse(p,events=('end',)):
            xp=node.findtext('xpath')
            if not xp:
                continue
            value=node.find('value')
            value_text=ET.tostring(value,encoding='unicode') if value is not None else ''
            selectors.append(xp)
            if any(t in xp+value_text for t in TOKENS) or xp.rstrip('/') in ('Defs','/Defs','Defs/ThingDef','/Defs/ThingDef'):
                candidates.append({'file':str(p.relative_to(repo)), 'class':node.get('Class'),
                                   'xpath':xp,'value':value_text})
            node.clear()
        patch_files.append({'file':str(p.relative_to(repo)), 'sha256':digest.hexdigest(), 'bytes':p.stat().st_size, 'xpaths':selectors})
    (out/'patch-audit.json').write_text(json.dumps({'scope':'repository src/**/Patches/*.xml; excluded lanes '+str(sorted(SKIP)),
         'files':patch_files,'candidates':candidates},indent=2)+'\n')

    parent=resolve(definitions[('ThingDef','RM_Reefback')])
    child=copy.deepcopy(definitions[('ThingDef','RM_ReefbackJuv')])
    child.find('race/lifeStageAges').attrib.pop('Inherit')
    bad=merge(parent,child)
    bad_names=[n.findtext('def') for n in bad.find('race/lifeStageAges')]
    bad_kind=copy.deepcopy(definitions[('PawnKindDef','RM_ReefbackJuv')])
    bad_kind.find('lifeStages').attrib.pop('Inherit')
    bad_kind=merge(resolve(definitions[('PawnKindDef','RM_Reefback')]),bad_kind)
    expected=['AnimalBaby','AnimalJuvenile']
    assert bad_names != expected and len(bad_kind.find('lifeStages')) == 5
    assert results['RM_ReefbackJuv']['max_supported_GetTier'] < tier(32,floors)
    controls={'missing_InheritFalse': {'mutated_stage_names':bad_names,
             'mutated_kind_count':len(bad_kind.find('lifeStages')),
             'shape_oracle_rejects':bad_names!=expected,
             'note':'Appending leaves an unsorted five-entry list. Reverse selection can shadow the inherited adult; this control proves list replacement, not an automatic T3 transition.'},
              'base_only_oracle': {'wrong_size':32,'wrong_tier':tier(32,floors),
                  'supported_sizes':[r['body_size_float32'] for r in results['RM_ReefbackJuv']['stages']],
                  'rejected':all(r['body_size_float32']!=32 for r in results['RM_ReefbackJuv']['stages'])}}
    same_list=copy.deepcopy(definitions[('ThingDef','RM_ReefbackJuv')].find('race/lifeStageAges'))
    same_child=copy.deepcopy(same_list)
    same_child.attrib.pop('Inherit')
    same_bad=merge(same_list,same_child)
    same_good=merge(same_list,definitions[('ThingDef','RM_ReefbackJuv')].find('race/lifeStageAges'))
    assert len(same_bad)==4 and len(same_good)==2
    controls['inherited_same_list_fixture']={'parent_and_child_stage_names':expected,
        'without_InheritFalse_count':len(same_bad),'with_InheritFalse_count':len(same_good),
        'rejected_without_replacement':len(same_bad)!=len(same_good)}
    (out/'negative-controls.json').write_text(json.dumps(controls,indent=2)+'\n')

    # Opus BROADEN followups: growth edges and actual classifier consumers.
    young=results['RM_ReefbackJuv']
    ages=[]
    for age in (0, 0.099, 0.1, 0.6, 25, 500):
        growth=f32(min(1, max(0, f32(age)/f32(0.1))))
        mapped=f32(f32(0.1)*growth)
        row=next(r for r in reversed(young['stages']) if f32(r['minAge_years_xml']) <= f32(mapped+f32(1e-6)))
        ages.append({'initial_age_years':age,'growth':growth,'stage':row['stage'],
                     'body_size_float32':row['body_size_float32'],'default_GetTier':row['default_GetTier']})
    text=il.decode('utf-8-sig')
    curve_block=text.split('tmpMissingParts',1)[1].split('DefaultAgeGenerationCurve',1)[0]
    pairs=re.findall(r'ldc\.r4 ([0-9.]+)\s+IL_[0-9A-F]+: ldc\.r4 ([0-9.]+)\s+IL_[0-9A-F]+: newobj Verse.CurvePoint',curve_block)
    curve=[list(map(float,pair)) for pair in pairs]
    if len(curve)<3:
        raise ValueError('default age curve not recovered from installed IL')
    min_age=curve[0][0]*young['lifeExpectancy']
    max_age=curve[-1][0]*young['lifeExpectancy']
    assert min_age > young['stages'][-1]['minAge_years_xml']
    classifier=young['AdultTier_classifier']
    case_inputs={
        'Miasma_no_existing_T3_season_ok_no_override_list': [classifier,False,False,False,False,False,True,True,False],
        'Miasma_existing_T3': [classifier,False,False,False,False,False,True,True,True],
        'sea_map_with_same_land_homed_kind': [classifier,False,False,True,False,False,False,True,False],
        'explicit_list_omits_kind': [classifier,False,False,False,True,False,True,True,False],
        'biome_opt_out': [classifier,True,False,False,False,False,True,True,False],
        'unacceptable_season': [classifier,False,False,False,False,False,True,False,False]}
    pool_cases={name:{'predicate_arguments':args,'eligible':event_eligible(*args)} for name,args in case_inputs.items()}
    assert pool_cases['Miasma_no_existing_T3_season_ok_no_override_list']['eligible']
    assert not any(row['eligible'] for name,row in pool_cases.items() if name!='Miasma_no_existing_T3_season_ok_no_override_list')
    followups={'initial_age_cases':ages,
        'unconstrained_spawn_age_source_model':{
            'DefaultAgeGenerationCurve_IL_points':curve,
            'lifeExpectancy':young['lifeExpectancy'],'support_years':[min_age,max_age],
            'baby_share':0,'juvenile_share':1,
            'conditions':'Selected unpatched default age curve, no fixed/newborn/range override; wild spawner uses GeneratePawn(kind), stranding and creche requests do not force biological age. This is conditional source support, not an observed spawn census or realized age distribution.'},
        'consumer_cases':{
            'classifier_AdultTier':young['AdultTier_classifier'],
            'passage_predicate_cases':pool_cases,
            'DefQualifies_default_wake_attachment':young['baseBodySize']>=floors[0],
            'scavenger_eligible':young['predator']=='true' and classifier==0,
            'scavenger_exclusion_reason':'predator=false independently of the AdultTier test',
            'LargePawns_explicit_override_row':bool(young['force_extensions']),
            'LargePawns_reason':'PushOverrideRows only adds rows for explicit forceEnabled; none in selected race/parent XML. No claim about external Large Pawns runtime footprint.',
            'scope':'Conditional source evaluation of TitanEventEligible; no actual incident fired. Replacing classifier factor with actual maximum would still give T2 eligible on land, but would change the T3-on-map veto.'}}
    (out/'broaden-followups.json').write_text(json.dumps(followups,indent=2)+'\n')
    ET.indent(selections)
    ET.ElementTree(selections).write(out/'selected-source.xml',encoding='utf-8',xml_declaration=True)
    result={'mode':'offline selected source model; no running-game observation',
            'tier_floors':floors,'species':results,'biomes':biome_rows,
            'limits':['Default HugeThings thresholds, no force extension, no uninspected external mod or saved-setting override.',
                      'Stage minAge is XML provenance. Animal stage selection uses growth clamped to final minAge, plus 1e-6 comparison tolerance; no exact wall-clock transition claim.',
                      'Young race never gains an adult entry by aging. No automatic juvenile-to-adult species conversion demonstrated.',
                      'No art, combat balance, runtime pathing, lifecycle transport, deployment, DLL or first-touch acceptance.']}
    (out/'measurement.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'git-base.txt').write_text(subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True))
    print(json.dumps({'mode':result['mode'], 'species':{k:[(r['stage'],r['body_size_decimal'],r['default_GetTier']) for r in v['stages']]
          for k,v in results.items()},'patch_files':len(patch_files),'candidate_operations':len(candidates)},indent=2))


if __name__ == '__main__':
    main()
