#!/usr/bin/env python3
"""agents_timeline.py — the RimPulse "Who worked when" page (RIMPULSE_AGENTS_BUILD_DAY_TIMELINE).

Owner, 2026-10-27: "Impulse should also be modified to show which agents are currently active. Probably as a timeline
so I can see when agents existed for the past day."

    /agents        the page: who is working now, then a 24 h timeline, one lane per agent, local time, a now line
    /agents.json   the same data
    agents_timeline.py show    the page's data as text (debug)

Served by brief.page (loopback 8765 and the tailnet listener, like /streams). Computed on request from what is on
disk, cached 30 s; transcripts are parsed incrementally (only the bytes added since the last read).

Sources (each lane says when its source could not be read — a grey hatched gap with the reason, never an empty lane
that would read as "nobody worked"):
  windows      ~/.claude/sessions/*.json (the live window registry: name, current session, process alive) and every
               session transcript ~/.claude/projects/*/<session>.jsonl touched in the day. A transcript's custom
               title names its window: "AGENT BENCH ▶ …", "AGENT FOUNDRY", "HESTIA", "EMERGENCY", "ROLE <Role> <unit>".
               A session bar runs from its first to its last record (to now while its window is open on it); the
               solid parts are working stretches (records less than BUSY_GAP apart), the faint rest is "open, waiting".
  helpers      <session>/subagents/agent-*.jsonl (first..last record; still running = pulse_core.subagent_running ->
               ends at now) and agent-*.meta.json "description" (the label the window wrote when it started it).
  roles        the systemd user journal "Started rm-role-<role>-<n>.service" (dispatcher role_launch), joined to the
               role's transcript (its end). A start with no transcript and no live unit is a start MARKER, labelled
               "end not recorded". The Conductor is a role; with no run its lane says so (and whether it is switched
               off in dispatcher_schedule.json).
  SteveDesktop the testq records (testq/done, testq/running): started..finished, a running job ends at now.
  PC off       `journalctl --list-boots`: the time between two boots is hatched across every lane.
  labels       a seat window's label is the title of the item its seat claimed/started in that span (the ledger);
               HESTIA/EMERGENCY and untitled sessions use the last thing they were asked. Ids appear only in the
               hover/tap text.
"""
from __future__ import annotations

import datetime
import glob
import html
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pulse_core as pc  # noqa: E402

DAY = 86400.0
BUSY_GAP = 10 * 60            # records further apart than this are not one working stretch
PX_H = 40                     # chart px per hour at its narrowest (960 px: fills a desk, scrolls inside the chart on a phone)
ROW_H = 22
CACHE_S = 30
TESTQ_ROOT = Path(os.environ.get("RM_TESTQ_ROOT", "/mnt/d/ClaudeWork/rimmandrake/testq"))
SCHEDULE = Path(os.environ.get("RM_DISPATCH_SCHEDULE", str(HERE.parents[1] / "rimflow" / "dispatcher_schedule.json")))
WINDOWS = (("BENCH", "BENCH", "window"),
           ("FOUNDRY", "FOUNDRY", "window"),
           ("HESTIA", "HESTIA", "window"),
           ("EMERGENCY", "EMERGENCY", "window"))
STEWARD_PROMPT = "started by the SteveDesktop lane steward"
ROLE_WORDS = {"Proof": "a test launch of the role starter", "Conductor": "plans and briefs the day",
              "Arbiter": "judges finished work", "Auditor": "checks the books", "Operations": "keeps the machines running",
              "Producer": "re-plans when a step fails", "Innovator": "proposes new work"}
ITEM_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")

_LOCK = threading.Lock()
_SCAN: dict = {}             # path -> {"off", "st"}: incremental transcript parse state
_CACHE: dict = {}            # "page" -> (at, data)
_LEDGER: dict = {}           # path -> (size, mtime, titles, seat events)


# ---------------------------------------------------------------------------------------------- reading
def _ts(s) -> float | None:
    if not s:
        return None
    try:
        return pc.iso_to_epoch(str(s))
    except Exception:  # noqa: BLE001 - a malformed stamp is a skipped record, not a crash
        return None


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def _new_state() -> dict:
    return {"first": None, "last": None, "segs": [], "title": None, "prompts": [], "first_user": None,
            "last_rec": None}


def _feed(st: dict, d: dict) -> None:
    kind = d.get("type")
    if kind == "custom-title" and d.get("customTitle"):
        st["title"] = str(d["customTitle"])
        return
    if kind not in ("user", "assistant", "queue-operation", "system"):
        return
    t = _ts(d.get("timestamp"))
    if t is None:
        return
    st["first"] = t if st["first"] is None else min(st["first"], t)
    st["last"] = t if st["last"] is None else max(st["last"], t)
    segs = st["segs"]
    if segs and t - segs[-1][1] <= BUSY_GAP and t >= segs[-1][0] - BUSY_GAP:
        segs[-1][0], segs[-1][1] = min(segs[-1][0], t), max(segs[-1][1], t)
    else:
        segs.append([t, t])
    if kind == "queue-operation" and d.get("operation") == "enqueue" and d.get("content") \
            and not str(d["content"]).lstrip().startswith(("/", "<")):   # slash commands, task notifications
        st["prompts"].append((t, str(d["content"])[:300]))
        del st["prompts"][:-40]
    if kind == "user":
        txt = _text((d.get("message") or {}).get("content"))
        if st["first_user"] is None and txt:
            st["first_user"] = txt[:6000]
        if txt and not txt.startswith(("<", "/")) and not st["prompts"] and not d.get("isMeta"):
            st["prompts"].append((t, txt[:300]))
    if kind in ("user", "assistant"):
        m = d.get("message") or {}
        st["last_rec"] = {"type": kind, "message": {"stop_reason": m.get("stop_reason")}}


