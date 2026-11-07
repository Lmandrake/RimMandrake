"""situational_pass: the every-suite --situational --policy abort pass, run per suite through the testq lane
(NORTHSTAR_SITUATIONAL_ROLLOUT_1). situational_rerun.py wants one seat driving one game session for hours, and no lane
runs that (a live proof is read-only and capped at 600 s; a worker never drives the game); testq already loads each
suite's closure on SteveDesktop with no model in the loop.

    python3 .../situational_pass.py submit --sha <published sha> [--mods A,B] [--priority 21] [--timeout 3600]
    python3 .../situational_pass.py status --sha <sha>
    python3 .../situational_pass.py rollup --sha <sha> [--write]

`submit` queues every suite (suite_set.situational_suites) with no job yet at that sha. `rollup` judges the results by
situational_rerun.judge and, with --write, appends the record rollout_gate.py reads to the committed RECORD: only a
complete pass is written. Exit: 0 PASS, 1 FAIL, 2 not complete.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import FAIL, MEASURED, PASS, ROOT       # noqa: E402

TESTQ = os.path.join(ROOT, "src", "RimMandrake", "Utils", "testq", "testq.py")
RECORD = os.path.join(ROOT, "infrastructure", "state", "situational_pass.jsonl")
STATES = ("pending", "running", "done")


def queue_home():
    return os.environ.get("TESTQ_QUEUE") or "/mnt/d/ClaudeWork/rimmandrake/testq"


def read_jobs(sha, home=None):
    """-> {state: [record]} for this sha's situational jobs. A done record is {"job", "result", ...}; a pending one is the
    job itself; a running one holds the job under "job"."""
    out = {s: [] for s in STATES}
    for state in STATES:
        for p in glob.glob(os.path.join(home or queue_home(), state, "*.json")):
            try:
                with open(p, encoding="utf-8") as f:
                    r = json.load(f)
            except (OSError, ValueError):
                continue
            job = r["job"] if isinstance(r.get("job"), dict) else r
            if job.get("situational") and job.get("source_sha") == sha:
                out[state].append(r)
    return out


def job_of(r):
    return r["job"] if isinstance(r.get("job"), dict) else r


def latest_results(done):
    """-> {mod: result}, the newest attempt per suite: a harness death re-submitted must not stand for ever."""
    best = {}
    for r in done:
        mod, res = job_of(r)["mod"], r.get("result") or {}
        if mod not in best or (res.get("finished") or "") > (best[mod].get("finished") or ""):
            best[mod] = res
    return best


class Tally(object):
    """The part of common.Job judge() uses: common.Job writes the per-clone results file on finish, which this must not."""

    def __init__(self):
        self.checks = []

    def check(self, name, ok, detail=""):
        self.checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:600]})
        return bool(ok)


def judge_pass(results, suites, sha, finished=None):
    """-> the situational_rerun record for this pass. Pure: `results` {mod: testq result}, `suites` what it owes.
    A suite with no result leaves it UNMEASURED; a job that did not end DONE is a crash, never a pass."""
    import situational_rerun as R
    digests, crashed = [], []
    for mod in sorted(results):
        res = results[mod]
        d = res.get("situational")
        if res.get("outcome") != "DONE":
            crashed.append("%s: %s/%s %s" % (mod, res.get("outcome"), res.get("cause"), (res.get("note") or "")[:160]))
        elif not d or d.get("digest_error"):
            crashed.append("%s: no digest (%s)" % (mod, (d or {}).get("digest_error") or "the result carries none"))
        else:
            digests.append(d)
    t = Tally()
    # the sidecars are on the host that ran the suite: the worker looked there (evidence_missing), so judge() must not
    # look here, where every one reads as missing
    R.judge(t, [dict(d, surprises=[]) for d in digests], crashed)
    t.check("every recorded surprise has its evidence on the host that ran it",
            not [m for d in digests for m in d.get("evidence_missing") or []],
            ["%s: %s" % (d["mod"], m) for d in digests for m in d.get("evidence_missing") or []])
    refused = ["%s: %s" % (d["mod"], d["refused"][:120]) for d in digests if d.get("refused")]
    t.check("no suite refused (a refused suite ran nothing)", not refused, refused)
    missing = sorted(set(suites) - set(results))
    failed = [c["name"] for c in t.checks if not c["ok"]]
    measured = not missing
    return {"job": "situational_rerun", "status": MEASURED if measured else "UNMEASURED",
            "verdict": None if not measured else (FAIL if failed else PASS), "dry_run": False,
            "finished": finished or time.strftime("%Y-%m-%dT%H:%M:%S"), "failed": failed, "checks": t.checks,
            "unmeasured_reason": ("%d suite(s) have no result" % len(missing)) if missing else None,
            "evidence": {"source": "testq", "digests": digests, "crashed": crashed, "missing": missing,
                         "run_identity": {"git": {"sha": sha}}}}


def suites():
    import suite_set
    return sorted(suite_set.situational_suites())


def cmd_submit(a, have):
    mods = [m for m in a.mods.split(",") if m] if a.mods else suites()
    rc = 0
    for m in mods:
        if m in have:
            print("have %s" % m)
            continue
        r = subprocess.run([sys.executable, TESTQ, "submit", m, "--full", "--purpose", "sweep", "--by", "BENCH", "--sha", a.sha,
                            "--situational", "--priority", str(a.priority), "--timeout", str(a.timeout)],
                           capture_output=True, text=True, timeout=120)
        print("%s %s %s" % ("sent" if r.returncode == 0 else "REFUSED", m, (r.stdout + r.stderr).strip()[-200:]))
        rc = rc or r.returncode
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("verb", choices=("submit", "status", "rollup"))
    ap.add_argument("--sha", required=True)
    ap.add_argument("--mods")
    ap.add_argument("--priority", type=int, default=21, help="above the filler and guards (20), below Relentless (50)")
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    jobs = read_jobs(a.sha)
    if a.verb == "submit":
        return cmd_submit(a, {job_of(r)["mod"] for s in STATES for r in jobs[s]})
    rec = judge_pass(latest_results(jobs["done"]), suites(), a.sha)
    ev = rec["evidence"]
    print("%s %s: pending %d running %d done %d; missing %d crashed %d" % (
        rec["status"], rec["verdict"], len(jobs["pending"]), len(jobs["running"]), len(jobs["done"]),
        len(ev["missing"]), len(ev["crashed"])))
    for c in rec["checks"]:
        if not c["ok"]:
            print("  FAIL %s -- %s" % (c["name"], c["detail"][:400]))
    if a.verb == "rollup" and a.write:
        if rec["status"] != MEASURED:
            print("not written: the pass is not complete")
            return 2
        with open(RECORD, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print("written: %s" % RECORD)
    if rec["status"] != MEASURED:
        return 2
    return 0 if rec["verdict"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
