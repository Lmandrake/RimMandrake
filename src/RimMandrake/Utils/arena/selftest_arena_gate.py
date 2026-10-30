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
  round 2        runner isolation (json.dumps / conftest / sitecustomize / PYTHONSTARTUP forgeries stay red), a test
                 rewriting a later instrument, a valid record then a hang (UNMEASURED), signing failure (main() nonzero),
                 records bound to one run and ordered (replay, cross-run, supersedes), zero-exit UNMEASURED proof/build,
                 deletions, `pass; return None`, .js placeholders, native shadows, unknown statuses, glob depth,
                 code under bookkeeping paths, binary-only diffs, and the REAL run_selftests.py --only path.
  round 3        sys.exit(0) from candidate code at import / mid-test / atexit under an UNCHANGED selftest is never a
                 pass (collected entries must all return); a covered change does not hide an uncovered .py/.xml; the
                 C# build cannot rewrite the evaluated checkout (sandboxed: refused; unsandboxed: detected, FAIL);
                 sandboxed code cannot reach WSL interop (cmd.exe) while the build can; the eventlog runner marker;
                 a live_release in the real arena_lane shape (verdict ok, no sha, keyed by run id).
  Each round-3 fix is shown RED first: the same scenario with the fix disabled (monkeypatched) reads PASS / leaks.
Writes only under a temp dir.
"""
import json
import os
import re
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


# the gate never runs the checkout's run_selftests.py (its own runner does the counting): a tripwire, so a gate that
# did would fail every control
STUB_SELFTESTS = '''import sys
sys.exit("the gate ran the checkout's run_selftests.py")
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
if "UNMPHRASE" in src: print("UNMEASURED, not a pass or a fail"); sys.exit(0)
if "REWRITE" in src:   # a csproj Exec target reaching the REAL head checkout (sibling of the build dir) by absolute path
    t = os.path.join(os.path.dirname(os.getcwd()), "co", "src/RimMandrake/Utils/proof_bad.py")
    try:
        open(t, "w").write("import sys\\nimport foo\\nsys.exit(0)\\n"); print("REWROTE " + t)
    except OSError as e:
        print("rewrite refused: %s" % e)
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
    UT + "proof_unm.py": "import foo\nprint('UNMEASURED, not a pass or a fail')\n",
    UT + "foo_extra.py": "def extra():\n    return 1\n",
    UT + "unrelated.py": "import sys\nsys.exit(0)\n",
    "src/RimMandrake/ModA/Patches/p.xml": "<Patch/>\n",
    "src/RimMandrake/ModA/Source/A.cs": "class A {}\n",
    "src/RimMandrake/ModA/About/About.xml": "<ModMetaData/>\n",
}
AREA = [UT + "foo*", UT + "selftest_foo*", "src/RimMandrake/ModA/**"]
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
                f.write_bytes(content) if isinstance(content, bytes) else f.write_text(content)
        git(self.repo, "add", "-A", "--", ".")
        git(self.repo, "commit", "-q", "-m", msg)
        return git(self.repo, "rev-parse", "HEAD")

    def emit(self, event, sha, lane="L", run_id="r", **kw):
        return self.w.emit("armx", event, lane=lane, run_id=run_id, task="T1", sha=sha, **kw)

    def records(self, head, builder="B1", tester="T9", test="pass", run_id="r"):
        self.emit("build_end", head, run_id=run_id, detail={"builder": builder})
        if tester:
            self.emit("test_start", head, run_id=run_id, detail={"tester": tester})
            if test:
                self.emit("test_end", head, run_id=run_id, verdict=test, detail={"tester": tester})

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


RED = "import foo\n\ndef t_a():\n    assert foo.foo() == 3\n\nt_a()\n"
FOO2 = "def foo():\n    return 2\n"


def t_isolation(tmp):
    """round 2 (1): the candidate shares the runner's process, so nothing it can patch decides the record."""
    check("json" not in G.RUNNER_SRC and "ARENAGATE2" in G.RUNNER_SRC,
          "the runner imports no json (a module the candidate could patch) and writes the fixed ARENAGATE2 line")
    forge = ("import json\n_o = json.dumps\njson.dumps = lambda r, *a, **k: _o(dict(r, status='pass', tampered=False, "
             "asserts=99, checks=99, tests=99, lines=99), *a, **k)\n\n" + FOO2)
    c = Ctx(tmp, "iso_js"); h = c.commit({UT + "foo.py": forge, UT + "selftest_foo.py": RED}); c.records(h); r = c.gate(h)
    check(st(r, "tests") == "FAIL" and r["verdict"] == "fail",
          "a planted json.dumps monkeypatch does not turn a red test into a pass (tests %s)" % st(r, "tests"))
    conf = ("import os, builtins\n_w, _e = os.write, getattr(os, '_ex' + 'it')\n"
            "def w(fd, b):\n    return _w(fd, b.replace(b'\"fail\"', b'\"pass\"').replace(b' fail ', b' pass '))\n"
            "os.write = w\nsetattr(os, '_ex' + 'it', lambda c: _e(0))\nbuiltins.isinstance = lambda *a: True\n"
            "m = getattr(__import__('sys'), 'moni' + 'toring')\n")
    task = dict(id="T1", area=AREA + [UT + "conftest.py"], proof="python3 src/RimMandrake/Utils/proof_ok.py", live="none")
    c = Ctx(tmp, "iso_cf"); h = c.commit({UT + "foo.py": FOO2, UT + "conftest.py": conf,
                                          UT + "selftest_foo.py": "import conftest\n" + RED})
    c.records(h); r = c.gate(h, task=task)
    check(st(r, "tests") == "FAIL" and r["verdict"] == "fail",
          "a conftest the red test imports, patching os.write/os._exit/builtins, cannot forge a pass (tests %s)" % st(r, "tests"))
    sc = conf.replace("builtins.isinstance = lambda *a: True\n", "")
    task_sc = dict(task, area=AREA + [UT + "sitecustomize.py"])
    c = Ctx(tmp, "iso_sc"); h = c.commit({UT + "foo.py": FOO2, UT + "sitecustomize.py": sc,
                                          UT + "selftest_foo.py": "import sitecustomize\n" + RED})
    c.records(h); r = c.gate(h, task=task_sc)
    check(st(r, "tests") == "FAIL" and st(r, "scope") == "FAIL" and r["verdict"] == "fail",
          "a sitecustomize that patches the runner: scope FAIL and the red test stays FAIL (tests %s)" % st(r, "tests"))
    evil = tmp / "evil_env"; evil.mkdir(exist_ok=True)
    (evil / "startup.py").write_text(sc); (evil / "sitecustomize.py").write_text(sc)
    saved = {k: os.environ.get(k) for k in ("PYTHONSTARTUP", "PYTHONPATH", "PYTHONINSPECT")}
    os.environ.update(PYTHONSTARTUP=str(evil / "startup.py"), PYTHONPATH=str(evil), PYTHONINSPECT="1")
    try:
        c = Ctx(tmp, "iso_env"); h = c.commit({UT + "foo.py": FOO2, UT + "selftest_foo.py": RED}); c.records(h)
        r = c.gate(h)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    check(st(r, "tests") == "FAIL", "PYTHONSTARTUP/PYTHONPATH/PYTHONINSPECT in the gate's env do not reach the runner "
          "(red test FAIL, got %s)" % st(r, "tests"))


