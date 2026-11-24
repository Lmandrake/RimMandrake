#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_BUILD_VISIT_AND_CYCLE_KITS_SEVENTEEN_COPIES_TODAY (rank 2 of one_page.md), the offline part.
The live part (one real visit through the kit) has no offline test; the item says how it is read.

Contract:
  src/RimMandrake/rimflow/visit_kit.py
    open_plan(mod, visits_dir) -> {"visit", "folder", "last_visit": path or None, "could_not_look": [str], "text"}
        makes nothing from another mod's folder; with no last visit it says so.
    run_scenes(scenes, out_dir, build_read, expect_build, deadline_s=3600) -> {"status": "value"|"empty", "rows": [row]}
        scenes: [{"id", "argv"}]; a scene prints one line `ROW {json with "verdict"}` per row. row = {"scene", "check",
        "verdict", "why", "build", "class": None}. A scene that dies, hangs, prints no row, cannot start, or runs on a
        build other than expect_build (build_read() is read before each scene; None is unreadable) leaves a row
        COULD NOT LOOK with the cause. The kit never sets a class. Rows go to <out_dir>/rows.jsonl.
  src/RimMandrake/rimflow/cycle_kit.py
    lane2(faults, deciders, root, out_path, deadline_s=600) -> {"status": "value"|"empty", "rows": [row], "tree_clean": bool}
        faults: [{"id", "patch"}] written by the judge, none by the kit. deciders: [{"id", "command"}] (shell). Each
        decider runs on the clean tree first; one that is not green there is could_not_look for every fault. row =
        {"fault", "decider", "verdict": "caught"|"not_caught"|"could_not_look", "rc", "why"}; rc 1 is caught, 0 is not.
Expected when built: PASS 19/19."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

VK, CK = H.load("visit_kit"), H.load("cycle_kit")
PY = sys.executable


def scene(code, sid="s1"):
    return {"id": sid, "argv": [PY, "-c", code]}


def run(scenes, read=lambda: "BUILD1", deadline=20):
    d = tempfile.mkdtemp()
    r = H.need(VK).run_scenes(scenes, d, read, "BUILD1", deadline_s=deadline)
    return r, d


ROW = "import json; print('ROW ' + json.dumps({'check': 'c1', 'verdict': '%s', 'why': 'w'}))"


def one(code, **k):
    r, _ = run([scene(code)], **k)
    return r["rows"][0]


H.check("a scene that passes leaves its row, on its build, with no class", lambda: (
    lambda x: x["verdict"] == "PASS" and x["build"] == "BUILD1" and x["class"] is None)(one(ROW % "PASS")))
H.check("a FAIL stays FAIL, and the kit does not class it", lambda: (
    lambda x: x["verdict"] == "FAIL" and x["class"] is None)(one(ROW % "FAIL")))
H.check("a scene that dies leaves COULD NOT LOOK with its exit", lambda: (
    lambda x: x["verdict"] == "COULD NOT LOOK" and "3" in x["why"])(one("import sys; sys.exit(3)")))
H.check("a scene that ends well with no row is COULD NOT LOOK, never PASS", lambda: one("pass")["verdict"] == "COULD NOT LOOK")
H.check("a scene that dies after a PASS row keeps the row and adds COULD NOT LOOK", lambda: sorted(
    x["verdict"] for x in run([scene(ROW % "PASS" + "; import sys; sys.exit(9)")])[0]["rows"]) == ["COULD NOT LOOK", "PASS"])
H.check("hung: a scene past the deadline is COULD NOT LOOK, and the why says hung", lambda: (
    lambda x: x["verdict"] == "COULD NOT LOOK" and "hung" in x["why"].lower())(one("import time; time.sleep(30)", deadline=2)))
H.check("missing: a scene that cannot start is COULD NOT LOOK", lambda: run(
    [{"id": "s", "argv": ["/no/such/program"]}])[0]["rows"][0]["verdict"] == "COULD NOT LOOK")
H.check("stale: the wrong build is COULD NOT LOOK and names both builds", lambda: (
    lambda x: x["verdict"] == "COULD NOT LOOK" and "OLD" in x["why"] and "BUILD1" in x["why"])(one(ROW % "PASS", read=lambda: "OLD")))
