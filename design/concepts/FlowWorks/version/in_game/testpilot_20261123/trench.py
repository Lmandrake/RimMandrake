# trench.py <out.json> <pit width 1|2> <ticks> [--wardens]
# The first experiment of RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_4M_TRENCH_ONCE: stage the 4 m spiked trench of
# sc_pit_trap_raid, leave the raid on the map (no drive-off), and read every 30 ticks, for <ticks> after two are held:
# each held raider's place, job, ProofTrap and fetch reads, every ladder near the trench, and the free raiders within 3
# squares. --wardens: also order one capture per held raider from the strip (the old run had a warden; he was downed).
# The trace is the receipt key holdTrace; the row TP_held_stay_held is FAIL when a held raider left the pit alive.
import sys, os
sys.path.insert(0, r'src/RimMandrake/FlowWorks/northstar'); sys.path.insert(0, r'src/RimMandrake/Utils'); sys.path.insert(0, r'src/RimMandrake/Utils/modcheck')
import concept_scenes as cs
out, width, ticks = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
wardens = '--wardens' in sys.argv
cs.TRAP_PW = width
STEP = 30


def body(S):
    for k in ('captureDownEnabled', 'superdeepRoomsEnabled'):
        S.setting(k, True)
    pit = cs._pit_trap(S)
    pitset = set(pit)
    prior, S.B.stop_on = S.B.stop_on, cs.RAID_STOP_ON
    trace, left = [], {}
    try:
        seen = cs._watch_trap(S, pit, until_ladder=False, until_held=2)
        held = sorted(seen['held'])
        if wardens:
            for pid in held[:2]:
                _, v = cs._ptr_prisoner(S, pid)
                cell = cs.kv(v).get('cell', '')
                if ',' in cell:
                    lip = cs._trap_lip(tuple(int(q) for q in cell.split(',')))
                    w = S.pawn('Colonist', lip, 'player')
                    S.call('jawa/ordered_job', pawnId=w, jobDef='RM_CaptureDown', targetAId=pid, targetBX=lip[0], targetBZ=lip[1])
        for i in range(ticks // STEP + 1):
            r = S.B.call('jawa/site_state') or {}
            tick = (r.get('state') or {}).get('tick')
            parts = []
            for p in r.get('pawns') or []:
                pid, at = p.get('id'), (p.get('x'), p.get('z'))
                if p.get('x') is None:
                    continue
                t = p.get('targetA') or {}
                tgt = t.get('id') or t.get('thingId') or ('%s,%s' % (t.get('x'), t.get('z')) if t else '-')
                if pid in held:
                    trap = S.sc(cs.NSP, 'ProofTrap', str(pid))
                    is_held = 'held=True' in trap
                    parts.append('H %s@%s,%s:%s>%s held=%s%s' % (pid, at[0], at[1], p.get('job'), tgt, is_held,
                                                                 ' DOWNED' if p.get('downed') else ''))
                    if at not in pitset and pid not in left:
                        left[pid] = {'tick': tick, 'at': at, 'poll': i, 'trap': trap[:160],
                                     'fate': cs._ptr_fate(S, pid)}
                elif min(cs._cheb(at, c) for c in pit) <= 3:
                    parts.append('%s %s@%s,%s:%s>%s' % ('C' if p.get('faction') == 'PlayerColony' else 'F', pid, at[0], at[1],
                                                        p.get('job'), tgt))
            lad = [(t.get('x'), t.get('z')) for t in S.B.call('jawa/list_things', defName='RM_LadderPortable',
                                                                rect=cs._trap_rect(pit, 2)).get('things') or []]
            here = {q.split()[1].split('@')[0] for q in parts if q.startswith('H ')}
            trace.append('t=%s %s ladders=%s%s' % (tick, ' | '.join(sorted(parts)), lad,
                                                  ''.join(' %s:OFF-MAP %s' % (h, cs._ptr_fate(S, h)) for h in held if h not in here)))
            if left and i - min(v['poll'] for v in left.values()) >= 4:
                break
            S.ticks(STEP)
        S.r['holdTrace'], S.r['holdLeft'], S.r['holdHeld'] = trace, left, held
        S.row('TP_held_stay_held', not left, {'held': held, 'left': left, 'polls': len(trace), 'width': width},
              unmeasured=len(held) < 1)
    finally:
        S.r.setdefault('holdTrace', trace)
        S.B.stop_on = prior


cs.STAGE3_SCENES['scene_pit_trap_raid'] = cs._run('scene_pit_trap_raid', body)
sys.argv = ['x', '--scene', 'scene_pit_trap_raid', '--out', out]
cs.main()
