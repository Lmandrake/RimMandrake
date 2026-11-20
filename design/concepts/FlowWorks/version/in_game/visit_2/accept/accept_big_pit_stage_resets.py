#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_RESET_FLOWWORKS_BIG_PIT_CALLED_WRONG_CLASS (FlowWorks 0.1.0, visit 2).

OL_OWNER_LOOK_READS read 9 FAIL in visit 2: the minified goods were absent from the 2-4 m copies, and the reader called
each absence "drawn whole over the liquid". Two faults, both offline:
  (a) big_pit_scene.stage calls ProofResetRect on RM_SubmergeDraw (its SUB type) since a09040a09e; the method lives on
      RM_NorthstarProofs, so the bridge says "No public static ProofResetRect with 1 params" and the site is never reset
      (every copy then reads d=16 against DEPTH=8). The method is not gone from the mod; the call names the wrong class.
  (b) owner_look_regressions reads "REFUSED: nothing drawn under liquid" as FAIL even when no thing stands at the cell.
      ProofSubmerge gives that one text both for a thing drawn whole and for no thing at all, so only a presence read
      (list_things) can tell them apart. An absent thing is UNMEASURED, never a look FAIL.
Cases: (a) the stage's ProofResetRect call names a class whose C# source defines it; (a2) its arg is the "x;z;w;h" that
ProofResetRect parses (a comma rect is REFUSED by the method itself); (a3) a reset that does not answer RESET stops the
stage before it clears, digs or spawns anything (no scene on an unreset site); (b1) on the visit-2 plan, with no
thing at any planned cell and every read "nothing drawn", no *_covered row reads FAIL; (b2) the same plan, with every
planned thing present and every read "nothing drawn", the *_covered rows still read FAIL (the real look fault stays red);
(b3) the presence read itself unreadable: no *_covered row reads FAIL (could not look is UNMEASURED).
Red at the filing commit on (a) and (b1); (a2), (a3) and (b3) added by the fixer and watched red on the same base.
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
NS = ROOT / 'src/RimMandrake/FlowWorks/northstar'
PLAN = ROOT / 'design/concepts/FlowWorks/version/in_game/visit_2/evidence/bigpit/scene_plan.json'
sys.path.insert(0, str(NS))
FAILS = []


