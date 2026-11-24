#!/usr/bin/env python3
"""sc_pit_crowd: crowded pawns stay in their hole (RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT). Kind A.

Claim: vanilla's collision recovery ("Unstuck") never sets a pawn over a pit wall. Entry point: the mover's real PatherTick
(RM_Patch_PitRecovery.ProofRecover). Valid opportunity: the pair collides (collides=True). Success: the mover is on a square a
person can step to. Forbidden effect: a step over the wall. End: one call per case. cheaper_why: the rule and the search are
read offline (PitRecovery_* over 5,760 cases); only the game shows that its own search calls the patch.
Cases: a 1x1 cut 4 m (nowhere to go: stays), a 1x3 cut (moves along the floor), the rim of a 4 m cut (not crowded in), flat
ground (the control: the pair separates), and the 1x1 cut with the pits switch off (the planted fault: he lands on the bank).

    python.exe src\\RimMandrake\\FlowWorks\\northstar\\pit_crowd_live.py --out <json>   (bridge held; minimal list + FlowWorks)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concept_scenes as C   # noqa: E402

REC = 'RimMandrake.FlowWorks.RM_Patch_PitRecovery'
PERSON = 2                                     # notches a person steps: RM_PitTrapMath.ClimbLimit(1), the shipped rule


def crowd(S, at):
    """Two colonists on one square; the second spawned has the higher id and is the mover (vanilla's rule). -> the reading."""
    a, b = S.pawn('Colonist', at, 'player'), S.pawn('Colonist', at, 'player')
    for pid in (a, b):                         # drafted where they stand, so neither walks off before the reading
        here = C._at(S, pid) or at
        S.call('jawa/order_pawn', pawnId=pid, x=here[0], z=here[1], waitTicks=0, draft=True)
    S.ticks(10)
    txt = S.sc(REC, 'ProofRecover', '%s;%s' % (b, a))
    return txt, C.kv(txt)


def verdict(d, at, want_move=None, escape=False):
    """-> (ok, unmeasured) of one reading."""
    try:
        here, there = int(d['fromDepth']), int(d['toDepth'])
    except (KeyError, ValueError):
        return False, True
    if d.get('collides') != 'True' or d.get('from') != '%d,%d' % at:
        return False, True
    crossed = abs(here - there) > PERSON
    moved = d.get('to') != d.get('from')
    return (crossed if escape else not crossed and (want_move is None or moved == want_move)), False


def _crowd(S):
    x, z = C.O
    one, line, rim, flat = (x, z), (x + 6, z), (x + 12, z - 1), (x + 18, z)
    S.dig([one] + [(line[0] + i, z) for i in range(3)] + [(rim[0] + i, z) for i in range(-1, 2)], 8)
    S.ticks(70)
    for rid, at, move in (('CROWD_one_square_cut_stays', one, False), ('CROWD_long_cut_moves_along_the_floor', line, True),
                          ('CROWD_rim_not_crowded_in', rim, True), ('CROWD_control_flat_ground_separates', flat, True)):
        txt, d = crowd(S, at)
        ok, um = verdict(d, at, move)
        S.row(rid, ok, txt, unmeasured=um)
    S.again()
    S.dig([one], 8)
    S.ticks(70)
    S.setting('superdeepCaptureEnabled', False)
    txt, d = crowd(S, one)
    ok, um = verdict(d, one, escape=True)
    S.row('CROWD_plant_switch_off_he_lands_on_the_bank', ok, txt, unmeasured=um)


scene_pit_crowd = C._run('scene_pit_crowd', _crowd)
C.STAGE3_SCENES['scene_pit_crowd'] = scene_pit_crowd

if __name__ == '__main__':
    sys.argv += [] if '--scene' in sys.argv else ['--scene', 'scene_pit_crowd']
    sys.exit(C.main())
