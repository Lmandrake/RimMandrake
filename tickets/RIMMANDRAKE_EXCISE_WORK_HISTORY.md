---
id: RIMMANDRAKE_EXCISE_WORK_HISTORY
title: Cut over the RimMandrake work-scrub history rewrite tonight
project: rimmaster
type: action
status: open
owner: agent
created: 2026-10-27T10:03:12-07:00
updated: 2026-10-27T10:03:12-07:00
act_by: 2026-10-28
effort: 1h
source: manual
check: "{\"reason\":\"cutover is a one-shot fleet act\",\"review_by\":\"2026-11-10\",\"type\":\"gap\"}"
---

Owner 2026-10-27: 'Rewrite history in place', fold mandrake@users.noreply.github.com + mandrake@local into 313496996+Lmandrake noreply ('Fold them in, same push'), reword the C-3PO quote ('Reword it'), cutover 'Tonight, when the seats are idle'. Prepared in /Users/mandrake/ClaudeWork/rimmandrake-rewrite (REPORT.md has the cutover steps; mailmap and expressions already updated, rewrite must be re-run on a fresh fetch). Force-push authorized by the owner for this one push only.

## Log
- 2026-10-27T10:03 mt-400028/ticket: new (manual)
- 2026-10-28T09:58 BENCH (Archmagi): the 2026-10-28 05:04 attempt paused every rm-*/testq-* timer on Archmagi (list in ~/rm/paused-timers-rewrite-20261028.txt) and Lodestar sync until 11:04, then never cut over (origin/main still carries mandrake@users.noreply.github.com, 10538 commits) and never restarted the timers; BENCH restarted them 09:41. Owner by card 09:55: "Tonight, overnight" (over today's idle window). Before the next attempt: arm the timer restart in the same command as the pause (systemd-run --on-active), hold tonight's night shift off, re-fetch, then cut over.
