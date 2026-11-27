# BOUNDARY: the void rule on the pipeline's counters, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/run_void.py` (`resolve`, `sync_system`, `heal_system`), the Designer chain count in
`src/RimMandrake/rimflow/role_launch.py` (`refuse_now`, `give_back_chain`, `close_concept`, the chain sweep in
`decide_roles`, `never_opened`; the stage-5 judge look: `judge_looked`, `judge_look_close`, `reclass_judge_look`), the certificate rerun in `src/RimMandrake/rimflow/maturation_dispatch.py` (`cert_rerun_decide`,
`cert_rerun_launch`) and the Designer's loop ceiling in `src/RimMandrake/rimflow/designer_stage.py` (`loop_start`,
`loop_spend`, `ceiling_crossed_at`, `loop_ceiling`; `judge_look_rejection`, `reclass_judge_look`). Item: `RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE`, written
2026-11-19. The owner, 2026-11-18: *"I will not accept ANY system that pointlessly expends such statistical measurements
based on failed system calls or behavior."* Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_void_counters.py`. This page covers only the six places a review named; the rest of
the void rule is `run_void.py`'s docstring and `design/RimMandrake/pipeline_trial_counters_census_2026-11-18.md`.

## ACCEPTS (the only inputs these readers are built for)

- **a-run-record.** A detached run record (`detached_helper.read_record`): `status`, and at finish a `result` of the
  form `outcome()` writes, `<service result> (<exit code> <exit status>)`. A finish run without systemd's variables
  writes `unknown (- -)` when the agent's own result JSON was read, and `killed: unknown (- -)` when it was not.
- **the-dispatch-books.** `state.json`'s per-mod books (`run_void.DICT_BOOKS`, `LIST_BOOKS`, `ONE_BOOKS`) and the
  `voided` list `sync_system` moves entries into, each moved entry holding its `entry` with the run's `at`.
- **a-chained-run-now.** A Designer run-now request carrying `chain_key` and `chain_stage` (`chain_ask`).
- **a-concept-stage-file.** A concept's `stage.json` as `designer_stage.load_state` returns it: budget charges with
  their `ref`, coverage rounds, results, and `voided.spend_refs` (`run_void.sync_stage`).
- **a-certificate-rerun.** `state.json`'s `cert_rerun` entry and the rerun's result file (`rerun_result`). The rerun's
  unit (`rm-cert-rerun-*`) has no detached run record: its only evidence is that result file and its age.

## DOES NOT SURVIVE (not promised)

- **a-void-mark-that-raises.** A Designer run the machine stopped before it wrote `result.json` is void_system; if
  marking that on `stage.json` (`stage_void`) itself raises (a failed read or write just after the close wrote the same
  file), the rejection counts and is routed as before, said once by the `role:<Role>:stage_void` alarm, and nothing
  retries the mark. A second failure while the first is handled: rare by the owner's card of 2026-11-19.
- **a-certificate-rerun-killed-early.** A rerun unit that dies well before its bound reads `live` until
  `RERUN_MAX_S` has passed since it started; only then is it tried again.
- **a-stage-machine-refusal-loop.** A run-now the stage machine refuses (`stage machine: ...`: its state, or a
  stage.json it could not read) keeps its chain spent; see `a-gate-refusal-keeps-its-chain`.

## PROMISES (each one is owed a test of the same name)

- **unknown-result-with-its-own-answer-counts.** A finished record whose result reads `unknown (...)` holds the agent's
  own result JSON (`outcome()` writes `killed: unknown` when there is none), so it is a run that ended on its merits:
  it counts, is final, and heals a void_system class an earlier read gave it. One with no JSON is void_system.
- **mod-since-finds-moved-system-voids.** `void --mod MOD --since TIME` finds a run `sync_system` already moved out as
  void_system, by its entry's saved `at`, and makes it a hand void; a run already hand-voided is not taken again.
- **a-killed-pilot-launch-spends-no-holder-try.** A hand `pilot-launch` whose run died of a system cause (killed,
  timed out, the CLI exiting with no result of its own) is classed void_system and moved out of `pilot_launches`, so
  `holder_spent` does not read it as a holder run that ended with its items still open.
- **a-killed-red-decider-builder-spends-no-try.** A red-decider builder (`cert_red`) whose run is void_system goes out
  with its `launches` entry, so `cert_red_decide` does not stop on "ended and still red"; it comes back if the run heals.
- **ledger-runs-stay-for-their-run-end.** `ledger_runs` is bookkeeping, not a counter: every unit in it sits in another
  book too, which classes it. A void_system run's `ledger_runs` entry stays, so `end_ledger_runs` still records its
  `run.end`, and its ceiling release is still given back.
