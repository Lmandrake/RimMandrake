#!/usr/bin/env python3
"""disk_grower.py -- name what is filling the root disk WHILE it fills (ROOT_DISK_FIX_NIGHT_GROWTH_OUTRUNS_REAPER).

Why: on 2026-11-04 root free fell 578 -> 140 GB between 10:40 and 12:52Z at ~3.3 GB/min, then came back in one step by
13:07Z (ops_watch series/disk.jsonl). The pool and scratch readings stayed flat, so no reaper could have freed it, and
by the time anyone looked the grower had gone with its evidence. The 2026-10-31 fall (474 -> 399 GB in ~90 min) went
the same way.

So every pressure tick (rm-scratch-pressure.timer, 10 min) this samples, cheaply, from /proc:
  - each readable process's `write_bytes` (bytes it sent to storage), keyed by pid AND start time so a reused pid is
    never read as growth;
  - and, only when the root is falling fast or is under the pressure line, the big regular files on the root's device
    that processes hold open, deleted ones included (a deleted file still open is space nobody can see with du).
A fall of FALL_GB within WINDOW_MIN, or a reading under the line, writes a capture (the alarm reads held_fall_gb, the
part of the fall still standing at the tick after, so churn freed within a tick is captured but not alarmed) naming the top writers since the
last tick (pid, GB, GB/min, systemd unit, cwd, command) and the big open files. A writer over GROWER_GB in one tick is
an alarm line in the reaper's alarms.log.

State (the reaper's state dir): growth.jsonl one row per tick (the live reading), io_last.json the previous sample,
growth_capture.json the latest capture, growth_captures.jsonl every capture.

Instrument limits, said rather than hidden: other users' processes are unreadable (counted as `blind`); a process
that exited between ticks takes its bytes with it; write_bytes counts page-cache writeback, so a writer's bytes can
land a tick late; tmpfs and drvfs writes are not root-disk bytes and mostly do not count.
"""
import json
import os
import stat
import time
from pathlib import Path

FALL_GB = 30.0          # a fall this big within WINDOW_MIN captures (11-04: ~33 GB per 10-min tick)
WINDOW_MIN = 30.0
GROWER_GB = 10.0        # one process writing this much since the last tick is named in alarms.log
BIG_FILE_GB = 1.0       # open files at least this big (allocated) are listed
TOP = 10
HISTORY_CAP = 8 * 1024 ** 2
SCAN_S = 60.0           # the open-file walk stops after this long and says so
SKIP_PREFIXES = ("/mnt/", "/proc/", "/sys/", "/dev/")     # other mounts, never stat'ed (a tmpfs fails the device test)
RATE_MAX_S = 3600       # a previous sample older than this gives a total, not a rate


def proc_root() -> Path:
    return Path(os.environ.get("DISK_GROWER_PROC", "/proc"))


def _read(p: Path) -> str | None:
    try:
        return p.read_text(errors="replace")
    except OSError:
        return None


def _pids(proc: Path) -> list[str]:
    try:
        return [n for n in os.listdir(proc) if n.isdigit()]
    except OSError:
        return []


def _start(proc: Path, pid: str) -> str | None:
    """Field 22 of /proc/<pid>/stat (start time in ticks); the comm field may hold spaces, so split after ')'."""
    s = _read(proc / pid / "stat")
    if not s or ")" not in s:
        return None
    rest = s.rsplit(")", 1)[1].split()
    return rest[19] if len(rest) > 19 else None


def sample_io(proc: Path) -> tuple[dict, int]:
    """{pid: {"w": write_bytes, "s": start}} for every readable process, and the count that could not be read."""
    out, blind = {}, 0
    for pid in _pids(proc):
        io = _read(proc / pid / "io")
        st = _start(proc, pid)
        if io is None or st is None:
            blind += 1
            continue
        for ln in io.splitlines():
            if ln.startswith("write_bytes:"):
                try:
                    out[pid] = {"w": int(ln.split(":", 1)[1]), "s": st}
                except ValueError:
                    blind += 1
                break
        else:
            blind += 1
    return out, blind


