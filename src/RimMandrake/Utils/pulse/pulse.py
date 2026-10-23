#!/usr/bin/env python3
"""rimflow pulse — the away-dashboard spine (AWAY_DASHBOARD_BUILD_1).

  pulse.py daemon              collector loop (5 s) + HTTP/SSE on 127.0.0.1:8765. Run by
                               rm-pulse.service (systemd --user, Restart=always). Nothing
                               else needs to keep it fresh.
  pulse.py collect             one collection, prints the rows (debug)
  pulse.py since [--back | --scheduled | --since ISO] [--quiet]
                               the "since you left" digest: printed with native paths,
                               saved dated under D:\\ClaudeWork\\rimmandrake\\dashboard\\digests\\ and
                               shown in the widget. `./pulse back` is the "I'm back" form.
  pulse.py ack <incident> [--noise]
  pulse.py hand <path-or-url> --read-by seat:<SEAT>|judge:<model> --caught "<one line>"
                [--title "what it is"] [--seat BENCH|FOUNDRY]
                               HAND THE OWNER SOMETHING TO LOOK AT. It appears in the widget's
                               "to look at" list (one line, tiny preview for images, an open link,
                               coloured by --seat) until he opens it, which marks it seen. Use it
                               for a thing you deliberately made for his eyes: a contact sheet,
                               a review page, a keeper save, a folder of shots. Relative paths
                               resolve against the cwd. Nothing reaches the owner unread (owner
                               2026-10-22): --read-by and --caught are required and a missing path is
                               refused. Re-handing the revision he already opened does not re-open it;
                               a changed file (a new revision) does.
                               Review-sheet servers (Transient/biome_ffar/*.serve.log) need no hand: pulse
                               lists every live one whose sheet has a valid pre-review record
                               (src/RimMandrake/Utils/art/prereview.py); the rest are "held back".
  pulse.py withdraw <id> [--by <id|title>]
                               take a hand back (or mark it superseded); it stays listed, dimmed, uncounted
  pulse.py seen <id>           mark a look item seen without opening it (ids print from `hand`)
  pulse.py report <task> failed|ok [--cause ..] [--blocks] [--lost] [--seat ..] [--link ..]
                               one attempt of a build/selftest/artpipe/digest job; red only when work stays
                               blocked (--blocks, 15 min) or output is lost (--lost); else history
  pulse.py metrics             time-to-notice red, question age, alert precision
  pulse.py refresh             ask the running daemon for a full re-collect now (the widget's ⟳ button)
  pulse.py update [--restart]  fast-forward THIS checkout to origin/main (the dedicated deploy checkout
                               under the agent storage root; refuses a seat clone), restart on new code

State: ~/.local/state/rm-dashboard/ (state.json and pulse_now.json - daemon only; last_digest.json - `since`
only; hands.jsonl, failures.jsonl, pulse.jsonl, metrics.jsonl - append-only).
The widget is src/RimMandrake/Utils/pulse/widget/ (Windows, pywebview).
"""
from __future__ import annotations

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import hashlib
import re
import json
import os
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pulse_core as pc  # noqa: E402

HERE = Path(__file__).resolve().parent
WIDGET_HTML = HERE / "widget" / "index.html"
PORT = int(os.environ.get("RM_PULSE_PORT", "8765"))
DIGEST_DIR = Path(os.environ.get("RM_PULSE_DIGESTS", rm_str("dashboard", "digests")))
INTERVAL = 5.0
REFRESH_TIMEOUT = 40.0   # a refresh that has not finished collecting by then answers with why

# Phone push: NOT decided by the owner yet (2026-10-08). Hook point only; stays off until
# he rules. Wire ntfy (or anything) here, never in the widget.
PHONE_PUSH_ENABLED = False


def notify_phone(row: dict) -> None:
    if not PHONE_PUSH_ENABLED:
        return


# ---------------------------------------------------------------- state io

def _p(name: str) -> Path:
    pc.STATE_DIR.mkdir(parents=True, exist_ok=True)
    return pc.STATE_DIR / name


def load_state() -> dict:
    try:
        return json.loads(_p("state.json").read_text())
    except (OSError, ValueError):
        return {}


