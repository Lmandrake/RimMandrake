## spec
Codex full-file review of `src/RimMandrake/rimflow/maturation.py` (2026-11-18, while reviewing RIMMANDRAKE_SCOPE_RUN_SPEND_TO_VERSION_OLD_RUNS_LINGER) found six flaws that predate that change. Each, with its scenario and smallest fix as Codex gave it:
1. `read_run_spend` (~line 1531): a RUN_SPEND file that exists but cannot be read reads as `[]`: reports omit its charges, and `record_run_spend` may re-add an old unit and rewrite the unreadable file. Fix: tell FileNotFoundError apart from other read failures, return an UNMEASURED reading, and refuse to write without readable history.
2. `spend_by_stage` (~line 1598): a stage whose every row has `tokens=UNMEASURED` reads `tokens: 0` in next, pass_cost's by_stage and show ("0 weighted tokens"); wall time likewise. Fix: per field, UNMEASURED when no row measured it.
3. `next_version` (~line 1481) resets cycle, visit and arrival counters but keeps their numbered evidence folders: a previous version's blind cycles 1 and 2 block the new version's first cycle as "past", or its old exit is read instead of a fresh judge; visits and walk briefs collide the same way. Fix: archive the previous version's numbered evidence folders at rollover.
4. `build_facts` (~line 1884) omits `owed_scene_parts`: with a runnable bar whose scene's owed_parts_item is open, evaluate refuses the advance but the builder is launched with `refused_bars=[]`. Fix: merge the owed-scene bars into refused_bars, kept through the walk/live exemptions as evaluate keeps them.
5. The live-driver brief (~line 3188) tells a driver a same-visit rerun supersedes a FAIL; the reader refuses that visit for its earlier FAIL (and a source change breaks its one-build check). Fix: the brief asks for the road back and a new visit after a failure.
6. `add_spend` (~line 1513) reads the record, then writes it back unlocked: an `advance` in between is erased. Fix: hold `_mod_lock` across add_spend's read, modify and write.

## verify
Acceptance test: drafted, NOT yet watched failing (the filing run was closing another ticket): one case per point in `src/RimMandrake/rimflow/selftest_maturation.py` built from the scenario above, each watched failing on origin/main first; expected 6 new checks PASS after the fix.

## criteria
Each of the six behaves as its fix says, with its check.

## refs
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/selftest_maturation.py
