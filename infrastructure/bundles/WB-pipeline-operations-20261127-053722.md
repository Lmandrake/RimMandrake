# WB-pipeline-operations-20261127-053722

Home pipeline:operations. Members: 1. State: DONE.

- `OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW`: closed at 6a6ace92ea (ledger afac486d92).
  - Step A: keep. The trigger of the dated wait happened. RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL closed at
    69f0e3e153 (fix db97e6c7e4 + 69f0e3e153).
  - Step B: the class guard is `src/RimMandrake/rimflow/selftest_dispatch_clone_sync.py --at ccfbc2b57e`. The `--at REV`
    replay was added at 6a6ace92ea. It shows 7 failed at ccfbc2b57e (the parent of the fix). It passes on HEAD and at
    69f0e3e153. The guard event was landed at a45c928cfb.
  - Step C: no code fix owed. The fix was already live. The close promise is
    `unit=rm-maturation-dispatch.timer reading=dispatcher/maturation/reading.json max_age=1h host=archmagi`. Archmagi
    series/maturation.jsonl at 2026-11-27T05:32:52Z read clone_behind_min 0.0.
- Open polish, not taken (this run did not change the file): the alarm line in the comments of
  `src/RimMandrake/rimflow/maturation_dispatch.py`, on `design/specs/2026-11-19-maturation-dispatch-reads/polish.md`.
