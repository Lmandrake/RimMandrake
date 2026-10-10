#!/usr/bin/env python3
"""Offline selftest for preflight_bridge.py and experiment_manifest.py -- no game, no bridge, no Windows calls.

preflight: the verdict contract (GREEN only with no FAIL and no required UNMEASURED; fail-fast SKIPs count as
UNMEASURED; a crashed check is UNMEASURED, never PASS), the ordered-list comparison (an order change is a FAIL, a
Core-only reset is named), the wedger gate, composed-member ids, and the live log readers on real line shapes from
JawaBenchInit.cs / JawaBenchTpsSampler.cs / JawaBenchAwareness.cs.
experiment_manifest: a cell whose inputs moved during the run is void; a cell differing from C0 outside its
declared variable cannot count; `complete` refuses on a missing cell, a preflight FAIL, an open safety item, or an
unknown item state -- and passes only when all hold.
"""
import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import preflight_bridge as pf  # noqa: E402
import experiment_manifest as em  # noqa: E402

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append(bool(ok))
    print('%s %s%s' % ('ok  ' if ok else 'FAIL', name, ('  -- %s' % detail) if detail and not ok else ''))


def quiet(*a, **k):
    pass


def t_verdict():
    def boom(ctx):
        raise RuntimeError('probe died')
    checks = [pf.Check('A', 'cheap_pass', 0.1, True, lambda c: pf.PASS('x')),
              pf.Check('B', 'crashes', 0.2, True, boom),
              pf.Check('C', 'opt_unm', 0.3, False, lambda c: pf.UNM('x'))]
    rows = pf.run_checks(checks, {}, out=quiet)
    check('a crashed check is UNMEASURED, never PASS', rows[1]['status'] == 'UNMEASURED')
    check('required UNMEASURED -> NOT-GREEN exit 2', pf.verdict(rows) == ('NOT-GREEN', 2))
    rows = pf.run_checks([checks[0], checks[2]], {}, out=quiet)
    check('optional UNMEASURED alone still GREEN', pf.verdict(rows) == ('GREEN', 0))
    order = []
    checks = [pf.Check('X', 'expensive', 50, True, lambda c: order.append('X') or pf.PASS('x')),
              pf.Check('Y', 'cheap_fail', 0.1, True, lambda c: order.append('Y') or pf.FAIL('bad')),
              pf.Check('Z', 'mid', 5, False, lambda c: order.append('Z') or pf.PASS('x'))]
    rows = pf.run_checks(checks, {}, out=quiet)
    check('cost-ordered: cheapest runs first', order[0] == 'Y')
    check('fail-fast: later checks SKIPPED after a required FAIL', [r['status'] for r in rows] == ['FAIL', 'SKIPPED', 'SKIPPED'])
    check('FAIL -> NO-GO exit 1', pf.verdict(rows) == ('NO-GO', 1))
    rows = pf.run_checks(checks, {}, fail_fast=False, out=quiet)
    check('--all runs everything', [r['status'] for r in rows] == ['FAIL', 'PASS', 'PASS'])


def modsconfig(td, ids):
    p = os.path.join(td, 'mc_%d.xml' % len(os.listdir(td)))
    with open(p, 'w') as fh:
        fh.write('<ModsConfigData><activeMods>%s</activeMods><knownExpansions><li>x</li></knownExpansions></ModsConfigData>'
                 % ''.join('<li>%s</li>' % i for i in ids))
    return p


