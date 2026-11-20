#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT: the game-only advance of FlowWorks from the blind
challenge, naming its five game-side tickets, is not refused on exit_met. A dry evaluate: it writes nothing. Run from the
repo root. Red on 47ff540ca (2026-11-19 7:46 PM PST). Bound to FlowWorks state today: once FlowWorks has moved, it
reads nothing useful."""
import sys; sys.path.insert(0, 'src/RimMandrake/rimflow')
import maturation as M
ids = ["RIMMANDRAKE_PROVE_FLOWWORKS_SHEET_DROWNS_CROPS_LIVE", "RIMMANDRAKE_PROVE_FLOWWORKS_BOTTLE_JOBS_MOVE_EXACT_LITRES",
       "RIMMANDRAKE_PROVE_FLOWWORKS_DRILL_SURVEY_ROLLS_PER_BIOME_LIVE", "RIMMANDRAKE_RETEST_FLOWWORKS_TOSS_FLAME_SINCE_JOBDEF_BUILT",
       "RIMMANDRAKE_PASS_FLOWWORKS_COATING_WASH_SCENE_NEVER_PASSED"]
v = M.evaluate('.', 'FlowWorks', 'in_game', steward='dry', conductor='dry', by='CONDUCTOR', why='dry', check_by=True, game_only=ids)['verdict']
bad = [r['clause'] for r in v['refusals'] if r['clause'] == 'exit_met']
print('PASS 1/1' if not bad else 'FAIL 0/1: exit_met refused: ' + str([r['observed'] for r in v['refusals'] if r['clause'] == 'exit_met'])[:300])
sys.exit(1 if bad else 0)
