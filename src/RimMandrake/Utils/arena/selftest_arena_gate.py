#!/usr/bin/env python3
"""selftest_arena_gate.py - arena_gate.py, each ARENA_GATE_BUILD_UNMEASURED_NEVER_PASSES criterion proven by FORCED
FAILURE against a throwaway git repo whose gate instruments (run_selftests/validate_patch/winbuild/deploy) are stubs.

  control        a clean candidate with a signed different-agent test record passes (a gate that never passes proves
                 nothing); the gate event it writes is signed and a hand-appended gate "pass" line is rejected
  placeholder    empty diff (only bookkeeping), TODO text, stub function, deleted selftest, dropped selftest def: fail
  scope          an out-of-area edit fails; arm bookkeeping (AGENTS.md) alongside a good change is stripped, not refused
  red test       a failing selftest fails the gate
  canary         a live task with a failed canary is `invalid` (not fail); no modcheck, a canary for another sha: invalid
  different agent builder == tester fails; no test_start fails; a hand-appended (unsigned) test_start is ignored;
                 a failing tester verdict fails; tester start with no end is UNMEASURED
  unmeasured     each step forced unrunnable (no tests map, tool absent, dump absent, dotnet absent, proof with no
                 runnable segment, tool edited by the diff, no token, no checkout, unfrozen task) reads UNMEASURED and
                 the overall verdict is never `pass`; verdict_of() with a missing step is not `pass`
  xml/csharp/deploy  bad xml fails; build failure fails; blocked plan fails; plan naming a mod outside the area fails
  location       running from inside an arm clone is refused
Writes only under a temp dir.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import arena_gate as G  # noqa: E402
import arena_tasks as A  # noqa: E402

FAILS = []
TD = "TO" + "DO"
UT = "src/RimMandrake/Utils/"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


STUB_SELFTESTS = '''import re, subprocess, sys
files = sys.argv[sys.argv.index("--only") + 1:]
bad = sum(1 for f in files if subprocess.run([sys.executable, f]).returncode != 0)
n = len(files)
print("PASS %d/%d  FAIL %d/%d  UNMEASURED 0/%d  CRASH 0/%d  SKIPPED 0/%d" % (n - bad, n, bad, n, n, n, n))
sys.exit(1 if bad else 0)
'''
STUB_VALIDATE = '''import sys
t = "".join(open(a).read() for a in sys.argv[1:] if a.endswith(".xml"))
if "BADXML" in t: print("1 error"); sys.exit(1)
if "UNMEAS" in t: print("UNMEASURED - empty def type"); sys.exit(0)
print("OK - 0 errors")
'''
STUB_WINBUILD = '''import os, sys
m = sys.argv[1]
src = open(os.path.join("src/RimMandrake", m, "Source", "A.cs")).read()
if "NODOTNET" in src: sys.exit("dotnet.exe not found; set WINBUILD_DOTNET")
if "BUILDFAIL" in src: print("error CS1002"); sys.exit(1)
print("BUILT")
'''
STUB_DEPLOY = '''import os, sys
m = sys.argv[sys.argv.index("--mod") + 1]
print("%s    mandrake.rsw.%s    ok" % (m, m.lower()))
if os.path.exists("src/RimMandrake/%s/ALSO" % m): print("OtherMod    mandrake.rsw.other    ok")
if os.path.exists("src/RimMandrake/%s/BLOCK" % m): print("  ! VANISHED ThingDef X\\nBLOCKING"); sys.exit(1)
'''
BASE = {
    UT + "run_selftests.py": STUB_SELFTESTS,
    "skills/rimworld-modding/scripts/validate_patch.py": STUB_VALIDATE,
    UT + "winbuild.py": STUB_WINBUILD,
    UT + "deploy_custom_mods.py": STUB_DEPLOY,
    UT + "foo.py": "def foo():\n    return 1\n",
    UT + "selftest_foo.py": "import sys\n\ndef t_a():\n    return 1\n\nsys.exit(0)\n",
    UT + "proof_ok.py": "import sys\nsys.exit(0)\n",
    UT + "proof_bad.py": "import sys\nsys.exit(3)\n",
    "src/RimMandrake/ModA/Patches/p.xml": "<Patch/>\n",
    "src/RimMandrake/ModA/Source/A.cs": "class A {}\n",
    "src/RimMandrake/ModA/About/x.txt": "x\n",
}
AREA = [UT + "foo*", UT + "selftest_foo*", "src/RimMandrake/ModA/*"]
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True, env=ENV).stdout.strip()


class Ctx:
    def __init__(self, tmp, name, live="none", proof="python3 src/RimMandrake/Utils/proof_ok.py"):
        self.root = tmp / name
        os.environ["ARENA_ROOT"] = str(self.root / "arena")
        os.environ["ARENA_CLONES"] = str(self.root / "clones")
        os.environ["ARENA_EVENT_TOKEN_FILE"] = str(self.root / "secret" / "event_token")
        self.p = A.paths()
        L.init_token(self.p)
        self.w = L.HarnessWriter(self.p)
        self.repo = self.root / "repo"
        self.repo.mkdir(parents=True)
        git(self.repo, "init", "-q")
        self.base = self.commit(BASE, "base")
        self.task = {"id": "T1", "area": AREA, "proof": proof, "live": live}
        self.dump = self.root / "dump"
        self.dump.mkdir()

    def commit(self, changes, msg="c"):
        for path, content in changes.items():
            f = self.repo / path
            if content is None:
                f.unlink()
            else:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(content)
        git(self.repo, "add", "-A", "--", ".")
        git(self.repo, "commit", "-q", "-m", msg)
        return git(self.repo, "rev-parse", "HEAD")

    def emit(self, event, sha, **kw):
        return self.w.emit("armx", event, lane="L", run_id="r", task="T1", sha=sha, **kw)

    def records(self, head, builder="B1", tester="T9", test="pass"):
        self.emit("build_end", head, detail={"builder": builder})
        if tester:
            self.emit("test_start", head, detail={"tester": tester})
            if test:
                self.emit("test_end", head, verdict=test, detail={"tester": tester})

    def gate(self, head, task=None, **kw):
        kw.setdefault("defs_roots", [])
        g = G.Gate(task or self.task, self.base, head, "armx", self.repo, self.p, dump=kw.pop("dump", str(self.dump)),
                   writer=self.w, **kw)
        return g.execute()


GOOD = {UT + "foo.py": "def foo():\n    return 2\n", UT + "selftest_foo.py": "import sys\n\ndef t_a():\n    return 1\n\n"
        "def t_b():\n    return 2\n\nsys.exit(0)\n"}


def st(rec, s):
    return rec["steps"][s]["status"]


def t_control(tmp):
    c = Ctx(tmp, "ctl")
    h = c.commit(GOOD)
    c.records(h)
    r = c.gate(h)
    check(r["verdict"] == "pass" and r["passed"], "control: clean candidate with different-agent test record passes (%s)"
          % {s: st(r, s) for s in G.STEPS})
    check(r["verdict"] in G.VERDICTS and set(r["steps"]) == set(G.STEPS), "output is one record, verdict in {pass,fail,invalid}")
    check(r["recorded"] and any(x["event"] == "gate" and x["verdict"] == "pass" for x in L.verify(c.p, "armx")["accepted"]),
          "gate result is a SIGNED gate event")
    f = L.arm_file(c.p, "armx")
    with open(f, "a") as fh:
        fh.write(json.dumps({"ts": "2026-10-30T00:00:00Z", "arm": "armx", "lane": "L", "run_id": "r", "task": "T9",
                             "event": "gate", "verdict": "pass", "sha": h}, sort_keys=True) + "\n")
    v = L.verify(c.p, "armx")
    check(len(v["rejected"]) == 1 and all(x.get("task") != "T9" for x in v["accepted"]),
          "a hand-written gate pass line by the builder is REJECTED (not self-reportable)")
    bk = dict(GOOD); bk["AGENTS.md"] = "notes\n"; bk["infrastructure/state/ledger/events/X.jsonl"] = "{}\n"
    c2 = Ctx(tmp, "ctl2"); h2 = c2.commit(bk); c2.records(h2); r2 = c2.gate(h2)
    check(r2["verdict"] == "pass" and st(r2, "scope") == "PASS", "arm bookkeeping (AGENTS.md, ledger shard) is stripped, not refused")


def t_placeholder(tmp):
    c = Ctx(tmp, "ph")
    h = c.commit({"AGENTS.md": "only notes\n"})
    c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "placeholders") == "FAIL" and "empty" in r["steps"]["placeholders"]["why"],
          "empty diff (bookkeeping only) FAILS")
    cases = {
        "todo": ({UT + "foo.py": "def foo():\n    # %s later\n    return 2\n" % TD}, "TODO text"),
        "stub_pass": ({UT + "foo.py": "def foo():\n    return 1\n\ndef bar():\n    pass\n"}, "pass stub"),
        "stub_ni": ({UT + "foo.py": "def foo():\n    return 1\n\ndef bar():\n    raise Not" + "ImplementedError\n"}, "NotImplemented stub"),
        "deltest": ({UT + "selftest_foo.py": None}, "deleted selftest"),
        "dropdef": ({UT + "selftest_foo.py": "import sys\nsys.exit(0)\n"}, "dropped selftest def"),
    }
    for k, (ch, label) in cases.items():
        cc = Ctx(tmp, "ph_" + k); hh = cc.commit(ch); cc.records(hh); rr = cc.gate(hh)
        check(rr["verdict"] == "fail" and st(rr, "placeholders") == "FAIL", "%s FAILS the gate (%s)" % (label, rr["steps"]["placeholders"]["why"]))


def t_scope_tests(tmp):
    c = Ctx(tmp, "sc")
    ch = dict(GOOD); ch["src/RimMandrake/Other/Defs/d.xml"] = "<Defs/>\n"
    h = c.commit(ch); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "scope") == "FAIL" and "src/RimMandrake/Other/Defs/d.xml" in r["steps"]["scope"]["outside"],
          "out-of-area edit FAILS scope and names the path")
    c = Ctx(tmp, "red")
    h = c.commit({UT + "selftest_foo.py": "import sys\nsys.exit(1)\n\ndef t_a():\n    return 1\n"}); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "tests") == "FAIL", "a red selftest FAILS the gate (%s)" % r["steps"]["tests"]["why"])
    c = Ctx(tmp, "pf", proof="python3 src/RimMandrake/Utils/proof_bad.py")
    h = c.commit(GOOD); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "proof") == "FAIL", "the task's own proof exiting non-zero FAILS")


def t_live(tmp):
    def live(canary_verdict="pass", modcheck=True, sha_override=None, release="pass", with_canary=True, tag="x"):
        c = Ctx(tmp, "lv_" + tag, live="minimal")
        h = c.commit(GOOD); c.records(h)
        if with_canary:
            c.emit("canary", sha_override or h, verdict=canary_verdict, detail={"modcheck": modcheck} if modcheck else {})
            if release:
                c.emit("live_release", sha_override or h, verdict=release)
        return c.gate(h)
    r = live(tag="ok")
    check(r["verdict"] == "pass" and st(r, "live") == "PASS", "control: live task with passed canary, modcheck and live pass is pass")
    r = live("fail", tag="dead")
    check(r["verdict"] == "invalid" and st(r, "live") == "INVALID", "dead-colony canary -> INVALID (never fail, never pass)")
    r = live(modcheck=False, tag="nm")
    check(r["verdict"] == "invalid" and st(r, "live") == "INVALID", "no modcheck with the deploy -> invalid")
    r = live(sha_override="a" * 40, tag="sha")
    check(r["verdict"] == "invalid" and st(r, "live") == "INVALID", "canary record for another sha -> invalid")
    r = live(release="fail", tag="rf")
    check(r["verdict"] == "fail" and st(r, "live") == "FAIL", "canary ok but live verdict fail -> fail")
    r = live(with_canary=False, tag="none")
    check(r["verdict"] == "invalid" and st(r, "live") == "UNMEASURED", "no live record at all -> UNMEASURED, not pass")


def t_agents(tmp):
    c = Ctx(tmp, "ag1"); h = c.commit(GOOD); c.records(h, builder="A1", tester="A1"); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "test_record") == "FAIL", "builder id == tester id FAILS (%s)" % r["steps"]["test_record"]["why"])
    c = Ctx(tmp, "ag2"); h = c.commit(GOOD); c.records(h, tester=None); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "test_record") == "FAIL", "no test_start at all FAILS")
    c = Ctx(tmp, "ag3"); h = c.commit(GOOD); c.records(h, tester=None)
    with open(L.arm_file(c.p, "armx"), "a") as fh:
        fh.write(json.dumps({"ts": "2026-10-30T00:00:00Z", "arm": "armx", "lane": "L", "run_id": "r", "task": "T1", "event": "test_start",
                             "sha": h, "detail": {"tester": "FAKE"}}, sort_keys=True) + "\n")
    r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "test_record") == "FAIL", "a hand-appended unsigned test_start is ignored -> FAIL")
    c = Ctx(tmp, "ag4"); h = c.commit(GOOD); c.records(h, test="fail"); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "test_record") == "FAIL", "different-agent tester verdict fail -> fail")
    c = Ctx(tmp, "ag5"); h = c.commit(GOOD); c.records(h, test=None); r = c.gate(h)
    check(r["verdict"] == "invalid" and st(r, "test_record") == "UNMEASURED", "tester started, no verdict yet -> UNMEASURED")
    c = Ctx(tmp, "ag6"); h = c.commit(GOOD); c.emit("test_start", h, detail={"tester": "T9"}); r = c.gate(h)
    check(r["verdict"] != "pass" and st(r, "test_record") == "UNMEASURED", "no build_end (builder unknown) -> UNMEASURED")
    c = Ctx(tmp, "ag7"); h = c.commit(GOOD); c.records(h, builder="A1", tester="A2")
    other = c.commit({UT + "foo.py": "def foo():\n    return 3\n"}); r = c.gate(other)
    check(r["verdict"] != "pass" and st(r, "test_record") != "PASS", "a test record for an EARLIER sha does not cover a new head")


def t_unmeasured(tmp):
    def one(label, changes, mutate=None, expect_step=None, task=None, dump=None, records=True):
        c = Ctx(tmp, "um_" + label)
        if mutate:
            mutate(c)
            c.base = git(c.repo, "rev-parse", "HEAD")
        h = c.commit(changes)
        if records:
            c.records(h)
        r = c.gate(h, task=task(c) if task else None, dump=dump(c) if dump else None)
        check(r["verdict"] != "pass" and (expect_step is None or st(r, expect_step) == "UNMEASURED") and
              (expect_step is None or expect_step in r["unmeasured"]),
              "%s -> %s UNMEASURED, gate does not pass (verdict %s)" % (label, expect_step, r["verdict"]))
        return r
    one("no_selftest_maps", {UT + "lonely.py": "def f():\n    return 1\n"}, expect_step="tests",
        task=lambda c: dict(c.task, area=[UT + "lonely*"]))
    one("runner_absent", GOOD, mutate=lambda c: c.commit({UT + "run_selftests.py": None}), expect_step="tests")
    one("tool_edited_by_diff", dict(GOOD, **{UT + "run_selftests.py": "import sys\nprint('PASS 9/9')\nsys.exit(0)\n"}),
        expect_step="tests", task=lambda c: dict(c.task, area=c.task["area"] + [UT + "run_selftests.py"]))
    one("dump_absent", dict(GOOD, **{"src/RimMandrake/ModA/Patches/p.xml": "<Patch>1</Patch>\n"}), expect_step="xml",
        dump=lambda c: str(c.root / "nope"))
    one("empty_deftype", dict(GOOD, **{"src/RimMandrake/ModA/Defs/d.xml": "<Defs>UNMEAS</Defs>\n"}), expect_step="xml")
    one("no_dotnet", dict(GOOD, **{"src/RimMandrake/ModA/Source/A.cs": "class A { /* NODOTNET */ }\n"}), expect_step="csharp")
    one("proof_prose_only", GOOD, expect_step="proof", task=lambda c: dict(c.task, proof="the judge runs 1 held-back selftest(s)"))
    c = Ctx(tmp, "um_nocheckout"); h = c.commit(GOOD); c.records(h)
    g = G.Gate(c.task, c.base, "f" * 40, "armx", c.repo, c.p, writer=c.w); r = g.execute()
    check(r["verdict"] == "invalid" and set(r["unmeasured"]) == set(G.STEPS), "head sha missing from the repo: every step UNMEASURED, invalid")
    c = Ctx(tmp, "um_notoken"); h = c.commit(GOOD); c.records(h)
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(c.root / "gone" / "event_token")
    g = G.Gate(c.task, c.base, h, "armx", c.repo, c.p, dump=str(c.dump), defs_roots=[]); r = g.execute()
    check(r["verdict"] == "invalid" and st(r, "test_record") == "UNMEASURED" and not r["recorded"],
          "no harness token: test_record UNMEASURED, verdict not pass, result NOT recorded as if signed")
    r = G.verdict_of({s: {"status": "PASS"} for s in G.STEPS if s != "proof"})
    check(r == "invalid", "verdict_of(): a missing step is UNMEASURED -> invalid, never pass")
    check(G.verdict_of({s: {"status": "PASS"} for s in G.STEPS}) == "pass", "verdict_of(): all PASS -> pass (control)")
    check(G.verdict_of({**{s: {"status": "NA"} for s in G.STEPS}}) == "invalid", "verdict_of(): all NA never passes (scope/placeholders/test_record must PASS)")
    check(G.verdict_of({**{s: {"status": "PASS"} for s in G.STEPS}, "xml": {"status": "FAIL"}, "live": {"status": "INVALID"}}) == "fail",
          "verdict_of(): a FAIL outranks INVALID")


def t_tools(tmp):
    c = Ctx(tmp, "x1"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/Patches/p.xml": "<Patch>BADXML</Patch>\n"})); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "xml") == "FAIL", "validate_patch errors FAIL")
    c = Ctx(tmp, "x2"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/Patches/p.xml": "<Patch>fine</Patch>\n"})); c.records(h); r = c.gate(h)
    check(r["verdict"] == "pass" and st(r, "xml") == "PASS" and st(r, "deploy_plan") == "PASS", "control: clean xml passes xml and deploy plan")
    c = Ctx(tmp, "c1"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/Source/A.cs": "class A { /* BUILDFAIL */ }\n"})); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "csharp") == "FAIL", "a build failure FAILS")
    c = Ctx(tmp, "d1"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/BLOCK": "x\n"})); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "deploy_plan") == "FAIL", "a BLOCKING deploy plan FAILS")
    c = Ctx(tmp, "d2"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/ALSO": "x\n"})); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "deploy_plan") == "FAIL" and "OtherMod" in r["steps"]["deploy_plan"]["why"],
          "a plan touching a mod outside the task area FAILS")


def t_cli_location(tmp):
    c = Ctx(tmp, "cli")
    inside = c.root / "clones" / "armx" / "arena_gate.py"
    inside.parent.mkdir(parents=True)
    inside.write_text("x")
    try:
        G.refuse_arm_location(str(inside)); ok = False
    except G.GateError:
        ok = True
    check(ok, "running the gate from inside an arm clone is refused")
    try:
        G.refuse_arm_location(G.__file__); ok2 = True
    except G.GateError:
        ok2 = False
    check(ok2, "running from the judge's own checkout is allowed (control)")
    out = subprocess.run([sys.executable, str(HERE / "arena_gate.py"), "--task", "NOPE", "--base", "a" * 40, "--head", "b" * 40,
                          "--arm", "armx"], capture_output=True, text=True, env=dict(os.environ))
    try:
        rec = json.loads(out.stdout)
    except ValueError:
        rec = {}
    check(out.returncode == 2 and rec.get("verdict") == "invalid" and rec.get("passed") is False,
          "CLI: an unfrozen task -> invalid, exit 2 (%s)" % out.stdout[:80])


def main():
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE")}
    tmp = Path(tempfile.mkdtemp(prefix="arena_gate_st_"))
    try:
        for t in (t_control, t_placeholder, t_scope_tests, t_live, t_agents, t_unmeasured, t_tools, t_cli_location):
            t(tmp)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
