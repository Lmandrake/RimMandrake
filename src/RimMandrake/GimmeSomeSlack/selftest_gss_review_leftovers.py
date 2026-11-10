#!/usr/bin/env python3
"""Offline regression cases for the post-approval GSS proof-harness findings. No bridge or game."""
import copy
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


def png_bytes():
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00')) + chunk(b'IEND', b''))


class ReviewLeftovers(unittest.TestCase):
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
