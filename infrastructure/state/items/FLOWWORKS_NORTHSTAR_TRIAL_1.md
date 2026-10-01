# FLOWWORKS_NORTHSTAR_TRIAL_1

Parent of the FlowWorks north-star trial. Plan (authority for every child): `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` — bars and bindings
(§2), site preparation and preflight (§3), run sequence (§4), SHIPPED gaps (§5), driver requirements
(§6), proposed bar text (§7), GPT review (§9; prompt/answer in `Transient/northstar_trials_gpt/`).

Owner, 2026-09-30 (typed): *"Write out comprehensive northatar plans for all three and ticket them out
as trials for full completion. Use gpt reviews for their validation plan especially site preparation
that's often overlooked before a proper test setup. I'd like this to go very well. Then use ultra fast
python to drive the bridge to validate. Make it happen!"*

## children (ladder order)
1. `FLOWWORKS_NORTHSTAR_REVALIDATE_1` — VALIDATED again, with the pit bars folded in (BENCH, owner sitting).
2. `FLOWWORKS_NORTHSTAR_WIRE_1` — WIRED.
3. `FLOWWORKS_NORTHSTAR_SITE_PREP_1` — golden site + preflight.
4. `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` — first live run (RED expected).
5. `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` → 6. `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` → 7. `FLOWWORKS_NORTHSTAR_SHIP_1`.
Blocker for GREEN-full: `PITS_STALE_DEPLOY_COLLISION_1`.
Depends on the shared driver at `src/RimMandrake/Utils/northstar_driver/` (another agent builds it; §6 lists the calls).

## acceptance
- Every child closed against a real sha.
- `python3 -m modcheck.cli status FlowWorks` (from `src/RimMandrake/Utils`) prints GREEN, re-derived, on the full list.
- §5's SHIPPED gaps all closed or parked by his word.

## watch out
- STALE today means nothing: the stored GREEN is a pre-rename `FluidCanals` run against a deleted comp (MEASURED 2026-09-30).
- `modcheck run` REWRITES the live ModsConfig.xml — bridge holder only, with the §3.1 backups.
