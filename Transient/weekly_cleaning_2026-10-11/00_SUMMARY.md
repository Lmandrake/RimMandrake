# Weekly cleaning, learning, growth — 2026-10-11 summary

Owner order (typed): "Before we return to work, it's time now to do our weekly cleaning, learning, growth. ... No RimMaster game dev work will continue until we're done."

## Done
| Area | Before → after | Where |
|---|---|---|
| Project CLAUDE.md | 73 KB → 21 KB; 40/40 owner quotes preserved; moved blocks into 6 docs; Compact Instructions added | 15_claudemd_progress.md |
| Global CLAUDE.md | drifted from Lodestar sources → rendered clean; worktree + wsl-plumbing lines fixed | 20_global_claudemd_progress.md |
| Auto-memory | 197 files / 163-line index → 136 / 65; expired orders gone; model ladder now points to Agent_Policy.md | 14_nightshift_and_memory_progress.md |
| Lessons | 298 → 213 (dupes merged, stale deleted, absorbed into skills); 5 stranded owner rulings homed | 16_, 13_ |
| Handoffs | 214 → 128; handoff.py caps tree dump, merges REBOOT families, `--owed` | 16_ |
| New skills | clone-landing-commits, live-debugging-proof-harness, night-shift-orchestration (global), rimworld-review-sheets; chatgpt-consult + wsl-windows-plumbing linked globally, 15 GPT lessons folded in | 12_, 13_, 14_, 17_, 20_ |
| Git root causes | serve logs untracked; land.sh realigns + defaults to own clone; `./sync` (reset --keep); publish without autostash; ledger_sync leak fixed; bench gc 11→6.8 GB | 12_git_tooling_progress.md |
| Review sheets | scale panels enforced in code at serve/commit/phone; buildings+items sized; any-art mode | 17_review_sheet_build_progress.md |
| Owner-quote guards | census: 0 forgeries in 1,461 events, 95% false refusals → ~3,100 lines of guards removed; --by-card / --per-ruling / --why fields | 23_, 24_ |
| Disk | WSL used 541 → 345 GB (18 stray clones deleted, nothing unlanded lost); old D: worktrees checked | 11_, 19_, 21_, 22_ |
| Public repos | 4 repos had a stranger's or Gmail address → correct noreply | — |

## Decided, scheduled
- WSL move to E: (sparse, backup to F:) — right after this grooming. Runbook: src/RimMandrake/Utils/wslmove/, 18_wsl_move_prep.md.
- Telemetry: hybrid (VictoriaMetrics + SQLite + Grafana + RimPulse alerts) on E:, 1 s windows + flight recorder during tests. Build after the move. Design: 08_telemetry_deep_design.md.

## Idle compaction (owner card: keep it, adapt the ritual)
Agents hand off on idle unprompted; lessons are filed as learned; after a compaction, `compaction_check.py` (night-shift-orchestration skill) and `handoff.py --owed` show whether a handoff is owed, and it is written from the transcript on disk.