def save_json(name: str, obj) -> None:
    """Atomic replace through a tmp name unique to this process AND thread: two writers sharing one `.tmp`
    could rename each other's half-written file into place (RIMPULSE_STATE_FIX_TWO_WRITERS_ONE_FILE)."""
    p = _p(name)
    tmp = p.with_name(f"{p.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False))
    os.replace(tmp, p)


# ONE WRITER PER FILE (RIMPULSE_STATE_FIX_TWO_WRITERS_ONE_FILE, GPT rec 9): state.json is written only by the
# daemon process; `pulse.py since` writes only last_digest.json, which the daemon reads on every tick. Before,
# the digest process rewrote state.json from its own copy, so an ack or seen the daemon saved in between could
# be lost (the lock was process-local), and both used one `.tmp` name.
LAST_DIGEST = "last_digest.json"


def load_last_digest() -> dict | None:
    try:
        d = json.loads(_p(LAST_DIGEST).read_text())
        return d if isinstance(d, dict) and d.get("rec") else None
    except (OSError, ValueError):
        return None


ROTATE_BYTES = 32 << 20   # an append-only log past this is renamed <stem>.<YYYYmmdd-HHMMSS-micro>.jsonl and restarted


def append(name: str, rec: dict) -> None:
    rec.setdefault("ts", time.time())
    p = _p(name)
    try:
        if p.stat().st_size > ROTATE_BYTES:   # metrics.jsonl reached 253 MB unrotated (MEASURED 2026-10-22)
            os.replace(p, p.with_name(f"{p.stem}.{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}{p.suffix}"))
    except OSError:
        pass
    with open(p, "a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


_lock = threading.RLock()

# ---------------------------------------------------------------- collection


class Collector:
    def __init__(self):
        self.state = load_state()
        self.snapshot: dict = {}
        self.version = 0
        self.cond = threading.Condition()
        self.probe: dict | None = None
        self.artpipe: dict = {}
        self.ledger_cache: dict = {}
        self.prev_kinds: dict = {}
        self.kernel: dict = {}
        self.sheets: dict = {"at": 0, "rows": []}
        self.tick_lock = threading.Lock()   # one collection at a time: the 5 s loop and a refresh never interleave
        self.last_refresh: dict | None = None
        self.wake = threading.Event()       # ack/seen ask the ONE loop for an early tick; they never start their own

    def _ledger(self) -> list[dict]:
        """Re-read (and re-fold through rimflow's replay) only when a ledger file in either clone moved.
        The 5 s tick is the latency: a rimflow write in either seat's clone reaches the widget on the
        next tick, with no push/pull in the path (both clones are local disk)."""
        sig = []
        for f in pc.ledger_files():
            try:
                st = f.stat()
                sig.append((str(f), st.st_mtime_ns, st.st_size))
            except OSError:
                pass
        if self.ledger_cache.get("sig") != sig or self.ledger_cache.get("force"):
            events = pc.read_ledger()
            self.ledger_cache = {"sig": sig, "events": events, "rulings": pc.owner_rulings(events),
                                 "changed_at": time.time()}
        return self.ledger_cache["events"]

    def gather(self, now: float, force: bool = False) -> dict:
        """force=True (a refresh) re-reads every source now: the ledger is re-folded even if no file moved,
        and the kernel log and sheet servers skip their 20 s / 45 s caches."""
        status, raw = {}, {"at": {}}
        if force:
            self.ledger_cache["force"] = True
            self.kernel["at"] = 0
            self.sheets["at"] = 0

        def src(name, fn):
            t0 = time.time()
            try:
                v = fn()
                status[name] = {"ok": True, "at": now, "ms": round((time.time() - t0) * 1000)}
                return v
            except Exception as e:  # a broken source degrades coverage; it never guesses
                status[name] = {"ok": False, "at": self.snapshot.get("sources", {}).get(name, {}).get("at"),
                                "error": f"{type(e).__name__}: {e}"[:160]}
                return None

        sessions = src("sessions", pc.read_sessions) or []
        raw["sessions"] = sessions
        raw["boot"] = pc.boot_time()
        raw["extras"] = src("subagents", lambda: {s.get("sessionId"): pc.session_extras(s.get("sessionId"), now)
                                                  for s in sessions if s.get("alive")}) or {}
        if now - self.kernel.get("at", 0) > 20:
            k = src("kernel", pc.read_kernel_oom)
            self.kernel = {"at": now, "kills": k}
        else:
            status["kernel"] = self.snapshot.get("sources", {}).get("kernel", {"ok": True, "at": now})
        raw["kernel_oom"] = self.kernel.get("kills")
        raw["memwatch"] = src("memwatch", lambda: pc.read_jsonl_tail(pc.MEMWATCH_EVENTS, 2 << 20, strict=True)) or []
        raw["ledger"] = src("ledger", self._ledger) or []
        raw["rulings"] = self.ledger_cache.get("rulings") if raw["ledger"] else None
        if raw["ledger"]:
            status["ledger"].update({"events": len(raw["ledger"]), "changed_at": self.ledger_cache.get("changed_at")})
        a = src("artpipe", lambda: pc.read_artpipe(pc.ARTPIPE_DIR, self.artpipe, now))
        if a:
            self.artpipe = a
        raw["artpipe"] = self.artpipe
        raw["hands"] = src("hands", pc.read_hands) or []
        raw["failures"] = src("failures", pc.read_failures) or []
        if now - self.sheets["at"] > 45:
            r = src("sheets", pc.read_sheets)
            if r is not None:
                self.sheets = {"at": now, "rows": r}
        else:
            status["sheets"] = self.snapshot.get("sources", {}).get("sheets", {"ok": True, "at": now})
        raw["sheets"] = self.sheets["rows"]
        raw["bridge"] = src("bridge", pc.read_bridge)
        raw["telemetry"] = src("telemetry", pc.read_telemetry)
        raw["services"] = src("services", pc.read_services) or {}
        raw["probe"] = self.probe
        status["probe"] = {"ok": self.probe is not None, "at": (self.probe or {}).get("at")}
        raw["source_status"] = status
        return raw

    def tick(self, force: bool = False) -> dict:
        with self.tick_lock:
            return self._tick(force)

    def _tick(self, force: bool) -> dict:
        # snapshot time never moves backwards, even if the wall clock steps back (GPT rec 9's check)
        now = max(time.time(), self.snapshot.get("collected_at") or 0)
        raw = self.gather(now, force)
        with _lock:
            ld = load_last_digest()   # written by `pulse.py since` (its only file); merged here, by the one writer
            if ld and (ld["rec"].get("at") or 0) > ((self.state.get("last_digest") or {}).get("at") or 0):
                self.state["last_digest"] = ld["rec"]
                self.state["done_since"] = ld.get("done_since")
            snap, new_state, events = pc.collect_snapshot(raw, self.state, now)
            self._notice_metrics(snap, new_state, now)
            snap["digest"] = new_state.get("last_digest")
            snap["widget_version"] = widget_version()
            snap["code"] = code_rev()
            snap["refresh"] = self.last_refresh
            self.state = new_state
            save_json("state.json", self.state)
            save_json("pulse_now.json", snap)
        for ev in events:
            append("metrics.jsonl", ev)
        kinds = {r["key"]: r["kind"] for r in snap["rows"]}
        for k, kind in kinds.items():
            if self.prev_kinds.get(k) != kind:
                append("pulse.jsonl", {"key": k, "kind": kind, "was": self.prev_kinds.get(k)})
                if kind in ("red", "amber"):
                    notify_phone(next(r for r in snap["rows"] if r["key"] == k))
        self.prev_kinds = kinds
        with self.cond:
            self.snapshot = snap
            self.version += 1
            self.cond.notify_all()
        return snap

    def _notice_metrics(self, snap: dict, state: dict, now: float) -> None:
        """time-to-notice red: first owner prompt (any window) after the incident opened."""
        noticed = state.setdefault("noticed", {})
        reds = [r for r in snap["rows"] if r["kind"] == "red" and r["incident"] not in noticed]
        if not reds:
            return
        oldest = min(r["since"] for r in reds)
        prompts = sorted((h.get("timestamp") or 0) / 1000 for h in pc.owner_prompts(oldest))
        for r in reds:
            after = [t for t in prompts if t > r["since"]]
            if after:
                noticed[r["incident"]] = after[0]
                append("metrics.jsonl", {"m": "red_noticed", "id": r["incident"], "via": "next_prompt",
                                         "latency_s": round(after[0] - r["since"])})
        # forget a noticed incident only once it has left the screen: pruning one still showing made
        # it "noticed" again every 5 s tick (MEASURED 2026-10-22: metrics.jsonl at 253 MB of re-notices)
        live = {r.get("incident") for r in snap["rows"]}
        for k in list(noticed):
            if k not in live and now - noticed[k] > 3 * 86400:
                noticed.pop(k)

    def ack(self, inc: str, label: str = "actionable", actor: str = "unknown") -> bool:
        with _lock:
            row = next((r for r in self.snapshot.get("rows", []) if r.get("incident") == inc), None)
            acks = self.state.setdefault("acks", {})
            acks[inc] = {"at": time.time(), "count": (row or {}).get("count", 1), "label": label}
            # keep the ack table small: drop acks older than 3 days
            for k in [k for k, v in acks.items() if time.time() - v.get("at", 0) > 3 * 86400]:
                acks.pop(k)
            save_json("state.json", self.state)
        append("metrics.jsonl", {"m": "alarm_ack", "id": inc, "label": label, "actor": actor,
                                 "kind": (row or {}).get("kind"),
                                 "latency_s": round(time.time() - (row or {}).get("since", time.time()))})
        self.wake.set()
        return True

    def seen(self, sid: str) -> bool:
        """Mark a look opened. For a hand, the revision he opened is kept too: re-handing that same revision
        does not re-open it, a new one does."""
        rev = next((r.get("rev") for r in self.snapshot.get("rows", []) if r.get("seen_id") == sid), None)
        with _lock:
            self.state.setdefault("seen_look", {})[sid] = time.time()
            if rev:
                self.state.setdefault("seen_rev", {})[sid] = rev
            save_json("state.json", self.state)
        self.wake.set()
        return True

    def refresh(self, timeout: float = REFRESH_TIMEOUT) -> dict:
        """A full re-collect, synchronously, bounded by `timeout`. The answer always says what happened: the
        new collected_at, or why there is none - a refresh never silently keeps the old data."""
        t0, box = time.time(), {}

        def run():
            try:
                box["snap"] = self.tick(force=True)
            except Exception as e:  # reported to the widget, never swallowed
                box["error"] = f"{type(e).__name__}: {e}"[:200]
                return
            if box.get("timed_out"):   # it finished after the answer said it had not: say so, once
                self.last_refresh = {"ok": True, "late": True, "at": time.time(),
                                     "ms": round((time.time() - t0) * 1000),
                                     "collected_at": box["snap"]["collected_at"], "sources_down": {}}
        th = threading.Thread(target=run, daemon=True)
        th.start()
        th.join(timeout)
        ms = round((time.time() - t0) * 1000)
        if th.is_alive():
            box["timed_out"] = True
            res = {"ok": False, "at": time.time(), "ms": ms,
                   "error": f"collection still running after {int(timeout)} s (data shown is from "
                            f"{time.strftime('%H:%M:%S', time.localtime(self.snapshot.get('collected_at') or 0))})"}
        elif "error" in box:
            res = {"ok": False, "at": time.time(), "ms": ms, "error": "collection failed: " + box["error"]}
        else:
            snap = box["snap"]
            down = {k: v.get("error") or v.get("stale") for k, v in (snap.get("sources") or {}).items()
                    if not v.get("ok") or v.get("stale")}
            res = {"ok": True, "at": time.time(), "ms": ms, "collected_at": snap["collected_at"],
                   "sources_down": down}
        if not (box.get("timed_out") and "snap" in box):   # a late finish already wrote the truer answer
            self.last_refresh = res
        with self.cond:   # the next snapshot carries it; push it now too so the widget sees a failure at once
            if self.snapshot:
                self.snapshot = {**self.snapshot, "refresh": res}
                self.version += 1
                self.cond.notify_all()
        append("metrics.jsonl", {"m": "refresh", "ok": res["ok"], "ms": ms})
        return res

    def hand_row(self, sid: str) -> dict | None:
        return next((h for h in pc.read_hands() if h["id"] == sid), None)


def thumb_bytes(path: str, w: int = 78, h: int = 54) -> bytes | None:
    """Cached small JPEG of a handed image (3x the 26x18 chip, so it stays sharp)."""
    import io
    from PIL import Image
    src = Path(path)
    try:
        key = hashlib.sha1(f"{src}|{src.stat().st_mtime_ns}".encode()).hexdigest()[:16]
        cache = pc.STATE_DIR / "thumbs"
        cache.mkdir(parents=True, exist_ok=True)
        c = cache / f"{key}.jpg"
        if c.exists():
            return c.read_bytes()
        from PIL import ImageOps
        with Image.open(src) as im:
            im = ImageOps.fit(im.convert("RGB"), (w, h))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=80)
        c.write_bytes(buf.getvalue())
        return buf.getvalue()
    except Exception:
        return None


READ_BY_RE = re.compile(r"(seat|judge):\S.*")   # the prereview.py vocabulary: the seat that looked, or a naive judge


def target_rev(path: str) -> str | None:
    """A content revision for a handed path: sha1 of the file's bytes (size+mtime past 64 MB), or of a folder's
    listing (names, sizes, mtimes). None for a url. Re-handing the same revision does not re-open it."""
    p = Path(path)
    h = hashlib.sha1()
    if p.is_file():
        st = p.stat()
        if st.st_size > 64 << 20:
            h.update(f"{st.st_size}:{st.st_mtime_ns}".encode())
        else:
            h.update(p.read_bytes())
    elif p.is_dir():
        for c in sorted(p.rglob("*")):
            if c.is_file():
                st = c.stat()
                h.update(f"{c.relative_to(p)}:{st.st_size}:{st.st_mtime_ns}\n".encode())
    else:
        return None
    return h.hexdigest()[:12]


def hand(target: str, title: str | None, seat: str | None, read_by: str | None = None,
         caught: str | None = None) -> dict:
    """Write one hand-off record (pure file append; the daemon picks it up within 5 s). REFUSES (ValueError) a
    path that does not exist and a hand nobody read first - Nothing reaches the owner unread (owner 2026-10-22):
    `read_by` is `seat:<SEAT>` or `judge:<model>`, `caught` one line of what was fixed or dropped ('nothing' is
    a valid answer)."""
    if not (read_by and READ_BY_RE.fullmatch(read_by.strip())):
        raise ValueError(f"--read-by {read_by!r}: say who looked at it first, 'seat:<SEAT>' or 'judge:<model>' "
                         "(Nothing reaches the owner unread, owner 2026-10-22)")
    if not (caught or "").strip():
        raise ValueError("--caught is empty: one line of what was fixed or dropped before he sees it ('nothing' is valid)")
    if re.match(r"^https?://", target):
        tgt, win, rev = target, None, None
    else:
        p = Path(target).expanduser()
        p = p if p.is_absolute() else Path.cwd() / p
        tgt = os.path.normpath(str(p))
        if not os.path.exists(tgt):
            raise ValueError(f"no such target: {tgt} (a hand of a missing file is a delivery problem)")
        win, rev = pc.win_path(tgt), target_rev(tgt)
    rec = {"id": "hand:" + hashlib.sha1(tgt.encode()).hexdigest()[:10], "target": tgt, "win": win,
           "title": title or Path(tgt).name or tgt, "seat": (seat or "").upper() or None, "ts": time.time(),
           "rev": rev, "read_by": read_by.strip(), "caught": caught.strip()[:200]}
    append("hands.jsonl", rec)
    return rec


def withdraw(hid: str, superseded_by: str | None = None) -> dict:
    """Withdraw a hand (or mark it superseded by another hand id / title). It stays listed, dimmed and uncounted,
    so what he already opened keeps its history."""
    known = {h["id"]: h for h in pc.read_hands()}
    if hid not in known:
        raise ValueError(f"no hand {hid!r} (ids print from `hand`; known: {', '.join(sorted(known)) or 'none'})")
    rec = {"id": hid, "withdrawn": time.time(), "superseded_by": superseded_by}
    append("hands.jsonl", rec)
    return rec


ROOT = Path(__file__).resolve().parents[4]   # the checkout this code runs from
# what the sparse deploy checkout holds (systemd/install.sh sets the same list): pulse itself, rimflow's fold,
# and art/ for prereview.py (the "to look at" gate). Files directly in a parent dir (Utils/rmpaths.py) come free.
SPARSE_DIRS = ("src/RimMandrake/Utils/pulse", "src/RimMandrake/rimflow", "src/RimMandrake/Utils/art")
_CODE: dict = {}


def code_rev(root: Path = ROOT) -> dict:
    """Which revision is running, read once per process (the code cannot change under a running daemon;
    `update` restarts it). `deploy` = the dedicated origin/main checkout; `seat clone` = a working tree."""
    if _CODE.get("root") != str(root):
        import subprocess
        r = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%H%x00%cI%x00%s"],
                           capture_output=True, text=True, timeout=15)
        sha, at, subj = (r.stdout.strip().split("\x00") + ["", "", ""])[:3] if r.returncode == 0 else ("", "", "")
        _CODE.clear()
        _CODE.update(root=str(root), sha=sha[:12] or "unknown", committed_at=at, subject=subj[:100],
                     checkout="seat clone" if root in pc.CLONES else "deploy" if sha else "unknown",
                     started_at=time.time())
    return dict(_CODE)


