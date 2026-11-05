#!/usr/bin/env python3
"""CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS: the supervisor's offbox adapters for what the Marker's box withholds by design -
git history at the candidate sha, MandrakeWorkflows-dev through gh, other processes' /proc.

G1 fill_argv fills {sha}/{repo} from supervisor values only and refuses an unknown slot, a missing value or a value of the
   wrong shape (worker text cannot ride in a slot); G2 offbox_readings never runs an adapter it cannot fill, and hands the
   runner the filled argv; G3 the check launch passes the candidate sha and the clean clone; G4 every rules adapter names
   known slots only and the new adapters exist with the shape each hold needs; G5 git_log_candidate / git_stat_candidate,
   run for real on a fixture repo, read history AT {sha} (a later commit is absent); G6 proc_cwds, run for real, shows a
   process under /tmp with its pid and never its later argv. The gh readings need the network the box lacks: their argv
   shape is checked here, and the reading itself is the contract's --offbox output."""
import inspect
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R            # noqa: E402
import relentless_wall as W       # noqa: E402

FAILS = []


def ok(c, msg):
    print(("PASS " if c else "FAIL ") + msg)
    if not c:
        FAILS.append(msg)


SHA = "0123456789abcdef0123456789abcdef01234567"
RULES = json.load(open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8"))


def t_fill():
    argv, why = W.fill_argv(["git", "-C", "{repo}", "log", "{sha}", "--x={sha}"], {"sha": SHA, "repo": "/r/c"})
    ok(why is None and argv == ["git", "-C", "/r/c", "log", SHA, "--x=" + SHA], "G1 slots fill: %s %s" % (argv, why))
    for vals, slot in (({"sha": "abc; rm -rf ~", "repo": "/r"}, "sha"), ({"sha": SHA[:12], "repo": "/r"}, "sha"),
                       ({"sha": SHA, "repo": "rel/path"}, "repo"), ({"sha": SHA, "repo": "/r\n/x"}, "repo"),
                       ({"repo": "/r"}, "sha"), (None, "sha")):
        argv, why = W.fill_argv(["x", "{%s}" % slot], vals)
        ok(argv is None and "{%s}" % slot in (why or ""), "G1 a bad or missing {%s} refuses: %r -> %s" % (slot, vals, why))
    argv, why = W.fill_argv(["cat", "{home}"], {"sha": SHA, "repo": "/r", "home": "/home"})
    ok(argv is None and "not a supervisor value" in (why or ""), "G1 an unknown slot refuses: %s" % why)
    argv, why = W.fill_argv(["echo", "{0} %s"], {})
    ok(argv == ["echo", "{0} %s"], "G1 a token with no slot passes untouched")


def t_readings():
    ran = []

    class Fx:
        def run_offbox(self, name, adapter, timeout):
            ran.append((name, adapter["argv"]))
            return {"cmd": name, "exit": 0, "out": "x", "at": 0}

    r = {"offbox_max_s": 30, "offbox_adapters": {"a_log": {"what": "w", "argv": ["git", "-C", "{repo}", "log", "{sha}"]}}}
    got = R.offbox_readings(Fx(), {"offbox": ["a_log"]}, r)
    ok(not ran and "{" in str(got[0]["exit"]) and got[0]["out"] == "", "G2 no values: the adapter is not run: %s" % got)
    got = R.offbox_readings(Fx(), {"offbox": ["a_log"]}, r, {"sha": "nothex", "repo": "/c"})
    ok(not ran, "G2 a malformed sha: the adapter is not run")
    got = R.offbox_readings(Fx(), {"offbox": ["a_log"]}, r, {"sha": SHA, "repo": "/c"})
    ok(ran == [("a_log", ["git", "-C", "/c", "log", SHA])] and got[0]["exit"] == 0, "G2 filled argv reaches the runner: %s" % ran)
    ok(r["offbox_adapters"]["a_log"]["argv"][2] == "{repo}", "G2 the rules' own argv is not mutated")


def t_launch():
    src = inspect.getsource(R)
    ok('offbox_readings(fx, st["contract"], r, {"sha": c["sha"], "repo": clean})' in src,
       "G3 the check launch passes the candidate sha and the clean clone to the offbox readings")


def t_rules():
    known = W.adapters(RULES)
    for name, a in known.items():
        slots = {s for t in a["argv"] for s in W._SLOT.findall(t)}
        ok(slots <= set(W._SLOT_OK), "G4 %s names known slots only: %s" % (name, sorted(slots)))
        ok(W._NAME.match(name) is not None and bool(a.get("what")), "G4 %s has an adapter name and a what" % name)
    need = {"git_log_candidate": ["{repo}", "{sha}"], "git_stat_candidate": ["{repo}", "{sha}"],
            "git_origin_main": ["{repo}", "ls-remote"], "mw_dev_relentless_paths": ["gh", "MandrakeWorkflows-dev"],
            "mw_dev_relentless_readme": ["relentless/README.md"], "mw_dev_workers_readme": ["relentless/workers/README.md"],
            "mw_dev_builder_judge": ["relentless/workers/BUILDER_JUDGE.md"], "proc_cwds": ["python3", "-I"]}
    for name, bits in need.items():
        a = known.get(name)
        ok(a is not None and all(any(b in t for t in a["argv"]) for b in bits), "G4 adapter %s exists with %s" % (name, bits))
    for name in ("mw_dev_relentless_readme", "mw_dev_workers_readme", "mw_dev_builder_judge"):
        a = known.get(name) or {"argv": []}
        ok(a["argv"][:2] == ["gh", "api"] and "Accept: application/vnd.github.raw" in a["argv"], "G4 %s is a raw gh api read" % name)
    ok(all(W.check_offbox_names([n], RULES) == [n] for n in need), "G4 contract/unhold accept the new names")


def git(d, *a):
    return subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, check=True,
                          env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                   GIT_COMMITTER_EMAIL="t@t")).stdout.strip()


