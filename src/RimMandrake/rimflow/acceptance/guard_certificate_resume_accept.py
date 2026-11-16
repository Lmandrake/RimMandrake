#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_RESUME_CERTIFICATE_RERUN_KILLED_AFTER_THIRTY_EIGHT (filed 2026-11-16 by the
FlowWorks fetch-fallen builder: `maturation.py certificate FlowWorks --run` reran 83 offline deciders for over an hour,
was killed at the helper's 1-hour background cap after 38, and a second --run would have started again from the first).

    python3 src/RimMandrake/rimflow/acceptance/guard_certificate_resume_accept.py      # "PASS 7/7" when built

THE CONTRACT IT ADDS to `judge_certificate.run_offline(root, mod, resume=False)` and `maturation.py certificate --run
--resume`: with resume, a test whose runs_today is a green stamp (rc 0) on the build its reads and file have NOW, with
the command it has now, is not rerun (its stamp is the same evidence a rerun would write); every other test runs: no
stamp, a stale build, a changed command, a red stamp. Without resume every test runs, as before. The certificate itself
(certify) is untouched: it still refuses a stamp whose build or command differs.
Exit 0 when every check passes.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
MOD = "FixtureMod"
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def tpath(root):
    return os.path.join(root, "design/concepts", MOD, "version/test_table.json")


def counting(root, name, rc=0):
    """A test file that appends one line to runs/<name> each time it runs, then exits rc."""
    open(os.path.join(root, "src", name + ".py"), "w").write(
        "import os, sys\nopen(os.path.join('runs', %r), 'a').write('x\\n')\nsys.exit(%d)\n" % (name, rc))


def runs(root, name):
    p = os.path.join(root, "runs", name)
    return len(open(p).read().splitlines()) if os.path.exists(p) else 0


def fixture(root):
    for d in ("design/concepts/%s/version" % MOD, "src", "runs"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    counting(root, "t_a")
    counting(root, "t_b")
    counting(root, "t_red", rc=1)
    tests = {n.upper(): {"id": n.upper(), "kind": "offline", "stage": "4-5", "file": "src/%s.py" % n, "reads": [],
                         "command": "%s src/%s.py" % (sys.executable, n)} for n in ("t_a", "t_b", "t_red")}
    json.dump({"mod": MOD, "version": "0.1.0", "tests": tests, "bars": []}, open(tpath(root), "w"), indent=1)


def main():
    import judge_certificate as JC
    with tempfile.TemporaryDirectory(prefix="cert_resume_") as root:
        fixture(root)
        JC.run_offline(root, MOD)
        check([runs(root, n) for n in ("t_a", "t_b", "t_red")] == [1, 1, 1], "control: a first run runs every test once")
        JC.run_offline(root, MOD)
        check([runs(root, n) for n in ("t_a", "t_b", "t_red")] == [2, 2, 2], "without resume every test runs again")
        r = JC.run_offline(root, MOD, resume=True)
        check([runs(root, n) for n in ("t_a", "t_b")] == [2, 2], "resume: a green stamp on the current build is not rerun")
        check(runs(root, "t_red") == 3, "resume: a red stamp is rerun")
        check(r.get("skipped") == 2, "resume reports the tests it kept (skipped 2), got %r" % r.get("skipped"))
        open(os.path.join(root, "src/t_a.py"), "a").write("# changed\n")
        t = json.load(open(tpath(root)))
        t["tests"]["T_B"]["command"] = "%s src/t_b.py --again" % sys.executable
        json.dump(t, open(tpath(root), "w"), indent=1)
        JC.run_offline(root, MOD, resume=True)
        check(runs(root, "t_a") == 3, "resume: a stamp on a stale build (its file changed) is rerun")
        check(runs(root, "t_b") == 3, "resume: a stamp whose command changed is rerun")
    n = len(RESULTS)
    print("PASS %d/%d" % (sum(RESULTS), n) if all(RESULTS) else "FAIL %d/%d" % (sum(RESULTS), n))
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