def update_code(root: Path = ROOT, timeout: float = 60) -> dict:
    """Fast-forward the deploy checkout to origin/main. Refuses a seat clone: pulling there would move
    another agent's working tree under it (RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE)."""
    import subprocess
    if root in pc.CLONES:
        raise RuntimeError(f"{root} is a seat clone, not the deploy checkout; never pulled from here")

    def git(*a):
        return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, timeout=timeout)
    old = git("rev-parse", "HEAD").stdout.strip()
    have = set(git("sparse-checkout", "list").stdout.split())
    if have and not set(SPARSE_DIRS) <= have:   # a dir pulse newly imports from (art/ for prereview.py, 2026-10-23)
        s = git("sparse-checkout", "set", *SPARSE_DIRS)
        if s.returncode != 0:
            raise RuntimeError(f"git sparse-checkout set: rc {s.returncode}: {(s.stderr or s.stdout).strip()[:200]}")
    p = git("pull", "--ff-only", "-q", "origin", "main")
    if p.returncode != 0:
        raise RuntimeError(f"git pull --ff-only: rc {p.returncode}: {(p.stderr or p.stdout).strip()[:200]}")
    new = git("rev-parse", "HEAD").stdout.strip()
    return {"old": old[:12], "new": new[:12], "changed": old != new}


