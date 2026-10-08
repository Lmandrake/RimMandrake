#!/usr/bin/env python3
"""Run every selftest in the repo in parallel and print an explicit N/N summary.

Replaces the serial `for f in $(find src -name selftest_*.py); do python3 "$f" ...`
loop, which was silently truncated by the 120s tool timeout once the sweep grew past
it (SELFTEST_SWEEP_EXCEEDS_COMMIT_BUDGET_1) — a killed run printed only the FAILs it
had reached so far, indistinguishable from a real all-pass.

selftest_render.py carries its own hard wall-clock budget (bench() targets 100ms) and
goes flaky under the CPU/IO contention of a parallel sweep — it runs ISOLATED, after
the parallel pool, with nothing else in flight. Nothing else in the suite has a
timing-sensitive assertion (checked 2026-09-03); if a future one does, add its
basename to SEQUENTIAL_ISOLATED rather than raising the worker count to paper over it.

selftest_cli.py is the long pole (~150s+ solo — 87 real subprocess spawns, deliberately
not in-process, see that file's own docstring) and is NOT parallelized internally here;
that's real, separate surgery (PARALLELIZE_SELFTEST_CLI_INTERNAL_1), not a rider on this
fix. It still runs inside the shared pool since it has no timing assertion of its own to
protect from contention.

🔑 Discovery is `selftest*.py` — NOT `selftest_*.py` — over SEARCH_ROOTS. The narrower
glob silently skipped every selftest named plainly `selftest.py` (rimbench's and
rimplace's), and the `src/`-only root silently skipped all nine `.claude/hooks/`
selftests: 12 files, 10 of them green and runnable, that "run every selftest before a
commit" was never running. A selftest that cannot run as bare `python3 <file>` is named
in NOT_STANDALONE with its real invocation, so it is a VISIBLE `SKIPPED` line rather
than a glob miss nobody can see.

🔴 MEMORY PEN (2026-10-08, SEAT_MEMORY_CLONES_DRIVES_1). Every test runs in its OWN
transient scope inside `rm-harness.slice` (12G, a sibling of claude.slice — never inside
the Claude seat that launched the run), with a per-test MemoryMax and no swap. A
16-worker in-seat fan-out repeatedly filled the seat's 10G cap and the kernel killed
Claude itself. The runner FAILS CLOSED: a probe must land under rm-harness.slice with a
numeric memory.max, and every test's wrapper re-checks /proc/self/cgroup before it runs
the test at all. If containment is unavailable, the run drops to ONE worker in the
caller and the summary says NOT CONTAINED. A test killed by its cap is KILLED, never a
pass. Admission reads the slice's live memory (memory.current minus reclaimable
inactive file cache) plus the recorded memory.peak of what is starting — never a lock
file or counter, which leaks on SIGKILL (design doc §8 #10).
"""
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PER_TEST_TIMEOUT_S = 240
# A test that legitimately outlasts that (one that walks every deployed mod on
# the drvfs mount) declares its own cap in its first 40 lines, e.g.
#   # selftest-timeout: 600
# so the runner does not report a 367 s PASS as a TIMEOUT (2026-09-23).
_TIMEOUT_TAG = re.compile(r"^#\s*selftest-timeout:\s*(\d+)", re.M)


def per_test_timeout(path: Path) -> int:
    try:
        head = "".join(path.open(encoding="utf-8", errors="replace").readlines()[:40])
    except OSError:
        return PER_TEST_TIMEOUT_S
    m = _TIMEOUT_TAG.search(head)
    return int(m.group(1)) if m else PER_TEST_TIMEOUT_S
# The phrase a child prints when it could not run at all (a toolchain this
# machine lacks, a game that is not up) rather than when something is wrong.
# It is a convention the children already follow verbatim — grep it before
# changing this string.
UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"
SEQUENTIAL_ISOLATED = {"selftest_render.py"}
# Tests that load the large def dump: each passes alone but several at once (plus the
# 16-worker pool) get SIGKILLed by the OOM killer with no output (SELFTEST_RUNNER_SILENT_OOM_1).
# Serializing them among themselves was measured NOT enough (the Utinni one still died at ~17 s beside the
# 16-worker pool) IN A SEAT. Contained in rm-harness.slice they run one at a time in a lane beside the
# admission-gated pool (peaks 2.1-4.4 GB, 2026-10-08); uncontained they run after it, alone.
MEMORY_HEAVY = {"selftest_starwarspatches_semantics.py", "selftest_utinnipatches_dump.py",
                "selftest_mandrakepatches.py"}
