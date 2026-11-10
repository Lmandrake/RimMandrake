#!/usr/bin/env python3
"""Offline regression cases for the post-approval GSS proof-harness findings. No bridge or game."""
import copy
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / 'northstar'), str(HERE / 'northstar_matrix'), str(HERE), str(HERE.parent / 'Utils')]
import scene_rows as S


class ReviewLeftovers(unittest.TestCase):
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