def check(label, ok, why=''):
    print('%s  %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else str(why)[:400]))
    if not ok:
        FAILS.append(label)


def defines(typ, method):
    short = typ.rsplit('.', 1)[-1]
    for f in glob.glob(str(ROOT / 'src/RimMandrake/FlowWorks/Source/**/*.cs'), recursive=True):
        txt = open(f, encoding='utf-8', errors='ignore').read()
        if re.search(r'\bclass %s\b' % short, txt) and re.search(r'public static \w+ %s\(' % method, txt):
            return True
    return False


class Stop(Exception):
    pass


def case_a():
    import big_pit_scene as S
    seen = []

    def call(tool, **kw):
        if tool == 'jawa/static_call':
            seen.append((kw.get('type'), kw.get('method'), kw.get('args')))
            if kw.get('method') == 'ProofResetRect':
                raise Stop()
        return {'success': True}
    S.call, S.log = call, (lambda *a, **k: None)
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    try:
        S.stage(plan)
    except Stop:
        pass
    except Exception as ex:  # noqa: BLE001  a stage that dies before its reset is read below as "no reset call"
        print('      stage stopped before its reset: %r' % ex)
    resets = [(t, a) for t, m, a in seen if m == 'ProofResetRect']
    check('(a) stage calls ProofResetRect on a class that defines it %s' % [t for t, _a in resets],
          resets and all(defines(t, 'ProofResetRect') for t, _a in resets), resets or 'no ProofResetRect call')
    # RM_NorthstarProofs.ProofResetRect: arg.Split(';') must give 4 ints, else "REFUSED: arg must be x;z;w;h"
    want = ';'.join(str(v) for v in plan['site'])
    check('(a2) the reset arg is the site as x;z;w;h (%s)' % want,
          resets and all(a == want for _t, a in resets), [a for _t, a in resets])


def case_a3():
    """A reset the mod refuses (or the bridge cannot route) stops the stage before any clear, dig or spawn."""
    import importlib
    import big_pit_scene as S
    S = importlib.reload(S)
    acts = []

    def call(tool, **kw):
        if tool == 'jawa/static_call' and kw.get('method') == 'ProofResetRect':
            return {'success': False, 'message': 'No public static ProofResetRect with 1 params.'}
        acts.append(tool)
        return {'success': True}
    S.call, S.log, S.dump = call, (lambda *a, **k: None), (lambda: None)
    S.ROWS[:] = []
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    stopped = None
    try:
        S.stage(plan)
    except SystemExit as ex:
        stopped = ex.code
    except Exception as ex:  # noqa: BLE001
        stopped = repr(ex)
    later = [a for a in acts if a in ('jawa/destroy_batch', 'jawa/flowworks_excavation_drive', 'jawa/spawn_batch',
                                      'jawa/spawn_pawn', 'jawa/set_terrain_batch')]
    rows = [r for r in S.ROWS if 'reset' in r['row']]
    check('(a3) a refused reset stops the stage (exit %s) with a reset row, before any clear/dig/spawn (%d such calls)'
          % (stopped, len(later)), stopped == 2 and not later and rows and rows[0]['verdict'] == 'UNMEASURED',
          {'exit': stopped, 'later': later[:4], 'rows': rows})


def case_b(present, readable=True):
    import importlib
    import owner_look_regressions as O
    O = importlib.reload(O)
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    things = [{'def': 'MinifiedThing' if kind == 'mini' else ('Corpse_Human' if kind == 'corpse' else dn), 'inner': dn,
               'x': x, 'z': z, 'id': 'Thing_%s_%d_%d' % (dn, x, z)} for (_k, _x0, _z0, _f, _fl, kind, dn, x, z) in O.plan_rows(plan)]

    def call(tool, **kw):
        if tool == 'jawa/static_call' and kw.get('method') == 'ProofSubmerge':
            x, z = kw['args'].split(',')
            return {'success': True, 'result': 'REFUSED: nothing drawn under liquid at %s,%s (depth=8 waterM=1)' % (x, z)}
        if tool == 'jawa/list_things':
            if not readable:
                return {'success': False, 'error': 'bridge timeout'}
            got = things if present else []
            if kw.get('rect'):
                x0, z0, w, h = (int(v) for v in str(kw['rect']).split(','))
                got = [t for t in got if x0 <= t['x'] < x0 + w and z0 <= t['z'] < z0 + h]
            if kw.get('defName'):
                got = [t for t in got if t['def'] == kw['defName'] or t['inner'] == kw['defName']]
            return {'success': True, 'things': got, 'count': len(got)}
        return {'success': True}
    O.call = call
    import tempfile
    out = tempfile.mkdtemp(prefix='accept_big_pit_')
    try:
        O.main(['owner_look_regressions.py', out, '--plan', str(PLAN)])
    except SystemExit:
        pass
    rows = json.load(open(Path(out) / 'owner_look_regressions.json'))
    cov = [r for r in rows if '_covered_' in r['row'] and '_BP0_' not in r['row']]
    fails = [r['row'] for r in cov if r['verdict'] == 'FAIL']
    if not readable:
        check('(b3) presence unreadable: no *_covered row reads FAIL (%d FAIL of %d)' % (len(fails), len(cov)),
              cov and not fails, fails[:4])
    elif present:
        check('(b2) things present, read "nothing drawn": the wet *_covered rows read FAIL (%d of %d)' % (len(fails), len(cov)),
              cov and len(fails) == len(cov), [r for r in cov if r['verdict'] != 'FAIL'][:3])
    else:
        check('(b1) no thing at the planned cells: no *_covered row reads FAIL (%d FAIL of %d)' % (len(fails), len(cov)),
              cov and not fails, fails[:4])


def main():
    case_a()
    case_a3()
    case_b(present=False)
    case_b(present=True)
    case_b(present=True, readable=False)
    print('accept_big_pit_stage_resets: %s' % ('FAIL %s' % FAILS if FAILS else 'ok'))
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