# Per-test wall times from the previous run (path -> seconds). Used ONLY to start the
# slowest tests first (longest-processing-time scheduling), so the long pole overlaps
# everything else instead of starting last. Never read for a verdict. Lives in /tmp:
# a program reads it, not a human.
TIMINGS_FILE = Path(os.environ.get("SELFTEST_TIMINGS_FILE",
                                   Path(os.environ.get("TMPDIR", "/tmp")) / "selftest_timings.json"))
# Per-test memory.peak (bytes) from the previous contained run, beside the timings. Sizes
# admission and each test's cap; never read for a verdict.
PEAKS_FILE = TIMINGS_FILE.with_name("selftest_peaks.json")
# Contained worker count. MEASURED 2026-10-08 from a BENCH seat: 338 tests, 6 workers 298 s,
# 8 workers 307 s (the one-at-a-time heavy lane and modcheck's ~106 s are the pole, not width).
# Outside the slice it is ALWAYS 1: the seat's 10G must hold Claude, not a test fan-out.
DEFAULT_WORKERS = 6

HARNESS_SLICE = "rm-harness.slice"
GiB = 1 << 30
CAP_UNKNOWN = 6 * GiB       # a test with no recorded peak
CAP_MIN, CAP_MAX = 3 * GiB, 10 * GiB   # known peak p -> clamp(2p)
CAP_ISOLATED = 10 * GiB     # one-at-a-time tests get nearly the whole pen
EST_UNKNOWN = 1 * GiB       # admission estimate for a test with no recorded peak (most use <100 MB)
EST_HEAVY_UNKNOWN = 6 * GiB  # ...and for a MEMORY_HEAVY one (single tests reach 5.1 GB)
HEADROOM = 2 * GiB          # admit only while projected use <= slice max - this
_MARKER = "@@RM_HARNESS "   # the wrapper's one-line JSON report on stderr
_PLACEMENT_RC = 97          # wrapper refused: not under rm-harness.slice


def load_peaks() -> dict:
    try:
        return json.loads(PEAKS_FILE.read_text())
    except (OSError, ValueError):
        return {}


def load_timings() -> dict:
    try:
        return json.loads(TIMINGS_FILE.read_text())
    except (OSError, ValueError):
        return {}


def save_timings(results) -> None:
    old = load_timings()
    for path, status, elapsed, _ in results:
        if status in ("PASS", "FAIL", "UNMEASURED"):  # a TIMEOUT time is the cap, not a measurement
            old[path.relative_to(REPO_ROOT).as_posix()] = round(elapsed, 1)
    try:
        TIMINGS_FILE.write_text(json.dumps(old, indent=0, sort_keys=True))
    except OSError:
        pass
SEARCH_ROOTS = ("src", ".claude/hooks", "skills", "infrastructure/dashboards/hub")
SELFTEST_GLOB = "selftest*.py"

# Selftests that exist and are real, but cannot be run as bare `python3 <file>`.
# Excluding one here is a deliberate, VISIBLE act — it prints as SKIPPED with this
# reason. A key naming no discovered file is a hard error, so a rename cannot quietly
# turn an exclusion into a permanent disappearance.
NOT_STANDALONE: dict[str, str] = {}

# Lints the suite must always carry: a rename or move that drops one out of discovery is a hard error.
# selftest_placeholder_lint.py — no shipped def draws a geometric placeholder (owner rule 2026-10-07 22:33 PDT).
REQUIRED = {"src/RimMandrake/Utils/art/selftest_placeholder_lint.py"}

RIMLUA_PY = Path.home() / ".local/venvs/rimlua/bin/python"
RIMLUA_FIX = ("python3 -m venv ~/.local/venvs/rimlua && "
              "~/.local/venvs/rimlua/bin/pip install lupa")