def t_instruments(tmp):
    """round 2 (2): a candidate test cannot rewrite a later instrument (head or base copy) at run time."""
    rw = ("import os, foo\n\ndef t_a():\n    assert foo.foo() == 2\n\n"
          "for root in ('.', '../base'):\n    for rel in ('skills/rimworld-modding/scripts/validate_patch.py', "
          "'src/RimMandrake/Utils/deploy_custom_mods.py'):\n        try:\n"
          "            open(os.path.join(root, rel), 'w').write(\"print('OK - 0 errors')\\n\")\n"
          "        except OSError:\n            pass\nt_a()\n")
    c = Ctx(tmp, "ins_rw")
    h = c.commit({UT + "foo.py": FOO2, UT + "selftest_foo.py": rw, "src/RimMandrake/ModA/Patches/p.xml": "<Patch>BADXML</Patch>\n"})
    c.records(h); r = c.gate(h)
    check(st(r, "xml") == "FAIL" and r["verdict"] == "fail",
          "a selftest that rewrites validate_patch.py at run time does not launder bad xml (xml %s)" % st(r, "xml"))
    c = Ctx(tmp, "ins_ctl")
    h = c.commit({UT + "foo.py": FOO2, UT + "selftest_foo.py": rw, "src/RimMandrake/ModA/Patches/p.xml": "<Patch>fine</Patch>\n"})
    c.records(h); r = c.gate(h)
    check(st(r, "tests") == "PASS" and st(r, "xml") == "PASS",
          "control: the same selftest passes when its writes are refused, and good xml still PASSES (%s/%s)"
          % (st(r, "tests"), st(r, "xml")))


