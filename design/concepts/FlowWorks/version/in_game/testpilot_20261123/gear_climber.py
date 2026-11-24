# gear_climber.py <out.json>: RIMMANDRAKE_TRACE_FLOWWORKS_RAIDER_IN_OPEN_PIT_WALKED_OUT. Kind A, no raid: single hostiles on jobs.
# Claim: a hostile in climbing gear steps into and out of a 4 m pit square, about 450 ticks a step (vanilla MaxMoveTicks), never
# held; the same hostile without gear never enters an open pit square, and one set in it is held and stays.
# The pit is sc_pit_trap_raid's (2 x 8, 4 m, spikes left out). Run by the trace, kept as evidence, not an acceptance test.
import sys
sys.path.insert(0, r'src/RimMandrake/FlowWorks/northstar'); sys.path.insert(0, r'src/RimMandrake/Utils'); sys.path.insert(0, r'src/RimMandrake/Utils/modcheck')
import os.path; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import on_pit
import concept_scenes as cs
out = sys.argv[1]
WR = 'RimMandrake.FlowWorks.RM_WallReach'
TRACE = {}


def gone(S, p):
    if any(q.get('id') == p for q in S.call('jawa/site_state').get('pawns') or []):
        S.call('jawa/pawn_force_incapacitate', pawn=p, action='vanish')


def foe(S, at, gear):
    p = S.pawn('Drifter', at, 'PirateWaster')
    S.call('jawa/pawn_gear', pawn=p, action='clear')            # generated gear off, so the case decides who climbs
    if gear:
        S.call('jawa/pawn_gear', pawn=p, action='wear', **{'def': 'RM_ClimbingGear'})
    return p


def what(S, p):
    return on_pit.label(S.sc(cs.NSP, 'ProofTrap', str(p)), on_pit.worn(S.B.call('jawa/pawn_get', pawn=str(p))))


def go(S, name, p, to, ticks, step=30):
    """Order Goto, read every `step` ticks: [(t, at, held, job)]. Re-ordered when the pawn drops the job."""
    tr, t = [], 0
    order = lambda: S.call('jawa/ordered_job', pawnId=p, jobDef='Goto', targetAX=to[0], targetAZ=to[1])
    first = str(order())[:160]
    while t <= ticks:
        q = next((x for x in S.call('jawa/site_state').get('pawns') or [] if x.get('id') == p), {})
        at = (q.get('x'), q.get('z'))
        tr.append((t, at, 'held=True' in S.sc(cs.NSP, 'ProofTrap', str(p)), q.get('job'), bool(q.get('downed'))))
        if at == to or not q:          # arrived, or left the map
            break
        if q.get('job') != 'Goto':
            order()
        S.ticks(step); t += step
    TRACE[name] = {'order': first, 'trace': tr}
    return tr


def body(S):
    S.r['TRACE'] = TRACE
    S.B.stop_on = cs.RAID_STOP_ON               # the default governor vanishes a stray hostile within 60 ticks (run g2)
    S.setting('superdeepCaptureEnabled', True)
    cs.TRAP_PW = 2
    pit = cs._trap_cells()
    S.dig(pit, cs.TRAP_DEPTH)
    S.call('jawa/build_batch', ops=';'.join('Wall:%d,%d' % c for c in cs._trap_walls()), stuff='BlocksGranite', faction='player')
    S.ticks(120)
    S.sc(WR, 'ProofReachForce', '')
    foot, sq, strip = (pit[1][0], pit[1][1] - 1), pit[1], (pit[1][0] + 1, pit[1][1] + 2)
    S.r['geometry'] = {'foot': foot, 'sq': sq, 'strip': strip}
    g = foe(S, foot, True)
    tr = go(S, 'gear_in', g, sq, 900)
    S.row('GEAR_steps_in', tr[-1][1] == sq and not any(x[2] for x in tr), tr[-1])
    S.r['labels'] = {'gear': what(S, g)}
    S.row('GEAR_reads_climber', S.r['labels']['gear'] == 'CLIMBER', S.r['labels']['gear'])
    tr = go(S, 'gear_out', g, strip, 900)
    S.row('GEAR_climbs_out_unheld', tr[-1][1] == strip and not any(x[2] for x in tr), tr[-1])
    gone(S, g)
    g = foe(S, (foot[0], foot[1] - 2), True)                    # the open pit on his way north: walked round or climbed through?
    tr = go(S, 'gear_past_open_pit', g, (foot[0], pit[-1][1] + 3), 1500)
    TRACE['gear_past_open_pit']['onPit'] = [x for x in tr if x[1] in pit]
    gone(S, g)
    n = foe(S, foot, False)
    tr = go(S, 'plain_in', n, sq, 600)
    S.row('PLAIN_never_enters_open_pit', not any(x[1] in pit for x in tr), tr[-1])
    gone(S, n)
    n = foe(S, sq, False)
    S.ticks(5)
    tr = go(S, 'plain_out', n, strip, 900)
    S.row('PLAIN_in_pit_is_held', all(x[2] for x in tr) and all(x[1] in pit for x in tr), tr[-1])
    S.r['labels']['plain'] = what(S, n)
    S.setting('superdeepCaptureEnabled', False)                 # the planted fault: the hold's switch off, the same man, same square
    S.r['labels']['plant'] = what(S, n)
    S.row('PLANT_switch_off_reads_onpit', S.r['labels']['plant'] == 'ONPIT', S.r['labels'])
    S.r['reach'] = S.sc(WR, 'ProofReach', '')


cs.STAGE3_SCENES['scene_pit_trap_raid'] = cs._run('scene_pit_trap_raid', body)
sys.argv = ['x', '--scene', 'scene_pit_trap_raid', '--out', out]
cs.main()
