#!/usr/bin/env python3
"""selftest_relentless_exam.py - RELENTLESS_BUILD_EXAM_BEFORE_BUILDER (redesign_final §2 G3/G4, acceptance row 03).

A Setter that is not the builder writes the exam before the build; VALIDATE (no agent) refuses, by corpus:
(1) a file-exists / grep-only check on a behavioural clause (EXISTENCE_ONLY), and `kind: artifact` the item never asked for;
(2) a red that is an ImportError (or exit 2, a timeout, an undeclared exit, a missing marker): RED_NOT_ASSERTION;
(3) a planted break that deletes the file the check names, or only deletes files: BREAK_DELETES;
(4) exam_hash moves when a named test file (or named repo file, or the item text) changes, not for an unnamed file;
(5) maps: every clause from a verbatim item sentence, every '## Done when' bullet mapped;
(6) shadow: catch runs the exam at each Marker-returned candidate (caught = assertion red) and at the done sha; summary;
(7) on_contract owes once, only on the host's own store (never a selftest's), never raises; contract() calls it;
(8) run_item: SET -> refusal -> one resumed retry -> validated; two refusals -> arbiter_owed (not auto-bar).
Runs on a throwaway git repo; the box runner is replaced by a local runner with the same contract.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_exam as E             # noqa: E402

FAILS = []
CFG = {"mode": "shadow", "max_items": 60, "shadow_target": 30, "setter_agent": "rm-judge", "setter_model": "opus"}

ITEM_TEXT = ("FOO_DOUBLE_RETURNS_TWICE: foo.double(n) must return 2*n, not n. "
             "Keep foo.name() returning 'foo'.")
M_OLD = "def double(n):\n    return n\n\n\ndef name():\n    return 'foo'\n"
M_NEW = "def double(n):\n    return 2 * n\n\n\ndef name():\n    return 'foo'\n"
T_DOUBLE = ("import sys\nsys.path.insert(0, 'src')\nimport foo\n"
            "if foo.double(3) != 6:\n    print('FAIL double(3)=%r' % foo.double(3))\n    sys.exit(1)\nprint('ok')\n")
T_NAME = ("import sys\nsys.path.insert(0, 'src')\nimport foo\n"
          "if foo.name() != 'foo':\n    print('FAIL name')\n    sys.exit(1)\nprint('ok')\n")
BREAK_NAME = ("--- a/src/foo.py\n+++ b/src/foo.py\n@@ -4,3 +4,3 @@\n \n def name():\n-    return 'foo'\n+    return 'bar'\n")
PRE = "import sys; sys.path.insert(0, 'src'); import foo; foo.double(1); "
BREAK_DELETE = ("--- a/src/foo.py\n+++ /dev/null\n@@ -1,6 +0,0 @@\n-def double(n):\n-    return n\n-\n-\n-def name():\n"
                "-    return 'foo'\n")


def ok(cond, what):
    print(("  ok    " if cond else "  FAIL  ") + what)
    if not cond:
        FAILS.append(what)


def git(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True, check=True).stdout.strip()


def make_repo(tmp):
    repo = tempfile.mkdtemp(dir=tmp, prefix="repo")
    os.makedirs(os.path.join(repo, "src"))
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    with open(os.path.join(repo, "src", "foo.py"), "w") as f:
        f.write(M_OLD)
    git(repo, "add", "src/foo.py")
    git(repo, "commit", "-qm", "base")
    base = git(repo, "rev-parse", "HEAD")
    with open(os.path.join(repo, "src", "foo.py"), "w") as f:
        f.write(M_OLD.replace("return n", "return n + 0"))      # a candidate that still misses the clause
    git(repo, "commit", "-qam", "wrong")
    wrong = git(repo, "rev-parse", "HEAD")
    with open(os.path.join(repo, "src", "foo.py"), "w") as f:
        f.write(M_NEW)
    git(repo, "commit", "-qam", "right")
    return repo, base, wrong, git(repo, "rev-parse", "HEAD")


def files_dir(tmp, double=T_DOUBLE, name=T_NAME):
    d = tempfile.mkdtemp(dir=tmp, prefix="files")
    for n, body in (("t_double.py", double), ("t_name.py", name)):
        with open(os.path.join(d, n), "w") as f:
            f.write(body)
    return d


def local_boxer(repo, tmp):
    """box_runner's contract on a local export: (run, read_file, close), read_file.tree."""
    def boxer(rules, source, sha, files, item=None, nonce=None):
        def fresh():
            t = tempfile.mkdtemp(dir=tmp, prefix="tree")
            subprocess.run("git -C %s archive %s | tar -x -C %s" % (repo, sha, t), shell=True, check=True)
            if files and os.path.isdir(files):
                shutil.copytree(files, os.path.join(t, E.EXAM_DIR), dirs_exist_ok=True)
            return t
        tree = fresh()

        def run(argv, patch, timeout):
            rt = fresh()                                # as box_runner: every run in its own tree
            try:
                if patch:
                    why = E.apply_patch(patch, rt)
                    if why:
                        return None, "PATCH_FAILED: " + why, False
                try:
                    q = subprocess.run(argv, cwd=rt, capture_output=True, text=True, timeout=timeout,
                                       env=dict(os.environ, **E.RUN_ENV))
                    return q.returncode, q.stdout + q.stderr, False
                except subprocess.TimeoutExpired:
                    return None, "timeout", True
            finally:
                shutil.rmtree(rt, ignore_errors=True)

        def read_file(path):
            try:
                with open(os.path.join(tree, path), "rb") as f:
                    return f.read()
            except OSError:
                return None
        read_file.tree = tree
        return run, read_file, (lambda: shutil.rmtree(tree, ignore_errors=True))
    return boxer


