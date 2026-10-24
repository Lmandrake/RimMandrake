"""Pulse spine core: read live sources, classify into red / amber / calm rows.

AWAY_DASHBOARD_BUILD_1. Design: Transient/away_dashboard_design_2026-10-08.md (owner
rulings 2026-10-08 20:01 + 20:39 by card). Everything here is a pure function of
(raw sources, persisted state, now) so selftest_pulse.py can drive it with fixtures.

Signals, all MEASURED 2026-10-08:
  ~/.claude/sessions/<pid>.json   status busy|idle|waiting|shell, waitingFor. A pending
                                  AskUserQuestion card reads status=waiting,
                                  waitingFor="input needed". Liveness = /proc/<pid> exists
                                  AND its stat field 22 == the file's procStart (PID reuse).
  <projects>/<sid>/subagents/agent-*.jsonl
                                  a subagent is RUNNING while its last record is not an
                                  assistant end_turn and the file moved in the last 15 min.
  ~/.local/state/rm-memwatch/events.jsonl
                                  kind oom_kill|oom_group_kill; toast:true = memwatch
                                  already toasted it (seats), harness kills are toast:false.
  infrastructure/state/ledger/events/*.jsonl
                                  the key is `id`, NOT `item`.

Amber (owner ruling): explicit requests (status waiting) always; finished-and-idle only
while NO subagent / background agent of that window is still running (typed: "(2) but
not if there are subagents or background agents still working").
Red: OOM kill (any cgroup, harness included), a window whose process died while its
session file stayed behind (a clean exit removes the file -> neutral).
"""
from __future__ import annotations

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import glob
import json
import os
import time
from pathlib import Path

HOME = Path.home()
SESSIONS_DIR = HOME / ".claude" / "sessions"
PROJECTS_DIR = HOME / ".claude" / "projects"
HISTORY = HOME / ".claude" / "history.jsonl"
MEMWATCH_EVENTS = HOME / ".local" / "state" / "rm-memwatch" / "events.jsonl"
STATE_DIR = Path(os.environ.get("RM_PULSE_STATE", HOME / ".local" / "state" / "rm-dashboard"))
CLONES = [Path("/home/mandrake/rm/bench"), Path("/home/mandrake/rm/foundry")]
ARTPIPE_DIR = Path(os.environ.get("ARTPIPE_STATE_DIR", rm_str("artpipe")))
MIRROR_WIN = "D:\\Luke\\dev\\RimMandrake"
GITHUB_COMMIT = "https://github.com/Lmandrake/RimMandrake/commit/"

SUBAGENT_LIVE_SECS = 15 * 60     # the Agent watchdog kills at 600 s of silence; 15 min is past it
IDLE_AMBER_SECS = 60             # Claude Code's own idle_prompt fires after ~60 s
STUCK_SECS = 20 * 60             # busy with no transcript growth: dim amber, never flashes
RED_WINDOW_SECS = 24 * 3600      # how far back an un-acked red stays on screen
OOM_CLUSTER_GAP = 30 * 60        # harness kills come in bursts; one incident per burst
DONE_WINDOW_SECS = 12 * 3600
SEAT_WAIT_FADE_SECS = 2 * 3600   # "finished, waiting for you" fades to a plain chip after this
SEATS = ("BENCH", "FOUNDRY")     # the only windows that can ask for the owner
OLD_ASK_SECS = 3 * 86400        # older asks fold into one "older (N)" line (nothing dropped)
RULE_WINDOW_SECS = 14 * 86400   # a ruling older than this (since needs became owner) leaves the widget, not rimflow
SHEETS_DIRS = [c / "Transient" for c in CLONES]   # every sheet root under Transient (one level of subfolders too)
# Telemetry (TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED): the Windows-side telemetryd writes its alert
# verdicts + sparklines here; pulse only displays them (design 08 §5.6: pulse is the attention surface).
TELEMETRY_STATE = Path(os.environ.get("RM_TELEMETRY_ALERTS", "/mnt/e/telemetry/state/alerts.json"))
TELEMETRY_STALE_SECS = 300

# ---------------------------------------------------------------- readers (impure)


def proc_start(pid: int) -> str | None:
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # comm may contain spaces; fields after the closing paren are stable
    rest = raw[raw.rfind(")") + 2:].split()
    return rest[19] if len(rest) > 19 else None   # field 22 overall


def read_sessions(sessions_dir: Path = SESSIONS_DIR) -> list[dict]:
    """A missing sessions dir RAISES (the collector then shows the source down and the seat chips
    'unknown'): an empty list would read as 'no windows open' (RIMPULSE_SOURCES_FIX_SILENCE_READS_HEALTHY).
    One unparseable file is skipped - a session file is rewritten in place and can be read mid-write."""
    if not sessions_dir.is_dir():
        raise FileNotFoundError(f"no sessions dir {sessions_dir}")
    out = []
    for f in sessions_dir.glob("*.json"):
        try:
            s = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if s.get("kind") != "interactive":
            continue
        pid = s.get("pid")
        s["alive"] = bool(pid) and proc_start(int(pid)) == str(s.get("procStart"))
        s["_file"] = str(f)
        out.append(s)
    return out


def _last_record(path: Path, tail_bytes: int = 65536) -> dict | None:
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - tail_bytes))
            chunk = fh.read().decode("utf-8", "replace")
    except OSError:
        return None
    for line in reversed(chunk.splitlines()):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") in ("assistant", "user"):
            return d
    return None


def subagent_running(last: dict | None, mtime: float, now: float) -> bool:
    if now - mtime > SUBAGENT_LIVE_SECS:
        return False
    if last is None:
        return True
    m = last.get("message") or {}
    return not (last.get("type") == "assistant" and m.get("stop_reason") == "end_turn")


def card_text(questions: list) -> tuple[str, str]:
    """(first question, the whole card as plain text: every question with its option labels). Pure."""
    first, parts = None, []
    for q in questions or []:
        if not isinstance(q, dict):
            continue
        qt = " ".join(str(q.get("question") or q.get("header") or "").split())
        first = first or qt
        opts = [str(o.get("label") or "") for o in (q.get("options") or []) if isinstance(o, dict) and o.get("label")]
        parts.append(qt + (" — options: " + " / ".join(opts) if opts else ""))
    return first or "", "\n".join(parts)


def pending_card(records: list[dict]) -> dict | None:
    """The question card that is up RIGHT NOW in a transcript tail, or None. Pure.

    A card is pending only while its AskUserQuestion tool_use has no tool_result after it: an answer (or a
    hook refusing the card, which the owner never saw) closes it. Reading only the LAST record made an
    answered card's text linger whenever the session file still said `waiting` (owner, 2026-10-23: the amber
    'asks' text was truncated and stale)."""
    card, answered = None, set()
    for r in records:
        m = r.get("message") or {}
        cs = m.get("content") if isinstance(m.get("content"), list) else []
        for c in cs:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use" and c.get("name") == "AskUserQuestion":
                first, full = card_text((c.get("input") or {}).get("questions") or [])
                card = {"id": c.get("id"), "question": first, "full": full,
                        "at": iso_to_epoch(r.get("timestamp") or "")}
            elif c.get("type") == "tool_result" and c.get("tool_use_id"):
                answered.add(c["tool_use_id"])
    if card and card["id"] not in answered and card["question"]:
        return card
    return None


def _tail_records(path: Path, tail_bytes: int = 512 << 10) -> list[dict]:
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - tail_bytes))
            chunk = fh.read().decode("utf-8", "replace")
    except OSError:
        return []
    out = []
    for line in chunk.splitlines():
        if '"AskUserQuestion"' not in line and '"tool_result"' not in line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def session_extras(sid: str, now: float, projects_dir: Path = PROJECTS_DIR) -> dict:
    """active subagent count, transcript mtime, and the question card that is up (if any)."""
    ex = {"subagents": 0, "transcript_mtime": None, "question": None, "question_full": None, "question_at": None}
    for t in projects_dir.glob(f"*/{sid}.jsonl"):
        try:
            ex["transcript_mtime"] = t.stat().st_mtime
        except OSError:
            pass
        card = pending_card(_tail_records(t))
        if card:
            ex.update(question=card["question"], question_full=card["full"], question_at=card["at"] or None)
        for a in (t.parent / sid / "subagents").glob("agent-*.jsonl"):
            try:
                mt = a.stat().st_mtime
            except OSError:
                continue
            if now - mt > SUBAGENT_LIVE_SECS:
                continue
            if subagent_running(_last_record(a, 16384), mt, now):
                ex["subagents"] += 1
        break
    return ex


def read_jsonl_tail(path: Path, tail_bytes: int = 1 << 20, strict: bool = False,
                    allow_missing: bool = True) -> list[dict]:
    """The last `tail_bytes` of a JSONL file as records; torn lines are skipped.

    strict=True is for a collector SOURCE (RIMPULSE_SOURCES_FIX_SILENCE_READS_HEALTHY): an unreadable file
    raises instead of reading as "nothing happened", a missing one raises unless `allow_missing` (a log
    nobody has written yet is a valid empty), and a non-empty tail with no parseable line raises."""
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - tail_bytes))
            chunk = fh.read().decode("utf-8", "replace")
    except FileNotFoundError:
        if strict and not allow_missing:
            raise
        return []
    except OSError:
        if strict:
            raise
        return []
    out, bad = [], 0
    for line in chunk.splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            bad += bool(line.strip())
    if strict and bad and not out:
        raise ValueError(f"{path.name}: {bad} line(s), none parseable")
    return out


def _model():
    """rimflow's own fold (src/RimMandrake/rimflow/model.py): the single source of item state."""
    import sys
    root = str(Path(__file__).resolve().parents[2])
    if root not in sys.path:
        sys.path.insert(0, root)
    from rimflow import model
    return model


def read_ledger(clones: list[Path] = CLONES) -> list[dict]:
    """Union of every clone's shards (each seat's own shard is freshest in its own clone), deduped and
    ordered by rimflow's reader invariant (identity = content, never file position). WHOLE files: a
    tail would drop the `file` events and rimflow's replay would lose the items (FOUNDRY.jsonl was
    1.9 MB on 2026-10-10 and the old tail was 4 MB). A torn line is skipped here, not raised - a
    window mid-append must not blank the widget."""
    model, out = _model(), []
    for f in ledger_files(clones):
        out.extend(read_jsonl_tail(f, 1 << 40, strict=True, allow_missing=False))
    return model.canonical_order(out)


def ledger_files(clones: list[Path] = CLONES) -> list[Path]:
    """rimflow's own file list per clone: the frozen history `events.jsonl` + every seat shard. Without
    the history file the replay never sees pre-cutover `file` events and those items do not exist."""
    model = _model()
    return [Path(f) for c in clones for f in model.ledger_files(str(c / "infrastructure/state/ledger/events.jsonl"))]


