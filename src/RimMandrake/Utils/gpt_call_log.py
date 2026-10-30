#!/usr/bin/env python3
"""GPT call log for per-arm metering: crash-safe under parallel writers.

drvfs (/mnt/<drive>) O_APPEND is NOT atomic across processes (60 parallel calls -> 49 lines, 4 corrupt), so:
  * RM_GPT_CALL_LOG set -> that FILE (explicit override, one O_APPEND write per record) or, if it names a
    directory (existing, or a trailing '/'), one file per call inside it;
  * default: <agent-storage>/rimmandrake/arena/gpt_calls.jsonl ONLY when that root is on ext4, else the directory
    <root>/arena/gpt_calls.d/ with one uniquely named file per call (pid+time+uuid). Nothing is ever appended
    to a shared drvfs file by two processes.
read_records() merges the file (if any) and the directory (if any), and counts unreadable lines.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

AGENT_STORAGE = Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"
FALLBACK_ROOT = "/mnt/d/ClaudeWork/rimmandrake"


def fs_type(path) -> str:
    """Filesystem type of the longest /proc/mounts mount point containing path ('' if unknown)."""
    p = os.path.realpath(str(path))
    best, typ = "", ""
    try:
        for ln in open("/proc/mounts", errors="replace"):
            f = ln.split()
            if len(f) < 3:
                continue
            mp = f[1].replace("\\040", " ")
            if (p == mp or p.startswith(mp.rstrip("/") + "/")) and len(mp) >= len(best):
                best, typ = mp, f[2]
    except OSError:
        pass
    return typ


def storage_root() -> str:
    env = os.environ.get("RM_AGENT_STORAGE_ROOT", "").strip()
    if env:
        return env
    try:
        r = subprocess.run([sys.executable or "python3", str(AGENT_STORAGE), "rimmandrake"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:                                       # noqa: BLE001
        pass
    return FALLBACK_ROOT


def default_target(root=None):
    """(path, mode) with mode 'file' (single append file, ext4 only) or 'dir' (one file per call)."""
    root = Path(root or storage_root())
    probe = root
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    base = root / "arena"
    if fs_type(probe) == "ext4":
        return str(base / "gpt_calls.jsonl"), "file"
    return str(base / "gpt_calls.d"), "dir"


def resolve_target(mode=None):
    """(path, mode) honouring RM_GPT_CALL_LOG; mode arg 'dir'/'file' forces the mode on the default."""
    env = os.environ.get("RM_GPT_CALL_LOG", "").strip()
    if env:
        if env.endswith("/") or os.path.isdir(env):
            return env, "dir"
        return env, "file"
    p, m = default_target()
    return (p, m) if mode is None else (p, mode)


def write_record(rec: dict, target=None, mode=None) -> str:
    """Write one record; returns the file written. Raises on failure (caller decides to warn)."""
    if target is None:
        target, m = resolve_target()
        mode = mode or m
    mode = mode or ("dir" if (str(target).endswith("/") or os.path.isdir(target)) else "file")
    data = (json.dumps(rec) + "\n").encode()
    if mode == "dir":
        d = Path(target)
        d.mkdir(parents=True, exist_ok=True)
        name = "%d-%d-%s.jsonl" % (os.getpid(), int(time.time() * 1000), uuid.uuid4().hex[:12])
        tmp = d / ("." + name + ".tmp")
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, d / name)                            # readers never see a half-written record
        return str(d / name)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(target, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, data)                                   # one write call per record
    finally:
        os.close(fd)
    return str(target)


def read_records(target=None):
    """(records, unreadable_count). target None -> default file + default dir (both, merged), plus an
    RM_GPT_CALL_LOG override. A dir target is read as every *.jsonl in it; a file target also reads '<file>.d'."""
    if target is None:
        env = os.environ.get("RM_GPT_CALL_LOG", "").strip()
        if env:
            targets = [env]
        else:
            root = Path(storage_root()) / "arena"
            targets = [str(root / "gpt_calls.jsonl"), str(root / "gpt_calls.d")]
    else:
        targets = [str(target)]
    files = []
    for t in targets:
        if os.path.isdir(t):
            files += sorted(str(p) for p in Path(t).glob("*.jsonl"))
        elif os.path.isfile(t):
            files.append(t)
        if os.path.isdir(t + ".d"):
            files += sorted(str(p) for p in Path(t + ".d").glob("*.jsonl"))
    recs, bad = [], 0
    for fp in files:
        try:
            lines = open(fp, errors="replace").read().splitlines()
        except OSError:
            bad += 1
            continue
        for ln in lines:
            if not ln.strip():
                continue
            try:
                d = json.loads(ln)
                if not isinstance(d, dict):
                    raise ValueError
                recs.append(d)
            except Exception:                                # noqa: BLE001
                bad += 1
    return recs, bad