- **a-certificate-rerun-left-no-result-is-tried-again.** A rerun that left no result of its own by `RERUN_MAX_S` after
  its start (killed or timed out) spends no rerun of its build key: it is started again, within `launch_tries`, and
  only then owes one repair run with the evidence (form_fault; never a wait for a hand).
- **a-run-now-never-launched-gives-its-chain-back.** A chained run-now consumed without a launch because it expired,
  the pipeline is paused, the owner holds the concept, or the role's off switch is set, gives its chain back: the
  day's count less one and its stage off the day's list.
- **no-sweep-while-the-role-is-off.** While a role's off switch is set, the chain sweep asks nothing for it, so a
  given-back chain is never re-asked and refused every tick.
- **a-concept-no-run-opened-is-not-swept.** The chain sweep asks no run for a concept no run has opened (stage 0, no
  result, no open run, no `open` row in its history: `role_launch.never_opened`), and the Designer stall reader
  (`ops_watch._q_designer`) counts it as pending to nobody, by the same rule. The sweep is for a concept whose chain
  broke; a new concept moves only on a hand run-now (`role_launch.py run-now`), after its mod's readiness list reads
  READY and `pipe on <Mod>` cites it. Before this, `designer_stage.py init` on a new mod's concept was swept into an
  opus Designer run 10 minutes later, the Designer role's `enabled: false` notwithstanding (that flag means "run-now
  only", and every Designer run is a request, so it never stopped one). A concept whose first run opened and died
  still has its `open` row and is swept as before. Added 2026-11-19 by
  `RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS`.
- **a-gate-refusal-keeps-its-chain.** A run-now refused by the stage machine, the band, the cap, the daily cap or the
  ops reading keeps its chain spent: the sweep re-asks a ready concept every tick, and the daily chain cap is what
  stops that ask-and-refuse loop.
- **void-runs-spend-nothing-on-the-loop-ceiling.** The Designer's judge-and-rework loop counts no void charge toward its
  ceiling, its crossing or its start: a hand-voided run's or judge's (`voided.spend_refs`), a void_system judge round's
  (with its second reader), and a Designer run whose rejection is marked void_system. The void spend is shown apart in
  the ceiling's line.
- **a-done-run-after-the-voids-lifts-the-void-hold.** A concept at `run_void.SYSTEM_FAULT_LIMIT` void_system runs in a
  day is held from every chain (`role_launch.void_held`) until the day turns, or until a run on that concept that was
  launched after the last of those voids finishes `done`. That run proves the system cause repaired, so the sweep
  chains the concept again the same day. A failed run, a done run launched before the last void, another concept's
  run, or a void unit lifts nothing. Added 2026-11-21 for incident queues-20261121133600 (Pyrelands sat ready 4.6 h
  after an accepted hand run-now).
- **an-unsigned-judge-look-is-the-judges-result.** A stage-5 Designer unit that ended at its coverage judge step, with
  no result.json, no claude result and no transcript, is the judge's look when the concept's `coverage_verdict.json`
  is unsigned, its judge started inside the unit's window, and its round did not die of a system cause
  (`coverage_judge.void_cause`). The run is not void_system and adds no void fault. It reads done at 0 tokens: the judge
  charges its own look by its own rules. Its stage.json rejection is marked `judge_look`: no Designer retry, no
  rejection for `rejection_parked`, no loop spend for the run. Stage 5 is chained again when that is the act the
  verdict names: a fresh judge look after a judge's own fix, the Designer's mend after a plain refusal. A stop, a
  park, or an advisory verdict that waits for a calibrated brief chains nothing. Added 2026-11-27 by
  `RIMMANDRAKE_CLASS_UNSIGNED_JUDGE_LOOK_AS_VERDICT_FOURTH_VOID` (Wrecked Machines: the judge fixed `scenes.json`
  itself, its step exited `STOP_EXIT`, and the fourth void of the day stopped the chain).
- **a-unit-with-no-look-of-its-own-stays-void.** A unit killed before any verdict, a unit whose only verdict on file
  was left by an EARLIER unit, and a verdict whose own judge call died stay void_system, as before. A unit whose model
  started (a transcript) is harvested as before.
- **a-void-judge-look-is-reclassed-by-its-verb.** `role_launch.py reclass-judge-look <unit> --why "..."` corrects a run
  an earlier harvest classed void_system that was its judge's look, by the same rule over the window up to its void:
  its void fault comes off the day's count, the run reads done by `judge_look` at 0 tokens, and its stage.json
  rejection loses its void_system marks and takes `judge_look`. A unit with no look of its own, or one already
  reclassed, is refused, and nothing is written.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
