#!/usr/bin/env python3
"""Offline selftest for effective_def_lint.py -- a synthetic two-mod tree, no game, no Windows.

The acceptance fixtures GPT's review section 3.3 asks for, each of which a raw-XML-only checker must miss:
  * a raw-valid def made invalid by a LATER patch (the material is removed by our patch),
  * an inherited bad entry (the costList lives on an abstract parent),
  * a renamed material (a full-def Replace brings a costList naming a def that does not exist),
  * an absent conditional dependency (MayRequire-guarded entries must be DROPPED, not reported),
  * a later full-def replacement.
Plus one fixture per known load killer, and the regression that motivated a fix: costlist_resolve_check.py
removed MayRequire children while lxml's iter() was live, which silently ended the walk, so guarded entries of LATER
defs survived and read as misses (the "11 older apparel / van.dacrypts misses" of 2026-10-10 were that artifact).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append(bool(ok))
    print('%s %s%s' % ('ok  ' if ok else 'FAIL', name, ('  -- %s' % detail) if detail and not ok else ''))


ABOUT = '<?xml version="1.0"?><ModMetaData><packageId>%s</packageId><name>%s</name></ModMetaData>'

DEFS_A = """<?xml version="1.0"?>
<Defs>
  <ThingDef><defName>Steel</defName></ThingDef>
  <ThingDef><defName>ComponentIndustrial</defName></ThingDef>
  <ThingDef><defName>WoodLog</defName></ThingDef>
  <ThingDef><defName>Beer</defName><ingestible><drugCategory>Social</drugCategory></ingestible>
    <comps><li Class="CompProperties_Drug"/></comps></ThingDef>
  <ThingDef><defName>MatGone</defName></ThingDef>
  <ThingDef Name="BaseWall" Abstract="True"><costList><MatGone>5</MatGone><Steel>1</Steel></costList></ThingDef>
  <ThingDef ParentName="BaseWall"><defName>ChildWall</defName><recipeMaker><workAmount>1</workAmount></recipeMaker></ThingDef>
  <ThingDef><defName>Guarded1</defName><costList><MatAbsent1 MayRequire="absent.mod">3</MatAbsent1></costList></ThingDef>
  <ThingDef><defName>Guarded2</defName><costList><MatAbsent2 MayRequire="absent.mod">3</MatAbsent2></costList></ThingDef>
  <ThingDef><defName>ReplacedThing</defName><costList><Steel>2</Steel></costList></ThingDef>
  <ThingDef><defName>DrugNoComp</defName><ingestible><drugCategory>Hard</drugCategory></ingestible></ThingDef>
  <ThingDef><defName>FoodOK</defName><ingestible><drugCategory>None</drugCategory></ingestible></ThingDef>
  <ThingDef><defName>PlantBad</defName><plant><purpose>None</purpose></plant></ThingDef>
  <ThingDef><defName>PlantOK</defName><plant><purpose>Food</purpose></plant></ThingDef>
  <PawnKindDef><defName>KindNoRace</defName><race>GhostRace</race></PawnKindDef>
  <PawnKindDef><defName>KindOK</defName><race>Steel</race></PawnKindDef>
  <BiomeDef><defName>BiomeNoWorker</defName></BiomeDef>
  <BiomeDef><defName>BiomePocket</defName><generatesNaturally>false</generatesNaturally></BiomeDef>
  <BiomeDef><defName>BiomeLi</defName><workerClass>BiomeWorker_X</workerClass>
    <wildAnimals><li><animal>Steel</animal></li></wildAnimals></BiomeDef>
  <BiomeDef><defName>BiomeOK</defName><workerClass>BiomeWorker_X</workerClass><wildAnimals><Steel>1</Steel></wildAnimals></BiomeDef>
  <FactionDef><defName>DonorFactionBare</defName></FactionDef>
  <RecipeDef><defName>RecipeBad</defName><ingredients><li><filter><thingDefs><li>NoSuchThing</li></thingDefs></filter></li></ingredients>
    <products><NoSuchProduct>1</NoSuchProduct></products></RecipeDef>
</Defs>"""

DEFS_B = """<?xml version="1.0"?>
<Defs>
  <FactionDef><defName>OurFactionBare</defName></FactionDef>
  <FactionDef><defName>OurFactionOK</defName><fixedName>X</fixedName></FactionDef>
  <ThingDef><defName>MemberGated</defName><comps><li MayRequire="mandrake.member" Class="X"/></comps></ThingDef>
  <ThingDef><defName>AnyOfOK</defName><comps><li MayRequireAnyOf="mandrake.member,test.a" Class="X"/></comps></ThingDef>
  <RimMandrake.X.RM_DefAliasDef><defName>Aliases</defName><aliases><li><from>MatGone</from></li></aliases></RimMandrake.X.RM_DefAliasDef>