def scan(path: Path) -> dict:
    """The parsed summary of a transcript, reading only bytes appended since the last call."""
    key = str(path)
    try:
        size = path.stat().st_size
    except OSError:
        return _new_state()
    with _LOCK:
        ent = _SCAN.get(key)
        if ent is None or size < ent["off"]:
            ent = _SCAN[key] = {"off": 0, "st": _new_state()}
        if size > ent["off"]:
            with open(path, "rb") as fh:
                fh.seek(ent["off"])
                chunk = fh.read(size - ent["off"])
            end = chunk.rfind(b"\n") + 1
            for line in chunk[:end].splitlines():
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if isinstance(d, dict):
                    _feed(ent["st"], d)
            ent["off"] += end
        return ent["st"]


def read_registry(sessions_dir: Path) -> tuple[list[dict], str | None]:
    try:
        return pc.read_sessions(sessions_dir), None
    except Exception as ex:  # noqa: BLE001
        return [], f"the window list ({sessions_dir}) could not be read: {ex}"


def window_of(name: str | None) -> str | None:
    n = (name or "").strip().upper()
    if n.startswith("AGENT "):
        first = n[6:].split()[0] if n[6:].split() else ""
        return first if first in ("BENCH", "FOUNDRY") else None
    for k in ("HESTIA", "EMERGENCY"):
        if n.startswith(k):
            return k
    return None


def role_of(name: str | None) -> tuple[str, str] | None:
    m = re.match(r"ROLE\s+(\S+)\s+(rm-role-\S+)", (name or "").strip())
    return (m.group(1), m.group(2)) if m else None


def read_ledger_bits(ledger: list | None) -> tuple[dict, list]:
    """(item id -> title, [(seat, id, t, event)]) from a given event list, or from the clones' shards (cached)."""
    if ledger is not None:
        return _bits(ledger)
    titles, evs = {}, []
    try:
        files = pc.ledger_files()
    except Exception:  # noqa: BLE001
        files = []
    for f in files:
        try:
            stt = f.stat()
        except OSError:
            continue
        hit = _LEDGER.get(str(f))
        if not hit or hit[0] != stt.st_size or hit[1] != stt.st_mtime:
            rows = []
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if '"file"' in line or '"claim"' in line or '"start"' in line:
                            try:
                                rows.append(json.loads(line))
                            except ValueError:
                                pass
            except OSError:
                continue
            hit = _LEDGER[str(f)] = (stt.st_size, stt.st_mtime) + _bits(rows)
        titles.update(hit[2])
        evs.extend(hit[3])
    return titles, evs


def _bits(rows) -> tuple[dict, list]:
    titles, evs = {}, []
    for e in rows:
        if not isinstance(e, dict) or not e.get("id"):
            continue
        if e.get("event") == "file" and e.get("title"):
            titles[e["id"]] = str(e["title"])
        elif e.get("event") in ("claim", "start"):
            t = _ts(e.get("ts"))
            if t is not None:
                evs.append(((e.get("seat") or "").upper(), e["id"], t, e["event"]))
    return titles, evs


def short_title(t: str, n: int = 78) -> str:
    """The first sentence of an item title, cut at a word boundary."""
    t = re.sub(r"\s+", " ", t or "").strip()
    t = re.split(r"(?<=[a-z0-9)])\. |; | — ", t)[0].rstrip(".")
    if len(t) > n:
        t = t[:n].rsplit(" ", 1)[0] + "…"
    return t


def plain_prompt(p: str, n: int = 70) -> str:
    p = re.sub(r"<[^>]+>", " ", p or "")
    p = ITEM_RE.sub(lambda m: m.group(0).lower().replace("_", " "), p)   # an id in his own words reads as words
    p = re.sub(r"\s+", " ", p).strip()
    return p if len(p) <= n else p[:n].rsplit(" ", 1)[0] + "…"


def read_role_lines(lo: float) -> tuple[list | None, str | None]:
    try:
        r = subprocess.run(["journalctl", "--user", "--since", "@%d" % int(lo), "-o", "short-unix", "--no-pager"],
                           capture_output=True, text=True, timeout=20)
    except Exception as ex:  # noqa: BLE001
        return None, f"the systemd journal could not be read: {ex}"
    if r.returncode != 0:
        return None, f"the systemd journal could not be read: {(r.stderr or '').strip()[:120]}"
    return [ln for ln in r.stdout.splitlines() if "rm-role-" in ln], None


def read_units_active() -> set:
    try:
        r = subprocess.run(["systemctl", "--user", "list-units", "rm-role-*", "--state=active", "--no-legend", "--plain"],
                           capture_output=True, text=True, timeout=10)
        return {ln.split()[0].removesuffix(".service") for ln in r.stdout.splitlines() if ln.strip()}
    except Exception:  # noqa: BLE001
        return set()


def read_boots() -> list | None:
    try:
        r = subprocess.run(["journalctl", "--list-boots", "-o", "json", "--no-pager"], capture_output=True, text=True,
                           timeout=10)
        return json.loads(r.stdout) if r.returncode == 0 else None
    except Exception:  # noqa: BLE001
        return None


