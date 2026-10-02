"""Run the next unfinished northstar live job (or list the queue).

    python.exe src/RimMandrake/Utils/modcheck/live_queue/run_next.py            run the next job
    python.exe .../run_next.py --all                                            run every remaining job in order
    python.exe .../run_next.py --list                                           show the queue and each job's state
    python.exe .../run_next.py --job J3_bland_tile                              run one job regardless of state
    add --dry-run to rehearse on FakeWorld (separate results file)

Each job runs in its own process (rimdrive allows one Session per process). Exit code is the last job's:
0 MEASURED PASS, 1 MEASURED FAIL, 2 UNMEASURED, 3 queue empty.
"""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from common import ROOT, results_path   # noqa: E402
from jobs import JOBS, latest, next_job  # noqa: E402


def show(dry):
    last = latest(dry)
    print("results: %s" % results_path(dry))
    for j in JOBS:
        r = last.get(j["id"])
        st = "not run" if r is None else ("%s %s" % (r["status"], r.get("verdict") or "")).strip()
        print("  %-22s %-16s %s" % (j["id"], st, j["title"]))
    n = next_job(dry)
    print("next: %s" % (n["id"] if n else "(queue done)"))


def run(job, dry):
    cmd = [sys.executable, os.path.join(_HERE, job["file"])] + (["--dry-run"] if dry else [])
    print(">> %s  (fails when: %s)" % (job["id"], job["fails_when"]))
    sys.stdout.flush()
    return subprocess.call(cmd, cwd=ROOT)


def main(argv):
    dry = "--dry-run" in argv
    if "--list" in argv:
        show(dry)
        return 0
    if "--job" in argv:
        want = argv[argv.index("--job") + 1]
        hit = [j for j in JOBS if j["id"] == want or j["id"].split("_")[0] == want]
        if not hit:
            print("no job %r; known: %s" % (want, ", ".join(j["id"] for j in JOBS)))
            return 3
        return run(hit[0], dry)
    rc, ran, tried = 3, 0, set()
    while True:
        j = next_job(dry, skip=tried)        # --all moves past an UNMEASURED job instead of idling on it
        if j is None:
            break
        tried.add(j["id"])
        rc = run(j, dry)
        ran += 1
        if "--all" not in argv:
            break
    if ran == 0:
        print("queue done: every job has a MEASURED record (run_next.py --list)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