def t_modsconfig():
    want = ['ludeon.rimworld', 'brrainz.harmony', 'a.one', 'a.two', 'mandrake.rm.biomes']
    real_intended, real_mc = pf.intended, pf.gp.MODS_CONFIG
    with tempfile.TemporaryDirectory() as td:
        pf.intended = lambda ctx: (list(want), 'fixture')
        try:
            pf.gp.MODS_CONFIG = modsconfig(td, want)
            check('identical ordered list PASSes', pf.c_modsconfig({}).status == 'PASS')
            pf.gp.MODS_CONFIG = modsconfig(td, [want[0], want[1], want[3], want[2], want[4]])
            r = pf.c_modsconfig({})
            check('same set, different ORDER is a FAIL that says so', r.status == 'FAIL' and 'ORDER' in r.reason)
            pf.gp.MODS_CONFIG = modsconfig(td, ['ludeon.rimworld', 'ludeon.rimworld.royalty'])
            r = pf.c_modsconfig({})
            check('a Core-only list is named as a RESET', r.status == 'FAIL' and 'RESET' in r.reason)
            check('knownExpansions <li> never counted (the 48-vs-631 trap)',
                  pf.active_ids(modsconfig(td, ['x'])) == ['x'])
            ctx = {'want': want + ['mandrake.rm.stillsand'], 'tier': 'full'}
            real_members = None
            import effective_def_lint as edl
            real_members = edl.composed_members
            edl.composed_members = lambda: {'mandrake.rm.stillsand'}
            pf._IDX.clear()
            pf._IDX.update({w: '/x' for w in want + ['mandrake.rm.stillsand']})
            r = pf.c_list_sane(ctx)
            check('a composed member id on the list is a FAIL', r.status == 'FAIL' and 'stillsand' in r.reason)
            edl.composed_members = real_members
            pf._IDX.clear()
        finally:
            pf.intended, pf.gp.MODS_CONFIG = real_intended, real_mc
    ctx = {'want': ['mlie.nwnrealfogofwar'], 'purpose': 'test'}
    check('RealFoW refused on a test run', pf.c_wedgers(ctx).status == 'FAIL')
    ctx['purpose'] = 'campaign'
    check('RealFoW allowed (and named) on a campaign run', pf.c_wedgers(ctx).status == 'PASS'
          and 'nwnrealfogofwar' in pf.c_wedgers(ctx).reason)


LOG_GOOD = """Mono path[0] = ...
[RimBridge] GABP server listening on port 5174
[RimBridge] Bridge token: abc123
[JawaBench] ready: 431 tools, build 1955bd4b6a12
[JawaBench] TPS sampler installed (bridge-registration): session s1 pid 42
[JawaBench] map awareness: installed by bridge-registration (all hooks); switches on
"""


def t_live():
    ctx = {'log': LOG_GOOD, 'companion': {'repo_build': '1955bd4b6a12'}}
    check('live companion build matches the repo artifact', pf.c_live_companion(ctx).status == 'PASS')
    ctx['companion'] = {'repo_build': '000000000000'}
    check('live companion build mismatch is a FAIL', pf.c_live_companion(ctx).status == 'FAIL')
    check('TPS autostart at bridge-registration PASSes', pf.c_live_tps(ctx).status == 'PASS')
    ctx2 = {'log': LOG_GOOD.replace('(bridge-registration)', '(tps_report)')}
    check('TPS started by a first call is a FAIL (autostart broken)', pf.c_live_tps(ctx2).status == 'FAIL')
    check('no TPS line is UNMEASURED, not PASS', pf.c_live_tps({'log': 'nothing'}).status == 'UNMEASURED')
    check('awareness installed PASSes', pf.c_live_awareness(ctx).status == 'PASS')
    ctx3 = {'log': LOG_GOOD.replace('map awareness: installed', 'map awareness: failed')}
    check('awareness failed is a FAIL', pf.c_live_awareness(ctx3).status == 'FAIL')
    with tempfile.NamedTemporaryFile('wb', suffix='.dll', delete=False) as fh:
        fh.write(b'\x00\x01MZ junk 0.1.0+1955bd4b6a12' + b'f' * 28 + b'\x00 tail')
    check('informational build read from DLL bytes', pf.informational_build(fh.name) == '1955bd4b6a12')
    os.unlink(fh.name)


def ns(**kw):
    return argparse.Namespace(**kw)


