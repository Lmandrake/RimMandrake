#!/usr/bin/env python3
"""Selftest for leather_amount_lint.py: a synthetic tree whose every fixture a naive grep would get wrong
(inherited amounts, inherited / patched / Inherit="False" leathers, vanilla's own 40, donor parents, the
FlowWorks skip), then the real src/ with its non-blind floor and the RM_Shokka probe."""
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leather_amount_lint as lint  # noqa: E402

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append(bool(ok))
    print('%s %s%s' % ('ok  ' if ok else 'FAIL', name, ('  -- %s' % detail) if detail and not ok else ''))


DEFS = """<?xml version="1.0"?>
<Defs>
  <ThingDef Name="OurBugBase" ParentName="AnimalThingBase" Abstract="True">
    <statBases><LeatherAmount>20</LeatherAmount></statBases><race><body>BeetleLike</body></race>
  </ThingDef>
  <ThingDef Name="OurHideBase" ParentName="AnimalThingBase" Abstract="True">
    <statBases><LeatherAmount>20</LeatherAmount></statBases><race><leatherDef>Leather_Plain</leatherDef></race>
  </ThingDef>
  <ThingDef ParentName="AnimalThingBase"><defName>T_ExplicitBad</defName>
    <statBases><LeatherAmount>30</LeatherAmount></statBases><race><body>BeetleLike</body></race></ThingDef>
  <ThingDef ParentName="AnimalThingBase"><defName>T_ExplicitGood</defName>
    <statBases><LeatherAmount>30</LeatherAmount></statBases><race><leatherDef>Leather_Plain</leatherDef></race></ThingDef>
  <ThingDef ParentName="OurBugBase"><defName>T_InheritedAmountBad</defName></ThingDef>
  <ThingDef ParentName="OurHideBase"><defName>T_InheritedLeatherGood</defName></ThingDef>
  <ThingDef ParentName="AnimalThingBase"><defName>T_UseLeatherFrom</defName>
    <statBases><LeatherAmount>10</LeatherAmount></statBases><race><useLeatherFrom>Cow</useLeatherFrom></race></ThingDef>
  <ThingDef ParentName="BaseInsect"><defName>T_VanillaFortyOnly</defName><race><body>BeetleLike</body></race></ThingDef>
  <ThingDef ParentName="AnimalThingBase"><defName>T_ZeroAmount</defName>
    <statBases><LeatherAmount>0</LeatherAmount></statBases><race><body>BeetleLike</body></race></ThingDef>
  <ThingDef ParentName="AnimalThingBase"><defName>T_PatchedGood</defName>
    <statBases><LeatherAmount>30</LeatherAmount></statBases><race><body>BeetleLike</body></race></ThingDef>
  <ThingDef ParentName="DonorDinoBase"><defName>T_DonorParent</defName>
    <statBases><LeatherAmount>30</LeatherAmount></statBases><race><body>BeetleLike</body></race></ThingDef>
  <ThingDef ParentName="OurHideBase"><defName>T_InheritFalseBad</defName>
    <race Inherit="False"><body>BeetleLike</body></race></ThingDef>
  <ThingDef ParentName="BaseBear"><defName>T_VanillaLeatherGood</defName>
    <statBases><LeatherAmount>50</LeatherAmount></statBases></ThingDef>
  <ThingDef><defName>T_NotARace</defName><statBases><LeatherAmount>30</LeatherAmount></statBases></ThingDef>
</Defs>"""

PATCH = """<?xml version="1.0"?>
<Patch>
  <Operation Class="PatchOperationAdd">
    <xpath>Defs/ThingDef[defName="T_PatchedGood"]/race</xpath>
    <value><leatherDef>Leather_Lizard</leatherDef></value>
  </Operation>
</Patch>"""

FLOWWORKS = """<?xml version="1.0"?>
<Defs><ThingDef ParentName="AnimalThingBase"><defName>T_FlowWorksBad</defName>
  <statBases><LeatherAmount>30</LeatherAmount></statBases><race><body>BeetleLike</body></race></ThingDef></Defs>"""


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(text)


def main():
    tmp = tempfile.mkdtemp(prefix='leatherlint_')
    try:
        write(tmp, 'RimMandrake/ModA/Defs/Races.xml', DEFS)
        write(tmp, 'RimMandrake/ModA/Patches/Leather.xml', PATCH)
        write(tmp, 'RimMandrake/FlowWorks/Defs/Races.xml', FLOWWORKS)
        write(tmp, 'RimMandrake/ModA/Defs/Broken.xml', '<Defs><ThingDef>')
        r = lint.scan(tmp)
        bad = sorted(o['defName'] for o in r['offenders'])
        check('explicit, inherited-amount and Inherit="False" races are the only offenders',
              bad == ['T_ExplicitBad', 'T_InheritFalseBad', 'T_InheritedAmountBad'], bad)
        good = set(r['good_explicit'])
        for n in ('T_ExplicitGood', 'T_InheritedLeatherGood', 'T_UseLeatherFrom', 'T_PatchedGood',
                  'T_VanillaLeatherGood'):
            check('%s passes and is seen as good' % n, n in good, sorted(good))
        check('vanilla AnimalThingBase 40 alone is counted, not failed',
              [o['defName'] for o in r['vanilla_inherited_amount']] == ['T_VanillaFortyOnly'],
              r['vanilla_inherited_amount'])
        check('donor parent is unresolved, not passed or failed',
              [o['defName'] for o in r['unresolved_parent']] == ['T_DonorParent'], r['unresolved_parent'])
        check('FlowWorks is skipped', 'T_FlowWorksBad' not in r['race_names'])
        check('non-race ThingDef is not a race', 'T_NotARace' not in r['race_names'])
        check('abstracts are not races', 'OurBugBase' not in r['race_names'])
        check('zero amount is seen as a race and not flagged', 'T_ZeroAmount' in r['race_names'] and
              'T_ZeroAmount' not in bad)
        check('a broken file is reported, not swallowed', len(r['parse_failures']) == 1, r['parse_failures'])
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lint.main([tmp])
        check('main exits 1 on offenders', rc == 1, buf.getvalue())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # The real tree: must be clean AND non-blind (floor + probe), else this is a FAIL, not a pass.
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = lint.main([])
    out = buf.getvalue()
    check('real src/ exits 0 (no offenders, not blind)', rc == 0, out.strip()[-600:])
    r = lint.scan(lint.DEFAULT_ROOT)
    check('real src/ sees >= %d races' % lint.MIN_RACES, r['races'] >= lint.MIN_RACES, r['races'])
    check('probe %s seen as good' % lint.PROBE_GOOD, lint.PROBE_GOOD in r['good_explicit'])
    check('real src/ parses every Defs/Patches file', not r['parse_failures'], r['parse_failures'][:3])
    print(out.strip().splitlines()[-1] if out.strip() else '')
    print('%d/%d passed' % (sum(RESULTS), len(RESULTS)))
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
