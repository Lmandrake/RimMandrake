# BOUNDARY: a run's sign of life and its lease come from the running process, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/run_alive.py`, its timer `src/RimMandrake/Utils/systemd/rm-run-alive.timer` (every 5 min),
the `ALIVE:` part of `detached_helper.finish` and `detached_helper.status`, and the two renewal texts of a holder's brief
(`maturation_dispatch.renew_line`, `modledger.holder_brief`).
Item: `RIMMANDRAKE_TIE_LIFE_SIGN_TO_PROCESS_484_HAND_NOTES`.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_run_alive.py`. The item's acceptance test is
`design/specs/2026-11-23-agent-work-to-code/acceptance/rank10_sign_of_life_accept.py`.

## ACCEPTS (the only inputs this is built for)

- **a-run-record.** A detached run's record (`<dispatcher state>/detached/<unit>.json`) whose status is `launching` or
  `running`. A finished record is not looked at.
- **a-lease.** The record's env names `RM_MODLEDGER_WRITER` (`HOLDER.<lease>`) and `RM_MODLEDGER_TOKEN`. The mod is
  `RM_CONTROL_MOD`. When it is absent (34 of 74 lease runs on record `[measured 2026-11-23]`), the mod is the one whose
  `DISPATCH` shard in the run's clone grants that lease.
- **a-live-process.** The run's Claude is a process named `claude` in the control group of the run's unit or of its
  scope (`detached_helper.scope_name`). A command of the run is a descendant of that process whose command line names a
  Claude shell snapshot. Measured on ten live scopes, 2026-11-23, Claude Code 2.1.325.
- **a-transcript.** The run's session transcript in its clone's project folder, and the transcripts of its subagents
  under the folder of that session. Any of them that grows is a sign of life.

## DOES NOT SURVIVE (not promised)

- **a-command-that-itself-hangs.** A command that never ends is a long wait. The run keeps its lease while it runs.
- **a-silent-in-process-tool.** A tool with no child process (a web page, an MCP call) that answers nothing for longer
  than the silence limit reads hung.
- **a-detached-child.** A command the agent detached (`nohup`, `setsid`) whose parent is no longer the run's Claude is not
  a command of the run.
- **a-git-rewrite-in-the-same-instant.** A renewal line written while the run's own git replaces the shard file may be
  lost. The next beat writes another; the lease lives 45 minutes and a beat comes each 20.
- **a-renewal-after-the-last-landing.** A renewal line that the run never landed goes into the clone's bundle, as a line
  that the agent wrote by hand would.
- **a-lease-held-outside-a-detached-run.** A holder started by hand with no run record is not looked at. Its brief keeps
  the renewal lines.

## PROMISES (each one is owed a check of the same name)

- **a-live-run-keeps-its-lease.** A run whose unit and process are up, and whose transcript grew, has its lease renewed
  with its own writer and token, once each beat, by the run's own clone's `modledger.py append`.
- **a-long-wait-is-not-hung.** A silent run with a command running is renewed.
- **a-dead-run-loses-its-lease.** A run whose unit or process is gone is not renewed, and its state line says `gone`.
- **a-hung-run-loses-its-lease.** A run silent past the limit with no command running is not renewed, and its state line
  says `hung`.
- **a-blind-beat-changes-nothing.** When a fact that decides could not be read, the beat renews nothing, lapses nothing,
  keeps the last `ALIVE:` line, and names the fact. It is never "dead" and never "alive".
- **a-run-on-another-host-is-not-gone.** A run whose record names another machine (`host`, a door of `run_host.py`) is
  never read from this machine's systemd or /proc. It reads blind, names its host and the command that reads it there,
  and changes nothing. A run on this machine is looked at as before.
- **a-refused-renewal-reads-refused.** A refused append, a failed append, and a lease that another holder fenced (on
  origin/main or in the clone) read `refused: <cause>`, and the next look tries again. A run with no lease calls no append.
- **the-alive-line-is-the-runs-own.** The line holds the run's last message and its commits. It holds no spend sentence
  (`spend_talk.strip`). An empty message reads `no message yet (looked)`, an unreadable one `could not look`, a message of
  which every sentence was spend talk says so, no commits reads `none (looked)`.
- **one-file-beside-the-record.** Each look writes `<unit>.alive.json`, whole or not at all. No reader of run records
  takes it for a record.
- **the-status-shows-it.** `detached_helper.py status` shows the act, its cause and the line of each live run, and says
  when no look is on file or the file cannot be read.
- **the-ledger-gets-it-once.** `finish` writes the line in its one note, when the run did not end success (a success note
  holds the run's last message already). A line that cannot be made never stops `finish`.
- **one-run-never-stops-the-others.** A run whose look raises reads blind with the cause. The other runs are looked at.
- **the-brief-asks-only-while-no-timer-lives.** A holder's brief carries the renewal lines while the timer's reading is
  absent, unreadable or older than an hour. Only a fresh reading takes them out.
- **a-beat-that-could-not-look-writes-no-reading.** When the run records cannot be listed, the beat exits 1 and leaves the
  old reading, which then goes stale.
- **it-raises-no-alarm.** It stops no run, writes no rimflow note and posts nothing.

## LIMITS

- `BEAT_S` 1200 s between two renewals: guards against a ledger line each look (14.3M + 7.5M weighted tokens of hand notes
  and renewals in the week to 2026-11-23 show the cost of chatter). 20 minutes is well under `lease_idle_minutes` (45).
- `SILENCE_S` 7500 s: guards against a hung run that keeps its lease. The longest allowed call is 7200 s (the Bash tool's
  background limit), so no call that the harness allows is past it. How often a run hangs is UNMEASURED.
- `LIVE_S` 3600 s: a reading older than this is not a live timer. The danger is a brief with no renewal lines while no
  program renews (GimmeSomeSlack blind cycle 5, 2026-11-16 1:03 AM PST, lost its closing checkpoint to a lapsed lease).
- `START_S` 120 s: a run this young whose Claude is not up yet is blind, not gone (`detached_helper.LAUNCH_GRACE_S`).
- `CMD_S` 120 s on each subprocess, and `TimeoutStartSec` 10 min on the unit: hang guards.