def t_manifest():
    base = {'companion': {'game_sha': 'c1'}, 'modlist': {'count': 3, 'ordered_digest': 'm1'}, 'mod_dlls': {'d': 1},
            'deps': {'rbs': 'r1'}, 'settings': {'Prefs.xml': 'p1'}, 'saves': {}, 'fixture': None,
            'collectors': {'tps_settings.json': {'sampler': True}}, 'client': {'head': 'h'}}
    state = {'cap': dict(base)}

    def cap(saves=(), fixture=None):
        return json.loads(json.dumps(state['cap']))
    with tempfile.TemporaryDirectory() as td:
        em.STORE = td
        rep_p = os.path.join(td, 'pf.json')
        json.dump({'when': 'now', 'mode': 'offline', 'rows': [{'id': 'O01', 'name': 'x', 'status': 'PASS'}]},
                  open(rep_p, 'w'))
        E = 'EXP'
        cells = 'C0,C1,C2'
        check('record C0', em.cmd_record(ns(experiment=E, cell='C0', save=None, fixture=None, variable=None, note=None,
                                            rerecord=False), cap=cap) == 0)
        check('re-recording a cell is refused', em.cmd_record(ns(experiment=E, cell='C0', save=None, fixture=None,
                                                                variable=None, note=None, rerecord=False), cap=cap) == 1)
        check('verify C0 unchanged', em.cmd_verify(ns(experiment=E, cell='C0', mutable=None), cap=cap) == 0)
        state['cap']['collectors'] = {'tps_settings.json': {'sampler': True, 'attribution': True}}
        check('C1 differing only in collectors records clean',
              em.cmd_record(ns(experiment=E, cell='C1', save=None, fixture=None, variable=None, note=None,
                               rerecord=False), cap=cap) == 0)
        state['cap']['companion'] = {'game_sha': 'c2'}                         # a mid-cell redeploy
        check('a companion redeploy DURING C1 voids the cell',
              em.cmd_verify(ns(experiment=E, cell='C1', mutable=None), cap=cap) == 1)
        check('C2 starting on the redeployed companion is refused at record',
              em.cmd_record(ns(experiment=E, cell='C2', save=None, fixture=None, variable=None, note=None,
                               rerecord=False), cap=cap) == 1)
        open_item = {'TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS': 'doing'}
        a = ns(experiment=E, cells=cells, safety_item=None, no_safety_item=None, reason=None)
        check('complete REFUSED (C1 void, C2 mismatched, safety item open)',
              em.cmd_complete(a, state_of=open_item.get, last_report=rep_p) == 1)
        why = em.load(E)['events'][-1]['why']
        check('...and says every reason', any('C1 not verified' in w for w in why) and
              any('C2 differs' in w for w in why) and any('still open' in w for w in why), why)
        # a clean experiment
        state['cap'] = dict(base)
        E2 = 'EXP2'
        for c, coll in (('C0', {'sampler': False}), ('C1', {'sampler': True}), ('C2', {'sampler': True, 'aw': 1})):
            state['cap']['collectors'] = {'tps_settings.json': coll}
            em.cmd_record(ns(experiment=E2, cell=c, save=None, fixture=None, variable=None, note=None, rerecord=False),
                          cap=cap)
            em.cmd_verify(ns(experiment=E2, cell=c, mutable=None), cap=cap)
        a = ns(experiment=E2, cells=cells, safety_item=None, no_safety_item=None, reason=None)
        check('complete REFUSED while the safety item is open', em.cmd_complete(a, state_of=open_item.get,
                                                                                last_report=rep_p) == 1)
        check('complete REFUSED when the safety item state is unknown', em.cmd_complete(a, state_of=lambda s: None,
                                                                                        last_report=rep_p) == 1)
        json.dump({'when': 'now', 'mode': 'offline', 'rows': [{'id': 'O09', 'name': 'companion_match',
                                                               'status': 'FAIL'}]}, open(rep_p, 'w'))
        check('complete REFUSED on a preflight FAIL', em.cmd_complete(a, state_of=lambda s: 'done',
                                                                      last_report=rep_p) == 1)
        json.dump({'when': 'now', 'mode': 'offline', 'rows': []}, open(rep_p, 'w'))
        check('complete PASSES when every cell held, preflight clean, safety done',
              em.cmd_complete(a, state_of=lambda s: 'done', last_report=rep_p) == 0)
        check('unreadable input never equals readable', em.diff({'k': {'unreadable': 'x'}}, {'k': {'a': 1}}) == ['k'])


def main():
    import io
    import contextlib
    for t in (t_verdict, t_modsconfig, t_live, t_manifest):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            before = len(RESULTS)
            try:
                t()
            except Exception as e:                                   # noqa: BLE001
                RESULTS.append(False)
                print('FAIL %s raised %s: %s' % (t.__name__, type(e).__name__, e))
        for ln in buf.getvalue().splitlines():
            if ln.startswith(('ok  ', 'FAIL')):
                print(ln)
        del before
    print('%d/%d passed' % (sum(RESULTS), len(RESULTS)))
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
