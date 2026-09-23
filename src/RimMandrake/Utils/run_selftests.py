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
import re
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
SEARCH_ROOTS = ("src", ".claude/hooks", "skills", "infrastructure/dashboards/hub")
SELFTEST_GLOB = "selftest*.py"

# Selftests that exist and are real, but cannot be run as bare `python3 <file>`.
# Excluding one here is a deliberate, VISIBLE act — it prints as SKIPPED with this
# reason. A key naming no discovered file is a hard error, so a rename cannot quietly
# turn an exclusion into a permanent disappearance.
NOT_STANDALONE = {
    "src/RimMandrake/Utils/rimplace/selftest.py":
        "package module — `python3 -m rimplace selftest` from src/RimMandrake/Utils, "
        "under ~/.local/venvs/rimlua/bin/python (needs lupa; 8/36 on plain python3)",
    "skills/generating-rimworld-sprites/scripts/selftest.py":
        "requires --reference <png>; a human-driven art check, not an unattended test",
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


def run_one(path: Path) -> tuple[Path, str, float, str]:
    start = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=per_test_timeout(path),
        )
        elapsed = time.monotonic() - start
        if proc.returncode == 0:
            return path, "PASS", elapsed, ""
        out = proc.stdout + proc.stderr
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
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    tests, excluded = find_selftests()
    if not tests:
        print(f"no {SELFTEST_GLOB} found under {', '.join(SEARCH_ROOTS)} — "
              "that itself is suspicious")
        return 1

    stale = set(NOT_STANDALONE) - {p.relative_to(REPO_ROOT).as_posix()
                                   for p, _ in excluded}
    if stale:
        print("NOT_STANDALONE names files that no longer exist — a rename would "
              "otherwise silently drop or re-add a selftest: " + ", ".join(sorted(stale)))
        return 1

    pooled = [t for t in tests if t.name not in SEQUENTIAL_ISOLATED]
    isolated = [t for t in tests if t.name in SEQUENTIAL_ISOLATED]

    results = []
    wall_start = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, t): t for t in pooled}
        for fut in as_completed(futures):
            results.append(fut.result())
    for t in isolated:
        results.append(run_one(t))
    wall_elapsed = time.monotonic() - wall_start

    results.sort(key=lambda r: str(r[0]))
    passed = [r for r in results if r[1] == "PASS"]
    unmeasured = [r for r in results if r[1] == "UNMEASURED"]
    failed = [r for r in results if r[1] not in ("PASS", "UNMEASURED")]

    for path, status, elapsed, detail in results:
        rel = path.relative_to(REPO_ROOT)
        note = "  (isolated)" if path.name in SEQUENTIAL_ISOLATED else ""
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
          f"{len(unmeasured)} unmeasured, {len(failed)} failed)")
    if unmeasured:
        print(f"UNMEASURED ({len(unmeasured)}) — could not run here, NOT failures: "
              + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in unmeasured))

    if len(results) != len(tests):
        print(f"DROPPED: discovered {len(tests)} runnable selftests but only "
              f"{len(results)} results came back — the sweep is NOT a clean signal")
        return 1

    if failed:
        print("FAILED: " + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
