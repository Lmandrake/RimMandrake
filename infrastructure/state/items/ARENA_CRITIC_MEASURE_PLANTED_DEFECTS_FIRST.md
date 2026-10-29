# ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST

Architecture-trial build, order 10 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build and run the critic calibration set (design/RimMandrake/testpilot_merged_2026-10-29.md §6.3 day 2): about 20 known-good and 10 planted-defect frozen candidates (planted defects re-introduce real Escaped defects from the census), put through the trio critic and the judge, giving the first measured false-reject and miss rates (flaws O2, O6). Then re-run the simulator with the measured rates. Opus because building realistic planted defects is judgement.

## criteria
Done when: false-reject and miss rates for critic and judge are written with counts and intervals to the event log; each planted defect has a recorded original rework item; the simulator re-run uses the measured rates.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
