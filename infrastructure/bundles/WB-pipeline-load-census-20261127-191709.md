# WB-pipeline-load-census-20261127-191709

Members: RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT (one; a measurement).

## Group 1: RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT
- Class: REAL (investigation). Outcome check `test -s design/specs/2026-11-26-slow-actions/load_users.md` red, rc=1,
  before the work.
- Instrument: design/specs/2026-11-26-slow-actions/load_sample.py (cgroups and /proc every 3 s),
  load_sample_win.ps1 (Win32_Process every 30 s), load_report.py (the tables). Run on Archmagi from SteveDesktop over
  Tailscale (ssh mandrake@archmagi-wsl), as the transient unit load-census-hour.service, 11:23:38 to 12:23:38 PST.
  Data: D:\ClaudeWork\scratch\load_census_20261127\hour on Archmagi (linux.json, win.jsonl, timers.txt, journal.txt).
- Reading (one hour): Linux 11.62 of 14.02 core-hours busy; claude-seats.slice 7.10 (helper tool commands 6.31),
  app.slice 2.73 (rm timers 1.79 by journal), kernel 1.07. Windows 99.6% CPU: vmmemWSL 8.26 of 13.35 core-hours,
  ArchSmall game 1.76, Plan 9 server 0.93. Disk: WSL page-ins 563 GB (86% refaults), Backblaze 410 GB.
- Page: design/specs/2026-11-26-slow-actions/load_users.md; one_page.md row 10 points at it.
- State: DONE. Page e1c6e78d80; lessons 322c7cbf03; closed (ledger e8bc088633). Fix rows handed to RIMMANDRAKE_ORDER_TEN_SLOW_ACTION_FIXES_PAGE_FILED_NONE by note.
