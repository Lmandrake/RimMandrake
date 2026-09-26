#!/usr/bin/env python3
"""console.py — the artpiped daemon's presentation layer (ARTPIPE_CONSOLE_REDESIGN_1).

Everything artpiped.py shows a human in the Artist tile, and everything it
leaves behind for a Claude seat: a live repainted status line, a permanent
line per finished job, timestamped codex-quota transition lines, a per-run
plain-text log, and a small JSON status file another process can read
(`artpiped.py --status`).

Design: `design/RimMandrake/artpipe_console_design_2026-09-26.md`. Modelled
on the sibling Fetcher project's `core/console.py` — its palette, glyphs and
repaint discipline, restated here rather than imported (this module is
independently importable and has no dependency on that project).

Nothing here knows about codex/gemini workers, subprocesses, or `Detector`
internals — every method is fed plain values (job ids, elapsed seconds,
`QuotaState` snapshots). `common` is imported only for `atomic_write_json`
(per the design's own §5) and `REPO_ROOT` for relative path display — both
already zero-third-party-dependency helpers, so this stays as "stdlib only"
as a module that must interoperate with the rest of this package can be.

Threading: worker threads never call anything here (they only ever return a
result dict; artpiped.py's main thread does all Console mutation).
`tick()` runs on its own renderer thread. One `threading.RLock` guards all
mutable state. Every public method swallows its own exceptions — a bug in
presentation must never abort a job or crash the daemon.
"""
from __future__ import annotations

import json
import os
import platform
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402 — atomic_write_json + REPO_ROOT only

# Read once at import, like Fetcher's own _IS_TTY — a piped/nohup/selftest
# (subprocess.run(capture_output=True)) run is never a TTY, and that fact
# never changes mid-process.
_IS_TTY = sys.stdout.isatty()

_RESET = "\033[0m"

# Display-only mirrors of artpiped.py's WEEKLY_REFUSE/WEEKLY_STOP thresholds
# (99.0 / 99.8, owner ruling 2026-09-23) — needed verbatim in the BLOCKED
# tail's "weekly 99% ≥ 99 refuse" text (design §4.2). Console must not import
# artpiped (artpiped imports console, not the reverse), so these are a
# deliberate, narrow duplication for TEXT ONLY — no admission decision here
# ever reads them; the decision itself lives entirely in QuotaState fields
# computed by artpiped.py's own Detector.
_WEEKLY_REFUSE_DISPLAY = 99.0
_WEEKLY_STOP_DISPLAY = 99.8

# §6: per-run log pruning — same figure DEFAULT_ARTSRC_PRUNE_DAYS already
# uses for _artsrc/ scratch dirs, duplicated here rather than imported from
# artpiped.py to avoid a circular import (artpiped imports console).
_LOG_PRUNE_DAYS = 14.0
_LOG_KEEP_MAX = 50


def _c(text: str, code: str, enabled: bool | None = None) -> str:
    """ANSI-wrap `text` iff enabled (defaults to the module's own _IS_TTY) —
    the log formatter always passes enabled=False explicitly, regardless of
    whether the console itself is a TTY, so the run log never carries ANSI."""
    on = _IS_TTY if enabled is None else enabled
    if not on:
        return text
    return f"\033[{code}m{text}{_RESET}"


def _fit(text: str, width: int) -> str:
    """Collapse internal whitespace, ellipsise if too long, ljust to width."""
    collapsed = " ".join(text.split())
    if width <= 0:
        return ""
    if len(collapsed) > width:
        if width == 1:
            return collapsed[:1]
        return collapsed[: width - 1] + "…"
    return collapsed.ljust(width)


def _term_cols() -> int:
    import shutil as _shutil
    return _shutil.get_terminal_size((80, 24)).columns


def hhmm(ts: float | None = None) -> str:
    return time.strftime("%H:%M", time.localtime(ts if ts is not None else time.time()))


def stamp(ts: float | None = None) -> str:
    return time.strftime("%H:%M:%S", time.localtime(ts if ts is not None else time.time()))