def owner_rulings(ledger: list[dict]) -> dict:
    """iid -> the event that made an OPEN item's `needs` "owner", for every item rimflow itself says
    is waiting on him right now. Derived from rimflow's replay, never from a second reading of the
    verbs: `implemented`, `verify`, `file --needs`, `needs`, close/drop/... all move `needs` or the
    state, and pulse once only knew about `needs` (SCRAPNEST stayed "to rule" after `implemented`
    made it needs=bridge, 2026-10-10). A repeated `needs --to owner` re-asks and moves the time."""
    became: dict[str, dict] = {}
    answered: dict[str, dict] = {}

    def obs(ev, world, ok):
        iid = ev.get("id")
        it = world.items.get(iid) if iid else None
        if it is None:
            return
        # a BLOCKED item is parked on something else (another item, or his own "later"): he cannot act on it
        # now, so it is not an ask; unblocking re-asks it fresh (owner 2026-10-23: answered rows lingered)
        if it.open and it.needs == "owner" and not it.blocked:
            if iid not in became or (ok and ev.get("event") == "needs"):
                became[iid] = ev            # (re-)asked: any earlier answer was to an earlier question
                answered.pop(iid, None)
            elif ok and (ev.get("ownerSaid") or ev.get("byCard")):
                # his words or his card AFTER the ask, on this item: the question is answered even though
                # nobody has moved `needs` yet (owner 2026-10-23: rows for answered cards persisted)
                answered[iid] = ev
        else:
            became.pop(iid, None)
            answered.pop(iid, None)
    world = _model().replay(list(ledger), observe=obs)
    out = {}
    for iid, ev in became.items():
        it = world.items[iid]
        an = answered.get(iid)
        klass, why = ask_class(it, ev)
        out[iid] = {"ev": ev, "t": iso_to_epoch(ev.get("ts", "")), "seat": (ev.get("seat") or "").upper(),
                    "reason": ev.get("reason") or it.title, "state": it.state, "class": klass, "class_why": why,
                    "answered": ({"t": iso_to_epoch(an.get("ts", "")), "event": an.get("event"),
                                  "seat": (an.get("seat") or "").upper(),
                                  "by": "card" if an.get("byCard") else "his words",
                                  "text": an.get("byCard") or an.get("ownerSaid")} if an else None)}
    return out


# What the owner is being asked for, from the item itself (owner 2026-10-23: a look masqueraded as a ruling).
RULE_KINDS = {"decision", "ruling", "question", "card", "decide", "design"}
LOOK_KINDS = {"art", "review", "check", "verify", "trial"}
_LOOK_RE = r"(\(?\blook\b[,:)]|\bL4\b|\blooks? at\b|\bglances?\b|\bin[- ]game\b|\bin[- ]situ\b|\bwalk\b|\bsheet\b|\bscreenshot|\bkeeper save|\bjoint\b)"
# a FACT only he has (an address, a host, a key); verbs like "address the issue" or "provide feedback" are not
_PROVIDE_RE = (r"(\bname/address\b|\b(ip|e-?mail|network|home) address\b|\baddress (of|for)\b|\bhostname\b|"
               r"\bpassword\b|\bcredentials?\b|\bwhich (pc|machine|account)\b|"
               r"\bneeds (its|his|the) (name|address|number|path|url|key)\b)")


# a LIVE walkthrough (game running, a joint session) is not an artifact he opens: never in "to look at"
# (owner 2026-10-23). "in-game" alone stays a look when the thing is a saved picture, so only walk wording counts.
_WALK_RE = r"(\bwalk-?through\b|\bwalk\b|\bin[- ]game\b|\bjoint\b|\bkeeper save|\bbridge run\b)"


def ask_class(it, ev: dict) -> tuple[str, str]:
    """ask_class_raw, but a look that is a live interactive walkthrough is class 'walk' (not listed anywhere)."""
    klass, why = ask_class_raw(it, ev)
    if klass == "look":
        crit = " ".join(str(c.get("text") or c.get("desc") or "") for c in getattr(it, "criteria", [])
                        if c.get("id") in getattr(it, "outstanding", ()) and c.get("level") == "L4")
        import re
        text = f"{it.title or ''} {ev.get('reason') or ev.get('why') or ''} {crit}"
        if re.search(_WALK_RE, text, re.I):
            return "walk", f"live walkthrough, not an artifact ({why})"
    return klass, why


def _is_artifact_link(lk) -> bool:
    """True when a look row's link is something to open and review: not missing, not an item/spec .md, not a commit."""
    v = str((lk or {}).get("value") or "")
    return bool(v) and not v.lower().endswith(".md") and "/commit/" not in v


def ask_class_raw(it, ev: dict) -> tuple[str, str]:
    """('rule' | 'look' | 'provide', why) for an open item waiting on the owner. Pure over the item fold.

    Order: an explicit word on the needs event wins ('look:', 'provide:', 'rule:', or '(LOOK, not a ruling)');
    an item whose only owed criteria are L4 is a look; then the item's kind; then its words. Anything else is
    a ruling - the only class that asks him for a verdict."""
    import re
    reason = str(ev.get("reason") or ev.get("why") or "")
    text = f"{it.title or ''} {reason}"
    head = reason.strip().lower()
    for k in ("look", "provide", "rule"):
        if head.startswith(k + ":"):
            return k, f"needs event says '{k}:'"
    if re.search(r"\bLOOK, not a ruling\b", reason, re.I):
        return "look", "needs event says it is a look"
    owed = it.owed_levels() if hasattr(it, "owed_levels") else []
    if owed and set(owed) == {"L4"}:
        return "look", "only an L4 (owner look) criterion is owed"
    kind = (it.kind or "").lower()
    if kind in RULE_KINDS:
        return "rule", f"kind {kind}"
    if re.search(_PROVIDE_RE, text, re.I):
        return "provide", "asks for a fact"
    if kind in LOOK_KINDS:
        return "look", f"kind {kind}"
    if re.search(_LOOK_RE, text, re.I):
        return "look", "asks him to look"
    return "rule", "default: waiting on his verdict"


def read_artpipe(d: Path = ARTPIPE_DIR, prev: dict | None = None, now: float = 0) -> dict:
    def n(sub: str) -> int:
        try:
            return sum(1 for e in os.scandir(d / sub) if e.name.endswith(".json"))
        except OSError:
            return -1
    out = {"pending": n("pending"), "active": n("active"), "failed": n("failed")}
    if out["pending"] < 0:   # unreadable state dir: a source failure, never an idle chip
        raise FileNotFoundError(f"artpipe state unreadable: {d / 'pending'}")
    if prev and now - prev.get("done_at", 0) < 300:   # done/ holds 10k entries on drvfs
        out["done"], out["done_at"] = prev.get("done"), prev.get("done_at")
    else:
        out["done"], out["done_at"] = n("done"), now
    out["ok"] = out["pending"] >= 0
    return out


def read_bridge(clone: Path = CLONES[0]) -> str | None:
    """The BRIDGE holder line. An unreadable file RAISES (source down); a file with no holder line is None."""
    for line in (clone / "infrastructure/state/BRIDGE").read_text().splitlines():
        if line and not line.startswith("#"):
            return line.strip()
    return None


def read_hands(state_dir: Path | None = None) -> list[dict]:
    """Things agents deliberately handed the owner (`pulse.py hand`). Newest hand record per id wins; a later
    `withdraw` record (no target) marks it withdrawn or superseded. `missing` = a path target that no longer
    exists (a delivery problem, RIMPULSE_LOOKS_BUILD_UNREAD_NEVER_LISTED)."""
    out: dict[str, dict] = {}
    for h in read_jsonl_tail((state_dir or STATE_DIR) / "hands.jsonl", 2 << 20, strict=True):
        hid = h.get("id")
        if not hid:
            continue
        if h.get("target"):
            out[hid] = h                    # a (re-)hand replaces the record, an earlier withdrawal included
        elif h.get("withdrawn") and hid in out:
            out[hid] = {**out[hid], "withdrawn": h["withdrawn"], "superseded_by": h.get("superseded_by")}
    for h in out.values():
        h["missing"] = not str(h["target"]).startswith("http") and not os.path.exists(h["target"])
    return list(out.values())


def http_ok(url: str, timeout: float = 0.8) -> bool:
    """Probe a sheet server on its small `/status` endpoint (same ?t= token) and READ the reply.
    Opening the page itself and dropping it unread made every probe a BrokenPipe traceback in the
    server's serve.log (MEASURED 2026-10-22: logs of 17-27 MB, which pulse then read whole)."""
    import urllib.request
    from urllib.parse import urlsplit, urlunsplit
    p = urlsplit(url)
    try:
        with urllib.request.urlopen(urlunsplit((p.scheme, p.netloc, "/status", p.query, "")),
                                    timeout=timeout) as r:
            r.read()
            return r.status == 200
    except Exception:
        return False


_PROBE_VERIFIED: dict[str, float] = {}
PROBE_REVERIFY_SECS = 30 * 60


def sheet_alive(url: str, now: float | None = None, full=http_ok) -> bool:
    """Is this sheet server still up, WITHOUT writing its log every 45 s? A full `/status?t=` request (which
    proves the token, i.e. the same server) at most once per PROBE_REVERIFY_SECS; between those a bare TCP
    connect, which http.server never logs. Every /status probe was a log line: the logs were nothing but
    probes and the sheet's time - then its log mtime - moved every 45 s (MEASURED 2026-10-22)."""
    import socket
    from urllib.parse import urlsplit
    now = time.time() if now is None else now
    if now - _PROBE_VERIFIED.get(url, -1e18) < PROBE_REVERIFY_SECS:
        p = urlsplit(url)
        try:
            with socket.create_connection((p.hostname, p.port or 80), timeout=0.8):
                return True
        except OSError:
            _PROBE_VERIFIED.pop(url, None)
            return False
    ok = full(url)
    if ok:
        _PROBE_VERIFIED[url] = now
    else:
        _PROBE_VERIFIED.pop(url, None)
    return ok


def wsl_from_win(p: str) -> str:
    """\\\\wsl.localhost\\Ubuntu\\home\\x -> /home/x ; D:\\a\\b -> /mnt/d/a/b ; anything else unchanged."""
    import re
    p = p.strip()
    m = re.match(r"^\\\\wsl(?:\.localhost|\$)\\[^\\]+(\\.*)$", p)
    if m:
        return m.group(1).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):\\(.*)$", p)
    if m:
        return f"/mnt/{m.group(1).lower()}/" + m.group(2).replace("\\", "/")
    return p


