#!/usr/bin/env python3
"""selftest_own_cgroup.py: the promises of design/specs/2026-11-24-tick-children-own-cgroup/boundary.md, one test of each
promise's name, and the outcome check's parser. The service tests run real transient user services for a few seconds.
OWN_CGROUP_BASE_DIR=<dir holding a parent's modules> runs the caller tests on that copy (watch it fail)."""
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "acceptance"))
sys.path.insert(0, HERE)
import own_cgroup as OC           # noqa: E402
import tick_peak_accept as TPA    # noqa: E402

TMP = tempfile.mkdtemp(prefix="own_cgroup_")
FAILS, SEEN = [], []


def ok(name, cond, why=""):
    SEEN.append(name)
    print("%s  %s%s" % ("ok   " if cond else "FAIL ", name, "" if cond else ": %s" % (why,)))
    if not cond:
        FAILS.append(name)


CHILD = r'''
import os, sys
sys.path.insert(0, %r)
import own_cgroup as OC
me = open("/proc/self/cgroup").read().strip()
r = OC.run(["sh", "-c", "cat /proc/self/cgroup; pwd; echo $OC_PROBE ${1#}; echo to-stderr >&2; exit 7", "sh", "a $OC_PROBE $$ b"], cwd="/usr", text=True,
           capture_output=True, env=dict(os.environ, OC_PROBE="kept"))
open(sys.argv[1], "w").write(repr({"me": me, "rc": r.returncode, "out": r.stdout, "err": r.stderr}))
''' % HERE
DIES = r'''
import os, sys
sys.path.insert(0, %r)
import own_cgroup as OC
OC.run(["sh", "-c", "echo $$ > " + sys.argv[1] + "; exec sleep 300"])
''' % HERE


def service(name, code, *args, wait=True):
    path = os.path.join(TMP, name + ".py")      # a file: systemd-run would expand a $ in a service's own arguments
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return subprocess.run(["systemd-run", "--user", "--quiet", "--collect"] + (["--wait"] if wait else ["-p", "Type=exec"]) + [
        "--unit", name, sys.executable, path] + list(args), capture_output=True, text=True, timeout=120,
        stdin=subprocess.DEVNULL)


def t_child_leaves_the_service_cgroup():
    out = os.path.join(TMP, "r")
    r = service("selftest-own-cgroup-%d.service" % os.getpid(), CHILD, out)
    got = eval(open(out).read()) if os.path.exists(out) else {}
    lines = (got.get("out") or "").splitlines()
    ok("child-leaves-the-service-cgroup: the command is in a scope of its own, not the service's",
       len(lines) == 3 and lines[0].endswith(".scope") and lines[0] != got["me"] and got["me"].endswith(".service"),
       (r.stderr, got))
    ok("child-leaves-the-service-cgroup: exit code, output, cwd and environment come back",
       got.get("rc") == 7 and lines[1:] == ["/usr", "kept a $OC_PROBE $$ b"] and got.get("err") == "to-stderr\n", got)


def alive(pid):
    try:
        return open("/proc/%d/stat" % pid).read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return False


def t_child_dies_with_its_service():
    pidf, unit = os.path.join(TMP, "pid"), "selftest-own-cgroup-dies-%d.service" % os.getpid()
    service(unit, DIES, pidf, wait=False)
    end = time.time() + 60      # a hang guard: the start is immediate on an idle machine
    while time.time() < end and not (os.path.exists(pidf) and open(pidf).read().strip()):
        time.sleep(.1)
    pid = int(open(pidf).read()) if os.path.exists(pidf) else 0
    was = bool(pid) and alive(pid)
    where = open("/proc/%d/cgroup" % pid).read() if was else ""
    subprocess.run(["systemctl", "--user", "stop", unit], capture_output=True, timeout=120)
    end = time.time() + 60
    while time.time() < end and pid and alive(pid):
        time.sleep(.1)
    ok("child-dies-with-its-service: a stopped service takes the scope with it",
       was and ".scope" in where and not alive(pid), (pid, was, where))


class Fake:
    def __init__(self, *results):
        self.calls, self.results = [], list(results)

    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        rc, err = self.results.pop(0)
        return subprocess.CompletedProcess(argv, rc, "", err)


def with_fake(service_name, fake, argv=("true",), which="/usr/bin/systemd-run"):
    keep = OC.my_service, OC.subprocess.run, OC.shutil.which
    OC.my_service, OC.subprocess.run, OC.shutil.which = (lambda: service_name), fake, (lambda n: which)
    try:
        return OC.run(list(argv), capture_output=True, text=True)
    finally:
        OC.my_service, OC.subprocess.run, OC.shutil.which = keep