SPRITE_REFERENCE = ("src/RimMandrake/Pyrinth/Textures/Things/Item/Resource/"
                    "Pyrinth/Pyrinth_a.png")

# Selftests that cannot run as bare `python3 <file>` from the repo root: rel path ->
# (argv builder, cwd). A missing prerequisite is a visible FAIL, never a skip.
def _rimplace():
    if not RIMLUA_PY.exists():
        raise FileNotFoundError(f"{RIMLUA_PY} missing (rimplace needs lupa) — create it: {RIMLUA_FIX}")
    return [str(RIMLUA_PY), "-m", "rimplace", "selftest"], REPO_ROOT / "src/RimMandrake/Utils"


def _sprite():
    ref = REPO_ROOT / SPRITE_REFERENCE
    if not ref.exists():
        raise FileNotFoundError(f"committed reference PNG missing: {ref}")
    return [sys.executable, str(REPO_ROOT / "skills/generating-rimworld-sprites/scripts/selftest.py"),
            "--reference", str(ref)], REPO_ROOT


SPECIAL_INVOCATIONS = {
    "src/RimMandrake/Utils/rimplace/selftest.py": _rimplace,
    "skills/generating-rimworld-sprites/scripts/selftest.py": _sprite,
}


def find_selftests() -> tuple[list[Path], list[tuple[Path, str]]]:
    """Return (runnable, [(path, why_skipped)]) — every selftest file, classified."""
    found: set[Path] = set()
    for root in SEARCH_ROOTS:
        found.update((REPO_ROOT / root).rglob(SELFTEST_GLOB))
    runnable, excluded = [], []
    for path in sorted(found):
        why = NOT_STANDALONE.get(path.relative_to(REPO_ROOT).as_posix())
        (excluded.append((path, why)) if why else runnable.append(path))
    return runnable, excluded


# --- the memory pen ---------------------------------------------------------------
# _HARNESS is None when uncontained (fallback / Mac / selftest fixtures), else a dict:
# {"slice_cg": "/sys/fs/cgroup/.../rm.slice/rm-harness.slice", "max": bytes}.
_HARNESS = None
_RUNNING: dict = {}          # Popen pid -> (estimate bytes) for tests in flight
_PEAK_SEEN: dict = {}        # rel path -> memory.peak bytes reported by its wrapper
_SEQ = [0]


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:  # a fixture outside the repo (selftest_run_selftests.py)
        return ""


def _read_int(p: str):
    try:
        v = open(p).read().strip()
        return int(v) if v.isdigit() else None
    except OSError:
        return None


def _kv(p: str) -> dict:
    try:
        return {k: int(v) for k, v in (ln.split() for ln in open(p) if ln.strip())}
    except (OSError, ValueError):
        return {}


def _cgroup_of(pid) -> str:
    """The unified-hierarchy cgroup path of pid, or '' if unreadable."""
    try:
        for ln in open(f"/proc/{pid}/cgroup"):
            if ln.startswith("0::"):
                return ln[3:].strip()
    except OSError:
        pass
    return ""


def _in_harness(cg: str) -> bool:
    return f"/{HARNESS_SLICE}/" in cg + "/"


def _harness_child(argv: list) -> int:
    """Runs INSIDE a test's scope: refuse unless placed in the pen, run the test, then
    report the scope's own memory.events/peak on stderr so the runner can tell a cap kill
    from a failure. The scope dies with us, so this is the only moment that can be read."""
    cg = _cgroup_of("self")
    if not _in_harness(cg):
        print(_MARKER + json.dumps({"placement": cg, "ok": False}), file=sys.stderr, flush=True)
        return _PLACEMENT_RC
    rc = subprocess.call(argv) if argv else 0
    base = "/sys/fs/cgroup" + cg
    ev = _kv(base + "/memory.events")
    rep = {"ok": True, "placement": cg, "oom_kill": ev.get("oom_kill", 0),
           "max_events": ev.get("max", 0), "peak": _read_int(base + "/memory.peak"),
           "cap": _read_int(base + "/memory.max"), "rc": rc}
    print(_MARKER + json.dumps(rep), file=sys.stderr, flush=True)
    return rc if rc >= 0 else 128 - rc


