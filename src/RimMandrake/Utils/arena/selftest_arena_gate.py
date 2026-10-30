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
import vhelper
t = "".join(open(a).read() for a in sys.argv[1:] if a.endswith(".xml"))
if "BADXML" in t: print("1 error"); sys.exit(1)
if "UNMEAS" in t: print("UNMEASURED - empty def type"); sys.exit(0)
if "SILENT" in t: sys.exit(0)
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
    "skills/rimworld-modding/scripts/vhelper.py": "X = 1\n",
    UT + "winbuild.py": STUB_WINBUILD,
    UT + "deploy_custom_mods.py": STUB_DEPLOY,
    UT + "foo.py": "def foo():\n    return 1\n",
    UT + "selftest_foo.py": "import foo\n\ndef t_a():\n    assert foo.foo() >= 1\n\nt_a()\n",
    UT + "proof_ok.py": "import sys\nimport foo\nsys.exit(0)\n",
    UT + "proof_bad.py": "import sys\nimport foo\nsys.exit(3)\n",
    UT + "unrelated.py": "import sys\nsys.exit(0)\n",
    "src/RimMandrake/ModA/Patches/p.xml": "<Patch/>\n",
    "src/RimMandrake/ModA/Source/A.cs": "class A {}\n",
    "src/RimMandrake/ModA/About/About.xml": "<ModMetaData/>\n",
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


GOOD = {UT + "foo.py": "def foo():\n    return 2\n", UT + "selftest_foo.py": "import foo\n\ndef t_a():\n    assert foo.foo() >= 1\n\n"
        "def t_b():\n    assert foo.foo() == 2\n\nt_a()\nt_b()\n"}


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
    check(st(r, "deploy_plan") == "NA", "a Utils-only diff has deploy_plan NA, not UNMEASURED (%s)" % r["steps"]["deploy_plan"]["why"])
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
    src = G.RUNNER_SRC                    # the harness runner starts but leaves no record (as os._exit(0) would)
    G.RUNNER_SRC = "import os\nos._exit(0)\n"
    try:
        one("runner_no_record", GOOD, expect_step="tests")
    finally:
        G.RUNNER_SRC = src
    one("checkout_runner_absent_is_irrelevant", GOOD, mutate=lambda c: c.commit({UT + "run_selftests.py": None}),
        expect_step=None, records=False)
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

def t_sandbox(tmp):
    """(1) arm code the gate runs cannot reach the signing key, the harness env or the real HOME."""
    c = Ctx(tmp, "sb")
    tok = str(L.token_path(c.p))
    probe = ("import os, foo\n\ndef t_a():\n    assert foo.foo() == 2\n\ndef t_env():\n"
             "    assert not any(k.startswith('ARENA') for k in os.environ), 'harness env leaked'\n"
             "    assert os.environ.get('HOME') != %r, 'real HOME'\n"
             "    assert not os.path.exists(%r), 'token visible'\n"
             "    assert not os.path.exists(os.path.expanduser('~/.local/state/rimmandrake/arena_harness/event_token'))\n"
             "    assert not os.path.isdir(%r) or not os.listdir(%r), 'arena judge dir visible'\n\nt_a()\nt_env()\n"
             % (str(Path.home()), tok, str(c.p["root"] / "judge" / "gate"), str(c.p["root"] / "judge" / "gate")))
    h = c.commit({UT + "foo.py": "def foo():\n    return 2\n", UT + "selftest_foo.py": probe}); c.records(h); r = c.gate(h)
    check(r["verdict"] == "pass" and st(r, "tests") == "PASS",
          "sandboxed selftest sees no token, no ARENA_* env, no real HOME (%s %s)" % (st(r, "tests"),
                                                                                   r["steps"]["tests"].get("findings")))
    saved = shutil.which
    G.shutil.which = lambda n, _s=saved: None if n == "bwrap" else _s(n)
    try:
        c2 = Ctx(tmp, "sb2"); h2 = c2.commit(GOOD); c2.records(h2); r2 = c2.gate(h2)
    finally:
        G.shutil.which = saved
    check(r2["verdict"] == "invalid" and st(r2, "tests") == "UNMEASURED" and st(r2, "proof") == "UNMEASURED",
          "no bwrap: sandboxed steps UNMEASURED, arm code never runs beside the key")


