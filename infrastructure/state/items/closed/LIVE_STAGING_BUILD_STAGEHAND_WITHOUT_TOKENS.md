# LIVE_STAGING_BUILD_STAGEHAND_WITHOUT_TOKENS — deterministic Python staging for live rounds

Fast-testing #2 (`design/RimMandrake/fast_testing_2026-11-05/scored.md`, rank 2, score 4.60). Owner 2026-11-06: "yes and expedite".

## spec
- Today `src/RimMandrake/rimflow/relentless_game.py` takes the bridge ("relentless staging …: deploy and restart") and
  launches an LLM session with `stage_prompt(...)`. Every step that prompt asks for is already a script:
  `deploy_custom_mods.py --apply`, `modlist_swap.py`, `./game`, `winbuild.py`. Replace it with a Python state machine
  (build → deploy → mod list → restart/wait for load → ready) that calls those scripts directly.
- An LLM is launched only for a state the machine has no rule for (unknown first exception in Player.log, a stuck modal),
  with the state and log tail as its brief.
- Keep every existing guard: the owner's OWNER bridge hold, the never-flyer-flight rule, no fullscreen/focus,
  release the bridge on every exit path.
- Record each stage's duration (feeds PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES when it lands).

## verify
- Selftests drive the state machine with a fake Effects: happy path, deploy failure, load timeout, an unknown state
  falls back to the LLM, bridge released on each path, OWNER hold refuses.
- Live: one real staging round completes without an LLM launch, and its bridge hold for staging is measured
  (was 9-20 min).