def clause(cid, argv, kind="behaviour", brk=None, red=None):
    return {"id": cid, "says": "x", "kind": kind, "check": {"argv": argv, "timeout_s": 60, "red": red or {"exit": [1], "marker": "FAIL"}},
            "break": brk or {"kind": "base_red"}}


GOOD = {"clauses": [clause("c1", ["python3", ".exam/t_double.py"]),
                    clause("c2", ["python3", ".exam/t_name.py"], brk={"kind": "patch", "patch": BREAK_NAME})],
        "maps": {"foo.double(n) must return 2*n, not n.": ["c1"], "Keep foo.name() returning 'foo'.": ["c2"]}}


def with_clause(c, sentence="foo.double(n) must return 2*n, not n."):
    return {"clauses": [c], "maps": {sentence: [c["id"]]}}


def codes(v):
    return [r["code"] for r in v["refusals"]]


def t_validate(tmp):
    repo, base, wrong, right = make_repo(tmp)
    boxer = local_boxer(repo, tmp)
    run, rf, close = boxer(None, None, base, files_dir(tmp))
    try:
        v = E.validate(GOOD, run, ITEM_TEXT, "", rf)
        ok(v["ok"], "V0 a real exam validates: c1 base_red is an assertion red, c2 green on base and red under a behavioural break %s"
           % v["refusals"])
        # (1) existence-only on a behavioural clause, by argv shape, refused before any run
        for argv in (["test", "-f", "src/foo.py"], ["bash", "-c", "test -f src/foo.py && grep -q 'return 2' src/foo.py"],
                     ["grep", "-q", "2 \\* n", "src/foo.py"],
                     ["python3", "-c", "import os,sys; sys.exit(0 if os.path.exists('src/foo.py') else 1)"],
                     ["python3", "-c", "from pathlib import Path; assert '2 * n' in Path('src/foo.py').read_text()"]):
            v = E.validate(with_clause(clause("c1", argv)), run, ITEM_TEXT, "", rf)
            ok("EXISTENCE_ONLY" in codes(v), "V1 behavioural clause refuses existence/grep-only check %s" % argv[:3])
        v = E.validate(with_clause(clause("c1", ["test", "-f", "docs/r.md"], kind="artifact")), run, ITEM_TEXT, "", rf)
        ok("ARTIFACT_NOT_ASKED" in codes(v), "V1b kind: artifact refused where the item asks for no artifact")
        ok(not [x for x in E.lint(with_clause(clause("c1", ["test", "-f", "docs/r.md"], kind="artifact"),
                                              "write the census report"), "FOO: write the census report to docs/r.md")
                if x["code"] in ("ARTIFACT_NOT_ASKED", "EXISTENCE_ONLY")],
           "V1c kind: artifact with an existence check is allowed where the item asks for an artifact")
        # (2) a red that is not an assertion
        for argv, why in ((["python3", "-c", "import foo_not_written_yet"], "ImportError"),
                          (["python3", ".exam/no_such_test.py"], "missing file / exit 2"),
                          (["python3", "-c", PRE + "print('FAIL'); sys.exit(3)"], "undeclared exit 3"),
                          (["python3", "-c", PRE + "sys.exit(1)"], "declared marker absent"),
                          (["python3", "-c", PRE + "print('FAIL'); sys.exit(2)"], "exit 2")):
            v = E.validate(with_clause(clause("c1", argv)), run, ITEM_TEXT, "", rf)
            ok(codes(v) == ["RED_NOT_ASSERTION"], "V2 red refused as not an assertion: %s %s" % (why, codes(v)))
        for argv, why in ((["python3", "-c", "import foo_not_written_yet"], "ImportError"),
                          (["python3", "-c", PRE + "open('src/missing.txt')"], "missing file")):
            v = E.validate(with_clause(clause("c1", argv, red={"exit": [1]})), run, ITEM_TEXT, "", rf)
            ok(codes(v) == ["RED_NOT_ASSERTION"], "V2a with no marker declared, a %s exit 1 is still not a red %s" % (why, codes(v)))
        v = E.validate(with_clause(clause("c1", ["python3", "-c", "import time; time.sleep(5)"])),
                       lambda a, p, t: (None, "", True), ITEM_TEXT, "", rf)
        ok(codes(v) == ["RED_NOT_ASSERTION"], "V2b a timeout is not a red")
        v = E.validate(with_clause(clause("c1", ["python3", ".exam/t_name.py"])), run, ITEM_TEXT, "", rf)
        ok(codes(v) == ["STAYS_GREEN"], "V2c base_red on preserved behaviour: green on base is refused")
        # (3) a break that deletes the file instead of changing behaviour
        v = E.validate(with_clause(clause("c2", ["python3", ".exam/t_name.py", "src/foo.py"],
                                          brk={"kind": "patch", "patch": BREAK_DELETE}), "Keep foo.name() returning 'foo'."),
                       run, ITEM_TEXT, "", rf)
        ok("BREAK_DELETES" in codes(v), "V3 a break that deletes the file the check names is refused %s" % codes(v))
        v = E.validate(with_clause(clause("c2", ["python3", ".exam/t_name.py"], brk={"kind": "patch", "patch": BREAK_DELETE}),
                                   "Keep foo.name() returning 'foo'."), run, ITEM_TEXT, "", rf)
        ok("BREAK_DELETES" in codes(v), "V3b a break that only deletes files is refused")
        v = E.validate(with_clause(clause("c2", ["python3", ".exam/t_name.py"], brk={"kind": "patch", "patch": BREAK_NAME.replace(
            "'bar'", "'foo'  # same")}), "Keep foo.name() returning 'foo'."), run, ITEM_TEXT, "", rf)
        ok(codes(v) == ["STAYS_GREEN"], "V3c a break the check does not notice: STAYS_GREEN %s" % codes(v))
        v = E.validate(with_clause(clause("c2", ["python3", ".exam/t_name.py"], brk={"kind": "patch", "patch": "--- a/src/x.py\n+++ b/src/x.py\n@@ -1 +1 @@\n-a\n+b\n"}),
                                   "Keep foo.name() returning 'foo'."), run, ITEM_TEXT, "", rf)
        ok(codes(v) == ["PATCH_FAILED"], "V3d a break that does not apply is refused")
    finally:
        close()


