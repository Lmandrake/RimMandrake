#!/usr/bin/env python3
"""idle_fill.py — keep the art queue fed when it runs dry (ARTPIPE_IDLE_FILL_EMPTY_ALL_NIGHT).

The night of 2026-10-26/27 the daemon (rm-artpiped) sat IDLE with 0 pending, 0 active and Codex at 15% of its week
while owed art waited. Two causes: nothing ran the gated feeder (`art/donor_regen_jobs.py submit`) on a schedule,
and its only job list was built once (design/RimMandrake/donor_regen_jobs_2026-10-18.json) and exhausted, so defs
that became owed later never entered it. Art runs on Codex, not Claude tokens: a fed queue keeps producing when the
seats cannot.

    python3 src/RimMandrake/Utils/artpipe/idle_fill.py tick [--low-water 3] [--cap 40] [--max-age-h 20] [--dry-run]
    python3 src/RimMandrake/Utils/artpipe/idle_fill.py status

One tick:
  1. depth = job files in pending/ + active/ (manifests excluded). An absent state dir is an error, never "empty".
     depth >= --low-water -> BUSY, nothing else happens.
  2. the owed list = the newest <state>/_idle_fill/<stamp>/jobs.json. None, or older than --max-age-h -> rebuild it:
     biome_census.py -> texture_regen_audit.py -> donor_regen_jobs.py build (~11 min, reads the game folder; only
     ever when the queue is idle). A failed rebuild falls back to the previous list; with none -> BUILD_FAILED.
  3. `donor_regen_jobs.py submit --jobs <list> --cap <cap>`: unchanged, so every row still passes
     regen_eligibility.Gate — only confirmed NONE / PLACEHOLDER / DONOR art is queued (owner 2026-10-19); KEPT and
     already-regenerated (REFUSED_KEPT / REFUSED_REGEN) are refused there and logged in _refs/. Already-filed ids,
     the 429 back-off and the failed-pool requeue are submit's too.
  4. <state>/status/idle_fill.json records depth, action (BUSY / FED / NOTHING_OWED / BUILD_FAILED / LOCKED), the
     count filed and the list used, so a briefing can tell "nothing owed" from "owed but nobody fed it".
     Other actions: BACKOFF_429 (submit saw 429s), SUBMIT_FAILED, and a failed rebuild is not retried for
     BUILD_BACKOFF_H hours.

Run by the user timer rm-artpipe-idle-fill.timer (src/RimMandrake/Utils/systemd/). It never judges art and never
installs it: Opus/GPT judging (art_eval) and installs stay where they were.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import state_dir  # noqa: E402

REPO = state_dir.REPO_ROOT
ART_TOOLS = REPO / "src/RimMandrake/Utils/art"
LIST_DIR = "_idle_fill"
STATUS = "status/idle_fill.json"
BUILD_BACKOFF_H = 2
FILED_RE = re.compile(r"^(\d+) job\(s\) filed\b", re.M)


def depth(root: Path) -> int:
    return sum(1 for st in ("pending", "active") for f in (root / st).iterdir()
               if f.name.endswith(".json") and not f.name.endswith(".manifest.json"))


def newest_list(root: Path) -> Path | None:
    lists = [p for p in (root / LIST_DIR).glob("*/jobs.json") if p.is_file()]
    return max(lists, key=lambda p: p.stat().st_mtime) if lists else None


def parse_filed(out: str) -> int:
    return sum(int(m) for m in FILED_RE.findall(out))


def _env(root: Path) -> dict:
    # bulk_accept_renders (imported by donor_regen_jobs) reads ARTPIPE_STATE; state_dir reads ARTPIPE_STATE_DIR
    return dict(os.environ, ARTPIPE_STATE=str(root), ARTPIPE_STATE_DIR=str(root))


def _run(cmd: list, root: Path, log, timeout: int) -> subprocess.CompletedProcess:
    log.write(f"\n$ {' '.join(map(str, cmd))}\n")
    log.flush()
    r = subprocess.run([str(c) for c in cmd], cwd=REPO, env=_env(root), capture_output=True, text=True,
                       timeout=timeout)
    log.write(r.stdout + r.stderr + f"[rc={r.returncode}]\n")
    log.flush()
    return r


def real_build(root: Path):
    def build(out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "build.log").open("a") as log:
            steps = [
                ([sys.executable, ART_TOOLS / "biome_census.py", "--no-wookiee", "--out", out_dir], 1500),
                ([sys.executable, ART_TOOLS / "texture_regen_audit.py", "--census", out_dir / "census.json",
                  "--out", out_dir / "audit.json"], 900),
                ([sys.executable, ART_TOOLS / "donor_regen_jobs.py", "build", "--audit", out_dir / "audit.json",
                  "--census", out_dir / "census.json", "--out", out_dir / "jobs.tmp.json"], 600),
            ]
            for cmd, to in steps:
                r = _run(cmd, root, log, to)
                if r.returncode != 0:
                    raise RuntimeError(f"{Path(str(cmd[1])).name} rc={r.returncode} (see {out_dir / 'build.log'})")
        (out_dir / "jobs.tmp.json").replace(out_dir / "jobs.json")   # a half-built list is never "newest"
        return out_dir / "jobs.json"
    return build


def real_submit(root: Path):
    def submit(jobs: list, cap: int, dry: bool) -> dict:
        (root / "logs").mkdir(exist_ok=True)
        with (root / "logs" / f"idle_fill_{time.strftime('%Y%m%d')}.log").open("a") as log:
            log.write(f"\n=== {time.strftime('%Y-%m-%dT%H:%M:%S%z')} submit\n")
            cmd = [sys.executable, ART_TOOLS / "donor_regen_jobs.py", "submit", "--jobs", *jobs, "--cap", str(cap)]
            r = _run(cmd + (["--dry-run"] if dry else []), root, log, 1200)
        out = r.stdout + r.stderr
        return {"rc": r.returncode, "filed": parse_filed(out), "tail": out.strip().splitlines()[-3:]}
    return submit


def tick(root: Path, low_water: int, cap: int, max_age_h: float, dry: bool, build=None, submit=None) -> dict:
    state_dir.require(root)                          # SystemExit: wrong machine / unset, never "empty queue"
    build = build or real_build(root)
    submit = submit or real_submit(root)
    rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "depth": depth(root), "low_water": low_water, "cap": cap,
           "dry_run": dry, "filed": 0, "jobs_list": None, "rebuilt": False}
    if rec["depth"] >= low_water:
        return _finish(root, rec, "BUSY", dry)
    (root / LIST_DIR).mkdir(exist_ok=True)
    with (root / LIST_DIR / ".lock").open("w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return _finish(root, rec, "LOCKED", dry)
        lst = newest_list(root)
        failed_recently = _failed_attempt_age(root)
        if failed_recently is not None and failed_recently < BUILD_BACKOFF_H * 3600:
            rec["build_backoff"] = f"last rebuild failed {failed_recently / 3600:.1f} h ago (< {BUILD_BACKOFF_H} h)"
            if lst is None:
                return _finish(root, rec, "BUILD_FAILED", dry)
        elif lst is None or time.time() - lst.stat().st_mtime > max_age_h * 3600:
            try:
                lst = build(root / LIST_DIR / time.strftime("%Y%m%d_%H%M%S"))
                rec["rebuilt"] = True
            except Exception as e:                   # noqa: BLE001 — fall back to the previous list, if any
                rec["build_error"] = f"{type(e).__name__}: {e}"
                if lst is None:
                    return _finish(root, rec, "BUILD_FAILED", dry)
        rec["jobs_list"] = str(lst)
        try:
            res = submit([lst], cap, dry)
        except Exception as e:                       # noqa: BLE001 — a hung/crashed submit still leaves a status
            rec["submit_error"] = f"{type(e).__name__}: {e}"
            return _finish(root, rec, "SUBMIT_FAILED", dry)
    rec["filed"] = int(res.get("filed") or 0)
    rec["submit_rc"] = res.get("rc")
    rec["depth_after"] = depth(root)
    tail = res.get("tail") or []
    if tail:
        rec["submit_tail"] = tail
    if rec["filed"] or (not dry and rec["depth_after"] > rec["depth"]):   # failed-pool requeues file no summary line
        action = "FED"
    elif any("backing off" in ln for ln in tail):
        action = "BACKOFF_429"
    elif res.get("rc"):
        action = "SUBMIT_FAILED"
    else:
        action = "NOTHING_OWED"
    return _finish(root, rec, action, dry)


def _failed_attempt_age(root: Path) -> float | None:
    """Seconds since the newest rebuild attempt, when that attempt left no jobs.json (it failed); else None.
    A census that fails (game folder unreachable) must not be retried every tick at ~11 min a try."""
    dirs = [d for d in (root / LIST_DIR).iterdir() if d.is_dir()]
    if not dirs:
        return None
    last = max(dirs, key=lambda d: d.stat().st_mtime)
    return None if (last / "jobs.json").is_file() else time.time() - last.stat().st_mtime


def _finish(root: Path, rec: dict, action: str, dry: bool) -> dict:
    rec["action"] = action
    if not dry:
        p = root / STATUS
        p.parent.mkdir(exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, indent=1))
        tmp.replace(p)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--state", type=Path, default=state_dir.STATE_ROOT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tick")
    t.add_argument("--low-water", type=int, default=3, help="feed only when fewer job files than this are in flight")
    t.add_argument("--cap", type=int, default=40, help="max job files pending+active after filing (submit's cap)")
    t.add_argument("--max-age-h", type=float, default=20, help="rebuild the owed list when older than this")
    t.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    if a.cmd == "status":
        p = a.state / STATUS
        print(p.read_text() if p.exists() else f"no {p}: idle_fill has never ticked here")
        return 0
    rec = tick(a.state, a.low_water, a.cap, a.max_age_h, a.dry_run)
    print(json.dumps(rec, indent=1))
    return 1 if rec["action"] in ("BUILD_FAILED", "SUBMIT_FAILED") else 0


if __name__ == "__main__":
    sys.exit(main())
