#!/usr/bin/env python3
"""selftest_close_evidence.py -- the close-evidence recorder and lookup (CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE).

Offline, fixture git repos under a temp dir; RM_CLOSE_EVIDENCE_DIR points every write at the temp dir, so the real
evidence store is never touched. Checks: a clean run is found by sha (prefix) and item; a dirty-tree run is recorded
but never returned as evidence; session transcripts do not make a tree dirty; a write error never raises; a tool run
inside a selftest writes nothing unless redirected; summarize lets FAIL win; validate_patch, run_selftests and
modcheck each write their line (or, for a redirected modcheck registry, do not).
"""
import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import close_evidence as CE  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def make_repo(root):
    repo = Path(root) / "clone"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("x = 1\n")
    git(repo, "add", "src/a.py")
    git(repo, "commit", "-q", "-m", "one")
    return repo, git(repo, "rev-parse", "HEAD")


def main():
    with tempfile.TemporaryDirectory() as td:
        store = Path(td) / "evidence"
        os.environ[CE.ENV_DIR] = str(store)
        os.environ.pop("RIMFLOW_ITEM", None)
        repo, sha = make_repo(td)

        # clean tree: found by full sha, by 12-char prefix, by item; a 6-char prefix is too short to match
        r1 = CE.record("selftest", "PASS", [repo / "src" / "a.py"], clone=repo, item="ITEM_ONE")
        check(r1 is not None and r1["sha"] == sha and r1["dirty"] is False, "clean record carries HEAD, dirty False")
        check(r1["paths"] == ["src/a.py"], "paths are clone-relative: %r" % (r1 and r1["paths"],))
        check(len(CE.lookup(sha=sha)) == 1, "lookup by sha finds the clean run")
        check(len(CE.lookup(sha=sha[:12])) == 1, "lookup by 12-char prefix finds it")
        check(CE.lookup(sha=sha[:6]) == [], "a 6-char prefix matches nothing")
        check(len(CE.lookup(item="ITEM_ONE")) == 1 and CE.lookup(item="OTHER") == [], "lookup by item")
        check(len(CE.lookup(sha=sha, item="ITEM_ONE")) == 1 and CE.lookup(sha=sha, item="OTHER") == [],
              "sha and item together must both match")

        # transcripts are not dirt
        (repo / "conversations").mkdir()
        (repo / "conversations" / "t.md").write_text("chat\n")
        r2 = CE.record("selftest", "PASS", [repo / "src"], clone=repo)
        check(r2["dirty"] is False, "an untracked conversations/ file leaves the tree clean")

        # dirty tree: recorded, never evidence
        (repo / "src" / "a.py").write_text("x = 2\n")
        r3 = CE.record("validate_patch", "PASS", [repo / "src" / "a.py"], clone=repo)
        check(r3["dirty"] is True and r3["dirty_paths"] == ["src/a.py"], "a modified tracked file marks it dirty")
        check(all(r["tool"] == "selftest" for r in CE.lookup(sha=sha)), "lookup excludes the dirty-tree run")
        check(any(r["tool"] == "validate_patch" for r in CE.lookup(sha=sha, include_dirty=True)),
              "include_dirty (audit) still sees it")
        git(repo, "checkout", "-q", "--", "src/a.py")
        (repo / "src" / "new.py").write_text("y = 1\n")
        r4 = CE.record("winbuild", "PASS", [repo / "src"], clone=repo)
        check(r4["dirty"] is True, "an untracked source file marks it dirty")
        (repo / "src" / "new.py").unlink()

        # no clone: sha None, never evidence
        loose = Path(td) / "loose.xml"
        loose.write_text("<Patch/>")
        r5 = CE.record("validate_patch", "PASS", [loose])
        check(r5["sha"] is None and not CE.counts_as_evidence(r5), "a file in no clone is never evidence")

        # result vocabulary is closed, and a bad value is a loud no-op, not an exception
        err = io.StringIO()
        with redirect_stderr(err):
            r6 = CE.record("selftest", "GREEN", [repo], clone=repo)
        check(r6 is None and "CLOSE-EVIDENCE WRITE FAILED" in err.getvalue(), "a non-vocabulary result is refused loudly")

        # write error never raises
        blocker = Path(td) / "blocker"
        blocker.write_text("not a dir")
        os.environ[CE.ENV_DIR] = str(blocker / "sub")
        err = io.StringIO()
        with redirect_stderr(err):
            r7 = CE.record("selftest", "PASS", [repo], clone=repo)
        check(r7 is None and "CLOSE-EVIDENCE WRITE FAILED" in err.getvalue(), "an unwritable store prints, never raises")
        os.environ[CE.ENV_DIR] = str(store)

        # nested under the selftest runner without a redirect: nothing written (fixtures are not evidence)
        os.environ.pop(CE.ENV_DIR)
        old = os.environ.get("RM_SELFTEST_NESTED")
        os.environ["RM_SELFTEST_NESTED"] = "1"
        check(CE.record("selftest", "PASS", [repo], clone=repo) is None, "nested tool run writes nothing")
        if old is None:
            os.environ.pop("RM_SELFTEST_NESTED")
        os.environ[CE.ENV_DIR] = str(store)

        # summarize: latest per path set, FAIL beats UNMEASURED beats PASS
        recs = [{"tool": "selftest", "paths": ["a"], "result": "FAIL", "ts": "1"},
                {"tool": "selftest", "paths": ["a"], "result": "PASS", "ts": "2"},
                {"tool": "selftest", "paths": ["b"], "result": "UNMEASURED", "ts": "3"},
                {"tool": "winbuild", "paths": ["c"], "result": "PASS", "ts": "1"},
                {"tool": "winbuild", "paths": ["d"], "result": "FAIL", "ts": "1"}]
        check(CE.summarize(recs) == {"selftest": "UNMEASURED", "winbuild": "FAIL"}, "summarize: %r" % CE.summarize(recs))

        # every line on disk is one JSON object with the fixed fields
        lines = [json.loads(ln) for f in store.glob("*.jsonl") for ln in f.read_text().splitlines()]
        want = {"v", "ts", "tool", "clone", "sha", "dirty", "dirty_n", "dirty_paths", "paths", "result", "item",
                "seat", "detail"}
        check(lines and all(set(l) == want for l in lines), "%d lines, each with exactly the schema fields" % len(lines))

        # validate_patch end to end: a run on a file in the fixture clone writes one validate_patch line
        (repo / "Patches").mkdir()
        (repo / "Patches" / "p.xml").write_text('<?xml version="1.0"?><Patch><Operation Class="PatchOperationAdd">'
                                                 '<xpath>Defs/ThingDef[defName="X"]</xpath><value><a/></value>'
                                                 '</Operation></Patch>')
        git(repo, "add", "Patches/p.xml")
        git(repo, "commit", "-q", "-m", "patch")
        sha2 = git(repo, "rev-parse", "HEAD")
        vp = REPO / "skills" / "rimworld-modding" / "scripts" / "validate_patch.py"
        env = dict(os.environ)
        env.pop("RM_SELFTEST_NESTED", None)
        p = subprocess.run([sys.executable, str(vp), "--quiet", "--mods-config", str(Path(td) / "none.xml"),
                            str(repo / "Patches" / "p.xml")], capture_output=True, text=True, env=env, timeout=120)
        vrec = CE.lookup(sha=sha2, tool="validate_patch")
        expect = {0: "PASS", 1: "FAIL"}.get(p.returncode, "UNMEASURED")
        check(len(vrec) == 1 and vrec[0]["result"] == expect and vrec[0]["paths"] == ["Patches/p.xml"],
              "validate_patch (exit %d) wrote one %s line for HEAD: %r" % (p.returncode, expect,
                                                                          [(r["result"], r["paths"]) for r in vrec]))

        # run_selftests: the outer run records the verdict-reaching tests, not the SKIPPED ones
        import run_selftests as RS
        RS._OUTER[0] = True
        ran = [(REPO / "src/RimMandrake/Utils/selftest_close_evidence.py", "PASS", 1.0, ""),
               (REPO / "src/RimMandrake/Utils/close_evidence.py", "SKIPPED", 0.0, "unchanged")]
        before = len(CE.read_all(folder=store))
        RS._record_evidence(ran)
        RS._record_evidence([ran[0], (ran[1][0], "FAIL", 1.0, "boom")])
        RS._OUTER[0] = None
        RS._record_evidence(ran)                     # not an outer run: nothing
        new = CE.read_all(folder=store)[before:]
        check([(r["tool"], r["result"], len(r["paths"])) for r in new] == [("selftest", "PASS", 1), ("selftest", "FAIL", 2)],
              "run_selftests records one line per outer run: %r" % [(r["tool"], r["result"]) for r in new])

        # modcheck: a registry redirected by a test writes no evidence
        sys.path.insert(0, str(HERE / "modcheck"))
        import status as ST
        real = ST.LOG_PATH
        ST.LOG_PATH = str(Path(td) / "status.json")
        before = len(CE.read_all(folder=store))
        ST._record_evidence("Demo", str(repo), {"status": "RED"}, False, "")
        check(len(CE.read_all(folder=store)) == before, "modcheck with a redirected registry records nothing")
        ST.LOG_PATH = real
        ST._record_evidence("Demo", str(repo / "src"), {"status": "GREEN", "run_id": "r", "hash": "h"}, True, "")
        last = CE.read_all(folder=store)[-1]
        check(last["tool"] == "modcheck" and last["result"] == "PASS" and last["detail"]["status"] == "GREEN",
              "modcheck records the machine verdict beside the registry status")

    print("RESULT: %s (%d failure(s))" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