def t_rc(tmp):
    """round 2 (3): a valid record followed by a hang, or by a nonzero exit, is never a pass."""
    src, real_run = G.RUNNER_SRC, G.run
    lines = src.split("\n")
    i = max(k for k, l in enumerate(lines) if "_exit(" in l)
    ind = len(lines[i]) - len(lines[i].lstrip())
    lines[i] = lines[i][:ind] + '__import__("time").sleep(30); ' + lines[i][ind:]
    G.RUNNER_SRC = "\n".join(lines)
    G.run = lambda *a, timeout=G.STEP_TIMEOUT, **k: real_run(*a, timeout=min(timeout, 8), **k)
    try:
        c = Ctx(tmp, "rc_hang"); h = c.commit(GOOD); c.records(h); r = c.gate(h)
    finally:
        G.RUNNER_SRC, G.run = src, real_run
    check(st(r, "tests") == "UNMEASURED" and r["verdict"] == "invalid",
          "a runner that writes a valid pass record then hangs past the timeout: tests UNMEASURED (%s)" % st(r, "tests"))
    vf, pr = getattr(G, "verdict_from", None), getattr(G, "parse_record", None)
    ok = vf is not None and pr is not None
    if ok:
        n = "ab" * 16
        good = ("ARENAGATE2 %s pass 1 2 3 4 0 2 2\n" % n).encode()
        short = ("ARENAGATE2 %s pass 1 2 3 4 0 1 2\n" % n).encode()
        rec = pr(good, n)
        ok = (rec is not None and vf(0, rec)[0] == "PASS" and vf(1, rec)[0] == "FAIL" and vf(None, rec)[0] == "UNMEASURED"
              and vf(0, None)[0] == "UNMEASURED" and pr(good + good, n) is None and pr(good, "cd" * 16) is None
              and pr(good[:-1], n) is None and vf(0, pr(good.replace(b" 0 2 2\n", b" 1 2 2\n"), n))[0] == "UNMEASURED"
              and vf(0, pr(short, n))[0] == "UNMEASURED" and vf(0, rec, 3)[0] == "UNMEASURED" and vf(0, rec, 2)[0] == "PASS")
    check(ok, "parent-side parse: pass needs rc 0 + the one exact line with this nonce; rc!=0 FAIL, timeout/extra/"
          "wrong nonce/tampered/fewer entries done than collected/expected count not the collector's UNMEASURED")


def t_signfail(tmp):
    """round 2 (4): signing failure -> verdict invalid, main() exits nonzero."""
    import contextlib
    import io
    c = Ctx(tmp, "sf"); h = c.commit(GOOD); c.records(h)
    real_load, real_pass = G.A.load_frozen, L.harness_pass
    os.environ["ARENA_GATE_DUMP"] = str(c.dump)
    argv = ["--task", "T1", "--base", c.base, "--head", h, "--arm", "armx", "--repo", str(c.repo)]
    out = {}
    try:
        G.A.load_frozen = lambda *a, **k: c.task
        for k in ("ctl", "nosign"):
            if k == "nosign":
                L.harness_pass = lambda *a, **kw: (_ for _ in ()).throw(L.Rejected("no pass"))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = G.main(argv)
            try:
                out[k] = (rc, json.loads(buf.getvalue().strip().splitlines()[-1]))
            except (ValueError, IndexError):
                out[k] = (rc, {})
    finally:
        G.A.load_frozen, L.harness_pass = real_load, real_pass
        os.environ.pop("ARENA_GATE_DUMP", None)
    rc, rec = out["ctl"]
    check(rc == 0 and rec.get("verdict") == "pass" and rec.get("recorded"), "control: main() on a clean signed pass exits 0 (%s %s)"
          % (rc, rec.get("verdict")))
    rc, rec = out["nosign"]
    check(rc != 0 and rec.get("verdict") == "invalid" and rec.get("passed") is False and not rec.get("recorded"),
          "a pass that cannot be signed: verdict invalid, main() exits %s (nonzero)" % rc)


