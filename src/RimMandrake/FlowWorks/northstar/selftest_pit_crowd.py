#!/usr/bin/env python3
"""sc_pit_crowd's verdicts on known readings: good, escaped, stuck, unstacked with no collision, unreadable."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept_scenes as C
import pit_crowd_live as P

AT = (57, 60)
def rd(frm, to, fd, td, col=True):
    return C.kv('RECOVER collides=%s from=%d,%d fromDepth=%d to=%d,%d toDepth=%d edgesRefused=0' % (col, frm[0], frm[1], fd, to[0], to[1], td))

CASES = [('stays', rd(AT, AT, 8, 8), dict(want_move=False), (True, False)),
         ('lands on the bank', rd(AT, (57, 61), 8, 0), dict(want_move=False), (False, False)),
         ('along the floor', rd(AT, (58, 60), 8, 8), dict(want_move=True), (True, False)),
         ('never separates', rd(AT, AT, 0, 0), dict(want_move=True), (False, False)),
         ('crowded in', rd(AT, (57, 61), 0, 8), dict(want_move=True), (False, False)),
         ('no collision', rd(AT, AT, 8, 8, False), dict(want_move=False), (False, True)),
         ('wrong square', rd((1, 1), (1, 1), 8, 8), dict(want_move=False), (False, True)),
         ('refused', C.kv('REFUSED: no pawn'), dict(want_move=False), (False, True)),
         ('the plant escapes', rd(AT, (57, 61), 8, 0), dict(escape=True), (True, False)),
         ('the plant held', rd(AT, AT, 8, 8), dict(escape=True), (False, False))]
bad = [(n, P.verdict(d, AT, **kw), w) for n, d, kw, w in CASES if P.verdict(d, AT, **kw) != w]
bad += [] if C.STAGE3_SCENES.get('scene_pit_crowd') is P.scene_pit_crowd else ['not in the scene table']
print('selftest_pit_crowd: %s (%d cases)' % ('FAIL %s' % bad if bad else 'ok', len(CASES)))
sys.exit(1 if bad else 0)