def t_runner(tmp):
    """(2) code under test cannot turn red green: excepthook, stdlib shadows, harness/instrument-import edits."""
    hook = ("import os, sys\nsetattr(sys, 'excepth' + 'ook', lambda *a: getattr(os, '_ex' + 'it')(0))\n\n"
            "def foo():\n    return 2\n")
    red = "import foo\n\ndef t_a():\n    assert foo.foo() == 3\n\nt_a()\n"
    c = Ctx(tmp, "rn1"); h = c.commit({UT + "foo.py": hook, UT + "selftest_foo.py": red}); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "tests") == "FAIL",
          "an (obfuscated) excepthook exiting 0 does not hide a red selftest: tests FAIL (%s)" % st(r, "tests"))
    plain = "import os, sys\nsys.excepthook = lambda *a: os._exit(0)\n\ndef foo():\n    return 2\n"
    c = Ctx(tmp, "rn2"); h = c.commit({UT + "foo.py": plain, UT + "selftest_foo.py": red}); c.records(h); r = c.gate(h)
    check(r["verdict"] != "pass" and st(r, "tests") != "PASS", "a plain excepthook in the diff is never a pass")
    shadow = "import os\nprint('PASS 1/1  FAIL 0/1')\nos._exit(0)\n"
    task = {"id": "T1", "area": [UT + "*"], "proof": "python3 src/RimMandrake/Utils/proof_ok.py", "live": "none"}
    for k, path in (("cf", UT + "concurrent/futures.py"), ("js", UT + "json.py"), ("sc", UT + "sitecustomize.py"),
                    ("pth", UT + "x.pth")):
        c = Ctx(tmp, "rn_" + k); h = c.commit({UT + "foo.py": "def foo():\n    return 2\n", UT + "selftest_foo.py": red,
                                               path: shadow}); c.records(h); r = c.gate(h, task=task)
        check(r["verdict"] == "fail" and st(r, "scope") == "FAIL" and st(r, "tests") != "PASS",
              "a new stdlib/hook shadow %s FAILS scope and the red test stays red (%s)" % (path, st(r, "tests")))
    task2 = dict(task, area=task["area"] + ["skills/*", "src/RimMandrake/ModA/*"])
    for k, extra in (("vh", {"skills/rimworld-modding/scripts/vhelper.py": "X = 2\n"}),
                     ("ar", {UT + "arena/x.py": "X = 1\n"})):
        c = Ctx(tmp, "rn_" + k)
        h = c.commit(dict(GOOD, **extra, **{"src/RimMandrake/ModA/Patches/p.xml": "<Patch>fine</Patch>\n"}))
        c.records(h); r = c.gate(h, task=task2)
        check(st(r, "xml") == "UNMEASURED" and r["verdict"] != "pass",
              "a diff editing %s (instrument import / harness code) leaves xml UNMEASURED" % list(extra)[0])


def t_ids(tmp):
    """(4) builder ids are compared normalised; every builder of the task is excluded; confusables refused."""
    for k, tester in (("case", "buildera"), ("space", "BuilderA "), ("cyr", "ВuilderA"), ("full", "ＢuilderA"),
                      ("zw", "Builder​A"), ("zero", "Bui1derA")):
        c = Ctx(tmp, "id_" + k); h = c.commit(GOOD); c.records(h, builder="BuilderA", tester=tester); r = c.gate(h)
        check(r["verdict"] == "fail" and st(r, "test_record") == "FAIL",
              "tester %r vs builder 'BuilderA' is the same agent: FAIL" % tester)
    c = Ctx(tmp, "id_many"); h = c.commit(GOOD)
    c.emit("build_end", h, detail={"builder": "A1"}); c.emit("build_end", h, detail={"builder": "C1"})
    c.emit("test_start", h, detail={"tester": "A1"}); c.emit("test_end", h, verdict="pass", detail={"tester": "A1"})
    r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "test_record") == "FAIL", "an EARLIER builder of the task testing it: FAIL")
    c = Ctx(tmp, "id_short"); h = c.commit(GOOD)
    c.emit("build_end", h[:12], detail={"builder": "B1"}); c.emit("test_start", h[:12], detail={"tester": "T9"})
    c.emit("test_end", h[:12], verdict="pass", detail={"tester": "T9"}); r = c.gate(h)
    check(r["verdict"] == "pass", "records naming head by a 12-char prefix count (control; %s)" % st(r, "test_record"))
    check(G.sha_match(h[:12], h) and not G.sha_match(h[:11], h) and not G.sha_match("", h), "sha prefix needs >= 12 chars")


