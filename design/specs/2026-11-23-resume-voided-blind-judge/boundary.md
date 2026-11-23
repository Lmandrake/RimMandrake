# BOUNDARY: a voided blind judge run is resumed, never read as a verdict, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/run_void.py` (`voided_cycle_run`), `src/RimMandrake/rimflow/maturation.py`
(`blind_facts`, `next`, the `exit_met` clause, `launch_mod`), `src/RimMandrake/rimflow/maturation_dispatch.py`
(`add_blind`, `decide_blind`, `resume_kw`, `holder_launch`, `launch_stage`, `judge_reopen`, `judge-reopen`),
`src/RimMandrake/rimflow/modledger.py` (`seals`, `unseal`), `src/RimMandrake/rimflow/detached_helper.py`
(`run_session`). Item `RIMMANDRAKE_RESUME_VOIDED_BLIND_JUDGE_NOT_READ_AS_VERDICT`, written 2026-11-23. Each promise
has a test of its name in `src/RimMandrake/rimflow/selftest_resume_voided_blind_judge.py`.

Why: on 2026-11-23 the ExplosiveKnockback blind cycle 6 judge
(`rm-detached-bench-rimmandrake-judge-explosiveknockback-bli-1795437194`) was killed mid-work by a system fault and
voided (`void-5ae28fe22cb2`). Its interim exit block ("exit_met false", written before its own fix) stayed in
`cycle_6/SUMMARY.md`. The void moved its `blind_auto` entry out of the books, so `maturation.py next` read
"launch: none: blind cycle 6 is exit not met" and handed the cycle to the Conductor. Its ledger shard
`JUDGE.judge-1795437145` was sealed empty at the run's end, so its 10 real lines were refused as `SEALED_CHANGED`.
The Conductor's decision: a voided run gave no verdict; the cycle continues with the same judge's own session; if
that session cannot be resumed, the cycle opens fresh; the seal of a voided run's shard reopens for that run's own
lines.

## ACCEPTS (the only inputs this is built for)

- **a-dispatch-state.** The Dispatch tick's `state.json` (after `run_void.sync_dispatch`): a mod's `blind_auto` and
  `voided` books, where a voided blind run's entry keeps its `visit_id`, `cycle`, `unit` and `at`, and its
  `ledger_runs` entry keeps `run`.
- **a-run-record.** A detached run record (`detached_helper.read_record`) with `clone`, `at` and `ended`, and the
  transcripts under `~/.claude/projects/<the clone's project folder>/`.

## DOES NOT SURVIVE (not promised)

- **a-hand-launched-judge-outside-the-books.** A blind run that no `blind_auto` entry booked (a hand launch) and that
  was voided is not seen as the cycle's last run. Its block still reads as before.
- **the-old-clones-bundle.** The resumed run gets a fresh clone of origin/main. Work that the voided run left only in
  its bundle is not put back by this code (`detached_helper.restore_session_bundle` finds no record naming the
  session, because a killed run records none). Its shard lines land with `judge-reopen --lines`.

## PROMISES (each one is owed a test of the same name)

- **a-voided-judges-block-is-no-verdict.** When the newest booked judge run on the open cycle is voided and the
  cycle's record exists, `blind_facts` reads owed `resume`, the `exit_met` clause refuses with the void named, and
  `next` names the resume, never "launch: none". Red on the base: "exit not met" and "launch: none".
- **the-tick-resumes-the-voided-judges-own-session.** `decide_blind` launches on owed `resume` with `retry_of` = the
  voided entry and `judge_resume` = its ledger run, its session and its unit. The visit's automatic count, the
  certificate wait and a hand run from before the void do not stop it. A run after the void does.
- **a-fresh-judge-when-the-session-cannot-resume.** With no session found, or one at or past
  `holder_context_ceiling_tokens`, `decide_blind` launches with `judge_fresh` instead, and `launch_mod` gives that
  judge no resume section and tells it to move the cycle folder aside unread first.
- **a-counted-run-after-the-void-reads-normally.** A `blind_auto` entry on that cycle as new as the void (the resumed
  or fresh run's own entry) ends the `resume` reading: the block is read as before.
- **the-voided-runs-shard-seal-reopens-for-its-own-lines.** `modledger.unseal` lets the run's own lines append and
  lint without `SEALED_CHANGED`; `judge-reopen` refuses a run that is not void, lands only lines of that run, and
  seals the shard again.
- **the-resumed-judge-writes-its-old-shard.** `launch_stage` with `judge_resume` reopens `JUDGE.<run>` (no new judge
  run), gives the unit that writer, passes the session to `launch_mod`, and the brief opens with the judge's resume
  text, not the holder's.

## LIMITS

- **the session ceiling.** A session is resumed only under `holder_context_ceiling_tokens` (modledger.json, 400k; the
  owner's card of 2026-11-15). Danger: a resumed context past it rereads that much on every turn. No new number.
- **the kill loop.** No new bound. A resumed judge that dies again is voided again by `sync_system` and counted on
  `system_faults`; at `SYSTEM_FAULT_LIMIT` the mod reads `system_fault` and nothing launches (run_void.py).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
