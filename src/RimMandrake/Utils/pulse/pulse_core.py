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
ARTPIPE_DIR = Path(os.environ.get("ARTPIPE_STATE_DIR", "/mnt/d/Luke/dev/_artpipe"))
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
OLD_ASK_SECS = 3 * 86400         # older asks fold into one "older (N)" line (nothing dropped)
SHEETS_DIRS = [c / "Transient" / "biome_ffar" for c in CLONES]

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


def session_extras(sid: str, now: float, projects_dir: Path = PROJECTS_DIR) -> dict:
    """active subagent count, transcript mtime, and the pending question text if any."""
    ex = {"subagents": 0, "transcript_mtime": None, "question": None}
    for t in projects_dir.glob(f"*/{sid}.jsonl"):
        try:
            ex["transcript_mtime"] = t.stat().st_mtime
        except OSError:
            pass
        last = _last_record(t)
        m = (last or {}).get("message") or {}
        for c in m.get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "AskUserQuestion":
                qs = (c.get("input") or {}).get("questions") or []
                if qs:
                    ex["question"] = qs[0].get("question") or qs[0].get("header")
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


def read_jsonl_tail(path: Path, tail_bytes: int = 1 << 20) -> list[dict]:
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
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def read_ledger(clones: list[Path] = CLONES) -> list[dict]:
    """Union of every clone's shards (each seat's own shard is freshest in its own clone)."""
    seen, out = set(), []
    for c in clones:
        for f in glob.glob(str(c / "infrastructure/state/ledger/events/*.jsonl")):
            for e in read_jsonl_tail(Path(f), 4 << 20):
                k = (e.get("seat"), e.get("tsn"), e.get("event"), e.get("id"))
                if k in seen:
                    continue
                seen.add(k)
                out.append(e)
    out.sort(key=lambda e: e.get("tsn") or 0)
    return out


def read_artpipe(d: Path = ARTPIPE_DIR, prev: dict | None = None, now: float = 0) -> dict:
    def n(sub: str) -> int:
        try:
            return sum(1 for e in os.scandir(d / sub) if e.name.endswith(".json"))
        except OSError:
            return -1
    out = {"pending": n("pending"), "active": n("active"), "failed": n("failed")}
    if prev and now - prev.get("done_at", 0) < 300:   # done/ holds 10k entries on drvfs
        out["done"], out["done_at"] = prev.get("done"), prev.get("done_at")
    else:
        out["done"], out["done_at"] = n("done"), now
    out["ok"] = out["pending"] >= 0
    return out


def read_bridge(clone: Path = CLONES[0]) -> str | None:
    try:
        for line in (clone / "infrastructure/state/BRIDGE").read_text().splitlines():
            if line and not line.startswith("#"):
                return line.strip()
    except OSError:
        return None
    return None


def read_hands(state_dir: Path | None = None) -> list[dict]:
    """Things agents deliberately handed the owner (`pulse.py hand`). Newest record per id wins."""
    out: dict[str, dict] = {}
    for h in read_jsonl_tail((state_dir or STATE_DIR) / "hands.jsonl", 2 << 20):
        if h.get("id") and h.get("target"):
            out[h["id"]] = h
    return list(out.values())


def http_ok(url: str, timeout: float = 0.8) -> bool:
    import urllib.request
    try:
        return urllib.request.urlopen(url, timeout=timeout).status == 200
    except Exception:
        return False


def parse_sheet_log(text: str) -> dict:
    import re
    urls = re.findall(r"https?://[^\s]+", text)
    m = re.search(r"(\d+) rows\s*·\s*(\d+) decided", text)
    return {"urls": urls, "never_reviewed": "NEVER reviewed" in text,
            "rows": int(m.group(1)) if m else None}


def read_sheets(dirs: list[Path] | None = None, probe=http_ok) -> list[dict]:
    """Every review-sheet server that answers: the LAST url in its serve.log that returns HTTP 200
    (SHEETS_INDEX/TONIGHT docs carry stale ports - never read those)."""
    import re
    from concurrent.futures import ThreadPoolExecutor
    logs: dict[str, Path] = {}
    for d in (dirs if dirs is not None else SHEETS_DIRS):
        for f in glob.glob(str(d / "*.serve.log")):
            f = Path(f)
            if f.name not in logs or f.stat().st_mtime > logs[f.name].stat().st_mtime:
                logs[f.name] = f

    def one(f: Path):
        try:
            info = parse_sheet_log(f.read_text(errors="replace"))
            mt = f.stat().st_mtime
        except OSError:
            return None
        live = next((u for u in reversed(info["urls"]) if probe(u)), None)
        if not live:
            return None
        name = re.sub(r"_sheet_.*$", "", f.name.replace(".serve.log", ""))
        return {"name": name, "url": live, "unreviewed": info["never_reviewed"], "rows": info["rows"], "mtime": mt}
    with ThreadPoolExecutor(8) as ex:
        return [r for r in ex.map(one, logs.values()) if r]


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


