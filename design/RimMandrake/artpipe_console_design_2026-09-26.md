# artpipe daemon console — design (2026-09-26)

Presentation-only redesign of what `src/RimMandrake/Utils/artpipe/artpiped.py` shows a human
in the Artist tile and what it leaves behind for a Claude seat. Questions and the owner's
answers: `design/RimMandrake/artpipe_console_questions_2026-09-26.md` (answered the same day).
The model is the sibling project's `D:\Luke\dev\Fetcher\core\console.py`; everything of it that
matters is restated here, so the implementor need not read Fetcher.

## 0. Rulings this implements (owner, 2026-09-26, by question card)

| # | Ruling |
|---|---|
| 1 | One permanent line per finished job, Fetcher-shaped (`✓ … PASS hh:mm` / `✗ … FAIL …`). |
| 2 | One live repainted status line, Fetcher-style — **no gemini on it**. Verbatim: *"(1) but not gemini, we are not following that path anymore."* Read as a direction, not a cosmetic: **the new console, status file, log summary and stopped line surface no gemini figure anywhere.** Gemini *code* in `artpiped.py` is not this work's to remove (§9). |
| 3 | The artreg "no 'queued' event … pass --target explicitly" NOTE leaves the console for a per-run log. |
| 4 | Always append a plain per-run log under `infrastructure/artpipe/logs/` (uncommitted, pruned) **and** add `artpiped --status`, reading a status file the daemon keeps current. |
| 5 | Stopped line is a human summary only: `stopped — 37 ok, 4 failed, 0 pending, codex weekly 61% (clean drain)`. |
| 6 | Fetcher's palette and glyphs (`✓ ✗ ▶ ◔ ●`, `█░`, green/red/cyan/yellow ANSI), gated on TTY. |
| 7 | Codex quota transitions get a timestamped permanent line at the moment they happen **and** show on the status line. |
| 8 | Console is session-scoped plus one gating number: codex weekly %. `art_status.html` stays the global view and is untouched. |

## 1. Scope

**In:** a new `console.py` module; rewiring every `print(` in `artpiped.py` (24 calls, listed in
§8) to it; the status file; the per-run log; the `--status` verb; removing gemini from the
console surface; updating the five selftest assertions that grep console text (§10).

**Out (do not touch):** `art_status.{json,html}`, `artreg.py render`, `regen_hub.py`; job
processing (`process_job`, `process_codex_job`, `run_worker`, retry logic, validator/facts/
legibility gates); `claim_next`/`reconcile`/`repair`; the `Detector` class and its thresholds
(`WEEKLY_WARN/REFUSE/STOP = 95/99/99.8`, `FIVE_H_DROP_N1/SLEEP = 90/98`, wall-clock ratchet);
`GeminiBudget` and every gemini code path (the console just stops *reporting* them); the exit
code rule (`1` iff `pending/` non-empty). The nine committed `daemon_run_*.log` files in
`infrastructure/artpipe/` are ad-hoc captures from before this design — leave them alone.

## 2. Module structure

New file `src/RimMandrake/Utils/artpipe/console.py`, stdlib only, importable by
`artpiped.py` (`from artpipe import console` or the sibling-import style `artpiped.py` already
uses for `common`/`artreg`). Nothing in it knows about codex/gemini workers, subprocesses, or
`Detector` internals — it is fed plain values.

