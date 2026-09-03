#!/usr/bin/env python3
"""Run every selftest_*.py under src/ in parallel and print an explicit N/N summary.

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
"""
import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PER_TEST_TIMEOUT_S = 240
SEQUENTIAL_ISOLATED = {"selftest_render.py"}


def find_selftests() -> list[Path]:
    return sorted((REPO_ROOT / "src").rglob("selftest_*.py"))


def run_one(path: Path) -> tuple[Path, str, float, str]:
    start = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=PER_TEST_TIMEOUT_S,
        )
        elapsed = time.monotonic() - start
        if proc.returncode == 0:
            return path, "PASS", elapsed, ""
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-40:]
        return path, "FAIL", elapsed, "\n".join(tail)
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return path, "TIMEOUT", elapsed, f"exceeded {PER_TEST_TIMEOUT_S}s"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    tests = find_selftests()
    if not tests:
        print("no selftest_*.py found under src/ — that itself is suspicious")
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
    failed = [r for r in results if r[1] != "PASS"]

    for path, status, elapsed, detail in results:
        rel = path.relative_to(REPO_ROOT)
        note = "  (isolated)" if path.name in SEQUENTIAL_ISOLATED else ""
        print(f"{status:8s} {elapsed:6.1f}s  {rel}{note}")
        if status != "PASS" and detail:
            for line in detail.splitlines():
                print(f"           {line}")

    print(f"\n{len(passed)}/{len(results)} passed  (wall {wall_elapsed:.1f}s, "
          f"{args.workers} workers)")

    if failed:
        print("FAILED: " + ", ".join(str(p.relative_to(REPO_ROOT)) for p, *_ in failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