def parse_sheet_log(text: str) -> dict:
    import re
    urls = re.findall(r"https?://[^\s]+", text)
    m = re.search(r"(\d+) rows\s*·\s*(\d+) decided", text)
    sh = re.search(r"^\s*sheet\s+(\S.*?)\s*$", text, re.M)
    return {"urls": urls, "never_reviewed": "NEVER reviewed" in text,
            "rows": int(m.group(1)) if m else None, "sheet": wsl_from_win(sh.group(1)) if sh else None}


_SHEET_LOG_CACHE: dict[str, tuple] = {}


def scan_sheet_log(f: Path) -> dict:
    """parse_sheet_log over a serve.log, streamed and incremental: only bytes appended since the last
    scan are read, line by line. Reading every log whole each 45 s held ~250 MB and OOM-killed the
    daemon at its 256 MB MemoryMax (MEASURED 2026-10-22, ×5 in a night)."""
    st = f.stat()
    c = _SHEET_LOG_CACHE.get(str(f))
    if not c or c[0] != st.st_ino or st.st_size < c[1]:
        c = (st.st_ino, 0, {"urls": [], "never_reviewed": False, "rows": None, "sheet": None})
    ino, off, info = c[0], c[1], dict(c[2], urls=list(c[2]["urls"]))
    if st.st_size > off:
        with open(f, "rb") as fh:
            fh.seek(off)
            for raw in fh:
                if not raw.endswith(b"\n"):
                    break                      # a line still being written: read it next time
                off += len(raw)
                if b"://" not in raw and b"rows" not in raw and b"NEVER" not in raw and b"sheet" not in raw:
                    continue
                part = parse_sheet_log(raw.decode("utf-8", "replace"))
                info["urls"] = [u for u in info["urls"] if u not in part["urls"]] + part["urls"]
                info["never_reviewed"] = info["never_reviewed"] or part["never_reviewed"]
                if info["rows"] is None:
                    info["rows"] = part["rows"]
                if part["sheet"] and not part["sheet"].startswith("GET") and info.get("sheet") is None:
                    info["sheet"] = part["sheet"]
    _SHEET_LOG_CACHE[str(f)] = (ino, off, info)
    return info


def sheet_html(log: Path, info: dict) -> Path | None:
    """The sheet's html: named on the serve.log's `sheet` line, else the html beside the log. Its mtime is the
    sheet's own time - NEVER the log's mtime: every request, pulse's probe included, appends to the log, so the
    sheet looked brand new and re-opened every 45 s (RIMPULSE_SHEETS_FIX_OWN_PROBE_REOPENS_THEM). No html: the
    row has no age (0), but opening it still sticks."""
    stem = log.name[: -len(".serve.log")]
    for c in ([info.get("sheet")] if info.get("sheet") else []) + [str(log.parent / stem),
                                                                     str(log.parent / (stem + ".html"))]:
        if c.endswith(".html") and Path(c).is_file():
            return Path(c)
    return None


_PREREVIEW_CACHE: dict[str, tuple] = {}


def sheet_prereviewed(html: Path | None) -> tuple[bool, str]:
    """(ok, why) from prereview.py's own verify() - Nothing reaches the owner unread (owner 2026-10-22). Cached
    per (html mtime, record mtime): verify reads the whole html, and the sheets source runs every 45 s."""
    if html is None:
        return False, "no sheet html found beside its serve.log"
    rp = html.with_name(html.stem + ".prereview.json")
    try:
        key = (html.stat().st_mtime_ns, rp.stat().st_mtime_ns if rp.exists() else 0)
    except OSError as e:
        return False, f"unreadable: {e}"
    c = _PREREVIEW_CACHE.get(str(html))
    if c and c[0] == key:
        return c[1]
    import sys
    art = str(Path(__file__).resolve().parents[1] / "art")
    if art not in sys.path:
        sys.path.insert(0, art)
    import prereview
    ok, msg = prereview.verify(html)
    res = (ok, msg.split(" Look at every row yourself")[0][:200])   # the HOW tail is for agents, not the widget
    _PREREVIEW_CACHE[str(html)] = (key, res)
    return res


def read_sheets(dirs: list[Path] | None = None, probe=sheet_alive, review=sheet_prereviewed) -> list[dict]:
    """Every review-sheet server that answers: the LAST url in its serve.log that is alive
    (SHEETS_INDEX/TONIGHT docs carry stale ports - never read those). `mtime` is the sheet's revision;
    `prereviewed`/`prereview` say whether a valid pre-review record covers it (unread sheets are held back)."""
    import re
    from concurrent.futures import ThreadPoolExecutor
    logs: dict[str, Path] = {}
    for d in (dirs if dirs is not None else SHEETS_DIRS):
        for f in glob.glob(str(d / "*.serve.log")) + glob.glob(str(d / "*" / "*.serve.log")):
            f = Path(f)
            if f.name not in logs or f.stat().st_mtime > logs[f.name].stat().st_mtime:
                logs[f.name] = f

    def one(f: Path):
        try:
            info = scan_sheet_log(f)
        except OSError:
            return None
        html = sheet_html(f, info)
        try:
            mt = html.stat().st_mtime if html else 0.0
        except OSError:   # rebuilt (replaced) between the two calls: no age this round, never a source crash
            mt = 0.0
        live = next((u for u in reversed(info["urls"]) if probe(u)), None)
        if not live:
            return None
        name = re.sub(r"_sheet_.*$", "", f.name.replace(".serve.log", ""))
        try:
            ok, why = review(html)
        except Exception as e:   # a broken checker holds the sheet back and says so; it never waves it through
            ok, why = False, f"pre-review check failed: {type(e).__name__}: {e}"[:200]
        return {"name": name, "url": live, "unreviewed": info["never_reviewed"], "rows": info["rows"], "mtime": mt,
                "prereviewed": ok, "prereview": why}
    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, logs.values()) if r]


def read_services(names=("rm-pulse.service",)) -> dict:
    """{unit: {"active": bool, "since": epoch of the current main process start}} - the recovery evidence
    for a service OOM (systemd 259: `--timestamp=unix` prints `@<epoch>`)."""
    import subprocess
    out = {}
    for n in names:
        r = subprocess.run(["systemctl", "--user", "show", n, "-p", "ActiveState", "-p", "ExecMainStartTimestamp",
                            "--timestamp=unix"], capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            raise RuntimeError(f"systemctl show {n}: rc {r.returncode}")
        kv = dict(ln.split("=", 1) for ln in r.stdout.splitlines() if "=" in ln)
        ts = kv.get("ExecMainStartTimestamp", "").lstrip("@")
        out[n] = {"active": kv.get("ActiveState") == "active", "since": float(ts) if ts.isdigit() else 0.0}
    return out


def owner_prompts(since: float, history: Path = HISTORY) -> list[dict]:
    return [h for h in read_jsonl_tail(history, 2 << 20) if (h.get("timestamp") or 0) / 1000 >= since]

# ---------------------------------------------------------------- helpers (pure)


def seat_name(s: dict) -> str:
    n = (s.get("name") or "").strip()
    return n[6:] if n.upper().startswith("AGENT ") else (n or f"pid {s.get('pid')}")


def seat_key(s: dict) -> str | None:
    """BENCH / FOUNDRY for a real seat window, else None. A seat is a user-named `AGENT <SEAT>`
    interactive window; the phone's remote-control child (entrypoint sdk-cli, derived name
    like `bench-61`) and other projects' windows (HESTIA, EMERGENCY) are never seats."""
    if s.get("entrypoint") == "sdk-cli":
        return None
    n = (s.get("name") or "").strip().upper()
    if not n.startswith("AGENT "):
        return None
    first = n[6:].split()[0] if n[6:].split() else ""
    return first if first in SEATS else None


def chip_label(s: dict) -> str:
    if s.get("entrypoint") == "sdk-cli":
        return "phone"
    n = seat_name(s).lower()
    return "emerg" if n.startswith("emergency") else n.split()[0] if n.split() else n


def nice_id(iid: str) -> str:
    import re
    return re.sub(r"_\d+$", "", str(iid or "")).lower().replace("_", " ")


def iso_to_epoch(ts: str) -> float:
    from datetime import datetime
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError):
        return 0.0


def win_path(rel: str) -> str:
    rel = rel.strip()
    if rel.startswith("/mnt/") and len(rel) > 6:
        return rel[5].upper() + ":\\" + rel[7:].replace("/", "\\")
    if rel.startswith("/"):
        return "\\\\wsl.localhost\\Ubuntu" + rel.replace("/", "\\")
    # Transient/ is untracked since 2026-10-18 (only pins reach the D:\ mirror): an unpinned file lives only
    # in the seat clone that wrote it, so link that clone's copy when the mirror has none.
    if rel.startswith("Transient/") and not os.path.exists("/mnt/d/Luke/dev/RimMandrake/" + rel):
        for c in CLONES:
            if (c / rel).exists():
                return "\\\\wsl.localhost\\Ubuntu" + str(c / rel).replace("/", "\\")
    return MIRROR_WIN + "\\" + rel.replace("/", "\\")


def link_for(e: dict) -> dict | None:
    ev = e.get("evidence")
    if isinstance(ev, str) and ev and " " not in ev.strip():
        return {"type": "path", "value": win_path(ev), "label": Path(ev).name[:28]}
    if e.get("sha"):
        sha = str(e["sha"])
        return {"type": "url", "value": GITHUB_COMMIT + sha, "label": sha[:9]}
    return None


def item_link(iid: str, clones: list[Path] | None = None) -> dict | None:
    """A ruling with no evidence field still opens its item file (needs events carry none)."""
    for c in (clones if clones is not None else CLONES):
        f = c / "infrastructure/state/items" / f"{iid}.md"
        if f.exists():
            return {"type": "path", "value": win_path(str(f)), "label": "item"}
    return None


def short(s: str, n: int = 72) -> str:
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"

# ---------------------------------------------------------------- classification (pure)


def boot_time() -> float:
    """Kernel boot (WSL VM start) epoch from /proc/stat btime; 0 when unreadable."""
    try:
        for ln in Path("/proc/stat").read_text().splitlines():
            if ln.startswith("btime "):
                return float(ln.split()[1])
    except (OSError, ValueError):
        pass
    return 0.0


