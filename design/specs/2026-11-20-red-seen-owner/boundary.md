# BOUNDARY: the red-seen proof has an owner (maturation_dispatch.py red_seen_owed, cert_red_decide, cert_launch, editing_session), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py`. **This page covers only the certificate that refuses on
`red_seen` alone**: `red_seen_owed`, the `red_seen` kind of `cert_red_decide` and `cert_launch`, `red_seen_brief` and
`editing_session`. Item `RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION` (point 4); report
`design/specs/2026-11-20-context-kept-not-reloaded/report.md` §2 and change 5. Measured 2026-11-20: Gimme Some Slack's
certificate refused 18 of 26 bars on `red_seen` after two fixers edited its deciding test file; `stale_key` drops every
`red_seen` refusal and `cert_red_decide` acts only on `green` refusals, so nothing launched and no alarm fired from
2:14 AM to about 4:50 AM PST. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_red_seen_owner.py`.

## ACCEPTS (the only inputs these parts are built for)

- **a-certificate-reading.** `f["certificate"]` as `maturation.py certificate --json` gives it: `ok`, and `rows` with
  `status`, `clause`, `test`, `bar`.
- **a-run-record.** A detached run record (`detached_helper.all_records`) with `at`, `ended` (epoch seconds),
  `session` and `unit`.
- **a-decider-file.** The test table entry's `file` for each test, read with `git log -1 --format=%ct -- <file>`.

## DOES NOT SURVIVE (not handled)

- **two-runs-in-the-window.** When two runs were live at the commit time of a decider's last change, no session is
  resumed: the run starts fresh.
- **a-commit-landed-late.** The commit time is the clone's; a commit made in one run and landed by another reads as the
  first run's.

## PROMISES (each one is owed a test of the same name)

- **red-seen-only-launches.** A certificate whose every refusal is `red_seen` gives `launch` with `cert_kind`
  `red_seen` and the refused tests, where before it gave None.
- **mixed-refusal-keeps-its-route.** A certificate that also refuses a red decider (`green`) takes the red route
  (`cert_kind` `red`); one that also refuses anything else (`registered`, stale stamps) gives None, as before.
- **one-try-per-set.** After a launch on a set of tests, the same set refused again reads `stopped`, never a second
  automatic launch; a red-decider launch on the same tests does not count against it.
- **a-new-set-gets-its-own-try.** "The same set" means a set that shares a test with the last try's set (red or
  `red_seen` kind). A refused set that shares no test with it launches its own try. A set that still holds a test of the
  last try, and is not a strict subset of it, reads `stopped`.
- **a-proof-recorded-since-the-try-is-a-new-debt.** A decider of the last try whose newest red proof is later than that
  try (the certificate row's `proof_at`) was paid, so its refusal now is of a later edit. A `red_seen` set that shares
  only paid deciders with the last try launches. A proof older than the try, no proof, or a time that cannot be read
  pays nothing. Measured 2026-11-23 7:20 PM PST: a try of 2026-11-21 stopped Gimme Some Slack on new debts of T_CORE and
  T_STUB_JOINS (`RIMMANDRAKE_UNBLOCK_SLACK_FOUR_RED_DECIDERS_PAUSED_THE_MOD`).
- **the-certificate-row-carries-the-proof-time.** A `red_seen` row of `judge_certificate.certify` carries `proof_at`, the
  time of the decider's newest red proof, or None.
- **the-stop-says-what-is-owed.** The stop of a `red_seen` set says that a red proof is owed and never that a decider
  is red. The stop of a red set still says "still red".
- **clear-lifts-the-red-seen-stop.** `maturation_dispatch.py clear <Mod>`, which the stop names, lifts it.
- **a-voided-run-gives-its-try-back.** A voided or killed red-proof run takes its `cert_red_seen` entry out with its
  launch.
- **warm-editor-is-resumed.** `cert_launch` of the `red_seen` kind passes the session of the one run whose window holds
  the last commit to the decider's file, when that run ended under 55 min ago; ended 2 h ago, two runs in the window,
  or a file git cannot read, it launches fresh.
- **brief-names-the-proof.** The `red_seen` brief names `maturation.py red-seen <Mod> <test> --patch` for each test,
  and the item it files is named `..._RED_SEEN_OWED`.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