def t_hash(tmp):
    repo, base, wrong, right = make_repo(tmp)
    boxer = local_boxer(repo, tmp)
    exam = json.loads(json.dumps(GOOD))
    exam["clauses"][1]["check"]["argv"] = ["python3", ".exam/t_name.py", "src/foo.py"]
    run, rf, close = boxer(None, None, base, files_dir(tmp))
    h0 = E.validate(exam, run, ITEM_TEXT, "", rf)["exam_hash"]
    h0b = E.validate(exam, run, ITEM_TEXT, "", rf)["exam_hash"]
    close()
    ok(h0 == h0b and len(h0) == 64, "H0 exam_hash is stable")
    run, rf, close = boxer(None, None, base, files_dir(tmp, double=T_DOUBLE + "# edited\n"))
    h1 = E.validate(exam, run, ITEM_TEXT, "", rf)["exam_hash"]
    close()
    ok(h1 != h0, "H1 exam_hash changes when a named test file (.exam/t_double.py) changes")
    run, rf, close = boxer(None, None, right, files_dir(tmp))
    ok(E.exam_hash(exam, {p: rf(p) for p in E.all_named(exam)}, ITEM_TEXT) != h0,
       "H2 exam_hash changes when a named repo file (src/foo.py) changes")
    close()
    ok("src/foo.py" in E.all_named(exam) and ".exam/t_double.py" in E.all_named(exam), "H3 named files are found in argv")
    files = {p: b"x" for p in E.all_named(exam)}
    ok(E.exam_hash(exam, files, ITEM_TEXT) == E.exam_hash(exam, dict(files), ITEM_TEXT)
       and E.exam_hash(exam, files, ITEM_TEXT + " more") != E.exam_hash(exam, files, ITEM_TEXT), "H4 the item text is in the hash")
    ok(E.exam_hash(exam, dict(files, **{"unnamed/z.py": b"1"}), ITEM_TEXT) != E.exam_hash(exam, files, ITEM_TEXT)
       and E.validate(exam, lambda a, p, t: (0, "", False), ITEM_TEXT, "", lambda p: b"x")["exam_hash"]
       == E.validate(exam, lambda a, p, t: (0, "", False), ITEM_TEXT, "", lambda p: b"x" if p in E.all_named(exam) else b"y")["exam_hash"],
       "H5 only named files enter validate's hash")


def t_maps():
    bad = E.lint({"clauses": GOOD["clauses"], "maps": {"foo.double must be fast": ["c1"]}}, ITEM_TEXT)
    c = [x["code"] for x in bad]
    ok("MAP_UNKNOWN_SENTENCE" in c and "MAP_UNMAPPED_CLAUSE" in c, "M1 a paraphrased sentence and an unmapped clause are refused %s" % c)
    prose = "# FOO\n\n## Done when\n- foo.double(n) must return 2*n, not n.\n- the README says so\n\n## Notes\n- not a bullet\n"
    c = [x["code"] for x in E.lint(GOOD, ITEM_TEXT, prose)]
    ok(c == ["MAP_DONE_WHEN"], "M2 an unmapped '## Done when' bullet is refused, other sections are not %s" % c)
    ok(E.done_when(prose) == ["foo.double(n) must return 2*n, not n.", "the README says so"], "M3 done_when reads the bullets")
    c = [x["code"] for x in E.lint({"clauses": [dict(GOOD["clauses"][0], check={"argv": ["x"], "red": {"exit": [124]}})],
                                    "maps": {"foo.double(n) must return 2*n, not n.": ["c1"]}}, ITEM_TEXT)]
    ok("SCHEMA" in c, "M4 declaring a timeout exit (124) as an assertion red is refused")


def t_review_fixes():
    # REVIEW 2026-11-06: an empty item sentence is a substring of everything and must not satisfy the mapping
    bad = E.lint({"clauses": GOOD["clauses"], "maps": {"": ["c1"]}}, ITEM_TEXT)
    ok("MAP_UNKNOWN_SENTENCE" in [x["code"] for x in bad], "R1 an empty mapping sentence is refused %s" % bad)
    # a null clause is a refusal, not a crash out of validate
    try:
        v = E.validate({"clauses": [None], "maps": {}}, lambda *a, **k: (0, "", False), ITEM_TEXT, "", lambda p: None)
        ok(not v["ok"], "R2 a null clause refuses, no crash")
    except Exception as e:
        ok(False, "R2 a null clause crashed validate: %r" % e)


