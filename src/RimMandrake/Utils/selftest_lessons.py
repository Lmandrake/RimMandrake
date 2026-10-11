#!/usr/bin/env python3
"""Selftest for lessons.py: --home warning/line, duplicate hint, stats. Uses a temp LESSONS_ROOT."""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LESSONS = os.path.join(HERE, "lessons.py")
fails = []


def check(name, cond, detail=""):
    if not cond:
        fails.append(name)
        print("FAIL: %s %s" % (name, detail))


def run(root, *args):
    env = dict(os.environ, LESSONS_ROOT=root)
    return subprocess.run([sys.executable, LESSONS] + list(args), env=env, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as root:
    d = os.path.join(root, "infrastructure", "state", "lessons")
    os.makedirs(d)
    now = time.time()

    def stamp(days):
        return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now - days * 86400))

    fixtures = [(2, "BENCH", "a", "alpha beta gamma\nhome: skill-x\n"),
                (10, "FOUNDRY", "b", "delta epsilon\n"),
                (20, "BENCH", "c", "zeta eta\nhome: skill-x\n"),
                (40, "BENCH", "d", "theta iota\nhome: NONE\n")]
    for days, seat, slug, body in fixtures:
        with open(os.path.join(d, "%s-%s-%s.md" % (stamp(days), seat, slug)), "w") as f:
            f.write(body)
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# header\n")

    r = run(root, "stats")
    out = r.stdout
    check("stats rc", r.returncode == 0, r.stderr)
    check("stats total", "total: 4" in out, out)
    check("stats seat", "BENCH=3" in out and "FOUNDRY=1" in out, out)
    check("stats age", "<7d=1" in out and "7-14d=1" in out and "14-30d=1" in out and ">30d=1" in out, out)
    check("stats home", "with home: 3, without home: 1" in out and "skill-x=2" in out, out)
    check("stats oldest", "oldest undrained: 40 days" in out, out)

    r = run(root, "add", "kappa lambda mu nu xi omicron", "--seat", "bench")
    check("add no-home warns", "no --home given" in r.stderr and r.returncode == 0, r.stderr)
    r = run(root, "add", "pi rho sigma tau", "--seat", "bench", "--home", "skills/foo")
    check("add home no warn", "no --home" not in r.stderr and r.returncode == 0, r.stderr)
    newest = [n for n in sorted(os.listdir(d)) if "pi-rho" in n]
    check("home line written", newest and open(os.path.join(d, newest[0])).read().splitlines()[-1] == "home: skills/foo")

    r = run(root, "add", "alpha beta gamma delta", "--home", "NONE")
    check("dup hint", "possible duplicates:" in r.stdout and "alpha beta gamma" in r.stdout, r.stdout)
    r = run(root, "add", "completely unrelated words here", "--home", "NONE")
    check("no dup hint", "possible duplicates:" not in r.stdout, r.stdout)

if fails:
    print("selftest_lessons: %d FAILED" % len(fails))
    sys.exit(1)
print("selftest_lessons: OK")
