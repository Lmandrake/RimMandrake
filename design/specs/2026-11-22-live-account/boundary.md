# BOUNDARY: which Claude account a machine is logged in as, read in one place, Design Version 0.1.0

Code: `src/RimMandrake/Utils/account_live.py` (`read`, `parse`, `name_of`, `why_of`).
Item: `RIMMANDRAKE_MERGE_LIVE_ACCOUNT_READERS_SIX_PARSE_ONE_STATUS`, group 2 of
`design/specs/2026-11-22-pipeline-single-source-sweep/report.md` (candidate 2), written 2026-11-22.
Each promise has a check of its name in `src/RimMandrake/Utils/selftest_account_live.py`.
Proof that the one home equals or beats each old reader: `equivalence.md` beside this page.

The fact: the account that a machine's Claude sessions use now, as `claude-account --json status` names it in its
`live` field. Every reader of that fact calls `account_live.read`: `slot_allocator.live_login_name`,
`switching_plan.switcher_status`, `running_now.collect_inuse`, `account_handover` (`check`) and
`account_usage.remote_live` and `run_host.read_facts` (another machine, over ssh). For the usage poller,
`account_usage.live_email` reads this machine's session config file. The poller matches that email against its own
registry.

## ACCEPTS (the only inputs this is built for)

- **a-status-output.** The exit code and stdout of `claude-account --json status` (this machine), or of
  `bash -lc 'claude-account --json status'` over ssh (another machine). The status is one JSON object with a `live`
  key; text may come before or after it (a warning line, a login shell's banner, a trailing note).
- **a-run-seam.** An optional `run(argv, timeout) -> (rc, stdout)` from a caller that already has a world seam
  (`running_now.Env.run`). It may raise `subprocess.TimeoutExpired` or `OSError`.
- **the-exe-seam.** `RM_CLAUDE_ACCOUNT` (read at call time), else `claude-account` on PATH, else
  `~/.local/bin/claude-account`. A caller may pass `exe=` (switching_plan passes its `CA`). This is the only seam.

## DOES NOT SURVIVE (not promised)

- **an-inner-object-with-a-live-key.** When the outer status object is cut and an object nested inside it also has a
  `live` key, that inner object is read as the status. No nested object in today's status has a `live` key (measured
  2026-11-22 on the Archmagi and SteveDesktop outputs).
- **a-switcher-that-lies.** A `live` name that does not match the machine's real login is passed through.

## PROMISES (each one is owed a check of the same name)

- **a-clean-status-names-its-account.** A status that exits 0 and holds `"live": "<name>"` reads `value`, and
  `name_of` gives the name. `ok` may be absent (older switchers and the test fakes print none).
- **text-around-the-json-is-tolerated.** A warning line before the JSON, or a note after it, reads the same as the
  clean status.
- **a-cut-status-is-failed-not-a-name.** A status cut before its end (no whole object with a `live` key) reads
  `failed`, never a name and never a crash.
- **a-non-zero-exit-is-failed.** An exit code other than 0 reads `failed` with the code, even when the stdout holds a
  `live` name.
- **not-ok-is-failed.** A status with `"ok": false` (the switcher's refusal) reads `failed`.
- **no-live-account-is-empty.** A status that exits 0 with `live` null, empty or not a string reads `empty`: the
  switcher answered, and it names no account. `name_of` gives None.
- **a-missing-or-hung-switcher-could-not-look.** A switcher that is not found, cannot run, or passes the deadline reads
  `could_not_look` with the cause (`not found`, `could not run`, `timed out after N s`).
- **every-blind-answer-names-its-cause.** `why_of` is None on `value` and a non-empty cause on every other kind.
- **a-remote-machine-is-read-over-ssh.** `read(target=...)` runs the status on that machine through
  `ssh -o BatchMode=yes` and a login shell, and its output goes through the same parse.
- **every-reader-uses-the-one-home.** No tracked file outside `account_live.py` and its tests runs
  `claude-account` with `status`, and each of the readers above calls `account_live`.
- **remote-list-preflight-reads-the-live-field.** The remote list preflight uses the live name in the status object
  even when a login banner mentions another account.

## LIMITS

- `DEADLINE_S` = 60. Danger: a hung switcher (or ssh) stalls the caller's timer pass, and the next pass stacks on it.
  Evidence: the status itself waits at most 2 s on the switcher's machine lock (`capture(wait=2)` in
  `claude-account`), and it took 0.10 to 0.14 s on 2026-11-22 (three runs). 60 s is a hang guard far above a real
  run, not a speed bar.
- ssh `ConnectTimeout=8`. Danger: an unreachable machine holds a pass for the TCP default (minutes). Evidence: kept
  from `account_usage._ssh`, which the usage poll has run every pass since 2026-10-28.