def unit_of(proc: Path, pid: str) -> str | None:
    """The innermost systemd unit (.service or .scope) in the process's cgroup path."""
    cg = _read(proc / pid / "cgroup") or ""
    for ln in cg.splitlines():
        parts = ln.split(":", 2)[-1].split("/")
        for p in reversed(parts):
            if p.endswith((".service", ".scope")):
                return p
    return None


def describe(proc: Path, pid: str) -> dict:
    cmd = (_read(proc / pid / "cmdline") or "").replace("\0", " ").strip()
    try:
        cwd = os.readlink(proc / pid / "cwd")
    except OSError:
        cwd = None
    return {"pid": int(pid), "unit": unit_of(proc, pid), "cwd": cwd, "cmd": cmd}


def writers(prev: dict, cur: dict, dt_s: float) -> list[dict]:
    """Bytes each process wrote since the previous sample. A pid whose start time changed is a new process: its
    whole count is since its own start, which is still at most this tick for anything started since."""
    out = []
    for pid, c in cur.items():
        p = prev.get(pid)
        base = p["w"] if p and p.get("s") == c["s"] else 0
        d = c["w"] - base
        if d > 0:
            out.append({"pid": pid, "bytes": d})
    out.sort(key=lambda r: -r["bytes"])
    return out


def open_big(proc: Path, dev: int, min_bytes: int, deadline: float) -> tuple[list[dict], bool]:
    """Regular files on device `dev` held open by readable processes, allocated >= min_bytes, one row per file
    (inode), naming every pid holding it. Returns (rows, finished)."""
    files: dict[tuple, dict] = {}
    for pid in _pids(proc):
        if time.time() > deadline:
            return list(files.values()), False
        fd_dir = proc / pid / "fd"
        try:
            fds = os.listdir(fd_dir)
        except OSError:
            continue
        for fd in fds:
            if time.time() > deadline:
                return list(files.values()), False
            try:       # readlink touches no target filesystem: sockets, pipes and other mounts (a hung drvfs or 9p
                target = os.readlink(fd_dir / fd)  # stat can block) are skipped before anything is stat'ed
            except OSError:
                continue
            if not target.startswith("/") or target.startswith(SKIP_PREFIXES):
                continue
            try:
                st = os.stat(fd_dir / fd)
            except OSError:
                continue
            if not stat.S_ISREG(st.st_mode) or st.st_dev != dev:
                continue
            alloc = st.st_blocks * 512
            if alloc < min_bytes:
                continue
            key = (st.st_dev, st.st_ino)
            row = files.get(key)
            if row is None:
                row = files[key] = {"path": target.removesuffix(" (deleted)"), "deleted": target.endswith(" (deleted)"),
                                    "alloc_bytes": alloc, "size_bytes": st.st_size, "pids": []}
            if int(pid) not in row["pids"]:
                row["pids"].append(int(pid))
    return list(files.values()), True


def _history(sd: Path, now: float, window_s: float) -> list[dict]:
    rows = []
    for p in (sd / "growth.jsonl.1", sd / "growth.jsonl"):
        try:
            lines = p.read_text().splitlines()
        except OSError:
            continue
        for ln in lines[-200:]:  # cut-ok: the last 200 lines read, a list
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if isinstance(r, dict) and now - r.get("t", 0) <= window_s:
                rows.append(r)
    return rows


def _gb(b: float) -> float:
    return round(b / 1e9, 2)