def widget_version() -> str:
    try:
        return hashlib.sha1(WIDGET_HTML.read_bytes()).hexdigest()[:10]
    except OSError:
        return "missing"

# ---------------------------------------------------------------- digest


def back_since(now: float) -> float:
    """Owner's last prompt before the most recent >=30 min gap in his prompt stream."""
    ts = sorted((h.get("timestamp") or 0) / 1000 for h in pc.owner_prompts(now - 36 * 3600))
    ts = [t for t in ts if t < now - 120]
    gaps = [(ts[i], ts[i + 1]) for i in range(len(ts) - 1) if ts[i + 1] - ts[i] >= 1800]
    if ts and now - 120 - ts[-1] >= 1800:
        return ts[-1]
    if gaps:
        return gaps[-1][0]
    return now - 12 * 3600


def parse_since(v: str) -> float:
    """How far back: a duration ("3h", "90m", "2d", "1h30m"), a clock time today ("17:30"), or ISO."""
    import re as _re
    v = v.strip().lower()
    m = _re.fullmatch(r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?", v)
    if m and any(m.groups()):
        d, h, mi = (int(x or 0) for x in m.groups())
        return time.time() - (d * 86400 + h * 3600 + mi * 60)
    m = _re.fullmatch(r"(\d{1,2}):(\d{2})", v)
    if m:
        lt = time.localtime()
        t = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, int(m[1]), int(m[2]), 0, 0, 0, -1))
        return t if t <= time.time() else t - 86400
    return pc.iso_to_epoch(v)