def roles_switch(path: Path = SCHEDULE) -> dict:
    try:
        return {r.get("name"): bool(r.get("enabled")) for r in json.loads(path.read_text()).get("roles") or []}
    except Exception:  # noqa: BLE001
        return {}


# ---------------------------------------------------------------------------------------------- the model
def _bar(kind, lo, hi, label, tip, running=False, **kw):
    return dict(kind=kind, lo=lo, hi=hi, label=label, tip=tip, running=running, **kw)


def pack(bars: list) -> list[list]:
    """Greedy rows: a bar goes to the first row whose last bar ended before it starts."""
    rows: list[list] = []
    for b in sorted(bars, key=lambda b: b["lo"]):
        for row in rows:
            if row[-1]["hi"] <= b["lo"]:
                row.append(b)
                break
        else:
            rows.append([b])
    return rows


def _hm(t: float) -> str:
    return datetime.datetime.fromtimestamp(t).strftime("%H:%M")


def _when(t: float, now: float) -> str:
    """'14:05' today, 'yesterday 23:38' otherwise (the axis spans two dates)."""
    a, b = datetime.datetime.fromtimestamp(t), datetime.datetime.fromtimestamp(now)
    return a.strftime("%H:%M") if a.date() == b.date() else ("yesterday " if (b.date() - a.date()).days == 1 else a.strftime("%a ")) + a.strftime("%H:%M")


def _union(segs) -> float:
    """Seconds covered by a set of [lo, hi] stretches, overlaps counted once."""
    tot, end = 0.0, None
    for a, b in sorted(segs):
        if end is None or a > end:
            tot += b - a
            end = b
        elif b > end:
            tot += b - end
            end = b
    return tot


def _dur(s: float) -> str:
    m = int(round(s / 60))
    return f"{m} min" if m < 90 else f"{m // 60} h {m % 60:02d} min"


