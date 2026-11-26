#!/usr/bin/env python3
"""Selftest of the certificate's red_seen proof (RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN), the cases its
acceptance test does not hold: a run that reached no verdict (a signal, a command the shell could not run) is never a
red proof; a fault that edits the test itself is refused; a test that writes a file it reads is restored and earns
nothing; a non-ASCII path is restored; unreadable evidence is "did not run", never "no proof", and is never overwritten;
--resume reruns a stamp that never ran. No game, no model.

    python3 src/RimMandrake/rimflow/selftest_red_seen.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge_certificate as JC  # noqa: E402

MOD = "Fix"
RESULTS = []


def ok(c, what):
    RESULTS.append(bool(c))
    print(("PASS  " if c else "FAIL  ") + what)


class R:
    def __init__(self, rc, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def fixture(root):
    os.makedirs(os.path.join(root, "design/concepts", MOD, "version"))
    os.makedirs(os.path.join(root, "src"))
    for name, body in (("kernel.py", "LIMIT = 5\n"), ("café.py", "X = 1\n"), ("Deck.cs", "float shield = 0.35f;\n"),
                       ("t_good.py", "import sys\nsys.path.insert(0, 'src')\nimport kernel\n"
                                     "sys.exit(0 if kernel.LIMIT == 5 else 1)\n"),
                       ("t_writer.py", "import sys\nopen('src/kernel.py', 'a').write('# written by the test\\n')\n"
                                       "sys.exit(1)\n")):
        with open(os.path.join(root, "src", name), "w", encoding="utf-8") as f:
            f.write(body)
    t = lambda f: {"kind": "offline", "stage": "4-5", "file": "src/" + f, "reads": ["src/kernel.py"],  # noqa: E731
                   "command": "%s src/%s" % (sys.executable, f)}
    live = dict(t("t_good.py"), kind="live_minimal", stage="6", reads=["src/Deck.cs", "src/kernel.py"])
    tt = {"mod": MOD, "version": "0.1.0", "tests": {"T_GOOD": t("t_good.py"), "T_WRITER": t("t_writer.py"), "sc_live": live},
          "bars": [{"id": "b", "decides": ["T_GOOD"], "offline_decides": ["T_GOOD"]}]}
    with open(JC.tpath(root, MOD), "w") as f:
        json.dump(tt, f)
    subprocess.run(["git", "init", "-q"], cwd=root)
    patches = {}
    for name, path, old, new in (("fault", "src/kernel.py", "LIMIT = 5", "LIMIT = 50"),
                                 ("self", "src/t_good.py", "import kernel", "import kernel  # x"),
                                 ("accent", "src/café.py", "X = 1", "X = 2"),
                                 ("cs", "src/Deck.cs", "float shield = 0.35f;", "float shield = 0f;")):
        p = os.path.join(root, name + ".patch")
        with open(p, "w", encoding="utf-8") as f:
            f.write("--- a/%s\n+++ b/%s\n@@ -1 +1 @@\n-%s\n+%s\n" % (path, path, old, new))
        patches[name] = p
    return patches


def red_record(root):
    try:
        return json.load(open(os.path.join(root, "design/concepts", MOD, JC.RED_SEEN)))
    except (OSError, ValueError):
        return {}


def main():
    root = tempfile.mkdtemp(prefix="redseen_")
    try:
        P = fixture(root)
        kernel = open(os.path.join(root, "src/kernel.py")).read()
        for rc, what in ((-15, "a run killed by a signal"), (143, "a shell child killed by SIGTERM"),
                         (127, "a command the shell could not find"),
                         (126, "a command the shell could not run")):
            r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"], runner=lambda *a, rc=rc, **k: R(rc))
            ok(r["ok"] is False and "to a verdict" in r["why"] and "T_GOOD" not in red_record(root),
               "%s (rc %s) is no red proof (%s)" % (what, rc, r["why"][:80]))
        ok(open(os.path.join(root, "src/kernel.py")).read() == kernel, "the fault is reversed after each of those")
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["self"])
        ok(r["ok"] is False and "the test" in r["why"] and "T_GOOD" not in red_record(root),
           "a fault that edits the test itself is refused (%s)" % r["why"][:90])
        tt = json.load(open(JC.tpath(root, MOD)))
        tt["tests"]["T_DOT"] = dict(tt["tests"]["T_GOOD"], file="./src/t_good.py")
        with open(JC.tpath(root, MOD), "w") as f:
            json.dump(tt, f)
        r = JC.red_seen(root, MOD, "T_DOT", patch=P["self"])
        ok(r["ok"] is False and "the test" in r["why"], "the same, spelled ./src/t_good.py in the table (%s)" % r["why"][:80])
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"],
                        runner=lambda *a, **k: (open(os.path.join(root, "src/new_output.txt"), "w").write("x"), R(1))[1])
        ok(r["ok"] is False and "new_output.txt" in r["why"] and "T_GOOD" not in red_record(root),
           "a run that creates a file outside what it reads earns nothing and is named (%s)" % r["why"][:90])
        os.remove(os.path.join(root, "src/new_output.txt"))
        r = JC.red_seen(root, MOD, "T_WRITER", patch=P["fault"])
        ok(r["ok"] is False and "kernel.py" in r["why"] and "T_WRITER" not in red_record(root)
           and open(os.path.join(root, "src/kernel.py")).read() == kernel,
           "a test that writes a file it reads is restored and earns nothing (%s)" % r["why"][:90])
        accent = open(os.path.join(root, "src/café.py"), encoding="utf-8").read()
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["accent"],
                        runner=lambda *a, **k: (open(os.path.join(root, "src/café.py"), "a").write("#\n"), R(1))[1])
        ok(r["ok"] is False and open(os.path.join(root, "src/café.py"), encoding="utf-8").read() == accent,
           "a non-ASCII path the run changed is seen and restored (%s)" % r["why"][:90])
        # RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START: a command that dies the same way with no fault
        # (an import error, a shell syntax error: all 46 Pyrelands live commands, 2026-11-20) proves nothing
        dead = "ModuleNotFoundError: No module named 'modcheck'"
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"], runner=lambda *a, **k: R(1, dead))
        ok(r["ok"] is False and "without the fault" in r["why"] and "T_GOOD" not in red_record(root),
           "a command that fails the same way without the fault is no red proof (%s)" % r["why"][:100])
        # RIMMANDRAKE_REFUSE_LIVE_RED_SEEN_ON_A_FAULT_THE_GAME_NEVER_LOADS (FlowWorks visit 6, 2026-11-22): an in-game check
        # drives the DEPLOYED build; a C# or XML fault planted in the tree never reaches it, so a red there is the check's
        # own chance (sc_hung_bridge reads FAIL about one run in two on the real build) and proves nothing about the fault
        calls = []
        flip = lambda *a, **k: (calls.append(1), R(1, "FAIL GRATE") if len(calls) == 1 else R(0, "PASS"))[1]  # noqa: E731
        r = JC.red_seen(root, MOD, "sc_live", patch=P["cs"], runner=flip)
        ok(r["ok"] is False and r["why"].startswith("did not run") and "Deck.cs" in r["why"] and not calls
           and "sc_live" not in red_record(root) and open(os.path.join(root, "src/Deck.cs")).read() == "float shield = 0.35f;\n",
           "an in-game check planted with a C# fault the game never loads is refused before it runs (%s)" % r["why"][:110])
        calls.clear()
        r = JC.red_seen(root, MOD, "sc_live", patch=P["fault"], runner=flip)
        ok(r["ok"] is True and red_record(root).get("sc_live", {}).get("rc") == 1,
           "control: an in-game check planted in harness Python it runs from the tree is still recorded (%s)" % r["why"][:80])
        # RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_THREE (2026-11-26): `scene.py accept` refuses a tree that differs
        # from its commit (REFUSED TREE_NOT_CLEAN, exit 3) and exits 0 on a scene that prints FAIL, so a planted fault in the
        # tree yields exit 3 whatever the scene would read: a red here proves nothing. A scene proves its red with --plant.
        tt = json.load(open(JC.tpath(root, MOD)))
        tt["tests"]["sc_scene"] = dict(tt["tests"]["sc_live"], command="python.exe src\\RimMandrake\\Utils\\scene.py accept "
                                       "src\\RimMandrake\\X\\proof\\scene_x.py   (release build, minimal list)")
        with open(JC.tpath(root, MOD), "w") as f:
            json.dump(tt, f)
        calls.clear()
        def refused(*a, **k):      # accept as it behaves: a tree the patch changed is refused (exit 3); a clean one runs the scene
            calls.append(1)
            if open(os.path.join(root, "src/kernel.py")).read() != kernel:
                return R(3, "REFUSED TREE_NOT_CLEAN: 1 path(s) differ from the commit")
            return R(0, "PASS sc_x: 0 failing row(s)")
        r = JC.red_seen(root, MOD, "sc_scene", patch=P["fault"], runner=refused)
        ok(r["ok"] is False and r["why"].startswith("did not run") and "--plant" in r["why"] and not calls
           and "sc_scene" not in red_record(root) and open(os.path.join(root, "src/kernel.py")).read() == kernel,
           "a scene.py accept check is refused before it runs: a planted tree reads TREE_NOT_CLEAN, not red (%s)" % r["why"][:110])
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"])
        ok(r["ok"] is True and red_record(root).get("T_GOOD", {}).get("rc") == 1, "control: a real red is recorded")
        JC.run_offline(root, MOD)
        tt = json.load(open(JC.tpath(root, MOD)))
        good = tt["tests"]["T_GOOD"]["command"]
        tt["tests"]["T_GOOD"]["command"] = "true"
        with open(JC.tpath(root, MOD), "w") as f:
            json.dump(tt, f)
        JC.run_offline(root, MOD)
        v = JC.certify(root, MOD)
        ok([x for x in v["rows"] if x["clause"] == "red_seen" and x["status"] == "REFUSED" and "command" in x["observed"]],
           "a red proof of another command does not pass the clause")
        tt = json.load(open(JC.tpath(root, MOD)))
        tt["tests"]["T_GOOD"]["command"] = good
        with open(JC.tpath(root, MOD), "w") as f:
            json.dump(tt, f)
        rs = os.path.join(root, "design/concepts", MOD, JC.RED_SEEN)
        with open(rs, "w") as f:
            f.write("{ not json")
        JC.grandfather(root, MOD)
        JC.run_offline(root, MOD)
        v = JC.certify(root, MOD)
        row = [x for x in v["rows"] if x["clause"] == "red_seen"]
        ok(row and row[0]["status"] == "WARN" and "did not run" in row[0]["observed"]
           and any("red_seen did not run" in d for d in v["did_not_run"]),
           "unreadable red_seen evidence reads did not run, never 'no proof' (%s)" % (row[:1],))
        r = JC.red_seen(root, MOD, "T_GOOD", patch=P["fault"])
        ok(r["ok"] is False and open(rs).read() == "{ not json", "unreadable evidence is never overwritten")
        tt = json.load(open(JC.tpath(root, MOD)))
        tt["tests"]["T_GOOD"]["runs_today"]["ran"] = False
        with open(JC.tpath(root, MOD), "w") as f:
            json.dump(tt, f)
        s = JC.run_offline(root, MOD, resume=True)
        ok(s.get("ran", 0) >= 1 and json.load(open(JC.tpath(root, MOD)))["tests"]["T_GOOD"]["runs_today"]["ran"] is True,
           "--resume reruns a stamp that never ran (%s)" % s)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