def t_outside_a_service_runs_plain():
    for nm, svc, which in (("no service", None, "/usr/bin/systemd-run"), ("no systemd-run", "x.service", None)):
        f = Fake((3, ""))
        r = with_fake(svc, f, which=which)
        ok("outside-a-service-runs-plain: %s" % nm, f.calls == [["true"]] and r.returncode == 3, f.calls)
    for nm, text, want in (("a service", "0::/user.slice/user@1000.service/app.slice/a.service", "a.service"),
                           ("a scope", "0::/user.slice/user@1000.service/app.slice/a.scope", None),
                           ("the manager itself", "0::/user.slice/user-1000.slice/user@1000.service", None),
                           ("an empty file", "", None)):
        p = os.path.join(TMP, "cg")
        open(p, "w").write(text)
        ok("outside-a-service-runs-plain: my_service reads %s" % nm, OC.my_service(p) == want, OC.my_service(p))
    try:
        got = OC.my_service(os.path.join(TMP, "none"))
    except OSError:
        got = "raised"
    ok("outside-a-service-runs-plain: an unreadable cgroup file raises, it is not 'no service'", got == "raised", got)


def t_scope_refused_runs_plain():
    f = Fake((1, "Failed to start transient scope unit: Connection refused\n"), (0, ""))
    r = with_fake("x.service", f)
    ok("scope-refused-runs-plain: the command still runs once, in place",
       len(f.calls) == 2 and f.calls[0][0] == "systemd-run" and f.calls[1] == ["true"] and r.returncode == 0, f.calls)
    f = Fake((1, "error: cannot lock ref\n"))
    r = with_fake("x.service", f)
    ok("scope-refused-runs-plain: a command that failed is not run twice", len(f.calls) == 1 and r.returncode == 1, f.calls)


def t_clone_and_landing_children_use_it():
    base = os.environ.get("OWN_CGROUP_BASE_DIR")
    if base:
        sys.path.insert(0, base)
    os.environ["RM_DETACHED_POOL"] = os.path.join(TMP, "pool")
    import detached_helper as DH
    import maturation_dispatch as MD
    dest = os.path.join(TMP, "pool", "clones", "IT.det")
    os.makedirs(os.path.join(dest, ".git"))
    open(os.path.join(dest, "sync"), "w").close()
    seen = []
    keep = OC.run
    OC.run = lambda argv, **kw: seen.append(list(argv)) or subprocess.CompletedProcess(argv, 0, "", "")
    try:
        try:
            DH.take_clone("IT")
        except Exception as e:  # noqa: BLE001  the parent runs the real ./sync of an empty file
            print("      take_clone: %s" % str(e)[:100])
        ok("clone-and-landing-children-use-it: a reused clone's ./sync", seen == [["./sync"]], seen)
        del seen[:]
        try:
            DH.take_clone("NEW") if not base else None      # the parent would make a real clone
        except RuntimeError:        # the stand-in made no clone
            pass
        ok("clone-and-landing-children-use-it: a new clone's scratch_clone.py",
           len(seen) == 1 and any("scratch_clone.py" in a for a in seen[0]), seen)
        del seen[:]
        root = os.path.join(TMP, "root")
        subprocess.run(["git", "init", "-q", root], check=True)
        if not base:
            MD.land_spend(root, ["a.md"])
        ok("clone-and-landing-children-use-it: land_spend's land.sh",
           len(seen) == 1 and seen[0][0].endswith("land.sh") and seen[0][-1] == "a.md", seen)
        del seen[:]
        mine = []
        DH.take_clone("IT", runner=lambda argv, **kw: mine.append(list(argv)) or subprocess.CompletedProcess(argv, 0, "", ""))
        ok("clone-and-landing-children-use-it: a test's own runner is used as given", mine[:1] == [["./sync"]] and not seen,
           (mine, seen))
    finally:
        OC.run = keep