```
console.py
  _IS_TTY = sys.stdout.isatty()          # read once at import, like Fetcher
  _c(text, code) -> str                  # ANSI wrap iff _IS_TTY
  _fit(text, width) -> str               # collapse whitespace, ellipsise, ljust
  _term_cols() -> int                    # shutil.get_terminal_size((80, 24)).columns, each paint
  hhmm() / stamp()                       # local "%H:%M" and "%H:%M:%S"

  @dataclass(frozen=True) QuotaState     # the ONLY thing the console knows about codex quota
      weekly_pct: float | None           # None = UNMEASURED (never 0)
      five_h_pct: float | None
      weekly_resets_at: float | None     # epoch
      sleep_until: float | None          # epoch
      refuse_new: bool; stop_all: bool; hard_stop: bool
      admission_blocked: bool
      current_n: int                     # detector.current_n(configured_n)

  @dataclass InFlight                    # one per claimed job, main thread only
      job_id: str; mode: str ("generate"|"edit"); channel: str; started: float; timeout_s: int

  class RunLog                           # §6 — the per-run plain-text file
      open(logs_dir) -> RunLog; write(kind, text); close(); path
  class StatusFile                       # §5 — infrastructure/artpipe/status/<pid>.json
      write(snapshot: dict); remove()

  class Console                          # §3/§4 — the live line + the permanent record
      __init__(pending_count: Callable[[], int], configured_n: int, log: RunLog,
               status: StatusFile, started_at: float)
      # main-thread mutations
      job_started(job_id, mode, channel, timeout_s)
      job_finished(result: dict)         # prints the record line, updates tallies
      quota(state: QuotaState)           # diffs against the last QuotaState -> transition lines
      warn(text)                         # console + log      (Fetcher's emit(), warnings only)
      info(text)                         # console + log      (startup facts, signal, prune/repair/reconcile)
      note(text)                         # log ONLY           (bookkeeping the operator cannot act on)
      stopped(pending_remaining: int, work_remains: bool)   # final line, status phase STOPPED
      # renderer thread
      tick(force=False)                  # repaint iff signature changed; heartbeat the status file
      close()
```

`artpiped.py` changes: `main()` builds `RunLog`, `StatusFile`, `Console`; starts a daemon
thread calling `console.tick()` every 0.25 s (exactly Fetcher's `_render_loop`); calls
`console.job_started` right after `claim_next` returns a path (mode = `"edit"` if the job has a
`reference` else `"generate"`, channel = `_channel_of(job_path)`, timeout = the matching
`--timeout-*`/`--gemini-timeout`), `console.job_finished(result)` at the end of `finalize_job`,
and `console.quota(quota_state(detector, configured_n))` after **every** `detector.note_*`
call (the three in `finalize_job`, lines 2068–2079, and the meter refresh at line 2426).
`quota_state()` is a 10-line pure function in `artpiped.py` that reads `Detector`'s public
fields plus `codex_grumpiness.read_meters()`'s last `ok` reading (store the last `weekly`/
`five_h` values on the Detector as two new plain attributes set inside `note_meters` — the only
Detector edit, and it changes no decision). A new `--status` verb (§7) returns before
`ensure_queue_dirs`, like `--dry-run` does today.

Threading facts the implementor must preserve: worker threads (`process_job`) never touch the
console — they already capture all subprocess output (`capture_output=True`) and print nothing.
All `Console` mutations happen on the main thread; `tick()` runs on the renderer thread; one
`threading.RLock` guards the state, as in Fetcher. Every Console method is wrapped so an
exception in presentation can never abort a job (`finalize_job` already promises that for
artreg; the console gets the same guard).

## 3. Streams and TTY gating

- **One stream.** Everything the console prints goes to **stdout**, warnings included. Today
  WARNINGs go to stderr and the rest to stdout, so a `> file` capture loses the warnings; with
  the run log always present there is no reason to keep two streams. (Selftest impact: §10.)
- `_IS_TTY` is read once at import. **TTY:** ANSI colour, the status line is repainted in place
  with `\r\033[K`, a permanent line first clears the status line, prints, and lets the next tick
  repaint beneath it (Fetcher's `record()` sequence). **Not a TTY** (piped, `nohup`, selftest's
  `capture_output`): no escape codes, no repaint; a fresh plain line is appended only when the
  *coarse* signature changes (§4.2), so a piped log stays complete and greppable and never gets
  one line per second.
- The Artist tile (`install_wt_seat_profiles.py`, profile `ARTIST`) runs the daemon in the
  foreground of a Windows Terminal pane and is a real TTY; that is the normal case.

## 4. Line formats (all codex-only; a job's *channel* column is a fact about the job and may read `gemini` while such jobs still exist in `pending/` — no *figure* about gemini is ever shown)

### 4.1 Permanent per-job record — `Console.job_finished`