def t_shadow(tmp):
    repo, base, wrong, right = make_repo(tmp)
    root = os.path.join(tmp, "relroot")
    store = R.Store(root)
    item = "FOO_DOUBLE_RETURNS_TWICE"
    d = E.item_dir(store, item)
    os.makedirs(d)
    shutil.copytree(files_dir(tmp), os.path.join(d, "files"))
    E._write(os.path.join(d, "exam.json"), dict(GOOD, item=item, exam_hash="h"))
    E.set_status(store, item, state="validated", base=base)
    os.makedirs(store.item_dir(item), exist_ok=True)
    for rec in ({"end": "finish", "sha": wrong, "gen": 1}, {"end": "blind_fail", "detail": "double(3)=3"},
                {"end": "finish", "sha": right, "gen": 2}, {"end": "done", "sha": right}):
        store.attempt(item, rec)
    rets, done = E.returns(store.attempts(item), E.descender(repo, base))
    ok([r[0] for r in rets] == [wrong] and done == right, "S1 returns() pairs each Marker return with the sha it returned")
    rows = E.catch(store, item, None, boxer=local_boxer(repo, tmp), repo=repo)
    by = {r["role"]: r for r in rows}
    ok(by.get("return", {}).get("caught") is True and by["return"]["red_clauses"] == ["c1"],
       "S2 the exam would have caught the returned candidate (c1 assertion red at it)")
    ok(by.get("done", {}).get("green_at_done") is True, "S3 the exam is green at the done sha")
    ok(E.catch(store, item, None, boxer=local_boxer(repo, tmp), repo=repo) == [], "S4 a sha already run is not rerun")
    s = E.summary(store, CFG, repo=repo)
    ok(s["returns_run"] == 1 and s["returns_caught"] == 1 and s["done_green"] == 1 and s["with_marker_verdict"] == 1
       and s["target"] == 30 and s["caught_items"] == [item], "S5 summary counts returns caught toward the 30-item target %s" % s)
    src = open(os.path.join(HERE, "relentless.py"), encoding="utf-8").read()
    ok('rec["exam_shadow"] = relentless_exam.summary(store)' in src, "S6 relentless.py reading carries exam_shadow")


def t_on_contract(tmp):
    store = R.Store(os.path.join(tmp, "oc"))
    kicked = []
    ok(E.on_contract(store, "A_B_C", "abc", cfg=CFG, kicker=lambda s, i, c: kicked.append(i)) is None and not kicked
       and not os.path.isdir(E.exam_root(store)), "O1 a store that is not the host's own owes nothing (selftest stores)")
    roots = [store.root]
    msg = E.on_contract(store, "A_B_C", "abc", cfg=CFG, kicker=lambda s, i, c: kicked.append(i), roots=roots)
    ok(kicked == ["A_B_C"] and (E.status(store, "A_B_C") or {}).get("state") == "owed" and "owed" in (msg or ""),
       "O2 the first contract owes the exam and starts its unit")
    ok(E.on_contract(store, "A_B_C", "abc", cfg=CFG, kicker=lambda s, i, c: kicked.append(i), roots=roots) is None
       and kicked == ["A_B_C"], "O3 never owed twice")
    ok(E.on_contract(store, "D_E_F", "abc", cfg={"mode": "off"}, kicker=lambda s, i, c: kicked.append(i), roots=roots) is None,
       "O4 mode off owes nothing")
    m = E.on_contract(store, "G_H_I", "abc", cfg=CFG, kicker=lambda s, i, c: "no systemd", roots=roots)
    ok("did not start" in m and E.status(store, "G_H_I").get("kick_failed") == "no systemd", "O5 a unit that will not start is recorded")

    def boom(s, i, c):
        raise RuntimeError("x")
    ok(E.on_contract(store, "J_K_L", "abc", cfg=CFG, kicker=boom, roots=roots) is None
       and "RuntimeError" in E.status(store, "J_K_L").get("hook_error", ""), "O6 on_contract never raises")
    ok(E.on_contract(store, "M_N_O", "abc", cfg=dict(CFG, max_items=3), kicker=lambda s, i, c: None, roots=roots) is None,
       "O7 the shadow sample stops at max_items")
    calls = []
    E.kick(store, "A_B_C", CFG, runner=lambda argv, **k: calls.append(argv) or subprocess.CompletedProcess(argv, 0, "", ""))
    a = calls[0]
    ok(a[:2] == ["systemd-run", "--user"] and "--wait" not in a and a[-2:] == ["run", "A_B_C"]
       and "RELENTLESS_ROOT=" + store.root in a, "O8 the unit is detached, runs `relentless_exam.py run ID` on this store")
    src = open(os.path.join(HERE, "relentless.py"), encoding="utf-8").read()
    body = src[src.index("\ndef contract("):src.index("\ndef rebind(")]
    ok("relentless_exam.on_contract(store, item, st.get(\"base\")" in body and "if not prev:" in body,
       "O9 contract() calls on_contract on the first contract only")