def _pct(x: float | None) -> str:
    """Minimal decimal representation — 99 -> "99%", 99.8 -> "99.8%". Never
    shown for an unmeasured (None) value by any caller that cares (the
    status line's own "wk —" convention); this helper itself renders None
    as an em dash so a caller that forgets the check still fails honestly."""
    if x is None:
        return "—"
    xf = float(x)
    if xf == int(xf):
        return f"{int(xf)}%"
    return f"{xf:.1f}%"


def _wk_text(weekly_pct: float | None) -> str:
    return f"wk {_pct(weekly_pct)}" if weekly_pct is not None else "wk —"


def _reset_text(epoch: float | None) -> str:
    if epoch is None:
        return "an unknown time"
    return time.strftime("%a %H:%M", time.localtime(epoch))


def _bar(frac: float, width: int = 12) -> str:
    frac = max(0.0, min(1.0, frac))
    filled = round(frac * width)
    return "█" * filled + "░" * (width - filled)


def _label_width() -> int:
    """Terminal columns minus the fixed decoration (glyph, mode/channel
    column, elapsed column, status column, hh:mm column, and the spaces
    between them), clamped to [20, 200] — Fetcher's `_label_width`, so the
    job-id column reflows on resize and never wraps."""
    fixed_decoration = 1 + 1 + 15 + 1 + 5 + 1 + 4 + 1 + 5  # = 34
    return max(20, min(200, _term_cols() - fixed_decoration))


# --------------------------------------------------------------------------
# QuotaState / InFlight
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class QuotaState:
    """The ONLY thing the console knows about codex quota. Built by
    artpiped.py's `quota_state()` from `Detector`'s public fields — see that
    function's own docstring for exactly which Detector attributes feed
    each one.

    `slowdown_mode`/`slowdown_median_s`/`slowdown_baseline_s` are not in the
    design doc's literal field list for this dataclass, but are needed to
    render §4.3's own "sustained slowdown (edit median 340s vs 150s
    baseline)" worked example without Console reaching back into Detector
    internals. They are populated ONLY in the snapshot built right after
    `Detector.note_wall_clock()` — see `quota_state()`'s `slowdown=` kwarg —
    so a `current_n` drop diffed at that snapshot is unambiguously row 4,
    never confused with a row-3 five-hour-window drop (which is diffed at
    the separate snapshot taken after `note_meters()` instead).
    """
    weekly_pct: float | None
    five_h_pct: float | None
    weekly_resets_at: float | None
    sleep_until: float | None
    refuse_new: bool
    stop_all: bool
    hard_stop: bool
    admission_blocked: bool
    current_n: int
    slowdown_mode: str | None = None
    slowdown_median_s: float | None = None
    slowdown_baseline_s: float | None = None


@dataclass
class InFlight:
    """One per claimed job. Main thread only — Console owns the whole
    dict, keyed by job id, so `job_finished` can recover a job's mode and
    channel even for a gemini result (whose own result dict carries no
    `mode` key at all)."""
    job_id: str
    mode: str
    channel: str
    started: float
    timeout_s: int


def _weekly_band(pct: float | None) -> str:
    if pct is None:
        return "unmeasured"
    if pct < 95:
        return "<95"
    if pct < 99:
        return "95-99"
    if pct < 99.8:
        return "99-99.8"
    return ">=99.8"


