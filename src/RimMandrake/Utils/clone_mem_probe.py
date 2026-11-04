#!/usr/bin/env python3
"""clone_mem_probe.py — the memory one relentless clone costs, and who holds it.

Makes one clone exactly as relentless.py does (`scratch_clone.py clone ... --checkout --fetch`, RM_SEAT=clones) inside a
transient systemd user scope of its own, so the cgroup's memory.peak covers that clone and nothing else — the same counter
systemd shows as rm-relentless.service's MemoryPeak. It samples, every SAMPLE_S:
  - the scope's memory.current and memory.stat (anon vs file = page cache),
  - every process in the scope (VmRSS by command line), so the anon peak has a name.
Writes one JSON record per run under the agent storage root and prints a verdict. The clone is removed afterwards.

    clone_mem_probe.py [--runs N] [--keep] [--check]

--check exits 0 only while the attribution recorded in infrastructure/state/facts/clone_memory_peak.md still holds
(item RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK): the scope's peak is mostly page cache, not anon, and the largest anon
holder is a git process, not scratch_clone.py.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SAMPLE_S = 0.02
RM = Path(os.environ.get("RM_HOME", Path.home() / "rm"))
PROBE_ROOT = RM / "scratch" / "memprobe"   # ext4, beside the pool: the same filesystem a relentless clone is written to


def out_dir() -> Path:
    r = subprocess.run(["python3", str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True, timeout=30)
    if r.returncode or not r.stdout.strip():
        sys.exit("clone_mem_probe: agent storage root unknown: " + (r.stderr or r.stdout).strip())
    d = Path(r.stdout.strip()) / "rimmandrake" / "clone_mem_probe"
    d.mkdir(parents=True, exist_ok=True)
    return d


def own_cgroup() -> Path:
    line = Path("/proc/self/cgroup").read_text().strip().splitlines()[-1]
    return Path("/sys/fs/cgroup") / line.split(":", 2)[2].lstrip("/")


def mem_stat(cg: Path) -> dict:
    out = {}
    for ln in (cg / "memory.stat").read_text().splitlines():
        k, v = ln.split()
        if k in ("anon", "file", "file_dirty", "file_writeback", "shmem", "kernel", "sock"):
            out[k] = int(v)
    return out


def mem_available() -> int:
    for ln in Path("/proc/meminfo").read_text().splitlines():
        if ln.startswith("MemAvailable:"):
            return int(ln.split()[1]) * 1024
    return 0


def procs(cg: Path) -> list[tuple[int, str, int]]:
    """(pid, label, anon rss bytes) for every process in the scope. RssAnon, not VmRSS: a git that mmaps the store's
    packs shows gigabytes of VmRSS that are shared, reclaimable file pages (counted under the cgroup's `file`)."""
    rows = []
    for p in (cg / "cgroup.procs").read_text().split():
        try:
            cmd = Path(f"/proc/{p}/cmdline").read_bytes().split(b"\0")
            st = Path(f"/proc/{p}/status").read_text()
        except OSError:
            continue
        rss = next((int(ln.split()[1]) * 1024 for ln in st.splitlines() if ln.startswith("RssAnon:")), 0)
        argv = [a.decode(errors="replace") for a in cmd if a]
        label = label_of(argv)
        rows.append((int(p), label, rss))
    return rows


def label_of(argv: list[str]) -> str:
    if not argv:
        return "?"
    base = os.path.basename(argv[0])
    if base.startswith("python"):
        return "python " + os.path.basename(argv[1]) if len(argv) > 1 else "python"
    if base == "git" or base.startswith("git-"):
        sub = next((a for a in argv[1:] if not a.startswith("-") and "/" not in a), "")
        return ("git " + sub).strip() if base == "git" else base
    return base


def inner(args) -> int:
    """Runs inside the scope: one clone, sampled."""
    cg = own_cgroup()
    dest_root = PROBE_ROOT
    name = "probe-%s-%d" % (time.strftime("%Y%m%d-%H%M%S"), os.getpid())
    dest = dest_root / "clones" / name
    env = dict(os.environ, RM_SCRATCH_ROOT=str(dest_root), RM_SEAT="clones")
    cmd = ["python3", str(REPO / "src/RimMandrake/Utils/scratch_clone.py"), "clone", "relentless memprobe",
           "--name", name, "--checkout", "--fetch"]
    rec = {"cgroup": str(cg), "cmd": cmd, "dest": str(dest), "samples": 0,
           "peak_current": 0, "at_peak": {}, "max_anon": 0, "max_file": 0, "top_rss": {},
           "mem_available_start": mem_available(), "mem_available_min": mem_available()}
    stop = threading.Event()
    timeline = []

    def sample():
        t0 = time.time()
        while not stop.is_set():
            try:
                cur = int((cg / "memory.current").read_text())
                ms = mem_stat(cg)
                pr = procs(cg)
            except (OSError, ValueError):
                time.sleep(SAMPLE_S)
                continue
            rec["samples"] += 1
            rec["mem_available_min"] = min(rec["mem_available_min"], mem_available())
            if cur > rec["peak_current"]:
                rec["peak_current"] = cur
                rec["at_peak"] = dict(ms, t=round(time.time() - t0, 2),
                                      procs=sorted(((lbl, rss) for _, lbl, rss in pr), key=lambda x: -x[1])[:5])
            rec["max_anon"] = max(rec["max_anon"], ms.get("anon", 0))
            rec["max_file"] = max(rec["max_file"], ms.get("file", 0))
            for _, lbl, rss in pr:
                if rss > rec["top_rss"].get(lbl, 0):
                    rec["top_rss"][lbl] = rss
            if not timeline or time.time() - t0 - timeline[-1][0] >= 0.5:
                timeline.append((round(time.time() - t0, 2), cur, ms.get("anon", 0), ms.get("file", 0),
                                 max(pr, key=lambda x: x[2])[1] if pr else ""))
            time.sleep(SAMPLE_S)

    th = threading.Thread(target=sample, daemon=True)
    th.start()
    t0 = time.time()
    r = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True, timeout=500, stdin=subprocess.DEVNULL)
    rec["wall_s"] = round(time.time() - t0, 2)
    stop.set()
    th.join()
    rec["rc"] = r.returncode
    rec["stderr"] = r.stderr[-400:]
    rec["mem_available_end"] = mem_available()
    rec["memory_peak"] = int((cg / "memory.peak").read_text())   # kernel's own high-water mark, sampler-independent
    rec["timeline"] = timeline
    if not args.keep and dest.exists():
        shutil.rmtree(dest)
    Path(args.inner_out).write_text(json.dumps(rec, indent=1))
    return 0 if r.returncode == 0 else 1


