# Done claim

- true: Replay: at least 17 of the 20 R1/R2 items get the right mod added before repair; zero wrong additions. | evidence: `whittle/live_needs_enforce_absence_now_explicit/evidence/replay_enforce.txt` `whittle/live_needs_enforce_absence_now_explicit/evidence/replay_enforce_report.json` `whittle/live_needs_enforce_absence_now_explicit/evidence/selftests.txt`
- cannot tell: Negative control: zero additions on the last 50 PASS proofs, after the migration's `live-without:` lines. | evidence: `whittle/live_needs_enforce_absence_now_explicit/evidence/replay_enforce.txt` `whittle/live_needs_enforce_absence_now_explicit/evidence/negative_control_unrecorded.md` `whittle/live_needs_enforce_absence_now_explicit/evidence/migrate.txt` `whittle/live_needs_enforce_absence_now_explicit/evidence/migrate_absence_crosscheck.txt`
- cannot tell: One week after landing: runs failing on a mod-list cause in `runs.jsonl`, against a baseline recounted first. | evidence: `whittle/live_needs_enforce_absence_now_explicit/evidence/criterion3_census.txt` `whittle/live_needs_enforce_absence_now_explicit/evidence/criterion3_relentless_state.txt`

## Where each line stands

1. **Replay: true.** `replay --enforce` over the frozen fixture (57 failed runs, each at its own historical proof text,
   scripts and build sha) gets 17 of 20 R1/R2 items right, with 0 wrong additions. The 3 misses are named in the
   output (ART_OVERRIDE, TITANIC, WORLD_NULLTEX).
2. **Negative control: cannot tell.** Read as "a mod the gate would add that the passing run did not hold". The 50 PASS
   proofs before landing get 50 inferred mods. 24 fall at recorded times, and the run already held all 24. 14 more are
   shown held by the passing script's own rule. **0 are shown absent. 12 cannot be told**: 11 transitive About.xml
   dependencies and 1 HORRORS clause that can pass without its mod. No record of those runs' running loads exists.
   The migration over 215 proofs finds 0 conflicts, and its 41 absence-worded lines were read by hand: none
   contradicts intent.
3. **Week after landing: cannot tell yet.** The recounted baseline (7 days before; data starts 4 days before) has 15 of
   365 proof runs failing in-game on a mod-list cause, plus 126 pre-slot holds. Since landing: 0 of 209 proof runs,
   78 pre-slot holds. But Relentless ran only ~23 h of that week before it was switched off. The week closes
   2026-11-13T03:26Z, and nothing writes runs.jsonl now.

## What I'm least sure about
- That a snapshot interval [mtime, stamp] is the list the game was RUNNING. ModsConfig names the next load. A staging
  restarts the game on it at once, but a write by anything else would not.
- The 14 entries "shown held by the proof" rest on my reading of the frozen scripts (the exit-2-unless-running rules,
  C# types read). They are cited line by line in `negative_control_unrecorded.md`, but they are reading, not a recorded
  list.
- `relentless_names.py`, `relentless_live.py` and `relentless_live_round.py` have no clean code-review mark.

## What I did not test
- No live run: this is the offline lane. `env.running` (the running load on each admitted row) and the
  dependency-closure refusal are proven by selftests, not yet seen on a real Relentless row.
- The negative control on proofs after this change. Rows since landing were admitted only with every inferred mod
  running, so they cannot serve as a pre-gate control.
- `selftest_relentless_live_round.py` is RED on another lane's GSS `.criteria` file, which is not mine (filed as
  RIMMANDRAKE_FIX_CRITERIA_BULLETS_BREAK_PROOF_PARSE). Its other checks pass.
