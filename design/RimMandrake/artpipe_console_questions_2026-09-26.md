# artpipe daemon console — clarifying questions before a design (2026-09-26)

Owner's prompt: the Artist tile's output is unreadable (e.g. `artpiped: NOTE artreg event
skipped for rut_firehawk_grounded_v3_south: no 'queued' event found for job_id=… — pass
--target explicitly`). He pointed at the sibling project `D:\Luke\dev\Fetcher` as the model.

**What was read.** Fetcher: `core/console.py` (247 lines), `core/daemon.py` (88), `README.md`,
`docs/architecture.md` §"The console". Ours: every `print(` in
`src/RimMandrake/Utils/artpipe/artpiped.py` (24 calls), `finalize_job`/`process_job`, the
argparse block, `artreg.py`'s `RegError` text, the nine committed
`infrastructure/artpipe/daemon_run_*.log` files, `art_status.{json,html}` and who regenerates
them (`infrastructure/dashboards/hub/regen_hub.py` → `artreg.py render`, not the daemon), and
the Artist tile definition in `src/RimMandrake/Utils/install_wt_seat_profiles.py`.

**Fetcher's approach, in one line.** One always-painted status line at the bottom
(`● IDLE — no further actions (12 ok, 1 failed this session)` / `◔ PENDING — 3 requests queued`
/ `▶ WORKING 2/5 ████░░░░░░░░  FETCH https://…  +3 queued`), repainted by a background thread
only when its signature changes; above it, one permanent line per finished directive
(`✓ FETCH https://…   COMPLETE  14:07`, red `✗ … FAILED`); `emit()` is a timestamped line
"reserved for warnings/errors only" and fires mostly at startup (missing capability, prune
report, lock eviction). ANSI colour and in-place repaint only when stdout is a TTY; piped, it
appends a plain line per state change. There is no `--status` verb, no status file, no TUI —
the console line IS the status, and the doc says to run it in the foreground of a window.

**artpiped's approach, in one line.** Prints nothing on the success path at all — a job that
claims, generates, validates and files to `done/` is invisible; `--verbose` only forwards to
the worker (line 1279). What does print: startup preflight (`codex sandbox preflight ok — …`
/ `CODEX CHANNEL DISABLED …`), throughput-file parse warnings, one-shot quota WARNINGs from
`Detector.note_meters`, the per-job artreg NOTE/WARNING (lines 2029–2032), the signal line,
and a final `stopped. hard_stop=False refuse_new=False stop_all=False gemini_hard_stop=False
gemini_spent=$4.02 pending_remaining=False — CLEAN DRAIN (exit 0)`. WARNINGs go to stderr,
the rest to stdout. `daemon_run_20260923_owner_100pct.log` (6.7 KB) is ~90 % artreg NOTE
lines. The Artist tile runs `python3 …/artpiped.py` in the foreground of a Windows Terminal
pane, i.e. a real TTY.

---

## Questions

### 1. Should a finished job leave a permanent line, as Fetcher's `record()` does?
Fetcher prints exactly one line per completed directive (`✓ label  COMPLETE  hh:mm`), so the
scrollback is a complete record of the session. artpiped prints nothing for a success and
nothing for an ordinary validator FAIL either — those only reach `done/`/`failed/` and the
manifest. Options:
- (a) One line per finished job, Fetcher-shaped: `✓ rut_firehawk_grounded_v3_south  edit/codex  62s  PASS  14:07`.
- (b) Only failures scroll (`✗ … validator REJECT: mask coverage 41%`); successes are just a count on the status line.
- (c) Keep the scrollback warning-only as now; the record is `done/` and `art_status.html`.

### 2. Do you want Fetcher's single live status line, and what must it carry?
Fetcher's line answers "is it doing anything, how far, how much is waiting" at a glance and is
repainted in place (no scrolling). artpiped today has no such line — with 402 jobs in
`pending/` and up to `--workers` in flight there is no way to see in-flight ids or the queue
depth without `ls`. Options:
- (a) One line, Fetcher-style: `▶ WORKING 2 in flight ████░░  rut_firehawk_grounded_v3_south, korrum_v2_east  +400 pending  codex 5h 42% / wk 61%  gemini $4.02/$10`.
- (b) A small block: one line per worker slot plus a summary line — costs N+1 lines but shows each job's elapsed time against its timeout.
- (c) No live line; scrolling record only (question 1), like a plain log.
Note either way: `active/` is shared between concurrent daemons (comment at line 2476), so
"in flight" must mean *this* daemon's futures, and "pending" is the global count.

