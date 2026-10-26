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


def t_deploy_staged():
    """c_deploy compares what deploy SHIPS: an ordinary mod naming a folded member's packageId is deployed as a
    MayRequire-rewritten copy (biomes_compose.stage_rewritten), so the raw src must not read as drift (wave 9;
    the old code compared raw src and FAILed every such mod right after a clean deploy)."""
    import deploy_custom_mods as dm
    import biomes_compose as bc
    with tempfile.TemporaryDirectory() as td:
        old_tmp = tempfile.tempdir
        tempfile.tempdir = os.path.join(td, 'tmp')
        os.makedirs(tempfile.tempdir)
        src, game = os.path.join(td, 'src', 'ModB'), os.path.join(td, 'Mods')
        about = '<ModMetaData><name>B</name><packageId>x.b</packageId></ModMetaData>'
        raw = '<Defs><ThingDef MayRequire="old.member"><defName>X</defName></ThingDef></Defs>'

        def put(root, rel, text):
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(text)
        put(src, 'About/About.xml', about)
        put(src, 'Defs/a.xml', raw)
        put(os.path.join(game, 'ModB'), 'About/About.xml', about)
        saved = (dm.mod_dirs, dm.load_holds, dm.LOCAL_MODS, bc.folded_ids, bc.folded_names, pf.deployed_trees)
        try:
            dm.mod_dirs, dm.load_holds, dm.LOCAL_MODS = (lambda: {'ModB': src}), (lambda: []), game
            bc.folded_ids, bc.folded_names = (lambda r: {'old.member': 'x.composed'}), (lambda r: {})
            pf.deployed_trees = lambda dirs, ex: {d: (pf._tree_sha(d, ex) if os.path.isdir(d) else None) for d in dirs}
            put(os.path.join(game, 'ModB'), 'Defs/a.xml', raw.replace('old.member', 'x.composed'))
            r = pf.c_deploy({'want': ['x.b']})
            check('c_deploy: rewritten deployed copy of a mod naming a folded id is in sync', r.status == 'PASS',
                  '%s %s' % (r.status, r.reason))
            check('c_deploy: staged link farm removed after the check', os.listdir(tempfile.tempdir) == [],
                  os.listdir(tempfile.tempdir))
            put(os.path.join(game, 'ModB'), 'Defs/a.xml', raw)
            r = pf.c_deploy({'want': ['x.b']})
            check('c_deploy negative control: an UNrewritten deployed copy is drift', r.status == 'FAIL',
                  '%s %s' % (r.status, r.reason))
        finally:
            dm.mod_dirs, dm.load_holds, dm.LOCAL_MODS, bc.folded_ids, bc.folded_names, pf.deployed_trees = saved
            tempfile.tempdir = old_tmp


def t_review_w10():
    """DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 10: four ways a check passed or crashed on something it never measured."""
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        saved = (pf.SCRATCH, pf.MODLISTS, pf.subprocess.run, pf.shutil.which, pf.intended, pf.gp.MODS_CONFIG,
                 pf.read_log, pf.gp.PLAYER_LOG)
        try:
            # 1. O14 must not read the previous run's report when this run crashed before writing one
            pf.SCRATCH, pf.MODLISTS = td, td
            open(os.path.join(td, pf.TIER_FILES['full']), 'w').write('<ModsConfigData/>')
            json.dump({'checks': {}, 'meta': {'modlist': 'old', 'cache': 'hit'}},
                      open(os.path.join(td, 'effective_def_lint_last.json'), 'w'))
            pf.shutil.which = lambda n: None
            pf.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 1, 'Traceback ...', 'KeyError: x')
            r = pf.c_def_lint({'want_src': 'snapshot x', 'tier': 'full', 'deep': True})
            check('O14: a lint that crashed before writing is UNMEASURED, not the stale last report',
                  r.status == 'UNMEASURED', '%s %s' % (r.status, r.reason))
            pf.subprocess.run, pf.shutil.which = saved[2], saved[3]
            # 2. ModsConfig with an extra repeated id (same set, zip runs out): a FAIL that says so, not StopIteration
            pf.intended = lambda ctx: (['a.one', 'a.two'], 'fixture')
            pf.gp.MODS_CONFIG = modsconfig(td, ['a.one', 'a.two', 'a.two'])
            r = pf.c_modsconfig({})
            check('O04: a repeated id is a FAIL naming it, not a crash', r.status == 'FAIL' and 'repeated' in r.reason,
                  r.reason)
            # 3. L01 with nobody seen listening: unproven, not "held by pid []"
            log = os.path.join(td, 'Player.log')
            open(log, 'w').write(LOG_GOOD)
            pf.gp.PLAYER_LOG, pf.read_log = log, (lambda path=None: LOG_GOOD)
            pf.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 1, '', '')
            r = pf.c_live_identity({'procs': [(42, None)]})
            check('L01: an empty listener read is UNMEASURED', r.status == 'UNMEASURED', '%s %s' % (r.status, r.reason))
            pf.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 0, '42\n', '')
            check('L01 control: the game pid listening PASSes', pf.c_live_identity({'procs': [(42, None)]}).status
                  == 'PASS')
        finally:
            (pf.SCRATCH, pf.MODLISTS, pf.subprocess.run, pf.shutil.which, pf.intended, pf.gp.MODS_CONFIG,
             pf.read_log, pf.gp.PLAYER_LOG) = saved
    # 4. --only naming no check must not print VERDICT GREEN on zero rows
    import io
    import contextlib
    saved_last = pf.LAST_REPORT
    with tempfile.TemporaryDirectory() as td, contextlib.redirect_stderr(io.StringIO()):
        pf.LAST_REPORT = os.path.join(td, 'last_preflight.json')     # the old code wrote its zero-row GREEN here
        try:
            rc = pf.main(['--only', 'O99_no_such_check', '--no-archive'])
        finally:
            pf.LAST_REPORT = saved_last
    check('--only matching nothing exits 3 (usage), not GREEN 0', rc == 3, rc)


def main():
    import io
    import contextlib
    for t in (t_verdict, t_modsconfig, t_live, t_manifest, t_deploy_staged, t_review_w10):
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