def t_records(tmp):
    """round 2 (5): records are bound to one run and ordered by signed time; any unsuperseded failure counts."""
    def tr(tag, fn):
        c = Ctx(tmp, "rec_" + tag); h = c.commit(GOOD); fn(c, h); return st(c.gate(h), "test_record")
    s = tr("oldpass_newstart", lambda c, h: (c.records(h, run_id="r1"), c.emit("test_start", h, run_id="r2", detail={"tester": "T9"})))
    check(s == "UNMEASURED", "an old passing test_end then a NEW test_start: the new run has no verdict -> UNMEASURED (%s)" % s)
    s = tr("mismatch", lambda c, h: (c.emit("build_end", h, detail={"builder": "B1"}),
                                     c.emit("test_start", h, run_id="ra", detail={"tester": "T9"}),
                                     c.emit("test_end", h, run_id="rb", verdict="pass", detail={"tester": "T9"})))
    check(s == "UNMEASURED", "a test_end from another run_id does not answer a test_start -> UNMEASURED (%s)" % s)

    def fail_then_pass(sup, early=False):
        def fn(c, h):
            c.records(h, test="fail", run_id="r1")
            ts = "2000-01-01T00:00:00+00:00" if early else None
            c.emit("test_start", h, run_id="r2", detail={"tester": "T9"})
            d = {"tester": "T9"}
            if sup:
                d["supersedes"] = "r1"
            c.emit("test_end", h, run_id="r2", verdict="pass", detail=d, ts=ts)
        return fn
    s = tr("fp", fail_then_pass(False))
    check(s == "FAIL", "a failed test run then a passing one that does not name it -> FAIL (%s)" % s)
    s = tr("fps", fail_then_pass(True))
    check(s == "PASS", "control: a later signed re-run whose detail.supersedes names the failed run -> PASS (%s)" % s)
    s = tr("fpe", fail_then_pass(True, early=True))
    check(s != "PASS", "a 'superseding' pass signed with a time BEFORE the failure supersedes nothing (%s)" % s)

    def lv(tag, fn):
        c = Ctx(tmp, "lv2_" + tag, live="minimal"); h = c.commit(GOOD); c.records(h); fn(c, h); return st(c.gate(h), "live")
    can = lambda c, h, v, run, **d: c.emit("canary", h, run_id=run, verdict=v, detail=dict({"modcheck": True}, **d))  # noqa: E731
    rel = lambda c, h, run: c.emit("live_release", h, run_id=run, verdict="pass")  # noqa: E731
    s = lv("fp", lambda c, h: (can(c, h, "fail", "r1"), can(c, h, "pass", "r2"), rel(c, h, "r2")))
    check(s == "INVALID", "a failed canary is not erased by a later passing canary of another run -> INVALID (%s)" % s)
    s = lv("fps", lambda c, h: (can(c, h, "fail", "r1"), can(c, h, "pass", "r2", supersedes=["r1"]), rel(c, h, "r2")))
    check(s == "PASS", "control: a later passing canary naming the failed run in supersedes -> PASS (%s)" % s)
    s = lv("xrun", lambda c, h: (rel(c, h, "r1"), can(c, h, "pass", "r2")))
    check(s == "UNMEASURED", "a live_release from another run (and older than the canary) is not paired -> UNMEASURED (%s)" % s)
    s = lv("build", lambda c, h: (can(c, h, "pass", "r2", build="b2"), rel(c, h, "r2")))
    check(s == "UNMEASURED", "a live_release whose build id differs from the canary's is not paired (%s)" % s)


