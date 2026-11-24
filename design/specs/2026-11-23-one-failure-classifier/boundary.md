# BOUNDARY: one function decides what counts against a check, a trial or a retry (failure_class.py), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/failure_class.py` (the function), `src/RimMandrake/Utils/failure_counter_lint.py` (the
lint), and each counter in `census.md` that calls the function. Item
`RIMMANDRAKE_SHARE_ONE_FAILURE_CLASSIFIER_EVERY_COUNTER_ROLLED_ITS_OWN`. The rules:
`design/RimMandrake/standing_rulings.md` §No trial is spent by a system failure, §A fault of form is repaired where it
is found, and §Live tests have three kinds. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_failure_class.py`. Each counter promise has one in the selftest that it names.

Words: a **counter** counts bad outcomes of a piece of work and then stops, gives up, escalates or files something. The
**work** is the check, trial, run, item or mod that the counter is about. An outcome **counts** when it is the work's own.

## The danger

- **The failure (measured 2026-11-23).** The in-game visit feed (`testq/visit_feed.py`) counted four lane refusals as
  failures of six FlowWorks chains, stopped sending them, and read `quiet` for six hours. The rule "a run that was
  killed, timed out, refused or never started spends no trial" was already built, in `run_void.py`, and the feed did
  not call it. The owner: "Why did setup failure count as mod failure? We fixed this!"

## ACCEPTS (the only inputs this is built for)

- **an-outcome-word.** One of the seven outcomes of `live_kinds.py`, or one of the run words below, in any letter case.
- **a-row.** A `rows.jsonl` row with `outcome`, or with `verdict` and `class` (read by `live_kinds.outcome` first).
- **a-run-record.** A detached run record (`detached_helper`), read by `run_void.system_cause`.
- **a-testq-record.** A finished testq record: its job, its result and its `cancelled` mark, for one chain or the job.
- **a-launch-refusal.** The text of a launch that did not start.

The run words: KILLED, TIMED OUT, REFUSED, NEVER STARTED, STOPPED (a person stopped or cancelled it), ACCOUNT LIMIT,
ENDED (the run ended on its own merits and the work is not done), BAD REQUEST (the request itself is wrong, so the same
request gives the same refusal).

## DOES NOT SURVIVE (not promised)

- **a-false-record.** A record that says the wrong outcome is believed.
- **a-counter-of-another-shape.** The lint reads Python by AST. It does not see a counter in shell or PowerShell, or a
  counter whose names hold none of its failure words.
- **a-machine-brake.** A counter about the machine itself (a lane brake, a system-fault meter, an alarm on a timer) counts
  machine faults by design. The census names each one, and the lint's list gives its reason.

## PROMISES (each one is owed a test of the same name)

- **only-the-works-own-outcome-counts.** MOD FAILURE, ENDED and BAD REQUEST count. SUCCESS, RANDOM MISS, ENVIRONMENT
  FAULT, APPARATUS FAULT, UNRESOLVED, COULD NOT LOOK, KILLED, TIMED OUT, REFUSED, NEVER STARTED, STOPPED and ACCOUNT
  LIMIT do not.
- **an-outcome-nobody-can-class-does-not-count-and-is-named.** An unknown word, an empty word or a wrong type does not
  count, reads `classed` False, and its text names the word.
- **a-run-record-reads-as-run-void-reads-it.** For a detached run record, the answer is a system cause of
  `run_void.system_cause`, else ENDED. A record that is missing or has no result is UNCLASSED. A refusal's result text is kept whole.
- **a-testq-job-reads-its-cause.** DONE with a FAIL row of the chain reads MOD FAILURE, with a PASS row SUCCESS, with
  neither COULD NOT LOOK. The causes PREFLIGHT, BLOCKED_SELECTION and SCHEMA read BAD REQUEST. Any other
  REFUSED reads REFUSED. INTERRUPTED reads KILLED. INVALID reads by `invalid_class`: TEST or DELIVERY is APPARATUS FAULT,
  GAME is UNRESOLVED (the mod could have spoiled it), and CANARY, HARNESS and DEPLOY are APPARATUS FAULT. A cancelled
  job reads STOPPED.
- **the-count-names-what-it-left-out.** `count` gives the number that counts and the words it left out with their
  number, so a counter can report them.
- **an-error-text-is-the-tools-or-the-records.** The error text of our own tool reads TIMED OUT or APPARATUS FAULT for a
  timeout, a crash, a lock or a traceback, and BAD REQUEST for a refusal. The reading keeps the whole explanation on one line.

## COUNTER PROMISES (each one is owed a test of the same name, in the selftest that it names)

- **visit-feed-spends-a-chain-only-on-its-own-fault** (`Utils/selftest_steve_visit_feed.py`). An INTERRUPTED, INVALID or
  cancelled run, and a DONE run that read no verdict, do not spend a chain. The chain waits (`BOUNCE_BACKOFF_S`, doubled
  for each such run in a row that held the lane, up to `FAULT_BACKOFF_MAX_S`), is named in `faults`, and is sent again.
- **a-dry-chain-is-read-from-done-runs-only** (`testq/selftest_testq.py`). The filler's chain history takes a run as
  measured or dry only from a DONE job. A run of any other outcome is `void`.
- **a-verdict-is-not-dropped-by-a-crash** (`testq/selftest_ingest.py`). An ingest that crashed or timed out does not
  spend one of its tries: the record waits and is tried again. A refusal by rimflow counts as before.
- **a-quarantined-job-is-queued-again** (`testq/selftest_testq_fault_monitor.py`). A job quarantined by a machine fault
  is queued again however often that happened, inside 48 h.
- **a-refused-resume-is-tried-again** (`rimflow/selftest_stop_resume.py`). A resume whose launch was refused is never
  given up. It is tried again after `REFUSED_WAIT_S`, and said once when it has been refused `MAX_TRIES` times. A saved
  refusal record leaves the stopped run eligible for retry. The successful relaunch is recorded as its successor.
- **a-red-fixer-that-died-spends-no-attempt** (`rimflow/selftest_red_dispatch.py`). A launch that never started and a run
  that died of a system cause do not stop the red item. The next try waits `SYSTEM_WAIT_S` and stays inside the night cap.
- **a-red-that-returns-after-its-fix-gets-a-new-attempt** (`rimflow/selftest_red_dispatch.py`). An attempt made before the
  red item's last close on the ledger is not a failed attempt. An attempt after the last close that ended with the item
  open stops the item, as before. The danger: 2026-11-24, a red that came back stood 8 hours with no fixer.
- **a-list-run-that-died-spends-no-run** (`rimflow/selftest_list_dispatch.py`). A Work or Shape run that died of a system
  cause is not one of `max_runs_per_item` and stops nothing. Launches that never started hold the item for
  `SYSTEM_WAIT_S`, said once, and never stop it, except a refusal of form, which names its repair.
- **an-unmeasured-run-is-in-no-pilot-streak** (`rimflow/selftest_testpilot_route.py`). A verify that carries an outcome
  that does not count is in no streak, and the verdict names it. A verify with no outcome counts as before.
- **ingest-says-could-not-look** (`testq/selftest_ingest.py`). A `partial` run holds no FAIL row: what it
  lacks was not measured. It is recorded with outcome COULD NOT LOOK.
- **a-killed-run-is-no-cycle-on-the-page** (`Utils/selftest_maturation_now.py`). "has run N times" counts the runs that
  are not void and not killed.
- **an-account-ending-after-work-spends-no-resume** (`rimflow/selftest_role_resume_account.py`). A role run that did work
  and then ended on the account spends no resume. Three resumes in a row that did no work are given up, as before.
- **a-dead-author-spends-no-converge-round** (`rimflow/selftest_designer_cleanse.py`). A converge author that died and
  changed nothing, a cold sort unreadable twice and a verifier that gave a record no verdict twice spend no round. The
  mod reads blocked, could not look, and the same round runs on the next start.
- **a-killed-repair-run-is-no-repair** (`rimflow/selftest_repair_at_refusal.py`). A repair run of the tick that was killed
  from outside reads `void`. Its refusal coming back is no fault of substance, it is none of `FAULT_REPAIRS_MOST` runs,
  it resets no fault count, and the next one waits `VOID_REPAIR_WAIT_S`.
- **a-killed-continuation-spends-no-slot** (`rimflow/selftest_left_open_continue.py`). A continuation that died of a system
  cause is none of the three a day.
- **a-dead-wake-is-tried-after-its-cooldown** (`testq/selftest_testq_steward.py`). A wake of the lane's steward that died on
  the login after its quick retries, or was killed from outside, is tried again after its cooldown. A surviving wake
  wrapper records the child's signal in the exit file. A wake that ended in its own error is told and not tried again.
- **a-dead-render-spends-no-attempt** (`Utils/art/selftest_facing_regen_batch_trailer.py`,
  `Utils/artpipe/selftest_requeue_flakes.py`). A render that died spends no attempt and no requeue.
- **the-lint-refuses-a-new-counter** (`Utils/selftest_failure_counter_lint.py`). A new counter in pipeline machinery whose file does not call the function, and that
  is not in the lint's list with its reason, is refused by name. The real tree passes. An entry of the list that no
  longer matches anything is refused as stale.

## LIMITS

- `visit_feed.FAULT_BACKOFF_MAX_S` 7200: the danger is a chain that the lane cannot measure, sent again every 10 min (20 h
  of lane lost on 2026-10-25). Twelve sends a day of a median 4.1 min job hold under one hour of lane.
- `SYSTEM_WAIT_S` 3600 in `red_dispatch.py` and `list_dispatch.py`, `REFUSED_WAIT_S` 3600 in `stop_resume.py`, and
  `VOID_REPAIR_WAIT_S` 3600 in `maturation_dispatch.py`: the danger
  is a launch sent again on every tick into the same refusal (the night of 2026-11-20, `REPAIR_LAUNCH_MOST`).

Lists beside this page: `census.md`, `polish.md`.