def t_weakened(tmp):
    """(5) a changed selftest may not lose executed checks; constant assertions are refused."""
    base_st = "import foo\n\ndef t_a():\n    assert foo.foo() >= 1\n\ndef t_b():\n    assert foo.foo() < 9\n\nt_a()\nt_b()\n"
    cases = {
        "assert_true": ("import foo\n\ndef t_a():\n    assert True\n\ndef t_b():\n    assert foo.foo() < 9\n\nt_a()\nt_b()\n",
                        "placeholders"),
        "not_called": ("import foo\n\ndef t_a():\n    assert foo.foo() >= 1\n\ndef t_b():\n    assert foo.foo() < 9\n", "tests"),
        "early_exit": ("import sys, foo\nsys.exit(0)\n\ndef t_a():\n    assert foo.foo() >= 1\n\ndef t_b():\n"
                       "    assert foo.foo() < 9\n\nt_a()\nt_b()\n", "tests"),
        "check_true": ("import foo\n\ndef check(ok, m):\n    assert ok, m\n\ndef t_a():\n    check(True, 'x')\n\ndef t_b():\n"
                       "    assert foo.foo() < 9\n\nt_a()\nt_b()\n", "placeholders"),
    }
    for k, (head, where) in cases.items():
        c = Ctx(tmp, "wk_" + k); c.commit({UT + "selftest_foo.py": base_st}); c.base = git(c.repo, "rev-parse", "HEAD")
        h = c.commit({UT + "foo.py": "def foo():\n    return 2\n", UT + "selftest_foo.py": head}); c.records(h); r = c.gate(h)
        check(r["verdict"] == "fail" and st(r, where) == "FAIL", "weakened selftest (%s) FAILS %s (%s)" % (k, where, st(r, where)))
    c = Ctx(tmp, "wk_new"); h = c.commit(dict(GOOD, **{UT + "selftest_foo2.py": "assert True\n"})); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "placeholders") == "FAIL", "a new `assert True`-only selftest FAILS")
    c = Ctx(tmp, "wk_empty"); h = c.commit(dict(GOOD, **{UT + "selftest_foo2.py": "print('fine')\n"})); c.records(h); r = c.gate(h)
    check(r["verdict"] == "invalid" and st(r, "tests") == "UNMEASURED", "a new selftest executing no check is UNMEASURED")


def t_med(tmp):
    c = Ctx(tmp, "md_x"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/Patches/p.xml": "<Patch>SILENT</Patch>\n"}))
    c.records(h); r = c.gate(h)
    check(r["verdict"] == "invalid" and st(r, "xml") == "UNMEASURED", "a validator exiting 0 with no OK marker: xml UNMEASURED")
    for k, ch in (("doc", {UT + "foo.py": '"""doc."""\ndef foo():\n    """says one."""\n    return 1\n'}),
                  ("ws", {UT + "foo.py": "def foo():\n\n    return   1\n\n"}),
                  ("cm", {UT + "foo.py": "# note\ndef foo():\n    return 1  # one\n"}),
                  ("xmlcm", {"src/RimMandrake/ModA/Patches/p.xml": "<!-- c -->\n<Patch/>\n"})):
        c = Ctx(tmp, "md_" + k); h = c.commit(ch); c.records(h); r = c.gate(h)
        check(r["verdict"] == "fail" and st(r, "placeholders") == "FAIL", "a %s-only diff counts as empty: FAIL" % k)
    c = Ctx(tmp, "md_ln"); (c.repo / UT).mkdir(parents=True, exist_ok=True)
    os.symlink("run_selftests.py", c.repo / UT / "foo_link.py"); h = c.commit(GOOD); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "scope") == "FAIL", "an in-area symlink FAILS scope")
    c = Ctx(tmp, "md_sub")
    git(c.repo, "update-index", "--add", "--cacheinfo", "160000,%s,%s" % (c.base, UT + "foo_sub"))
    git(c.repo, "commit", "-q", "-m", "sub"); h = git(c.repo, "rev-parse", "HEAD"); c.records(h); r = c.gate(h)
    check(r["verdict"] == "fail" and st(r, "scope") == "FAIL", "a submodule gitlink-only diff FAILS scope")
    c = Ctx(tmp, "md_rec"); h = c.commit(GOOD); c.records(h); r = c.gate(h)
    rf = r.get("record_file")
    try:
        ok = G.load_verified(c.p, "armx", rf)["verdict"] == "pass"
    except G.GateError:
        ok = False
    check(ok, "gate.json verifies against the sha256 in its signed gate event (control)")
    body = json.loads(Path(rf).read_text()); body["verdict"] = "pass"; body["steps"]["tests"]["why"] = "edited"
    Path(rf).write_text(json.dumps(body, indent=1, sort_keys=True))
    try:
        G.load_verified(c.p, "armx", rf); ok = False
    except G.GateError:
        ok = True
    check(ok, "an edited gate.json is refused at read (hash differs from the signed event)")