def t_backfill():
    """EXAM_SHADOW_FILL_ITEMS_OLDER_THAN_EXAMS: an item contracted before the hook owes its exam at its next start,
    through the real tick/_lease path (selftest_relentless's Rig), at its current base."""
    import selftest_relentless as SR
    x = SR.Rig(n=1, share=1.0, max_workers=1)
    kicked, roots0, kick0, cfg0 = [], E.live_roots, E.kick, E.config
    try:
        E.config = lambda path=None: dict(CFG)          # the shipped mode may change; this row is about the hook
        E.live_roots = lambda: [x.s.root]
        E.kick = lambda store, item, cfg=None, runner=None: kicked.append(item)
        x.run_one("I0")
        ok(E.status(x.s, "I0") is None and not kicked, "B2 a start with no contract owes nothing (its first contract will)")
        g = x.st("I0")["gen"]
        E.live_roots = lambda: []                       # the hook not yet landed: the old contract owes nothing
        R.contract(x.s, "I0", g, "run the test")
        ok(E.status(x.s, "I0") is None, "B0 the old contract owed nothing")
        E.live_roots = lambda: [x.s.root]
        R.snag(x.s, "I0", g, "test", "back to the line", x.r, now=x.now)
        for _ in range(12):
            if x.st("I0")["status"] == "running" and x.st("I0")["gen"] > g:
                break
            x.tick()
        st = x.st("I0")
        rec = E.status(x.s, "I0") or {}
        ok(st["status"] == "running" and st["gen"] > g and rec.get("state") == "owed" and rec.get("base") == st["base"]
           and rec.get("origin") == "start_backfill" and kicked == ["I0"],
           "B1 the next start of an item contracted before the hook owes its exam at its current base %s %s" % (rec, kicked))
        R.snag(x.s, "I0", st["gen"], "test", "again", x.r, now=x.now)
        for _ in range(12):
            if x.st("I0")["status"] == "running" and x.st("I0")["gen"] > st["gen"]:
                break
            x.tick()
        ok(x.st("I0")["gen"] > st["gen"] and kicked == ["I0"], "B3 a second start owes it no second time %s" % kicked)
        y = R.Store(os.path.join(x.d, "first"))
        ok(E.on_contract(y, "P_Q_R", "abc", cfg=CFG, kicker=lambda s, i, c: None, roots=[y.root])
           and E.status(y, "P_Q_R").get("origin") == "first_contract", "B4 a first contract records its origin")
    finally:
        E.live_roots, E.kick, E.config = roots0, kick0, cfg0
        x.done()


def t_run_item(tmp):
    repo, base, wrong, right = make_repo(tmp)
    store = R.Store(os.path.join(tmp, "ri"))
    calls = []
    good, bad = json.loads(json.dumps(GOOD)), with_clause(clause("c1", ["test", "-f", "src/foo.py"]))

    def setter_of(seq):
        def setter(cwd, prompt, cfg, out, session=None, resume=None):
            calls.append({"resume": resume, "prompt": prompt, "cwd": cwd,
                          "has_base": open(os.path.join(cwd, "src", "foo.py")).read() == M_OLD})
            exam = seq[len(calls) - 1]
            work = os.path.join(E.item_dir(store, it), "setter")
            E._write(os.path.join(work, "exam.json"), exam)
            for n, body in (("t_double.py", T_DOUBLE), ("t_name.py", T_NAME)):
                with open(os.path.join(work, "files", n), "w") as f:
                    f.write(body)
            return "sess-1"
        return setter

    it = "FOO_DOUBLE_RETURNS_TWICE"
    E.set_status(store, it, state="owed", base=base)
    st = E.run_item(store, it, None, CFG, setter=setter_of([bad, good]), boxer=local_boxer(repo, tmp), text_of=lambda i: ITEM_TEXT)
    ok(st == "validated" and calls[1]["resume"] == "sess-1" and "EXISTENCE_ONLY" in calls[1]["prompt"],
       "R1 a refused exam gets one resumed Setter turn with the refusal, then validates")
    ok(calls[0]["resume"] is None and ITEM_TEXT in calls[0]["prompt"] and calls[0]["has_base"],
       "R2 the Setter starts fresh in a tree at the base sha with the item's words")
    ex = E._read(os.path.join(E.item_dir(store, it), "exam.json"))
    ok(ex and ex["base_sha"] == base and len(ex["exam_hash"]) == 64 and ex["setter"]["session"] == "sess-1"
       and os.path.isfile(os.path.join(E.item_dir(store, it), "files", "t_double.py")), "R3 the frozen exam carries base, hash, Setter")
    calls.clear()
    it = "FOO_DOUBLE_RETURNS_TWICE_B"
    E.set_status(store, it, state="owed", base=base)
    st = E.run_item(store, it, None, CFG, setter=setter_of([bad, bad]), boxer=local_boxer(repo, tmp), text_of=lambda i: ITEM_TEXT)
    ok(st == "arbiter_owed" and len(calls) == 2 and E.status(store, it)["refusals"][0]["code"] == "EXISTENCE_ONLY"
       and not os.path.exists(os.path.join(E.item_dir(store, it), "exam.json")),
       "R4 a second refusal goes to an arbiter (not auto-bar, no exam frozen)")
    ok(len(E._lines(os.path.join(E.item_dir(store, it), "validation.jsonl"))) == 2, "R5 both VALIDATE verdicts are kept")