def collect(now: float | None = None, projects_dir: Path = pc.PROJECTS_DIR, sessions_dir: Path = pc.SESSIONS_DIR,
            testq_root: Path = TESTQ_ROOT, ledger: list | None = None, role_lines="read", boots="read",
            roles_on: dict | None = None, units_active: set | None = None) -> dict:
    now = float(now if now is not None else time.time())
    lo, hi = now - DAY, now
    gaps: list[str] = []
    if role_lines == "read":
        role_lines, role_why = read_role_lines(lo)
    else:
        role_why = None if role_lines is not None else "the systemd journal could not be read"
    if boots == "read":
        boots = read_boots()
    if roles_on is None:
        roles_on = roles_switch()
    if units_active is None:
        units_active = read_units_active()
    titles, seat_evs = read_ledger_bits(ledger)

    reg, reg_why = read_registry(Path(sessions_dir))
    sid_name = {s.get("sessionId"): s.get("name") for s in reg}
    alive_sid = {s.get("sessionId"): s for s in reg if s.get("alive")}
    proj_why = None if Path(projects_dir).is_dir() else f"the transcript folder {projects_dir} was not found"

    win_bars = {k: [] for k, _, _ in WINDOWS}
    win_help = {k: [] for k, _, _ in WINDOWS}
    role_tx: dict[str, dict] = {}
    auto_bars, other_bars = [], []
    active = []

    # live windows: open from when they started (or the day's start) to now
    for s in reg:
        w = window_of(s.get("name"))
        if w and s.get("alive") and s.get("entrypoint") != "sdk-cli":
            st = float(s.get("startedAt") or 0) / 1000 or lo
            win_bars[w].append(_bar("open", max(lo, st), hi, "open", f"{s.get('name')} · window open since "
                                    f"{datetime.datetime.fromtimestamp(st).strftime('%a %H:%M')} · session {s.get('sessionId')}"))

    files = []
    if not proj_why:
        for f in glob.glob(os.path.join(str(projects_dir), "*", "*.jsonl")):
            try:
                if os.path.getmtime(f) >= lo:
                    files.append(Path(f))
            except OSError:
                pass
    for f in files:
        st = scan(f)
        if st["last"] is None or st["last"] < lo:
            continue
        sid = f.stem
        name = st["title"] or sid_name.get(sid)
        live = sid in alive_sid
        a, b = max(lo, st["first"]), (hi if live else st["last"])
        segs = [[max(lo, x), min(hi, y)] for x, y in st["segs"] if y >= lo]
        w, role = window_of(name), role_of(name)
        last_ask = plain_prompt(st["prompts"][-1][1]) if st["prompts"] else ""
        if w:
            items = [(t, iid) for (seat, iid, t, _ev) in seat_evs if seat == w and st["first"] - 60 <= t <= b + 60]
            items.sort()
            seen, order = set(), []
            for t, iid in reversed(items):
                if iid not in seen:
                    seen.add(iid)
                    order.append(iid)
            named = [i for i in order if titles.get(i)]   # an item with no title would show its id: skip it
            if named:
                label = short_title(titles[named[0]])
                if len(order) > 1:
                    label += f" (+{len(order) - 1} more)"
            else:
                label = ("asked: " + last_ask) if last_ask else "nothing asked of it"
            tip = (f"{name} · session {sid} · {_when(st['first'], now)}–{'now' if live else _when(b, now)}"
                   + "".join(f" · {iid}: {short_title(titles.get(iid, ''), 60)}" for iid in order[:6])
                   + (f" · last asked: {last_ask}" if last_ask else ""))
            win_bars[w].append(_bar("session", a, b, label, tip, live, segs=segs))
            if live:
                active.append({"who": f"{w} window", "what": label, "since": a,
                               "state": "working" if alive_sid[sid].get("status") == "busy" else "open, waiting",
                               "tip": tip})
            # helpers
            for sf in glob.glob(os.path.join(str(f.with_suffix("")), "subagents", "agent-*.jsonl")):
                sp = Path(sf)
                try:
                    mt = sp.stat().st_mtime
                except OSError:
                    continue
                if mt < lo:
                    continue
                hs = scan(sp)
                if hs["last"] is None or hs["last"] < lo:
                    continue
                try:
                    meta = json.loads(sp.with_suffix("").with_suffix(".meta.json").read_text())
                except (OSError, ValueError):
                    meta = {}
                if not meta:
                    try:
                        meta = json.loads(Path(str(sp)[:-6] + ".meta.json").read_text())
                    except (OSError, ValueError):
                        meta = {}
                ids = [m for m in ITEM_RE.findall(hs["first_user"] or "") if m in titles]
                iid = ids[0] if ids else None
                desc = (meta.get("description") or "").strip()
                hlabel = desc or (short_title(titles[iid]) if iid else "helper (no description written)")
                running = live and pc.subagent_running(hs["last_rec"], mt, now)
                hb = hi if running else hs["last"]
                agent = sp.stem.removeprefix("agent-")
                htip = (f"helper of {w} · {hlabel} · {_when(hs['first'], now)}–{'now' if running else _when(hb, now)}"
                        f" ({_dur(hb - hs['first'])}) · agent {agent}" + (f" · {meta.get('agentType')}" if meta.get("agentType") else "")
                        + (f" · item {iid}: {short_title(titles[iid], 60)}" if iid else ""))
                win_help[w].append(_bar("helper", max(lo, hs["first"]), hb, hlabel, htip, running))
                if running:
                    active.append({"who": f"helper of {w}", "what": hlabel, "since": hs["first"], "state": "working",
                                   "tip": htip})
        elif role:
            role_tx[role[1]] = {"role": role[0], "first": st["first"], "last": st["last"], "ask": last_ask, "sid": sid}
        else:
            first = st["first_user"] or (st["prompts"][0][1] if st["prompts"] else "")
            fresh = now - st["last"] < 5 * 60
            if STEWARD_PROMPT in (first or "") or any(STEWARD_PROMPT in p for _, p in st["prompts"][:1]):
                lab = "called in because the SteveDesktop test lane was stuck"
                auto_bars.append(_bar("auto", a, min(b, hi), lab, f"automatic session {sid} · {f.parent.name} · {lab}"))
                if fresh:
                    active.append({"who": "automatic session", "what": lab, "since": a, "state": "working", "tip": sid})
            else:
                where = f.parent.name.replace("-mnt-d-ClaudeWork-rimmandrake-", "").replace("-home-mandrake-", "~/")
                lab = (("art judging: " if "art-eval" in where else "") + (plain_prompt(first, 60) if first else "no prompt recorded"))
                other_bars.append(_bar("auto", a, min(b, hi), lab, f"session {sid} · {name or 'untitled'} · started in {where}"))
                if fresh:
                    active.append({"who": "other Claude session", "what": lab, "since": a, "state": "working", "tip": sid})

    # roles: journal starts joined to transcripts
    role_bars, conductor_bars = [], []
    started = {}
    for ln in role_lines or []:
        m = re.match(r"\s*([\d.]+)\s.*Started (rm-role-[\w.-]+?)\.service", ln)
        if m:
            started[m.group(2)] = float(m.group(1))
    for unit in set(started) | {u for u in role_tx if role_tx[u]["last"] >= lo}:
        tx = role_tx.get(unit)
        rname = tx["role"] if tx else (unit.split("-")[2].capitalize() if unit.count("-") >= 3 else unit)
        t0 = started.get(unit) or (tx and tx["first"])
        what = ROLE_WORDS.get(rname, "a dispatcher role")
        if unit in units_active:
            b = _bar("role", max(lo, t0), hi, f"{rname} run: {what}", f"{unit} · running now", True)
            active.append({"who": f"{rname} run", "what": what, "since": t0, "state": "working", "tip": unit})
        elif tx:
            b = _bar("role", max(lo, t0), tx["last"], f"{rname} run: {what}",
                     f"{unit} · session {tx['sid']} · {_hm(t0)}–{_hm(tx['last'])} ({_dur(tx['last'] - t0)})"
                     + (f" · asked: {tx['ask']}" if tx["ask"] else ""))
        else:
            b = _bar("marker", t0, t0, f"{rname} run started {_hm(t0)}, end not recorded",
                     f"{unit} · started {_hm(t0)} · no transcript and no running unit, so its end is unknown")
        (conductor_bars if rname == "Conductor" else role_bars).append(b)

    # SteveDesktop (and any other testq host)
    tq_bars, tq_why = [], None
    if not Path(testq_root).is_dir():
        tq_why = f"the test-run records folder {testq_root} was not found"
    else:
        for state in ("done", "running", "orphans"):
            dpath = Path(testq_root) / state
            try:
                ents = [e for e in os.scandir(dpath) if e.name.endswith(".json") and e.stat().st_mtime >= lo - DAY]
            except OSError:
                continue
            for e in ents:
                try:
                    r = json.loads(Path(e.path).read_text())
                except (OSError, ValueError):
                    continue
                job = r.get("job") if isinstance(r.get("job"), dict) else {}
                res = r.get("result") if isinstance(r.get("result"), dict) else {}
                mod = job.get("mod") or "?"
                filler = job.get("requested_by") == "BENCH.filler"
                why = "queued automatically to keep the machine busy" if filler else f"asked for by {job.get('requested_by') or 'unknown'}"
                if state == "running" and not res:
                    t0 = _ts(r.get("sent")) or _ts(job.get("submitted"))
                    if t0 is None:
                        continue
                    lab = f"testing {mod} (running)"
                    tq_bars.append(_bar("test", max(lo, t0), hi, lab, f"job {job.get('id')} · {mod} · {why} · running since {_hm(t0)}", True, short=mod))
                    active.append({"who": "SteveDesktop", "what": f"testing {mod}", "since": t0, "state": "working",
                                   "tip": f"job {job.get('id')}"})
                    continue
                t0, t1 = _ts(res.get("started")), _ts(res.get("finished"))
                if t0 is None or t1 is None or t1 < lo:
                    continue
                cnt = res.get("counts") or {}
                outcome = ", ".join(f"{v} {k.lower().replace('unmeasured', 'not measured').replace('pass', 'passed').replace('fail', 'failed')}"
                                    for k, v in cnt.items() if v) or (res.get("outcome") or "").lower()
                lab = f"testing {mod}" + (f": {outcome}" if outcome else "")
                bad = any(str(k).upper().startswith("FAIL") and v for k, v in cnt.items()) \
                    or str(res.get("outcome") or "").upper() not in ("DONE", "PASS", "")
                tq_bars.append(_bar("test", max(lo, t0), t1, lab, f"job {job.get('id') or res.get('job')} · {mod} · {why} · "
                                    f"{_when(t0, now)}–{_when(t1, now)} ({_dur(t1 - t0)}) · host {res.get('host') or job.get('lane')} · "
                                    f"run {str(res.get('outcome') or '?').lower()}" + (f", {outcome}" if outcome else "") + (f" · cause {res.get('cause')}" if res.get("cause") else ""), short=mod, bad=bad))

    # PC off between boots
    off = []
    if boots is None:
        gaps.append("the boot list could not be read, so times the PC was off are not marked")
    else:
        bl = sorted((b.get("first_entry", 0) / 1e6, b.get("last_entry", 0) / 1e6) for b in boots if isinstance(b, dict))
        for (_, e0), (s1, _) in zip(bl, bl[1:]):
            if s1 > lo and e0 < hi and s1 - e0 > 60:
                off.append({"lo": max(lo, e0), "hi": min(hi, s1), "why": f"PC was off or restarting {_hm(e0)}–{_hm(s1)}"})

    lanes = []
    for k, title, sub in WINDOWS:
        opens = [b for b in win_bars[k] if b["kind"] == "open"]
        rows = pack([b for b in win_bars[k] if b["kind"] != "open"])
        if opens:
            rows = [opens + rows[0]] + rows[1:] if rows else [opens]
        rows += pack(win_help[k])
        nh = len(win_help[k])
        busy = _union([sg for x in win_bars[k] if x["kind"] == "session" for sg in x.get("segs") or []])
        sub = (f"{_dur(busy)} busy" if busy >= 60 else "window, idle") + (f", {nh} helper run{'s' if nh != 1 else ''}" if nh else "")
        lanes.append({"key": k, "title": title, "sub": sub, "busy": busy, "helpers": nh,
                      "rows": rows, "gap": proj_why or (reg_why if not rows else None),
                      "note": "" if rows else f"no {k} window in the past day"})
    cond_note = "" if conductor_bars else ("no Conductor run in the past day (the role is switched off in the dispatcher)"
                                           if roles_on.get("Conductor") is False else "no Conductor run in the past day")
    lanes.append({"key": "Conductor", "title": "Conductor", "sub": "dispatcher role", "rows": pack(conductor_bars),
                  "gap": role_why if not conductor_bars else None, "note": cond_note})
    lanes.append({"key": "Dispatcher", "title": "Roles", "sub": "dispatcher runs", "rows": pack(role_bars),
                  "gap": role_why, "note": "" if role_bars else "no role run in the past day"})
    if auto_bars:
        lanes.append({"key": "Steward", "title": "Auto runs", "sub": "test-lane rescues",
                      "rows": pack(auto_bars), "gap": None, "note": ""})
    if other_bars:
        lanes.append({"key": "Other", "title": "One-offs", "sub": "other sessions", "rows": pack(other_bars),
                      "gap": None, "note": ""})
    lanes.append({"key": "SteveDesktop", "title": "SteveDesktop", "sub": "test runs", "rows": pack(tq_bars),
                  "gap": tq_why, "note": "" if tq_bars else "no test run in the past day"})
    for k, _, _ in WINDOWS:   # a window that is open but did nothing all day is still "there"
        if not any(x["who"] == f"{k} window" for x in active):
            for ob in (x for x in win_bars[k] if x["kind"] == "open"):
                active.append({"who": f"{k} window", "what": "open, nothing asked of it in the past day",
                               "since": ob["lo"], "state": "idle", "tip": ob["tip"]})
    active.sort(key=lambda a: a["since"])
    return {"at": now, "lo": lo, "hi": hi, "lanes": lanes, "off": off, "gaps": gaps, "active": active}


