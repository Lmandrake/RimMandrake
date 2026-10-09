#!/usr/bin/env python3
"""selftest_run_selftests_evidence.py — the runner's tiers, suite lock and skip-when-unchanged, end to end.

Builds a fake repo of fixture selftests under /home/mandrake/rm/scratch/BENCH/ (ext4, never /tmp) and drives the
REAL run_selftests.py at it (RM_SELFTEST_REPO_ROOT / _STATE_DIR / _LOCK point everything at the fixture; no memory
pen, so it is quick). Every skip claim is checked from both sides: an unchanged input IS skipped, and each kind of
change — file content, a new file in a listed dir, a failure, a runner-version change, --full — is NOT.

    python3 src/RimMandrake/Utils/selftest_run_selftests_evidence.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_selftests.py"
SCRATCH = Path("/home/mandrake/rm/scratch/BENCH") if Path("/home/mandrake/rm").is_dir() else HERE.parents[2] / ".scratch"
FAILS = []


def eq(got, want, what):
    print(("ok   " if got == want else "FAIL ") + what + ("" if got == want else f"  — got {got!r}, want {want!r}"))
    if got != want:
        FAILS.append(what)


ELIG = "# selftest-skip: eligible\n"
FIXTURES = {
    "src/selftest_reads_data.py": ELIG + "print(open('src/data.txt').read().strip())\n",
    "src/selftest_lists_dir.py": ELIG + "import os\nprint(sorted(os.listdir('src/listed')))\n",
    "src/selftest_reads_outside.py": ELIG + "import os\nprint(open(os.environ['FIX_OUTSIDE']).read())\n",
    "src/selftest_untraced_child.py": ELIG + ("import subprocess, sys\n"
                                              "subprocess.run([sys.executable, '-c', 'print(1)'], env={'PATH': '/usr/bin'}, check=True)\n"),
    "src/selftest_flaky.py": ELIG + "import os, sys\nprint('flaky')\nsys.exit(1 if os.path.exists('src/FAIL_NOW') else 0)\n",
    "src/selftest_plain.py": "print('not eligible: always runs')\n",
    "src/selftest_unmeasured_rc0.py": "print('no live dir — UNMEASURED, not a pass or a fail')\n",
    "src/selftest_deployed_thing.py": "# selftest-tier: deployed\nprint('live install check')\n",
}


def build(root: Path):
    shutil.rmtree(root, ignore_errors=True)
    for rel, body in FIXTURES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    (root / "src/data.txt").write_text("v1\n")
    (root / "src/listed").mkdir()
    (root / "src/listed/a").write_text("a")
    (root.parent / f"outside-{os.getpid()}.txt").write_text("outside the fixture repo")


def run(root: Path, *args, env_extra=None, timeout=120):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("RM_SELFTEST_") and k not in ("PYTHONPATH",)}
    env.update(RM_SELFTEST_REPO_ROOT=str(root), RM_SELFTEST_STATE_DIR=str(root / ".state"),
               RM_SELFTEST_LOCK=str(root / ".lock"), RM_SELFTEST_NO_HARNESS="1",
               SELFTEST_TIMINGS_FILE=str(root / ".state/timings.json"),
               FIX_OUTSIDE=str(root.parent / f"outside-{os.getpid()}.txt"))
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, str(RUNNER), *args], cwd=root, env=env, capture_output=True, text=True,
                       timeout=timeout)
    states = {}
    for ln in p.stdout.splitlines():
        parts = ln.split()
        if len(parts) >= 2 and parts[0] in ("PASS", "FAIL", "UNMEASURED", "CRASH", "SKIPPED"):
            path = next((x for x in parts[1:] if x.startswith("src/")), None)
            if path:
                states[path] = parts[0]
    return p, states


def main():
    root = SCRATCH / f"runner_fixture_{os.getpid()}"
    build(root)
    try:
        p, st = run(root)
        eq(p.returncode, 0, "run 1: fixture suite is GREEN (UNMEASURED and SKIPPED do not redden it)")
        eq(st.get("src/selftest_unmeasured_rc0.py"), "UNMEASURED", "run 1: rc-0 test printing the phrase is UNMEASURED")
        eq(st.get("src/selftest_deployed_thing.py"), "SKIPPED", "run 1: a deployed-tier test is SKIPPED in the default tier")
        eq(st.get("src/selftest_reads_data.py"), "PASS", "run 1: eligible test runs the first time")
        eq("PASS 6/8" in p.stdout and "SKIPPED 1/8" in p.stdout and "UNMEASURED 1/8" in p.stdout, True,
           "run 1: explicit N/N per state over all 8 discovered")
        eq("2 PASS not recordable" in p.stdout, True, "run 1: outside-read and untraced-child PASSes are not recordable")

        p, st = run(root)
        eq(st.get("src/selftest_reads_data.py"), "SKIPPED", "run 2: unchanged input -> SKIPPED")
        eq(st.get("src/selftest_lists_dir.py"), "SKIPPED", "run 2: unchanged listing -> SKIPPED")
        eq(st.get("src/selftest_flaky.py"), "SKIPPED", "run 2: unchanged flaky test -> SKIPPED")
        eq(st.get("src/selftest_reads_outside.py"), "PASS", "run 2: a test reading outside the repo is never skipped")
        eq(st.get("src/selftest_untraced_child.py"), "PASS", "run 2: a test whose python child dropped the tracer is never skipped")
        eq(st.get("src/selftest_plain.py"), "PASS", "run 2: a non-eligible test always runs")
        eq("unchanged since its PASS" in p.stdout, True, "run 2: the skip prints its reason")

        (root / "src/data.txt").write_text("v2\n")
        (root / "src/listed/b").write_text("b")
        (root / "src/FAIL_NOW").write_text("x")
        p, st = run(root)
        eq(st.get("src/selftest_reads_data.py"), "PASS", "run 3: changed file content -> re-run")
        eq(st.get("src/selftest_lists_dir.py"), "PASS", "run 3: a new file in a listed dir -> re-run")
        eq(st.get("src/selftest_flaky.py"), "FAIL", "run 3: a probed path appearing -> re-run, and it FAILs")
        eq(p.returncode, 1, "run 3: a FAIL makes the run RED")

        (root / "src/FAIL_NOW").unlink()
        p, st = run(root)
        eq(st.get("src/selftest_flaky.py"), "PASS", "run 4: after a FAIL the record is gone, so it runs again")
        eq(st.get("src/selftest_reads_data.py"), "SKIPPED", "run 4: the re-recorded v2 input is skipped again")

        p, st = run(root, "--full")
        eq(st.get("src/selftest_reads_data.py"), "PASS", "--full runs a test whose record says unchanged")

        recs = list((root / ".state/records").rglob("*.json.z"))
        import zlib
        for r in recs:   # simulate a runner change: every record's version stops matching
            d = json.loads(zlib.decompress(r.read_bytes()))
            d["version"] = "older-runner"
            r.write_bytes(zlib.compress(json.dumps(d).encode()))
        p, st = run(root)
        eq(st.get("src/selftest_reads_data.py"), "PASS", "a runner-version change invalidates every record")

        p, st = run(root, "--tier", "deployed")
        eq((st.get("src/selftest_deployed_thing.py"), st.get("src/selftest_plain.py")), ("PASS", "SKIPPED"),
           "--tier deployed runs only the deployed-tier test")

        # the suite lock: a second suite WAITS and names the holder, then runs
        env = {**os.environ, "RM_SELFTEST_LOCK": str(root / ".lock")}
        holder = subprocess.Popen([sys.executable, "-c",
                                   "import sys, time; sys.path.insert(0, %r)\nimport run_selftests as r\n"
                                   "with r.suite_lock():\n    print('held', flush=True); time.sleep(4)" % str(HERE)],
                                  env=env, stdout=subprocess.PIPE, text=True)
        holder.stdout.readline()
        t0 = time.monotonic()
        p, st = run(root, "--tier", "deployed")
        waited = time.monotonic() - t0
        holder.wait(timeout=30)
        eq("WAITING for the selftest suite lock" in p.stderr and f"pid {holder.pid}" in p.stderr, True,
           "a second suite prints that it is waiting, and on whom")
        eq(waited >= 2.5 and p.returncode == 0, True, "...and runs once the holder lets go")
        p, _ = run(root, "--only", str(root / "src/selftest_plain.py"))
        eq("WAITING" in p.stderr, False, "--only takes no suite lock")
    finally:
        shutil.rmtree(root, ignore_errors=True)
        try:
            (root.parent / f"outside-{os.getpid()}.txt").unlink()
        except OSError:
            pass
    if FAILS:
        print(f"FAIL selftest_run_selftests_evidence.py: {len(FAILS)} check(s)")
        return 1
    print("ok  selftest_run_selftests_evidence.py — tiers, suite lock, evidence skip both ways")
    return 0


if __name__ == "__main__":
    sys.exit(main())
