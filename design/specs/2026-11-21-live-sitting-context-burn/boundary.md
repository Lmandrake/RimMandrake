# BOUNDARY: resume or start fresh, the token estimate, and the pilot's agent launch, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/left_open_continue.py` (`resume_choice`, `progress_record`, `header`, `run`,
`conductor_resume`), `src/RimMandrake/rimflow/detached_helper.py` (`main` launch `--resume`, `--planned-resume` and `--agent`,
`launch_argv`, `FOOTER`), `src/RimMandrake/rimflow/modledger.py` (`tokens`), `src/RimMandrake/rimflow/testpilot_route.py`
(`brief`, `SIT_AGENT`) `src/RimMandrake/rimflow/maturation_autonomy.py` (`pilot_brief`, `pilot_env`, `launch_brief`) and
`src/RimMandrake/rimflow/maturation.py` (`launch_mod`'s argv).
Item: `RIMMANDRAKE_STOP_RESUME_REWRITING_CONTEXT_A_MILLION_AT_ONCE`, written 2026-11-21. The measurements are in
`design/specs/2026-11-21-live-sitting-context-burn/results.md` (this folder). The three choices are the Conductor's,
logged with `--per-ruling RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_continuation_progress.py`.

## ACCEPTS (the only inputs this is built for)

- **a-finished-run-record.** As `design/specs/2026-11-19-run-end-continue/boundary.md` ACCEPTS: a record in the
  detached run dir with `status`, `result`, `item`, `at`, `ended`, `session`, `model`, `env` and, for a continuation,
  `continue_root` / `continue_brief_src`.
- **item-notes.** `read_item`'s `notes` list: `{"id", "event", "ts", "text"}` per ledger event of the item.
- **a-session-transcript.** A claude `<session>.jsonl` under a project folder; its last main-thread usage is its
  context (`detached_helper.context_tokens`).
- **an-agent-name.** `RM_CLAUDE_AGENT` in a run's env (or `launch --agent NAME`): the name of a file
  `.claude/agents/<NAME>.md` in the run's clone.

## DOES NOT SURVIVE (not promised)

- **a-stale-progress-record.** The rule checks that a progress record exists, not that it is current. A run that wrote
  one `PROGRESS:` note early and none after is continued fresh from that one note; the briefs ask for a note after each
  experiment, and nothing enforces it.
- **a-progress-note-in-an-unpublished-clone.** The Conductor's `--resume` reads the notes from its own clone
  (`detached_helper.REPO`). A note the run wrote but never published is not seen there, and the resume goes ahead.
- **the-holder-resume.** `modledger.resume_plan` (a mod holder's session, his card 2026-11-15, "Try 400k first.") keeps
  its own rule. Its launches pass `--planned-resume` (promise below), and this page does not decide them.
- **real-tokens-of-other-text.** `tokens()` uses one measured ratio for all text. Text with a different ratio (code
  dense in symbols, non-English text) is counted with the same ratio.

## PROMISES (each one is owed a check of the same name)

- **a-small-session-resumes.** A continuation of a run whose session has a transcript and a context under
  `RESUME_WHOLE_MAX_TOKENS` resumes that session, whatever the time since the run ended, and whether or not a progress
  record exists. A blind role still starts fresh (run-end-continue page, `a-blind-role-never-resumes`).
- **a-large-session-with-a-progress-record-starts-fresh.** A continuation of a run whose session context is at or over
  `RESUME_WHOLE_MAX_TOKENS`, when a progress record exists, launches with no `resume_session`. Its brief is the header,
  the progress record (each note whole, oldest first) and the previous run's brief. The record carries `continue_how`
  `fresh` and a `continue_fresh_why` that names the context and the threshold.
- **a-large-session-without-a-progress-record-resumes.** The same large session with no progress record resumes, so no
  work is lost. The record carries `continue_resume_why` naming the missing progress record.
- **an-unmeasured-context-counts-as-large.** A transcript whose context cannot be read is treated as large: fresh when
  a progress record exists, else a resume.
- **a-lost-session-starts-fresh.** A session with no transcript cannot be resumed: the continuation starts fresh, with
  the progress record when one exists. A resume refused because the transcript vanished is retried once fresh.
- **a-progress-record-is-a-progress-or-left-open-note-since-the-chain-began.** The progress record is every note on the
  run's item (or its chain's first item) whose text starts `PROGRESS:` or `LEFT OPEN:`, written at or after the start
  of the chain's first run, plus a `LEFT OPEN:` paragraph from the run's result text. A note from before the chain
  began does not count.
- **a-capped-continuation-follows-the-same-rule.** A run the spend watchdog stopped, launched with `--continue-on-cap`,
  is continued under the same choice: large with a progress record is fresh, large without one is a resume.
- **the-conductors-resume-follows-the-same-rule.** `detached_helper.py launch --resume SESSION --item ITEM` with a
  session context at or over `RESUME_WHOLE_MAX_TOKENS` and a progress record on ITEM since that session's first run
  launches fresh: no `--resume`, the brief is the given brief, a fresh-session header, the progress record and the
  previous run's brief, and the output's first line says it went fresh and why. A small session, or one with no
  progress record, resumes as before.
- **a-holder-resume-is-not-turned-fresh.** `launch --resume SESSION --planned-resume` resumes as given, whatever the
  context and the progress record. The holder launchers (`maturation.launch_mod`, `maturation_autonomy.launch_brief`)
  pass `--planned-resume` with every `--resume` (found by the fresh reader of this fix: without it, every holder session
  between 150k and 400k with a `PROGRESS:` note was turned fresh, against his 400k card).
- **the-briefs-require-a-progress-note.** The detached footer (`FOOTER`), the pilot's sitting brief and the builder
  role `src/RimMandrake/rimflow/roles/builder.md` (which `.claude/agents/rm-testpilot.md` points at) each tell the run to write a `PROGRESS:` note on its item after each experiment or
  step, with its theory, experiment, reading and next action.
- **the-token-estimate-is-the-measured-ratio.** `modledger.tokens(text)` is the character count divided by
  `chars_per_token` in `modledger.json` (1.8, measured), rounded up; a config without it fails by name.
- **the-packet-bound-counts-real-tokens.** A packet built under a budget of 15000 holds at most 27,000 characters (it
  held up to 60,000 bytes under `bytes / 4`), or says OVER BUDGET. The config's `packet_budget_tokens` is 25,000 real
  tokens (about 45,000 characters); measured 2026-11-21, the three pilot mods' launch packets fell from 49,324-59,820
  characters to 41,477-43,177, and FlowWorks' never-dropped part (about 22.4k tokens with the holder lines) still fits.
- **a-pilot-sitting-launches-with-its-agent.** The Maturation tick's Test Pilot step launches with `RM_CLAUDE_AGENT`
  `rm-testpilot` in its env; `launch_argv` then passes `--agent rm-testpilot`; the sitting brief says the role file is
  the system prompt and does not ask for a Read of it. `launch --agent NAME` sets the same env.
- **a-missing-agent-file-is-repaired-not-refused.** An agent name with no `.claude/agents/<NAME>.md` in the clone is a
  fault of form: the run launches without `--agent`, its brief gets a line that names the role file to read, and the
  record carries `agent_dropped` with the cause.
- **a-continuation-keeps-the-agent.** A continuation of a run launched with an agent carries the same `RM_CLAUDE_AGENT`.

## LIMITS

- `RESUME_WHOLE_MAX_TOKENS` = 150,000 (`left_open_continue.py`). Danger: a resume carries the session's whole context
  into every request, and on a cache miss (past the 1 h cache life, or on a model change) its first request writes all
  of it again. Evidence, 2026-11-21 (`results.md` §(1)): three resumes of 252k to 362k contexts cost 0.72M to 1.20M
  weighted_v2 in their first request, 29% to 48% of a 2.5M cap; the one warm resume (306k) still spent 50% of its run
  on the context it took over. A fresh sitting starts at 74k to 105k (the same table), so a session at 150k carries at
  least 45k tokens more than a fresh start on every request. Under 150k a cold resume writes at most about 1.5 times what
  a fresh start writes, and keeps all of the session's knowledge, so it resumes.
- `chars_per_token` = 1.8 is a measurement, not a limit: the FlowWorks brief probe (56,704 characters more, about
  31,000 tokens more), the lower of the two measured ratios (tool results: median 2.0), so the estimate errs high and the
  bound is never looser than it says.

Later lists beside this page: `polish.md`.