def tick(sd: Path, free_gb: float, line_gb: float, root: str = "/", now: float | None = None) -> dict:
    """One pressure tick: sample, decide, capture. Returns the growth row it appended."""
    now = time.time() if now is None else now
    proc = proc_root()
    sd.mkdir(parents=True, exist_ok=True)
    fall_gb = float(os.environ.get("DISK_GROWER_FALL_GB", FALL_GB))
    window_s = float(os.environ.get("DISK_GROWER_WINDOW_MIN", WINDOW_MIN)) * 60
    grower_b = float(os.environ.get("DISK_GROWER_GB", GROWER_GB)) * 1e9

    hist = _history(sd, now, window_s)
    peak = max([r["free_gb"] for r in hist if isinstance(r.get("free_gb"), (int, float))] + [free_gb])
    fall = round(peak - free_gb, 1)
    # OPS_ROOT_GROWER_MEASURE_CAUGHT_WRITING_QMOX: the fall that held for a tick, peak minus the HIGHER of this reading and
    # the one before it. Relentless's walled boxes (a 3.8 GB export per check, often copied again by the checker) swung
    # the root 750 -> 704 -> 750 -> 708 GB on 2026-11-06, reaped within a tick: fall_gb read 41-46 and alarmed on churn
    # that was already being given back. A real fill (11-04: ~33 GB every tick) holds, so it still reads by its 2nd tick.
    prior = [r for r in hist if isinstance(r.get("free_gb"), (int, float)) and isinstance(r.get("t"), (int, float))
             and r["t"] < now]
    held = round(max(0.0, peak - max(free_gb, max(prior, key=lambda r: r["t"])["free_gb"])), 1) if prior else 0.0

    cur, blind = sample_io(proc)
    try:
        last = json.loads((sd / "io_last.json").read_text())
        prev, dt = last.get("pids", {}), now - float(last.get("t", now))
    except (OSError, ValueError, AttributeError, TypeError):
        prev, dt = {}, 0.0
    tmp = sd / "io_last.json.tmp"
    tmp.write_text(json.dumps({"t": now, "pids": cur}))
    os.replace(tmp, sd / "io_last.json")
    # with no previous sample every count is lifetime, not this tick: rank nobody
    ws = writers(prev, cur, dt) if prev else []

    why = []
    if fall >= fall_gb:
        why.append(f"root fell {fall} GB within {window_s / 60:.0f} min")
    if free_gb < line_gb:
        why.append(f"root {free_gb} GB free is under the {line_gb} GB line")
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "t": now, "free_gb": free_gb,
           "fall_gb": fall, "held_fall_gb": held, "window_min": window_s / 60, "readable": len(cur), "blind": blind,
           "top_writer_gb": _gb(ws[0]["bytes"]) if ws else 0.0, "captured": bool(why)}
    if why:
        try:
            dev = os.stat(root).st_dev
        except OSError:
            dev = -1
        files, finished = open_big(proc, dev, int(float(os.environ.get("DISK_GROWER_BIG_GB", BIG_FILE_GB)) * 1e9),
                                   time.time() + SCAN_S)
        files.sort(key=lambda r: -r["alloc_bytes"])
        top = []
        for w in ws[:TOP]:
            d = describe(proc, w["pid"])
            d.update(gb=_gb(w["bytes"]), gb_per_min=round(w["bytes"] / 1e9 / (dt / 60), 2) if 0 < dt <= RATE_MAX_S else None)
            top.append(d)
        cap = {"ts": row["ts"], "why": why, "free_gb": free_gb, "fall_gb": fall, "held_fall_gb": held, "since_last_sample_s": round(dt),
               "writers": top, "open_big": [dict(f, alloc_gb=_gb(f["alloc_bytes"])) for f in files[:TOP]],
               "open_scan_finished": finished, "readable": len(cur), "blind": blind}
        tmp = sd / "growth_capture.json.tmp"
        tmp.write_text(json.dumps(cap, indent=1))
        os.replace(tmp, sd / "growth_capture.json")
        _append(sd / "growth_captures.jsonl", cap)
        named = [w for w in top if w["gb"] * 1e9 >= grower_b]
        if named:
            with open(sd / "alarms.log", "a") as f:
                for w in named:
                    f.write(f"{row['ts']} GROWER pid {w['pid']} wrote {w['gb']} GB in {dt / 60:.0f} min "
                            f"({w['unit']}; cwd {w['cwd']}): {w['cmd']}\n")
        row["named"] = [{"pid": w["pid"], "gb": w["gb"], "unit": w["unit"]} for w in named]
    _append(sd / "growth.jsonl", row)
    return row


def _append(p: Path, obj: dict):
    try:
        if p.stat().st_size > HISTORY_CAP:
            os.replace(p, p.with_name(p.name + ".1"))
    except FileNotFoundError:
        pass
    with open(p, "a") as f:
        f.write(json.dumps(obj) + "\n")
