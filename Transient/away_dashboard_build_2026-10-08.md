# AWAY_DASHBOARD_BUILD_1 — build log (2026-10-08)

Builder: BENCH subagent. Design: `Transient/away_dashboard_design_2026-10-08.md`.

## Progress
- started — skeleton written

## What runs where
(pending)

## Signals wired (measured)
(pending)

## Digest
(pending)

## Metrics
(pending)

## Known gaps
(pending)
- 20:40 owner input via coordinator: widget follows concept C's look (Marquee strip style), not A; no statusline strip; C-style toasts OK
- 20:45 measured: AskUserQuestion pending => session file `status:"waiting"`, `waitingFor:"input needed"` (BENCH + FOUNDRY both, transcripts end in an AskUserQuestion tool_use). procStart == /proc/<pid>/stat field 22. Subagent signal: `~/.claude/projects/*/<sessionId>/subagents/agent-*.jsonl` — running = last record not an `end_turn` assistant message and mtime < 15 min. Harness OOM kills come ~every 5 min in bursts (`toast:false`). pywebview 6.2.1 installed in Windows Python 3.13 (user pip). Service-launched powershell.exe steals focus (memwatch note) => toasts are raised by the Windows widget (CREATE_NO_WINDOW), never by the WSL service; `./game` is not called by the service.
- plan: WSL `rm-pulse.service` (collector loop + HTTP/SSE on :8765) -> Windows `pythonw lantern.pyw` (pywebview, frameless, topmost, no-activate) styled as concept C.
- 21:05 spine built: `src/RimMandrake/Utils/pulse/` (pulse_core.py classifier, pulse.py daemon/since/ack/metrics/health, selftest_pulse.py 37 checks GREEN via run_selftests), units rm-pulse.service + rm-pulse-health.timer (2 min, restarts a hung spine) + rm-pulse-digest.timer (06:00, 17:30) installed and active. Windows python.exe reaches http://127.0.0.1:8765 (WSL localhost forwarding works). `./pulse back` = the I'm-back digest.