def _split_marker(err: str):
    """(stderr without the wrapper's line, its report dict or None)."""
    rep, keep = None, []
    for ln in err.splitlines(keepends=True):
        if ln.startswith(_MARKER):
            try:
                rep = json.loads(ln[len(_MARKER):])
            except ValueError:
                keep.append(ln)
        else:
            keep.append(ln)
    return "".join(keep), rep


def _install_slice() -> None:
    src = Path(__file__).resolve().with_name(HARNESS_SLICE)
    dst = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "systemd/user" / HARNESS_SLICE
    try:
        if src.is_file() and (not dst.is_file() or dst.read_bytes() != src.read_bytes()):
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
            subprocess.run(["systemctl", "--user", "daemon-reload"], timeout=30,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass  # the probe below decides; a failed install just means NOT CONTAINED


def _scope_argv(cap: int, timeout: int, inner: list) -> list:
    _SEQ[0] += 1
    return ["systemd-run", "--user", "--scope", "--quiet", f"--slice={HARNESS_SLICE}",
            f"--unit=rm-harness-{os.getpid()}-{_SEQ[0]}",
            "-p", "MemoryAccounting=yes", "-p", f"MemoryMax={cap}", "-p", "MemorySwapMax=0",
            # continue: an OOM kill of the test must not stop the scope and take the
            # wrapper (our only reporter) with it. RuntimeMaxSec: if this runner is
            # SIGKILLed, systemd still reaps the orphan at its timeout.
            "-p", "OOMPolicy=continue", "-p", f"RuntimeMaxSec={timeout + 60}",
            "--", sys.executable, str(Path(__file__).resolve()), "--_harness-child", "--", *inner]


def probe_harness():
    """Return (harness dict, None) if a scope really lands in a BOUNDED rm-harness.slice,
    else (None, why). Fails closed: anything unexpected is a reason, not a guess."""
    if os.environ.get("RM_SELFTEST_NO_HARNESS"):
        return None, "RM_SELFTEST_NO_HARNESS set"
    if not Path("/sys/fs/cgroup/cgroup.controllers").exists():
        return None, "no cgroup v2 here"
    _install_slice()
    try:
        p = subprocess.run(_scope_argv(256 << 20, 30, []), capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"systemd-run unavailable ({type(exc).__name__}: {exc})"
    _, rep = _split_marker(p.stderr)
    if not rep:
        return None, f"probe scope did not start (rc {p.returncode}: {p.stderr.strip()[-200:]})"
    if not rep.get("ok"):
        return None, f"probe landed OUTSIDE {HARNESS_SLICE}: {rep.get('placement')}"
    slice_cg = "/sys/fs/cgroup" + rep["placement"].rsplit("/", 1)[0]
    mx = _read_int(slice_cg + "/memory.max")
    if not mx:
        return None, f"{slice_cg}/memory.max is not a number — the slice is UNBOUNDED"
    return {"slice_cg": slice_cg, "max": mx}, None


def _slice_in_use() -> int:
    """Live working set of the whole pen (ours AND any other runner's): memory.current
    minus inactive file cache, which the kernel reclaims before it OOM-kills."""
    cur = _read_int(_HARNESS["slice_cg"] + "/memory.current") or 0
    return max(0, cur - _kv(_HARNESS["slice_cg"] + "/memory.stat").get("inactive_file", 0))


def estimate(path: Path, peaks: dict) -> int:
    p = peaks.get(_rel(path))
    if p:
        return int(p * 1.25)
    return EST_HEAVY_UNKNOWN if path.name in MEMORY_HEAVY else EST_UNKNOWN


def cap_for(path: Path, peaks: dict, isolated: bool) -> int:
    if isolated:
        return min(CAP_ISOLATED, _HARNESS["max"])
    p = peaks.get(_rel(path))
    return max(CAP_MIN, min(CAP_MAX, 2 * p)) if p else CAP_UNKNOWN


def admit(est: int) -> bool:
    """Room for one more test of size est? Always yes when nothing of ours is running."""
    if not _RUNNING:
        return True
    pending = 0
    for pid, e in list(_RUNNING.items()):
        cg = _cgroup_of(pid)
        cur = _read_int(f"/sys/fs/cgroup{cg}/memory.current") if cg else None
        pending += max(0, e - (cur or 0))  # reserved but not yet touched
    return _slice_in_use() + pending + est <= _HARNESS["max"] - HEADROOM


def _run_capped(path: Path, timeout: int, cap: int = 0, est: int = 0):
    """subprocess.run, but a timeout kills the child's whole scope / PROCESS GROUP.

    Plain subprocess.run(timeout=) kills only the direct child; a grandchild (a grep,
    a dotnet, a nested python) keeps the stdout pipe open and communicate() then blocks
    until IT exits -- so a "240 s" timeout could silently take far longer.
    Returns (CompletedProcess, wrapper report or None).
    """
    special = SPECIAL_INVOCATIONS.get(_rel(path))
    argv, cwd = special() if special else ([sys.executable, str(path)], REPO_ROOT)
    if _HARNESS:
        argv = _scope_argv(cap, timeout, argv)
    p = subprocess.Popen(argv, cwd=cwd, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    _RUNNING[p.pid] = est
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        cg = _cgroup_of(p.pid)
        if _HARNESS and _in_harness(cg):
            try:
                Path(f"/sys/fs/cgroup{cg}/cgroup.kill").write_text("1")
            except OSError:
                pass
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        p.communicate()
        raise
    finally:
        _RUNNING.pop(p.pid, None)
    err, rep = _split_marker(err)
    return subprocess.CompletedProcess(p.args, p.returncode, out, err), rep


def run_one(path: Path, cap: int = 0, est: int = 0) -> tuple[Path, str, float, str]:
    start = time.monotonic()
    try:
        proc, rep = _run_capped(path, per_test_timeout(path), cap, est)
        elapsed = time.monotonic() - start
        if _HARNESS:
            if not rep:
                return path, "ERROR", elapsed, ("contained run gave no wrapper report (rc "
                                                f"{proc.returncode}): {proc.stderr.strip()[-400:]}")
            if not rep.get("ok"):
                return path, "PLACEMENT", elapsed, (f"refused to run: landed in {rep.get('placement')}, "
                                                    f"not {HARNESS_SLICE}")
            if rep.get("peak"):
                _PEAK_SEEN[_rel(path)] = rep["peak"]
            if rep.get("oom_kill"):
                # Never a pass, even at rc 0: something in its scope died to the cap.
                tail = (proc.stdout + proc.stderr).strip().splitlines()[-20:]
                return path, "KILLED", elapsed, "\n".join(tail + [
                    f"KILLED by memory cap: oom_kill={rep['oom_kill']} in its scope, "
                    f"peak {rep.get('peak', 0) / GiB:.2f} GiB, cap {(rep.get('cap') or cap) / GiB:.2f} GiB, "
                    f"rc {proc.returncode}"])
        if proc.returncode == 0:
            return path, "PASS", elapsed, ""
        out = proc.stdout + proc.stderr
        rc = proc.returncode
        if rc < 0 or rc in (137, 139):  # killed by a signal: say so, never a silent FAIL
            sig = -rc if rc < 0 else rc - 128
            out += (f"\nKILLED by signal {sig} (rc={rc}) - SIGKILL(9) is almost always the OOM "
                    "killer; rerun this test alone before believing it is a real failure")
        tail = out.strip().splitlines()[-40:]
        # UNMEASURED is not FAILED. A child that could not run at all — no
        # Windows-side dotnet.exe here, no live game — says so with the phrase
        # below and exits non-zero, and printing that identically to a real
        # failure is how a suite stops being read (11 red of 57 on macOS,
        # 6 of them unrunnable). The `FAIL` guard is what keeps an unmeasured
        # sub-check from masking a genuine failure in the same file:
        # selftest_codebase_health.py PASSES while discussing UNMEASURED, so the
        # verdict is read from the child's OUTPUT and exit code, never its source.
        if UNMEASURED_PHRASE in out and "FAIL" not in out:
            return path, "UNMEASURED", elapsed, "\n".join(tail)
        return path, "FAIL", elapsed, "\n".join(tail)
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return path, "TIMEOUT", elapsed, f"exceeded {per_test_timeout(path)}s"
    except Exception as exc:  # harness-side failure: OSError, ENOMEM, bad interpreter
        # Never let this escape into as_completed — one raised future would abort the
        # whole loop and print NO summary at all, which is the truncation this file
        # exists to prevent. Report it as a named non-PASS instead.
        elapsed = time.monotonic() - start
        return path, "ERROR", elapsed, f"{type(exc).__name__}: {exc}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=None,
                    help=f"contained default {DEFAULT_WORKERS}; forced to 1 when NOT CONTAINED")
    ap.add_argument("--timings", action="store_true",
                    help="print the 10 slowest tests after the summary")
    ap.add_argument("--only", nargs="+", metavar="PATH",
                    help="run just these selftest files (still contained, still N/N)")
    args = ap.parse_args()

    global _HARNESS
    _HARNESS, why_not = probe_harness()
    if _HARNESS:
        workers = args.workers or DEFAULT_WORKERS
        contain_note = (f"contained in {HARNESS_SLICE} (max {_HARNESS['max'] / GiB:.0f}G), "
                        f"{workers} workers")
    else:
        workers = 1
        contain_note = (f"NOT CONTAINED ({why_not}) — ran in the caller's cgroup with 1 worker"
                        + (f", --workers {args.workers} IGNORED" if (args.workers or 1) > 1 else ""))
    print(contain_note, file=sys.stderr, flush=True)
    peaks = load_peaks()

    tests, excluded = find_selftests()
    if not tests:
        print(f"no {SELFTEST_GLOB} found under {', '.join(SEARCH_ROOTS)} — "
              "that itself is suspicious")
        return 1

    if args.only:
        want = {Path(o).resolve() for o in args.only}
        tests = [t for t in tests if t.resolve() in want]
        # a file outside discovery (e.g. a planted fixture) is still run when named
        tests += sorted(w for w in want if w.is_file() and w not in {t.resolve() for t in tests})
        excluded = []
    missing = set() if args.only else REQUIRED - {p.resolve().as_posix()[len(str(REPO_ROOT.resolve())) + 1:] for p in tests}
    if missing:
        print("REQUIRED lint selftest(s) not discovered: " + ", ".join(sorted(missing)))
        return 1

    stale = set() if args.only else set(NOT_STANDALONE) - {p.relative_to(REPO_ROOT).as_posix()
                                   for p, _ in excluded}
    if stale:
        print("NOT_STANDALONE names files that no longer exist — a rename would "
              "otherwise silently drop or re-add a selftest: " + ", ".join(sorted(stale)))
        return 1

    # Contained, MEMORY_HEAVY joins the admission-gated pool as a one-at-a-time lane with
    # its peak reserved and a near-whole-pen cap: its isolation was only ever about memory,
    # and admission now provides that (serial tail was ~200 s of a ~6 min run).
    # SEQUENTIAL_ISOLATED is about CPU timing, so it still runs alone at the end.
    ISOLATED = SEQUENTIAL_ISOLATED | (set() if _HARNESS else MEMORY_HEAVY)
    pooled = [t for t in tests if t.name not in ISOLATED]
    isolated = [t for t in tests if t.name in ISOLATED]

    # Slowest-first (from last run's timings); unknown tests go first too, so a new
    # slow test cannot become the tail.
    prior = load_timings()
    pooled.sort(key=lambda t: -prior.get(t.relative_to(REPO_ROOT).as_posix(), 1e9))

    results = []
    wall_start = time.monotonic()
    total = len(tests)

    def _progress(r):
        # Live line per finished test (flushed) so a long run is never silent.
        results.append(r)
        print(f"[{len(results)}/{total}] {r[1]:10s} {r[2]:6.1f}s  "
              f"{r[0].relative_to(REPO_ROOT)}", file=sys.stderr, flush=True)

    if _HARNESS:
        # Admission-gated pool: start the first queued test (slowest-first) whose
        # recorded peak fits the pen's LIVE headroom; with nothing of ours running,
        # always start one so a test bigger than the budget still runs, alone.
        queue = list(pooled)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            inflight, heavy = set(), {}
            while queue or inflight:
                while queue and len(inflight) < workers:
                    heavy_busy = any(heavy[f] for f in inflight)
                    pick = next((t for t in queue
                                 if not (t.name in MEMORY_HEAVY and heavy_busy)
                                 and admit(estimate(t, peaks))), None)
                    if pick is None:
                        break
                    queue.remove(pick)
                    est = estimate(pick, peaks)
                    fut = pool.submit(run_one, pick,
                                      cap_for(pick, peaks, pick.name in MEMORY_HEAVY), est)
                    heavy[fut] = pick.name in MEMORY_HEAVY
                    inflight.add(fut)
                    time.sleep(0.05)  # let the scope register before the next admit() reads
                done, inflight = wait(inflight, timeout=1.0, return_when=FIRST_COMPLETED)
                for fut in done:
                    _progress(fut.result())
    else:
        for t in pooled:
            _progress(run_one(t))
    for t in isolated:
        _progress(run_one(t, cap_for(t, peaks, True) if _HARNESS else 0, estimate(t, peaks)))
    wall_elapsed = time.monotonic() - wall_start

    save_timings(results)
    if _PEAK_SEEN:
        try:
            PEAKS_FILE.write_text(json.dumps({**load_peaks(), **_PEAK_SEEN}, indent=0, sort_keys=True))
        except OSError:
            pass
    results.sort(key=lambda r: str(r[0]))
    passed = [r for r in results if r[1] == "PASS"]
    unmeasured = [r for r in results if r[1] == "UNMEASURED"]
    timed_out = [r for r in results if r[1] == "TIMEOUT"]
    capkilled = [r for r in results if r[1] == "KILLED"]
    failed = [r for r in results if r[1] not in ("PASS", "UNMEASURED", "TIMEOUT", "KILLED")]

    for path, status, elapsed, detail in results:
        rel = path.relative_to(REPO_ROOT)
        note = "  (isolated)" if path.name in ISOLATED else (
            "  (heavy lane)" if path.name in MEMORY_HEAVY else "")
        print(f"{status:8s} {elapsed:6.1f}s  {rel}{note}")
        if status != "PASS" and detail:
            for line in detail.splitlines():
                print(f"           {line}")

    for path, why in excluded:
        print(f"{'SKIPPED':8s} {'':6s}   {path.relative_to(REPO_ROOT)}  — {why}")

    # Denominator is what was DISCOVERED, not what came back — so a dropped result
    # shrinks the numerator and shows, instead of shrinking both and reading green.
    print(f"\n{len(passed)}/{len(tests)} passed  (wall {wall_elapsed:.1f}s, "
          f"{len(excluded)} skipped, {len(unmeasured)} unmeasured, {len(timed_out)} timeout, "
          f"{len(capkilled)} killed-by-cap, {len(failed)} failed) — {contain_note}")
    if args.timings:
        for path, status, elapsed, _ in sorted(results, key=lambda r: -r[2])[:10]:
            print(f"  slow: {elapsed:6.1f}s {status:8s} {path.relative_to(REPO_ROOT)}")
    if unmeasured:
        print(f"UNMEASURED ({len(unmeasured)}) — could not run here, NOT failures: "
              + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in unmeasured))

    if len(results) != len(tests):
        print(f"DROPPED: discovered {len(tests)} runnable selftests but only "
              f"{len(results)} results came back — the sweep is NOT a clean signal")
        return 1

    if capkilled:
        print("KILLED BY MEMORY CAP (%d) — NOT passes; their scope's OOM killer fired: " % len(capkilled)
              + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in capkilled))
    killed = [r for r in results if "KILLED by signal" in r[3]]
    if killed:
        print("KILLED (%d) - died on a signal (rc 137 = SIGKILL, usually the OOM killer), NOT real assertion failures; "
              "rerun alone: " % len(killed) + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in killed))
    if timed_out:
        print("TIMEOUT (%d) — NOT passes, exceeded their cap: " % len(timed_out)
              + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in timed_out))
    if failed or timed_out or capkilled:
        if failed:
            print("FAILED: " + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in failed))
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--_harness-child":
        raise SystemExit(_harness_child(sys.argv[3:] if sys.argv[2:3] == ["--"] else sys.argv[2:]))
    raise SystemExit(main())
