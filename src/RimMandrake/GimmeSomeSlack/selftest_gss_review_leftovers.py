#!/usr/bin/env python3
"""Offline regression cases for the post-approval GSS proof-harness findings. No bridge or game."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / 'northstar'), str(HERE / 'northstar_matrix'), str(HERE), str(HERE.parent / 'Utils')]
import scene_rows as S


class ReviewLeftovers(unittest.TestCase):
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
