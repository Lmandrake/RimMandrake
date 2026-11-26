# BOUNDARY: the stage ceiling's spend count, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py`, `arrivals`, `_off_ceiling`, `stage_spent` and `offline_tokens`
(what the tick compares with `stage_ceiling_tokens` before a launch). Item:
`RIMMANDRAKE_TRACE_SLACK_STAGE_SIX_SPEND_BEFORE_FIRST_VISIT`. Written 2026-11-19. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_stage_ceiling_arrival.py`, whose fixture is GimmeSomeSlack's real Stage 6 box of that
day (13 runs, nine started before the mod arrived at Stage 6, so the ceiling stopped it falsely). The count keeps no
state between calls, so the page has no LIFE CYCLES.

## ACCEPTS (the only inputs the count is built for)

- **the-status-page-boxes.** The runs `maturation_now.py` placed in the stage's box, each with its unit, start time
  (`runs_seen`) and its weighted_v2 tokens (else its measured list dollars converted once by
  `role_launch.list_usd_to_weighted`, else its cap), as `gather` reads them. Figures moved to weighted tokens
  2026-11-26 at 250,000 per list dollar (`RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS`).
- **the-stage-record.** The mod's `version/stage_record.json`: its `moves` (from, to, at) and its `since`.

## DOES NOT SURVIVE (not promised)

- **a-run-placed-in-the-wrong-box.** A run the status page puts in a stage it did not work on, but that started after
  the arrival, is still counted; placement is `maturation_now.py`'s.
- **a-move-with-an-unreadable-time.** It is skipped; the arrival falls back to an older move or the record's since.

## PROMISES (each one is owed a test of the same name)

- **counts-only-since-arrival.** A run that started before the mod's latest arrival at the stage is not counted
  toward that stage's ceiling (in-game, blind challenge and the offline build alike): it was spent on an earlier pass.
- **a-move-within-the-stage-is-not-an-arrival.** A cycle or visit opened inside the stage (a move whose from and to are
  the same stage) does not reset the count; only a move in from another stage does. A record with no such move reads
  its `since` for its current stage.
- **unknown-arrival-counts-every-run.** With no arrival read, every run in the box counts, as before this page.
- **void-runs-spend-nothing.** A void run (hand void, `void_system`, killed before it wrote a result) is shown apart as
  void spend and never counted (his card, 2026-11-18 11:06 AM PST, "Does not count").
- **this-steps-launches-count.** A launch this tick made that the status page has not placed yet counts at its
  weighted tokens, else its cap.
- **counts-weighted-tokens-not-list-dollars.** A run's spend is its run record's weighted_v2 `tokens`, never the CLI's
  `cost_usd`: a Fable 5.2 run the CLI priced at Opus rates (costBasis "unknown") counts its whole weight. A run with no
  tokens counts its list dollars at the one rate in `role_launch`, and a legacy `read_usd`/`release_usd` release lifts
  the ceiling through the same rate. Its test runs `selftest_stage_ceiling_tokens.py`.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