DIGEST_CAP_SECS = 16 * 3600   # a scheduled digest never reaches back further than this


def _hm(t: float) -> str:
    return time.strftime("%H:%M", time.localtime(t))


def build_digest(snap: dict, since: float, now: float) -> list[dict]:
    """Pure: the return brief as sections answering his three questions (GPT rec 3,
    RIMPULSE_DIGEST_REBUILD_THREE_QUESTIONS) - what broke (incl. recovered, and older faults still broken
    now), what needs his verdict or a fact, what to look at - each split NEW (since >= the interval start)
    from BACKLOG (waiting from before), then what got done. Every row appears exactly once.
    -> [{"id", "title", "lines": [{g, kind, t, text, link, new}], "backlog": [{...}]}]"""
    rows, used = snap.get("rows") or [], set()

    def take(r) -> bool:
        if r["key"] in used:
            return False
        used.add(r["key"])
        return True

    def line(g, r, text=None):
        return {"g": g, "kind": r["kind"], "t": r.get("since") or 0, "text": text or r["text"],
                "link": r.get("link"), "new": (r.get("since") or 0) >= since}

    issues = []
    for r in rows:
        if r["kind"] == "red" and take(r):
            old = (r.get("since") or 0) < since
            issues.append(line("✖", r, r["text"] + (" · still broken, from before the interval" if old else "")))
    for r in rows:   # broke and recovered inside the interval: history he should still hear about
        if r["kind"] == "recovered" and (r.get("since") or 0) >= since and take(r):
            issues.append(line("↺", r))
    for r in rows:   # a job that failed in the interval and is not blocking anything: history, said once
        if r["kind"] == "failed" and (r.get("since") or 0) >= since and take(r):
            issues.append(line("·", r))
    for r in rows:
        if r["kind"] == "warn" and not r.get("acked") and take(r):
            issues.append(line("◆", r))
    asks, ask_old = [], []
    for r in rows:
        if r["kind"] == "amber" and r.get("seat") and take(r):   # a card up right now is always news
            asks.append({**line("◐", r, f"{r['who']} asks: {r.get('full') or r.get('question') or r['text']}"), "new": True})
    for kind, g in (("review", "◇"), ("provide", "✎")):
        for r in rows:
            if r["kind"] == kind and take(r):
                (asks if (r.get("since") or 0) >= since else ask_old).append(
                    line(g, r, f"{r['text']}" + (" (a fact only you have)" if kind == "provide" else "")))
    looks, look_old = [], []
    for r in rows:
        if r["kind"] == "look" and not r.get("opened") and take(r):
            (looks if (r.get("since") or 0) >= since else look_old).append(
                line("▣", r, (r.get("title") or r["text"]) + (" (target missing - a delivery problem)" if r.get("missing") else "")))
    held = sum(1 for r in rows if r["kind"] == "held")
    done = [line("✓", r, f"{r['who']:<8} {r['text']}") for r in sorted(rows, key=lambda r: r.get("since") or 0)
            if r["kind"] == "done" and (r.get("since") or 0) >= since and take(r)]
    answered = [r for r in rows if r["kind"] == "answered"]
    out = [{"id": "issues", "title": "What broke", "lines": issues, "backlog": []},
           {"id": "rule", "title": "Needs your verdict or a fact", "lines": asks, "backlog": ask_old,
            "note": (f"{len(answered)} you already answered, an agent still owes the follow-through"
                     if answered else "")},
           {"id": "look", "title": "To look at", "lines": looks, "backlog": look_old,
            "note": f"{held} held back: nobody recorded reading them first" if held else ""},
           {"id": "done", "title": "Done", "lines": done, "backlog": []}]
    return out


