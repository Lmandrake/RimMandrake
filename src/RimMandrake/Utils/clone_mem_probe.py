#!/usr/bin/env python3
"""clone_mem_probe.py — the memory one relentless clone costs, and who holds it.

Makes one clone exactly as relentless.py does (`scratch_clone.py clone ... --checkout --fetch`, RM_SEAT=clones) inside a
transient systemd user scope of its own, so the cgroup's memory.peak covers that clone and nothing else — the same counter
systemd shows as rm-relentless.service's MemoryPeak. It samples, every SAMPLE_S:
  - the scope's memory.current and memory.stat (anon vs file = page cache),
  - every process in the scope (VmRSS by command line), so the anon peak has a name.
Writes one JSON record per run under the agent storage root and prints a verdict. The clone is removed afterwards.

    clone_mem_probe.py [--runs N] [--keep] [--check] [--private-store] [--no-fetch]

--check exits 0 only while the attribution recorded in infrastructure/state/facts/clone_memory_peak.md still holds
(item RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK): the scope's peak is mostly page cache, not anon, and the largest anon
holder is a git process, not scratch_clone.py. Exit 2 = UNMEASURED (no scope, clone failed, or the instrument saw too
little to judge).

It runs where the live store, GitHub or Lodestar cannot be reached (a blind checker's sandbox), and says which it used:
  - record dir: $RM_PROBE_OUT, else <agent storage>/rimmandrake/clone_mem_probe, else a fresh dir under $TMPDIR;
  - store: the live store (RM_OBJSTORE or ~/rm/store.git) when readable, else (or with --private-store) a private store
    seeded OUTSIDE the measured scope from this checkout's HEAD tree, so its packs are not charged to the clone;
  - --fetch (as relentless passes it) only when the live store is used and origin answers within 30 s.
The checkout — `git read-tree -mu HEAD` writing the whole worktree — is the same in every mode, and it is what is measured.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SAMPLE_S = 0.02
RM = Path(os.environ.get("RM_HOME", Path.home() / "rm"))
PROBE_ROOT = RM / "scratch" / "memprobe"   # ext4, beside the pool: the same filesystem a relentless clone is written to


def out_dir() -> tuple[Path, str]:
    if os.environ.get("RM_PROBE_OUT"):
        d = Path(os.environ["RM_PROBE_OUT"])
        d.mkdir(parents=True, exist_ok=True)
        return d, "RM_PROBE_OUT"
    why = ""
    try:
        r = subprocess.run(["python3", str(Path.home() / "dev/Lodestar/bin/lib/agent_storage.py")],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            d = Path(r.stdout.strip()) / "rimmandrake" / "clone_mem_probe"
            d.mkdir(parents=True, exist_ok=True)
            return d, "agent storage"
        why = (r.stderr or r.stdout).strip()[-200:]
    except (OSError, subprocess.SubprocessError) as e:
        why = str(e)[:200]
    return Path(tempfile.mkdtemp(prefix="clone_mem_probe-")), "TMPDIR (agent storage unreachable: %s)" % why


def git_ok(*args, cwd=None, timeout=60) -> bool:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, timeout=timeout,
                              stdin=subprocess.DEVNULL).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def run_git(*args, cwd=None, env=None, timeout=480) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout,
                       stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args[:3]), (r.stderr or r.stdout).strip()[-300:]))
    return r.stdout.strip()


def live_store() -> Path:
    return Path(os.environ.get("RM_OBJSTORE", RM / "store.git"))


def live_store_readable() -> bool:
    st = live_store()
    return git_ok("--git-dir", str(st), "rev-parse", "--verify", "-q", "refs/heads/main^{tree}", timeout=30)


def private_root() -> Path:
    """Beside the pool when writable (same ext4 a relentless clone is written to), else TMPDIR."""
    try:
        PROBE_ROOT.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="private-", dir=PROBE_ROOT))
    except OSError:
        return Path(tempfile.mkdtemp(prefix="clone_mem_probe-private-"))


def seed_private(root: Path) -> tuple[Path, str]:
    """A bare seed repo holding one parentless commit of this checkout's tree, in mirror.git's ref layout, built
    BEFORE the scope starts. From this checkout's objects when git can read them, else from its files (git add)."""
    seed = root / "seed.git"
    run_git("init", "-q", "--bare", "-b", "main", str(seed))
    objs = Path(run_git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=REPO)) / "objects" \
        if git_ok("rev-parse", "--git-dir", cwd=REPO) else None
    env = dict(os.environ, GIT_AUTHOR_NAME="clone_mem_probe", GIT_AUTHOR_EMAIL="probe@localhost",
               GIT_COMMITTER_NAME="clone_mem_probe", GIT_COMMITTER_EMAIL="probe@localhost")
    how = ""
    if objs and git_ok("cat-file", "-e", "HEAD^{tree}", cwd=REPO):
        tree = run_git("rev-parse", "HEAD^{tree}", cwd=REPO)
        (seed / "objects" / "info" / "alternates").write_text(str(objs) + "\n")
        try:
            tip = run_git("--git-dir", str(seed), "commit-tree", tree, "-m", "clone_mem_probe seed", env=env)
            run_git("--git-dir", str(seed), "update-ref", "refs/remotes/origin/main", tip)
            run_git("--git-dir", str(seed), "repack", "-a", "-d", "-q")
            (seed / "objects" / "info" / "alternates").unlink()
            run_git("--git-dir", str(seed), "cat-file", "-e", tip + "^{tree}")
            how = "this checkout's HEAD tree %s (repacked from its objects)" % tree[:10]
        except RuntimeError as e:
            alt = seed / "objects" / "info" / "alternates"
            if alt.exists():
                alt.unlink()
            how = "objects unusable (%s); " % str(e)[:120]
    if not how.startswith("this"):
        idx = root / "seed.index"
        genv = dict(env, GIT_INDEX_FILE=str(idx))
        run_git("--git-dir", str(seed), "--work-tree", str(REPO), "add", "-A", ".", cwd=REPO, env=genv, timeout=480)
        tree = run_git("--git-dir", str(seed), "write-tree", env=genv)
        tip = run_git("--git-dir", str(seed), "commit-tree", tree, "-m", "clone_mem_probe seed", env=genv)
        run_git("--git-dir", str(seed), "update-ref", "refs/remotes/origin/main", tip)
        idx.unlink()
        how += "this checkout's files, git add (tree %s)" % tree[:10]
    return seed, how


