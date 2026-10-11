#!/usr/bin/env python3
"""WSL-side exporter (rm-telemetry-export.timer, every minute).

telemetryd lives on Windows so it survives `wsl --shutdown` (design §5), and it must NOT read
\\\\wsl.localhost\\... itself: touching that path starts the distro, which would undo an intentional
shutdown. So WSL pushes its own sources out instead, as JSON lines appended to
E:\\telemetry\\inbox\\wsl\\wsl_<utc-day>.jsonl, each row tagged `src`:

  memwatch_sample / memwatch_event   ~/.local/state/rm-memwatch/{samples,events}.jsonl (cursor tail)
  objstore                           ~/.local/state/rm-objstore/samples.jsonl
  pulse                              ~/.local/state/rm-dashboard/metrics.jsonl (alarm open/close/ack)
  ledger                             both seat clones' ledger shards; deduped by line hash (`_h`),
                                     because union-merge pulls reorder and duplicate lines
  selftests                          ~/.local/state/rm-selftests/last_run.json when it changes
  wsl_host                           /proc/meminfo, / disk usage, load — every run

Cursors: ~/.local/state/rm-telemetry/export_state.json. Inbox files older than 7 days are
deleted here (telemetryd has kept a raw copy by then).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tcommon import cfg, read_json, utc_day, write_json_atomic  # noqa: E402

HOME = os.path.expanduser("~")
STATE = os.environ.get("RM_TELEMETRY_EXPORT_STATE", os.path.join(HOME, ".local", "state", "rm-telemetry",
                                                                  "export_state.json"))
CLONES = ["/home/mandrake/rm/bench", "/home/mandrake/rm/foundry"]
MAX_READ = 4 << 20


def tail(path: str, st: dict, key: str) -> list[dict]:
    """Rows appended since last time; follows rename rotation via inode (path and path.1)."""
    out = []
    for p in (path + ".1", path):
        try:
            s = os.stat(p)
        except OSError:
            continue
        k = f"{key}:{s.st_ino}"
        off = st.get(k)
        midfile = False
        if off is None:
            # first sight of this file: read from 0, except on install (key never seen), where an
            # existing big file contributes only its last 1 MB so the inbox does not balloon
            off = 0
            if not st.get("_seen_" + key) and s.st_size > (1 << 20):
                off, midfile = s.st_size - (1 << 20), True
        if s.st_size < off:
            off = 0
        if s.st_size == off:
            st[k] = off
            continue
        with open(p, "rb") as f:
            f.seek(off)
            data = f.read(min(MAX_READ, s.st_size - off))
        end = data.rfind(b"\n")
        if end < 0:
            continue
        lines = data[:end + 1].split(b"\n")[:-1]
        if midfile:
            lines = lines[1:]   # the first fragment is a partial line
        for line in lines:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict):
                out.append(r)
        st[k] = off + end + 1
    st["_seen_" + key] = True
    # forget cursors of inodes that no longer exist under either name
    live = set()
    for p in (path, path + ".1"):
        try:
            live.add(f"{key}:{os.stat(p).st_ino}")
        except OSError:
            pass
    for k in [k for k in st if k.startswith(key + ":") and k not in live]:
        del st[k]
    return out


def ledger_rows(st: dict) -> list[dict]:
    seen = set(st.get("ledger_seen", []))
    mt = st.setdefault("ledger_mtime", {})
    out = []
    for c in CLONES:
        for p in glob.glob(os.path.join(c, "infrastructure", "state", "ledger", "events", "*.jsonl")):
            try:
                m = os.path.getmtime(p)
            except OSError:
                continue
            if mt.get(p) == m:
                continue
            mt[p] = m
            with open(p, "rb") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    h = hashlib.sha1(line).hexdigest()[:16]
                    if h in seen:
                        continue
                    seen.add(h)
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(r, dict):
                        r["_h"] = h
                        out.append(r)
    st["ledger_seen"] = sorted(seen)
    return out


def wsl_host() -> dict:
    mi = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                mi[k] = int(v.split()[0]) * 1024
    except OSError:
        pass
    vs = os.statvfs("/")
    return {"src": "wsl_host", "ts": time.time(), "mem_total": mi.get("MemTotal"), "mem_avail": mi.get("MemAvailable"),
            "swap_used": (mi.get("SwapTotal", 0) - mi.get("SwapFree", 0)) if mi else None,
            "disk_total": vs.f_blocks * vs.f_frsize, "disk_free": vs.f_bavail * vs.f_frsize,
            "disk_used": (vs.f_blocks - vs.f_bfree) * vs.f_frsize, "load1": os.getloadavg()[0]}


def collect(st: dict) -> list[dict]:
    S = os.path.join(HOME, ".local", "state")
    rows = []
    for r in tail(os.path.join(S, "rm-memwatch", "samples.jsonl"), st, "mw_s"):
        rows.append({"src": "memwatch_sample", **r})
    for r in tail(os.path.join(S, "rm-memwatch", "events.jsonl"), st, "mw_e"):
        rows.append({"src": "memwatch_event", **r})
    for r in tail(os.path.join(S, "rm-objstore", "samples.jsonl"), st, "obj"):
        rows.append({**r, "src": "objstore", "ts": r.get("ts") or r.get("at") or time.time()})
    for r in tail(os.path.join(S, "rm-dashboard", "metrics.jsonl"), st, "pulse"):
        rows.append({"src": "pulse", **r})
    for r in ledger_rows(st):
        rows.append({**r, "src": "ledger"})
    lr = os.path.join(S, "rm-selftests", "last_run.json")
    try:
        m = os.path.getmtime(lr)
        if st.get("selftests_mtime") != m:
            st["selftests_mtime"] = m
            d = read_json(lr, {}) or {}
            counts: dict = {}
            for x in d.get("results") or []:
                counts[x.get("state", "?")] = counts.get(x.get("state", "?"), 0) + 1
            rows.append({"src": "selftests", "ts": m, "wall": d.get("wall"), "counts": counts,
                         "failed": [x.get("path") for x in d.get("results") or [] if x.get("state") == "FAIL"][:30]})
    except OSError:
        pass
    rows.append(wsl_host())
    return rows


def main() -> int:
    inbox = os.path.join(cfg()["inbox"], "wsl")
    if not os.path.isdir(cfg()["root"]):
        print(f"telemetry root {cfg()['root']} absent: nothing exported (UNMEASURED)", file=sys.stderr)
        return 2
    os.makedirs(inbox, exist_ok=True)
    st = read_json(STATE, {}) or {}
    rows = collect(st)
    if rows:
        with open(os.path.join(inbox, f"wsl_{utc_day(time.time())}.jsonl"), "a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, separators=(",", ":"), default=str) + "\n")
    write_json_atomic(STATE, st)
    for p in glob.glob(os.path.join(inbox, "wsl_*.jsonl")):
        if time.time() - os.path.getmtime(p) > 7 * 86400:
            os.remove(p)
    print(f"exported {len(rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