def _quota_diff_lines(prev: QuotaState, new: QuotaState) -> list[tuple[str, str]]:
    """One (ansi_code, text) pair per changed fact, in the order §4.3 shows
    them. `text` excludes the `codex: ` prefix and the leading timestamp —
    the caller (`Console.quota`) adds both."""
    out: list[tuple[str, str]] = []

    if new.refuse_new and not new.stop_all and not prev.refuse_new:
        out.append(("33", f"weekly {_pct(new.weekly_pct)} → refusing new claims "
                          f"until {_reset_text(new.weekly_resets_at)}"))
    if new.stop_all and not prev.stop_all:
        out.append(("33", f"weekly {_pct(new.weekly_pct)} → stopping all claims "
                          f"until {_reset_text(new.weekly_resets_at)}"))
    if new.hard_stop and not prev.hard_stop:
        out.append(("31", "TooManyRequests → hard stop for the rest of this run"))

    # Row 3 concurrency drop: diffed at a note_meters()-derived snapshot
    # (slowdown_mode is None there — see quota_state()), so a current_n
    # drop seen here is never a row-4 slowdown.
    if (new.current_n < prev.current_n and new.slowdown_mode is None
            and not (new.sleep_until and new.sleep_until != prev.sleep_until)):
        out.append(("33", f"5h window {_pct(new.five_h_pct)} → concurrency "
                          f"{prev.current_n}→{new.current_n}"))
    if new.sleep_until and new.sleep_until != prev.sleep_until:
        out.append(("33", f"5h window {_pct(new.five_h_pct)} → sleeping "
                          f"until {hhmm(new.sleep_until)}"))
    # Row 4 slowdown: only ever populated at the note_wall_clock()-derived
    # snapshot, so this and the row-3 check above are mutually exclusive by
    # construction (each fires only at its own call site's snapshot).
    if new.slowdown_mode is not None and new.current_n < prev.current_n:
        med = new.slowdown_median_s if new.slowdown_median_s is not None else 0.0
        base = new.slowdown_baseline_s if new.slowdown_baseline_s is not None else 0.0
        out.append(("33", f"sustained slowdown ({new.slowdown_mode} median "
                          f"{round(med)}s vs {round(base)}s baseline) → "
                          f"concurrency {prev.current_n}→{new.current_n}"))

    if ((prev.refuse_new or prev.stop_all) and not new.refuse_new
            and not new.stop_all and not new.hard_stop):
        out.append(("32", f"weekly {_pct(new.weekly_pct)} → admitting again"))
    if new.current_n > prev.current_n:
        out.append(("32", f"5h window {_pct(new.five_h_pct)} → concurrency "
                          f"restored to {new.current_n}"))
    return out


def _blocked_reason(quota: QuotaState) -> str | None:
    if quota.hard_stop:
        return "hard stop (TooManyRequests)"
    if quota.stop_all:
        return (f"weekly {_pct(quota.weekly_pct)} ≥ {_pct(_WEEKLY_STOP_DISPLAY)} stop"
                f" — admits again {_reset_text(quota.weekly_resets_at)}"
                if quota.weekly_resets_at is not None else
                f"weekly {_pct(quota.weekly_pct)} ≥ {_pct(_WEEKLY_STOP_DISPLAY)} stop "
                f"— no reset time known")
    if quota.refuse_new:
        return (f"weekly {_pct(quota.weekly_pct)} ≥ {_pct(_WEEKLY_REFUSE_DISPLAY)} refuse"
                f" — admits again {_reset_text(quota.weekly_resets_at)}"
                if quota.weekly_resets_at is not None else
                f"weekly {_pct(quota.weekly_pct)} ≥ {_pct(_WEEKLY_REFUSE_DISPLAY)} refuse "
                f"— no reset time known")
    return None


def _fail_reason(result: dict) -> str:
    """§4.1's exact rule: the first non-empty of timeout / a failing
    validator verdict's note / worker_status / the first 40 chars of note /
    "failed"."""
    if result.get("timed_out"):
        return "timeout"
    validator = result.get("validator")
    if validator in ("REJECT", "ERROR", "CANNOT_VALIDATE"):
        note = result.get("note") or ""
        return (f"validator: {note}")[:40]
    ws = result.get("worker_status")
    if ws:
        return str(ws)[:40]
    note = result.get("note") or ""
    if note:
        return str(note)[:40]
    return "failed"


