#!/usr/bin/env python3
"""selftest_console.py — proves console.py's presentation contract without
ever touching artpiped.py's job-processing machinery.

Drives `Console` directly (never a subprocess — there is nothing here that
needs a real daemon), with `console._IS_TTY` monkeypatched both ways, and
asserts the properties `artpipe_console_design_2026-09-26.md` §10 step 1
names explicitly:

  - one record line per job_finished
  - no appended line on a fine-only change when not a TTY
  - exactly one transition line per changed quota fact
  - `wk —` when weekly_pct is None
  - no ANSI bytes in non-TTY output
  - logs_dir/status_dir honoured

    python3 selftest_console.py
"""
from __future__ import annotations

import io
import json
import re
import sys
import tempfile
import time
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import console  # noqa: E402

FAILED: list[str] = []
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def ok(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"ok    {name}")
    else:
        FAILED.append(name)
        print(f"FAIL  {name}" + (f"\n      {detail}" if detail else ""))


def make_console(tmp: Path, pending=lambda: 0, configured_n=3) -> console.Console:
    logs_dir = tmp / "logs"
    status_dir = tmp / "status"
    log = console.RunLog.open(logs_dir)
    status = console.StatusFile(status_dir, pid=12345)
    return console.Console(pending, configured_n, log, status, time.time())


_BASE_FIELDS = dict(weekly_pct=10.0, five_h_pct=10.0, weekly_resets_at=None,
                     sleep_until=None, refuse_new=False, stop_all=False,
                     hard_stop=False, admission_blocked=False, current_n=3,
                     slowdown_mode=None, slowdown_median_s=None, slowdown_baseline_s=None)


def base_quota(**overrides) -> console.QuotaState:
    fields = dict(_BASE_FIELDS)
    fields.update(overrides)
    return console.QuotaState(**fields)


def advance(prev: console.QuotaState, **overrides) -> console.QuotaState:
    """Build the NEXT QuotaState from `prev`'s own fields plus overrides —
    unlike `base_quota()`, this never silently resets an unrelated field
    (e.g. current_n) back to its hardcoded default, which would fabricate
    a spurious diff between two calls that were only supposed to change
    ONE fact."""
    fields = {k: getattr(prev, k) for k in _BASE_FIELDS}
    fields.update(overrides)
    return console.QuotaState(**fields)


# --------------------------------------------------------------------------