def classify_sessions(sessions: list[dict], extras: dict, seen: dict, items: dict,
                      acks: dict, now: float, boot: float = 0.0) -> tuple[list[dict], dict, list[dict]]:
    """rows, new `seen` map, metric events. `seen` is {sid: {name, last_alive, file}}.

    A dead window is red only when it died on its own, inside the red window (24 h). Windows last
    seen alive BEFORE the current boot died with the machine (WSL restart / reboot leaves every
    session file behind): one `warn` line names them, never one red each. A dead file older than the
    red window is forgotten (MEASURED 2026-10-22: 17 reds from 2026-10-11 were still on screen)."""
    rows, events = [], []
    new_seen = dict(seen)
    present = set()
    restarted: list[tuple[str, float]] = []
    for s in sessions:
        sid = s.get("sessionId") or str(s.get("pid"))
        present.add(sid)
        who = seat_name(s)
        ex = extras.get(sid, {})
        sub = ex.get("subagents", 0)
        upd = (s.get("statusUpdatedAt") or s.get("updatedAt") or 0) / 1000
        if not s.get("alive"):
            if sid in seen:   # we watched it live; process gone, file left behind
                last = seen[sid].get("last_alive", upd)
                if now - last > RED_WINDOW_SECS:
                    new_seen.pop(sid, None)     # old residue: stop tracking it
                elif boot and last < boot:
                    restarted.append((who, last))
                else:
                    inc = f"lost:{sid}"
                    r = _red(inc, who, f"{who} window lost — process gone, session file left",
                             last, acks, src="sessions",
                             link={"type": "path", "value": win_path(s.get('_file', '')), "label": "session"})
                    r["pill"] = _red_pill(f"{who} window died (process gone)", 1, last)
                    rows.append(r)
            continue
        new_seen[sid] = {"name": who, "last_alive": now, "file": s.get("_file")}
        item = items.get(who.upper())
        doing = f" · {item}" if item else ""
        status = s.get("status")
        key = f"win:{sid}"
        seat = seat_key(s)
        win = {"seat": seat, "label": chip_label(s), "upd": upd, "sub": sub, "who": who,
               "started": (s.get("startedAt") or 0) / 1000}
        did = (not s.get("startedAt")) or (upd - s["startedAt"] / 1000 > 5)   # acted since launch
        lead = f"{who} "

        def add(r, state):
            r["seat"], r["win"] = seat, {**win, "state": state}
            r["label"] = r["text"][len(lead):] if r["text"].startswith(lead) else r["text"]
            rows.append(r)
        if status == "waiting" and seat:
            q = ex.get("question") or s.get("waitingFor") or "waiting"
            label = "asks" if ex.get("question") else "waiting"
            r = _amber(key, who, f"{who} {label}: {short(q, 90)}", upd, acks, explicit=True, sub=sub)
            # the full card, for the widget's expand: the row text stays one line (owner 2026-10-23: truncated)
            r.update(question=ex.get("question"), full=ex.get("question_full") or q,
                     asked_at=ex.get("question_at"), src_detail="transcript card" if ex.get("question")
                     else f"session file: waitingFor={s.get('waitingFor')!r}")
            add(r, "wait")
        elif (status == "idle" and sub == 0 and seat and did and now - upd >= IDLE_AMBER_SECS
              and now - upd < SEAT_WAIT_FADE_SECS):
            add(_amber(key, who, f"{who} finished — idle, waiting for you{doing}", upd, acks,
                       explicit=False, sub=0), "idle")
        elif status == "waiting":      # a non-seat window asking: presence only, never a top row
            add(_row(key, "idle", who, f"{who} waiting", upd), "idle")
        elif status == "idle" and sub > 0:
            add(_row(key, "run", who, f"{who} · {sub} agent{'s' * (sub > 1)} working{doing}", upd), "run")
        elif status == "idle":
            add(_row(key, "idle", who, f"{who} just finished{doing}", upd), "idle")
        else:
            tm = ex.get("transcript_mtime") or upd
            if now - max(tm, upd) >= STUCK_SECS:
                add(_row(key, "stuck", who, f"{who} busy · no observed progress{doing}", max(tm, upd)), "stuck")
            else:
                extra = f" · {sub} agent{'s' * (sub > 1)}" if sub else ""
                add(_row(key, "run", who, f"{who} working{doing}{extra}", upd), "run")
    if restarted:
        names = sorted({w for w, _ in restarted})
        at = time.strftime("%m-%d %H:%M", time.localtime(boot))
        inc = f"restart:{int(boot)}"
        rows.append(_row(inc, "warn", "WSL", f"WSL restarted {at} · {len(restarted)} window"
                         f"{'s' * (len(restarted) > 1)} ended with it: {', '.join(names)} · reopen them "
                         f"(claude --resume)", max(t for _, t in restarted), src="sessions", incident=inc,
                         acked=inc in acks, count=len(restarted), pill=f"◆ restart {at[6:]}"))
    for sid, info in seen.items():
        if sid not in present:      # session file removed: a clean exit, neutral
            new_seen.pop(sid, None)
            events.append({"m": "session_ended_clean", "sid": sid, "who": info.get("name")})
    return rows, new_seen, events


def _row(key, kind, who, text, since, link=None, src="sessions", **kw) -> dict:
    r = {"key": key, "kind": kind, "who": who, "text": text, "since": since, "link": link, "src": src}
    r.update(kw)
    if "incident" in r:
        r.setdefault("toast_key", r["incident"])
    return r


def _amber(key, who, text, since, acks, explicit, sub, src="sessions") -> dict:
    inc = f"{key}@{int(since)}"
    acked = inc in acks
    return _row(key, "amber" if explicit else "amber_soft", who, text, since, src=src,
                incident=inc, acked=acked, subagents=sub, toast_key=inc)


def _red(inc, who, text, since, acks, src, link=None, count=1, toasted=False) -> dict:
    a = acks.get(inc)
    acked = a is not None and a.get("at", 0) >= since
    return _row(inc, "red", who, text, since, link=link, src=src, incident=inc, acked=acked,
                count=count, toasted_elsewhere=toasted)


def classify_oom(mem_events: list[dict], acks: dict, now: float) -> list[dict]:
    """One red line per cgroup (seat or harness) over the last 24 h. An ack covers every
    kill up to the ack time; any later kill re-raises it (re-alert on a NEW occurrence)."""
    by_cg: dict[str, list] = {}
    for e in mem_events:
        if e.get("kind") not in ("oom_kill", "oom_group_kill"):
            continue
        t = iso_to_epoch(e.get("ts", ""))
        if now - t > RED_WINDOW_SECS:
            continue
        # a seat kill and its tool child are one event; key on the top two cgroup levels
        top = "/".join((e.get("cgroup") or "?").split("/")[:2])
        by_cg.setdefault(top, []).append((t, e))
    rows = []
    for cg, ks in by_cg.items():
        ks.sort(key=lambda x: x[0])
        inc = f"oom:{cg}"
        ack_at = (acks.get(inc) or {}).get("at", 0)
        fresh = [(t, e) for t, e in ks if t > ack_at]
        last_t, last = ks[-1]
        seat = last.get("seat") or cg
        who = "HARNESS" if "harness" in cg else seat.replace(".slice", "").upper()
        gb = (last.get("snapshot") or {}).get("current_gb")
        n_all = sum(int(e.get("delta") or 1) for _, e in ks)
        n_new = sum(int(e.get("delta") or 1) for _, e in fresh)
        when = time.strftime("%H:%M", time.localtime(last_t))
        tail = f" · {n_new} new" if fresh and n_new != n_all else ""
        text = (f"OOM kill · {who.lower() if who == 'HARNESS' else who}"
                + (f" @{gb} GB" if gb is not None else "")
                + (f" · ×{n_all} today" if n_all > 1 else "") + tail)
        r = _red(inc, who, text, last_t, {}, src="memwatch", count=n_all,
                 toasted=any(e.get("toast") for _, e in (fresh or ks[-1:])),
                 link={"type": "path", "value": win_path(str(MEMWATCH_EVENTS)), "label": "events"})
        r["acked"] = not fresh
        r["toast_key"] = f"{inc}@{int(last_t)}"
        r["pill"] = _red_pill(f"{who} OOM" + (f" @{gb} GB" if gb is not None else ""), n_all, last_t)
        rows.append(r)
    return rows


# ---------------------------------------------------------------- kernel OOM (the precise source)
# memwatch only sees "rm-harness.slice: oom_kill +1". The kernel log names the exact scope and
# its cap, which is what separates the runner's PLANTED containment test from a real kill:
# selftest_run_selftests.py runs a 512 MiB bomb under a 128 MiB cap on every runner selftest
# (MEASURED 2026-10-08: 37 of today's 39 kernel OOM kills were that bomb).
PLANTED_CAP_KB = 131072


def read_kernel_oom(since_secs: int = RED_WINDOW_SECS) -> list[dict]:
    import subprocess
    r = subprocess.run(["journalctl", "-k", "--since", f"-{since_secs}s", "--no-pager", "-o", "short-unix",
                        "-g", "oom-kill:|memory: usage|Killed process"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode not in (0, 1):
        raise RuntimeError(f"journalctl rc {r.returncode}: {r.stderr.strip()[:120]}")
    return parse_kernel_oom(r.stdout.splitlines())


def parse_kernel_oom(lines: list[str]) -> list[dict]:
    import re
    out, limit = [], None
    for ln in lines:
        parts = ln.split(" ", 1)
        try:
            t = float(parts[0])
        except (ValueError, IndexError):
            continue
        m = re.search(r"memory: usage \d+kB, limit (\d+)kB", ln)
        if m:
            limit = int(m.group(1))
            continue
        m = re.search(r"oom-kill:.*?oom_memcg=([^,]+),task_memcg=([^,]+),task=([^,]+),pid=(\d+)", ln)
        if m:
            memcg = re.sub(r"^/user\.slice/user-\d+\.slice/user@\d+\.service", "", m.group(1))
            out.append({"t": t, "limit_kb": limit, "memcg": memcg, "task": m.group(3), "pid": int(m.group(4))})
            limit = None
            continue
        m = re.search(r"Killed process (\d+) .*?anon-rss:(\d+)kB", ln)
        if m and out and out[-1]["pid"] == int(m.group(1)):
            out[-1]["anon_kb"] = int(m.group(2))
    return out


SERVICE_NAMES = {"rm-pulse.service": "RimPulse daemon"}


def kill_class(k: dict) -> str:
    """planted | harness_test | service | seat. A systemd user service (app.slice/<x>.service, e.g.
    rm-pulse.service at its MemoryMax) is NOT a seat window (MEASURED 2026-10-22: five
    rm-pulse.service kills showed as "SEAT window")."""
    mc = k.get("memcg") or ""
    if "rm-harness" in mc:
        return "planted" if k.get("limit_kb") == PLANTED_CAP_KB else "harness_test"
    if mc.rstrip("/").rsplit("/", 1)[-1].endswith(".service"):
        return "service"
    return "seat"


def _cap(limit_kb) -> str:
    if not limit_kb:
        return "its cap"
    return f"{limit_kb / 1048576:.1f} GB cap" if limit_kb >= 1048576 else f"{limit_kb // 1024} MB cap"


def _cap_short(limit_kb) -> str:
    """'6 GB cap' / '256 MB cap' - the pill-sized form of _cap."""
    if not limit_kb:
        return "at cap"
    if limit_kb >= 1048576:
        gb = limit_kb / 1048576
        return f"{gb:.0f} GB cap" if abs(gb - round(gb)) < 0.05 else f"{gb:.1f} GB cap"
    return f"{limit_kb // 1024} MB cap"


def _victim(k: dict) -> str:
    """'killed python 4.0 GB' from the kernel's Killed-process line (MEASURED 2026-10-22: the BENCH tool
    kills were one ~4 GB python re-run five times, not page cache)."""
    if not k.get("task"):
        return ""
    a = k.get("anon_kb")
    return f"killed {k['task']}" + (f" {a / 1048576:.1f} GB" if a else "")


def _red_pill(what: str, n: int, t: float) -> str:
    """A collapsed-strip red pill: WHAT broke and WHY, count, time (owner 2026-10-22: '✖ BENCH 19:40' made
    him deduce). Never only a name and a time."""
    return f"✖ {what}" + (f" ×{n}" if n > 1 else "") + f" · {time.strftime('%H:%M', time.localtime(t))}"


def today_window(now: float) -> float:
    """'today' = since local midnight, but never less than 6 h (a 23:50 kill still shows at 00:10)."""
    lt = time.localtime(now)
    midnight = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, 0, 0, 0, 0, 0, -1))
    return min(midnight, now - 6 * 3600)


