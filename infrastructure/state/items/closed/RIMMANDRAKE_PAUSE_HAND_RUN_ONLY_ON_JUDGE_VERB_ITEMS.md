# RIMMANDRAKE_PAUSE_HAND_RUN_ONLY_ON_JUDGE_VERB_ITEMS

## spec
`maturation_dispatch.add_blind` counted every run whose item contained the substring BLIND, started since the blind
cycle opened, as a hand-launched blind judge; if it ended without writing `cycle_<N>/`, the tick paused the mod
`hand_run_seen`. On 2026-11-17 that paused Pyrelands for 416 min on the fixer
`RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS` (tied to Pyrelands through note citations) and Graffiti
for 545 min on the builder `RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS`. Neither was a judge.

Fix: one rule, `maturation_dispatch._is_blind_item`. A `RIMMANDRAKE_<VERB>_...` item is a blind run only when it
has BLIND in it and its verb is JUDGE, CHALLENGE or PILOT. A name without the RIMMANDRAKE_ prefix has no verb, so
BLIND alone still decides. The rule is used by `add_blind`, `killed_runs`, `run_stages` and the hand-act census in
`maturation_hands`.

## criteria
- A builder, fixer or prover whose item has BLIND in it never gives `hand_run_seen`.
- A JUDGE, CHALLENGE or PILOT blind item still does.
- Swept over every run record (626 records, 331 distinct items): 23 BLIND items under the old rule, 18 under the new.
  The 5 dropped are BUILD_BLIND_CHALLENGE_LAUNCHER..., BUILD_GRAFFITI_..._BLIND_FOUND..., FIX_DESIGNER_STALL_READING_BLIND...,
  PROVE_SPEND_BLIND... and UNSTICK_DISPATCH_BLIND_CYCLES.... None was added.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_dispatch` (new cases after the FlowWorks
hand_run_seen case), plus the 17 other selftests that import maturation_dispatch or maturation_hands, all green.
Then `python3 src/RimMandrake/rimflow/maturation_dispatch.py status` must not read hand_run_seen for Pyrelands or Graffiti.

## refs
file: src/RimMandrake/rimflow/maturation_dispatch.py
file: src/RimMandrake/rimflow/maturation_hands.py
file: src/RimMandrake/rimflow/selftest_maturation_dispatch.py