def _format_record(result: dict, mode: str, channel: str, ok: bool,
                    label_width: int | None = None, colored: bool | None = None,
                    include_hhmm: bool = True) -> str:
    """§4.1's per-job record line."""
    on = _IS_TTY if colored is None else colored
    glyph = _c("✓", "32", on) if ok else _c("✗", "31", on)
    lw = label_width if label_width is not None else _label_width()
    label = _fit(str(result.get("id", "?")), lw)
    modecol = _fit(f"{mode}/{channel}", 15)
    elapsed = result.get("elapsed_s")
    elapsed_txt = f"{round(elapsed)}s" if isinstance(elapsed, (int, float)) else "?s"
    elapsed_col = elapsed_txt.rjust(5)
    word = "PASS" if ok else "FAIL"
    status_col = _c(word.ljust(4), "32" if ok else "31", on)
    bits = [glyph, label, modecol, elapsed_col, status_col]
    if not ok:
        bits.append(_fail_reason(result))
    if include_hhmm:
        bits.append(_c(hhmm(), "2", on))
    return "  ".join(bits)


# --------------------------------------------------------------------------
# RunLog — §6
# --------------------------------------------------------------------------

class RunLog:
    """Plain UTF-8 per-run log, gitignored, pruned at startup. Never touched
    by a worker thread; `write()` is cheap enough to call from the main
    thread on every event without a separate buffering scheme."""

    def __init__(self, path: Path, fh):
        self.path = path
        self._fh = fh
        self._lock = threading.Lock()

    @classmethod
    def open(cls, logs_dir: Path) -> "RunLog":
        logs_dir.mkdir(parents=True, exist_ok=True)
        _prune_logs(logs_dir)
        name = f"artpiped_{time.strftime('%Y%m%d_%H%M%S')}_{os.getpid()}.log"
        path = logs_dir / name
        # buffering=1 = line-buffered in text mode; every write() call below
        # writes exactly one newline-terminated line, so this is enough to
        # make `tail -f` work without an explicit flush per call.
        fh = open(path, "a", encoding="utf-8", buffering=1)
        return cls(path, fh)

    def write(self, kind: str, text: str) -> None:
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {kind} {text}\n"
        with self._lock:
            try:
                self._fh.write(line)
            except (OSError, ValueError):
                pass  # a closed/broken log must never take the daemon down

    def close(self) -> None:
        with self._lock:
            try:
                self._fh.close()
            except OSError:
                pass


