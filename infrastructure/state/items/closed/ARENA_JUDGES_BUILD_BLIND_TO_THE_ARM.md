# ARENA_JUDGES_BUILD_BLIND_TO_THE_ARM

Architecture-trial build, order 4 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build the judge (design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.3): a neutraliser that turns an arm's head minus base over `area` into a diff with commit messages, trailers and branch names stripped and paths re-rooted; an Opus judge and a GPT judge (`gpt_consult.py`), each blind to the other and to the arm, both must accept, a split goes to a third fresh Opus run; hidden checks run for replay; each judge guesses the arm and the guess rate is tested (binomial p<0.05). The arm map lives where the judge process cannot read it. Opus because judge prompts and blinding leaks are hard to validate.

## criteria
Done when: a diff containing the arm name is caught by the neutraliser; a known-bad replay output is rejected; the judge process cannot open the arm map; the arm-guess report is produced.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