</Defs>"""

PATCH_B = """<?xml version="1.0"?>
<Patch>
  <Operation Class="PatchOperationRemove"><xpath>Defs/ThingDef[defName="MatGone"]</xpath></Operation>
  <Operation Class="PatchOperationReplace"><xpath>Defs/ThingDef[defName="ReplacedThing"]</xpath>
    <value><ThingDef><defName>ReplacedThing</defName><costList><MatRenamed>2</MatRenamed></costList></ThingDef></value></Operation>
  <Operation Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="NotThere"]</xpath><value><x/></value></Operation>
  <Operation Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="NotThere2"]</xpath><success>Always</success><value><x/></value></Operation>
  <Operation Class="PatchOperationAdd" MayRequire="absent.mod"><xpath>Defs/ThingDef[defName="Steel"]</xpath><value><y/></value></Operation>
  <Operation Class="PatchOperationFindMod"><mods><li>Absent Mod</li></mods>
    <match Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="FoodOK"]</xpath><value><costList><MatNever>1</MatNever></costList></value></match>
  </Operation>
  <Operation Class="PatchOperationAdd"><xpath>Defs</xpath><value><ThingDef><defName>PatchMade</defName><costList><MatPatch>1</MatPatch></costList></ThingDef></value></Operation>
  <!-- RAKATA_PATCHES_PROBE_THREE_OPS_MATCH_NOTHING: a NESTED <success>Always</success> is honoured by the engine
       (PatchOperation.Apply), so this Sequence succeeds and its second op runs. -->
  <Operation Class="PatchOperationSequence"><operations>
    <li Class="PatchOperationRemove"><xpath>Defs/ThingDef[defName="WoodLog"]/notPresent</xpath><success>Always</success></li>
    <li Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="WoodLog"]</xpath><value><costList><MatSeq>1</MatSeq></costList></value></li>
  </operations></Operation>
  <Operation Class="PatchOperationFindMod"><mods><li>Test A</li></mods>
    <match Class="PatchOperationRemove"><xpath>Defs/ThingDef[defName="Steel"]/notPresent</xpath><success>Always</success></match>
  </Operation>
  <Operation Class="Some.CustomOperation"><xpath>Defs/ThingDef</xpath></Operation>
