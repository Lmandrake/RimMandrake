"""L1 loaded tier/spacing controls at Entry. No map, spawning, RNG, passage, ticks or settings-file writes.

PROVE actual GetTier/AdultTier/SpacingTier/DefQualifies and TitanEventEligible calls on resolved races and local fixtures.
EXPECT lineage eligibility stays; supported size16 spaces as T2 by default and T3 at custom T3=16.
LIES stale DLL/process, unresolved inheritance, synthetic fixtures mistaken for real races, or settings not restored.
Orchestration must establish fresh-process/preflight identity separately; this script verifies source/deployed bytes.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

MOD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOD.parent / 'Utils'))
from validation_core import Bridge
import game_paths

SETTINGS = 'RimMandrake.HugeThings.RM_HugeThingsSettings'
HOOK = 'RimMandrake.TitanicCreatures.JuvenileTierValidationHooks'
UTILITY = 'RimMandrake.TitanicCreatures.TitanicTierUtility'
FIELDS = ['giantAnimalsEnabled', 'tierThresholdsCustom', 'tierT1MinBodySize', 'tierT2MinBodySize', 'tierT3MinBodySize']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(text):
    rows = text.split(';')
    assert all('=' in row for row in rows), 'malformed field receipt'
    result = dict(row.split('=', 1) for row in rows)
    assert len(result) == len(rows), 'duplicate keys'
    return result


def tier(size, ladder, force=0):
    return 0 if force < 0 else max(1 if force > 0 else 0, sum(size >= value for value in ladder))


def gate(adult, spacing, bits):
    f = [bool(bits & (1 << i)) for i in range(8)]
    return (not f[0] and adult >= 2 and f[1] == f[2] and f[6]
            and (f[4] if f[3] else f[5]) and not (spacing == 3 and f[7]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--juvenile-race', required=True)
    ap.add_argument('--adult-race', required=True)
    ap.add_argument('--deployed-mod', type=Path, default=Path(game_paths.LOCAL_MODS) / 'HugeThings')
    a = ap.parse_args()
    report = dict(started_utc=datetime.now(timezone.utc).isoformat(), scope='L1 Entry-state loaded-method proof; no passage/crossing/flight/L4',
                  calls=[], observations=[], errors=[], restoration={'attempted': False, 'ok': False})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    original = {}
    b = None

    def persist():
        a.out.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')

    def call(tool, **params):
        assert set(params) <= declared[tool], 'undeclared parameters: '+tool
        entry = dict(tool=tool, params=params)
        report['calls'].append(entry)
        try:
            result = b.call(tool, **params)
            entry['result'] = result
            persist()
            assert result.get('success') is True, 'refused/missing success: '+str(result)
            return result
        except Exception as exc:
            entry['error'] = str(exc)
            persist()
            raise

    def field(action, name, value=None):
        args = dict(typeName=SETTINGS, action=action, field=name)
        if value is not None:
            args['value'] = value
        r = call('jawa/mod_settings_field', **args)
        assert r.get('fieldKind') == 'static'
        return r['value'] if action=='get' else r['valueAfter']

    def invoke(method, args='', type_name=HOOK):
        return call('jawa/static_call', type=type_name, method=method, args=args)['result']

    def configure(ladder, custom=True, animals=True):
        for name, value in zip(FIELDS, [str(animals), str(custom), *map(str, ladder)]):
            field('set', name, value)
            got = field('get', name)
            assert got.lower() == value.lower() or float(got) == float(value), (name, value, got)

    def observe(method, args, expected_adult, expected_spacing, expected_body, ladder, force=0, tag=''):
        row = parse(invoke(method, args))
        report['observations'].append(dict(tag=tag, method=method, args=args, fields=row))
        assert int(row['AdultTier']) == expected_adult, row
        assert int(row['SpacingTier']) == expected_spacing, row
        assert [float(x) for x in row['thresholds'].split(',')] == ladder, row
        if expected_body is not None:
            assert abs(float(row['body'])-expected_body) < 1e-5, row
            assert int(row['GetTier']) == tier(expected_body, ladder, force), row
        base=float(row['base'])
        stages=[float(x.split(':',1)[1]) for x in row['stages'].split(',') if ':' in x]
        if stages and all(x>0 and x<float('inf') for x in stages):
            expected_comp=force>=0 and (force>0 or base*max(1,max(stages))>=ladder[0])
            assert (row['DefQualifies']=='True') == expected_comp, row
        assert (row['eligibleNoT3']=='True') == (expected_adult>=2), row
        assert (row['eligibleWithT3']=='True') == (expected_adult>=2 and expected_spacing!=3), row
        persist()
        return row

    def files():
        return {p.name: sha(p) for p in Path(game_paths.MODS_CONFIG).parent.glob('Mod_*.xml') if 'hugethings' in p.name.lower()}

    try:
        dll = MOD/'Assemblies/RM_HugeThings.dll'
        stamp = dll.with_suffix('.dll.srchash')
        text = stamp.read_text(encoding='utf-8')
        rows = re.findall(r'^([0-9a-f]{64}) (.+)$', text, re.M)
        assert rows, 'empty source stamp'
        for expected, rel in rows:
            assert sha(MOD/'Source'/rel.strip()) == expected, 'stamp/source mismatch: '+rel
        assert '# dll: '+sha(dll) in text
        report['artifact'] = dict(dll_sha256=sha(dll), stamp_sha256=sha(stamp), source_stamp=text,
                                  deployed_dll_sha256=sha(a.deployed_mod/'Assemblies'/dll.name),
                                  deployed_stamp_sha256=sha(a.deployed_mod/'Assemblies'/stamp.name))
        assert sha(dll) == report['artifact']['deployed_dll_sha256']
        assert sha(stamp) == report['artifact']['deployed_stamp_sha256']
        b = Bridge()
        tools = b.S.list_tools()
        wanted = ['jawa/mod_settings_field', 'jawa/static_call']
        schemas = {t['name']: t for t in tools if t.get('name') in wanted}
        declared = {name: b.S._declared_params(schemas.get(name)) for name in wanted}
        assert all(declared.values())
        report.update(schemas=schemas, jawa_tool_count=sum(t.get('name','').startswith('jawa/') for t in tools),
                      script_sha256=sha(Path(__file__)), settings_files_before=files())
        for name in FIELDS:
            original[name] = field('get', name)
        report['original_settings'] = original.copy()
        report['restoration']['attempted'] = True
        # Repeat after valid, invalid and disabled ladders to detect accidental cached event tiers.
        ladders = [('shipped',[4,8,20],False,True), ('custom_boundary',[4,8,16],True,True),
                   ('custom_calf_below_T2',[4,18,30],True,True), ('custom_above_lineage',[4,8,40],True,True),
                   ('custom_growth_boundary',[4,8,12],True,True), ('equal',[4,8,8],True,True),
                   ('descending',[8,4,20],True,True), ('nan',['NaN',8,20],True,True),
                   ('infinity',[4,8,'Infinity'],True,True), ('custom_disabled',[4,18,30],False,True),
                   ('animals_disabled',[4,18,30],True,False), ('shipped_again',[4,8,20],False,True)]
        for label, values, custom, animals in ladders:
            configure(values,custom,animals)
            ladder = values if label.startswith('custom_') and custom and animals else [4,8,20]
            for race, factors in [(a.juvenile_race,[.2,.5]),(a.adult_race,[.2,.5,1])]:
                for index, factor in enumerate(factors):
                    row=observe('Observe',race+'|'+str(index),tier(32,ladder),tier(32*max(factors),ladder),32*factor,ladder,tag=label)
                    assert float(row['base'])==32 and len(row['stages'].split(','))==len(factors)
                    assert row['force']=='0' and row['harness']=='False', row
            observe('Fixture','3|4|0|0',tier(12,ladder),tier(12,ladder),12,ladder,tag=label)
        configure([4,8,20],False)
        for factors in ['null-list','empty','0.2,0.5,null-entry','0.2,0.5,null-def','0.2,0.5,0',
                        '0.2,0.5,-1','0.2,0.5,NaN','0.2,0.5,Infinity','0.2,0.5,-Infinity']:
            observe('Fixture','32|'+factors+'|0|-1',3,3,None,[4,8,20],tag='malformed')
        for base,factors,maxfactor in [(32,'0.2,0.5',.5),(6,'0.5',.5),(1,'0.5',.5),(3,'4',4)]:
            for force in [-1,0,1]:
                observe('Fixture',f'{base}|{factors}|{force}|0',tier(base*max(1,maxfactor),[4,8,20],force),
                        tier(base*maxfactor,[4,8,20],force),base*float(factors.split(',')[0]),[4,8,20],force,tag='force')
        for adult in range(4):
            for spacing in range(4):
                raw = invoke('GateMatrix',f'{adult}|{spacing}')
                expected=''.join('1' if gate(adult,spacing,bits) else '0' for bits in range(256))
                assert raw==expected, (adult,spacing,raw)
        assert invoke('GetTier','null',UTILITY)=='None'
        assert invoke('AdultTier','null',UTILITY)=='None'
        assert invoke('SpacingTier','null',UTILITY)=='None'
        raw=invoke('Census')
        census=[parse(line) for line in raw.splitlines()]
        assert census and len({r['kind'] for r in census})==len(census)
        assert {a.juvenile_race,a.adult_race} <= {r['race'] for r in census}
        report['resolved_kind_census']=census
    except Exception as exc:
        report['errors'].append(str(exc))
    finally:
        if report['restoration']['attempted']:
            restored,failures={},[]
            for name,value in original.items():
                try:
                    field('set',name,value)
                    restored[name]=field('get',name)
                    assert restored[name]==value
                except Exception as exc:
                    failures.append(str(exc))
            report['restoration'].update(readbacks=restored,failures=failures,ok=not failures and restored==original)
            report['settings_files_after']=files()
            if report['settings_files_before']!=report['settings_files_after']:
                report['errors'].append('settings file bytes changed')
        if b is not None:
            b.S.close()
        report['finished_utc']=datetime.now(timezone.utc).isoformat()
        report['ok']=not report['errors'] and report['restoration']['ok']
        persist()
    print(json.dumps({k:report[k] for k in ['ok','errors','restoration']}))
    return 0 if report['ok'] else 1


if __name__=='__main__':
    sys.exit(main())