def t_phrase_deletes(tmp):
    """round 2 (6)+(7): exit 0 with the unmeasured phrase is UNMEASURED; deleted code files are code changes."""
    c = Ctx(tmp, "ph_proof", proof="python3 src/RimMandrake/Utils/proof_unm.py"); h = c.commit(GOOD); c.records(h); r = c.gate(h)
    check(st(r, "proof") == "UNMEASURED" and r["verdict"] == "invalid",
          "a proof printing the unmeasured phrase and exiting 0 is UNMEASURED (%s)" % st(r, "proof"))
    c = Ctx(tmp, "ph_cs"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/Source/A.cs": "class A { /* UNMPHRASE */ }\n"}))
    c.records(h); r = c.gate(h)
    check(st(r, "csharp") == "UNMEASURED" and r["verdict"] == "invalid",
          "a build printing the unmeasured phrase and exiting 0 is UNMEASURED (%s: %s)" % (st(r, "csharp"),
                                                                                 r["steps"]["csharp"]["why"][:200]))
    c = Ctx(tmp, "del_py"); h = c.commit({UT + "foo_extra.py": None, UT + "foo_data.txt": "rows\n"}); c.records(h); r = c.gate(h)
    check(st(r, "tests") == "UNMEASURED" and r["verdict"] != "pass",
          "a deleted .py (plus an added data file) with no selftest mapping: tests UNMEASURED, not NA (%s)" % st(r, "tests"))
    c = Ctx(tmp, "del_cs"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/Source/A.cs": None, "src/RimMandrake/ModA/d.txt": "x\n"}))
    c.records(h); r = c.gate(h)
    check(st(r, "csharp") != "NA" and r["verdict"] != "pass", "a deleted .cs: csharp runs, not NA (%s)" % st(r, "csharp"))
    c = Ctx(tmp, "del_xml"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/Patches/p.xml": None, "src/RimMandrake/ModA/d.txt": "x\n"}))
    c.records(h); r = c.gate(h)
    check(st(r, "xml") == "UNMEASURED" and r["verdict"] != "pass", "a deleted Patches xml: xml UNMEASURED, not NA (%s)" % st(r, "xml"))


def t_static(tmp):
    """round 2 (8)+(9) and the round-1 leftovers p3f/p3g/p3h."""
    c = Ctx(tmp, "stb"); h = c.commit({UT + "foo.py": FOO2 + "\ndef bar():\n    pass\n    return None\n"}); c.records(h); r = c.gate(h)
    check(st(r, "placeholders") == "FAIL", "`def bar(): pass; return None` is a stub: placeholders FAIL (%s)" % st(r, "placeholders"))
    c = Ctx(tmp, "js"); h = c.commit(dict(GOOD, **{UT + "foo.js": "// " + TD + ": later\nexport const x = 1;\n"})); c.records(h); r = c.gate(h)
    check(st(r, "placeholders") == "FAIL", "a placeholder in an added .js is found (%s)" % st(r, "placeholders"))
    wide = dict(id="T1", area=[UT + "*", "src/RimMandrake/ModA/**"], proof="python3 src/RimMandrake/Utils/proof_ok.py", live="none")
    for k, path in (("so", UT + "socket.cpython-312-x86_64-linux-gnu.so"), ("pyd", UT + "foo_native.pyd")):
        c = Ctx(tmp, "nat_" + k); h = c.commit(dict(GOOD, **{path: b"\x7fELF\x00\x01binary"})); c.records(h); r = c.gate(h, task=wide)
        check(st(r, "scope") == "FAIL" and r["verdict"] == "fail", "a native %s in the diff FAILS scope (%s)" % (path, st(r, "scope")))
    for bad in (None, "BROKEN"):
        res = {s: {"status": "PASS"} for s in G.STEPS}
        res["proof"] = {"status": bad}
        check(G.verdict_of(res) == "invalid", "verdict_of(): a step status %r is invalid, never pass" % (bad,))
    check(G.verdict_of({**{s: {"status": "PASS"} for s in G.STEPS}, "xml": {"status": "NA"}}) == "pass",
          "verdict_of(): PASS plus NA passes (control)")
    c = Ctx(tmp, "glob"); h = c.commit(dict(GOOD, **{UT + "foo_dir/evil.py": "X = 1\n"})); c.records(h); r = c.gate(h)
    check(st(r, "scope") == "FAIL", "p3g: area glob foo* does not reach into foo_dir/ (scope %s)" % st(r, "scope"))
    c = Ctx(tmp, "bkq"); h = c.commit(dict(GOOD, **{"infrastructure/state/queue/evil.py": "X = 1\n"})); c.records(h); r = c.gate(h)
    check(st(r, "scope") == "FAIL", "p3h: code under a bookkeeping path is not stripped: scope FAIL (%s)" % st(r, "scope"))
    c = Ctx(tmp, "bkq_ok"); h = c.commit(dict(GOOD, **{"infrastructure/state/queue/notes.md": "x\n"})); c.records(h); r = c.gate(h)
    check(st(r, "scope") == "PASS" and r["verdict"] == "pass", "control: a bookkeeping .md note is still stripped (%s)" % st(r, "scope"))
    c = Ctx(tmp, "bin"); h = c.commit({"src/RimMandrake/ModA/Textures/t.png": b"\x89PNG\x00\x00data"}); c.records(h); r = c.gate(h)
    check(st(r, "placeholders") == "UNMEASURED" and r["verdict"] != "pass",
          "p3f: a binary-only diff: placeholders UNMEASURED (%s)" % st(r, "placeholders"))


def t_real(tmp):
    """The real `run_selftests.py --only` and the harness runner agree on a real selftest; the runner sees red."""
    import secrets
    root = HERE.parents[3]
    env = {k: v for k, v in os.environ.items() if not k.startswith(("ARENA", "PYTHON"))}
    # a real selftest that needs no harness capability (selftest_arena_eventlog refuses any entrypoint but its own
    # /proc/self/cmdline script, so under the gate's runner it reads FAIL by design: a known residual)
    target = HERE.parent / "selftest_about_dependency_urls.py"
    out = subprocess.run([sys.executable, str(root / UT / "run_selftests.py"), "--only", str(target), "--no-cache"],
                         cwd=str(root), capture_output=True, text=True, env=env, timeout=300)
    check(out.returncode == 0 and "RESULT: GREEN" in out.stdout,
          "the real run_selftests.py --only passes %s (rc %s)" % (target.name, out.returncode))
    runner = tmp / "real_runner.py"; runner.write_text(G.RUNNER_SRC)

    collector = tmp / "real_collect.py"; collector.write_text(G.COLLECT_SRC)

    def via_runner(path):
        col = subprocess.run([sys.executable, "-I", str(collector), str(path)], capture_output=True, text=True,
                             env=env, timeout=60)
        ent = col.stdout.strip().splitlines()[-1] if col.returncode == 0 and col.stdout.strip() else "ENTRIES "
        names = [x for x in ent.split(" ", 1)[1].split(",") if x] if " " in ent else []
        rfd, wfd = os.pipe(); n = secrets.token_hex(16)
        p = subprocess.run([sys.executable, "-I", str(runner), str(wfd), str(path)], input=n + "\n" + ent + "\n",
                           text=True, capture_output=True, pass_fds=(wfd,), env=env, timeout=300,
                           cwd=str(Path(path).parent))
        os.close(wfd); buf = os.read(rfd, 4096); os.close(rfd)
        rec = G.parse_record(buf, n) if hasattr(G, "parse_record") else None
        return (G.verdict_from(p.returncode, rec, len(names) + 1)[0] if rec else "NONE"), rec
    v, rec = via_runner(target)
    check(v == "PASS" and rec and rec["lines"] > 0,
          "the harness runner passes the same real selftest, lines counted (%s %s)" % (v, rec))
    red = tmp / "selftest_red_real.py"; red.write_text("def t_a():\n    assert 1 == 2\n\nt_a()\n")
    v, rec = via_runner(red)
    check(v == "FAIL", "the harness runner reports a real red selftest as FAIL (%s)" % v)


FOO_EXIT_MID = "import sys\n\ndef foo():\n    sys.exit(0)\n"
FOO_EXIT_IMPORT = "import sys\nsys.exit(0)\n\ndef foo():\n    return 2\n"
FOO_ATEXIT_RED = "import atexit, sys\natexit.register(lambda: sys.exit(0))\n\ndef foo():\n    return 0\n"


def t_round3_exit(tmp):
    """GPT r2 (3): SystemExit(0) from candidate code before the unchanged selftest's checks complete."""
    def tests_of(tag, changes, mutate=False):
        real = G.verdict_from
        if mutate:      # the fix disabled: completion ignored (the round-2 behaviour)
            G.verdict_from = lambda rc, rec, expected=None: real(rc, dict(rec, done=rec["expected"]) if rec else rec)
        try:
            c = Ctx(tmp, "r3x_" + tag); h = c.commit(changes); c.records(h); r = c.gate(h)
        finally:
            G.verdict_from = real
        return st(r, "tests"), r["verdict"], r["steps"]["tests"]
    s, v, _ = tests_of("mid_red", {UT + "foo.py": FOO_EXIT_MID}, mutate=True)
    check(s == "PASS", "RED first: with completion ignored, foo() calling sys.exit(0) under the unchanged selftest "
          "reads tests PASS (the false pass GPT found) (%s)" % s)
    s, v, d = tests_of("mid", {UT + "foo.py": FOO_EXIT_MID})
    check(s == "UNMEASURED" and v != "pass", "sys.exit(0) mid-test from candidate code: tests UNMEASURED, never pass "
          "(%s %s %s)" % (s, v, str(d.get("findings"))[:160]))
    s, v, _ = tests_of("imp", {UT + "foo.py": FOO_EXIT_IMPORT})
    check(s == "UNMEASURED" and v != "pass", "sys.exit(0) at import of candidate code: tests UNMEASURED (%s %s)" % (s, v))
    s, v, _ = tests_of("atexit", {UT + "foo.py": FOO_ATEXIT_RED})
    check(s == "FAIL", "an atexit sys.exit(0) cannot turn a red selftest green (the runner never runs atexit) (%s)" % s)
    ok = dict(GOOD); ok[UT + "selftest_foo.py"] = "import sys\n" + GOOD[UT + "selftest_foo.py"] + "sys.exit(0)\n"
    s, v, _ = tests_of("ctl", ok)
    check(s == "PASS" and v == "pass", "control: a selftest that itself ends with sys.exit(0) after its checks passes "
          "(%s %s)" % (s, v))
    c = tmp / "r3_collect.py"; c.write_text(G.COLLECT_SRC)
    f = tmp / "selftest_r3c.py"; f.write_text("def t_a():\n    pass\n\ndef helper():\n    def test_in():\n        pass\n"
                                             "\ndef main():\n    t_a()\n")
    out = subprocess.run([sys.executable, "-I", str(c), str(f)], capture_output=True, text=True, timeout=60).stdout
    check(out.strip() == "ENTRIES main,t_a,test_in", "the collector names t_*/test_* (nested too) + top-level main and "
          "runs no candidate code (%r)" % out.strip())


def t_round3_cover(tmp):
    """GPT r2 (4): one covered change must not hide an uncovered one."""
    mixed = dict(GOOD, **{UT + "foo_extra.py": "def extra():\n    return 9\n"})
    real = G.Gate.uncovered
    G.Gate.uncovered = lambda self: [f for f in self.selftests_for()[1] if f not in self.alive()]  # round-2 rule
    try:
        c = Ctx(tmp, "r3c_red"); h = c.commit(mixed); c.records(h); r = c.gate(h)
    finally:
        G.Gate.uncovered = real
    check(st(r, "tests") == "PASS", "RED first: under the round-2 rule GOOD + a modified unmapped foo_extra.py reads "
          "tests PASS (%s)" % st(r, "tests"))
    c = Ctx(tmp, "r3c"); h = c.commit(mixed); c.records(h); r = c.gate(h)
    check(st(r, "tests") == "UNMEASURED" and "foo_extra.py" in r["steps"]["tests"]["why"] and r["verdict"] != "pass",
          "GOOD + a modified unmapped foo_extra.py: tests UNMEASURED naming it (%s: %s)"
          % (st(r, "tests"), r["steps"]["tests"]["why"][:120]))
    c = Ctx(tmp, "r3c_xml"); h = c.commit(dict(GOOD, **{UT + "foo_cfg.xml": "<cfg/>\n"})); c.records(h); r = c.gate(h)
    check(st(r, "tests") == "UNMEASURED" and r["verdict"] != "pass",
          "GOOD + an .xml no step measures (not Defs/Patches, no deployable mod): tests UNMEASURED (%s)" % st(r, "tests"))
    c = Ctx(tmp, "r3c_ok"); h = c.commit(dict(GOOD, **{"src/RimMandrake/ModA/About/About.xml": "<ModMetaData><x/></ModMetaData>\n"}))
    c.records(h); r = c.gate(h)
    check(st(r, "tests") == "PASS", "control: an About.xml of a deployable mod is covered by deploy_plan (%s: %s)"
          % (st(r, "tests"), r["steps"]["tests"]["why"][:100]))


def t_round3_build(tmp):
    """GPT r2 (5): the C# build must not rewrite the checkout later steps evaluate."""
    task = {"id": "T1", "area": AREA, "proof": "python3 src/RimMandrake/Utils/proof_bad.py", "live": "none"}
    ch = dict(GOOD, **{"src/RimMandrake/ModA/Source/A.cs": "class A { /* REWRITE */ }\n"})
    os.environ.setdefault("WINBUILD_DOTNET", "stub")
    real_argv, real_fp = G.Gate.sandbox_argv, G.Gate.fingerprint

    def old_argv(self, argv, cwd, rw_dir=None, data_rw=True, interop=False):   # round 2: head writable to the build
        out = real_argv(self, argv, cwd, rw_dir=rw_dir, data_rw=data_rw, interop=interop)
        if rw_dir:
            r = os.path.realpath(self.clone); i = out.index("--")
            out[i:i] = ["--bind", r, r]
        return out
    G.Gate.sandbox_argv, G.Gate.fingerprint = old_argv, lambda self: {}
    try:
        c = Ctx(tmp, "r3b_red"); h = c.commit(ch); c.records(h); r = c.gate(h, task=task)
    finally:
        G.Gate.sandbox_argv, G.Gate.fingerprint = real_argv, real_fp
    check(st(r, "proof") == "PASS", "RED first: with head writable to the build and no fingerprint, a csproj target "
          "rewrites the failing proof and proof reads PASS (%s)" % st(r, "proof"))
    c = Ctx(tmp, "r3b"); h = c.commit(ch); c.records(h); r = c.gate(h, task=task)
    check(st(r, "proof") == "FAIL" and st(r, "csharp") == "PASS" and r["verdict"] == "fail",
          "the build runs in a throwaway copy: its write to the real head is refused, the proof stays FAIL "
          "(csharp %s proof %s)" % (st(r, "csharp"), st(r, "proof")))
    G.Gate.sandbox_argv = old_argv      # a Windows-side Exec that bypasses bwrap: prevention gone, detection left
    try:
        c = Ctx(tmp, "r3b_det"); h = c.commit(ch); c.records(h); r = c.gate(h, task=task)
    finally:
        G.Gate.sandbox_argv = real_argv
    check(st(r, "csharp") == "FAIL" and st(r, "proof") != "PASS" and r["verdict"] == "fail",
          "a build that does reach the head checkout is DETECTED: csharp FAIL, nothing later passes (csharp %s, proof "
          "%s)" % (st(r, "csharp"), st(r, "proof")))


def t_round3_interop(tmp):
    """GPT r2 (1): sandboxed candidate code cannot reach WSL interop; only the build keeps it."""
    cmd = "/mnt/c/Windows/System32/cmd.exe"
    try:
        outside = subprocess.run([cmd, "/c", "echo", "R3MARK"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        outside = ""
    if "R3MARK" not in outside:
        print("note  WSL interop unavailable on this host: the cmd.exe probe has nothing to prove (not counted)")
        return
    c = Ctx(tmp, "r3i"); h = c.commit(GOOD)
    g = G.Gate(c.task, c.base, h, "armx", c.repo, c.p, dump=str(c.dump), writer=c.w, defs_roots=[])
    g.logdir.mkdir(parents=True, exist_ok=True)
    g.checkout(); g.sandbox_probe()
    check(g.sandbox_why == "", "the sandbox probe accepts the scrubbed sandbox (%s)" % g.sandbox_why)
    rc, text = g.srun([cmd, "/c", "echo", "R3MARK"], g.logdir / "r3_interop_build.log", timeout=30, interop=True)
    check(re.search(r"^R3MARK\s*$", text or "", re.M) is not None, "RED first / instrument sees: with interop (the build's sandbox) cmd.exe runs "
          "from inside bwrap")
    rc, text = g.srun([cmd, "/c", "echo", "R3MARK"], g.logdir / "r3_interop.log", timeout=30)
    check(re.search(r"^R3MARK\s*$", text or "", re.M) is None, "every other sandboxed step: cmd.exe cannot run (rc %s, %s)"
          % (rc, (text or "").strip().splitlines()[-2:] if text else text))
    py = "import os,json;print(json.dumps(sorted(k for k in os.environ if k.startswith('WSL'))))"
    rc, text = g.srun([g.python, "-I", "-c", py], g.logdir / "r3_env.log", timeout=30)
    check(rc == 0 and re.search(r"^\[\]$", text or "", re.M) is not None, "no WSL_* variable reaches a non-build step")


def t_round3_marker(tmp):
    """The eventlog fold-in: the gate-side marker arena_eventlog can check, from the REAL runner argv and env."""
    c = Ctx(tmp, "r3m")
    probe = ("import os,sys,json\nprint('R3ARGV '+json.dumps({'argv':open('/proc/self/cmdline','rb').read()"
             ".decode().split('\\0')[:-1],'env':os.environ.get('%s')}))\n\ndef t_a():\n    assert 1\n\nt_a()\n"
             % G.GATE_RUNNER_ENV)
    h = c.commit({UT + "selftest_foo.py": probe})
    g = G.Gate(c.task, c.base, h, "armx", c.repo, c.p, dump=str(c.dump), writer=c.w, defs_roots=[])
    g.logdir.mkdir(parents=True, exist_ok=True)
    g.checkout(); g.sandbox_probe()
    rec, text = g.run_test(g.clone, UT + "selftest_foo.py", "head")
    line = [l for l in (text or "").splitlines() if l.startswith("R3ARGV ")]
    got = json.loads(line[-1][7:]) if line else {"argv": [], "env": None}
    want = os.path.realpath(g.clone / UT / "selftest_foo.py")
    env = {G.GATE_RUNNER_ENV: got["env"]} if got["env"] else {}
    check(rec is not None and rec["verdict"] == "PASS" and G.gate_runner_selftest(got["argv"], env) == want,
          "the runner's real /proc/self/cmdline + env identify the selftest it runs (%s)"
          % (G.gate_runner_selftest(got["argv"], env),))
    bad = []
    if got["argv"]:
        bad = [G.gate_runner_selftest(got["argv"], {}), G.gate_runner_selftest(got["argv"], {G.GATE_RUNNER_ENV: "0" * 64}),
               G.gate_runner_selftest(got["argv"] + ["x"], env), G.gate_runner_selftest(got["argv"][:3] + ["a", got["argv"][4]], env)]
        fake = tmp / G.GATE_RUNNER_NAME; fake.write_text(G.RUNNER_SRC + "#\n")
        bad.append(G.gate_runner_selftest(got["argv"][:2] + [str(fake)] + got["argv"][3:], env))
    check(bad and all(b is None for b in bad), "no marker / wrong marker / extra arg / bad fd / an edited runner file: "
          "not the gate runner (%s)" % bad)


def t_round3_live(tmp):
    """The live step accepts the REAL arena_lane record shape (copied from arena_lane.py's _ev calls)."""
    def lv(tag, rel_verdict="ok", aborted=False, problems=()):
        c = Ctx(tmp, "r3l_" + tag, live="minimal"); h = c.commit(GOOD); c.records(h)
        c.w.emit("armx", "canary", lane="L", run_id="run7", task="T1", sha=h, verdict="pass" if not problems else "fail",
                 detail={"problems": list(problems), "facts": {"active_mods": ["ludeon.rimworld"], "world": {"name": "w",
                         "seed": "s"}, "deployed_sha": h}})
        c.w.emit("armx", "live_release", lane="L", run_id="run7", task="T1", verdict=rel_verdict, minutes=0.2,
                 detail={"restored": True, "restore_ok": True, "restore_s": 12.0, "charged_to": "armx",
                         "aborted": aborted, "why": "", "inherited_swap": None, "restore_out": "", "release_out": "",
                         "mods_restored": [], "mods_restore_ok": True, "main_sha": "f" * 40, "mods_restore_out": ""})
        return st(c.gate(h), "live")
    s = lv("ok")
    check(s == "PASS", "a real lane canary (problems []) + live_release verdict ok with no sha, same run: live PASS (%s)" % s)
    s = lv("err", rel_verdict="error")
    check(s == "UNMEASURED", "a real lane live_release verdict error: live UNMEASURED (%s)" % s)
    s = lv("abort", aborted="watchdog")
    check(s == "UNMEASURED", "a real lane release of an aborted hold: live UNMEASURED (%s)" % s)
    s = lv("red", problems=("deployed mod(s) not active: x",))
    check(s == "INVALID", "a real lane canary with problems: live INVALID (%s)" % s)


def main():
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE", "ARENA_GATE_TEST")}
    os.environ["ARENA_GATE_TEST"] = "1"
    tmp = Path(tempfile.mkdtemp(prefix="arena_gate_st_"))
    try:
        for t in (t_control, t_placeholder, t_scope_tests, t_live, t_agents, t_unmeasured, t_tools, t_cli_location,
                  t_sandbox, t_runner, t_ids, t_weakened, t_med, t_low, t_signing, t_isolation, t_instruments, t_rc,
                  t_signfail, t_records, t_phrase_deletes, t_static, t_real, t_round3_exit, t_round3_cover,
                  t_round3_build, t_round3_interop, t_round3_marker, t_round3_live):
            t(tmp)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