def make_digest(mode: str, since: float | None = None) -> dict:
    now = time.time()
    state = load_state()   # read only: this process never writes state.json
    ld = load_last_digest()
    if ld and (ld["rec"].get("at") or 0) > ((state.get("last_digest") or {}).get("at") or 0):
        state["last_digest"] = ld["rec"]   # the daemon may not have merged our last one yet
    if since is not None:
        basis = "the interval you asked for"
    elif mode == "back":
        since = back_since(now)
        basis = "INFERRED: your last prompt before a 30-min gap"
    else:
        last = (state.get("last_digest") or {}).get("at") or 0
        since = max(last, now - DIGEST_CAP_SECS)
        basis = (f"since the last digest ({time.strftime('%a %H:%M', time.localtime(last))})" if last >= now - DIGEST_CAP_SECS
                 else f"the last {DIGEST_CAP_SECS // 3600} h (no digest since)")
    col = Collector()
    raw = col.gather(now)
    snap, _, _ = pc.collect_snapshot(raw, {**state, "done_since": since}, now)
    secs = build_digest(snap, since, now)
    c = snap["counts"]
    tail = f"{c['filed']} filed · {c['implemented']} implemented · {c['closed']} closed · {c['verifies']} verifies · {c['drops']} drops"
    span = now - since
    head = (f"rimflow since {time.strftime('%a %H:%M', time.localtime(since))} → {time.strftime('%a %H:%M', time.localtime(now))}"
            f"  ({int(span // 3600)}h {int(span % 3600 // 60)}m · {mode} · interval: {basis})")
    stamp = datetime.fromtimestamp(now).strftime("%Y-%m-%d_%H%M")
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    path = DIGEST_DIR / f"digest_{stamp}_{mode}.md"

    def fmt(ln, md=False):
        if not ln["t"]:
            when = "     "
        elif ln["kind"] in ("amber", "review", "provide", "look") or not ln["new"]:
            a = now - ln["t"]
            when = (f"{int(a // 60)}m" if a < 3600 else f"{int(a // 3600)}h" if a < 86400 else f"{int(a // 86400)}d").rjust(5)
        else:
            when = _hm(ln["t"]).rjust(5)
        link = ln.get("link") or {}
        lv = f"   {link['value']}" if link else ""
        return f"{ln['g']} {when}  {ln['text']}{('  `' + link['value'] + '`') if (md and link) else lv}"
    text, md, lines = [head], [f"# {head}", ""], []
    for sc in secs:
        n_new, n_old = len(sc["lines"]), len(sc["backlog"])
        label = f"{sc['title']}: {n_new} new" + (f" · {n_old} waiting from before" if n_old else "")
        if sc["id"] in ("issues", "done"):
            label = f"{sc['title']}: {n_new}"
        text.append(label)
        md += [f"## {label}", ""]
        for ln in sc["lines"]:
            text.append("  " + fmt(ln))
            md.append(f"- {fmt(ln, True)}")
        if sc["backlog"]:   # the backlog is one line of names, never a second copy of yesterday's digest
            names = ", ".join(ln["text"].split(" — ")[0] for ln in sorted(sc["backlog"], key=lambda x: x["t"]))
            text.append(f"  … from before: {names}")
            md.append(f"- _from before:_ {names}")
        if sc.get("note"):
            text.append(f"  ({sc['note']})")
            md.append(f"- _{sc['note']}_")
        if not sc["lines"] and not sc["backlog"]:
            text.append("  nothing")
            md.append("- nothing")
        md.append("")
        lines += [{**ln, "section": sc["id"]} for ln in sc["lines"] + sc["backlog"]]
    text.append("  · " + tail)
    md += [f"_{tail}_", ""]
    path.write_text("\n".join(md))
    rec = {"at": now, "mode": mode, "since": since, "basis": basis, "path": pc.win_path(str(path)), "head": head,
           "tail": tail, "lines": lines}
    save_json(LAST_DIGEST, {"rec": rec, "done_since": since})   # the daemon merges it into state.json
    append("metrics.jsonl", {"m": "digest", "mode": mode, "since": since, "lines": len(lines),
                             "new": sum(1 for ln in lines if ln["new"])})
    return {"text": "\n".join(text), "path": rec["path"], "rec": rec}

# ---------------------------------------------------------------- http


def make_handler(col: Collector):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _hdr(self, code=200, ctype="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

        def do_OPTIONS(self):
            self._hdr(204)

        def _json(self, obj, code=200):
            self._hdr(code)
            self.wfile.write(json.dumps(obj).encode())

        def _refresh(self):
            res = col.refresh()
            self._json({**res, "snap": col.snapshot if res["ok"] else None}, 200 if res["ok"] else 503)

        def do_GET(self):
            if self.path.startswith("/api/refresh"):   # GET too, so `curl` can drive it
                self._refresh()
            elif self.path in ("/", "/index.html"):
                self._hdr(200, "text/html; charset=utf-8")
                self.wfile.write(WIDGET_HTML.read_bytes())
            elif self.path.startswith("/api/now"):
                self._hdr()
                self.wfile.write(json.dumps(col.snapshot).encode())
            elif self.path.startswith("/api/series"):
                self._hdr()
                self.wfile.write(json.dumps({"at": (col.snapshot.get("telemetry") or {}).get("at"),
                                             "sparks": col.snapshot.get("sparks") or {}}).encode())
            elif self.path.startswith("/api/thumb"):
                from urllib.parse import parse_qs, urlparse
                h = col.hand_row((parse_qs(urlparse(self.path).query).get("id") or [""])[0])
                data = thumb_bytes(h["target"]) if h and not h["target"].startswith("http") else None
                if data:
                    self._hdr(200, "image/jpeg")
                    self.wfile.write(data)
                else:
                    self._hdr(404)
            elif self.path.startswith("/api/stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                seen = -1
                try:
                    while True:
                        with col.cond:
                            if col.version == seen:
                                col.cond.wait(timeout=15)
                            v, snap = col.version, col.snapshot
                        if v != seen:
                            self.wfile.write(b"data: " + json.dumps(snap).encode() + b"\n\n")
                            seen = v
                        else:
                            self.wfile.write(b": hb\n\n")
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    return
            else:
                self._hdr(404)

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                body = {}
            if self.path == "/api/refresh":
                self._refresh()
            elif self.path == "/api/ack" and body.get("id"):
                # who acked decides whether it counts as an owner precision label: the widget is his hand;
                # `pulse.py ack` is an agent's (17 agent bulk-acks once read as his judgement, 2026-10-11)
                actor = str(body.get("actor") or "unknown")[:16]
                col.ack(str(body["id"]), "noise" if body.get("noise") else "actionable", actor)
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            elif self.path == "/api/seen" and body.get("id"):
                col.seen(str(body["id"]))
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            elif self.path == "/api/probe":
                col.probe = {"rimworld_running": bool(body.get("rimworld_running")), "at": time.time(),
                             "host": str(body.get("host", ""))[:40]}
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            elif self.path == "/api/metric" and body.get("m"):
                append("metrics.jsonl", {k: v for k, v in body.items() if isinstance(v, (str, int, float))})
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            else:
                self._hdr(404)
    return H


def daemon() -> None:
    col = Collector()
    col.tick()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), make_handler(col))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"pulse: serving http://127.0.0.1:{PORT}/  state {pc.STATE_DIR}", flush=True)
    while True:
        col.wake.wait(INTERVAL)   # the ONE collection loop: every INTERVAL, or at once after an ack/seen
        col.wake.clear()
        try:
            col.tick()
        except Exception as e:  # never die on one bad tick; the snapshot just ages and goes STALE
            print(f"pulse: tick failed: {type(e).__name__}: {e}", flush=True)


