#!/usr/bin/env python3
# selftest-timeout: 300
"""RM_SCRATCH_FIX_ENACT_DIRS_UNREAPED: art.py enact selftests left enact_* fixture dirs in rm/scratch/<SEAT>.
Two proofs. SOURCE: a real enact selftest (v2, which never removed its own dir) leaves its ENACT_SELFTEST_ROOT empty.
CLEANER: an old enact_* dir is seen and DELETEd; a young one is YOUNG; one with a repo inside is not touched."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


td = Path(tempfile.mkdtemp(prefix="reap_enact_", dir=os.environ.get("SELFTEST_TMP") or "/home/mandrake/rm/scratch/BENCH"))
try:
    # SOURCE
    fx = td / "fixroot"
    fx.mkdir()
    r = subprocess.run([sys.executable, str(HERE / "art" / "selftest_enact_v2.py")], capture_output=True, text=True,
                       env={**os.environ, "ENACT_SELFTEST_ROOT": str(fx)}, timeout=240)
    check("ALL PASS" in r.stdout, "the v2 enact selftest ran green")
    check(not list(fx.iterdir()), f"it left nothing behind in its root: {[p.name for p in fx.iterdir()]}")

    # CLEANER
    os.environ["SCRATCH_REAP_ROOTS"] = str(td / "rmscratch")
    os.environ["SCRATCH_REAP_RM_SCRATCH"] = "/nonexistent"
    import scratch_reap as R
    R.pool_measures = lambda: {}
    R.CTIME_COUNTS = False
    seat = td / "rmscratch" / "SEAT"
    for n in ("enact_old_1", "enact_young_2", "enact_repo_3"):
        (seat / n).mkdir(parents=True)
        (seat / n / "f.txt").write_text("x")
    subprocess.run(["git", "init", "-q", str(seat / "enact_repo_3")], check=True)
    old = time.time() - 3 * 86400
    for n in ("enact_old_1", "enact_repo_3"):
        for d, _, fs in os.walk(seat / n):
            for x in [d] + [os.path.join(d, f) for f in fs]:
                os.utime(x, (old, old))
    rows = {Path(c[1]).name: c for c in R.candidates()}
    check("enact_old_1" in rows and rows["enact_old_1"][0] == "fixture", "the cleaner sees an enact_* dir")
    check("enact_repo_3" not in rows or rows["enact_repo_3"][0] != "fixture", "a dir holding a repo is not a fixture")
    ctx = R.Ctx(time.time())
    check(R.judge_fixture(seat / "enact_old_1", ctx)["verdict"] == "DELETE", "an old fixture is DELETE")
    check(R.judge_fixture(seat / "enact_young_2", ctx)["verdict"] == "YOUNG", "a young fixture is YOUNG")
finally:
    subprocess.run(["rm", "-rf", str(td)])
print("ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
sys.exit(1 if FAILS else 0)