def classify_sessions(sessions: list[dict], extras: dict, seen: dict, items: dict,
                      acks: dict, now: float) -> tuple[list[dict], dict, list[dict]]:
    """rows, new `seen` map, metric events. `seen` is {sid: {name, last_alive, file}}."""
    rows, events = [], []
    new_seen = dict(seen)
    present = set()
    for s in sessions:
        sid = s.get("sessionId") or str(s.get("pid"))
        present.add(sid)
        who = seat_name(s)
        ex = extras.get(sid, {})
        sub = ex.get("subagents", 0)
        upd = (s.get("statusUpdatedAt") or s.get("updatedAt") or 0) / 1000
        if not s.get("alive"):
            if sid in seen:   # we watched it live; process gone, file left behind
                inc = f"lost:{sid}"
                rows.append(_red(inc, who, f"{who} window lost — process gone, session file left",
                                 seen[sid].get("last_alive", upd), acks, src="sessions",
                                 link={"type": "path", "value": win_path(s.get('_file', '')), "label": "session"}))
            continue
        new_seen[sid] = {"name": who, "last_alive": now, "file": s.get("_file")}
        item = items.get(who.upper())
        doing = f" · {item}" if item else ""
        status = s.get("status")
        key = f"win:{sid}"
        seat = seat_key(s)
        win = {"seat": seat, "label": chip_label(s), "upd": upd, "sub": sub}
        did = (not s.get("startedAt")) or (upd - s["startedAt"] / 1000 > 5)   # acted since launch
        lead = f"{who} "

        def add(r, state):
            r["seat"], r["win"] = seat, {**win, "state": state}
            r["label"] = r["text"][len(lead):] if r["text"].startswith(lead) else r["text"]
            rows.append(r)
        if status == "waiting" and seat:
            q = ex.get("question") or s.get("waitingFor") or "waiting"
            label = "asks" if ex.get("question") else "waiting"
            add(_amber(key, who, f"{who} {label}: {short(q, 90)}", upd, acks, explicit=True, sub=sub), "run")
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


def kill_class(k: dict) -> str:
    """planted | harness_test | seat"""
    mc = k.get("memcg") or ""
    if "rm-harness" in mc:
        return "planted" if k.get("limit_kb") == PLANTED_CAP_KB else "harness_test"
    return "seat"


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
        else:
            groups.setdefault(c, []).append(k)
    rows = []
    for g, ks in groups.items():
        ks.sort(key=lambda k: k["t"])
        last = ks[-1]
        n = len(ks)
        cap = f"{(last.get('limit_kb') or 0) / 1048576:.1f} GB cap" if last.get("limit_kb") else "its cap"
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
        else:
            who = g.split(":", 1)[1]
            where = "tool cgroup" if last["memcg"].endswith("claude-code-bash") else "window"
            text = f"OOM kill · {who} {where} at {cap}" + (f" · ×{n} today" if n > 1 else "")
            r = _row(inc, "red", who, text, last["t"], src="kernel", incident=inc, count=n,
                     toasted_elsewhere=True)   # memwatch toasts seat kills itself
        r["acked"] = not fresh
        r["toast_key"] = f"{inc}@{int(last['t'])}"
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


def classify_ledger(ledger: list[dict], since: float, now: float) -> tuple[list[dict], dict]:
    titles = {e["id"]: e.get("title") for e in ledger if e.get("event") == "file" and e.get("id")}
    rows, counts = [], {"filed": 0, "closed": 0, "implemented": 0, "verifies": 0, "drops": 0}
    owner_needs = {}
    for e in ledger:
        t = iso_to_epoch(e.get("ts", ""))
        ev, iid = e.get("event"), e.get("id")
        if ev == "needs" and (e.get("to") or "").upper() == "OWNER":
            owner_needs[iid] = (t, e)
        elif ev in ("close", "drop", "supersede", "reassign") and iid in owner_needs:
            owner_needs.pop(iid, None)
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
    for iid, (t, e) in owner_needs.items():
        if now - t < 14 * 86400:
            reason = short(e.get("reason") or titles.get(iid) or "(no reason recorded on the needs event)", 90)
            lk = link_for(e) or item_link(iid)
            r = _row(f"needs:{iid}", "review", (e.get("seat") or "").upper(),
                     f"{iid} — {reason}", t, link=lk, src="ledger")
            r.update({"seat": (e.get("seat") or "").upper(), "title": nice_id(iid), "reason": reason})
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