# ---------------------------------------------------------------------------------------------- the page
CSS3 = """
main.wide{max-width:min(1100px,100vw)}
.act li{display:flex;flex-wrap:wrap;gap:0 8px;align-items:baseline}.act .w{color:var(--mustard);font-weight:600;white-space:nowrap}
.act .s{color:var(--dim);font-size:12.5px;margin-left:auto}
.tl{display:grid;grid-template-columns:104px minmax(0,1fr);margin-top:8px;border-top:1px solid #2c251f}
.nm{border-right:1px solid #2c251f}.nm div{box-sizing:border-box;padding:3px 6px 0 0;font-size:12.5px;line-height:1.2;overflow:hidden;border-bottom:1px solid #2c251f}
.nm b{display:block;color:var(--ink);font-weight:600}.nm small{color:var(--faint);font-size:11px}
.sc{min-width:0;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch}
.cv{position:relative}
.ln{position:relative;border-bottom:1px solid #2c251f;box-sizing:border-box}
.hd{position:relative;height:22px;border-bottom:1px solid #2c251f}
.tk{position:absolute;top:3px;font-size:11px;color:var(--dim);transform:translateX(-50%);white-space:nowrap}.tk.md{color:var(--mustard);font-weight:600}
.gl{position:absolute;top:0;bottom:0;width:1px;background:#2a231d}.gl.md{background:#5a4a2a}
.b{position:absolute;height:16px;border-radius:3px;font-size:11px;line-height:16px;padding:0 4px;white-space:nowrap;overflow:hidden;
 text-overflow:ellipsis;color:#191512;cursor:pointer;box-sizing:border-box;min-width:3px}
.b.open{background:#3a312a;color:var(--dim);height:6px;margin-top:5px;padding:0}
.b.session{background:#5c4a28;color:var(--ink)}.b.session i{position:absolute;top:0;bottom:0;background:var(--mustard)}
.b.session span{position:relative}
.b.helper{background:#d9c49a}.b.role{background:#8fb3a3}.b.test{background:#9fb0d6}.b.auto{background:#b9a3c9}.b.test.bad{background:#d9897a}
.b.run{box-shadow:inset -3px 0 0 #fff}
.b.marker{width:auto;background:none;color:#8fb3a3;padding-left:0;border-left:2px solid #8fb3a3;border-radius:0;padding-left:4px}
.gp{position:absolute;top:0;bottom:0;background:repeating-linear-gradient(45deg,#2b2520 0 6px,#211c18 6px 12px);
 color:var(--dim);font-size:11.5px;padding:3px 6px;box-sizing:border-box;overflow:hidden;white-space:nowrap}
.off{position:absolute;top:22px;bottom:0;background:repeating-linear-gradient(45deg,rgba(120,110,95,.28) 0 5px,transparent 5px 11px);
 z-index:3;pointer-events:auto;cursor:pointer}
.off span{position:sticky;left:0;font-size:11px;color:var(--ink);background:#191512;padding:0 3px}
.sd{position:absolute;z-index:2;padding-left:2px;font-size:11px;line-height:16px;color:var(--dim);white-space:nowrap;pointer-events:none}
.nt{position:absolute;left:8px;top:3px;font-size:12px;color:var(--faint);white-space:nowrap}
.nowl{position:absolute;top:0;bottom:0;width:2px;background:var(--red);z-index:4}
.nowt{position:absolute;bottom:3px;right:6px;font-size:11px;color:var(--red);font-weight:700;white-space:nowrap;z-index:5}
.key{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:12px;color:var(--dim);margin:8px 0}.key i{display:inline-block;width:18px;height:10px;
 border-radius:2px;margin-right:4px;vertical-align:-1px}
#tip{position:sticky;bottom:0;background:#2a221b;border:1px solid #4a3d2c;border-radius:8px;padding:8px 10px;font-size:13px;margin-top:10px;
 overflow-wrap:anywhere}
details{margin:6px 0}summary{cursor:pointer;color:var(--dim);font-size:13px}
"""


