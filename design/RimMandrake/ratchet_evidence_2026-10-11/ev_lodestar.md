# Lodestar evidence (read-only, 2026-10-11)
Repo: /mnt/d/Luke/dev/Lodestar (windows D:\Luke\dev\Lodestar)

## Machinery found
- The "sweep" = bin/sync.py, systemd system unit sync/systemd/lodestar-sync.{service,timer}: hourly at :07 (+120s jitter), oneshot, MemoryMax 2G, TimeoutStart 45min. It syncs ~dozens of repos (fetch/pull/push/commit dirty), regenerates SYNC.md, writes journal/<date>/archmagi-NN.heartbeat. It does NOT score or improve anything.
- bin/check.py (health composite), bin/shadow.py --gate (Phase-4 go-live gate, N criteria PASS/FAIL), airlock.py --gate, review.py gate: pass/fail gates, not scores. grep for ratchet/grader/score loops in bin/, docs/: none found. No score trajectory exists.
- tests: 122 files in tests/, 56,945 lines; run_tests.py. Not scheduled; manual.
- Other timers on this machine (rm-codebase-health every ~15m, rm-memwatch/telemetry-export/telemetry-health 1-2 min, rm-pulse-health 2 min, rm-objstore hourly) are RimMandrake, not Lodestar; not measured here.

## Sweep runtime (journalctl -u lodestar-sync, since 2026-09-25)
- 381 sweeps logged; total wall 13.1 h; median 114 s; p90 165 s; max 492 s; total CPU 99 min (CPU is ~12% of wall: it is waiting on slow drvfs/git/network, not computing).
- Last three: 3m12s/22s CPU, 1m42s/12s, 2m17s/16s.
- Current SYNC.md: 3 flags need owner (Lodestar itself diverged 3 ahead/20 behind with uncommitted tracked changes; lifecycle "5 approved plans; converge exited 1"; ~/.claude dangling skill link plaud-access). RimMandrake skipped: 2842 local changes uncommitted.
- Gate right now: shadow.py --gate FAILED 2 of 6 (PAUSE never exercised/resumed in window + one more).

## Commits, last 45 days (git log --since=45.days.ago): 2412 total
- 1110 "chore(sync): <machine> <ts> — journal/.../heartbeat" (46%): 646 by author "Lodestar sweep", ~458 "mandrake", 6 other. Machines: laptop 507, home(archmagi) 333, desktop 261. Content = one heartbeat file each: zero behaviour.
- 62 "chore(board): regenerate BOARD".
- ~199 "touch <loop>:" commits (loop last_touch bookkeeping), 45 handoff, 25 journal, 14+ "Phase N".
- So ~1,370 of 2,412 (57%) are mechanical bookkeeping; roughly 330 commits touch bin/ lib/ (behaviour), ~366 touch bin/lib/tests. Behaviour commits are by humans/agents (feat, fix, "Add teams_triage.py", "handoff.py: cap tree-state dump", "routing+beaconmatch: whole-word matching (halved live beacon candidates 51 -> 27)"), not by the sweep. The sweep itself has produced 0 improvements; it only transports.
- Daily commit rate 20-180 (peaks 179 on 2026-09-01, 146 on 10-01); sync heartbeats ~71/day on 10-02..05 (3 machines x 24h).

## Loops (loops/*.md, 69 files)
- 31 active open, 24 background open, 2 parked; 12 closed. i.e. 55 of 69 open (80%).
- Many open loops carry actual_spent 0m and a stale last_touch: e.g. measuring-large-artifacts (opened 08-31, last touch 08-31, est 1h30m), phase-3 (opened 09-01, last touch 09-01, est 2h), phase-4-sandbox (09-09), mandrakevisualize (09-03), earth-action-plenary (deadline 2026-09-16, passed, last touch 09-08), estim2026 (deadline 09-18, last touch 09-16), command-module (est 12h, last touch 09-17), fetcher-corpus-repairs, prework-fanout, zap-surface, brief-real-data (all last touch 09-10/15/16).
- Estimates vs actual: rimworld-biome-art-review est 30h actual 27h open; repo-lifecycle est 8h actual 11h45m; work-mail-triage est 20m actual 180m; heat28-competitive-claim est 60m actual 180m; chatgpt-consult est 1d6h. Note loops/lodestar.md itself warns its 30m est vs 3h actual is a "residual" artifact: est_close/actual_spent is hand-written and unreliable for calibration.
- Oldest still-open: measuring-large-artifacts, dispatchopencode (opened 08-31, touched 10-09, est 1h) = 41 days.

## Core project-independent abstractions (1 line each)
- Loop: one markdown file with front matter (id, class active|background|feature, state open|parked|closed, est_close, actual_spent, opened, last_touch, deadline) = a unit of work with a stated time-to-close.
- Board: BOARD.md, a regenerated personal-kanban projection of loops/, rebuilt and round-trip-checked (board.py --rebuild/--check).
- Journal: append-only per-day event files journal/<date>/ (json events + per-machine heartbeats) = durable record, safe across machines.
- Handoff: handoffs/*.md written by handoff.py at session end with `ID — state; NEXT:` pointers, consumed with --wake; audit found only pointers with concrete NEXT get picked up.
- Sync sweep: hourly idempotent multi-repo reconciler with tiered fetch (hot/warm/cold), freshness gate, PAUSE kill switch, honest "Remote verified/not checked" column.
- Airlock/shadow/review: sensed items are proposals in a quarantine; shadow mode runs unattended, a human reviews, a numeric gate (PASS/FAIL list) governs go-live; unreviewed never reads as approved.
- Registry (sync/registry.md): which repos every machine must hold; lifecycle.py propose->approve->converge for rename/rehome/retire.
- Conversations records: conversations.py renders sessions into repo.
- Doc theme: "complete well-tested subsystem wired to nothing" is called the signature defect (lifecycle.py header).

## Answer to owner's hunch
In Lodestar the wall-clock absorbers are (1) the hourly sweep, 13 h wall in ~16 days of logs, ~2 min each, CPU-idle (slow drvfs) and (2) 55 open loops that are never closed. Neither is an improve-by-iteration loop; no score ratchet exists in Lodestar. If the owner's "slowly improve" is a score loop, it is in RimMandrake (rm-codebase-health, code_review_status, modcheck floor), not here; not measured in this task.