</Patch>"""


def write(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(text)


def build_fixture(root):
    mods = os.path.join(root, 'mods')
    write(os.path.join(mods, 'A', 'About', 'About.xml'), ABOUT % ('test.a', 'Test A'))
    write(os.path.join(mods, 'A', 'Defs', 'a.xml'), DEFS_A)
    os.makedirs(os.path.join(mods, 'A', 'Defs', 'dir_named.xml'))           # a DIRECTORY named *.xml must be skipped
    write(os.path.join(mods, 'B', 'About', 'About.xml'), ABOUT % ('mandrake.test', 'Test B'))
    write(os.path.join(mods, 'B', 'Defs', 'b.xml'), DEFS_B)
    write(os.path.join(mods, 'B', 'Patches', 'p.xml'), PATCH_B)
    mc = os.path.join(root, 'ModsConfig.xml')
    write(mc, '<ModsConfigData><activeMods><li>test.a</li><li>mandrake.test</li></activeMods></ModsConfigData>')
    return mods, mc


def defs_of(rep, name, sev=None):
    return {f['def'] for f in rep.checks[name]['findings'] if sev is None or f['sev'] == sev}


def main():
    import effective_def_lint as edl
    with tempfile.TemporaryDirectory() as td:
        mods, mc = build_fixture(td)
        os.environ['EDL_ROOTS'] = mods
        os.environ['EDL_GAME'] = os.path.join(td, 'nogame')
        os.environ['EDL_CACHE'] = os.path.join(td, 'cache')
        edl.composed_members = lambda: {'mandrake.member'}
        rep = edl.Report()
        rep.use_cache = True
        rep.meta = {}
        edl.build_and_check(mc, {}, rep, progress=lambda s: None)

        cl = {f['def']: f for f in rep.checks['costlist']['findings']}
        check('costlist sanity probe sees Steel/Component/WoodLog/Beer (status not UNMEASURED)',
              rep.checks['costlist']['status'] == 'FAIL')
        check('inherited entry made dead by a LATER patch: ChildWall flagged', 'ChildWall' in cl)
        check('...as a crash on the RECIPE path (recipeMaker)', cl.get('ChildWall', {}).get('sev') == 'crash'
              and 'RECIPE' in cl.get('ChildWall', {}).get('detail', ''))
        check('...naming the parent it was inherited from', cl.get('ChildWall', {}).get('list_from') == 'BaseWall')
        check('full-def Replace bringing a renamed material: ReplacedThing flagged',
              cl.get('ReplacedThing', {}).get('material') == 'MatRenamed')
        check('...as error, not crash (no load-time consumer)', cl.get('ReplacedThing', {}).get('sev') == 'error')
        check('MayRequire-guarded entries DROPPED, both of them (live-iter removal regression)',
              'Guarded1' not in cl and 'Guarded2' not in cl, sorted(cl))
        check('absent conditional dependency (FindMod) not applied', 'FoodOK' not in cl)
        check('patch-created def checked and given provenance', cl.get('PatchMade', {}).get('mod') == 'mandrake.test')
        check('directory named *.xml skipped without error', True)
        check('removed_refs: BaseWall still names MatGone removed by our patch', 'BaseWall' in defs_of(rep, 'removed_refs'))
        check('removed_refs: an alias table <from> is exempt', 'Aliases' not in defs_of(rep, 'removed_refs'))
        check('recipe_refs: dead ingredient and null product', len(rep.checks['recipe_refs']['findings']) == 2)
        check('op_mayrequire: our top-level <Operation MayRequire> with the mod absent is an error',
              rep.checks['op_mayrequire']['status'] == 'FAIL')
        check('failed_ops: unguarded no-match flagged, <success>Always</success> exempt',
              len(rep.checks['failed_ops']['findings']) == 1, rep.checks['failed_ops']['findings'])
        check('nested <success>Always</success>: the Sequence and FindMod pass, the next op in the Sequence ran',
              cl.get('WoodLog', {}).get('material') == 'MatSeq', cl.get('WoodLog'))
        check('drug_comp: DrugNoComp crash, Beer and FoodOK clean', defs_of(rep, 'drug_comp') == {'DrugNoComp'})
        check('pawnkind_race: KindNoRace only', defs_of(rep, 'pawnkind_race') == {'KindNoRace'})
        check('biome_worker: BiomeNoWorker only (pocket biome exempt)', defs_of(rep, 'biome_worker') == {'BiomeNoWorker'})
        check('li_custom_loader: BiomeLi only', defs_of(rep, 'li_custom_loader') == {'BiomeLi'})
        check('plant_purpose: PlantBad only', defs_of(rep, 'plant_purpose') == {'PlantBad'})
        check('faction_name: ours is error, donor is warn',
              defs_of(rep, 'faction_name', 'error') == {'OurFactionBare'}
              and defs_of(rep, 'faction_name', 'warn') == {'DonorFactionBare'})
        check('member_mayrequire: MayRequire on a member flagged, AnyOf with a real id not',
              defs_of(rep, 'member_mayrequire') == {'MemberGated'}, defs_of(rep, 'member_mayrequire'))
        check('unsupported patch op is reported UNSUPPORTED, never silently passed',
              rep.checks['unsupported_patch_ops']['status'] == 'UNSUPPORTED')

        rep2 = edl.Report()
        rep2.use_cache = True
        rep2.meta = {}
        edl.build_and_check(mc, {}, rep2, progress=lambda s: None)
        check('second run is a cache HIT with identical findings', rep2.meta.get('cache', '').startswith('HIT')
              and rep2.checks['costlist']['findings'] == rep.checks['costlist']['findings'])
        mj = os.path.join(td, 'manifest.T.json')
        with open(mj, 'w') as fh:
            fh.write('{"name": "T", "ids": ["test.a", "mandrake.test"]}')
        repj = edl.Report()
        repj.meta = {}
        edl.build_and_check(mj, {}, repj, progress=lambda s: None)
        check('a modmanifest manifest.<NAME>.json with the same ordered ids hits the same cache entry',
              repj.meta.get('cache', '').startswith('HIT'))
        with open(os.path.join(mods, 'B', 'Patches', 'p.xml'), 'a') as fh:
            fh.write('\n<!-- touched -->\n')
        rep3 = edl.Report()
        rep3.use_cache = True
        rep3.meta = {}
        edl.build_and_check(mc, {}, rep3, progress=lambda s: None)
        check('a content change misses the cache', rep3.meta.get('cache') == 'MISS')
        rep4 = edl.Report()
        rep4.cache_only = True
        os.environ['EDL_CACHE'] = os.path.join(td, 'cache2')
        try:
            edl.build_and_check(mc, {}, rep4, progress=lambda s: None)
            check('--cache-only on a miss exits 4', False)
        except SystemExit as e:
            check('--cache-only on a miss exits 4', e.code == 4)

    texts = {
        '/x/W.cs': 'class BiomeWorker_Bad : BiomeWorker { float GetScore(){ return tile.Rivers.Count; } }\n'
                   'class BiomeWorker_Good : BiomeWorker { float GetScore(){ return tile.potentialRivers.Count; } }',
        '/x/A.cs': 'public abstract class Alert_Base : Alert { }\npublic abstract class Alert_Leaf : Alert_Base { }\n'
                   'public class Alert_Real : Alert_Base { }',
    }
    rep = edl.Report()
    edl.check_src(rep, texts=texts)
    check('biomeworker_rivers: the .Rivers reader only', defs_of(rep, 'biomeworker_rivers') == {'BiomeWorker_Bad'})
    check('alert_leaf: abstract leaf flagged, abstract parent with a concrete child not',
          defs_of(rep, 'alert_leaf') == {'Alert_Leaf'})

    print('%d/%d passed' % (sum(RESULTS), len(RESULTS)))
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
