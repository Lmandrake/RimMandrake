#!/usr/bin/env python3
"""selftest_flowworks_moat_rim_stabs.py -- the rule of row MOAT_rim_wardens_not_stabbed (sc_moat_raid), on hits captured live.

Test pilot sitting 2026-11-23, ArchBig, save TP_MOAT_HELD_A (RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS):
with the melee rule switched off a held raider stabbed a warden on the rim; with it on (the shipped default) nobody did.
The row must go red on the first reading and stay green on the second.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'northstar'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Utils'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Utils' / 'modcheck'))
import concept_scenes as cs  # noqa: E402

RAIDERS = {'Human21181', 'Human21233'}
OFF = {'Human24671': ['912 Human24671 Blunt', '1032 Human24671 Blunt'],                       # the warden's own punches
       'Human24675': ['915 Human24675 Blunt', '1035 Human24675 Blunt', '1096 Human21233 Stab']}  # and a raider's stab
ON = {'Human24671': [], 'Human24681': []}
fails = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else why))
    if not ok:
        fails.append(label)


off, on = cs._rim_stabs(OFF, RAIDERS), cs._rim_stabs(ON, RAIDERS)
check('rule off (live): the raider\'s stab is counted, on the warden it hit', off == {'Human24671': [], 'Human24675': ['1096 Human21233 Stab']}, off)
check('rule off: the row is red', any(off.values()))
check('rule on (live): no stab, the row is green', not any(on.values()), on)
check('a warden\'s own punches are not stabs', not cs._rim_stabs({'Human24671': OFF['Human24671']}, RAIDERS)['Human24671'])
check('a recorder that refused is not read as a stab', cs._rim_stabs({'W': 'damage recorder refused: x'}, RAIDERS) == {'W': []})
src = (Path(__file__).resolve().parent / 'northstar' / 'concept_scenes.py').read_text(encoding='utf-8')
check('the row asks the rule and is UNMEASURED on a refused recorder',
      "stabs = _rim_stabs(S.r['moatWardenHits'], raiders)" in src and "S.row('MOAT_rim_wardens_not_stabbed'" in src
      and "any(not isinstance(h, list) for h in S.r['moatWardenHits'].values())" in src)
print('selftest_flowworks_moat_rim_stabs: %s' % ('FAIL' if fails else 'PASS'))
sys.exit(1 if fails else 0)
