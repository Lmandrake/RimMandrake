#!/usr/bin/env python3
"""Selftest of the certificate's asks_on_empty_game clause (RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED):
before an in-game visit, a bar decided by a FlowWorks-harness scene that passes a row on an empty game is refused,
naming the row; an honest scene is not; a scene in another harness, or a scene file that cannot load, is did_not_run and
refuses nothing; a blind-challenge certificate does not read the clause. No game, no bridge, no model.

    python3 src/RimMandrake/rimflow/selftest_asks_on_empty_game.py
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge_certificate as JC  # noqa: E402

SCENES = '''
def scene_vac(B, snapshot, reload_snapshot, receipt, save_mid=None, load_mid=None):
    B.call("jawa/spawn_pawn")
    return {"rows": [{"id": "V_pass_on_nothing", "status": "PASS"}, {"id": "V_un", "status": "UNMEASURED"}]}

def scene_honest(B, snapshot, reload_snapshot, receipt, save_mid=None, load_mid=None):
    r = B.call("jawa/read")
    return {"rows": [{"id": "H", "status": "PASS" if r.get("value") else "UNMEASURED"}]}

STAGE3_SCENES = {"scene_vac": scene_vac, "scene_honest": scene_honest}
'''
FW = "src/RimMandrake/FlowWorks/northstar/concept_scenes.py"
RESULTS = []
ROOTS = []


def ok(c, what):
    RESULTS.append(bool(c))
    print(("PASS  " if c else "FAIL  ") + what)


def table():
    tests = {"sc_vac": {"kind": "live_minimal", "file": FW, "entry": "scene_vac", "command": "x"},
             "sc_honest": {"kind": "live_minimal", "file": FW, "entry": "scene_honest", "command": "x"},
             "sc_suite": {"kind": "live_minimal", "file": "src/RimMandrake/M/validation.py", "entry": "scene_s",
                          "command": "x"}}
    bars = [{"id": "bar_vac", "proves_at": "6", "decides": ["sc_vac"]},
            {"id": "bar_honest", "proves_at": "6", "decides": ["sc_honest"]},
            {"id": "bar_suite", "proves_at": "6", "decides": ["sc_suite"]}]
    return {"tests": tests, "bars": bars}


def root_with(scenes_src, tt):
    root = tempfile.mkdtemp(prefix="aoeg_")
    ROOTS.append(root)
    os.makedirs(os.path.join(root, "design/concepts/M/version"))
    with open(os.path.join(root, "design/concepts/M/version/test_table.json"), "w") as f:
        json.dump(tt, f)
    if scenes_src is not None:
        os.makedirs(os.path.join(root, os.path.dirname(FW)))
        with open(os.path.join(root, FW), "w") as f:
            f.write(scenes_src)
    return root


SUITE = '''
import os, subprocess
from modcheck import Suite
suite = Suite("M")

@suite.chain("scene_s")
def scene_s(t):
    for act in (lambda: open(%(w)r, "w").write("x"), lambda: subprocess.run(["touch", %(p)r]),
                lambda: os.makedirs(%(d)r)):
        try:
            act()
        except OSError:
            pass
    with t.component("c_vac"):
        pass
'''


def suite_run():
    """-> (certificate, [marks made]) for a Suite chain that writes, spawns and makes a dir before a vacuous row."""
    out = tempfile.mkdtemp(prefix="aoeg_out_")
    ROOTS.append(out)
    marks = {"w": os.path.join(out, "written"), "p": os.path.join(out, "spawned"), "d": os.path.join(out, "made")}
    root = root_with(None, table())
    os.makedirs(os.path.join(root, "src/RimMandrake/M"))
    with open(os.path.join(root, "src/RimMandrake/M/validation.py"), "w") as f:
        f.write(SUITE % marks)
    v = JC.certify(root, "M", to="in_game")
    return v, [k for k, m in marks.items() if os.path.exists(m)]


def t_suite_run_writes_and_launches_nothing():
    """A Suite chain runs its setup for real (Pyrelands' save_fixture copies the live Saves folder): the --suite child
    refuses every write, subprocess and mkdir, and still lists the vacuous row."""
    v, made = suite_run()
    ok(not made, "a Suite chain run on an empty game writes, spawns and makes nothing (made: %s)" % made)
    ok([r["bar"] for r in v["rows"] if r["clause"] == "asks_on_empty_game"] == ["bar_suite"],
       "the sealed Suite run still refuses the bar its vacuous row decides (%s)" % v["rows"])


def t_refused_act_is_named():
    v, _made = suite_run()
    ok(any("sandbox refused 3" in d for d in v["did_not_run"]),
       "the refused acts are named with their count, never silent (%s)" % v["did_not_run"])


def t_csharp_and_scene_scripts_are_not_executed():
    """RIMMANDRAKE_REPAIR_JUDGE_CERTIFICATE_LOADS_CSHARP_AS_PYTHON_AND_CLAIMS_GAME: a C# proof file is never parsed as
    Python, and a scene-library script (imperative: it opens a game at import) is never run to look for a suite, so the
    reading is the same whether a game is held or free. Both are named as having no empty-game adapter."""
    work = tempfile.mkdtemp(prefix="aoeg_lock_")
    ROOTS.append(work)
    lock = os.path.join(work, "lock")
    script = ('with open(%r) as fh:\n    held = fh.read() == "held"\n'
              'if held:\n    raise RuntimeError("Refused: GAME_HELD: ArchSmall: HELD by another process")\n'
              'open(%r + ".claim", "w").write("claimed")\nprint("PASS V_row")\n') % (lock, lock)
    tt = {"tests": {"sc_cs": {"kind": "live_minimal", "file": "src/RimMandrake/M/Source/Proof.cs", "entry": "calib",
                              "command": "x"},
                    "sc_scene": {"kind": "live_minimal", "file": "src/RimMandrake/M/proof/scene_x.py",
                                 "entry": "sc_x", "command": "x"}},
          "bars": [{"id": "bar_cs", "proves_at": "6", "decides": ["sc_cs"]},
                   {"id": "bar_scene", "proves_at": "6", "decides": ["sc_scene"]}]}
    root = root_with(None, tt)
    os.makedirs(os.path.join(root, "src/RimMandrake/M/Source"))
    os.makedirs(os.path.join(root, "src/RimMandrake/M/proof"))
    with open(os.path.join(root, "src/RimMandrake/M/Source/Proof.cs"), "w", encoding="utf-8") as f:
        f.write("// \u00a7 the proof scenes\nnamespace M { public static class Proof { } }\n")
    with open(os.path.join(root, "src/RimMandrake/M/proof/scene_x.py"), "w") as f:
        f.write(script)
    seen = {}
    for state in ("held", "free"):
        with open(lock, "w") as f:
            f.write(state)
        seen[state] = JC.certify(root, "M", to="in_game")["did_not_run"]
    held = seen["held"]
    ok(not any("SyntaxError" in d or ("Proof.cs" in d and "did not load" in d) for d in held),
       "a C# proof file is not parsed as Python (%s)" % held)
    ok(not any("GAME_HELD" in d or "did not load" in d for d in held),
       "a scene script is not run to look for a suite, so a held game never reaches the certificate (%s)" % held)
    ok(seen["held"] == seen["free"], "the reading is the same with the game held as with it free (%s | %s)"
       % (seen["held"], seen["free"]))
    ok(not os.path.exists(lock + ".claim"), "loading a scene script never claims a game")
    ok(any("no empty-game adapter" in d and "Proof.cs" in d and "scene_x.py" in d for d in held),
       "both are named as having no empty-game adapter, never skipped silently (%s)" % held)


def main():
    v = JC.certify(root_with(SCENES, table()), "M", to="in_game")
    aoeg = [r for r in v["rows"] if r["clause"] == "asks_on_empty_game"]
    ok([r["bar"] for r in aoeg] == ["bar_vac"] and "V_pass_on_nothing" in aoeg[0]["observed"]
       and "V_un" not in aoeg[0]["observed"] and aoeg[0]["would_pass"] and aoeg[0]["smallest_fix"],
       "the scene that passes a row on nothing refuses its bar, naming that row, with would_pass and a fix (%s)" % aoeg)
    ok(v["ok"] is False, "a vacuous row makes the in-game certificate refuse")
    ok(any("did not run" in d and "validation.py" in d for d in v["did_not_run"]),
       "a Suite scene whose file is not there is did_not_run, naming the file (%s)" % v["did_not_run"])
    ok("asks_on_empty_game" in JC.summary(v) and "DID NOT RUN" in JC.summary(v),
       "the summary names the refusal and the clause that could not look")
    vb = JC.certify(root_with(SCENES, table()), "M", to="blind_challenge")
    ok(not [r for r in vb["rows"] if r["clause"] == "asks_on_empty_game"] and not vb["did_not_run"],
       "a blind-challenge certificate does not read the clause")
    tt = table()
    tt["bars"] = [b for b in tt["bars"] if b["id"] != "bar_suite"]
    vh = JC.certify(root_with(SCENES.replace('"status": "PASS"}, {"id": "V_un"', '"status": "FAIL"}, {"id": "V_un"'), tt),
                    "M", to="in_game")
    ok(vh["ok"] is True and not vh["did_not_run"], "honest scenes only: certified, nothing did_not_run (%s)" % vh)
    vm = JC.certify(root_with(None, tt), "M", to="in_game")
    ok(vm["ok"] is True and any("did not run" in d and "is not there" in d for d in vm["did_not_run"]),
       "a scene file that is not there is did_not_run and refuses nothing (%s)" % vm["did_not_run"])
    vx = JC.certify(root_with("raise RuntimeError('boom')\n", tt), "M", to="in_game")
    ok(vx["ok"] is True and any("did not load" in d for d in vx["did_not_run"]),
       "a scene file that raises on load is did_not_run and refuses nothing (%s)" % vx["did_not_run"])
    tg = table()
    tg["tests"]["sc_gone"] = {"kind": "live_minimal", "file": FW, "entry": "scene_gone", "command": "x"}
    tg["tests"]["sc_noentry"] = {"kind": "live_full", "file": "src/RimMandrake/M/proof.py", "command": "x"}
    tg["bars"] += [{"id": "bar_gone", "proves_at": "6", "decides": ["sc_gone"]},
                   {"id": "bar_noentry", "proves_at": "6", "decides": ["sc_noentry"]}]
    vg = JC.certify(root_with(SCENES, tg), "M", to="in_game")
    ok(any("scene_gone" in d and "STAGE3_SCENES" in d for d in vg["did_not_run"])
       and not [r for r in vg["rows"] if r["bar"] == "bar_gone"],
       "a FlowWorks entry missing from STAGE3_SCENES is did_not_run, never certified (%s)" % vg["did_not_run"])
    ok(any("proof.py" in d for d in vg["did_not_run"]), "an in-game test with no entry is did_not_run, not skipped")
    t_suite_run_writes_and_launches_nothing()
    t_refused_act_is_named()
    t_csharp_and_scene_scripts_are_not_executed()
    td = table()
    td["bars"].append({"id": "bar_undecided", "proves_at": "2", "decides": []})
    vd = JC.certify(root_with(SCENES, td), "M", to="in_game")
    try:
        line = JC.summary(vd)
    except Exception as e:  # noqa: BLE001
        line = "raised %r" % (e,)
    ok("bar_undecided" in line and "decided" in line, "a bar-level refusal (test None) reads in the summary (%s)" % line)
    for r in ROOTS:
        shutil.rmtree(r, ignore_errors=True)
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
