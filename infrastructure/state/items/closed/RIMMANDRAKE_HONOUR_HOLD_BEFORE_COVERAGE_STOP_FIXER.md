# RIMMANDRAKE_HONOUR_HOLD_BEFORE_COVERAGE_STOP_FIXER

## spec

Found by Codex's full-file review of maturation_autonomy.py (2026-11-18, review for RIMMANDRAKE_ROUTE_SPENT_LIVE_FIXER_PILOT_BY_HAND, D:\ClaudeWork\rimmandrake\lane_e\route_spent_codex_review.md point 5), read in code, not reproduced: in `resolve`, the coverage-stop branch (`elif cs:`) runs `_stop_tickets` before the `elif dec in WAIT or dec in LAUNCH or dec in HOLDS: pass` branch, so a row that enters `held` (a Conductor hold) on a coverage-stopped mod can be given a ticket fixer (aut fixer) and launched. The HOLDS comment says a Conductor hold stands and nothing automatic is routed past it (RIMMANDRAKE_HONOUR_CONDUCTOR_HOLD_ROAD_BACK_FIXER_IGNORED_IT).

## verify

Acceptance test (drafted, NOT yet watched failing): in selftest_maturation_autonomy, a row with decision `held` whose designer_state is coverage-stopped (coverage_stopped(dst) truthy) and with an open stop ticket: after resolve, row aut is None and the mod is not in launches. Run: python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_autonomy. Watch it fail on the base first; if it passes on the base, drop this item as not reproduced.

## criteria

- The drafted acceptance test is red on the base and green after the fix (or the item is dropped as not reproduced).