def classify_kernel_oom(kills: list[dict], acks: dict, now: float) -> list[dict]:
    import re
    groups: dict[str, list] = {}
    start = today_window(now)
    for k in kills:
        if k["t"] < start:
            continue
        c = kill_class(k)
        if c == "seat":
            m = re.search(r"claude-seat-([A-Za-z0-9_]+)-\d+\.scope", k["memcg"])
            who = m.group(1).upper() if m else "SEAT"
            groups.setdefault(f"seat:{who}", []).append(k)
        elif c == "service":
            groups.setdefault(f"svc:{k['memcg'].rstrip('/').rsplit('/', 1)[-1]}", []).append(k)
        else:
            groups.setdefault(c, []).append(k)
    rows = []
    for g, ks in groups.items():
        ks.sort(key=lambda k: k["t"])
        last = ks[-1]
        n = len(ks)
        cap = _cap(last.get("limit_kb"))
        victim = _victim(last)
        if g == "planted":
            rows.append(_row("oom:planted", "idle", "HARNESS",
                             f"memory pen proven · planted 128 MiB test killed as designed ×{n} today", last["t"],
                             src="kernel"))
            continue
        inc = f"oom:{g}"
        ack_at = (acks.get(inc) or {}).get("at", 0)
        fresh = [k for k in ks if k["t"] > ack_at]
        if g == "harness_test":
            text = f"a selftest hit {cap} and was killed (contained)" + (f" · ×{n} today" if n > 1 else "")
            r = _row(inc, "warn", "HARNESS", text, last["t"], src="kernel", incident=inc, count=n)
        elif g.startswith("svc:"):
            svc = g[4:]
            who = SERVICE_NAMES.get(svc, svc)
            text = (f"OOM kill · {who} ({svc}) at {cap}" + (f" · ×{n} today" if n > 1 else "")
                    + f" · see journalctl --user -u {svc}")
            r = _row(inc, "red", who.split()[0].upper(), text, last["t"], src="kernel", incident=inc, count=n,
                     pill=_red_pill(f"{who} OOM · {_cap_short(last.get('limit_kb'))}", n, last["t"]))
        else:
            who = g.split(":", 1)[1]
            tool = last["memcg"].endswith("claude-code-bash")
            where = "tool cgroup" if tool else "window"
            text = (f"OOM kill · {who} {where} at {cap}" + (f" · {victim}" if victim else "")
                    + (f" · ×{n} today" if n > 1 else ""))
            r = _row(inc, "red", who, text, last["t"], src="kernel", incident=inc, count=n, tool=tool,
                     toasted_elsewhere=True,   # memwatch toasts seat kills itself
                     pill=_red_pill(f"{who} {'tool' if tool else 'window'} OOM · {_cap_short(last.get('limit_kb'))}",
                                    n, last["t"]))
        r["acked"] = not fresh
        r["toast_key"] = f"{inc}@{int(last['t'])}"
        if not g.startswith("svc:"):   # memwatch never records a service kill
            r["link"] = {"type": "path", "value": win_path(str(MEMWATCH_EVENTS)), "label": "events"}
        rows.append(r)
    return rows


def current_items(ledger: list[dict], now: float) -> dict:
    """seat -> the item it most recently started/claimed and has not closed (12 h)."""
    cur: dict[str, tuple[str, float]] = {}
    for e in ledger:
        ev, seat, iid = e.get("event"), (e.get("seat") or "").upper(), e.get("id")
        t = iso_to_epoch(e.get("ts", ""))
        if ev in ("start", "claim") and iid:
            cur[seat] = (iid, t)
        elif ev in ("close", "implemented", "drop", "supersede", "reassign") and iid and seat in cur and cur[seat][0] == iid:
            cur.pop(seat)
    return {s: i for s, (i, t) in cur.items() if now - t < 12 * 3600}


ASK_KINDS = {"rule": "review", "look": "look", "provide": "provide"}   # ask class -> row kind


def classify_ledger(ledger: list[dict], since: float, now: float,
                    rulings: dict | None = None) -> tuple[list[dict], dict]:
    """Done rows in the window + "to rule" rows. `rulings` is `owner_rulings(ledger)` (the daemon caches
    it per ledger change); computed here when not passed."""
    titles = {e["id"]: e.get("title") for e in ledger if e.get("event") == "file" and e.get("id")}
    rows, counts = [], {"filed": 0, "closed": 0, "implemented": 0, "verifies": 0, "drops": 0}
    if rulings is None:
        rulings = owner_rulings(ledger)
    for e in ledger:
        t = iso_to_epoch(e.get("ts", ""))
        ev, iid = e.get("event"), e.get("id")
        if t < since:
            continue
        if ev == "file":
            counts["filed"] += 1
        elif ev == "drop":
            counts["drops"] += 1
        elif ev in ("close", "implemented") or (ev == "verify" and e.get("result") == "pass"):
            counts["closed" if ev == "close" else "implemented" if ev == "implemented" else "verifies"] += 1
            verb = {"close": "closed", "implemented": "implemented", "verify": f"verified {e.get('criterion') or ''}".strip()}[ev]
            what = short(e.get("reason") or titles.get(iid) or "", 60) if ev != "verify" else short(titles.get(iid) or "", 50)
            rows.append(_row(f"item:{iid}", "done", (e.get("seat") or "").upper(),
                             f"{iid} {verb}" + (f" — {what}" if what else ""), t, link=link_for(e), src="ledger"))
    for iid, ru in rulings.items():
        t, e = ru["t"], ru["ev"]
        if ru.get("class") == "walk":
            continue                      # a live walkthrough is a joint session, never a row to open
        if now - t < RULE_WINDOW_SECS:
            full = " ".join(str(ru.get("reason") or titles.get(iid) or "(no reason recorded on the needs event)").split())
            reason = short(full, 90)
            lk = link_for(e) or item_link(iid)
            an = ru.get("answered")
            # answered = his card/words landed after the ask; the agent owes the follow-through, he owes nothing
            kind = "answered" if an else ASK_KINDS.get(ru.get("class") or "rule", "review")
            r = _row(f"needs:{iid}", kind, (e.get("seat") or "").upper(),
                     f"{iid} — {reason}", t, link=lk, src="ledger")
            r.update({"seat": (e.get("seat") or "").upper(), "title": nice_id(iid), "reason": reason, "full": full,
                      "iid": iid, "ask": ru.get("class") or "rule", "ask_why": ru.get("class_why"),
                      "answered": an, "src_detail": f"rimflow: {iid} open, needs=owner since {e.get('event')}"})
            if kind == "look":
                if not _is_artifact_link(lk):
                    continue            # a look is a thing he OPENS (sheet, image, page); an item .md or a commit is not
                r.update({"ltype": "item look", "seen_id": None, "group": None, "thumb": False, "opened": False})
            rows.append(r)
    # one line per thing: a later event on the same key replaces the earlier line
    dedup: dict[str, dict] = {}
    for r in rows:
        dedup[r["key"]] = r
    return list(dedup.values()), counts


HAND_TYPES = {"png": "image", "jpg": "image", "jpeg": "image", "gif": "image", "webp": "image", "bmp": "image",
              "html": "page", "htm": "page", "rws": "save", "md": "doc", "txt": "doc", "json": "data"}


def hand_type(target: str) -> str:
    if target.startswith("http"):
        return "web"
    ext = target.rsplit(".", 1)[-1].lower() if "." in Path(target).name else ""
    return HAND_TYPES.get(ext, "folder" if not ext else "file")


def classify_looks(hands: list[dict], sheets: list[dict], seen_look: dict, now: float,
                   seen_rev: dict | None = None) -> list[dict]:
    """The "to look at" feed: deliberate hand-offs + live review sheets. Nothing ever drops off when
    clicked (owner 2026-10-10): opening only sets `opened`, which the widget draws dimmed. Similar items
    share a `group` and fold under one expandable line ("Biome sheets: 27"). A sheet rebuilt after it was
    opened, or a hand of a NEW revision of a target, reads as unopened again; re-handing the revision he
    already opened does not (RIMPULSE_LOOKS_BUILD_UNREAD_NEVER_LISTED).

    Nothing reaches the owner unread (owner 2026-10-22): a hand with no `read_by` (who looked first) and a
    sheet with no valid pre-review record are never listed - each is one `held` row (the widget folds them
    under "held back"). A withdrawn or superseded hand stays, dimmed, and is not counted; a hand whose path
    target vanished shows as a delivery problem."""
    rows, seen_rev = [], seen_rev or {}
    for h in hands:
        tgt = h["target"]
        seat = (h.get("seat") or "").upper() or None
        title = h.get("title") or Path(tgt).name
        if not h.get("read_by"):
            rows.append(_row("held:" + h["id"], "held", seat or "", title, h.get("ts") or 0, src="hands",
                             seat=seat, why="handed with no pre-read (pulse.py hand --read-by)"))
            continue
        link = ({"type": "url", "value": tgt, "label": "open"} if tgt.startswith("http")
                else {"type": "path", "value": h.get("win") or win_path(tgt), "label": "open"})
        ty = hand_type(tgt)
        opened = ((seen_look.get(h["id"]) or 0) >= (h.get("ts") or 0)
                  or bool(h.get("rev")) and seen_rev.get(h["id"]) == h.get("rev"))
        r = _row(h["id"], "look", seat or "", title, h.get("ts") or 0, link=link, src="hands")
        r.update({"seat": seat, "title": title, "ltype": ty, "seen_id": h["id"], "group": None, "opened": opened,
                  "thumb": ty == "image" and not tgt.startswith("http") and not h.get("missing"),
                  "read_by": h.get("read_by"), "caught": h.get("caught"), "rev": h.get("rev")})
        if h.get("withdrawn"):
            sup = h.get("superseded_by")
            r.update(ltype=f"superseded by {sup}" if sup else "withdrawn", withdrawn=True, was_opened=opened,
                     opened=True)   # drawn dimmed like an opened one; `was_opened` keeps the real history
        elif h.get("missing"):
            r.update(ltype="target missing - delivery problem", missing=True)
        rows.append(r)
    for x in sorted(sheets, key=lambda x: x["name"]):
        if not x.get("prereviewed", True):
            rows.append(_row("held:sheet:" + x["name"], "held", "", x["name"], x["mtime"], src="sheets",
                             why=x.get("prereview") or "no pre-review record",
                             link={"type": "url", "value": x["url"], "label": "open"}))
            continue
        r = _row("sheet:" + x["name"], "look", "", x["name"], x["mtime"],
                 link={"type": "url", "value": x["url"], "label": "open"}, src="sheets")
        r.update({"seat": None, "title": r["text"], "ltype": "never reviewed" if x["unreviewed"] else "sheet",
                  "seen_id": "sheet:" + x["name"], "group": "Biome sheets", "thumb": False,
                  "opened": (seen_look.get("sheet:" + x["name"]) or 0) >= x["mtime"],
                  "prereview": x.get("prereview")})
        rows.append(r)
    return rows