def t_echoes(tmp):
    """EXAM_SHADOW_FIX_COUNTS_OWN_ECHOES: (a) concurrent catch writes a sha once and summary counts distinct (item, sha);
    (b) a done sha older than the exam's base is neither run nor counted; (c) an uncaught exception in the test's own
    code is not a red."""
    import threading
    repo, first, base, right = make_repo(tmp)          # the exam's base is the middle commit; `first` predates it
    store = R.Store(os.path.join(tmp, "echo"))
    item = "FOO_DOUBLE_ECHOES_TWICE"
    d = E.item_dir(store, item)
    os.makedirs(d)
    shutil.copytree(files_dir(tmp), os.path.join(d, "files"))
    E._write(os.path.join(d, "exam.json"), dict(GOOD, item=item, exam_hash="h", base_sha=base))
    E.set_status(store, item, state="validated", base=base)
    os.makedirs(store.item_dir(item), exist_ok=True)
    for rec in ({"end": "done", "sha": first}, {"end": "finish", "sha": base, "gen": 1}, {"end": "blind_fail"},
                {"end": "finish", "sha": right, "gen": 2}, {"end": "done", "sha": right}):
        store.attempt(item, rec)
    old = [{"end": "done", "sha": first}]
    ok(E.returns(old, E.descender(repo, base))[1] is None and E.returns(old)[1] == first,
       "E1 returns() drops a done sha that does not descend from the exam's base")
    inner, gate, entered = local_boxer(repo, tmp), threading.Event(), threading.Event()

    def slow(rules, source, sha, files, item=None, nonce=None):
        entered.set()
        gate.wait(10)
        return inner(rules, source, sha, files, item=item)
    out = {}
    ta = threading.Thread(target=lambda: out.setdefault("a", E.catch(store, item, None, boxer=slow, repo=repo)))
    ta.start()
    entered.wait(10)
    tb = threading.Thread(target=lambda: out.setdefault("b", E.catch(store, item, None, boxer=inner, repo=repo)))
    tb.start()
    time.sleep(0.3)
    gate.set()
    ta.join(60)
    tb.join(60)
    rows = E._lines(os.path.join(d, "catch.jsonl"))
    keys = [(r["sha"], r["role"]) for r in rows]
    ok(sorted(keys) == sorted({(base, "return"), (right, "done")}) and len(out.get("a", [])) + len(out.get("b", [])) == 2,
       "E2 two concurrent catches write each (sha, role) once, and never the off-base done %s" % keys)
    for r in list(rows) + [dict(rows[-1], at="later")] * 3 + [{"sha": first, "role": "done", "rows": [], "green_at_done": True}]:
        E._append(os.path.join(d, "catch.jsonl"), r)                     # echoes as the old harness wrote them
    s = E.summary(store, CFG, repo=repo)
    ok(s["returns_run"] == 1 and s["returns_caught"] == 1 and s["done_runs"] == 1 and s["done_green"] == 1
       and s["duplicate_rows"] == 5 and s["done_off_base"] == 1,
       "E3 summary counts distinct (item, sha) and skips a done sha off the exam's base %s" % s)
    own = ('Traceback (most recent call last):\n  File "/w/tree/.exam/t.py", line 9, in <module>\n    print("%s" % (1, 2))\n'
           '          ~~~~^~~~~~~~\nTypeError: not all arguments converted during string formatting\n')
    raised = own.replace("TypeError: not all", "rimbridge_client.RimBridgeError: tools/call failed: Tool x not")
    product = own.replace("/w/tree/.exam/t.py", "/w/tree/src/foo.py")
    asserted = own.replace("TypeError: not all arguments converted during string formatting", "AssertionError: FAIL 3 != 6")
    c = clause("c1", ["python3", ".exam/t.py"], red={"exit": [1]})
    ok(E.red_kind(c, 1, own).startswith("infra:") and E.red_kind(c, 1, raised).startswith("infra:"),
       "E4 an uncaught exception in the test's own code (its TypeError, its own raise) is not an assertion red")
    ok(E.red_kind(c, 1, asserted) == "assert" and E.red_kind(c, 1, product) == "assert" and E.red_kind(c, 1, "FAIL x") == "assert",
       "E5 an AssertionError, a product-code exception and a plain FAIL exit stay reds")
    v = E.validate(with_clause(c), lambda argv, patch, t: (1, own, False), ITEM_TEXT)
    ok(codes(v) == ["RED_NOT_ASSERTION"], "E6 VALIDATE refuses a base red that is the test's own exception %s" % codes(v))
    bad = {"sha": "x", "role": "done", "rows": [{"clause": "c1", "kind": "assert", "exit": 1, "out": own[-400:]}]}
    ok(E._reds(bad) == [], "E7 summary re-reads an old 'assert' row that was the test's own exception")


class FakeWall:
    """relentless_wall stand-in for box_runner: make_box exports `repo` at sha into <root>/<nonce>/tree; the unit runner
    runs the argv after `--` in WorkingDirectory=, so box_runner's own code (fresh trees, apply_patch, output) is tested."""
    def __init__(self, repo, root):
        self.repo, self.root, self.boxes, self.removed = repo, root, [], []

    def install(self):
        import relentless_wall as W
        self.saved = {k: getattr(W, k) for k in ("profile", "make_box", "props", "unit_env", "remove_box")}
        W.profile = lambda rules, role: {"box_root": self.root}
        W.make_box = self.make_box
        W.props = lambda prof, box: []
        W.unit_env = lambda prof, box: {}
        W.remove_box = lambda box: (self.removed.append(box), shutil.rmtree(box, ignore_errors=True))
        return self

    def restore(self):
        import relentless_wall as W
        for k, v in self.saved.items():
            setattr(W, k, v)

    def make_box(self, prof, source, sha, nonce, base=None, item=None):
        box = os.path.join(self.root, nonce)
        os.makedirs(os.path.join(box, "tree"))
        subprocess.run("git -C %s archive %s | tar -x -C %s" % (self.repo, sha, os.path.join(box, "tree")), shell=True, check=True)
        self.boxes.append(box)
        return box

    def runner(self, argv, **k):
        if argv[0] != "systemd-run":
            return subprocess.run(argv, **k)
        cwd = [a.split("=", 1)[1] for a in argv if a.startswith("WorkingDirectory=")][0]
        k.pop("stdin", None)
        return subprocess.run(argv[argv.index("--") + 1:], cwd=cwd, env=dict(os.environ, **E.RUN_ENV), **k)