def t_low(tmp):
    for k, proof in (("c", "python3 -c pass"), ("missing", "python3 src/RimMandrake/Utils/nope.py"),
                     ("unrelated", "python3 src/RimMandrake/Utils/unrelated.py")):
        c = Ctx(tmp, "lw_" + k, proof=proof); h = c.commit(GOOD); c.records(h); r = c.gate(h)
        check(r["verdict"] == "invalid" and st(r, "proof") == "UNMEASURED", "proof %r is UNMEASURED, not pass/fail" % proof)
    for k, ch in (("todo", {UT + "foo.py": "def foo():\n    # " + TD.lower() + ": later\n    return 2\n"}),
                  ("retnone", {UT + "foo.py": "def foo():\n    return 1\n\ndef bar():\n    return None\n"})):
        c = Ctx(tmp, "lw_" + k); h = c.commit(ch); c.records(h); r = c.gate(h)
        check(r["verdict"] == "fail" and st(r, "placeholders") == "FAIL", "%s FAILS placeholders" % k)
    r = None
    c = Ctx(tmp, "lw_can", live="minimal"); h = c.commit(GOOD); c.records(h)
    c.emit("canary", h[:1], verdict="pass", detail={"modcheck": True}); c.emit("live_release", h[:1], verdict="pass")
    r = c.gate(h)
    check(r["verdict"] != "pass" and st(r, "live") != "PASS", "a 1-char canary sha prefix does not name head")
    env = {"ARENA_CLONES": str(tmp / "elsewhere")}
    try:
        G.refuse_arm_location(G.__file__, env=env); ok = False
    except G.GateError:
        ok = True
    check(ok, "an ARENA_CLONES override without ARENA_GATE_TEST is refused")
    try:
        G.refuse_arm_location(G.__file__, env=dict(env, ARENA_GATE_TEST="1")); ok = True
    except G.GateError:
        ok = False
    check(ok, "the override is honoured under ARENA_GATE_TEST=1 (control)")


def t_signing(tmp):
    """finish() signs only inside an explicit harness_pass opened in the parent, closed before it returns."""
    opened, used = [], []
    real_pass, real_writer = L.harness_pass, L.HarnessWriter

    def spy_pass(*a, **k):
        cap = real_pass(*a, **k); opened.append(cap); return cap

    class SpyWriter(real_writer):
        def emit(self, *a, **k):
            used.append((self._cap, self._cap in opened, self._cap.closed)); return super().emit(*a, **k)
    L.harness_pass, L.HarnessWriter = spy_pass, SpyWriter
    try:
        c = Ctx(tmp, "sg"); h = c.commit(GOOD); c.records(h)
        g = G.Gate(c.task, c.base, h, "armx", c.repo, c.p, dump=str(c.dump), defs_roots=[]); r = g.execute()
    finally:
        L.harness_pass, L.HarnessWriter = real_pass, real_writer
    gate_uses = used[-1:] if r.get("recorded") else []
    check(r["verdict"] == "pass" and r["recorded"] and gate_uses and gate_uses[0][1] and not gate_uses[0][2],
          "finish() emits the gate event through a capability it opened with harness_pass (%s)" % (used[-1][1:] if used else None,))
    check(bool(gate_uses) and gate_uses[0][0].closed, "the signing pass is closed when finish() returns")
    c = Ctx(tmp, "sg2"); h = c.commit(GOOD); c.records(h)
    L.harness_pass = lambda *a, **k: (_ for _ in ()).throw(L.Rejected("no pass"))
    try:
        r = G.Gate(c.task, c.base, h, "armx", c.repo, c.p, dump=str(c.dump), defs_roots=[]).execute()
    finally:
        L.harness_pass = real_pass
    check(not r["recorded"] and "no pass" in r.get("record_error", ""),
          "without a harness pass finish() does not sign (record_error set)")


def main():
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE", "ARENA_GATE_TEST")}
    os.environ["ARENA_GATE_TEST"] = "1"
    tmp = Path(tempfile.mkdtemp(prefix="arena_gate_st_"))
    try:
        for t in (t_control, t_placeholder, t_scope_tests, t_live, t_agents, t_unmeasured, t_tools, t_cli_location,
                  t_sandbox, t_runner, t_ids, t_weakened, t_med, t_low, t_signing):
            t(tmp)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
