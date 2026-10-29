# ARENA_TASKS_BUILD_FROZEN_BEFORE_ASSIGNED

Architecture-trial build, order 1 of 16 (build order: design/RimMandrake/testpilot_merged_2026-10-29.md §6.3). Parent decision: TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD.

## spec
Build `arena_tasks.py census` and `freeze` (design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.1, §3.2). Census scans closed ledger items 10-12..10-27, keeps those with start+close, a resolving closing sha of 1-8 files, an offline-judgeable kind and an objective proof; labels each Clean or Escaped (a later `caused_by` rework within 7 days); writes one task JSON per item under D:\ClaudeWork\rimmandrake\arena\tasks\ with id, source_item, kind, size (1/2/4 points from the original diff), area globs, prompt as at claim time, criteria, proof, live (`none`/`minimal`/`minimal+deps` only: no `full` tier in the trial), hidden_checks (kept in the judge's directory) and base_sha. Freeze writes each file's sha256 to the event log before any assignment. Opus because labelling and writing hidden checks from rework items is judgement nobody can test mechanically.

## criteria
Done when: the census reports its pool count with a sanity probe (a hand-picked item it must find, and does); a changed task file is refused by its hash; no task has `live: full`; hidden checks are absent from every arm-readable path.

## verify
The forced-failure proofs in criteria, run by an agent other than the builder; then the blind GPT review.

## model
Opus: hard-to-validate work (owner's rule: Opus for code that is hard to validate).

## review
Blind GPT review before close (`gpt_consult.py`, fresh context, sees the code and this item's criteria only); at most 2 review rounds, then simplify or split. Proven by its own forced failure first. A different agent tests what was built, promptly (owner, 2026-10-29).