def t_harden(tmp):
    """RELENTLESS_EXAM_HARDEN_SANDBOX_AND_STATE (Codex review 2026-11-06): six defects, one row each."""
    repo, base, wrong, right = make_repo(tmp)
    # H1 a planted break outside the tree is refused by lint and never applied; no --unsafe-paths anywhere
    esc = "--- a/../escaped.txt\n+++ b/../escaped.txt\n@@ -0,0 +1 @@\n+pwned\n"
    absp = "--- /dev/null\n+++ b/%s\n@@ -0,0 +1 @@\n+pwned\n" % os.path.join(tmp, "abs_escaped.txt").lstrip("/")
    absp = absp.replace("+++ b/", "+++ /")
    c = clause("c1", ["python3", ".exam/t_name.py"], brk={"kind": "patch", "patch": esc})
    ok("BREAK_UNSAFE_PATH" in codes(E.validate(with_clause(c), lambda *a: (0, "", False), ITEM_TEXT)),
       "H1a lint refuses a break whose path climbs out of the tree (../)")
    ok(E.unsafe_patch_paths(absp) and E.unsafe_patch_paths("diff --git a/x b/x\nrename from x\nrename to ../../y\n")
       and not E.unsafe_patch_paths(BREAK_NAME), "H1b absolute and rename-to ../ paths are unsafe; an in-tree diff is not")
    tree = tempfile.mkdtemp(dir=tmp, prefix="h1tree")
    ok(E.apply_patch(esc, tree) and E.apply_patch(absp, tree) and not os.path.exists(os.path.join(os.path.dirname(tree), "escaped.txt"))
       and not os.path.exists(os.path.join(tmp, "abs_escaped.txt")), "H1c apply_patch refuses both and writes nothing outside")
    src = open(os.path.join(HERE, "relentless_exam.py"), encoding="utf-8").read()
    ok("--unsafe-paths\"" not in src.replace("WITHOUT --unsafe-paths", ""), "H1d no git apply --unsafe-paths in relentless_exam.py")
    # H2 every run gets a fresh tree: a sentinel the base run leaves cannot redden the break run
    files = os.path.join(tmp, "h2files")
    os.makedirs(files)
    with open(os.path.join(files, "t_once.py"), "w") as f:
        f.write("import os, sys\nif os.path.exists('sentinel'):\n    print('FAIL sentinel'); sys.exit(1)\n"
                "open('sentinel', 'w').write('x')\nprint('ok')\n")
    with open(os.path.join(repo, "README.md"), "w") as f:
        f.write("readme\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-qm", "readme")
    sha = git(repo, "rev-parse", "HEAD")
    noop = "--- a/README.md\n+++ b/README.md\n@@ -1 +1 @@\n-readme\n+readme changed\n"
    fw = FakeWall(repo, tempfile.mkdtemp(dir=tmp, prefix="boxes")).install()
    try:
        run, read_file, close = E.box_runner({}, repo, sha, files, runner=fw.runner)
        c = clause("c1", ["python3", ".exam/t_once.py"], brk={"kind": "patch", "patch": noop})
        v = E.validate(with_clause(c), run, ITEM_TEXT, read_file=read_file)
        ok(codes(v) == ["STAYS_GREEN"] and len(fw.boxes) == 3 and len(set(fw.removed)) == 2,
           "H2 each run is a fresh box (a no-op break with a sentinel test stays green, not a false red) %s %d" % (codes(v), len(fw.boxes)))
        ok(not os.path.exists(os.path.join(read_file.tree, "sentinel")), "H2b the first box (read_file, Setter cwd) is never run in")
        # H4 the whole output reaches red_kind through box_runner
        e, out, to = run(["python3", "-c", "import sys; print('ImportError: no x'); print('.' * 20000); print('FAIL'); sys.exit(1)"], None, 60)
        ok(len(out) > 20000 and E.red_kind(clause("c9", ["x"]), e, out, to).startswith("infra:ImportError"),
           "H4 an ImportError before a 20000-char dump still disqualifies the red (len %d)" % len(out))
        e, out, to = run(["python3", "-c", "print(1)"], esc, 60)
        ok(e is None and out.startswith("PATCH_FAILED") and "unsafe" in out, "H1e box_runner's run refuses the escaping break")
        close()
    finally:
        fw.restore()
    # H3 a second run on the same item while the first holds the lock: busy, nothing touched
    store = R.Store(os.path.join(tmp, "h3"))
    it = "FOO_DOUBLE_RUNS_TWICE"
    E.set_status(store, it, state="setting", base=base)
    called = []
    with E._RunLock(E.item_dir(store, it)) as lk:
        st = E.run_item(store, it, None, CFG, setter=lambda *a, **k: called.append(1), boxer=local_boxer(repo, tmp),
                        text_of=lambda i: ITEM_TEXT)
        ok(lk.held() and st == "busy" and not called and E.status(store, it)["state"] == "setting",
           "H3 a concurrent run_item on one item returns busy and leaves the first run alone")
    import relentless_dispute as D
    with D.session_lock(store, it):
        ok(E.run_item(store, it, None, CFG, setter=lambda *a, **k: called.append(1), boxer=local_boxer(repo, tmp),
                      text_of=lambda i: ITEM_TEXT) == "busy" and not called, "H3b a dispute amend holding setter.lock makes run_item busy")
    ok(E.run_item(store, "NEVER_OWED_ITEM", None, CFG, setter=lambda *a, **k: called.append(1)) is None
       and not os.path.exists(E.item_dir(store, "NEVER_OWED_ITEM")), "H3c run_item on a never-owed item makes no exam directory")
    # H5 argv[0] and root-level test files are named, and their contents move the hash
    ok(E.named_files(["python3", "test_acceptance.py"]) == ["test_acceptance.py"] and E.named_files(["./run.sh"]) == ["run.sh"]
       and ".exam/t.sh" in E.named_files(["bash", "-c", ".exam/t.sh && echo ok"]) and E.named_files(["python3", "../x.py"]) == [],
       "H5a argv[0], ./x.sh and root-level files are named; ../ is not")
    ex = with_clause(clause("c1", ["python3", "test_acceptance.py"]))
    h = [E.validate(ex, lambda *a: (1, "FAIL", False), ITEM_TEXT, read_file=lambda p, b=b: b)["exam_hash"] for b in (b"one", b"two")]
    ok(h[0] != h[1], "H5b changing a root-level test file moves exam_hash")
    # H6 a failed kick stays re-owable: the next contract or start retries the unit; a good kick clears it
    store = R.Store(os.path.join(tmp, "h6"))
    roots, kicks = [store.root], []

    def kicker(res):
        return lambda s, i, c: (kicks.append(i), res)[1]
    E.on_contract(store, "K_I_CK", "abc", cfg=CFG, kicker=kicker("no systemd"), roots=roots)
    m = E.on_contract(store, "K_I_CK", "abc", cfg=CFG, kicker=kicker(None), roots=roots)
    rec = E.status(store, "K_I_CK")
    ok(len(kicks) == 2 and "Setter unit" in (m or "") and not rec.get("kick_failed") and rec.get("kick_tries") == 2,
       "H6a a contract after a failed kick retries the unit %s" % rec)
    ok(E.on_contract(store, "K_I_CK", "abc", cfg=CFG, kicker=kicker(None), roots=roots) is None and len(kicks) == 2,
       "H6b once started, never kicked again")
    E.on_contract(store, "K_I_CK2", "abc", cfg=CFG, kicker=kicker("down"), roots=roots)
    E.on_start(store, {"item": "K_I_CK2", "contract": {"proof": "x"}, "base": "abc"}, cfg=CFG, kicker=kicker(None), roots=roots)
    ok(kicks[-1] == "K_I_CK2" and len(kicks) == 4 and not E.status(store, "K_I_CK2").get("kick_failed"),
       "H6c an item start after a failed kick retries it too")
    E.set_status(store, "K_I_CK3", state="owed", hook_error="OSError: x")          # the hook faulted before owe() wrote base
    E.on_contract(store, "K_I_CK3", "base3", cfg=CFG, kicker=kicker(None), roots=roots)
    rec = E.status(store, "K_I_CK3")
    ok(rec.get("base") == "base3" and rec.get("mode") == "shadow" and not rec.get("hook_error"),
       "H6d a re-owe after a hook fault fills the missing base %s" % rec)
    n = len(kicks)
    for _ in range(8):
        E.on_contract(store, "K_I_CK4", "abc", cfg=dict(CFG, kick_max_tries=3), kicker=kicker("down"), roots=roots)
    ok(len(kicks) - n == 3 and E.status(store, "K_I_CK4")["kick_tries"] == 3, "H6e kick retries stop at kick_max_tries")

    def slow_start(s_, i, c):
        E.set_status(s_, i, state="setting")                                       # the unit started, then systemd-run timed out
        return "TimeoutExpired: systemd-run"
    E.on_contract(store, "K_I_CK5", "abc", cfg=CFG, kicker=slow_start, roots=roots)
    rec = E.status(store, "K_I_CK5")
    ok(rec["state"] == "setting" and not rec.get("kick_failed"), "H6f a slow start that did start is not overwritten to owed %s" % rec)
    ok(not E.unsafe_patch_paths('--- "a/caf\\303\\251.py"\n+++ "b/caf\\303\\251.py"\n')
       and E.unsafe_patch_paths('--- "a/\\056\\056/q"\n+++ "b/\\056\\056/q"\n'), "H1f a quoted non-ASCII name is safe; a quoted \\056\\056 is not")


def main():
    tmp = tempfile.mkdtemp(prefix="selftest_exam_")
    try:
        t_validate(tmp)
        t_hash(tmp)
        t_maps()
        t_review_fixes()
        t_shadow(tmp)
        t_echoes(tmp)
        t_on_contract(tmp)
        t_backfill()
        t_run_item(tmp)
        t_harden(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("RESULT %s (%d failed)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
