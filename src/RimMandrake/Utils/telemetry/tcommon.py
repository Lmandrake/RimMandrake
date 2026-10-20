"""Shared paths, config and parsing for the telemetry stack (TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED).

Design: Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md (owner picks: hybrid
VictoriaMetrics + SQLite + Grafana + RimPulse alerts, data on E:, 1 s test tier + flight recorder).

Three laws (design §10): raw JSONL is the truth and the stores are caches; stale or absent is
UNMEASURED, never 0; no automatic mod blame.

Runs on Windows (telemetryd, supervise, cli) AND on WSL (wsl_export, health, selftest), so
every path is resolved through `cfg()`, and `TELEMETRY_CONFIG=<json>` overrides any key
(the selftest points the whole stack at a temp dir that way).
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone

IS_WIN = os.name == "nt"
CODE_DIR = os.path.dirname(os.path.abspath(__file__))


def _defaults() -> dict:
    # Where RimWorld's files are comes from game_paths.py ONLY (selftest_one_path_seam.py)
    import sys
    sys.path.insert(0, os.path.dirname(CODE_DIR))
    import game_paths
    import rmpaths  # the RimMandrake data root (scratch, artpipe, obs, build): never D:\\Luke\\dev
    jb = os.path.join(game_paths.LOCALLOW, "JawaBench")
    game_mods = game_paths.LOCAL_MODS
    modsconfig = game_paths.MODS_CONFIG
    if IS_WIN:
        root = "E:\\telemetry"
        mirror = "D:\\Luke\\dev\\RimMandrake"
        archive = "F:\\telemetry_archive"
    else:
        root = "/mnt/e/telemetry"
        mirror = "/mnt/d/Luke/dev/RimMandrake"
        archive = "/mnt/f/telemetry_archive"
    j = os.path.join
    return {
        "root": root,
        "db": j(root, "events.db"),
        "raw": j(root, "raw"),
        "state": j(root, "state"),
        "inbox": j(root, "inbox"),
        "logs": j(root, "logs"),
        "bin": j(root, "bin"),
        "archive": archive,
        "jawabench": jb,
        "game_mods": game_mods,
        "modsconfig": modsconfig,
        "bridge_calls": rmpaths.rm_str("scratch", "bridge_calls.jsonl"),
        "artpipe": rmpaths.rm_str("artpipe"),
        "mirror": mirror,
        "vm_url": "http://127.0.0.1:8428",
        "grafana_url": "http://127.0.0.1:3000",
        "pulse_url": "http://127.0.0.1:8765",
        # volumes the host sampler reads (letter -> role); a missing one is UNMEASURED, never 0
        "volumes": {"C": "os+game", "D": "dev", "E": "wsl+telemetry", "F": "archive"},
        "vhdx": j("E:\\" if IS_WIN else "/mnt/e/", "WSL", "Ubuntu", "ext4.vhdx"),
        # hourly directory sizes (name -> path); kept short, each walk costs IO
        "dirs": {
            "rmscratch": rmpaths.rm_str("scratch"), "artpipe": rmpaths.rm_str("artpipe"),
            "obs": rmpaths.rm_str("obs"), "rmbuild": rmpaths.rm_str("build"), "jawabench": jb, "telemetry": root,
        },
        # retention budgets (design §11 Q8a): VM 2y, raw 90 d on E: then F:, caps below
        "raw_days_hot": 90,
        "raw_cap_gb": 200,          # E: raw copies; oldest day moved to F: first when exceeded
        "archive_cap_gb": 2000,     # F: archive; oldest day deleted when exceeded
        "bridge_rows_days": 30,     # per-call SQLite rows (aggregates live 2 y in VM)
        "vm_retention": "2y",
        "poll_fast_s": 1.0,         # test tier armed
        "poll_slow_s": 15.0,
        "host_every_s": 60.0,
        "dirs_every_s": 3600.0,
        "run_health_observer": False,  # owner-gated (game_health_record.md: not during MUST 17)
    }


_CFG: dict | None = None


def cfg() -> dict:
    global _CFG
    if _CFG is None:
        c = _defaults()
        p = os.environ.get("TELEMETRY_CONFIG")
        if p and os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                c.update(json.load(f))
        _CFG = c
    return _CFG


def reset_cfg() -> None:
    global _CFG
    _CFG = None


# ------------------------------------------------------------------ JSON parsing

def _first_kind_hook(pairs):
    """Keep the FIRST `kind` (the envelope). JawaBench incident/awareness rows repeat `kind`
    (design §1.1 defect); a plain json.loads keeps the last and mis-files the row."""
    d = {}
    for k, v in pairs:
        if k in d:
            d.setdefault(k + "_2", v)
            continue
        d[k] = v
    return d


def loads(line: str | bytes):
    try:
        return json.loads(line, object_pairs_hook=_first_kind_hook)
    except (ValueError, UnicodeDecodeError):
        return None


def parse_ts(v) -> float | None:
    """ISO-8601 (Z, +00:00, -0700) or epoch seconds/ms -> epoch seconds."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) / 1000.0 if v > 1e11 else float(v)
    s = str(v).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    m = re.match(r"(.*[T ]\d\d:\d\d:\d\d(?:\.\d+)?)([+-]\d\d)(\d\d)$", s)
    if m:
        s = f"{m.group(1)}{m.group(2)}:{m.group(3)}"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def iso(ts: float | None) -> str:
    if ts is None:
        return "-"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def utc_day(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")


def write_json_atomic(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"), default=str)
    os.replace(tmp, path)


def read_json(path: str, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def now() -> float:
    return time.time()


def bridge_failed(success, status) -> bool:
    """Failed = the call said success false, or (success unknown) its status is not ok. Unknown + ok is not a failure."""
    if success is not None:
        return not success
    return status not in (None, "ok")