def _x(t: float, lo: float) -> float:
    return round((t - lo) / 3600 * PX_H, 1)


def _pc(px: float) -> str:
    """A nominal-px position as a share of the chart, so a desk-wide chart stretches and a phone scrolls."""
    return f"{px / (DAY / 3600 * PX_H) * 100:.3f}%"


def _day(t: float) -> str:
    return datetime.datetime.fromtimestamp(t).strftime("%a %d %b %H:%M")


def summary(d: dict) -> str:
    """One sentence for the day: who is working, who carried the day, what never ran."""
    act = [a for a in d["active"] if a["state"] == "working"]
    wins = [a["who"].split()[0] for a in act if a["who"].endswith(" window")]
    nh = sum(1 for a in act if a["who"].startswith("helper of"))
    nt = sum(1 for a in act if a["who"] == "SteveDesktop")
    now = (" + ".join(wins) or "no window") + (f" and {nh} helper{'s' if nh != 1 else ''}" if nh else "") + " working now"
    if nt:
        now += f", {nt} test running"
    busy = sorted(((ln.get("busy") or 0, ln) for ln in d["lanes"] if ln.get("busy")), key=lambda x: -x[0])
    day = "; over the day " + ", ".join(f"{ln['title']} was busy {_dur(b)}" + (f" with {ln['helpers']} helper runs" if ln.get("helpers") else "")
                                         for b, ln in busy[:3]) if busy else ""
    quiet = [ln["title"] for ln in d["lanes"] if not ln["rows"] and not ln.get("gap")]
    quiet += [ln["title"] for ln in d["lanes"] if ln["key"] in dict.fromkeys(k for k, _, _ in WINDOWS)
              and ln["rows"] and not ln.get("busy")]
    tail = f"; no work from {', '.join(quiet)}" if quiet else ""
    return now + day + tail + "."


