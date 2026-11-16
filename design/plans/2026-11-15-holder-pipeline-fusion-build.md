# Holder–pipeline fusion: build plan

Spec: `design/specs/2026-11-15-holder-pipeline-fusion.md` (Option B, built as A first; his card answers, 2026-11-15, at its top).
First item: `RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE` (steps 1–2 here). Pilots, side by side: Explosive
Knockback, Gimme Some Slack, FlowWorks; a fix to the system found on one lands for all three.

Every number a step needs (the 400k holder ceiling, the 15k packet budget, the 45-minute lease) lives in ONE config,
`src/RimMandrake/rimflow/modledger.json`; code reads it, nothing restates it.

Each step is its own item, filed `--caused-by RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE`, with its
acceptance test written and watched failing at filing. No step redirects, archives or deletes an old per-mod file
before step 4 (cutover).

## Step 1 — amend the spec, write this plan

Done by the first item (e44792cf2f). Acceptance: none, prose (the spec carries the four answers and his additions; no line still
says two pilot mods, a 600k ceiling, or that a judge fixes what it finds).

## Step 2 — `modledger`: append, lint, show, packet, views

`src/RimMandrake/rimflow/modledger.py` on rimflow's shard code (`model._append_locked`, `model._dir_lock`,
`model.canonical_order`; `ledger_lint.lint_blob` for MALFORMED / NO_NEWLINE / NOT_APPEND / DUP_DIFFERENT), config
`modledger.json`, ledgers at `design/concepts/<Mod>/ledger/<WRITER>.jsonl`, views at `design/concepts/<Mod>/ledger/views/`.

Done by the first item (6b4fb634a7; backfill and compare 872a7657e2). Acceptance test:
`python3 src/RimMandrake/Utils/run_selftests.py --only modledger` (the test is
`src/RimMandrake/rimflow/selftest_modledger.py`; it is in `pipeline_tests.json`, so `./publish` runs it). It fails on
the base commit (no `modledger.py` there).

## Step 3 — backfill and shadow views for the three pilots

`modledger.py backfill --mod <Mod>` reads today's stores (stage record, journal "stands", bars, coverage verdict and
fixes, exam, results, open items naming the mod, his answers) and appends one `BACKFILL` event per fact, each citing
its old file. Views are generated beside the old files; nothing is redirected. Explosive Knockback first (the smallest;
done by the first item at 872a7657e2: 383 events, packet 14,980 of 15,000 tokens, `compare` 3 of 8 agree),
then Gimme Some Slack and FlowWorks:
`RIMMANDRAKE_BACKFILL_SLACK_AND_FLOWWORKS_LEDGERS_IN_SHADOW`.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_backfill_accept.py GimmeSomeSlack FlowWorks`
(each mod: a ledger with BACKFILL events that all cite an existing file, lint clean, views current, packet under budget
and naming what it left out).

## Step 4 — cutover, the same day for each mod

When a mod's shadow views have agreed with its old files (compared at every dispatcher tick for a few days, and read
against them by a judge who did not write the backfill), its old files are archived read-only with their provenance and
every writer to them is redirected to `modledger append` or refused: `RIMMANDRAKE_CUTOVER_PILOT_MODS_TO_LEDGER_SAME_DAY`.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_cutover_accept.py ExplosiveKnockback GimmeSomeSlack FlowWorks`
(per mod: `stage.json`, `journal.md`, `version/stage_record.json` are generated views or archived copies, and no module
under `src/RimMandrake/` opens one of them for writing).

## Step 5 — stage runs start from the packet (Option A)

The dispatcher grants the holder lease (`modledger grant`), launches the stage run with the packet as its opening
context, records `run.start`/`run.end` itself, and flags a run that ends without a `session.checkpoint` of the fixed
shape: `RIMMANDRAKE_START_PILOT_STAGE_RUNS_FROM_LEDGER_PACKET`.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_packet_runs_accept.py` (a dry dispatcher tick
for a pilot mod builds a launch whose brief embeds `modledger packet` output, grants a lease with a higher token than
any before it, and writes `run.start`).

## Step 6 — resumed holder sessions, 400k, kill-and-resume (Option B)

The holder's session id is a `session.id` event; the dispatcher resumes it (`claude -p --resume`) for each of its
stages and through the judging phases, rotates it at the first boundary past `holder_context_ceiling_tokens`, and after
a forced stop reconciles (clone, unpublished commits, bridge) before it resumes or falls back to the packet. The holder
works all its mod's open tickets together and carries into the next Design Version:
`RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME`.

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_resume_accept.py` (offline, faked claude: kill a
holder mid-stage; the next launch reconciles, resumes the recorded session, avoids a refuted cause, does not re-ask an
answered question, and rotates once the recorded context passes the configured ceiling). The live half (a real resumed
detached systemd run) is recorded UNRUN until it runs.
