#!/usr/bin/env python3
"""selftest_run_tmp.py — the per-run TMPDIR (run_tmp.py, TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP) on a temp root only.

Proves: prepare makes a fresh 0700 dir; the launch argv carries TMPDIR/TMP/TEMP; a dead unit's dir goes, an active or
unknown one stays, a young one stays, a dir some process of ours uses (env or cwd) stays, a dead dir with a .git stays
as work, a crash's .reaping pin goes, a pid-name dir stays while its pid lives and goes after, drop(mine=True) frees
the owner's own dir, and relentless's tick hook journals what it removed.
"""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class R:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def fake_systemctl(states):
    def run(argv, **kw):
        units = argv[argv.index("--") + 1:]
        return R(0, "\n\n".join("Id=%s\nActiveState=%s" % (u, states.get(u, "inactive")) for u in units) + "\n")
    return run


def old(d, s=3600):
    """ctime cannot be set back, so the sweeps below look from LATER (now=LATER()) instead; the young dir is made last."""
    t = time.time() - s
    os.utime(d, (t, t))


def LATER():
    return time.time() + 3600


def main():
    base = tempfile.mkdtemp(prefix="selftest_run_tmp_")
    os.environ["RM_RUN_TMP_ROOT"] = os.path.join(base, "runs")
    import run_tmp
    rt = run_tmp.root()
    try:
        d = run_tmp.prepare("rm-relentless-work-abc-g1")
        ok(os.path.isdir(d) and (os.stat(d).st_mode & 0o777) == 0o700, "prepare makes a 0700 dir")
        open(os.path.join(d, "junk"), "w").close()
        d2 = run_tmp.prepare("rm-relentless-work-abc-g1")
        ok(d2 == d and os.listdir(d) == [], "prepare again starts empty (a relaunch inherits nothing)")
        try:
            run_tmp.path("../x")
            ok(False, "a name with a slash is refused")
        except ValueError:
            ok(True, "a name with a slash is refused")

        import role_launch
        argv = role_launch.launch_argv({"seat": "BENCH", "model": "m", "name": "R", "clone": base}, "u1", "msg", "o", "e",
                                       "claude", tmpdir=d)
        sets = [argv[i + 1] for i, x in enumerate(argv[:argv.index("--")]) if x == "--setenv"]
        ok(all(("%s=%s" % (k, d)) in sets for k in ("TMPDIR", "TMP", "TEMP")), "launch argv sets TMPDIR/TMP/TEMP before the command")
        argv = role_launch.launch_argv({"seat": "BENCH", "model": "m", "name": "R", "clone": base}, "u1", "msg", "o", "e",
                                       "claude")
        ok(not any(x.startswith("TMPDIR=") for x in argv), "no tmpdir, no TMPDIR (a fake runner's launch)")

        names = {"dead": "rm-relentless-work-dead-g1", "active": "rm-relentless-work-live-g1",
                 "unk": "rm-relentless-work-unk-g1", "young": "rm-relentless-work-young-g1",
                 "env": "rm-relentless-work-env-g1", "cwd": "rm-relentless-work-cwd-g1",
                 "work": "rm-relentless-work-repo-g1"}
        for n in names.values():
            run_tmp.prepare(n)
        os.makedirs(os.path.join(rt, names["work"], "clone", ".git"))
        pin = os.path.join(rt, ".reaping-999999999-gone")
        os.makedirs(os.path.join(pin, "x"))
        for k, n in names.items():
            if k != "young":
                old(os.path.join(rt, n))
        states = {names["active"] + ".service": "active"}

        def runner(argv, **kw):
            r = fake_systemctl(states)(argv, **kw)
            if names["unk"] + ".service" in argv:       # systemd cannot say for this one: a mismatched Id
                r.stdout = r.stdout.replace("Id=%s.service" % names["unk"], "Id=other.service")
            return r
        p_env = subprocess.Popen(["sleep", "30"], env=dict(os.environ, TMPDIR=os.path.join(rt, names["env"])))
        p_cwd = subprocess.Popen(["sleep", "30"], cwd=os.path.join(rt, names["cwd"]))
        try:
            time.sleep(0.2)
            out = run_tmp.sweep(now=LATER(), runner=runner)
        finally:
            p_env.kill()
            p_cwd.kill()
            p_env.wait()
            p_cwd.wait()
        left = set(os.listdir(rt))
        ok(names["dead"] not in left and names["dead"] in out["removed"], "a dead unit's dir is removed")
        ok(names["active"] in left, "an active unit's dir stays")
        ok(names["unk"] in left, "a unit systemd cannot report on stays")
        ok(names["young"] not in left, "a dead dir is removed once out of the grace window")
        ok(names["env"] in left, "a dir a process names in TMPDIR stays")
        ok(names["cwd"] in left, "a dir a process has as cwd stays")
        ok(names["work"] in left and names["work"] in out["work"], "a dead dir holding a git repo stays as work")
        ok(".reaping-999999999-gone" not in left, "a crash's .reaping pin of a dead pid is removed")
        ok(not out["errors"] and out["blind"] == 0, "the sweep saw every process (%s)" % out["errors"][:1])

        out = run_tmp.sweep(now=LATER(), runner=runner)
        left = set(os.listdir(rt))
        ok(names["env"] not in left and names["cwd"] not in left, "once the users exit their dirs go next sweep")

        run_tmp.prepare("rm-fresh-g1")
        out = run_tmp.sweep(runner=runner)
        ok("rm-fresh-g1" in os.listdir(rt) and out["young"] >= 1, "a dir inside the grace window stays (a launch in flight)")

        def failing(argv, **kw):
            return R(1, "")
        run_tmp.prepare("rm-x-g1")
        old(os.path.join(rt, "rm-x-g1"))
        run_tmp.sweep(now=LATER(), runner=failing)
        ok("rm-x-g1" in os.listdir(rt), "systemctl failing keeps every unit dir")

        child = subprocess.Popen(["sleep", "30"])
        pn = run_tmp.pid_name("tick", child.pid)
        run_tmp.prepare(pn)
        old(os.path.join(rt, pn))
        run_tmp.sweep(now=LATER(), runner=runner)
        ok(pn in os.listdir(rt), "a pid-name dir stays while its process runs")
        child.kill()
        child.wait()
        run_tmp.sweep(now=LATER(), runner=runner)
        ok(pn not in os.listdir(rt), "a pid-name dir goes after its process ends")

        mine = run_tmp.pid_name("tick")
        run_tmp.prepare(mine)
        r = run_tmp.drop(mine, runner=runner)
        ok(mine in os.listdir(rt), "drop without mine keeps the caller's own live pid dir (%s)" % (r or {}).get("live"))
        run_tmp.drop(mine, runner=runner, mine=True)
        ok(mine not in os.listdir(rt), "drop(mine=True) frees the owner's own dir")
        ok(run_tmp.drop(None) is None and run_tmp.drop("nope") is None, "drop of nothing is a no-op")

        # review fixes (GPT 2026-11-03): a reused live name, a pin's original name, an mmap-only user, a bare repo
        ln = "rm-relentless-work-reuse-g1"
        run_tmp.prepare(ln)
        open(os.path.join(rt, ln, "keep"), "w").close()
        try:
            run_tmp.prepare(ln, runner=fake_systemctl({ln + ".service": "active"}))
            ok(False, "prepare refuses a name whose unit is still active")
        except FileExistsError:
            ok(os.path.exists(os.path.join(rt, ln, "keep")), "prepare refuses a name whose unit is still active, and keeps its dir")

        pin2 = os.path.join(rt, ".reaping-999999999-origname")
        os.makedirs(pin2)
        old(pin2)
        kid = subprocess.Popen(["sleep", "30"], env=dict(os.environ, TMPDIR=os.path.join(rt, "origname")))
        try:
            time.sleep(0.2)
            run_tmp.sweep(now=LATER(), runner=runner)
            ok(os.path.isdir(pin2), "a crash's pin stays while a process names its ORIGINAL dir")
        finally:
            kid.kill()
            kid.wait()
        run_tmp.sweep(now=LATER(), runner=runner)
        ok(not os.path.exists(pin2), "the pin goes once that process ends")

        mm = "rm-relentless-work-mmap-g1"
        run_tmp.prepare(mm)
        with open(os.path.join(rt, mm, "blob"), "wb") as f:
            f.write(b"z" * 4096)
        old(os.path.join(rt, mm))
        code = ("import mmap,os,sys,time\nf=open(sys.argv[1],'r+b')\nm=mmap.mmap(f.fileno(),0)\nf.close()\n"
                "print('ready',flush=True)\ntime.sleep(30)\n")
        env = {k: v for k, v in os.environ.items() if k not in ("TMPDIR", "TMP", "TEMP")}
        kid = subprocess.Popen([sys.executable, "-c", code, os.path.join(rt, mm, "blob")], cwd="/", env=env,
                               stdout=subprocess.PIPE, text=True)
        try:
            kid.stdout.readline()
            run_tmp.sweep(now=LATER(), runner=runner)
            ok(mm in os.listdir(rt), "a dir only mmapped (no fd, no cwd, no TMPDIR) stays")
        finally:
            kid.kill()
            kid.wait()

        bare = "rm-relentless-work-bare-g1"
        run_tmp.prepare(bare)
        for sub in ("objects", "refs"):
            os.makedirs(os.path.join(rt, bare, "b.git", sub))
        open(os.path.join(rt, bare, "b.git", "HEAD"), "w").close()
        old(os.path.join(rt, bare))
        out = run_tmp.sweep(now=LATER(), runner=runner)
        ok(bare in os.listdir(rt) and bare in out["work"], "a dead dir holding a bare repo stays as work")
        a, b = os.path.join(base, "ra"), os.path.join(base, "rb")
        open(a, "w").write("pin")
        open(b, "w").write("new")
        ok(not run_tmp.restore(a, b) and open(b).read() == "new" and os.path.exists(a),
           "restore never replaces a name that exists again")
        os.unlink(b)
        ok(run_tmp.restore(a, b) and open(b).read() == "pin" and not os.path.exists(a), "restore renames when the name is free")
        ok(run_tmp.mounts_under("/") and not run_tmp.mounts_under(os.path.join(rt, bare)),
           "mounts_under sees / and finds nothing under a plain dir")

        import relentless

        class Store:
            def __init__(self):
                self.rows = []

            def journal(self, rec):
                self.rows.append(rec)

        class Fx:
            def sweep_run_tmp(self):
                return {"removed": ["a"], "errors": []}
        s, acts = Store(), []
        relentless.run_tmp_sweep(s, Fx(), time.time(), acts, "start")
        ok(s.rows and s.rows[0]["do"] == "run_tmp" and s.rows[0]["removed"] == ["a"], "the tick journals a removal")

        class Boom:
            def sweep_run_tmp(self):
                raise OSError("x")
        acts = []
        relentless.run_tmp_sweep(Store(), Boom(), time.time(), acts, "end")
        ok(acts and acts[0]["do"] == "error", "a raising sweep is an act, not the tick's end")
        acts = []
        relentless.run_tmp_sweep(Store(), object(), time.time(), acts, "end")
        ok(acts == [], "a fake fx without the hook is untouched")
    finally:
        subprocess.run(["rm", "-rf", base])
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