def origin_answers() -> bool:
    return git_ok("ls-remote", "--heads", "origin", "main", cwd=REPO, timeout=30)


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
    dest_root = Path(os.environ.get("RM_PROBE_SCRATCH", PROBE_ROOT))
    name = "probe-%s-%d" % (time.strftime("%Y%m%d-%H%M%S"), os.getpid())
    dest = dest_root / "clones" / name
    env = dict(os.environ, RM_SCRATCH_ROOT=str(dest_root), RM_SEAT="clones")
    cmd = ["python3", str(REPO / "src/RimMandrake/Utils/scratch_clone.py"), "clone", "relentless memprobe",
           "--name", name, "--checkout"] + (["--fetch"] if args.fetch else [])
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


MIN_SAMPLES = 20          # fewer and the sampler cannot have seen the checkout (it runs ~10 s)
MIN_PEAK = 300 * 2**20    # a full checkout writes ~3.8 GB; a scope peak under this means the scope missed it


def verdict(rec: dict) -> tuple[bool | None, str]:
    """(True holds | False changed | None unmeasured, line). Holds: >= 60 % of the sampled peak is page cache and the
    largest anon (RssAnon) holder over the run is a git process."""
    top_anon = max(rec["top_rss"].items(), key=lambda kv: kv[1]) if rec["top_rss"] else ("?", 0)
    ap = rec["at_peak"]
    file_share = ap.get("file", 0) / max(1, rec["peak_current"])
    if rec.get("samples", 0) < MIN_SAMPLES or rec.get("memory_peak", 0) < MIN_PEAK:
        holds = None
    else:
        holds = file_share >= 0.6 and top_anon[0].startswith("git")
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
    ap.add_argument("--private-store", action="store_true", help="seed a private store from this checkout even when "
                    "the live store is readable")
    ap.add_argument("--no-fetch", action="store_true", help="never fetch origin (relentless passes --fetch)")
    ap.add_argument("--inner-out", help=argparse.SUPPRESS)
    ap.add_argument("--fetch", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.inner_out:
        return inner(args)
    od, od_why = out_dir()
    print("records: %s (%s)" % (od, od_why))
    priv = None
    env = dict(os.environ)
    fetch = False
    try:
        if args.private_store or not live_store_readable():
            priv = private_root()
            t0 = time.time()
            try:
                seed, how = seed_private(priv)
            except (RuntimeError, OSError, subprocess.SubprocessError) as e:
                print("UNMEASURED: could not seed a private store from %s: %s" % (REPO, str(e)[:300]))
                return 2
            env.update(RM_OBJSTORE=str(priv / "store.git"), RM_OBJSTORE_SEED=str(seed),
                       RM_OBJSTORE_STATE=str(priv / "state"), RM_OBJSTORE_SCAN=str(priv / "none"),
                       RM_PROBE_SCRATCH=str(priv))
            print("store: PRIVATE, seeded outside the scope in %.0f s from %s%s" % (
                time.time() - t0, how, "" if args.private_store else " (live store %s unreadable)" % live_store()))
        else:
            fetch = not args.no_fetch and origin_answers()
            print("store: live %s; fetch %s" % (live_store(), "on, as relentless" if fetch else
                                                "OFF (%s)" % ("--no-fetch" if args.no_fetch else "origin did not answer")))
        return measure(args, od, env, fetch)
    finally:
        if priv and not args.keep:
            shutil.rmtree(priv, ignore_errors=True)


def measure(args, od: Path, env: dict, fetch: bool) -> int:
    ok_all: bool | None = True
    for i in range(args.runs):
        out = od / ("run-%s-%d.json" % (time.strftime("%Y%m%dT%H%M%S"), i))
        unit = "rm-cloneprobe-%d-%d" % (os.getpid(), i)
        cmd = ["systemd-run", "--user", "--scope", "-q", "--unit", unit, "-p", "MemoryAccounting=yes", "--",
               sys.executable, str(Path(__file__).resolve()), "--inner-out", str(out)] + (
               ["--keep"] if args.keep else []) + (["--fetch"] if fetch else [])
        try:
            r = subprocess.run(cmd, cwd=REPO, env=env, timeout=530)
        except (OSError, subprocess.SubprocessError) as e:
            print("UNMEASURED: no scope of its own: systemd-run --user failed: %s" % e)
            return 2
        if not out.exists():
            print("UNMEASURED: run %d left no record (systemd-run rc=%s; a user scope is needed so memory.peak is "
                  "this clone alone)" % (i, r.returncode))
            return 2
        rec = json.loads(out.read_text())
        if rec["rc"]:
            print("UNMEASURED: clone failed: " + rec["stderr"])
            return 2
        holds, line = verdict(rec)
        if holds is None:
            ok_all = None
        elif ok_all is not None:
            ok_all = ok_all and holds
        print("run %d: %s\n  record: %s" % (i, line, out))
    if args.check:
        if ok_all is None:
            print("UNMEASURED: the scope saw under %d samples or a peak under %s; the instrument did not see the "
                  "checkout" % (MIN_SAMPLES, gb(MIN_PEAK)))
            return 2
        print("ATTRIBUTION HOLDS" if ok_all else "ATTRIBUTION CHANGED: re-measure and rewrite "
              "infrastructure/state/facts/clone_memory_peak.md")
        return 0 if ok_all else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