### 3. Where does the artreg NOTE go — the line that started this?
It fires once per job filed before the registry existed (no `queued` event), and its text is
`artreg.py`'s CLI error (`RegError`, line 177: "pass --target explicitly") — advice for a human
running a different tool, not for the daemon's operator. Fetcher never emits per-item
bookkeeping notes; its NOTEs are once-at-startup capability reports. Options:
- (a) Off the console entirely; write to a per-run `daemon.log` beside the queue.
- (b) Collapse to one line at the end of the run: `registry: 12 jobs skipped (filed before ART_REGEN_REGISTRY_1, no queued event)`.
- (c) Keep per-job, but reworded as a daemon fact (`registry skipped: pre-registry job`) with no cross-tool advice.
And the general rule this decides: may a daemon line ever tell you to run another command?

### 4. What should the final `stopped.` line say?
Now it dumps six internal fields. Fetcher's equivalent is the IDLE tally `(12 ok, 1 failed this
session)`. Options:
- (a) Human summary only: `stopped — 37 ok, 4 failed, 0 pending, gemini $4.02 this run (clean drain)`.
- (b) Summary line plus the raw fields on a second dim line for a seat that greps it.
- (c) Leave the field dump; it is read by agents more than by you.

### 5. Is this watched live in the Artist tile, or captured to a file — or both?
Fetcher reads `isatty` once and documents "run it in the foreground of a window"; piped, it
degrades to plain lines. Our tile is a foreground TTY, but nine `daemon_run_*.log` captures
sit in `infrastructure/artpipe/` (seat-run sessions with redirection), and today WARNINGs go to
stderr while everything else goes to stdout, so a `> log` capture loses the warnings. Options:
- (a) Foreground only, Fetcher's degradation when piped; one stream (stdout) for everything.
- (b) Always also append a plain per-run log under `infrastructure/artpipe/logs/` (uncommitted, pruned), so a seat can read what happened without having watched.
- (c) (b) plus an `artpiped --status` verb that reads a small status file the daemon keeps current — something Fetcher does not have, but which lets a Claude seat ask "what is the daemon doing" without a screenshot.

### 6. Colour and glyphs in the Windows Terminal pane?
Fetcher uses green/red/cyan/yellow ANSI and the glyphs `✓ ✗ ▶ ◔ ●` plus `█░` bar cells, gated
on TTY. artpiped uses none. Options:
- (a) Same palette and glyphs as Fetcher.
- (b) Colour, but ASCII only (`OK`/`FAIL`, `[####....]`) in case the tile font lacks the glyphs.
- (c) No colour at all.

### 7. Should channel-state transitions be recorded as they happen?
`Detector` latches `refuse_new`, `stop_all`, `sleep_until`, `n_override` and the one-way
`effective_n` ratchet silently; the only console trace is a once-per-band WARNING at line 339
(weekly ≥ warn threshold) and the gemini-budget block printed once at startup (line 2311). So a
daemon that quietly stopped claiming codex jobs an hour ago looks identical to one that is
idle. Fetcher has no equivalent (its pacing is per-host and silent by design). Options:
- (a) Each transition is a timestamped permanent line: `codex: weekly 82% → refusing new claims until Tue 03:00`.
- (b) Shown only on the live status line (question 2), never in scrollback.
- (c) Both — the line for the moment, the record for later.

### 8. What is the console's relationship to `art_status.html`?
That page (Burn-up, State counts, Iterations histogram, Spend, Parked list, Projection) is
global and registry-scoped, rebuilt by `regen_hub.py` calling `artreg.py render` — the daemon
never touches it, so it lags a run. Options:
- (a) Console is session-scoped only (this run's ok/failed/pending); global numbers stay on the page.
- (b) Session-scoped plus the two live gating numbers (codex weekly %, gemini $ spent/budget), since those decide whether the run continues.
- (c) The daemon calls `artreg.render()` after each `finalize_job` so the page is live, and the console stays minimal.