def t_history_reads_and_the_filing_use_it():
    base = os.environ.get("OWN_CGROUP_BASE_DIR")
    if base:
        sys.path.insert(0, base)
    import importlib.util
    import build_match as BM
    import maturation as M
    import maturation_rescue as MR
    ing_py = os.path.join(base or HERE, "ingest.py") if base else os.path.join(HERE, "..", "Utils", "testq", "ingest.py")
    sys.path.insert(0, os.path.join(HERE, "..", "Utils", "testq"))
    spec = importlib.util.spec_from_file_location("own_cgroup_ingest", ing_py)
    ing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ing)
    root = os.path.join(TMP, "hist")
    os.makedirs(os.path.join(root, "src", "RimMandrake", "M"))
    subprocess.run(["git", "init", "-q", root], check=True)
    DAY, T0 = 86400, 1790000000

    def commit(n, t):
        with open(os.path.join(root, "src", "RimMandrake", "M", "a.xml"), "w") as f:
            f.write("<a>%d</a>\n" % n)
        env = dict(os.environ, GIT_COMMITTER_DATE="%d +0000" % t, GIT_AUTHOR_DATE="%d +0000" % t)
        subprocess.run(["git", "-C", root, "add", "-A"], check=True)
        subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", str(n)], env=env, check=True)
        return subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    for i in range(30):         # an old history: what the read must not walk
        commit(i, T0 - (60 - i) * DAY)
    at_line = commit(100, T0)
    a, skew, b = commit(101, T0 + 60), commit(102, T0 - 3600), commit(103, T0 + 120)      # skew: a clock an hour back
    late = commit(104, T0 + 999)
    seen, keep = [], OC.run

    def spy(argv, **kw):
        r = subprocess.run(argv, **kw)
        seen.append((list(argv), r.stdout))
        return r
    OC.run = spy
    try:
        got = M._git_log(root, T0, T0 + 120, "src/RimMandrake/M/")
        ok("history-reads-and-the-filing-use-it: the window is the same as a whole walk's",
           got == [(c, ["src/RimMandrake/M/a.xml"]) for c in (a, b)], (got, at_line, skew, late))
        ok("history-reads-and-the-filing-use-it: _git_log goes through run", len(seen) == 1, seen)
        ok("history-reads-and-the-filing-use-it: git does not walk the old history",
           len(seen) == 1 and 2 <= seen[0][1].count("\0") <= 5, [x[1].count("\0") for x in seen])
        del seen[:]
        n = MR.read_nudges(root, "M", T0)
        ok("history-reads-and-the-filing-use-it: read_nudges goes through run", len(seen) == 1 and len(n) >= 1, (seen, n))
        del seen[:]
        s = BM.source_sha(root, "M")
        ok("history-reads-and-the-filing-use-it: source_sha goes through run", len(seen) == 1 and s and late.startswith(s), (seen, s))
        del seen[:]
        rc, out = ing.rimflow("--help")
        ok("history-reads-and-the-filing-use-it: the ledger write goes through run, and answers",
           len(seen) == 1 and rc == 0 and "usage" in out, (len(seen), rc, out[:80]))
        del seen[:]
        MR.read_nudges(root, "M", T0, runner=lambda *x, **k: subprocess.CompletedProcess(x, 0, "", ""))
        ok("history-reads-and-the-filing-use-it: a test's own runner is used as given", not seen, seen)
    finally:
        OC.run = keep


def tick_lines(peak, wall, launched=None, n=0):
    u, t = TPA.UNIT, "2026-11-24T04:%02d:%02d-08:00 A" % (n // 60, n % 60)
    out = ["%s systemd[1]: Starting %s - x..." % (t, u)]
    if launched:
        out.append("%s python3[2]: Pyrelands   launch  launched      moving: run %s" % (t, launched))
    return out + ["%s systemd[1]: %s: Consumed 1min 2.5s CPU time over %s wall clock time, %s memory peak, 12M memory swap "
                  "peak." % (t, u, wall, peak)]


def t_outcome_check():
    def v(ticks):
        return TPA.verdict(TPA.ticks("\n".join(sum((tick_lines(*t, n=i) for i, t in enumerate(ticks)), []))))[0]
    quiet = [("500M", "50.2s")] * 20
    det, cert = "rm-detached-bench-x-1", "rm-cert-rerun-x-1"
    good = [("600M", "1min 2s", det)] * 3
    ok("outcome check: three launching ticks under the line holds", v(good + quiet) == 0)
    ok("outcome check: one launching tick at 1G fails", v(good[:2] + [("1G", "50s", det)] + quiet) == 1)
    ok("outcome check: an older launching tick at 1G is past", v([("1G", "50s", det)] + good + quiet) == 0)
    ok("outcome check: a certificate rerun is no helper launch", v(good[:2] + [("600M", "50s", cert)] + quiet) == 2)
    ok("outcome check: a quiet tick at the limit fails", v(good + quiet[:-1] + [("1G", "50s")]) == 1)
    ok("outcome check: a slow median wall fails", v(good + [("500M", "2min 30.5s")] * 20) == 1)
    ok("outcome check: too few launches is could-not-look", v(quiet) == 2)
    ok("outcome check: an empty journal is could-not-look", TPA.verdict(TPA.ticks("-- No entries --\n"))[0] == 2)
    ok("outcome check: spans and sizes", abs(TPA.secs("1h 2min 993ms") - 3720.993) < 1e-6 and TPA.mb("1.5G") == 1536
       and TPA.mb("512K") == .5, (TPA.secs("1h 2min 993ms"), TPA.mb("1.5G")))


def main():
    t_child_leaves_the_service_cgroup()
    t_child_dies_with_its_service()
    t_outside_a_service_runs_plain()
    t_scope_refused_runs_plain()
    t_clone_and_landing_children_use_it()
    t_history_reads_and_the_filing_use_it()
    t_outcome_check()
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d of %d checks failed" % (len(FAILS), len(SEEN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
