# BOUNDARY: the Designer mends the coverage judge's gaps in the session that holds them, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/designer_mend.py` (`plan`, `head`), `src/RimMandrake/rimflow/role_launch.py` (`mend_plan`,
its call in `decide_roles`, `session_part` in `_supervise_one`). Item
`RIMMANDRAKE_ASSIGN_LEFTOVER_CONTEXT_CHANGES_NEITHER_WORKER_HAD`, written 2026-11-24. Each promise has a test of its name
in `src/RimMandrake/rimflow/selftest_designer_mend.py`.

Why: the owner, 2026-11-20, on `RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION`: "For the Designer, you
could still allow it a chance to mend it during judgement while the context is fresh, even if it then gets blind judged
again. I'm trying to avoid the constant reloading of context for no gain here." Before this, each return from stage 5
started a new claude session that read the whole concept again.

Which session: the stage 5 run that read the verdict and returned, then the run that last finished the stage returned to.
Measured 2026-11-24 over the 13 stage 5 returns in the Designer clone's stage.json files: the run that wrote the design
was never under 55 minutes old at the return (3 had none on record; the rest were 80 minutes to 12 days). The stage 5 run had
just ended in 12 of the 13 (a program closed the other). So the design note's "writer only" rule would have resumed none.

## ACCEPTS (the only inputs this is built for)

- **a-stage-json.** A concept's `stage.json` whose newest result is an accepted stage 5 `return`.
- **a-coverage-verdict.** `coverage_verdict.json` in the same folder.
- **a-role-run.** The role's own run records in the Dispatcher's state (`rs["runs"]`, two days), with `concept`,
  `session`, `model_id`, `state` and `tokens`, and the transcripts under `~/.claude/projects`.

## DOES NOT SURVIVE (not promised)

- **a-hand-run-stage-5.** A stage 5 run that a seat made by hand (`bench-...`) is in no role record: the mend is fresh.
- **a-transcript-gone-between-decide-and-launch.** claude then refuses the resume and the run fails as any failed run.
- **a-codex-designer.** A Codex run has no claude session: its mend is fresh.

## PROMISES (each one is owed a test of the same name)

- **a-refusal-resumes-the-session-that-read-it.** After a stage 5 return on a `not_covered` verdict, the launch resumes the
  returning run's session, and the gap list is in the message.
- **a-program-return-resumes-the-writer.** When the program closed stage 5, the run that last finished the stage returned
  to is resumed while it is warm.
- **a-cold-or-large-session-starts-fresh.** A transcript last written 55 minutes ago or more, a context at or past the
  ceiling, an unreadable context, another model, a Codex run, a live run, or no transcript: the launch is fresh, and its
  `why` says the cause.
- **the-exam-and-the-judge-never-resume.** A return to stage 4 (the exam) is fresh, a stage 4 run is never resumed, and no
  launch at stage 5 (where the coverage judge reads) carries a resume.
- **only-the-return-resumes.** With any other newest result (a rejected mend, a done stage, a covered verdict, a verdict on
  another tree) nothing is resumed and nothing is said.
- **a-resumed-run-is-charged-its-own-part.** The claude result of a resumed session is the whole session; the run is
  charged that total less the session's earlier total. With no earlier total on record the run is UNMEASURED.
- **a-mend-that-cannot-look-launches-fresh.** A state that cannot be read never stops the launch; the cause is in its `why`.

## LIMITS

- **55 minutes** (`maturation_dispatch.RESUME_WARM_S`). Danger: a cold resume writes the whole context to the cache again.
  Evidence: 15 warm resumes cost 0.85M weighted tokens, 18 cold ones 13.8M (the scan report of 2026-11-20).
- **400k context** (`holder_context_ceiling_tokens`, modledger.json; the owner's card of 2026-11-15). Danger: each turn
  reads that context again. No new number.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