```
✓ rut_firehawk_grounded_v3_south  edit/codex      62s  PASS                          14:07
✗ korrum_v2_east                  generate/codex  301s  FAIL timeout                  14:09
✗ bilespawn_v1_north_r2           edit/codex      88s  FAIL validator: mask coverage 41%  14:12
```

Columns, left to right: glyph (`✓` green / `✗` red); job id, `_fit` to the label width;
`{mode}/{channel}` padded to 15; elapsed `f"{round(result['elapsed_s'])}s"` right-aligned in 5;
status word `PASS`/`FAIL` padded to 4 (green/red); on FAIL only, a reason ≤ 40 chars; dim
`hh:mm`. PASS is `result["status"] == "ok"` — the same test `finalize_job` uses (line 1975).
The FAIL reason is the first non-empty of: `"timeout"` if `result.get("timed_out")`;
`f"validator: {note}"` when `result.get("validator")` is a failing verdict; else
`result.get("worker_status")`; else the first 40 chars of `result.get("note")`; else
`"failed"`. Label width = terminal columns minus the fixed decoration, clamped to [20, 200]
(Fetcher's `_label_width`), so the line reflows on resize and never wraps.

### 4.2 Live status line — `Console.tick`

Three phases. `2/3` is in-flight jobs over `QuotaState.current_n` (so a ratchet to N=1 reads
`1/1`); the 12-cell bar is the **oldest in-flight job's elapsed / its timeout** (artpiped has no
batch total for Fetcher's done/total bar to mean anything); `+400 pending` is the global
`pending/` count read each tick (`pending_count()` = `len(_job_files(pending_dir))`), and
"in flight" is only *this* daemon's futures — `active/` is shared between concurrent daemons
(comment at line 2476) and must not be counted.

```
▶ WORKING 2/3 ████████░░░░  rut_firehawk_grounded_v3_south 118s, korrum_v2_east 41s  +400 pending  wk 61%
◔ BLOCKED — 400 pending, codex weekly 99% ≥ 99 refuse — admits again Tue 03:00
◔ SLEEPING until 14:35 — 5h window 98% — 400 pending
● IDLE — queue empty  (37 ok, 4 failed this session)  wk 61%
```

Colours: `▶`/`WORKING`/bar cyan (`36`, bold `36;1`), `◔`/`BLOCKED`/`SLEEPING` yellow (`33`),
`●`/`IDLE` green (`32`). `wk 61%` is the codex weekly percentage; when no meter reading has
been taken yet it prints `wk —` (unmeasured is never shown as 0). BLOCKED is shown when nothing
is in flight, `pending/` has claimable jobs, and `QuotaState.admission_blocked` is true; its
tail names the *reason*: `weekly 99% ≥ 99 refuse` / `weekly 99.8% ≥ 99.8 stop` / `hard stop
(TooManyRequests)` and the resume time from `weekly_resets_at` formatted `%a %H:%M` local, or
`— no reset time known` when it is None. SLEEPING is `sleep_until` in the future.

Two signatures: the **fine** signature (TTY) includes elapsed seconds floored to 5 s and the
bar fill; the **coarse** signature (non-TTY and the run log) is `(phase, in-flight ids,
current_n, pending, weekly band)` where weekly band is `<95`, `95–99`, `99–99.8`, `≥99.8`. A
repaint happens on fine change; an appended line happens on coarse change.

### 4.3 Codex quota transition lines — `Console.quota`

Each call diffs the new `QuotaState` against the previous one and prints one timestamped
permanent line per changed fact, in this order, then reflects the state on the status line:

```
[14:12:03] codex: weekly 99% → refusing new claims until Tue 03:00
[14:12:03] codex: weekly 99.8% → stopping all claims until Tue 03:00
[14:12:03] codex: TooManyRequests → hard stop for the rest of this run
[14:12:03] codex: 5h window 90% → concurrency 3→1
[14:12:03] codex: 5h window 98% → sleeping until 14:35
[14:12:03] codex: sustained slowdown (edit median 340s vs 150s baseline) → concurrency 3→1
[14:12:03] codex: weekly 12% → admitting again
[14:12:03] codex: 5h window 40% → concurrency restored to 3
```

Colour: yellow for tightening, green for loosening, red for the hard stop. The slowdown line
needs `Detector.effective_n` and the mode's median: expose them the same way as the meter
percentages (two read-only attributes, no logic change). The once-only `WARNING weekly Codex
usage at N%` at line 339 is **replaced** by these lines (the Detector's `warn_logged` flag may
stay; its print goes). Transitions also go to the run log (`state` kind).

### 4.4 Startup, signal and one-off lines — `Console.info` / `Console.warn`

Format `[hh:mm:ss] text`, dim timestamp; `WARNING` prefix in red where applicable.

```
[08:55:01] artpiped 12345 — 3 workers, 402 pending, log infrastructure/artpipe/logs/artpiped_20260926_085501_12345.log
[08:55:01] codex sandbox ok — seed template matches the installed build (codex-command-runner-0.153.4.exe)
[08:55:01] WARNING codex channel disabled for this run — <codex_sandbox_msg>
[08:55:02] reconciled korrum_v2_east — orphaned in active/ 31m, requeued
[08:55:02] repaired grank_v1_north — manifest present, job file moved to done/
[08:55:02] pruned 3 scratch dirs older than 14d
[14:31:44] signal 15 received — draining 2 in-flight jobs, then exiting
```

`pruned`/`repaired`/`reconciled` collapse to one line each with a count when more than 3 items
(the per-id lines go to the run log).

### 4.5 Stopped line — `Console.stopped`

```
■ stopped — 37 ok, 4 failed, 0 pending, codex weekly 61% (clean drain)
■ stopped — 12 ok, 1 failed, 388 pending, codex weekly 99% (work remains — refusing new claims until Tue 03:00)
■ stopped — 5 ok, 0 failed, 41 pending, codex weekly — (work remains — codex channel disabled this run)
```

The parenthesis is `clean drain` when `pending/` is empty, else `work remains — <reason>`
where the reason is the BLOCKED tail from §4.2, or `queue not exhausted` when nothing blocked
it (a `--once` run that was signalled). Exit code logic is unchanged (`1` iff pending remains).
`hard_stop=… refuse_new=… gemini_spent=…` are gone from the console; the same facts are in the
status file's last snapshot (phase `STOPPED`) for a seat that wants them.

## 5. Status file — `StatusFile`

Path `infrastructure/artpipe/status/artpiped_<pid>.json` (directory gitignored; one file per
running daemon, because two daemons may share the queue). Written with `common.atomic_write_json`
(a) on every fine-signature change, throttled to at most once per second, (b) as a heartbeat
every 10 s from `tick()` even when nothing changed, (c) on stop with `phase: "STOPPED"`, and
removed on clean exit. Shape:

```json
{"schema": 1, "pid": 12345, "host": "DESKTOP", "started_at": 1790000000.0, "updated_at": 1790000123.0,
 "phase": "WORKING",                       "// one of WORKING BLOCKED SLEEPING IDLE STOPPED": "",
 "workers": {"configured": 3, "current_n": 3},
 "in_flight": [{"id": "korrum_v2_east", "mode": "generate", "channel": "codex",
                "started_at": 1790000082.0, "elapsed_s": 41, "timeout_s": 300}],
 "pending": 400,
 "session": {"ok": 37, "failed": 4, "registry_skipped": 12},
 "codex": {"weekly_pct": 61.0, "five_h_pct": 22.0, "weekly_resets_at": null, "sleep_until": null,
           "refuse_new": false, "stop_all": false, "hard_stop": false, "admission_blocked": false,
           "reason": null, "channel_disabled": false},
 "last_record": "✓ rut_firehawk_grounded_v3_south  edit/codex  62s  PASS  14:07",
 "log_path": "infrastructure/artpipe/logs/artpiped_20260926_085501_12345.log",
 "exit": null                              "// {\"code\": 0, \"pending_remaining\": 0} once STOPPED": ""}
```

`weekly_pct`/`five_h_pct` are `null` until the first `ok` meter reading. No gemini key exists in
this file. Paths are repo-relative.

## 6. Per-run log — `RunLog`

**Path:** `infrastructure/artpipe/logs/artpiped_<YYYYMMDD_HHMMSS>_<pid>.log`, created at startup.
**Where and why:** CLAUDE.md's Transient rule routes program-read output to `/tmp` and
human-read-once output to `Transient/`. This file is both — a seat greps it after a crash and a
human tails it — and neither home fits: `/tmp` is tmpfs on this WSL and a diagnosis usually
wants *yesterday's* log after a reboot; `Transient/` is tracked and pushed, and the owner ruled
this log uncommitted. So it lives beside the queue it describes, **gitignored**
(`infrastructure/artpipe/logs/` and `infrastructure/artpipe/status/` added to `.gitignore` next
to the existing `_codex_homes/` and `*.lock` rules), and **pruned at startup**: delete logs older
than `DEFAULT_ARTSRC_PRUNE_DAYS` (14 d, the value scratch dirs already use) and keep at most the
newest 50. Selftest runs pass a tempdir as `--logs-dir`, so tests never write here (mirror the
`done_dir == common.DEFAULT_DONE` guard artreg already uses).

**Format:** plain UTF-8 text, no ANSI, one event per line:
`[YYYY-MM-DD HH:MM:SS] <kind> <text>` with `kind` ∈ `start`, `record`, `state`, `status`, `info`,
`warn`, `note`, `stop`. `record` lines are the §4.1 line minus the trailing `hh:mm`; `state` are
the §4.3 lines; `status` are coarse-signature changes of §4.2; `note` is the class that never
reaches the console. The log is flushed on every write (`line_buffering`), so `tail -f` works.

## 7. `artpiped --status`

Reads every `infrastructure/artpipe/status/artpiped_*.json`, never touches the queue, creates no
directories, takes no lock. For each file prints one block; a file whose `updated_at` is older
than 60 s is `STALE` and, if `pid` is not alive (`os.kill(pid, 0)` on POSIX, `tasklist` not
needed — the daemon runs under WSL), it is deleted and reported as such. `--status --json`
prints the raw snapshots as a JSON list. Exit `0` if at least one live daemon, `1` if none, `2`
if the directory holds only stale files (a seat can branch on it).

```
artpiped 12345 on DESKTOP — WORKING 2/3, 400 pending, 37 ok / 4 failed this session, codex weekly 61%  (heartbeat 4s ago)
  korrum_v2_east                    generate   41s / 300s
  rut_firehawk_grounded_v3_south    edit      118s / 420s
  log: infrastructure/artpipe/logs/artpiped_20260926_085501_12345.log

artpiped 9981 on DESKTOP — STALE, last heartbeat 3h ago, pid dead — status file removed
no live artpiped daemon
```

## 8. Where each existing print goes

| `artpiped.py` line | today | destination |
|---|---|---|
| 339 `WARNING weekly Codex usage at N%` | stderr, once per band | **replaced** by §4.3 transition lines |
| 352 `WARNING primary_resets_at is not a usable epoch` | stderr | `warn` |
| 447 `WARNING unrecognised gemini model` | stderr | `note` (log only) — gemini, §9 |
| 668, 2308 `WARNING throughput.jsonl has N unparseable line(s)` | stderr | `warn`, reworded without "gemini" |
| 2029 `NOTE artreg event skipped … pass --target explicitly` | stderr, per job | `note` (log only), §8.1 |
| 2031 `WARNING artreg event emit raised …` | stderr | `warn` (a real defect) |
| 2043 `WARNING …active/ file disappeared…` | stderr | `warn` |
| 2199–2216 dry-run lines | stdout | unchanged (`--dry-run` is its own report; it may keep the channel label) |
| 2279 `pruned old scratch dir` | stdout, per id | `info`, collapsed (§4.4); per-id to log |
| 2285, 2287 `repaired …` / `repair-only, N completed` | stdout | `info` |
| 2293, 2296 `reconciled …` / `reconcile-only …` | stdout | `info` |
| 2311 `gemini channel already at/over its budget` | stderr | **removed**, §9 |
| 2324 `codex sandbox preflight ok` | stdout | `info` (§4.4 wording) |
| 2326 `CODEX CHANNEL DISABLED` | stderr | `warn`, and `codex.channel_disabled` in the status file |
| 2342 `signal N received` | stderr | `info` (§4.4 wording) |
| 2402 `claimed … as gemini but the reservation was refused` | stderr | `note` (log only), §9 |
| 2487 `stopped. hard_stop=… gemini_spent=…` | stdout | **replaced** by §4.5 |

### 8.1 The artreg NOTE, specifically

Trigger: the `except artreg.RegError` branch in `finalize_job` (line 2028). New behaviour:
`console.note(f"registry skipped for {job_id}: no queued event on record — job filed before the "
f"ART_REGEN_REGISTRY_1 wiring or by hand, so artreg cannot resolve its target (artreg: {exc})")`
and `session.registry_skipped += 1` (status file only). Nothing on the console. The raw `exc`
text is kept at the end of the log line for diagnosis; the daemon's own wording carries no
"pass --target" instruction because the operator of the daemon cannot act on it there.

## 9. Gemini leaves the console surface — its own step, per ruling 2

Do this as one commit, so it cannot be mistaken for "adopt Fetcher's layout" leaving old text in
place. Remove from the **console** (not from the code paths): the budget block at 2311–2313; the
`gemini_hard_stop=` and `gemini_spent=$` fields of the stopped line (2487–2490); the word
"gemini" from the throughput-parse warnings (668, 2308). Demote to log-only `note`: 447 and
2402–2405. Add no gemini key to `QuotaState`, the status line, the status file or `--status`.
`GeminiBudget`, `read_gemini_spend`, `process_gemini_job` and the `--gemini-*` flags stay as
they are; whether they are retired is a separate item to file, not this work.

## 10. Implementation order and the tests that must change

1. `console.py` with `_c/_fit/_term_cols`, `Console` (status line + record + tick), `RunLog`,
   `StatusFile`, `QuotaState`; a `selftest_console.py` that drives `Console` with `_IS_TTY`
   monkeypatched both ways and asserts: one record line per `job_finished`; no appended line on a
   fine-only change when not a TTY; exactly one transition line per changed quota fact;
   `wk —` when `weekly_pct is None`; no ANSI bytes in non-TTY output; `logs_dir`/`status_dir`
   honoured.
2. Wire `main()`: renderer thread, `--logs-dir`/`--status-dir` flags (defaults under
   `common.QUEUE_ROOT`), `job_started`/`job_finished`/`quota` calls, `.gitignore` entries, log
   pruning at startup.
3. Convert every print in §8; delete the `stopped.` field dump.
4. §9 gemini removal, its own commit.
5. `--status` verb.
6. `selftest_artpipe.py` — update these assertions (they grep the old text):
   line 284 `"WORK REMAINS" in proc.stdout` → `"work remains" in proc.stdout` plus the exit code;
   line 830 `"WARNING weekly Codex usage" in proc.stderr` → a `codex: weekly` transition line in
   **stdout**; line 972 `"codex sandbox preflight ok"` → `"codex sandbox ok"` in stdout; line 1001
   `"CODEX CHANNEL DISABLED" in proc.stderr` → `"codex channel disabled"` in **stdout**; line 617
   (dry-run) unchanged. Every scenario passes `--logs-dir`/`--status-dir` under its tempdir.
   Run `python3 src/RimMandrake/Utils/run_selftests.py` before each commit.
7. Update `install_wt_seat_profiles.py`'s ARTIST comment only if the launch line changes (it
   should not), and `infrastructure/artpipe/README.md`'s layout block: add `logs/`, `status/`.

## 11. Acceptance — what the owner should see in the Artist tile

A green `● IDLE — queue empty (0 ok, 0 failed this session)  wk 61%` line at the bottom within a
second of launch; on a filled queue, `▶ WORKING …` with the job ids and a bar that grows; one
`✓`/`✗` line scrolling up per finished job; nothing about artreg; a yellow `codex: weekly …`
line only when the quota band actually changes; and on Ctrl-C the `■ stopped — …` summary.
`python3 src/RimMandrake/Utils/artpipe/artpiped.py --status` from any seat prints the block in
§7 without touching the queue.