def _prune_logs(logs_dir: Path, max_age_days: float = _LOG_PRUNE_DAYS,
                 max_kept: int = _LOG_KEEP_MAX) -> None:
    try:
        files = sorted(logs_dir.glob("artpiped_*.log"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        return
    cutoff = time.time() - max_age_days * 86400
    for i, p in enumerate(files):
        try:
            too_old = p.stat().st_mtime < cutoff
        except OSError:
            too_old = False
        if i >= max_kept or too_old:
            try:
                p.unlink()
            except OSError:
                pass


# --------------------------------------------------------------------------
# StatusFile — §5
# --------------------------------------------------------------------------

class StatusFile:
    """`infrastructure/artpipe/status/artpiped_<pid>.json` — one file per
    running daemon. Written via `common.atomic_write_json` so a reader
    (`--status`, or `Console.tick`'s own next read) never sees a half
    written file."""

    def __init__(self, status_dir: Path, pid: int | None = None):
        status_dir.mkdir(parents=True, exist_ok=True)
        self.dir = status_dir
        self.path = status_dir / f"artpiped_{pid if pid is not None else os.getpid()}.json"

    def write(self, snapshot: dict) -> None:
        try:
            common.atomic_write_json(self.path, snapshot)
        except OSError:
            pass  # presentation must never abort the daemon

    def remove(self) -> None:
        try:
            self.path.unlink()
        except OSError:
            pass


def _relpath(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(common.REPO_ROOT))
    except (ValueError, OSError):
        return str(path)


# --------------------------------------------------------------------------
# Console — §3/§4
# --------------------------------------------------------------------------

class Console:
    def __init__(self, pending_count: Callable[[], int], configured_n: int,
                 log: RunLog, status: StatusFile, started_at: float):
        self._pending_count = pending_count
        self._configured_n = configured_n
        self._log = log
        self._status = status
        self._started_at = started_at

        self._lock = threading.RLock()
        self._in_flight: dict[str, InFlight] = {}
        self._quota: QuotaState | None = None
        self._session_ok = 0
        self._session_failed = 0
        self._session_registry_skipped = 0
        self._last_record: str | None = None
        self._codex_channel_disabled = False

        self._last_fine_sig = None
        self._last_coarse_sig = None
        self._last_status_fine_sig = None
        self._last_status_write = 0.0
        self._last_heartbeat = 0.0
        self._stopped = False

    # ---------------------------------------------------------------- main-thread mutations

    def job_started(self, job_id: str, mode: str, channel: str, timeout_s: int) -> None:
        try:
            with self._lock:
                self._in_flight[job_id] = InFlight(job_id, mode, channel, time.time(), timeout_s)
        except Exception:
            pass

    def job_finished(self, result: dict) -> None:
        try:
            with self._lock:
                jid = str(result.get("id", "?"))
                inflight = self._in_flight.pop(jid, None)
                mode = (inflight.mode if inflight else result.get("mode")) or "generate"
                channel = (inflight.channel if inflight else result.get("channel")) or "codex"
                ok = result.get("status") == "ok"
                if ok:
                    self._session_ok += 1
                else:
                    self._session_failed += 1
                line = _format_record(result, mode, channel, ok)
                self._last_record = line
                self._emit_permanent(line)
                self._log.write("record", _format_record(
                    result, mode, channel, ok, colored=False, include_hhmm=False))
        except Exception:
            pass

    def quota(self, state: QuotaState) -> None:
        try:
            with self._lock:
                prev = self._quota
                if prev is None:
                    # No prior reading to diff against — synthesize a
                    # healthy baseline (never a real "sample of one") so a
                    # FIRST-EVER reading that already shows a wedge (the
                    # daemon's very first job runs against an account
                    # already at 99%) still announces it, instead of being
                    # silently swallowed as "just establishing a baseline".
                    prev = QuotaState(weekly_pct=None, five_h_pct=None, weekly_resets_at=None,
                                       sleep_until=None, refuse_new=False, stop_all=False,
                                       hard_stop=False, admission_blocked=False,
                                       current_n=self._configured_n)
                self._quota = state
                for code, text in _quota_diff_lines(prev, state):
                    full = f"[{stamp()}] codex: {text}"
                    self._emit_permanent(_c(full, code))
                    self._log.write("state", f"codex: {text}")
        except Exception:
            pass

    def warn(self, text: str) -> None:
        try:
            line = f"[{stamp()}] WARNING {text}"
            with self._lock:
                self._emit_permanent(_c(line, "31"))
            self._log.write("warn", text)
        except Exception:
            pass

    def info(self, text: str) -> None:
        try:
            line = f"[{stamp()}] {text}"
            with self._lock:
                self._emit_permanent(line)
            self._log.write("info", text)
        except Exception:
            pass

    def note(self, text: str) -> None:
        try:
            self._log.write("note", text)
        except Exception:
            pass

    def note_registry_skipped(self, text: str) -> None:
        """§8.1: the artreg 'no queued event' NOTE — log only, and counted
        in the status file's session.registry_skipped, never shown live."""
        try:
            with self._lock:
                self._session_registry_skipped += 1
            self._log.write("note", text)
        except Exception:
            pass

    def mark_codex_channel_disabled(self) -> None:
        try:
            with self._lock:
                self._codex_channel_disabled = True
        except Exception:
            pass

    def stopped(self, pending_remaining: int, work_remains: bool) -> None:
        """§4.5 final line — the exit-code decision itself is unchanged and
        made by the caller; this only renders the human summary."""
        try:
            with self._lock:
                self._stopped = True
                quota = self._quota
                # §4.5's own worked examples spell this "codex weekly NN%" —
                # distinct from the status line's "wk NN%" shorthand.
                weekly_txt = _pct(quota.weekly_pct if quota else None)
                if not work_remains:
                    paren = "clean drain"
                else:
                    reason = None
                    if self._codex_channel_disabled:
                        reason = "codex channel disabled this run"
                    elif quota is not None and quota.admission_blocked:
                        reason = _blocked_reason(quota)
                    paren = f"work remains — {reason or 'queue not exhausted'}"
                line = (f"■ stopped — {self._session_ok} ok, {self._session_failed} failed, "
                        f"{pending_remaining} pending, codex weekly {weekly_txt} ({paren})")
                self._emit_permanent(line)
                self._log.write("stop", line)
                now = time.time()
                snapshot = self._build_snapshot("STOPPED", quota, pending_remaining, {}, now,
                                                 exit_info={"code": 1 if work_remains else 0,
                                                            "pending_remaining": pending_remaining})
                self._status.write(snapshot)
                self._status.remove()
        except Exception:
            pass

    # ---------------------------------------------------------------- renderer thread

    def tick(self, force: bool = False) -> None:
        try:
            with self._lock:
                if self._stopped:
                    return
                now = time.time()
                pending = self._safe_pending_count()
                quota = self._quota
                in_flight = dict(self._in_flight)
                phase = self._phase(quota, pending, in_flight)
                fine = self._fine_sig(phase, in_flight, quota, pending, now)
                coarse = self._coarse_sig(phase, in_flight, quota, pending)

                if _IS_TTY:
                    if force or fine != self._last_fine_sig:
                        line = self._render_status_line(phase, quota, pending, in_flight, now, colored=True)
                        sys.stdout.write("\r\033[K" + line)
                        sys.stdout.flush()
                else:
                    if force or coarse != self._last_coarse_sig:
                        line = self._render_status_line(phase, quota, pending, in_flight, now, colored=False)
                        sys.stdout.write(line + "\n")
                        sys.stdout.flush()

                if force or coarse != self._last_coarse_sig:
                    plain = self._render_status_line(phase, quota, pending, in_flight, now, colored=False)
                    self._log.write("status", plain)

                due_heartbeat = (now - self._last_heartbeat) >= 10.0
                due_change = (fine != self._last_status_fine_sig
                              and (now - self._last_status_write) >= 1.0)
                if force or due_heartbeat or due_change:
                    self._status.write(self._build_snapshot(phase, quota, pending, in_flight, now))
                    self._last_status_write = now
                    self._last_status_fine_sig = fine
                    if force or due_heartbeat:
                        self._last_heartbeat = now

                self._last_fine_sig = fine
                self._last_coarse_sig = coarse
        except Exception:
            pass

    def close(self) -> None:
        try:
            self._log.close()
        except Exception:
            pass

    # ---------------------------------------------------------------- internals

    def _safe_pending_count(self) -> int:
        try:
            return int(self._pending_count())
        except Exception:
            return 0

    def _emit_permanent(self, line: str) -> None:
        if _IS_TTY:
            sys.stdout.write("\r\033[K" + line + "\n")
        else:
            sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def _phase(self, quota: QuotaState | None, pending: int,
               in_flight: dict[str, InFlight]) -> str:
        if in_flight:
            return "WORKING"
        if quota is not None and quota.sleep_until and time.time() < quota.sleep_until:
            return "SLEEPING"
        if pending > 0 and quota is not None and quota.admission_blocked:
            return "BLOCKED"
        return "IDLE"

    def _fine_sig(self, phase, in_flight, quota, pending, now):
        elapsed_bins = tuple(sorted(int((now - f.started) // 5) * 5 for f in in_flight.values()))
        bar_fill = None
        if in_flight:
            oldest = min(in_flight.values(), key=lambda f: f.started)
            frac = 0.0 if not oldest.timeout_s else \
                max(0.0, min(1.0, (now - oldest.started) / oldest.timeout_s))
            bar_fill = round(frac * 12)
        current_n = quota.current_n if quota else self._configured_n
        return (phase, elapsed_bins, bar_fill, pending, current_n,
                _weekly_band(quota.weekly_pct if quota else None))

    def _coarse_sig(self, phase, in_flight, quota, pending):
        ids = tuple(sorted(in_flight.keys()))
        current_n = quota.current_n if quota else self._configured_n
        return (phase, ids, current_n, pending, _weekly_band(quota.weekly_pct if quota else None))

    def _render_status_line(self, phase, quota, pending, in_flight, now, colored=True) -> str:
        on = colored
        wk = _wk_text(quota.weekly_pct if quota else None)
        current_n = quota.current_n if quota else self._configured_n

        if phase == "WORKING":
            oldest = min(in_flight.values(), key=lambda f: f.started)
            frac = 0.0 if not oldest.timeout_s else \
                max(0.0, min(1.0, (now - oldest.started) / oldest.timeout_s))
            bar = _c(_bar(frac), "36", on)
            jobs_txt = ", ".join(f"{f.job_id} {int(now - f.started)}s"
                                 for f in sorted(in_flight.values(), key=lambda f: f.started))
            glyph = _c("▶", "36", on)
            word = _c("WORKING", "36;1", on)
            return (f"{glyph} {word} {len(in_flight)}/{current_n} {bar}  {jobs_txt}  "
                    f"+{pending} pending  {wk}")

        if phase == "SLEEPING":
            glyph = _c("◔", "33", on)
            word = _c("SLEEPING", "33", on)
            sleep_until = quota.sleep_until if quota else None
            return (f"{glyph} {word} until {hhmm(sleep_until)} — "
                    f"5h window {_pct(quota.five_h_pct if quota else None)} — {pending} pending")

        if phase == "BLOCKED":
            glyph = _c("◔", "33", on)
            word = _c("BLOCKED", "33", on)
            reason = _blocked_reason(quota) if quota else "blocked"
            return f"{glyph} {word} — {pending} pending, codex {reason or 'blocked'}"

        glyph = _c("●", "32", on)
        word = _c("IDLE", "32", on)
        if pending == 0:
            return (f"{glyph} {word} — queue empty  "
                    f"({self._session_ok} ok, {self._session_failed} failed this session)  {wk}")
        return (f"{glyph} {word} — {pending} pending, nothing claimable  "
                f"({self._session_ok} ok, {self._session_failed} failed this session)  {wk}")

    def _build_snapshot(self, phase, quota, pending, in_flight, now, exit_info=None) -> dict:
        in_flight_list = []
        for f in sorted(in_flight.values(), key=lambda x: x.started):
            in_flight_list.append({
                "id": f.job_id, "mode": f.mode, "channel": f.channel,
                "started_at": f.started, "elapsed_s": int(now - f.started),
                "timeout_s": f.timeout_s,
            })
        codex = {
            "weekly_pct": quota.weekly_pct if quota else None,
            "five_h_pct": quota.five_h_pct if quota else None,
            "weekly_resets_at": quota.weekly_resets_at if quota else None,
            "sleep_until": quota.sleep_until if quota else None,
            "refuse_new": bool(quota.refuse_new) if quota else False,
            "stop_all": bool(quota.stop_all) if quota else False,
            "hard_stop": bool(quota.hard_stop) if quota else False,
            "admission_blocked": bool(quota.admission_blocked) if quota else False,
            "reason": (_blocked_reason(quota) if quota and quota.admission_blocked else None),
            "channel_disabled": self._codex_channel_disabled,
        }
        return {
            "schema": 1, "pid": os.getpid(), "host": platform.node(),
            "started_at": self._started_at, "updated_at": now,
            "phase": phase,
            "workers": {"configured": self._configured_n, "current_n": quota.current_n if quota else self._configured_n},
            "in_flight": in_flight_list,
            "pending": pending,
            "session": {"ok": self._session_ok, "failed": self._session_failed,
                        "registry_skipped": self._session_registry_skipped},
            "codex": codex,
            "last_record": self._last_record,
            "log_path": _relpath(self._log.path),
            "exit": exit_info,
        }
