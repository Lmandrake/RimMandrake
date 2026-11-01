# GATE_TAMPER_FIX_CTYPES_HALTS_ARM

## Problem
arena_gate.py TAMPER_RE refuses (tests UNMEASURED) any diff whose added lines name ctypes, _exit, frame access and
the like. The gate verdict is then `invalid`, the judge answers `invalid`, and arena_replay_run.unmeasured_result()
turned that into RunRefused: the WHOLE arm stopped. v3 hit it twice on RP_TESTENV_GUARD_UNSTICK_BLOCKS_ITS_OWN_SEQUEL
(its fix adds a ctypes pid_alive on nt). Any arm can hit it on that task.

## Rule (Conductor decision 2026-10-31, per CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM)
arena_gate.py and TAMPER_RE are not changed.
1. A MEASURED-INVALID gate counts as NOT ACCEPTED for that arm on that task. It is never dropped from the
   denominator, so no arm can gain from one (tripping TAMPER_RE on purpose scores exactly like a reject: the task
   is completed, zero points, its tokens count).
   Measured-invalid = the gate record is signed (`recorded` true), verdict `invalid`, and at least one step has a
   status other than UNMEASURED; the judge verdict is `invalid` (the judge answers invalid on every non-pass,
   non-fail gate before any model call).
2. The runner records it (runner.json `done[task]` with `invalid: {why, steps}`; the why names the UNMEASURED /
   INVALID steps and each one's reason) and goes on to the next task. Its log line says "counted NOT accepted".
3. arena_analysis: a task whose last judge event is `invalid` (not a pending marker) and whose latest earlier signed
   gate event on the same task and sha is `invalid` with at least one step measured is COMPLETED, not accepted
   (acceptance denominator, era gate, token efficiency all include it). The judgment is bound to its gate as tightly
   as the log allows (the judge event names no gate digest): the LAST gate event on that task before the judgment in
   log order, on the judgment's sha, with no other finished judgment of the task between them. Each arm's measured-invalid tasks are
   reported separately in report["gate_invalid"][arm] = {count, tasks: [{task, sha, steps}]} (present even when
   the verdict is UNMEASURED) and as `gate_invalid` in each arm's interval summary, so a TAMPER_RE false positive
   (ctypes) stays visible.
   This REPLACES the old analysis rule "a task is COMPLETED only when its last judge verdict is accept or reject"
   for this one case.
4. Still a stop (fail loud, task NOT recorded, rerun on the next start), unchanged: a gate whose every step is
   UNMEASURED (harness measured nothing: ARENA_GATE_WORK_REWIRE_OFF_DRVFS), an invalid gate record that is not signed
   or has no steps (gate crash / no JSON), and a judge `invalid` after a gate that passed or failed (judge fault). The
   analysis treats exactly these as not completed, as before, so runner and analysis agree.
5. A task interrupted by a runner restart is RERUN for that arm (it was never recorded), not scored invalid.

## Limits (GPT adversarial pass 2026-10-31, gpt_review.txt in D:\ClaudeWork\rimmandrake\foundry_arena\gatefix\invalid_rule)
- No gain over an honest reject at equal spend (selftest t_gate_invalid). A CHEAP invalid saves tokens like any
  cheap reject (give up early): that is the existing efficiency trade-off, not a new loophole.
- Residual: a runner killed exactly between a signed gate and its judgment, whose rerun yields the SAME head sha, a
  gate that crashes unsigned, and then is never rerun, would count that task completed NOT accepted (a loss for the
  arm, never a gain). Closing it needs the judge event to carry the gate's record_sha256 (arena_judge.py, unchanged).
- Pre-existing, not widened: unmeasured_result does not check `recorded` for a pass/fail gate.