def look_pending(r: dict) -> bool:
    """A look row he still owes a glance: unopened, not withdrawn, and its target reachable."""
    return r["kind"] == "look" and not r.get("opened") and not r.get("missing")


def build_chips(rows: list[dict], now: float, sessions_ok: bool = True) -> list[dict]:
    """The bottom strip: one small chip per thing that is alive, active first, stale last.
    Seat chips carry the seat; rimworld and mem are plain; idle non-seat windows merge into ONE
    dim chip at the far right (never a top row).

    Both seats ALWAYS have a chip (RIMPULSE_SEATS_FIX_WAITING_LOOKS_BUSY): `wait` (a question card is
    up - it never reads as working), `run`, `stuck`, `idle`, `stale`, `missing` (no window open) or
    `unknown` (the sessions source failed, so absence proves nothing). The chip carries its running
    subagent count and, as its title, what each window is doing."""
    chips = []
    wins = [r for r in rows if r.get("win")]
    for seat in SEATS:
        ws = [r["win"] for r in wins if r["win"]["seat"] == seat]
        if not ws:
            chips.append({"label": seat.lower(), "seat": seat, "state": "missing" if sessions_ok else "unknown",
                          "n": 0, "agents": 0, "since": 0,
                          "title": f"no {seat} window open" if sessions_ok
                          else f"{seat}: unknown - the sessions source is not reporting"})
            continue
        latest = max(w["upd"] for w in ws)
        agents = sum(w["sub"] for w in ws)
        states = {w["state"] for w in ws}
        st = ("wait" if "wait" in states else "run" if "run" in states else "stuck" if "stuck" in states
              else "idle" if now - latest < SEAT_WAIT_FADE_SECS else "stale")
        doing = [r["text"] for r in wins if r["win"]["seat"] == seat]
        chips.append({"label": seat.lower(), "seat": seat, "state": st, "n": len(ws), "agents": agents,
                      "since": latest, "title": " | ".join(doing)})
    for r in rows:
        if r["key"] == "game":
            chips.append({"label": "rimworld", "plain": True, "state": r["kind"] if r["kind"] == "run" else "idle",
                          "since": r["since"], "title": r["text"]})
        elif r["key"] == "artpipe":
            chips.append({"label": "artpipe", "seat": "ART", "state": r["kind"] if r["kind"] == "run" else "idle",
                          "since": r["since"], "title": r["text"]})
    others, dim = {}, {}
    for r in wins:
        w = r["win"]
        if w["seat"]:
            continue
        (others if w["state"] in ("run", "stuck") else dim).setdefault(w["label"], []).append(w)
    for lab, ws in others.items():
        chips.append({"label": lab, "state": "run", "n": len(ws), "since": max(w["upd"] for w in ws)})
    rank = {"wait": 0, "run": 0, "stuck": 0, "red": 0, "idle": 1, "stale": 2, "missing": 2, "unknown": 2}
    chips.sort(key=lambda c: (rank.get(c["state"], 1), -(c.get("since") or 0)))
    # the dim idle-window chip is gone from his view: windows that are not seats are not his
    return chips


def classify_artpipe(a: dict, now: float, at: float) -> list[dict]:
    if not a or not a.get("ok"):
        return []
    kind = "run" if a.get("active", 0) > 0 or a.get("pending", 0) > 0 else "idle"
    txt = f"artpipe · {a['active']} active · {a['pending']} queued"
    # the lifetime done/failed totals are agent iteration, not his: the failed/ row below carries the detail
    rows = [_row("artpipe", kind, "ART", txt, at, src="artpipe")]
    if a.get("failed", 0) > 0:   # failed jobs are history (the daemon retries or a seat re-queues), never red
        rows.append(_row("fail:artpipe", "failed", "ART", f"artpipe · {a['failed']} job{'s' * (a['failed'] > 1)} in failed/"
                         " · not blocking", at, src="artpipe",
                         link={"type": "path", "value": win_path(str(ARTPIPE_DIR / "failed")), "label": "failed/"}))
    return rows


def read_telemetry(path: Path = TELEMETRY_STATE) -> dict | None:
    """None = telemetry not installed (its state dir is absent: no row). Installed but the alerts file is
    missing or unreadable RAISES - silence is not health. A stale payload is reported by classify_telemetry
    and by `source_freshness`."""
    if not path.parent.is_dir():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# Telemetry episodes (RIMPULSE_ALERTS_FIX_TELEMETRY_CRIES_WOLF, GPT rec 7). MEASURED 2026-10-22 over 14 days:
# `hostiles` re-opened 475 times and `modal_stuck` 344, warn median life 21 s - each re-open was a new incident
# (new `since`) and so a new row, toast and ack. Now an alert id has ONE episode until it has been quiet for
# TEL_EPISODE_GAP; inside it every re-open only counts. Declared detection targets: an alert is shown once it
# has been present continuously for TEL_PERSIST[level] seconds, or at once when its episode has re-opened
# TEL_FLAP_SHOW times (a flapping fault is still a fault, shown ONCE as "flapping ×N"). A shown alert that goes
# quiet stays, marked clearing, for TEL_CLEAR_SECS, so a short dip does not drop and re-raise it.
TEL_PERSIST = {"red": 30, "warn": 60}
TEL_EPISODE_GAP = 10 * 60
TEL_CLEAR_SECS = 2 * 60
TEL_FLAP_SHOW = 4


def telemetry_episodes(t: dict | None, prev: dict | None, now: float) -> tuple[dict | None, dict]:
    """Pure: telemetryd's payload + the episode table -> (payload whose `alerts` are only those to SHOW, each
    carrying its episode `since`/`flaps`/`clearing`, new table). Table: {id: {first, on_since, last_seen,
    flaps, shown, level, text}}; `on_since` None = quiet now. A stale or absent payload leaves the table alone."""
    eps = {k: dict(v) for k, v in (prev or {}).items()}
    if not t or now - (t.get("at") or 0) > TELEMETRY_STALE_SECS:
        return t, eps
    present = set()
    for al in t.get("alerts") or []:
        aid = al.get("id")
        if not aid:
            continue
        present.add(aid)
        start = min(al.get("since") or now, now)
        e = eps.get(aid)
        if e is None or now - e["last_seen"] > TEL_EPISODE_GAP:
            e = {"first": start, "on_since": start, "flaps": 1, "shown": False}
        elif e.get("on_since") is None:
            e.update(on_since=start, flaps=e["flaps"] + 1)   # re-opened inside the episode: count it, nothing new
        e.update(last_seen=now, level=al.get("level") or "warn", text=al.get("text") or aid)
        if not e["shown"] and (now - e["on_since"] >= TEL_PERSIST.get(e["level"], 60) or e["flaps"] >= TEL_FLAP_SHOW):
            e["shown"] = True
        eps[aid] = e
    for aid, e in list(eps.items()):
        if aid in present:
            continue
        if now - e["last_seen"] > TEL_EPISODE_GAP:
            eps.pop(aid)            # quiet long enough: the episode is over
        else:
            e["on_since"] = None
    show = []
    for aid, e in eps.items():
        if not e["shown"]:
            continue
        clearing = aid not in present
        if clearing and now - e["last_seen"] > TEL_CLEAR_SECS:
            continue
        show.append({"id": aid, "level": e["level"], "text": e["text"], "since": e["first"], "flaps": e["flaps"],
                     "clearing": clearing})
    return {**t, "alerts": show}, eps


# RIMPULSE_RED_FIX_MEANS_YOUR_VERB: BENCH's throwaway test colonies die as tests do and Windows RAM dips when
# agents run; both read as "your colony" / "your PC" but he has no verb. They alarm only in HIS play session.
TEST_SESSION_ALERTS = ("colony_dead", "colonist_hostile", "mem_low")


def owner_play_session(game_running: bool | None, bridge: str | None) -> bool:
    """His own play session = the game is running and no seat holds the bridge (a held bridge is a test
    session). No bridge line, no probe or no game: not provably his, so those alarms stay quiet."""
    tok = (bridge or "").split()
    return bool(game_running) and bool(tok) and tok[0] == "FREE"


