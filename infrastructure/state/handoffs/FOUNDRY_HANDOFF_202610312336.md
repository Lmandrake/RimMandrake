# FOUNDRY handoff (context-limit restart)

## The one thing to carry forward
Trio relaunch chain: resume fix 4b6e562c13 worked; then a 401 (token rotated by another Claude process) was charged as a reject. Builder ada3b829c18272a34 is fixing TRIO_BUILD_FIX_401_CHARGED_AS_REJECT, voiding round 2, re-pinning /home/mandrake/rm/trial_pin_trio and relaunching trio; watcher running. ralph_a stays on /home/mandrake/rm/trial_pin (untouched; same 401 hazard noted on the item).

## Half-done
- `TRIO_BUILD_FIX_401_CHARGED_AS_REJECT` — builder ada3b829c18272a34 relaunched trio, liveness check done, waiting on first real critic verdict on task 1; NEXT: read tail of /mnt/d/ClaudeWork/rimmandrake/foundry_arena/replay/launcher.log and trio.log, confirm a real critic verdict, then tell the CONDUCTOR in one line (SendMessage CONDUCTOR) with trio's final pin sha for the verdict.
- `PARALLEL_TRIAL_AUDIT_BY_FRESH_OPUS` — design revised (31e42af496, rule v2 sha256 fc78e363...), blockers P0-P14 in design section 9 open, fresh re-audit owed; NEXT: after replay ends, spawn a naive Opus re-audit, then work blockers.
- `TRIO_RECOVER_FIX_LOGONLY_PENDING_WEDGES` and `TRIO_PARK_FIX_FILING_NEVER_RETRIED` — filed, unverified; NEXT: claim after trio runs.
- Owed after trial: code review of dirty arena files (incl. arena_replay.py, arena_replay_run.py, the two design files); ARENA_ANCHOR_CLOSEOUT (arena_anchor_publish.py --final).
Conductor orders: no lane codes in names; rimflow queue is the source; report only when trio has a scored task or blocked.
