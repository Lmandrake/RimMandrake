# RIMMASTER_TRACE_PYRELANDS_PROOF_ROWS_THE_LOOP_DROPPED

Traced 2026-11-07 17:06 PST by a Conductor peek (owner's AFK authority, `CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`).

## Method
- File: `src/RimMandrake/Pyrelands/validation.py`. Range: `git diff ff723afe8c origin/ralph/pyrelands` (merge base to the
  branch tip, 19a92fd4e5 at trace time; the loop's clone `/home/mandrake/rm/scratch/BENCH/ralph_pyrelands` has
  validation.py unchanged since then). Net numstat is 84 added and 102 removed, over 7 loop commits:
  186b8cd2ed (+10/-8), fd1725e98c (+12/-3), 4eebd22110 (+10/-13), a507c093e1 (+7/-0), 15a5f1c6de (+15/-44),
  2becd87bea (+1/-1), 5f8e6c28ec (+29/-33).
- Each removed hunk is matched to the suite row it belonged to, and that row to the bar it `shows` in
  `src/RimMandrake/Utils/modcheck/required_checks.json` (branch copy).
- The two canonical-save rows were re-run offline with the script they wrapped:
  `python3 src/RimMandrake/Pyrelands/diag/save_world_check.py` (17:04 PST).

## Table

| # | removed lines (what) | commit | row / bar served | class | evidence |
|---|---|---|---|---|---|
| 1 | docstring "ringed by `RM_FE_FirebreakLine`", `FIREBREAK = "RM_FE_FirebreakLine"`, `_firebreak` docstring | 186b8cd2ed | test hygiene for every fire pad (not a bar) | **replaced** | The terrain and its kernel special case were deleted in the same commit; the pads are now ringed with vanilla `Concrete`. Branch `git grep RM_FE_FirebreakLine -- src` finds it only in `review/KEYSHEET.md`. |
| 2 | `"rainAcc"` in `_probe`'s float keys | 186b8cd2ed | `fresh_burn_bonus` (pyre_fresh_burn_feeds_the_field) | **obsolete** | The rain accumulator and its grid were deleted from the mod (commit body). The old file parsed `rainAcc` and never read it (line 529 is its only use). The new keys are `base` and `wateredFertility`. |
| 3 | `if rained["bonus"] > 0.01: _fail(... Black Rain left a burn bonus ...)` plus the docstring "the bonus must be gone" | 186b8cd2ed | `fresh_burn_bonus/fresh_burn_feeds_the_field` (pyre_fresh_burn_feeds_the_field) | **replaced** (the bar was reworded by owner card) | The north star now reads "black rain compounds that advantage rather than washing it away" (`validated-by: BY CARD`). The replacement checks are stricter: bonus `0 < rained < day1` (still on its own clock) and `fertility >= wateredFertility + bonus` (it stacks). |
| 4 | `room_heat set 10 C` on both rooms, 10x250-tick series, "cold" mean delta below the 24 C cap, `coldStartSeries` | 4eebd22110 | `furnace_room/furnacebeast_heats_room` (pyre_furnacebeast_heats_room) | **replaced** | The old row chilled both rooms under the heat pusher's 24 C cap, so it passed while the beast heated nothing at the biome's real 50 C. The new row runs at map temperature for 12x1000 ticks and needs room A to end at least 5 C hotter than the control. It is stronger, and it fixes a check that could not fail on the real case. |
| 5 | `queue=True, waitTicks=60` and `_wait(t, 2500)` in the harvest loop | fd1725e98c | `scorchfruit_produces` (pyre_scorchfruit_produces) | **replaced** | The first order now interrupts (a queued order behind a sleeper never started), the wait is 3600 ticks, and a new assertion catches a harvest that leaves the pod standing (the 1% regrow stub bug). |
| 6 | `REGROW_OVERRIDE_DAYS`, `REGROW_SHORT_STEP` and the COMPRESSED regrow block: override set, two short steps, override/biome read-back and restore asserts, the closing `_unmeasured` | 15a5f1c6de | `embergrass_regrow/embergrass_regrows` (pyre_embergrass_regrows) | **replaced** (main logic); **obsolete** (restore asserts) | The old row ended in `_unmeasured` every time, so it could never pass or fail the bar. The new row samples the real clock at days 3 and 7 and fails below 25% and 60% of the pre-burn count. The restore and read-back asserts guarded the override, and no override is set any more. The read-back pinned "shipped 9", which the loop has since moved from 3 to 5. **Gap (not caused by the drop):** neither version has a ceiling, but the fresh judge's defect was regrowth that is *too fast* (55 to 60% at 2 days). See the OWNER_NOTE. |
| 7 | `with _comp(t, "save_holds_no_furnace_herds")`: offline read of the canonical start save's world (seeder latch, RM_FurnaceHerd objects) | 5f8e6c28ec | `gpt_hunt_plausible/save_holds_no_furnace_herds` (no north-star bar; GPT-hunt row; still `required: true` in required_checks.json) | **COVERAGE LOST** | The row was **FAILING** when it was dropped: in the loop's own run `Transient/northstar/Pyrelands_main.json` (06:16) it reads "the save still holds the cut furnace-herd world leg (seeder component True, 2 RM_FurnaceHerd objects)". It was removed at 12:34 with no stated reason ("canonical-save rows dropped"). Re-run 17:04 PST: still FAIL (`seederPresent: true`, `herds: 2`, worldObjects 138, so the reader can see). Nothing else runs it. Filed RIMMASTER_STRIP_CANONICAL_SAVE_OF_CUT_FURNACE_HERDS. |
| 8 | `with _comp(t, "tribes_lookup_one_faction")` | 5f8e6c28ec | `gpt_hunt_plausible/tribes_lookup_one_faction` (no north-star bar; still `required: true`) | **COVERAGE LOST** (low stakes) | It was passing (1 TribeCivil faction, Deep Desert Tribes) and still passes offline. It is required, so modcheck now reads it as missing rather than passed. |

Not rows: the `WATERED_MIN_GAIN` comment (0.40 to 0.70) and the furnace note key `coldStartSeries` to `series` are
cosmetic. `_save_world_module()` (branch line 2400) is now an unused helper.

## Owed before the next Pyrelands done claim
- Restore rows 7 and 8 verbatim from `ff723afe8c` (or put an equivalent in the suite that runs
  `diag/save_world_check.py` and reports both verdicts). Do not drop them again unless their `required_checks.json`
  entries are retired with a reason. Row 7 will FAIL until RIMMASTER_STRIP_CANONICAL_SAVE_OF_CUT_FURNACE_HERDS is done.
  That FAIL is a real campaign finding outside the Pyrelands north star, so it must be reported, not hidden.
- Told to the loop in `/home/mandrake/rm/scratch/BENCH/ralph_pyrelands/ralph/OWNER_NOTE` (block CONDUCTOR PEEK 5:07 PM).
