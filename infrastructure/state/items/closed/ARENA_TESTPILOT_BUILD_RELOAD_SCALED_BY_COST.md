# ARENA_TESTPILOT_BUILD_RELOAD_SCALED_BY_COST

Architecture-trial build, order 15 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build the TestPilot (design/RimMandrake/architecture_switch_harness_2026-10-29.md step 13; design/RimMandrake/testpilot_merged_2026-10-29.md §2.1 L6-L13, L9a, M1): fresh pilot passes per item against a game the machine worker owns; script canary as validity gate; the reload rule checked in order (recovery ladder, R0-R3) with the R3 drain scaled by the profile's measured reload cost (cheap: a few more unrelated tests then reload; expensive: keep testing while any test has value; never exhaustive; a maximum acceptance delay); re-test only scenarios whose declared footprint a rebuild touches (carried passes recorded); fix-now by class with MOD fixes built by a fix subagent and tested by the pilot; his presence at the machine is not an event, so there is no owner-return yield (owner 2026-10-30). Opus because pilot judgement is hard to validate. Mechanism never observed running: the TestPilot pass and its reload rule.

## criteria
Done when (the owner-return yield criterion was deleted: his presence triggers nothing, owner 2026-10-30):
- A1 L0: offline selftest and independent mutant rounds prove each criterion below on the fake driver
- A2 L1: a C# fix forces a logged reload naming its rule and the reload cost used, on a live minimal-list lane
- A3 L1: a pilot handoff loses no queued candidate, on a live lane
- A4 L1: a rebuild touching one scenario's footprint re-runs only that scenario plus any the taint note names
- A5 L1: no reload is logged without a rule over a live pass

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