def classify_telemetry(t: dict | None, acks: dict, now: float, owner_play: bool = True) -> list[dict]:
    """Rows for telemetryd's alerts. Pass the payload through `telemetry_episodes` first: then an alert's
    `since` is its episode start, so its incident (and toast, and ack) stays the same across re-opens."""
    if not t:
        return []
    link = {"label": "Grafana", "type": "url", "value": t.get("grafana") or "http://localhost:3000"}
    rows = []
    at = t.get("at") or 0
    if now - at > TELEMETRY_STALE_SECS:
        inc = f"tel:stale@{int(at)}"
        a = acks.get(inc)
        rows.append(_row(inc, "warn", "TELEMETRY", f"telemetry blind: Windows stack silent since "
                         f"{time.strftime('%H:%M', time.localtime(at))}", at, link=None, src="telemetry",
                         incident=inc, acked=a is not None, pill="◆ telemetry"))
        return rows
    for al in t.get("alerts") or []:
        if not owner_play and any(k in str(al.get("id")) for k in TEST_SESSION_ALERTS):
            continue
        since = al.get("since") or at
        inc = f"tel:{al['id']}@{int(since)}"
        n = al.get("flaps") or 1
        text = al["text"] + (f" · flapping ×{n}" if n > 1 else "") + (" · clearing" if al.get("clearing") else "")
        if al.get("level") == "red":
            r = _red(inc, "TELEMETRY", text, since, acks, "telemetry", link=link)
            r["pill"] = _red_pill(short(al["text"], 40), n, since)
            r["toast_title"] = "telemetry alarm"
            rows.append(r)
        else:
            a = acks.get(inc)
            rows.append(_row(inc, "warn", "TELEMETRY", text, since, link=link, src="telemetry", incident=inc,
                             acked=a is not None and a.get("at", 0) >= since, pill="◆ " + al["text"][:22]))
    if t.get("tier_armed"):
        rows.append(_row("tel:tier", "run", "TELEMETRY", "in-game test tier ARMED (1 s windows, flight recorder)",
                         at, link=link, src="telemetry"))
    return rows


# ---------------------------------------------------------------- job failures (RIMPULSE_FAILURES_BUILD_ONLY_THE_STUCK)
# Build, selftest, artpipe and digest jobs report each attempt to failures.jsonl (`pulse.py report`, or
# failreport.report() from Python). Normal agent iteration - a build that fails and then passes - is HISTORY,
# never an alarm (GPT rec 12). Red only when the owner-relevant consequence holds:
#   lost    the job's output is gone (a scheduled digest that was never written)   -> red at once
#   blocks  required work cannot go on without it                                  -> red once it has stayed
#           failed for FAIL_STUCK_SECS with no success since
# A failure that is neither is a calm `failed` row (folded, no pill, no toast); a success after failures is a
# `recovered` row. Record: {ts, task, status: failed|ok, cause?, seat?, blocks?, lost?, link?}.
FAILURES = STATE_DIR / "failures.jsonl"
FAIL_STUCK_SECS = 15 * 60
FAIL_HISTORY_SECS = 24 * 3600     # a recovered or non-blocking failure stays in the history this long
FAIL_STALE_SECS = 7 * 86400       # an unrecovered failure older than this is forgotten (the job is gone)


def read_failures(path: Path | None = None) -> list[dict]:
    return read_jsonl_tail(path or FAILURES, 4 << 20, strict=True)


def classify_failures(recs: list[dict], acks: dict, now: float) -> list[dict]:
    """Pure: one row per task from its attempt records (see the block comment above)."""
    by: dict[str, list] = {}
    for r in recs:
        if r.get("task") and r.get("status") in ("failed", "ok") and isinstance(r.get("ts"), (int, float)):
            by.setdefault(str(r["task"]), []).append(r)
    rows = []
    hm = lambda t: time.strftime("%H:%M", time.localtime(t))  # noqa: E731
    for task, rs in by.items():
        rs.sort(key=lambda r: r["ts"])
        last = rs[-1]
        streak = []
        for r in reversed(rs):              # the current run of failures (if the last attempt failed)
            if r["status"] != "failed":
                break
            streak.insert(0, r)
        who = (last.get("seat") or "JOB").upper()
        link = ({"type": "path", "value": win_path(last["link"]), "label": Path(last["link"]).name[:28]}
                if last.get("link") else None)
        if not streak:                       # last attempt passed: recovered, if it failed recently
            fails = [i for i, r in enumerate(rs) if r["status"] == "failed"]
            if not fails or now - rs[fails[-1]]["ts"] > FAIL_HISTORY_SECS:
                continue
            j = fails[-1]                    # the last failure, the run of failures it ends, the pass after it
            i = j
            while i > 0 and rs[i - 1]["status"] == "failed":
                i -= 1
            f, n, ok = rs[j], j - i + 1, rs[j + 1]
            rows.append(_row(f"fail:{task}", "recovered", (f.get("seat") or who).upper(),
                             f"{task} failed{f' ×{n}' if n > 1 else ''}" + (f" ({short(f['cause'], 60)})" if f.get("cause") else "")
                             + f" · recovered: passed {hm(ok['ts'])}", f["ts"], link=link, src="failures",
                             recovered=f"passed {hm(ok['ts'])}"))
            continue
        first, f = streak[0]["ts"], streak[-1]
        if now - f["ts"] > FAIL_STALE_SECS:
            continue
        n, cause = len(streak), (f" ({short(f['cause'], 60)})" if f.get("cause") else "")
        inc = f"fail:{task}@{int(first)}"
        base = f"{task} failed{f' ×{n}' if n > 1 else ''}{cause}"
        blocked_for = now - first
        if any(r.get("lost") for r in streak):
            r = _red(inc, who, f"{base} · output lost", first, acks, "failures", link=link, count=n)
            r.update(pill=_red_pill(f"{task} output lost", n, f["ts"]), toast_title="output lost")
        elif any(r.get("blocks") for r in streak) and blocked_for >= FAIL_STUCK_SECS:
            r = _red(inc, who, f"{base} · blocking work for {int(blocked_for // 60)} min, no success since", first,
                     acks, "failures", link=link, count=n)
            r.update(pill=_red_pill(f"{task} stuck", n, f["ts"]), toast_title="job stuck")
        else:
            if now - f["ts"] > FAIL_HISTORY_SECS:
                continue
            tail = " · blocking, retrying" if any(r.get("blocks") for r in streak) else " · not blocking"
            r = _row(f"fail:{task}", "failed", who, base + tail, f["ts"], link=link, src="failures")
        rows.append(r)
    return rows


PROBE_STALE_SECS = 120   # the widget posts a RimWorld probe every few seconds while it runs


def classify_game(probe: dict | None, bridge: str | None, now: float) -> list[dict]:
    """An old probe answers nothing: past PROBE_STALE_SECS the game reads 'unprobed', never 'UP'."""
    if probe is None and bridge is None:
        return []
    if probe and now - (probe.get("at") or 0) > PROBE_STALE_SECS:
        probe = None
    running = (probe or {}).get("rimworld_running")
    # BRIDGE reads "HELD    <SEAT>    since ..." or "FREE ..."; the holder is the seat, not the verb
    tok = (bridge or "").split()
    holder = (tok[1] if tok[0] == "HELD" and len(tok) > 1 else tok[0]) if tok else "?"
    state = "UP" if running else "down" if running is False else "unprobed"
    txt = f"RimWorld {state} · bridge " + ("free" if holder == "FREE" else "unknown" if holder == "?" else f"held by {holder}")
    return [_row("game", "run" if running else "idle", "GAME", txt, (probe or {}).get("at", now), src="probe")]


# ---------------------------------------------------------------- incidents (RIMPULSE_INCIDENTS_BUILD_RECOVERED_NOT_RED)
# An OOM is an EVENT; whether its subject is broken NOW is a separate question, answered only by evidence.
# A red with recovery evidence becomes a calm `recovered` row (history, not alarm); a new occurrence after
# that re-raises red. Ack never changes recovery. Evidence per kind:
#   service OOM     the unit is active and its main process started after the kill and has run RECOVER_SECS
#   seat tool OOM   the seat's window is alive, active after the kill, and RECOVER_SECS passed with no new kill
#   window OOM/lost a window of the same name started after the death is alive (it was replaced)
# Anything else (telemetry reds, non-seat windows with no replacement) says "recovery unknown". A job failure
# (fail:...) recovers only by its own next passing attempt, which classify_failures already turns into history.
RECOVER_SECS = 10 * 60
INCIDENT_KEEP_SECS = 48 * 3600


def recovery_evidence(r: dict, wins: list[dict], services: dict, now: float) -> tuple[str | None, str]:
    """(evidence text or None, pending note) for one red row. Pure."""
    inc, last = r.get("incident") or "", r.get("since") or 0
    if inc.startswith("fail:"):
        return None, ""          # a job failure recovers by its next passing attempt (classify_failures)
    hm = lambda t: time.strftime("%H:%M", time.localtime(t))  # noqa: E731
    if inc.startswith("oom:svc:"):
        sv = (services or {}).get(inc[len("oom:svc:"):])
        if sv is None:
            return None, "recovery unknown"
        if sv["active"] and sv["since"] > last and now - sv["since"] >= RECOVER_SECS:
            return f"running since {hm(sv['since'])}, no kill since", ""
        return None, "watching for recovery" if sv["active"] else "service not running"
    if inc.startswith("oom:seat:") or inc.startswith("lost:"):
        who = r.get("who") or ""
        mine = [w for w in wins if (w.get("seat") or w.get("who") or "").upper() == who.upper()]
        tool = bool(r.get("tool")) and inc.startswith("oom:seat:")
        if tool:
            act = [w for w in mine if w.get("upd", 0) > last]
            if act and now - last >= RECOVER_SECS:
                return f"{who} window alive, active {hm(max(w['upd'] for w in act))}, no kill since", ""
            return None, "watching for recovery" if mine else f"no live {who} window"
        new = [w for w in mine if w.get("started", 0) > last]
        if new:
            return f"replaced by a new {who} window at {hm(min(w['started'] for w in new))}", ""
        return None, "not replaced yet"
    return None, "recovery unknown"


def track_incidents(rows: list[dict], prev: dict, wins: list[dict], services: dict,
                    now: float) -> tuple[list[dict], dict, list[dict]]:
    """Apply recovery evidence to red rows and keep the incident history. Returns (rows, incidents, events).
    `incidents` is {incident: {who, text, first, last, count, status, recovered_at, evidence}}; an entry
    outlives its row (the 'today' window rolling, an expiry) for INCIDENT_KEEP_SECS so a digest can still
    say what happened. A row's occurrence is its `since` (last kill): a later one re-opens the incident."""
    inc_out, events, out = {k: dict(v) for k, v in (prev or {}).items()}, [], []
    for r in rows:
        if r["kind"] != "red" or not r.get("incident"):
            out.append(r)
            continue
        key, last = r["incident"], r.get("since") or 0
        h = inc_out.get(key) or {"first": last, "count": 0}
        if h.get("last") is not None and last > h["last"]:
            h["recovered_at"], h["evidence"] = None, None        # a new occurrence: open again
        h.update(who=r["who"], text=r["text"], last=last, count=max(r.get("count") or 1, h.get("count") or 0),
                 first=min(h.get("first") or last, last))
        ev, pending = recovery_evidence(r, wins, services, now)
        if not ev and h.get("recovered_at"):
            ev = h.get("evidence")   # this occurrence already recovered: a window closed later must not re-raise it
        if ev:
            if not h.get("recovered_at"):
                h["recovered_at"] = now
                events.append({"m": "incident_recovered", "id": key, "who": r["who"], "evidence": ev,
                               "age_s": round(now - last)})
            h.update(status="recovered", evidence=ev)
            r = {**r, "kind": "recovered", "text": f"{r['text']} · recovered: {ev}", "recovered": ev,
                 "pill": None, "toast_key": None}
        else:
            h.update(status="open", evidence=None, recovered_at=None)
            r = {**r, "text": f"{r['text']} · {pending}" if pending else r["text"], "pending": pending}
        inc_out[key] = h
        out.append(r)
    for k in [k for k, v in inc_out.items() if now - (v.get("last") or 0) > INCIDENT_KEEP_SECS]:
        inc_out.pop(k)
    return out, inc_out, events


