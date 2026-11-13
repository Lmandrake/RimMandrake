#!/usr/bin/env python3
"""Offline regression cases for the post-approval GSS proof-harness findings. No bridge or game."""
import copy
import ast
import json
from pathlib import Path
import sys
import unittest
import struct
import tempfile
import zlib
from unittest.mock import patch
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / 'northstar'), str(HERE / 'northstar_matrix'), str(HERE), str(HERE.parent / 'Utils')]
import scene_rows as S
import run_live as R
import render as MR
import validation_aerial as A
import validation_style as VS


def png_bytes():
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00')) + chunk(b'IEND', b''))


class ReviewLeftovers(unittest.TestCase):
    def test_style_restores_floor_ripple_after_aborted_restyle(self):
        probes = []
        def ap(cmd):
            if cmd.startswith('crestyle:'):
                raise RuntimeError('governor stopped')
            return {'success': True}
        B = SimpleNamespace(call=lambda *a, **kw: {'success': True}, ticks=lambda n: None, ap=ap, probe=probes.append)
        with patch.object(VS, '_cst', return_value={}), patch.object(VS.V, 'reveal'), \
             patch.object(VS.V, 'frame_fit'), patch.object(VS.time, 'sleep'):
            with self.assertRaisesRegex(RuntimeError, 'governor stopped'):
                VS.s9_runs(B, [], {})
        self.assertEqual(probes[-2:], ['set:floorRipple=False', 'set:floorRipple=True'])

    def test_style_controls_reject_missing_members_and_counters(self):
        B = SimpleNamespace(call=lambda *a, **kw: {'success': True}, ticks=lambda n: None,
                            ap=lambda cmd: {'success': True}, probe=lambda cmd: None)
        after = {'members': [{'x': x, 'z': z} for x, z in VS.LEGACY],
                 'pieces': [{'owner': VS.LEGACY[0], 'legacy': True, 'legacySameMaterials': True,
                             'strands': 1, 'strandTex': 'strand'}],
                 'defaultLook': 'Industrial', 'lookStrands': {'Industrial': ['strand']}}
        for counters, expected in (({}, 'FAIL'), ({'materialised': 3}, 'PASS')):
            rows = []
            with patch.object(VS, '_cst', side_effect=[{'counters': counters}, dict(after, counters=counters)]):
                VS.s10_legacy(B, rows, {})
            self.assertEqual(rows[-1]['status'], expected)
        on = {'x': VS.LAMP_ON[0], 'z': VS.LAMP_ON[1], 'rawStyle': 'StandingLamp_Modern', 'drawnPath': 'GimmeSomeSlack/lamp'}
        off = dict(on, drawnPath='vanilla/lamp')
        placed = {'x': VS.LAMP_OFF[0], 'z': VS.LAMP_OFF[1], 'rawStyle': None, 'drawnPath': 'vanilla/lamp'}
        for observed, expected in ((False, 'FAIL'), (True, 'PASS')):
            rows = []
            middle = {'lamps': [off] + ([placed] if observed else [])}
            with patch.object(VS, '_cst', side_effect=[{'lamps': [on]}, middle, {'lamps': [on]}]):
                VS.s11_lamp_master_off(B, rows)
            self.assertEqual(rows[-1]['status'], expected)
        for ctrl_cells, expected in ((3, 'FAIL'), (4, 'PASS')):
            rd = {'ctrl': ['Industrial'], 'staged': ['Industrial'], 'ctrlCells': ctrl_cells, 'stagedCells': 4}
            rows = []
            with patch.object(VS, '_D4_SAVE', {'saved': True, 'pendingAtSave': 1}), patch.object(VS, '_d4_read', return_value=rd):
                VS.s12d_after_load(B, rows, True)
            self.assertEqual(rows[-1]['status'], expected)

    def test_style_after_load_requires_explicit_successful_load(self):
        self.assertEqual(VS.s9_before_state({'st': {'old': 1}}, {'st': {'old': 2}}, {}), {})
        for saved in ({}, {'load_completed': False}, {'load_completed': True}):
            rows = []
            with patch.object(VS, 's9_after_load') as runs, patch.object(VS, 's12d_after_load') as pending:
                VS.after_load_checks(object(), rows, saved, {}, {}, {'before': 1}, True)
            if saved.get('load_completed') is True:
                self.assertEqual((runs.call_count, pending.call_count), (1, 1))
                self.assertEqual(runs.call_args.args[-1], {'before': 1})
            else:
                self.assertEqual((runs.call_count, pending.call_count), (0, 0))
                self.assertEqual([r['status'] for r in rows], ['UNMEASURED', 'UNMEASURED'])
        calls = []
        B = SimpleNamespace(call=lambda tool, **kw: calls.append(tool) or {'success': False})
        with patch.object(VS.V, '_saves_stat', return_value={'exists.rws': 1}):
            self.assertIs(VS._save_load(B, [], 'exists', {})['load_completed'], False)
        self.assertFalse(calls)
        with patch.object(VS.V, '_saves_stat', side_effect=[{}, {'fresh.rws': 1}]), patch.object(VS.V, '_wait_saved'), \
             patch.object(VS.V, '_wait_playing') as playing:
            self.assertIs(VS._save_load(B, [], 'fresh', {})['load_completed'], False)
            playing.assert_not_called()
        self.assertEqual(calls, ['rimworld/save_game', 'rimworld/load_game'])
        st = {'anchors': [{'x': 1, 'z': 2, 'rawStyle': 'Industrial', 'graphicPath': 'path', 'spans': []}]}
        B = SimpleNamespace(call=lambda *a, **kw: {'success': True}, ticks=lambda n: None, ap=lambda cmd: st)
        with patch.object(VS.V, '_saves_stat', side_effect=[{}, {'fresh.rws': 1}]), patch.object(VS.V, '_wait_saved'), \
             patch.object(VS.V, '_wait_playing', return_value=(True, 1)), patch.object(VS.time, 'sleep'):
            self.assertIs(VS._save_load(B, [], 'fresh', st)['load_completed'], True)

    def test_theft_controls_require_observed_counters_and_removed_clamp(self):
        self.assertEqual(A.counter_status(None, None), 'UNMEASURED')
        self.assertEqual(A.counter_status('1', 1), 'PASS')
        self.assertEqual(A.counter_status('1', '2', 1), 'PASS')
        self.assertEqual(A.counter_status(1, 2), 'FAIL')
        for reply, expected in (({'success': True, 'value': '12'}, 12),
                ({'success': False, 'value': '12'}, None), ({'success': True}, None),
                ({'success': True, 'value': 'nan'}, None)):
            B = SimpleNamespace(call=lambda *a, **kw: reply)
            self.assertEqual(A._pt_stat(B, 'caughtCount'), expected)
        before = {'goodwill': 25, 'goodwillCharged': '-3', 'clampLeft': []}
        self.assertEqual(A.theft_stopped_status(before, 25, -3), 'PASS')
        self.assertEqual(A.theft_stopped_status(before, 24, -4), 'FAIL')
        self.assertEqual(A.theft_stopped_status(before, None, None), 'UNMEASURED')
        self.assertEqual(A.theft_stopped_status(dict(before, clampLeft=None), 25, -3), 'UNMEASURED')
        self.assertEqual(A.theft_stopped_status(dict(before, clampLeft=['clamp']), 25, -3), 'FAIL')
        for reply, expected in (({'success': False}, None), ({'success': True}, None),
                ({'success': True, 'things': []}, [])):
            self.assertEqual(A._pt_ids(SimpleNamespace(call=lambda *a, **kw: reply), 'RM_PowerTapClamp', (1, 2, 3, 4)), expected)

    def test_aerial_removal_budget_refuses_incomplete_journal(self):
        bridge = SimpleNamespace(call=lambda tool, **kw: {'success': True, 'packageIds': ['base']}, ticks=lambda n: None)
        for complete, entries, expected in ((False, [], 'UNMEASURED'), (True, [], 'PASS'),
                (True, [{'Level': 'Error', 'Message': 'RimMandrake.GimmeSomeSlack fault'}], 'FAIL')):
            with patch.object(A.V, '_wait_playing', return_value=(True, 1)), patch.object(A.time, 'sleep'), \
                 patch.object(A.matrix_support(), 'streamed_logs', return_value=(entries, {'complete': complete})), \
                 patch.object(A.V.VC, 'log_alive', return_value={'alive': True}):
                result = A._run_removal_check(SimpleNamespace(removal_check='fake'), bridge, SimpleNamespace(base=0))
            self.assertEqual(result['rows'][-1]['status'], expected)

    def test_full_aerial_driver_keeps_its_journal_and_uses_a_complete_blockage_fixture(self):
        tree = ast.parse(Path(A.__file__).read_text())
        driver, = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_run_live']
        self.assertFalse([n for n in ast.walk(driver) if isinstance(n, ast.Name) and
                          n.id == 'tap' and isinstance(n.ctx, ast.Store)], 'power-tap dict overwrites LogTap')
        self.assertEqual(A.M14_BARRIER, [(A.ROOM[0], z) for z in range(A.SITE[1], A.SITE[1] + A.SITE[3])])
        # Each approved aim is within 50 degrees and lateral slack is capped at 2.6 cells.
        self.assertLess(A.ROOM[0] - A.M1[0], 5.7)
        self.assertLess(min(z for x, z in A.M14_BARRIER), A.M1[1] - 12)
        self.assertGreater(max(z for x, z in A.M14_BARRIER), A.M1[1] + 12)
        calls = [n for n in ast.walk(driver) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'sorted']
        self.assertTrue(any('M14_BARRIER' in ast.unparse(n) for n in calls), 'barrier must be built with the scene walls')

    def test_aerial_journal_restores_parent_and_shared_run_keeps_it(self):
        parent = object()
        bridge = SimpleNamespace(call=lambda tool, **kw: {'success': True, 'logs': []})
        with patch.object(A.V.VC, 'TAP', [parent]), patch.object(A, 'A', return_value=bridge):
            def fail(args, B, tap):
                self.assertIs(B, bridge)
                self.assertIs(A.V.VC.TAP[0], tap)
                raise RuntimeError('stopped')
            with self.assertRaisesRegex(RuntimeError, 'stopped'):
                A.with_journal(None, fail)
            self.assertEqual(A.V.VC.TAP, [parent])
            self.assertIsNone(A.with_journal(None, lambda args, B, tap: tap, shared=True))
            self.assertEqual(A.V.VC.TAP, [parent])

    def test_aerial_shot_uses_unique_complete_source(self):
        with tempfile.TemporaryDirectory() as td:
            requested = []
            def call(tool, **kw):
                if tool != 'jawa/take_screenshot':
                    return {'success': True}
                requested.append(kw['fileName'])
                source = Path(td) / (kw['fileName'] + '.png')
                source.write_bytes(png_bytes())
                return {'success': True, 'filePath': str(source)}
            bridge = SimpleNamespace(call=call)
            with patch.object(A, 'SHOTS', str(Path(td) / 'archive')), patch.object(A.time, 'sleep'):
                for _ in range(2):
                    dest = A.A.shot(bridge, 'same', (1, 2, 3, 4))
                    self.assertEqual(Path(dest).read_bytes(), png_bytes())
                with patch.object(A.matrix_support(), 'wait_png', return_value=False):
                    self.assertTrue(A.A.shot(bridge, 'broken', (1, 2, 3, 4)).startswith('copy failed'))
                    self.assertFalse((Path(A.SHOTS) / 'broken.png').exists())
            self.assertEqual(len(set(requested)), 3)

    def test_aerial_negative_controls_require_actual_observations(self):
        before = {'success': True, 'storedWd': 10}
        after = {'success': True, 'storedWd': 9.95}
        lamp = {'success': True, 'things': [{'def': 'StandingLamp', 'powerOn': False}]}
        self.assertEqual(A.taps_off_control(before, after, lamp)[0], 'PASS')
        for bad in ({}, {'success': False, 'storedWd': 10}, {'success': True, 'storedWd': '10'},
                    {'success': True, 'storedWd': float('nan')}):
            self.assertEqual(A.taps_off_control(bad, after, lamp)[0], 'UNMEASURED')
        for bad in ({}, {'success': True, 'things': []}, {'success': True, 'things': [{'def': 'StandingLamp'}]}):
            self.assertIsNone(A.observed_power(bad, 'StandingLamp'))
            self.assertEqual(A.taps_off_control(before, after, bad)[0], 'UNMEASURED')
        self.assertEqual(A.taps_off_control(before, {'success': True, 'storedWd': 8}, lamp)[0], 'FAIL')
        lit = {'success': True, 'things': [{'def': 'StandingLamp', 'powerOn': True}]}
        self.assertEqual(A.taps_off_control(before, after, lit)[0], 'FAIL')
        calls = []
        def call(tool, **kw):
            calls.append(tool)
            return {'success': True, 'things': [{'id': 1}]} if tool == 'jawa/list_things' else {'success': True}
        status, detail = S.ignition_control(SimpleNamespace(call=call, ticks=lambda n: None), (3, 4), stop_on_fire=True)
        self.assertEqual((status, detail['sweeps']), ('FAIL', 1))
        self.assertEqual(len(calls), 2)

    def test_theft_retry_drops_old_passes_and_downstream_state(self):
        prior = {'rows': [{'id': rid, 'status': 'PASS'} for rid in A.THEFT_PHASE_ROW.values()],
                 'catch': {'tick': 1}, 'day': {'done': True}, 'stop': {'done': True}, 'stopFrom': {'tick': 9}}
        restarted = copy.deepcopy(prior)
        A.restart_theft_phase(restarted, 'catch')
        self.assertFalse(restarted['rows'])
        self.assertFalse(any(k in restarted for k in ('catch', 'day', 'stop', 'stopFrom')))
        resumed = copy.deepcopy(prior)
        resumed['day'] = {'played': 123, 'done': False}
        A.restart_theft_phase(resumed, 'day')
        self.assertEqual(resumed['day']['played'], 123)
        self.assertNotIn('stopFrom', resumed)
        self.assertEqual(A.theft_phase_gap('day', resumed['rows']), A.THEFT_PHASE_ROW['day'])
        stopped = copy.deepcopy(prior)
        A.restart_theft_phase(stopped, 'stop')
        self.assertIn('stopFrom', stopped)  # an unfinished stop still resumes its own progress

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'result.json'
            out.write_text(json.dumps(prior))
            args = SimpleNamespace(out=str(out), origin=None, theft='catch')
            def catch(B, rows, res):
                res['catch'] = {'tick': 100}
                rows.append({'id': A.THEFT_PHASE_ROW['catch'], 'status': 'PASS'})
            with patch.object(A, 'A', return_value=object()), patch.object(A, 'theft_catch', side_effect=catch):
                fresh = A.run_theft(args)
            out.write_text(json.dumps(fresh))
            args.theft = 'day'
            with patch.object(A, 'A', return_value=object()), patch.object(A, 'theft_day'):
                result = A.run_theft(args)  # phase wall budget ended without writing a row
            self.assertTrue(result['aborted'])
            self.assertEqual(result['rows'][-1]['status'], 'UNMEASURED')

    def test_wire_trial_rejects_missing_health_and_positions(self):
        valid = {'id': 7, 'pos': [3, 4], 'dead': False, 'health': {'hediffs': []}}

        def trial(start, end, observed=True):
            reads = iter([start, end])

            def call(tool, **kw):
                if tool == 'jawa/spawn_pawn':
                    return {'success': True, 'pawns': [{'id': 7}]}
                if tool == 'jawa/list_pawns':
                    return {'success': observed, 'pawns': [next(reads)]}
                return {'success': True}

            return A._wire_trial(SimpleNamespace(call=call, ticks=lambda n: None), (3, 4))

        self.assertIs(trial(valid, valid)['shocked'], False)
        hot = copy.deepcopy(valid)
        hot['health']['hediffs'] = [{'def': 'RM_FallenWireShock'}]
        self.assertIs(trial(valid, hot)['shocked'], True)
        for key in ('health', 'pos', 'dead'):
            bad = copy.deepcopy(valid)
            del bad[key]
            self.assertIn('error', trial(valid, bad))
        bad = copy.deepcopy(valid)
        bad['health'] = {}
        self.assertIn('error', trial(valid, bad))
        self.assertIn('error', trial({'id': 7}, valid))
        self.assertIn('error', trial(valid, valid, observed=False))

    def test_closed_conduit_loop_is_rendered_once_without_ends(self):
        ring = [(x, y) for x in range(2, 7) for y in range(2, 7) if x in (2, 6) or y in (2, 6)]
        sc = {'w': 12, 'h': 12, 'conduit': ring, 'walls': [], 'rock': [], 'water': [], 'doors': [], 'trees': [], 'machines': []}
        net = MR.Net(sc, 1)
        self.assertEqual(len(net.chains), 1)
        chain = net.chains[0]
        self.assertEqual(chain[0], chain[-1])
        self.assertEqual(set(chain), set(ring))
        self.assertEqual(len(chain), len(ring) + 1)
        strands, extras = MR.build_strands(net, MR.STYLES['jawa'], dict(MR.LEVELS['default']), {})
        self.assertTrue(strands)
        self.assertEqual(extras['ends'], [])
        self.assertTrue(all((s['pts'][0] == s['pts'][-1]).all() for s in strands))
        # A separate ordinary chain keeps both ends, and adding the ring duplicates no edge.
        sc['conduit'] = ring + [(9, y) for y in range(2, 7)]
        net = MR.Net(sc, 1)
        self.assertEqual(len(net.chains), 2)
        edges = [frozenset(e) for path in net.chains for e in zip(path, path[1:])]
        self.assertEqual(len(edges), len(set(edges)))

    def test_matrix_negative_guards_require_observations(self):
        self.assertEqual(R.pawn_site_status({'success': True, 'pawns': []})[0], 'PASS')
        self.assertEqual(R.pawn_site_status({'success': True, 'pawns': [{'id': 1}]})[0], 'FAIL')
        for bad in ({}, {'success': False, 'pawns': []}, {'success': True}):
            self.assertEqual(R.pawn_site_status(bad)[0], 'UNMEASURED')
        with tempfile.TemporaryDirectory() as td:
            template = Path(td) / 'template.html'
            template.write_text('<script id="CONFIG" type="application/json"></script><script id="ITEMS" type="application/json"></script>')
            out = Path(td) / 'review.html'
            rec = {'group': 'aerial', 'status': 'PASS', 'shot': {'file': 'capture.png'}}
            with patch.object(R, 'TEMPLATE', str(template)), patch.object(R, '_native', side_effect=lambda p: p):
                R.write_review({'started': 'test'}, {'a': rec}, str(out))
                items = json.loads(R.re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', out.read_text(), R.re.S)[1])
                self.assertEqual(items[0]['prefill'], 'flag')
                rec['sanity'] = {'non_blank': True, 'no_magenta': True, 'brightness_ok': True, 'frame_ok': True}
                R.write_review({'started': 'test'}, {'a': rec}, str(out))
                items = json.loads(R.re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', out.read_text(), R.re.S)[1])
                self.assertEqual(items[0]['prefill'], 'keep')

    def test_compare_runs_requires_complete_compatible_measurements(self):
        good = {'spec_hash': 'same-spec', 'catalog': 'test', 'mode': 'live', 'scenes': {
            str(i): {'status': 'PASS', 'geometryHash': 'h%d' % i, 'got': {'strands': 1}, 'settings': {}}
            for i in range(30)}}
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / 'a.json', Path(td) / 'b.json'
            a.write_text(json.dumps(good))

            def same(result):
                b.write_text(json.dumps(result))
                return R.compare_runs(a, b)[0]

            self.assertTrue(same(good))
            partial = copy.deepcopy(good)
            for i in range(20, 30):
                del partial['scenes'][str(i)]
            self.assertFalse(same(partial))  # original 20-scene intersection falsely passed
            for field, value in (('geometryHash', None), ('got', None), ('status', 'UNMEASURED')):
                bad = copy.deepcopy(good)
                bad['scenes']['0'][field] = value
                self.assertFalse(same(bad))
            for field in ('spec_hash', 'catalog', 'mode'):
                bad = copy.deepcopy(good)
                bad[field] = 'different'
                self.assertFalse(same(bad))
            off = copy.deepcopy(good)
            off['scenes']['off'] = {'status': 'PASS', 'geometryHash': None, 'got': {'enabled': False},
                                     'settings': {'enabled': 'False'}}
            a.write_text(json.dumps(off))
            self.assertTrue(same(off))
            del off['scenes']['off']
            self.assertFalse(same(off))

    def test_journal_reader_accepts_stock_operation_envelope_and_rejects_failed_reads(self):
        entry = {'Sequence': 1, 'Level': 'error', 'Message': 'real error'}
        good = {'logs': [entry], 'operation': {'Success': True, 'Status': 'Completed'}}
        reader = R.JournalReader(SimpleNamespace(call=lambda *a, **kw: good))
        self.assertIs(reader.call('rimbridge/list_logs'), good)
        self.assertEqual(reader.failures, [])
        for bad in ({'logs': [entry]}, {'logs': [entry], 'operation': {'Success': False, 'Status': 'Completed'}},
                    {'logs': [entry], 'operation': {'Success': True, 'Status': 'Failed'}},
                    dict(good, success=False), dict(good, logs=None)):
            with self.subTest(bad=bad):
                reader = R.JournalReader(SimpleNamespace(call=lambda *a, **kw: bad))
                self.assertIs(reader.call('rimbridge/list_logs')['success'], False)
                self.assertTrue(reader.failures)

    def test_streamed_log_budget_retains_errors_and_rejects_gaps(self):
        class Bridge:
            def __init__(self):
                self.logs, self.success = [], True

            def call(self, tool, **kw):
                logs = [e for e in self.logs if e['Sequence'] > kw.get('afterSequence', -1)]
                return {'success': self.success, 'logs': logs[-kw['limit']:]}

        b = Bridge()
        reader = R.JournalReader(b)
        tap = R.V.LogTap(reader)
        b.logs = [{'Sequence': 1, 'Level': 'error', 'Message': 'first error'}]
        tap.poll()
        b.logs += [{'Sequence': i, 'Level': 'warning', 'Message': 'later warning'} for i in range(2, 603)]
        entries, coverage = R.streamed_logs(tap, 0)
        self.assertTrue(coverage['complete'])
        self.assertTrue(any(e['Level'] == 'error' for e in entries))
        self.assertFalse(any(e['Level'] == 'error' for e in b.logs[-500:]))  # original false-pass window
        b.logs = [{'Sequence': 2000, 'Level': 'warning', 'Message': 'ring overflow'}]
        self.assertFalse(R.streamed_logs(tap, 0)[1]['complete'])
        b.success = False
        self.assertTrue(R.streamed_logs(tap, 0)[1]['failedReads'])

    def test_matrix_restores_previous_journal_tap_on_exception(self):
        previous = list(R.V.TAP)
        marker = object()
        R.V.TAP[:] = [marker]
        bridge = SimpleNamespace(call=lambda *a, **k: {'success': True, 'logs': []})
        try:
            with patch.object(R, '_run', side_effect=RuntimeError('stopped')):
                with self.assertRaisesRegex(RuntimeError, 'stopped'):
                    R.run(None, bridge)
            self.assertEqual(R.V.TAP, [marker])
        finally:
            R.V.TAP[:] = previous

    def test_capture_waits_for_complete_png_and_uses_unique_names(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'capture.png'
            data = png_bytes()
            for bad in (b'', data[:-1], data[:40], data[:-5] + b'xxxxx'):
                p.write_bytes(bad)
                self.assertFalse(R.wait_png(p, timeout_s=0))
            p.write_bytes(data)
            self.assertTrue(R.wait_png(p, timeout_s=0))
            names = []

            def capture(tool, **kw):
                names.append(kw['fileName'])
                src = Path(td) / (kw['fileName'] + '.png')
                src.write_bytes(data)
                return {'success': True, 'path': str(src)}

            run = R.Run(SimpleNamespace(call=capture), SimpleNamespace(shot_settle=0))
            with patch.object(R, 'SHOTS', td):
                a = run._shot('same', [0, 0, 2, 2], 11, False)
                b = run._shot('same', [0, 0, 2, 2], 11, False)
                run.finish_copies()
                self.assertNotEqual(names[0], names[1])
                self.assertTrue(a['ok'] and b['ok'])
                self.assertEqual((Path(td) / b['file']).read_bytes(), data)

    def test_aerial_liveness_is_compared_without_count_changes(self):
        sc = {'build': [{'op': 'anchor', 'cells': [[1, 1], [5, 1]]},
                        {'op': 'build', 'id': 'h_air', 'def': 'Heater', 'cells': [[7, 1]]}]}
        census = {'success': True, 'netRepairs': 0, 'anchors': [
            {'x': 1, 'z': 1, 'netLive': True, 'fallenLive': True,
             'links': [{'state': 'Cut'}], 'fallen': [{'cutPartner': 2}]},
            {'x': 5, 'z': 1, 'netLive': False, 'fallenLive': False,
             'links': [{'state': 'Cut'}], 'fallen': [{'cutPartner': 1}]}]}
        exp = {'spans_up': 0, 'spans_cut': 1, 'pole_live': [True, False], 'net_repairs': 0,
               'downed_ends': [{'pole': 0, 'live': True}, {'pole': 1, 'live': False}],
               'fallen_ends': [], 'far_consumer_live': False}
        net = {'success': True, 'things': [{'def': 'Heater', 'powerOn': False}]}

        def compare(c, n):
            b = SimpleNamespace(ap=lambda cmd: c if cmd == 'census' else n)
            return R.Run.aerial_compare(SimpleNamespace(mock=False, B=b), sc, {}, exp, {}, [0, 0, 10, 5])

        self.assertEqual(compare(census, net), [])
        bad = copy.deepcopy(census)
        bad['anchors'][0]['fallenLive'] = False
        self.assertIn('aerial.downed_ends', [m['field'] for m in compare(bad, net)])
        for bad in ({'success': False}, {'success': True, 'things': []},
                    {'success': True, 'things': [{'def': 'Heater', 'powerOn': True}]}):
            self.assertIn('aerial.far_consumer_live', [m['field'] for m in compare(census, bad)])

    def test_ignition_requires_fuel_and_every_query(self):
        class Bridge:
            def __init__(self, fuel=True, fire=None):
                self.fuel, self.fire, self.queries = fuel, fire, 0

            def call(self, tool, **kw):
                if tool == 'rimworld/spawn_thing':
                    return {'success': self.fuel}
                self.queries += 1
                return self.fire if self.fire is not None else {'success': False}

            def ticks(self, n):
                pass

        empty = {'success': True, 'things': []}
        for b, expected in ((Bridge(), 'UNMEASURED'), (Bridge(False, empty), 'UNMEASURED'),
                            (Bridge(True, {'success': True}), 'UNMEASURED'), (Bridge(True, empty), 'PASS'),
                            (Bridge(True, {'success': True, 'things': [{'id': 1}]}), 'FAIL')):
            status, detail = S.ignition_control(b, (3, 4))
            self.assertEqual(status, expected)
            self.assertEqual(b.queries, 12)

    def test_scheduler_abort_restores_trial_state(self):
        class Bridge:
            def __init__(self, previous):
                self.hold_off, self.commands = previous, []

            def probe(self, cmd):
                self.commands.append(cmd)
                if cmd == 'colonists':
                    return {'success': True, 'pawns': [{'id': 7, 'pos': [42, 43]}]}
                return {'success': True, 'pawn': {'id': 7, 'drafted': cmd.endswith('=draft')}}

            def ap(self, cmd):
                return {'designated': True, 'cut': 1, 'jobsDone': 0, 'down': 1}

            def call(self, tool, **kw):
                return {'pawns': [{'skills': [{'skill': 'Construction', 'disabled': False}]}]}

            def ticks(self, n):
                if n == 250:
                    raise RuntimeError('governor stop')

        for previous in (False, True):
            b = Bridge(previous)
            with patch.object(S, '_site'), patch.object(S, '_span', return_value=(1, 2, False, None)):
                with self.assertRaisesRegex(RuntimeError, 'governor stop'):
                    S.restring(b, SimpleNamespace(row=lambda *args: None), [])
            self.assertEqual(b.hold_off, previous)
            self.assertEqual(b.commands[-2:], ['pawn:7=tp:42,43', 'pawn:7=draft'])

    def test_st1_allowed_fallbacks_are_slots_no_family_draws(self):
        # ST1 failed StarWars/ExtensionCord/Cybertek on CableTie (speed_20261112 runs): the slot came with the approved
        # look on 2026-11-09 with Jawa art only. A slot may fall back only while no family folder draws it.
        import validation as VV
        styles = Path(VV.__file__).resolve().parent / "Textures/RimMandrake/GimmeSomeSlack/Styles"
        self.assertIn("CableTie", VV.ALLOWED_FALLBACKS)
        for fam in ("Cybertek", "ExtCord", "StarWars"):
            drawn = {p.stem for p in (styles / fam).glob("*.png")}
            self.assertFalse(drawn & VV.ALLOWED_FALLBACKS, (fam, drawn & VV.ALLOWED_FALLBACKS))

    def test_inwall_cord_counts_every_face_decal(self):
        # M1e failed with cordEdges 1 and decals {Plug: 1, WallOutlet: 1} (speed_20261112): the Modern look seats its cord in
        # a wall outlet, a face decal like StubWall (CordMaterials.IsFace)
        import validation as VV
        for decals, edges, want in (({"StubWall": 1}, 1, True), ({"Plug": 1, "WallOutlet": 1}, 1, True),
                                    ({"Plug": 1}, 1, False), ({"StubWall": 1}, 0, False), ({}, 0, False)):
            self.assertIs(VV._inwall_cord_seen({"cordEdges": edges, "decals": decals}), want, (decals, edges))

    def test_production_bridge_carries_hold_off(self):
        # proof_all's SCENES_block raised AttributeError 'A' object has no attribute 'hold_off' (speed_20261112 runs):
        # restring reads B.hold_off from the real aerial bridge, which the fakes above always set
        import validation_aerial as VA
        self.assertIs(object.__new__(VA.A).hold_off, False)

    def test_drafted_control_requires_observed_pawns(self):
        roster = {'success': True, 'pawns': [{'id': 7}]}
        replies = {7: {'success': True, 'pawn': {'id': 7, 'drafted': True}}}
        self.assertTrue(S.drafted_control_observed(roster, replies))
        for bad in ({}, {'success': False}, {'success': True, 'pawns': []}):
            self.assertFalse(S.drafted_control_observed(bad, replies))
        for bad in ({}, {7: {'success': False}}, {7: {'success': True, 'pawn': {'id': 8, 'drafted': True}}}):
            self.assertFalse(S.drafted_control_observed(roster, bad))
        undrafted = copy.deepcopy(replies)
        undrafted[7]['pawn']['drafted'] = False
        self.assertFalse(S.drafted_control_observed(roster, undrafted))


if __name__ == '__main__':
    unittest.main()