def metric_files() -> list[Path]:
    """The live metrics log and every rotated one, oldest first."""
    live = _p("metrics.jsonl")
    return sorted(live.parent.glob("metrics.2*.jsonl")) + [live]


def iter_metrics(files: list[Path]):
    """Every record of every file, streamed (never a byte tail: the old 8 MB tail reported 'no acks yet'
    over 17 acks and n=60246 notices for 25 incidents, MEASURED 2026-10-22)."""
    for f in files:
        try:
            fh = open(f, "rb")
        except OSError:
            continue
        with fh:
            for raw in fh:
                try:
                    yield json.loads(raw)
                except ValueError:
                    continue


def metrics_summary(recs) -> dict:
    """Pure: the numbers `pulse.py metrics` prints. Repeated red_noticed for one incident count once (the
    first); acks split by actor - only the widget's (his hand) are precision labels."""
    first_notice: dict[str, float] = {}
    qage, owner_acks, other_acks, t0, t1, n = [], [], [], None, None, 0
    for r in recs:
        n += 1
        ts = r.get("ts")
        if isinstance(ts, (int, float)):
            t0 = ts if t0 is None else min(t0, ts)
            t1 = ts if t1 is None else max(t1, ts)
        m = r.get("m")
        if m == "red_noticed" and r.get("id") not in first_notice:
            first_notice[r.get("id")] = r.get("latency_s")
        elif m == "alarm_close" and r.get("kind") == "amber":
            qage.append(r.get("age_s"))
        elif m == "alarm_ack":
            (owner_acks if r.get("actor") == "widget" else other_acks).append(r)
    return {"records": n, "from": t0, "to": t1, "notice": [v for v in first_notice.values() if v is not None],
            "qage": [q for q in qage if q is not None], "owner_acks": owner_acks, "other_acks": other_acks}