def classify_looks(hands: list[dict], sheets: list[dict], seen_look: dict, now: float) -> list[dict]:
    """The "to look at" feed: deliberate hand-offs + live review sheets. An item leaves the list
    when its open link is clicked (state seen_look[id] = time). A re-handed target comes back."""
    rows = []
    for h in hands:
        if (seen_look.get(h["id"]) or 0) >= (h.get("ts") or 0):
            continue
        tgt = h["target"]
        link = ({"type": "url", "value": tgt, "label": "open"} if tgt.startswith("http")
                else {"type": "path", "value": h.get("win") or win_path(tgt), "label": "open"})
        ty = hand_type(tgt)
        seat = (h.get("seat") or "").upper() or None
        r = _row(h["id"], "look", seat or "", h.get("title") or Path(tgt).name, h.get("ts") or 0, link=link, src="hands")
        r.update({"seat": seat, "title": r["text"], "ltype": ty, "seen_id": h["id"],
                  "thumb": ty == "image" and not tgt.startswith("http")})
        rows.append(r)
    # one row per sheet rebuilt since he last opened it; clicking a row opens THAT sheet and
    # clears only that row (owner 2026-10-10: one aggregate row walked and cleared them all)
    for x in sorted(sheets, key=lambda x: x["name"]):
        if (seen_look.get("sheet:" + x["name"]) or 0) >= x["mtime"]:
            continue
        r = _row("sheet:" + x["name"], "look", "", f"{x['name']} sheet", x["mtime"],
                 link={"type": "url", "value": x["url"], "label": "open"}, src="sheets")
        r.update({"seat": None, "title": r["text"], "ltype": "sheet" + (" · never reviewed" if x["unreviewed"] else ""),
                  "seen_id": "sheet:" + x["name"], "thumb": False})
        rows.append(r)
    return rows


def build_chips(rows: list[dict], now: float) -> list[dict]:
    """The bottom strip: one small chip per thing that is alive, active first, stale last.
    Seat chips carry the seat; rimworld and mem are plain; idle non-seat windows merge into ONE
    dim chip at the far right (never a top row)."""
    chips = []
    wins = [r for r in rows if r.get("win")]
    for seat in SEATS:
        ws = [r["win"] for r in wins if r["win"]["seat"] == seat]
        if not ws:
            continue
        latest = max(w["upd"] for w in ws)
        agents = sum(w["sub"] for w in ws)
        st = ("run" if any(w["state"] == "run" for w in ws) else "stuck" if any(w["state"] == "stuck" for w in ws)
              else "idle" if now - latest < SEAT_WAIT_FADE_SECS else "stale")
        chips.append({"label": seat.lower(), "seat": seat, "state": st, "n": len(ws), "agents": agents,
                      "since": latest})
    for r in rows:
        if r["key"] == "game":
            chips.append({"label": "rimworld", "plain": True, "state": r["kind"] if r["kind"] == "run" else "idle",
                          "since": r["since"], "title": r["text"]})
        elif r["key"] == "artpipe":
            chips.append({"label": "artpipe", "seat": "ART", "state": r["kind"] if r["kind"] == "run" else "idle",
                          "since": r["since"], "title": r["text"]})
    bad = any(r["kind"] == "red" and not r.get("acked") and r.get("src") in ("memwatch", "kernel") for r in rows)
    chips.append({"label": "mem", "plain": True, "state": "red" if bad else "idle", "since": 0})
    others, dim = {}, {}
    for r in wins:
        w = r["win"]
        if w["seat"]:
            continue
        (others if w["state"] in ("run", "stuck") else dim).setdefault(w["label"], []).append(w)
    for lab, ws in others.items():
        chips.append({"label": lab, "state": "run", "n": len(ws), "since": max(w["upd"] for w in ws)})
    rank = {"run": 0, "stuck": 0, "red": 0, "idle": 1, "stale": 2}
    chips.sort(key=lambda c: (rank.get(c["state"], 1), -(c.get("since") or 0)))
    if dim:
        chips.append({"label": " · ".join(f"{k}{'×%d' % len(v) if len(v) > 1 else ''}" for k, v in
                                          sorted(dim.items(), key=lambda kv: -max(w["upd"] for w in kv[1]))),
                      "state": "dim", "since": max(w["upd"] for v in dim.values() for w in v)})
    return chips