def test_one_record_line_per_job_finished():
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td))
        try:
            console._IS_TTY = False
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.job_started("jobA", "generate", "codex", 300)
                c.job_finished({"id": "jobA", "channel": "codex", "mode": "generate",
                                 "status": "ok", "elapsed_s": 12.3})
                c.job_started("jobB", "edit", "codex", 420)
                c.job_finished({"id": "jobB", "channel": "codex", "mode": "edit",
                                 "status": "failed", "elapsed_s": 5.0,
                                 "worker_status": "worker_error"})
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("record: exactly one line per job_finished call",
               len(lines) == 2, repr(lines))
            ok("record: PASS line carries the glyph and job id",
               "✓" in lines[0] and "jobA" in lines[0], lines[0])
            ok("record: FAIL line carries the glyph, job id and reason",
               "✗" in lines[1] and "jobB" in lines[1] and "worker_error" in lines[1], lines[1])
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_gemini_job_recovers_mode_and_channel_from_in_flight():
    """A gemini result carries no `mode` key at all — job_finished must
    recover it from the InFlight record job_started created."""
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td))
        try:
            console._IS_TTY = False
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.job_started("gemjob", "generate", "gemini", 200)
                c.job_finished({"id": "gemjob", "channel": "gemini",
                                 "status": "ok", "elapsed_s": 40.0})
            line = buf.getvalue().strip()
            ok("gemini record: mode/channel recovered from in-flight, not the result dict",
               "generate/gemini" in line, line)
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_no_appended_line_on_fine_only_change_when_not_a_tty():
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td), pending=lambda: 5)
        try:
            console._IS_TTY = False
            c.job_started("longjob", "generate", "codex", 300)
            c.quota(base_quota())
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.tick(force=True)   # establish the coarse baseline
                first_len = len(buf.getvalue())
                # A FINE-only change: elapsed seconds tick forward, same
                # phase/ids/current_n/pending/weekly band -> coarse signature
                # is unchanged, so a non-TTY console must print nothing more.
                time.sleep(0.05)
                c.tick(force=False)
                second_len = len(buf.getvalue())
            ok("non-TTY: no appended line on a fine-only-changed tick",
               second_len == first_len, f"{first_len} -> {second_len}")
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_coarse_change_does_append_when_not_a_tty():
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td), pending=lambda: 5)
        try:
            console._IS_TTY = False
            c.quota(base_quota())
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.tick(force=True)
                before = buf.getvalue()
                c.job_started("newjob", "generate", "codex", 300)  # phase IDLE -> WORKING
                c.tick(force=False)
                after = buf.getvalue()
            ok("non-TTY: a genuine phase change DOES append a new line",
               len(after) > len(before), f"{len(before)} -> {len(after)}")
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_exactly_one_transition_line_per_changed_quota_fact():
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td))
        try:
            console._IS_TTY = False
            state = base_quota()
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)  # baseline — must print nothing (nothing to diff yet)
                baseline_out = buf.getvalue()
            ok("quota: first reading establishes a baseline silently",
               baseline_out == "", repr(baseline_out))

            state = advance(state, weekly_pct=99.0, refuse_new=True, admission_blocked=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for the weekly-refuse transition",
               len(lines) == 1 and "refusing new claims" in lines[0], lines)

            state = advance(state, weekly_pct=99.9, refuse_new=False, stop_all=True,
                             admission_blocked=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for the weekly-stop transition",
               len(lines) == 1 and "stopping all claims" in lines[0], lines)

            state = advance(state, weekly_pct=1.0, refuse_new=False, stop_all=False,
                             admission_blocked=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for the weekly-recovery transition",
               len(lines) == 1 and "admitting again" in lines[0], lines)

            state = advance(state, five_h_pct=95.0, current_n=1)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for the 5h-window concurrency drop",
               len(lines) == 1 and "concurrency" in lines[0] and "3→1" in lines[0], lines)

            state = advance(state, five_h_pct=40.0, current_n=3)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for the 5h-window concurrency restore",
               len(lines) == 1 and "restored to 3" in lines[0], lines)

            state = advance(state, current_n=1, slowdown_mode="edit",
                             slowdown_median_s=340.0, slowdown_baseline_s=150.0)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for a row-4 sustained-slowdown drop",
               len(lines) == 1 and "sustained slowdown" in lines[0]
               and "edit median 340s vs 150s baseline" in lines[0], lines)

            # NOTE: current_n deliberately stays at 1 here — the real
            # Detector's effective_n (row 4) is a one-way ratchet that never
            # self-heals, so a hard-stop transition never also moves
            # current_n back up; only a genuine 5h-window recovery does.
            state = advance(state, slowdown_mode=None, slowdown_median_s=None,
                             slowdown_baseline_s=None, hard_stop=True, admission_blocked=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for the hard-stop transition",
               len(lines) == 1 and "TooManyRequests" in lines[0], lines)

            sleep_until = time.time() + 3600
            state = advance(state, hard_stop=False, sleep_until=sleep_until,
                             admission_blocked=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: exactly one line for the sleep transition",
               len(lines) == 1 and "sleeping until" in lines[0], lines)

            buf = io.StringIO()
            with redirect_stdout(buf):
                c.quota(state)  # identical snapshot, nothing changed
            lines = [l for l in buf.getvalue().splitlines() if l.strip()]
            ok("quota: an unchanged snapshot prints nothing",
               lines == [], lines)
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_wk_dash_when_weekly_unmeasured():
    ok("wk text: None reads as 'wk —', never 'wk 0%'",
       console._wk_text(None) == "wk —")
    ok("wk text: a real reading formats minimally",
       console._wk_text(61.0) == "wk 61%")
    ok("wk text: a fractional reading keeps one decimal",
       console._wk_text(99.8) == "wk 99.8%")


