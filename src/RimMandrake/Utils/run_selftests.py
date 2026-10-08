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
"""
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
# 16-worker pool), so they run ISOLATED after the pool, one at a time, like selftest_render.py.
MEMORY_HEAVY = {"selftest_starwarspatches_semantics.py", "selftest_utinnipatches_dump.py",
                "selftest_mandrakepatches.py"}
# Per-test wall times from the previous run (path -> seconds). Used ONLY to start the
# slowest tests first (longest-processing-time scheduling), so the long pole overlaps
# everything else instead of starting last. Never read for a verdict. Lives in /tmp:
# a program reads it, not a human.
TIMINGS_FILE = Path(os.environ.get("SELFTEST_TIMINGS_FILE",
                                   Path(os.environ.get("TMPDIR", "/tmp")) / "selftest_timings.json"))
DEFAULT_WORKERS = 16  # tests are IO/subprocess-bound on drvfs, not CPU-bound


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


def _run_capped(path: Path, timeout: int):
    """subprocess.run, but a timeout kills the child's whole PROCESS GROUP.

    Plain subprocess.run(timeout=) kills only the direct child; a grandchild (a grep,
    a dotnet, a nested python) keeps the stdout pipe open and communicate() then blocks
    until IT exits -- so a "240 s" timeout could silently take far longer.
    """
    try:
        rel = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:  # a fixture outside the repo (selftest_run_selftests.py)
        rel = ""
    special = SPECIAL_INVOCATIONS.get(rel)
    argv, cwd = special() if special else ([sys.executable, str(path)], REPO_ROOT)
    p = subprocess.Popen(argv, cwd=cwd, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        p.communicate()
        raise
    return subprocess.CompletedProcess(p.args, p.returncode, out, err)


def run_one(path: Path) -> tuple[Path, str, float, str]:
    start = time.monotonic()
    try:
        proc = _run_capped(path, per_test_timeout(path))
        elapsed = time.monotonic() - start
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
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    ap.add_argument("--timings", action="store_true",
                    help="print the 10 slowest tests after the summary")
    args = ap.parse_args()

    tests, excluded = find_selftests()
    if not tests:
        print(f"no {SELFTEST_GLOB} found under {', '.join(SEARCH_ROOTS)} — "
              "that itself is suspicious")
        return 1

    missing = REQUIRED - {p.resolve().as_posix()[len(str(REPO_ROOT.resolve())) + 1:] for p in tests}
    if missing:
        print("REQUIRED lint selftest(s) not discovered: " + ", ".join(sorted(missing)))
        return 1

    stale = set(NOT_STANDALONE) - {p.relative_to(REPO_ROOT).as_posix()
                                   for p, _ in excluded}
    if stale:
        print("NOT_STANDALONE names files that no longer exist — a rename would "
              "otherwise silently drop or re-add a selftest: " + ", ".join(sorted(stale)))
        return 1

    ISOLATED = SEQUENTIAL_ISOLATED | MEMORY_HEAVY
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

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, t): t for t in pooled}
        for fut in as_completed(futures):
            _progress(fut.result())
    for t in isolated:
        _progress(run_one(t))
    wall_elapsed = time.monotonic() - wall_start

    save_timings(results)
    results.sort(key=lambda r: str(r[0]))
    passed = [r for r in results if r[1] == "PASS"]
    unmeasured = [r for r in results if r[1] == "UNMEASURED"]
    timed_out = [r for r in results if r[1] == "TIMEOUT"]
    failed = [r for r in results if r[1] not in ("PASS", "UNMEASURED", "TIMEOUT")]

    for path, status, elapsed, detail in results:
        rel = path.relative_to(REPO_ROOT)
        note = "  (isolated)" if path.name in SEQUENTIAL_ISOLATED | MEMORY_HEAVY else ""
        print(f"{status:8s} {elapsed:6.1f}s  {rel}{note}")
        if status != "PASS" and detail:
            for line in detail.splitlines():
                print(f"           {line}")

    for path, why in excluded:
        print(f"{'SKIPPED':8s} {'':6s}   {path.relative_to(REPO_ROOT)}  — {why}")

    # Denominator is what was DISCOVERED, not what came back — so a dropped result
    # shrinks the numerator and shows, instead of shrinking both and reading green.
    print(f"\n{len(passed)}/{len(tests)} passed  (wall {wall_elapsed:.1f}s, "
          f"{args.workers} workers, {len(excluded)} skipped, "
          f"{len(unmeasured)} unmeasured, {len(timed_out)} timeout, {len(failed)} failed)")
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

    killed = [r for r in results if "KILLED by signal" in r[3]]
    if killed:
        print("KILLED (%d) - died on a signal (rc 137 = SIGKILL, usually the OOM killer), NOT real assertion failures; "
              "rerun alone: " % len(killed) + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in killed))
    if timed_out:
        print("TIMEOUT (%d) — NOT passes, exceeded their cap: " % len(timed_out)
              + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in timed_out))
    if failed or timed_out:
        if failed:
            print("FAILED: " + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