def classify_artpipe(a: dict, now: float, at: float) -> list[dict]:
    if not a or not a.get("ok"):
        return []
    kind = "run" if a.get("active", 0) > 0 or a.get("pending", 0) > 0 else "idle"
    txt = f"artpipe · {a['active']} active · {a['pending']} queued"
    if a.get("done") is not None and a["done"] >= 0:
        txt += f" · {a['done']} done"
    if a.get("failed", 0) > 0:
        txt += f" · {a['failed']} failed"
    return [_row("artpipe", kind, "ART", txt, at, src="artpipe")]


def classify_game(probe: dict | None, bridge: str | None, now: float) -> list[dict]:
    if probe is None and bridge is None:
        return []
    running = (probe or {}).get("rimworld_running")
    # BRIDGE reads "HELD    <SEAT>    since ..." or "FREE ..."; the holder is the seat, not the verb
    tok = (bridge or "").split()
    holder = (tok[1] if tok[0] == "HELD" and len(tok) > 1 else tok[0]) if tok else "?"
    state = "UP" if running else "down" if running is False else "unprobed"
    txt = f"RimWorld {state} · bridge " + ("free" if holder == "FREE" else f"held by {holder}")
    return [_row("game", "run" if running else "idle", "GAME", txt, (probe or {}).get("at", now), src="probe")]


KIND_ORDER = {"red": 0, "amber": 1, "amber_soft": 2, "warn": 2.5, "stuck": 3, "run": 4, "review": 5, "look": 5.5, "idle": 6, "done": 7}


def order_rows(rows: list[dict]) -> list[dict]:
    def k(r):
        acked = 1 if r.get("acked") else 0
        base = KIND_ORDER.get(r["kind"], 9)
        if r["kind"] in ("red", "amber", "amber_soft", "warn") and acked:
            base = 6.5               # acked alarms drop below the live roster, still visible
        return (base, -(r.get("since") or 0) if r["kind"] in ("done", "red", "review", "look") else (r.get("since") or 0))
    return sorted(rows, key=k)


def build_strip(rows: list[dict]) -> list[dict]:
    """Alarm pills only (they must survive the widget being collapsed to its strip) + a done tally.
    Presence lives in `chips`."""
    pills = []
    for r in rows:
        if r.get("acked"):
            continue
        if r["kind"] == "red":
            pills.append({"kind": "red", "text": f"✖ {r['who']} {time.strftime('%H:%M', time.localtime(r['since']))}"})
        elif r["kind"] == "amber":
            pills.append({"kind": "amber", "text": f"◐ {r['who']}", "since": r["since"], "seat": r.get("seat")})
        elif r["kind"] == "amber_soft":
            pills.append({"kind": "amber_soft", "text": f"◑ {r['who']}", "since": r["since"], "seat": r.get("seat")})
        elif r["kind"] == "warn":
            pills.append({"kind": "warn", "text": "◆ test kill"})
    done = sum(1 for r in rows if r["kind"] == "done")
    if done:
        pills.append({"kind": "done", "text": f"✓ {done}"})
    return pills


def collect_snapshot(raw: dict, state: dict, now: float) -> tuple[dict, dict, list[dict]]:
    """Pure: raw sources + persisted state -> (snapshot, new state, metric events)."""
    acks = state.get("acks", {})
    items = current_items(raw.get("ledger", []), now)
    srows, seen, events = classify_sessions(raw.get("sessions", []), raw.get("extras", {}),
                                            state.get("seen", {}), items, acks, now)
    since = state.get("done_since") or (now - DONE_WINDOW_SECS)
    lrows, counts = classify_ledger(raw.get("ledger", []), since, now)
    oom = (classify_kernel_oom(raw["kernel_oom"], acks, now) if raw.get("kernel_oom") is not None
           else classify_oom(raw.get("memwatch", []), acks, now))   # memwatch only when the kernel log is unreadable
    looks = classify_looks(raw.get("hands", []), raw.get("sheets", []), state.get("seen_look", {}), now)
    rows = (oom + srows + lrows + looks
            + classify_artpipe(raw.get("artpipe", {}), now, raw.get("at", {}).get("artpipe", now))
            + classify_game(raw.get("probe"), raw.get("bridge"), now))
    rows = order_rows(rows)
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
    new_state = dict(state)
    new_state.update({"seen": seen, "open": open_now})
    snap = {
        "v": 2, "collected_at": now, "rows": rows, "strip": build_strip(rows), "chips": build_chips(rows, now), "counts": counts,
        "done_since": since, "sources": raw.get("source_status", {}),
        "tally": {k: sum(1 for r in rows if r["kind"] == k and not r.get("acked"))
                  for k in ("red", "amber", "amber_soft", "warn", "run", "done", "review", "look")},
    }
    return snap, new_state, events
