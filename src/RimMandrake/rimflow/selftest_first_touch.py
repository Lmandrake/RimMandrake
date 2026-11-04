#!/usr/bin/env python3
"""selftest_first_touch.py - FIRST_TOUCH_BUILD_DESIGNER_READS_FIRST: an unstarted item naming a mod with no Designer pass on
record gets no worker, and the pass is filed once, needs=owner. Offline, no ledger write."""
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import first_touch as FT  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("  %s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def no_tree(_repo, _mod):
    return False


def main():
    mapping = {"RimMandrake/FlowWorks": "FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS"}
    states = {"X_FIX": "proposed", "FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS": "proposed"}
    so = states.get

    why, owed = FT.hold(REPO, "X_FIX", ["RimMandrake/Pyrelands"], so, mapping, no_tree)
    check("a mod with no pass holds the item", why and "no Designer pass on record" in why, why)
    check("and owes its generated pass", owed == [("RimMandrake/Pyrelands", "PYRELANDS_DESIGN_FIRST_TOUCH")], owed)

    why, owed = FT.hold(REPO, "X_FIX", ["RimMandrake/FlowWorks"], so, mapping, no_tree)
    check("a hand-filed pass still open holds", why and "FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS" in why, why)
    check("but is not filed again", owed == [], owed)

    done = dict(states, FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS="done")
    check("a done pass releases", FT.hold(REPO, "X_FIX", ["RimMandrake/FlowWorks"], done.get, mapping, no_tree) == (None, []))
    check("a gating concept tree releases",
          FT.hold(REPO, "X_FIX", ["RimMandrake/Pyrelands"], so, mapping, lambda r, m: True) == (None, []))
    two = FT.hold(REPO, "X_FIX", ["RimMandrake/FlowWorks", "RimMandrake/Pyrelands"], done.get, mapping, no_tree)
    check("every named mod needs its pass", two[0] and "Pyrelands" in two[0] and "FlowWorks (" not in two[0], two)
    lost = FT.hold(REPO, "X_FIX", ["RimMandrake/Bones"], so, {"RimMandrake/Bones": "BAROQUE_X"}, no_tree)
    check("a hand-mapped pass never filed holds, loudly", lost[0] and "BAROQUE_X, not filed" in lost[0], lost)
    check("and Relentless does not file the owner's id", lost[1] == [], lost)
    check("no mod named, no hold", FT.hold(REPO, "X_FIX", [], so, mapping, no_tree) == (None, []))
    check("the pass item itself is never held", FT.hold(
        REPO, "FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS", ["RimMandrake/FlowWorks"], so, mapping, no_tree) == (None, []))
    check("a generated pass item is never held", FT.hold(
        REPO, "PYRELANDS_DESIGN_FIRST_TOUCH", ["RimMandrake/Pyrelands"], so, mapping, no_tree) == (None, []))
    for s in ("doing", "built", "validated"):
        check("a started item (%s) is not pulled off" % s, FT.hold(
            REPO, "X_FIX", ["RimMandrake/Pyrelands"], dict(states, X_FIX=s).get, mapping, no_tree) == (None, []))
    check("an unfiled item (no state) is held", FT.hold(
        REPO, "NEW", ["RimMandrake/Pyrelands"], so, mapping, no_tree)[0] is not None)

    # the default tree check (no `tree` argument): the real first_touch.tree_gates, reading
    # design/concepts/<Folder>/tree.json in a fixture repo and asking concept_tree.gate about THAT folder
    import tempfile
    import concept_tree as CT
    real_gate = CT.gate
    with tempfile.TemporaryDirectory() as fake:
        asked = []
        try:
            CT.gate = lambda d, repo=None, floor_file=None: (asked.append(os.path.realpath(d)), ([], []))[1]
            check("no tree.json holds, even with a gate that would pass",
                  FT.hold(fake, "X_FIX", ["RimMandrake/Pyrelands"], so, mapping)[0] is not None)
            check("and the gate is not asked about a missing tree", asked == [], asked)
            tdir = os.path.join(fake, "design", "concepts", "Pyrelands")
            os.makedirs(tdir)
            with open(os.path.join(tdir, "tree.json"), "w", encoding="utf-8") as f:
                f.write("{}")
            check("a tree.json whose gate passes releases (default tree check)",
                  FT.hold(fake, "X_FIX", ["RimMandrake/Pyrelands"], so, mapping) == (None, []))
            check("the gate was asked about the mod's own concepts folder", asked == [os.path.realpath(tdir)], asked)
            check("another mod's tree does not release this one",
                  FT.hold(fake, "X_FIX", ["RimMandrake/Bones"], so, mapping)[0] is not None)
            CT.gate = lambda d, repo=None, floor_file=None: (["no Arbiter coverage signature"], [])
            check("a tree.json whose gate refuses holds",
                  FT.hold(fake, "X_FIX", ["RimMandrake/Pyrelands"], so, mapping)[0] is not None)

            def boom(d, repo=None, floor_file=None):
                raise ValueError("unreadable")
            CT.gate = boom
            check("a gate that throws holds (fails shut)",
                  FT.hold(fake, "X_FIX", ["RimMandrake/Pyrelands"], so, mapping)[0] is not None)
        finally:
            CT.gate = real_gate
        check("the real gate on an empty tree.json holds",
              FT.hold(fake, "X_FIX", ["RimMandrake/Pyrelands"], so, mapping)[0] is not None)

    # the committed map: the four recent mods, Baroque Biomes by its compose members
    real = FT.pass_map(REPO, FT.load_passes())
    check("GSS maps to its filed pass", real.get("RimMandrake/GimmeSomeSlack") == "GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS")
    check("Solar maps to its filed pass", real.get("RimMandrake/SolarMirrors") == "SOLAR_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS")
    check("FlowWorks maps to its filed pass", real.get("RimMandrake/FlowWorks") == "FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS")
    baroque = sorted(m for m, i in real.items() if i == "BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS")
    check("Baroque Biomes covers its compose members", "RimMandrake/Bones" in baroque and len(baroque) > 10, baroque)
    for m, _ in real.items():
        if not os.path.isfile(os.path.join(REPO, "src", m, "About", "About.xml")):
            check("mapped mod %s is a real mod folder" % m, False, m)
    check("an unreadable compose maps nothing", FT.pass_map(REPO, {"compose": {"src/RimMandrake/NOPE.json": "X"}}) == {})

    # every generated name fits the cap and passes rimflow's grammar
    longest = FT.pass_item_id("RimMandrake/" + "A" * 60)
    check("the generated id keeps the cap", len(longest) <= FT.NAME_CAP, longest)
    nc = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", FT.pass_item_id("RimMandrake/HugeThingsTestRaces")],
                        capture_output=True, text=True, timeout=60)
    check("namecheck accepts a generated id", nc.returncode == 0 and "OK" in nc.stdout, (nc.stdout + nc.stderr)[-300:])

    # the wiring: Relentless asks at the pool and at the lease, and files each owed pass once
    import relentless as R
    src = open(R.__file__, encoding="utf-8").read()
    check("pool_order filters through first_touch_hold", "if not self.first_touch_hold(i.id)]" in src)
    check("concept_refusal (the lease) asks first_touch_hold", "or self.first_touch_hold(item)" in src)
    fx = R.Effects.__new__(R.Effects)
    fx.books, fx.r, fx._ledger = REPO, {"seat": "BENCH", "first_touch_hold": True}, None
    items = {"A_FIX": "proposed", "B_FIX": "ready", "C_FIX": "doing"}
    fx._ledger = ([], types.SimpleNamespace(items={k: types.SimpleNamespace(state=v, kind="bug", title="")
                                                   for k, v in items.items()}))
    fx.item_mods = lambda st: ["RimMandrake/Oracle"]
    calls = []
    fx.rimflow = lambda *a, **k: (calls.append(a), types.SimpleNamespace(returncode=0, stdout="", stderr=""))[1]
    a, b, c = fx.first_touch_hold("A_FIX"), fx.first_touch_hold("B_FIX"), fx.first_touch_hold("C_FIX")
    check("Effects holds both unstarted items", bool(a) and bool(b), (a, b))
    check("Effects leaves the started one", c is None, c)
    check("the pass is filed once", [x[1] for x in calls] == ["ORACLE_DESIGN_FIRST_TOUCH"], calls)
    check("filed needs=owner, kind task, for the seat", calls and calls[0][0] == "file" and "--needs" in calls[0]
          and calls[0][calls[0].index("--needs") + 1] == "owner" and calls[0][calls[0].index("--for") + 1] == "BENCH"
          and calls[0][calls[0].index("--kind") + 1] == "task", calls)
    fx.r["first_touch_hold"], fx._first_touch = False, {}
    check("the rule off releases", fx.first_touch_hold("A_FIX") is None)
    rules = R.rules()
    check("the shipped rules hold", rules.get("first_touch_hold") is True, rules.get("first_touch_hold"))

    print("selftest_first_touch: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