def metrics() -> None:
    def med(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else None
    files = metric_files()
    m = metrics_summary(iter_metrics(files))
    span = (f"{datetime.fromtimestamp(m['from']):%Y-%m-%d %H:%M} .. {datetime.fromtimestamp(m['to']):%Y-%m-%d %H:%M}"
            if m["from"] else "empty")
    qage, oa = m["qage"], m["owner_acks"]
    good = sum(1 for r in oa if r.get("label") == "actionable")
    print(f"coverage           : {m['records']} records, {span}, {len(files)} file(s)")
    print(f"time-to-next-prompt: n={len(m['notice'])} incidents  median={med(m['notice'])} s  "
          f"(first owner prompt after a red opened - NOT proof he saw it)")
    print(f"question age       : n={len(qage)} median={med(qage)} s  p90={sorted(qage)[int(len(qage)*.9)] if qage else None} s")
    print(f"alert precision    : {good}/{len(oa)} widget acks labelled actionable" if oa
          else "alert precision    : UNMEASURED - no ack from the widget (his hand) yet")
    if m["other_acks"]:
        print(f"                     ({len(m['other_acks'])} acks by an agent/CLI or unknown actor - not counted)")
    print(f"log                : {_p('metrics.jsonl')}")


def compact_metrics(path: Path) -> tuple[int, int]:
    """Rewrite a metrics log keeping only the FIRST red_noticed per incident (the 5 s tick once re-noticed
    every red still on screen: 1.82M of 1.83M lines). Lines the daemon appends meanwhile are carried over
    before the atomic replace. Returns (lines before, lines after)."""
    seen, before, after = set(), 0, 0
    tmp = path.with_suffix(".compact.tmp")
    with open(path, "rb") as src, open(tmp, "wb") as out:
        for raw in src:
            before += 1
            try:
                r = json.loads(raw)
            except ValueError:
                continue
            if r.get("m") == "red_noticed":
                if r.get("id") in seen:
                    continue
                seen.add(r.get("id"))
            out.write(raw if raw.endswith(b"\n") else raw + b"\n")
            after += 1
        end = src.tell()
    with open(path, "rb") as src, open(tmp, "ab") as out:   # appended while we read
        src.seek(end)
        tail = src.read()
        out.write(tail)
        after += tail.count(b"\n")
    os.replace(tmp, path)
    return before, after


def health(restart: bool) -> int:
    import subprocess
    import urllib.request
    try:
        snap = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/now", timeout=10).read())
        age = time.time() - snap.get("collected_at", 0)
    except Exception as e:
        age, snap = None, {"error": str(e)}
    ok = age is not None and age < 60
    print(f"pulse health: {'ok' if ok else 'BAD'} age={None if age is None else round(age)}s")
    if not ok and restart:
        append("metrics.jsonl", {"m": "spine_restart", "age_s": age})
        subprocess.run(["systemctl", "--user", "restart", "rm-pulse.service"], timeout=20)
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("daemon")
    sub.add_parser("collect")
    s = sub.add_parser("since")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--back", action="store_true")
    g.add_argument("--scheduled", action="store_true")
    g.add_argument("--since")
    s.add_argument("--quiet", action="store_true")
    a = sub.add_parser("ack")
    a.add_argument("incident")
    a.add_argument("--noise", action="store_true")
    hd = sub.add_parser("hand")
    hd.add_argument("target")
    hd.add_argument("--title")
    hd.add_argument("--seat")
    hd.add_argument("--read-by", help="who looked at it first: seat:<SEAT> or judge:<model> (required)")
    hd.add_argument("--caught", help="one line: what was fixed or dropped before he sees it; 'nothing' is valid (required)")
    wd = sub.add_parser("withdraw")
    wd.add_argument("id")
    wd.add_argument("--by", help="the hand id or title that supersedes it")
    rp = sub.add_parser("report")
    rp.add_argument("task", help="e.g. build:FlowWorks, selftests:nightly, digest:scheduled")
    rp.add_argument("status", choices=("failed", "ok"))
    rp.add_argument("--cause")
    rp.add_argument("--seat")
    rp.add_argument("--blocks", action="store_true", help="required work cannot go on without this job")
    rp.add_argument("--lost", action="store_true", help="the job's output is gone")
    rp.add_argument("--link", help="a log or output path")
    sn = sub.add_parser("seen")
    sn.add_argument("id")
    mt = sub.add_parser("metrics")
    mt.add_argument("--compact", action="store_true", help="drop repeated red_noticed lines from the live log first")
    h = sub.add_parser("health")
    h.add_argument("--restart", action="store_true")
    sub.add_parser("refresh")
    up = sub.add_parser("update")
    up.add_argument("--restart", action="store_true", help="restart rm-pulse.service when new code arrived")
    args = ap.parse_args(argv)
    if args.cmd == "daemon":
        daemon()
    elif args.cmd == "collect":   # read-only: only the daemon writes state.json / pulse_now.json
        col, now = Collector(), time.time()
        snap = pc.collect_snapshot(col.gather(now), col.state, now)[0]
        for r in snap["rows"]:
            print(f"{r['kind']:<10} {r['who']:<9} {r['text']}")
        print(" | ".join(p["text"] for p in snap["strip"]))
    elif args.cmd == "since":
        import failreport
        mode = "back" if args.back else "scheduled" if args.scheduled else "manual"
        since = parse_since(args.since) if args.since else None
        try:
            d = make_digest(mode, since)
        except Exception as e:   # a scheduled digest never written is output lost: the one red a job earns at once
            failreport.report(f"digest:{mode}", False, cause=f"{type(e).__name__}: {e}", lost=mode == "scheduled")
            raise
        failreport.report(f"digest:{mode}", True)
        if not args.quiet:
            print(d["text"])
        print(f"saved: {d['path']}")
    elif args.cmd == "ack":
        import urllib.request
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/ack", method="POST",
                                     data=json.dumps({"id": args.incident, "noise": args.noise, "actor": "cli"}).encode(),
                                     headers={"Content-Type": "application/json"})
        print(urllib.request.urlopen(req, timeout=5).read().decode())
    elif args.cmd == "hand":
        try:
            r = hand(args.target, args.title, args.seat, args.read_by, args.caught)
        except ValueError as e:
            print(f"hand REFUSED: {e}", file=sys.stderr)
            return 2
        print(f"handed: {r['id']}  {r['title']}  ->  {r['win'] or r['target']}  (rev {r['rev'] or '-'}, read by {r['read_by']})")
    elif args.cmd == "withdraw":
        try:
            r = withdraw(args.id, args.by)
        except ValueError as e:
            print(f"withdraw REFUSED: {e}", file=sys.stderr)
            return 2
        print(f"withdrawn: {r['id']}" + (f" (superseded by {r['superseded_by']})" if r["superseded_by"] else ""))
    elif args.cmd == "report":
        import failreport
        ok = failreport.report(args.task, args.status == "ok", cause=args.cause, seat=args.seat, blocks=args.blocks,
                               lost=args.lost, link=args.link)
        print(f"reported {args.task} {args.status}" if ok else "report NOT written (see stderr)")
        return 0 if ok else 1
    elif args.cmd == "seen":
        import urllib.request
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/seen", method="POST",
                                     data=json.dumps({"id": args.id}).encode(),
                                     headers={"Content-Type": "application/json"})
        print(urllib.request.urlopen(req, timeout=5).read().decode())
    elif args.cmd == "metrics":
        if args.compact:
            b, a = compact_metrics(_p("metrics.jsonl"))
            print(f"compacted metrics.jsonl: {b} -> {a} lines")
        metrics()
    elif args.cmd == "health":
        return health(args.restart)
    elif args.cmd == "refresh":
        import urllib.error
        import urllib.request
        try:
            body = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/refresh", timeout=REFRESH_TIMEOUT + 10).read()
        except urllib.error.HTTPError as e:
            body = e.read()
        res = json.loads(body)
        print(f"refresh: {'ok' if res['ok'] else 'FAILED'} in {res['ms']} ms"
              + (f", collected_at {time.strftime('%H:%M:%S', time.localtime(res['collected_at']))}" if res["ok"] else "")
              + (f" - {res['error']}" if res.get("error") else "")
              + (f"; sources not ok: {res['sources_down']}" if res.get("sources_down") else ""))
        return 0 if res["ok"] else 1
    elif args.cmd == "update":
        u = update_code()
        print(f"pulse update: {ROOT} {u['old']} -> {u['new']}" + ("" if u["changed"] else " (already current)"))
        if u["changed"] and args.restart:
            import subprocess
            subprocess.run(["systemctl", "--user", "restart", "rm-pulse.service"], timeout=30)
            print("pulse update: rm-pulse.service restarted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
