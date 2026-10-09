# AWAY_DASHBOARD_BUILD_1 — build log (2026-10-08)

Builder: BENCH subagent. Design: `Transient/away_dashboard_design_2026-10-08.md`.

## Progress
- started — skeleton written

- 20:58 final relaunch through the autostart task, at the saved position; verified topmost + WS_EX_NOACTIVATE, foreground stayed AGENT BENCH. Window settled — no further relaunches.

## What runs where
- **WSL** `rm-pulse.service` (systemd --user, Restart=always): `src/RimMandrake/Utils/pulse/pulse.py daemon` — collects every 5 s, serves the page + `/api/now` + SSE `/api/stream` on 127.0.0.1:8765. `rm-pulse-health.timer` (2 min) restarts it if its snapshot stops advancing. State: `~/.local/state/rm-dashboard/`.
- **Windows** scheduled task `RimFlow Pulse` (at logon + every 10 min; single-instance mutex) runs `pythonw.exe D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\pulse\widget\lantern.pyw` (pywebview 6.2.1 / WebView2): frameless, topmost, never activates, fixed 580x400, collapse to the strip by ▾ or double-click. If the spine is down it shows "monitor down", retries, and after 60 s runs `wsl.exe … systemctl --user start rm-pulse.service`. Widget state (position, toasts sent, log) lives in the Store-Python virtualised folder `C:\Users\Mandrake\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\Local\RimFlowPulse\`.
- Install/repair: `cp src/RimMandrake/Utils/pulse/systemd/rm-pulse* ~/.config/systemd/user/` + enable; `powershell.exe -File D:\…\pulse\widget\install_autostart.ps1`.

## Signals wired (measured)
- RED: seat / tool-cgroup OOM kill (kernel log, exact scope + cap); a window watched live whose process died while its session file stayed (pid + procStart). A removed session file = clean exit, neutral.
- ◆ warning: a real harness selftest killed at its cap (contained). The planted 128 MiB pen test is a calm line, never an alarm.
- AMBER: `status:"waiting"` (MEASURED: a pending AskUserQuestion card = waiting / "input needed"; the question text is read from the transcript) — always. Soft amber: idle >60 s **and no subagent running** (subagent transcript last record not end_turn, moved <15 min). Busy with no transcript growth 20 min = dim "no observed progress", never flashes.
- Calm: working (+N agents, + current ledger item), RimWorld up/down (probed from Windows by the widget), bridge holder, artpipe counts, review-ready (`needs` → OWNER), finished items with GitHub commit / native-path evidence links.
- Toasts: raised by the widget (CREATE_NO_WINDOW) for new red and explicit amber; seat kills are left to memwatch, which already toasts them. Phone push: hook point `notify_phone()` in pulse.py, disabled (not ruled).
- Every line carries its source; a line whose source has not refreshed shows `stale`, and the header shows live / stale / monitor down.

## Digest
`./pulse back` (the "I'm back" form; since = his last prompt before his latest ≥30 min gap), timers at 06:00 and 17:30 (`rm-pulse-digest.timer`, Persistent). Printed with native paths, saved as `D:\Luke\dev\_rmdashboard\digests\digest_<date>_<HHMM>_<mode>.md`, and the widget's "finished since" section switches to that window with a link to the file. `src/RimMandrake/Utils/pulse/hooks/im_back_hook.py` makes typing "I'm back" run it automatically — PREPARED, NOT INSTALLED (a settings.json hook needs the owner's own OK; it only fires in sessions started after).

## Metrics
`~/.local/state/rm-dashboard/metrics.jsonl`, fresh baseline from 20:58 (build-iteration records moved to `metrics.build-iteration-2026-10-08.jsonl`): `alarm_open`/`alarm_close` (question age), `red_noticed` (time-to-notice = his next prompt after a red), `alarm_ack` with label actionable/noise (alert precision — the widget's ack / noise buttons), `toast`, `digest`, `spine_restart`. `./pulse metrics` summarises.

## Known gaps
- The seat kill at 07:13 is in `claude-seat-TEST` (likely the morning's deliberate cap test) — it shows red until acked; nothing in the kernel line says it was deliberate.
- SessionEnd / StopFailure / Notification hooks not installed (settings change); window loss is inferred from pid + procStart, which cannot tell a crash from `kill -9`.
- Session-file format is Claude Code internal; a parse failure shows the sessions source as stale rather than guessing.
- Fonts load from Google Fonts; offline it falls back to Cascadia Mono / Consolas.
- 20:40 owner input via coordinator: widget follows concept C's look (Marquee strip style), not A; no statusline strip; C-style toasts OK
- 20:45 measured: AskUserQuestion pending => session file `status:"waiting"`, `waitingFor:"input needed"` (BENCH + FOUNDRY both, transcripts end in an AskUserQuestion tool_use). procStart == /proc/<pid>/stat field 22. Subagent signal: `~/.claude/projects/*/<sessionId>/subagents/agent-*.jsonl` — running = last record not an `end_turn` assistant message and mtime < 15 min. Harness OOM kills come ~every 5 min in bursts (`toast:false`). pywebview 6.2.1 installed in Windows Python 3.13 (user pip). Service-launched powershell.exe steals focus (memwatch note) => toasts are raised by the Windows widget (CREATE_NO_WINDOW), never by the WSL service; `./game` is not called by the service.
- plan: WSL `rm-pulse.service` (collector loop + HTTP/SSE on :8765) -> Windows `pythonw lantern.pyw` (pywebview, frameless, topmost, no-activate) styled as concept C.
- 21:05 spine built: `src/RimMandrake/Utils/pulse/` (pulse_core.py classifier, pulse.py daemon/since/ack/metrics/health, selftest_pulse.py 37 checks GREEN via run_selftests), units rm-pulse.service + rm-pulse-health.timer (2 min, restarts a hung spine) + rm-pulse-digest.timer (06:00, 17:30) installed and active. Windows python.exe reaches http://127.0.0.1:8765 (WSL localhost forwarding works). `./pulse back` = the I'm-back digest.
- 21:00 widget running on Windows (pywebview, frameless, on top, focus=False); first screenshot looked right — concept C rows + glowing pill strip. A live harness OOM kill raised a Windows toast from the widget (toasted.json). Fixed: window now fits its content; widget reloads itself when the served page changes; red rows get their band. Digest `./pulse back` works -> `D:\Luke\dev\_rmdashboard\digests\digest_2026-10-08_2051_back.md`. "I'm back" UserPromptSubmit hook PREPARED, not installed (settings change needs the owner's OK).
- 21:05 OOM tile corrected (coordinator: owner alarmed by "35 OOM kills today"). Source is now the KERNEL log (`journalctl -k`), which names each kill's scope and cap; memwatch only sees "rm-harness.slice +1". MEASURED today: 39 kernel OOM kills = **37 planted** (selftest_run_selftests.py's 512 MiB bomb under a 128 MiB cap, the runner proving containment — shown as one calm "memory pen proven" line, never an alarm) + **1 real harness test kill** (07:13:38, a selftest hit its 6 GB cap — contained; shown as a ◆ warning, not red) + **1 seat tool-cgroup kill** (07:13:29, claude-seat-TEST's claude-code-bash at its 1 GB cap — red). "Today" = since local midnight (min 6 h).
- 21:05 window behaviour (owner: "keeps moving around, flickering"): the page no longer resizes the window on data updates; the ONLY resize is his collapse/expand click; size is fixed (580x400); position is saved on move and restored at creation (no jump on relaunch). Page changes hot-reload inside the existing window — no relaunch per tweak.