H.check("an unreadable build is COULD NOT LOOK", lambda: one(ROW % "PASS", read=lambda: None)["verdict"] == "COULD NOT LOOK")
H.check("one dead scene does not stop the next", lambda: [x["verdict"] for x in run(
    [scene("import sys; sys.exit(3)"), scene(ROW % "PASS", "s2")])[0]["rows"]] == ["COULD NOT LOOK", "PASS"])
H.check("empty: no scenes reads empty, not a pass", lambda: run([])[0]["status"] == "empty" and run([])[0]["rows"] == [])
H.check("the rows are on disk", lambda: (lambda r, d: len(open(os.path.join(d, "rows.jsonl")).read().splitlines()) == 1)(
    *run([scene(ROW % "PASS")])))


def plan():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "OtherMod", "visit_7"))
    p = H.need(VK).open_plan("NewMod", os.path.join(d, "NewMod"))
    return p["last_visit"] is None and "no last visit" in p["text"].lower() and "OtherMod" not in p["text"]


H.check("a mod with no last visit says so and takes nothing from another mod", plan)


def tree():
    d = tempfile.mkdtemp()
    open(os.path.join(d, "a.py"), "w").write("X = 1\nY = 5\n")
    g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", d] + list(a), check=True,  # noqa: E731
                                  capture_output=True)
    g("init", "-q", "-b", "main")
    g("add", ".")
    g("commit", "-qm", "c")
    return d


def patch(old, new, name="X"):
    p = os.path.join(tempfile.mkdtemp(), "f.patch")
    a, b = ("-X = %s\n+X = %s\n Y = 5\n" % (old, new)) if name == "X" else "", (" X = 1\n-Y = %s\n+Y = %s\n" % (old, new))
    with open(p, "w") as f:
        f.write("--- a/a.py\n+++ b/a.py\n@@ -1,2 +1,2 @@\n" + (a or b))
    return p


DEC = {"id": "d1", "command": "%s -B -c \"import sys; sys.path.insert(0,'.'); import a; sys.exit(0 if a.X == 1 else 1)\"" % PY}


def lane(faults, deciders=None, deadline=20):
    d = tree()
    r = H.need(CK).lane2(faults, [DEC] if deciders is None else deciders, d, os.path.join(tempfile.mkdtemp(), "o.jsonl"),
                         deadline_s=deadline)
    if open(os.path.join(d, "a.py")).read() != "X = 1\nY = 5\n":
        raise RuntimeError("the tree was left with a fault in it")
    return r


H.check("a fault that the decider sees is caught; one it cannot see is not caught", lambda: [x["verdict"] for x in lane(
    [{"id": "f1", "patch": patch(1, 2)}, {"id": "f2", "patch": patch(5, 6, "Y")}])["rows"]] == ["caught", "not_caught"])
H.check("a fault that does not apply is could not look", lambda: lane([{"id": "f", "patch": patch(77, 78)}])["rows"][0]["verdict"] == "could_not_look")
H.check("hung: a decider that hangs is could not look, and the tree is put back", lambda: (
    lambda r: r["rows"][0]["verdict"] == "could_not_look" and r["tree_clean"])(
        lane([{"id": "f", "patch": patch(1, 2)}], [{"id": "d", "command": "grep -q 'X = 1' a.py || sleep 30"}], deadline=2)))
H.check("a decider that is red on the clean tree catches nothing: could not look", lambda: lane(
    [{"id": "f", "patch": patch(1, 2)}], [{"id": "d", "command": "exit 1"}])["rows"][0]["verdict"] == "could_not_look")
H.check("empty: no faults reads empty, and the kit writes no fault of its own", lambda: (
    lambda r: r["status"] == "empty" and r["rows"] == [])(lane([])))
H.check("the page names its promises and the selftests run at ./publish", lambda: H.page(
    "design/specs/2026-11-23-visit-and-cycle-kits/boundary.md", "a-dead-scene-leaves-a-row", "the-kit-never-classes",
    "the-kit-writes-no-fault") and H.listed("src/RimMandrake/rimflow/selftest_visit_kit.py")
    and H.listed("src/RimMandrake/rimflow/selftest_cycle_kit.py"))
H.done(19)