def gb(b: int) -> str:
    return "%.2f GB" % (b / 2**30)


def verdict(rec: dict) -> tuple[bool, str]:
    top_anon = max(rec["top_rss"].items(), key=lambda kv: kv[1]) if rec["top_rss"] else ("?", 0)
    ap = rec["at_peak"]
    file_share = ap.get("file", 0) / max(1, rec["peak_current"])
    holds = file_share >= 0.6 and not top_anon[0].startswith("python")
    line = ("memory.peak %s (sampled %s at t=%ss: anon %s, file/page-cache %s = %d%%); max anon %s; "
            "largest anon process %s at %s RssAnon; host MemAvailable %s -> min %s -> end %s; wall %ss rc=%s"
            % (gb(rec["memory_peak"]), gb(rec["peak_current"]), ap.get("t"), gb(ap.get("anon", 0)),
               gb(ap.get("file", 0)), round(100 * file_share), gb(rec["max_anon"]), top_anon[0], gb(top_anon[1]),
               gb(rec["mem_available_start"]), gb(rec["mem_available_min"]), gb(rec["mem_available_end"]), rec["wall_s"], rec["rc"]))
    return holds, line


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--keep", action="store_true", help="leave the probe clone on disk")
    ap.add_argument("--check", action="store_true", help="exit 1 unless the recorded attribution still holds")
    ap.add_argument("--inner-out", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.inner_out:
        return inner(args)
    od = out_dir()
    ok_all = True
    for i in range(args.runs):
        out = od / ("run-%s-%d.json" % (time.strftime("%Y%m%dT%H%M%S"), i))
        unit = "rm-cloneprobe-%d-%d" % (os.getpid(), i)
        cmd = ["systemd-run", "--user", "--scope", "-q", "--unit", unit, "-p", "MemoryAccounting=yes", "--",
               sys.executable, str(Path(__file__).resolve()), "--inner-out", str(out)] + (["--keep"] if args.keep else [])
        r = subprocess.run(cmd, cwd=REPO, timeout=530)
        if not out.exists():
            print("clone_mem_probe: run %d left no record (rc=%s)" % (i, r.returncode))
            return 2
        rec = json.loads(out.read_text())
        if rec["rc"]:
            print("clone_mem_probe: clone failed: " + rec["stderr"])
            return 2
        holds, line = verdict(rec)
        ok_all &= holds
        print("run %d: %s\n  record: %s" % (i, line, out))
    if args.check:
        print("ATTRIBUTION HOLDS" if ok_all else "ATTRIBUTION CHANGED: re-measure and rewrite "
              "infrastructure/state/facts/clone_memory_peak.md")
        return 0 if ok_all else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