KIND_ORDER = {"red": 0, "amber": 1, "amber_soft": 2, "warn": 2.5, "stuck": 3, "run": 4, "review": 5, "provide": 5.2, "look": 5.5, "idle": 6, "recovered": 6.4,
              "failed": 6.42, "answered": 6.45, "held": 6.46, "done": 7}


ANSWERED_SHOW_SECS = 24 * 3600     # "answered, agent to follow up" is agent debt: his view only after it ages a day
AGENT_KINDS = ("recovered", "failed", "held")     # §3 remove-list: agent iteration, kept for the digest only


def owner_view(rows: list[dict], now: float) -> list[dict]:
    """RIMPULSE_RED_FIX_MEANS_YOUR_VERB. Red means: he has a verb AND work waits on it - the monitor is down
    (the widget itself says so), a SEAT window died and was not replaced, or a card blocks a seat (that is
    the amber pinned at the top). Every other red is an agent or machine event that heals itself: it drops to
    `warn` and is flagged `agent` (the digest still tells it; the widget, strip, tally and phone do not).
    Also flagged `agent`: the §3 remove-list rows (recovered / failed / held, a young `answered`, the idle
    planted-OOM proof) and every `amber_soft` (seat finished, idle), which becomes a line in `health`.
    Pure; returns new rows."""
    out = []
    for r in rows:
        k = r["kind"]
        if k == "red":
            inc = r.get("incident") or ""
            seat_dead = ((inc.startswith("lost:") or inc.startswith("oom:seat:")) and (r.get("who") or "").upper() in SEATS)
            if not seat_dead and r.get("src") != "telemetry":   # telemetry reds are already gated by owner_play
                r = {**r, "kind": "warn", "agent": True, "was": "red", "pill": None}
        elif k in AGENT_KINDS or k == "amber_soft" or r.get("key") == "oom:planted":
            r = {**r, "agent": True}
        elif k == "answered":
            t = (r.get("answered") or {}).get("t") or r.get("since") or 0
            if now - t < ANSWERED_SHOW_SECS:
                r = {**r, "agent": True}
        elif k == "warn" and r.get("src") == "telemetry":
            r = {**r, "agent": True}      # telemetry warns are Grafana's; "blind" (stale payload) stays: silence is not health
            if str(r.get("key", "")).startswith("tel:stale"):
                r["agent"] = False
        out.append(r)
    return out


def health_lines(rows: list[dict], chips: list[dict], now: float) -> list[str]:
    """One sentence about the run, replacing the 'finished, idle, waiting for you' pills: a seat that
    stopped is a health fact (the belt), not a request."""
    lines = []
    for r in rows:
        if r["kind"] == "amber_soft" and r.get("seat") and not r.get("acked"):
            m = int((now - (r.get("since") or now)) // 60)
            lines.append(f"{r['who']} finished, idle {m} min — belt stopped" if m < 120 else f"{r['who']} finished, idle {m // 60} h — belt stopped")
    for c in chips:
        if c.get("seat") in SEATS and c["state"] == "missing":
            lines.append(f"{c['seat']} has no window open")
    return lines


def order_rows(rows: list[dict]) -> list[dict]:
    def k(r):
        acked = 1 if r.get("acked") else 0
        base = KIND_ORDER.get(r["kind"], 9)
        if r["kind"] in ("red", "amber", "amber_soft", "warn") and acked:
            base = 6.5               # acked alarms drop below the live roster, still visible
        return (base, -(r.get("since") or 0) if r["kind"] in ("done", "red", "review", "look", "provide", "answered", "failed", "held") else (r.get("since") or 0))
    return sorted(rows, key=k)


def build_strip(rows: list[dict]) -> list[dict]:
    """The collapsed strip's pills (they must survive the widget being collapsed): every unacked alarm
    says WHAT and WHY in its own text (N1, owner 2026-10-22), a seat's question keeps the seat and the
    question, then the two counts he returns for - to rule, to look at - and the done tally. Presence
    lives in `chips`."""
    pills = []
    rows = [r for r in rows if not r.get("agent")]
    for r in rows:
        if r.get("acked"):
            continue
        if r["kind"] == "red":
            pills.append({"kind": "red", "text": r.get("pill") or _red_pill(short(r["text"], 44), 1, r["since"]),
                          "title": r["text"], "since": r["since"]})
        elif r["kind"] == "amber":
            q = r.get("label") or r["text"]
            pills.append({"kind": "amber", "text": f"◐ {r['who']} {short(q, 40)}", "title": r["text"],
                          "since": r["since"], "seat": r.get("seat")})
        elif r["kind"] == "warn":
            pills.append({"kind": "warn", "text": r.get("pill") or "◆ " + short(r["text"], 40), "title": r["text"],
                          "since": r["since"]})
    rec = [r for r in rows if r["kind"] == "recovered" and r.get("src") != "failures"]   # a job that failed then
    if rec:                                                                            # passed is iteration: fold only
        pills.append({"kind": "recovered", "text": f"↺ {len(rec)} recovered", "title": "\n".join(r["text"] for r in rec)})
    rule = sum(1 for r in rows if r["kind"] == "review")
    if rule:
        pills.append({"kind": "rule", "text": f"◇ {rule} to rule"})
    give = sum(1 for r in rows if r["kind"] == "provide")
    if give:
        pills.append({"kind": "provide", "text": f"✎ {give} to provide"})
    look = sum(1 for r in rows if look_pending(r))
    if look:
        pills.append({"kind": "look", "text": f"▣ {look} to look at"})
    return pills                       # no done tally: finished work is told in the digest, not counted here


def source_freshness(status: dict, raw: dict, now: float) -> dict:
    """Mark a source whose READ succeeded but whose DATA is old as `stale` (a fresh read of a dead producer
    is not health): the telemetry payload's own `at`, the game probe's age. Pure; returns a new dict."""
    out = {k: dict(v) for k, v in (status or {}).items()}
    tel = raw.get("telemetry")
    if tel and out.get("telemetry", {}).get("ok") and now - (tel.get("at") or 0) > TELEMETRY_STALE_SECS:
        out["telemetry"]["stale"] = f"payload from {time.strftime('%H:%M', time.localtime(tel.get('at') or 0))}"
    pr = raw.get("probe")
    if "probe" in out:
        if not pr:
            out["probe"].update(ok=False, error="no game probe yet (widget not posting)")
        elif now - (pr.get("at") or 0) > PROBE_STALE_SECS:
            out["probe"]["stale"] = f"last probe {int((now - pr['at']) // 60)} min ago"
    return out


def collect_snapshot(raw: dict, state: dict, now: float) -> tuple[dict, dict, list[dict]]:
    """Pure: raw sources + persisted state -> (snapshot, new state, metric events)."""
    acks = state.get("acks", {})
    items = current_items(raw.get("ledger", []), now)
    srows, seen, events = classify_sessions(raw.get("sessions", []), raw.get("extras", {}),
                                            state.get("seen", {}), items, acks, now, raw.get("boot", 0.0))
    since = state.get("done_since") or (now - DONE_WINDOW_SECS)
    lrows, counts = classify_ledger(raw.get("ledger", []), since, now, raw.get("rulings"))
    oom = (classify_kernel_oom(raw["kernel_oom"], acks, now) if raw.get("kernel_oom") is not None
           else classify_oom(raw.get("memwatch", []), acks, now))   # memwatch only when the kernel log is unreadable
    looks = classify_looks(raw.get("hands", []), raw.get("sheets", []), state.get("seen_look", {}), now,
                           state.get("seen_rev", {}))
    tel, tel_eps = telemetry_episodes(raw.get("telemetry"), state.get("tel_episodes"), now)
    owner_play = owner_play_session((raw.get("probe") or {}).get("rimworld_running")
                                    or (raw.get("telemetry") or {}).get("game_running"), raw.get("bridge"))
    rows = (oom + srows + lrows + looks
            + classify_artpipe(raw.get("artpipe", {}), now, raw.get("at", {}).get("artpipe", now))
            + classify_game(raw.get("probe"), raw.get("bridge"), now)
            + classify_telemetry(tel, acks, now, owner_play)
            + classify_failures(raw.get("failures") or [], acks, now))
    wins = [r["win"] for r in srows if r.get("win")]
    rows, incidents, inc_events = track_incidents(rows, state.get("incidents", {}), wins, raw.get("services") or {}, now)
    events.extend(inc_events)
    rows = order_rows(owner_view(rows, now))
    # metrics: alarm transitions (question age, red open)
    open_prev = state.get("open", {})
    open_now = {r["incident"]: {"kind": r["kind"], "since": r["since"], "who": r["who"]}
                for r in rows if r.get("incident") and r["kind"] in ("red", "amber", "amber_soft", "warn")}
    for inc, o in open_now.items():
        if inc not in open_prev:
            events.append({"m": "alarm_open", "id": inc, **o})
    for inc, o in open_prev.items():
        if inc not in open_now:
            events.append({"m": "alarm_close", "id": inc, "kind": o["kind"], "who": o.get("who"),
                           "age_s": round(now - o["since"])})
    chips = build_chips(rows, now, (raw.get("source_status") or {}).get("sessions", {}).get("ok", True))
    new_state = dict(state)
    new_state.update({"seen": seen, "open": open_now, "incidents": incidents, "tel_episodes": tel_eps})
    snap = {
        "v": 2, "collected_at": now, "rows": rows, "strip": build_strip(rows), "chips": chips, "health": health_lines(rows, chips, now), "counts": counts,
        "done_since": since, "sources": source_freshness(raw.get("source_status", {}), raw, now),
        "sparks": None,          # sparklines are Grafana's, not his
        "telemetry": ({k: raw["telemetry"].get(k) for k in ("at", "grafana", "tier_armed", "game_running")}
                      if raw.get("telemetry") else None),
        "tally": {k: sum(1 for r in rows if r["kind"] == k and not r.get("acked") and not r.get("agent"))
                  for k in ("red", "amber", "amber_soft", "warn", "run", "done", "review", "provide", "look", "answered",
                            "recovered", "failed", "held")},
    }
    return snap, new_state, events