def t_git():
    known = W.adapters(RULES)
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", d], check=True)
        open(os.path.join(d, "a.txt"), "w").write("a\n")
        git(d, "add", "a.txt")
        git(d, "commit", "-q", "-m", "first commit FIXTURE_ONE")
        one = git(d, "rev-parse", "HEAD")
        open(os.path.join(d, "b.txt"), "w").write("b\n")
        git(d, "add", "b.txt")
        git(d, "commit", "-q", "-m", "second commit FIXTURE_TWO")
        two = git(d, "rev-parse", "HEAD")
        for name in ("git_log_candidate", "git_stat_candidate"):
            got = R.offbox_readings(type("Fx", (), {"run_offbox": lambda s, n, a, t: R.run_bounded(n, a, t)})(),
                                    {"offbox": [name]}, RULES, {"sha": one, "repo": d})[0]
            ok(got["exit"] == 0 and one in got["out"] and "FIXTURE_ONE" in got["out"], "G5 %s reads the candidate commit: %s"
               % (name, got["exit"]))
            ok(two not in got["out"] and "FIXTURE_TWO" not in got["out"], "G5 %s reads AT {sha}: a later commit is absent" % name)
            if name == "git_stat_candidate":
                ok("a.txt" in got["out"], "G5 git_stat_candidate names the files touched")
            got = R.offbox_readings(type("Fx", (), {"run_offbox": lambda s, n, a, t: R.run_bounded(n, a, t)})(),
                                    {"offbox": [name]}, RULES, {"sha": two, "repo": d})[0]
            ok(two in got["out"] and one in got["out"], "G5 %s at the later sha reads both" % name)


def t_proc():
    a = W.adapters(RULES)["proc_cwds"]
    with tempfile.TemporaryDirectory(dir="/tmp") as d:
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)", "SECRET_PROMPT_WORDS"], cwd=d)
        try:
            got = R.run_bounded("proc_cwds", a, 30)
        finally:
            p.kill()
            p.wait()
    line = [x for x in got["out"].splitlines() if x.split(" ", 1)[0] == str(p.pid)]
    ok(got["exit"] == 0 and line and os.path.realpath(d) in line[0] and " -c" in line[0],
       "G6 proc_cwds shows the fixture process with its cwd: %s" % (line or got["out"][-200:]))
    ok("SECRET_PROMPT_WORDS" not in got["out"], "G6 proc_cwds never carries argv past the second token")


if __name__ == "__main__":
    for t in (t_fill, t_readings, t_launch, t_rules, t_git, t_proc):
        t()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