def test_no_ansi_bytes_in_non_tty_output():
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td), pending=lambda: 0)
        try:
            console._IS_TTY = False
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.job_started("j1", "generate", "codex", 300)
                c.job_finished({"id": "j1", "channel": "codex", "mode": "generate",
                                 "status": "ok", "elapsed_s": 10})
                c.quota(base_quota())
                c.quota(base_quota(weekly_pct=99.0, refuse_new=True, admission_blocked=True))
                c.warn("a test warning")
                c.info("a test info line")
                c.tick(force=True)
                c.stopped(0, False)
            out = buf.getvalue()
            ok("non-TTY console output carries no ANSI escape bytes",
               not _ANSI_RE.search(out), repr(out))
            log_text = c._log.path.read_text()
            ok("run log carries no ANSI escape bytes either",
               not _ANSI_RE.search(log_text), repr(log_text))
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_ansi_present_when_tty():
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td))
        try:
            console._IS_TTY = True
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.job_started("j1", "generate", "codex", 300)
                c.job_finished({"id": "j1", "channel": "codex", "mode": "generate",
                                 "status": "ok", "elapsed_s": 10})
            out = buf.getvalue()
            ok("TTY console output DOES carry ANSI (glyph/status colour)",
               bool(_ANSI_RE.search(out)), repr(out))
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_logs_dir_and_status_dir_honoured():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        logs_dir = tmp / "custom_logs"
        status_dir = tmp / "custom_status"
        log = console.RunLog.open(logs_dir)
        status = console.StatusFile(status_dir, pid=999)
        c = console.Console(lambda: 0, 3, log, status, time.time())
        try:
            ok("RunLog writes under the given logs_dir",
               log.path.parent == logs_dir and log.path.is_file(), str(log.path))
            c.quota(base_quota())
            with redirect_stdout(io.StringIO()):
                c.tick(force=True)
            ok("StatusFile writes under the given status_dir",
               status.path.parent == status_dir and status.path.is_file(), str(status.path))
            snapshot = json.loads(status.path.read_text())
            ok("status snapshot is valid JSON with the documented top-level keys",
               {"schema", "pid", "phase", "workers", "in_flight", "pending",
                "session", "codex", "log_path", "exit"} <= set(snapshot.keys()),
               list(snapshot.keys()))
        finally:
            c.close()


def test_log_pruning_keeps_recent_and_drops_old():
    with tempfile.TemporaryDirectory() as td:
        logs_dir = Path(td)
        logs_dir.mkdir(exist_ok=True)
        old = logs_dir / "artpiped_20200101_000000_1.log"
        old.write_text("old\n")
        import os as _os
        very_old_time = time.time() - 40 * 86400
        _os.utime(old, (very_old_time, very_old_time))
        log = console.RunLog.open(logs_dir)
        try:
            ok("startup pruning removes a log older than the retention window",
               not old.is_file())
            ok("startup pruning leaves the fresh log this run just opened",
               log.path.is_file())
        finally:
            log.close()


def test_status_file_removed_on_stopped():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        c = make_console(tmp)
        try:
            console._IS_TTY = False
            with redirect_stdout(io.StringIO()):
                c.tick(force=True)
            ok("fixture: status file exists before stop", c._status.path.is_file())
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.stopped(0, False)
            line = buf.getvalue().strip()
            ok("stopped: prints the human summary line",
               line.startswith("■ stopped —") and "clean drain" in line, line)
            ok("stopped: status file is removed on clean exit",
               not c._status.path.is_file())
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


def test_stopped_reports_work_remains_reason():
    with tempfile.TemporaryDirectory() as td:
        c = make_console(Path(td))
        try:
            console._IS_TTY = False
            with redirect_stdout(io.StringIO()):
                c.quota(base_quota())
                c.quota(base_quota(weekly_pct=99.0, refuse_new=True, admission_blocked=True))
            buf = io.StringIO()
            with redirect_stdout(buf):
                c.stopped(12, True)
            line = buf.getvalue().strip()
            ok("stopped: work-remains line names the blocking reason",
               "work remains" in line and "refuse" in line, line)
        finally:
            console._IS_TTY = sys.stdout.isatty()
            c.close()


# --------------------------------------------------------------------------

def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    total = len(FAILED)
    print(f"\n{'FAILED ' + str(total) if total else 'all'} selftest_console checks"
          + (f" failed:\n  " + "\n  ".join(FAILED) if total else " passed"))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
