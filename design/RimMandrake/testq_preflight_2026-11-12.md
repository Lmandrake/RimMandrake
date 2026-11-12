# testq preflight and the deploy memo (2026-11-12)

Owner, 2026-11-12: "I agree to anything that gets our test evals faster." Plan: `design/RimMandrake/live_test_speed_assessment_2026-11-12.md`
section 2C. Items: RIMMANDRAKE_TESTQ_PREFLIGHT_REFUSE_BEFORE_THE_GAME, RIMMANDRAKE_TESTQ_DEPLOY_MEMO_SKIP_UNCHANGED.

## INVALID census (86 jobs since 2026-11-06, 26 INVALID, from `testq/done/*.json`)

| cause (result cause: note) | jobs | preflight catches? |
|---|---|---|
| stale `ModsConfig.swap-active.json` (modset_builder RestoreRefused) | 10 | YES: `swap_marker` runs the real `take_before_copy` on a copy, moves the marker aside, logs it |
| HARNESS: modcheck exit 1, no sheet json | 6 | no (modcheck's own failure; no cheap predictor found) |
| LOAD: game crashed / mono_profiler / timeout during load | 7 | no (game state) |
| DEPLOY: companion DLL stale | 1 | no (already refused before load, in deploy) |
| CRASH: FileNotFoundError in phase load | 1 | no |
| GAME_DIED | 1 | no |

So preflight can only prevent about 38% of INVALIDs, all of them the swap marker. `dll_current` (DLL older than its C#, from
`dll_source_stamp`) and `proof_lines` (a proofs clause with no `live-proof` line) did not happen as INVALID in this window;
they are one git blob read each and guard the same class (a whole load that can only read UNMEASURED or run old code).
`TESTQ_PREFLIGHT_TIER_BUILD=1` adds `modset_builder --tier T` (10 s), off by default.

A refusal is a finished attempt: `outcome REFUSED`, `cause PREFLIGHT`, the note naming the check, no deploy, no load, no game guard.
The cause is in `schema.py` CAUSES, `testq_schema.json` and `contracts/models.py`. The marker fix is logged in the result note
of the job that went on to run. `TESTQ_PREFLIGHT=0` disables all; `TESTQ_PREFLIGHT_MARKER_FIX=0` reports instead of moving.
Selftest: `infrastructure/stevedesktop/selftest_preflight.py` (mutants: swap check off -> 6 FAIL, DLL check off -> 3, proof check off -> 1).

## Fixed cost

Phases per job: deploy (plan about 42 s with no drift) + attest (sha256 of every deployed file) + load. Measured over the
73 jobs that deploy mods: 28 followed a job on the same lane that deployed the same mods from the same source trees, 3477 of
9363 s (37%) of deploy+attest. Same-sha-as-previous-job was only 12 of 86, which is why the key is the per-mod git tree.

`deploy_memo.py` (switch `TESTQ_DEPLOY_MEMO=1`, default OFF: old behaviour): one memo file per lane, key = mods + git tree id of
each source dir + deploy tool blob, signature = (path, size, mtime_ns) of every file of the game's mod folders. Hit needs both;
a hit skips the plan and reuses the attest record. Companion check still runs. Selftest `selftest_deploy_memo.py`.

Multi-scene jobs: a proofs job (`run_proofs`) and a chain job already run all their clauses on ONE load. The four Pyrelands jobs
exist because `split_sweep` cuts a sweep at WORKER_DRIVER_CAP_S = 7200 s; one job would exceed the driver cap. What was repeated
per job was deploy and attest, which the memo removes on the second to fourth job.