def render(d: dict, base: str = "") -> str:
    from brief import CSS
    e = html.escape
    lo, hi, now = d["lo"], d["hi"], d["at"]
    W = round(DAY / 3600 * PX_H)
    out = ["<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
           "<meta http-equiv='refresh' content='300'><title>RimPulse: who worked when</title>"
           f"<style>{CSS}{CSS3}</style></head><body><main class='wide'>",
           f"<div class='hb'>Who worked when · past 24 hours, {e(_day(lo))} to {e(_day(hi))}, "
           f"{e(time.strftime('%Z', time.localtime(now)))} · <a href='{base}/brief'>brief</a> · "
           f"<a href='{base}/streams'>streams</a></div>",
           f"<div class='m'>{e(summary(d))}</div>",
           "<div class='m'>Windows are the Claude chat windows agents work in; a helper is a short-lived agent a window "
           "starts for one job; roles are runs the dispatcher starts on its own; SteveDesktop is the test PC running mod "
           "tests.</div>",
           "<h2>Working right now</h2>"]
    act = [a for a in d["active"] if a["state"] == "working"]
    idle = [a for a in d["active"] if a["state"] != "working"]
    if act:
        out.append("<ul class='act'>")
        for a in act:
            out.append(f"<li data-t='{e(a.get('tip') or '')}' title='{e(a.get('tip') or '')}'><span class='w'>{e(a['who'])}</span>"
                       f"<span>{e(a['what'])}</span><span class='s'>started {e(_when(a['since'], now))}</span></li>")
        out.append("</ul>")
    else:
        out.append("<div class='none'>No agent is working right now.</div>")
    if idle:
        out.append("<div class='m'>Open but idle: " + "; ".join(
            f"<span data-t='{e(a.get('tip') or '')}' title='{e(a.get('tip') or '')}'>{e(a['who'])} ({e(a['what'])}, "
            f"open since {e(_when(a['since'], now))})</span>" for a in idle) + "</div>")
    out.append("<h2>The past 24 hours</h2>"
               "<div class='key'><span><i style='background:var(--mustard)'></i>window working</span>"
               "<span><i style='background:#5c4a28'></i>window waiting between tasks</span>"
               "<span><i style='background:#3a312a;height:5px'></i>window open, idle</span>"
               "<span><i style='background:#d9c49a'></i>helper</span><span><i style='background:#8fb3a3'></i>dispatcher role</span>"
               "<span><i style='background:#9fb0d6'></i>test run</span><span><i style='background:#d9897a'></i>test run with a failure</span>"
               "<span><i style='background:#b9a3c9'></i>automatic or one-off session</span>"
               "<span><i style='background:#9fb0d6;box-shadow:inset -3px 0 0 #fff'></i>white end: still running</span>"
               "<span><i style='background:repeating-linear-gradient(45deg,#4a4036 0 3px,#211c18 3px 6px)'></i>no record (reason shown)</span></div>"
               "<div class='m'>Tap or hover a bar for its details. Swipe the chart sideways to go back in time.</div>")
    names, body = [], []
    # hour ticks
    first_h = (int(lo) // 3600 + 1) * 3600
    ticks, grid = [], []
    t = first_h
    while t < hi:
        dt = datetime.datetime.fromtimestamp(t)
        md = dt.hour == 0
        lab = dt.strftime("%a") if md else dt.strftime("%H:00")
        ticks.append(f"<span class='tk{' md' if md else ''}' style='left:{_pc(_x(t, lo))}'>{lab}</span>")
        grid.append(f"<div class='gl{' md' if md else ''}' style='left:{_pc(_x(t, lo))}'></div>")
        t += 3600
    names.append("<div style='height:22px'><small>local time</small></div>")
    body.append("<div class='hd'>" + "".join(ticks) + "</div>")
    for ln in d["lanes"]:
        rows = ln["rows"]
        nrows = max(1, len(rows))
        hpx = max(40, 8 + nrows * ROW_H)
        names.append(f"<div style='height:{hpx}px'><b>{e(ln['title'])}</b><small>{e(ln['sub'])}</small></div>")
        inner = []
        if ln.get("gap"):
            inner.append(f"<div class='gp' style='left:0;width:100%' data-t='{e(ln['gap'])}'>no record: {e(ln['gap'])}</div>")
        elif not rows:
            inner.append(f"<span class='nt' style='left:auto;right:12px'>{e(ln['note'])}</span>")
        for ri, row in enumerate(rows):
            top = 4 + ri * ROW_H
            row = sorted(row, key=lambda b: b["lo"])
            for bi, b in enumerate(row):
                x0, x1 = _x(b["lo"], lo), _x(b["hi"], lo)
                nxt = next((_x(c["lo"], lo) for c in row[bi + 1:] if c["kind"] != "open"), W)
                tip = e(b["tip"])
                if b["kind"] == "marker":
                    inner.append(f"<div class='b marker' style='left:{_pc(x0)};top:{top}px' data-t='{tip}' title='{tip}'>{e(b['label'])}</div>")
                    continue
                w = max(3.0, x1 - x0)
                cls = f"b {b['kind']}" + (" run" if b["running"] else "") + (" bad" if b.get("bad") else "")
                text = b.get("short") or b["label"]
                lab = "" if b["kind"] == "open" else e(text)
                side = ""
                if lab and w < 6.5 * min(len(text), 12) + 10:   # too narrow to read inside
                    lab = ""
                    room = nxt - x1 - 8
                    if b["kind"] != "session" and room >= 40:
                        n = int(room // 6.5)
                        side = (f"<span class='sd' style='left:calc({_pc(x1)} + 3px);top:{top}px'>"
                                f"{e(text if len(text) <= n else text[:max(1, n - 1)] + '…')}</span>")
                fill = ""
                if b["kind"] == "session":
                    fill = "".join(f"<i style='left:{max(0, _x(a, lo) - x0) / w * 100:.2f}%;width:max(2px,{(_x(c, lo) - _x(a, lo)) / w * 100:.2f}%)'></i>"
                                   for a, c in b.get("segs") or [] if c >= b["lo"])
                    lab = f"<span>{lab}</span>"
                inner.append(f"<div class='{cls}' style='left:{_pc(x0)};width:{_pc(w)};top:{top}px' data-t='{tip}' title='{tip}'>{fill}{lab}</div>{side}")
        body.append(f"<div class='ln' style='height:{hpx}px'>" + "".join(inner) + "</div>")
    over = []
    for o in d["off"]:
        over.append(f"<div class='off' style='left:{_pc(_x(o['lo'], lo))};width:{_pc(max(3.0, _x(o['hi'], lo) - _x(o['lo'], lo)))}' "
                    f"data-t='{e(o['why'])}' title='{e(o['why'])}'><span>{e(o['why'])}</span></div>")
    over.append(f"<div class='nowl' style='right:0'></div><span class='nowt'>now {e(_hm(now))}</span>")
    out.append("<div class='tl'><div class='nm'>" + "".join(names) + "</div><div class='sc'>"
               f"<div class='cv' style='min-width:{W}px'>" + "".join(grid) + "".join(body) + "".join(over) + "</div></div></div>")
    out.append("<div id='tip' hidden></div>")
    for g in d["gaps"]:
        out.append(f"<div class='m'>Not shown: {e(g)}.</div>")
    # the same bars as words, for a reader who cannot see a 3 px bar
    out.append("<h2>The same day as a list</h2>")
    for ln in d["lanes"]:
        bars = sorted((b for row in ln["rows"] for b in row if b["kind"] != "open"), key=lambda b: -b["lo"])
        if not bars:
            continue
        out.append(f"<details><summary>{e(ln['title'])} · {len(bars)} entr{'y' if len(bars) == 1 else 'ies'}</summary><ul>")
        for b in bars:
            end = "now" if b["running"] else ("?" if b["kind"] == "marker" else _when(b["hi"], now))
            out.append(f"<li data-t='{e(b['tip'])}' title='{e(b['tip'])}'><span class='st'>{e(_when(b['lo'], now))}–{e(end)}</span> "
                       f"{e(b['label'])}</li>")
        out.append("</ul></details>")
    out.append("<div class='foot'>From the Claude window list and transcripts, the systemd journal, the test-run records and "
               "the work ledger on this PC. A blank stretch means none of these recorded anything then; work on other machines (the Mac "
               "laptop) is not shown. \"Working\" means the window or helper wrote to its transcript in the last few minutes, or "
               "the window says it is busy. Refreshes every 5 minutes.</div>"
               "<script>for(const s of document.querySelectorAll('.sc'))s.scrollLeft=s.scrollWidth;"
               "document.addEventListener('click',function(ev){var b=ev.target.closest('[data-t]');var p=document.getElementById('tip');"
               "if(!b){p.hidden=true;return}p.textContent=b.getAttribute('data-t');p.hidden=false;});</script></main></body></html>")
    return "".join(out)


def data(now: float | None = None) -> dict:
    now = now if now is not None else time.time()
    hit = _CACHE.get("page")
    if hit and now - hit[0] < CACHE_S:
        return hit[1]
    d = collect(now)
    _CACHE["page"] = (now, d)
    return d


def page(path: str, now: float | None = None) -> tuple[int, str, bytes]:
    """/agents and /agents.json, served by brief.page on loopback 8765 and the tailnet listener."""
    try:
        d = data(now)
    except Exception as ex:  # noqa: BLE001 - the page says it is broken rather than 500 with nothing
        return 500, "text/plain; charset=utf-8", f"agents timeline failed: {type(ex).__name__}: {ex}\n".encode()
    if path.endswith(".json"):
        return 200, "application/json", json.dumps(d, default=str).encode()
    return 200, "text/html; charset=utf-8", render(d).encode()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["html"]:
        sys.stdout.write(render(collect()))
        return 0
    d = collect()
    print(f"as of {_hm(d['at'])}; active now:")
    for a in d["active"]:
        print(f"  {a['who']}: {a['what']} ({a['state']}, since {_when(a['since'], d['at'])})")
    for ln in d["lanes"]:
        n = sum(len(r) for r in ln["rows"])
        print(f"{ln['title']}: {n} bars in {len(ln['rows'])} rows" + (f"  GAP: {ln['gap']}" if ln["gap"] else "")
              + (f"  ({ln['note']})" if ln["note"] else ""))
    for o in d["off"]:
        print("  " + o["why"])
    for g in d["gaps"]:
        print("  not shown: " + g)
    return 0


if __name__ == "__main__":
    sys.exit(main())
