# FlowWorks GPT fixes — builder B (terrain, pits, reachability, rivers) — 2026-10-15

| item | prio | status | sha | notes |
|---|---|---|---|---|
| PIT_REACH_VERIFY_FLYERS_AND_GIANTS | HIGH | closed (fixed) | 009abe3c49 | C3-F4 StartPath walker answers the pawnless reach; C3-F5 masks+floor step aside for a too-wide pawn. Live state read still owed. |
| RAMP_MASKS_VERIFY_STALE_SLOPE | HIGH | dropped (not a bug) | 009abe3c49 | vanilla Building spawn/despawn pushes the cell delta; pinned; ladder comment corrected |
| FERRY_ROPE_FIX_BUILT_ONLY_WHEN_ASKED | HIGH | closed (C6-F1 fixed) | 0377b63928 | C6-F8 same-bank pairing NOT fixed (scope) |
| REACH_VETO_FIX_ONE_END_ENOUGH | | closed (fixed) | 009abe3c49 | both ends judged; map-edge island; BFS walls |
| PIT_FALL_MEND_SAVED_MIDAIR | | closed (fixed) | 0377b63928 | jump falls at once |
| RIVER_CURRENT_PROBE_LATE_GRAB | | closed (C6-F10 fixed) | 0377b63928 | C6-F6 cadence accepted |
| FLOOD_RELEASE_PROBE_FORGOTTEN_REFUSALS | | closed (C5-F11 fixed) | 0377b63928 | C5-F1 order-only, C5-F2 not a bug |
| PANNING_SPOT_VERIFY_EMPTY_RIVER | | closed (fixed) | 0377b63928 | PoolAny gate |
| CANAL_SWIM_VERIFY_POISON_POOL_PARTY | | closed (fixed) | 0377b63928 | 44 fill tiers marked no-swim. Live joy check not run. |
| COVER_DECK_TUNE_QUADRATIC_CENSUS | | closed (fixed) | 0377b63928 | local-min lead, weakest tier, no cap |

Tests: Source/SelfTest/CliffMaskChecks.cs (5 new cases), src/RimMandrake/FlowWorks/selftest_flowworks_gpt_b.py (new),
selftest_flowworks_cover_breaks.py (second OnForcedDescent site), selftest_static_game_state.py (walker REVIEWED).
DLLs built from a clean HEAD export (shared tree carries other builders' WIP).
