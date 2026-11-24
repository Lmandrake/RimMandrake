#!/usr/bin/env python3
"""selftest_declaration_check.py: the promises of design/specs/2026-11-24-declaration-check/boundary.md, one test of each
promise's name (boundary_check.py). Item RIMMANDRAKE_CATCH_WRONG_CHECK_DECLARATION_FOUR_PLANTS_MISSED.

Two subjects. The real one: Pyrelands at two fixed commits of this repository, with a frozen copy of its exercises.json
(testdata/declaration_check_pyrelands_20261124.json), so that a later edit of the mod never turns this test red. The planted
one: a throwaway git repository. Nothing here reaches a launcher, a live game or the ledger.

  --mutate blind       plants "a scene names nothing" (no evidence kind); the run must go red
  --mutate naming      plants "every check is named"; the run must go red
  --mutate no_rerun    plants "a named check does not rerun"; the run must go red
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import declaration_check as DC              # noqa: E402
import rerun_relation as RR                 # noqa: E402
import selftest_rerun_relation as T         # noqa: E402  (its throwaway repository)

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FROZEN = os.path.join(HERE, "testdata", "declaration_check_pyrelands_20261124.json")
FIX = "a6f05380df"        # the six Pyrelands fixes of 2026-11-24; the four wrong entries were planted over them
TODAY = "47d24ceb51"            # Pyrelands as its table was declared, before the visit-9 work moved on
SRC = "src/RimMandrake/Pyrelands/Source/"
# the share of single dropped C# paths that this check names, measured 2026-11-24: 71 of 174. A change that blinds it falls
# far below; a promise is only that it does not go blind, so the floor is half of the reading.
RECALL_FLOOR = 35
FAILS, SEEN = [], []
_REL = {}


def ok(what, cond, got=None):
    SEEN.append(what)
    if not cond:
        FAILS.append(what)
        print("FAIL  %s%s" % (what, "" if got is None else "\n      got: %s" % str(got)[:700]))


def pyre(new):
    """The Pyrelands relation at a commit, its entries those of the frozen table (a fresh copy)."""
    if new not in _REL:
        g = RR.Git(REPO)
        txt = g.show(new, "design/concepts/Pyrelands/version/test_table.json")
        if txt is None:
            print("COULD NOT LOOK: this clone has no commit %s" % new)
            sys.exit(2)
        _REL[new] = RR.Relation(REPO, "Pyrelands", json.loads(txt)["tests"], new=new)
    rel = _REL[new]
    rel.declare(RR.read_declarations(FROZEN))
    rel._py = {k: v for k, v in rel._py.items() if k[0] != "partwords"}
    return rel


def drop(tid, *files):
    def mut(x):
        x[tid] = [p for p in x[tid] if not any(f in p for f in files)]
    return mut


def put(tid, entry):
    def mut(x):
        x[tid] = entry
    return mut


def swap_ash_field(x):
    x["sc_no_rain"] = [SRC + "PyrelandsAshField.cs::ProbeCell" if "AshField.cs" in p else p for p in x["sc_no_rain"]]


# the four wrong entries of 2026-11-24, word for word, each with the C# that its entry left out
PLANTS = (
    ("one of two checks drops the burrow", "sc_ashwallow", drop("sc_ashwallow", "RM_JobDriver_Burrow.cs"),
     SRC + "RM_JobDriver_Burrow.cs"),
    ("the fruit check drops the fire tick and the ash field", "sc_scorchfruit",
     drop("sc_scorchfruit", "FireEcologyHook", "AshField"), SRC + "FireEcologyHook.cs"),
    ("the dust check says none", "sc_fire_dusts_ash", put("sc_fire_dusts_ash", ["none"]), SRC + "FireEcologyHook.cs"),
    ("the rain check swaps the ash field for an unrelated part of it", "sc_no_rain", swap_ash_field,
     SRC + "PyrelandsAshField.cs"),
)


def t_left_out_csharp_is_named():
    name = "left-out-csharp-is-named"
    for what, tid, mut, f in PLANTS:
        rel = pyre(FIX)
        mut(rel.extra)
        named, _ = DC.read(rel)
        ok("%s: %s" % (name, what), list(named) == [tid] and any(ln.startswith(f + "::") for ln in named[tid]), named)
    n, got, _ = DC.recall(pyre(TODAY))
    print("  recall: %d of %d single dropped C# paths are named (floor %d)" % (got, n, RECALL_FLOOR))
    ok(name + ": of every declared C# path dropped alone, at least %d are named" % RECALL_FLOOR, got >= RECALL_FLOOR, (got, n))
    for kind, entry, scene in (("type", "B", "t.call(type='P.Fire')"), ("method", "B", "t.call(method='ProbeHeat')"),
                               ("def", "B", "t.seen('RM_Ember')"), ("switch", "B", "t.set({'emberOn': False})"),
                               ("field", "B", "t.defs('BiomeDef/X', 'wildSkyTable')")):
        res, _ = planted(scene, [CS + "Other.cs"])
        ok("%s: kind %s alone names the file" % (name, kind), set(x.split(" ")[0] for x in res.values()) == {kind} and
           {f for f, _ in res} == {CS + "Fire.cs"}, res)


def t_true_declaration_is_not_named():
    name = "true-declaration-is-not-named"
    for sha in (TODAY, FIX):
        named, unseen = DC.read(pyre(sha))
        ok("%s: Pyrelands at %s, every entry" % (name, sha), named == {} and unseen == {}, (named, unseen))
    rel = pyre(TODAY)
    n = sum(1 for t in rel.tests if DC.live(rel.tests[t]) and DC.entry_of(rel, t))
    ok(name + ": the reading looked at 38 entries", n == 38, n)
    for scene, entry in (("t.call(type='P.Fire')", [CS + "Fire.cs::Fire"]), ("t.call(method='ProbeHeat')", [CS + "Fire.cs"]),
                         ("t.set({'emberOn': False})", [CS + "Fire.cs::Ember"]), ("t.seen('RM_Ember')", [CS]),
                         ("t.seen('RM_Ember')", ["*"]), ("t.seen('RM_Ember')", ["*", CS + "Other.cs"]),
                         ("t.call(method='ProbeTwice')", [CS + "Other.cs"]),
                         ("t.set({'emberOn': False})", [CS + "Fire.cs::Ember", CS + "Other.cs"]), ("t.seen('some RM_Ember in a message')", [CS + "Other.cs"])):
        res, _ = planted(scene, entry)
        ok("%s: %s with %s" % (name, scene, entry), res == {}, res)


def t_staging_names_nothing():
    name = "staging-names-nothing"
    res, _ = planted("t.seen('RM_Ember')", [CS + "Other.cs"], others=6)
    ok(name + ": a def that seven scenes of seven name says nothing of one of them", res == {}, res)
    res, _ = planted("t.seen('RM_Ember')", [CS + "Other.cs"], others=3)
    ok(name + ": one that four scenes name does", res != {}, res)
    res, _ = planted("t.seen(LIST)", [CS + "Other.cs"], head="LIST = ('RM_Ember', 'RM_A', 'RM_B')\n")
    ok(name + ": a constant of three names is a roster", res == {}, res)
    res, _ = planted("t.seen(ONE)", [CS + "Other.cs"], head="ONE = 'RM_Ember'\n")
    ok(name + ": a constant of one name is read", res != {}, res)
    res, _ = planted("common(t)", [CS + "Other.cs"], others=6, head="def common(t):\n    t.seen('RM_Ember')\n", mine="t.seen('RM_Ember')")
    ok(name + ": a name in a helper that every scene runs does not hide the scene that names it itself", res != {}, res)


def t_left_out_with_a_reason_is_not_named():
    name = "left-out-with-a-reason-is-not-named"
    for what, why, entry, want in (("the file", "drawn only", CS + "Fire.cs", True), ("the type", "drawn only", CS + "Fire.cs::Fire", True),
                                   ("an empty reason", " ", CS + "Fire.cs", False), ("another file", "why", CS + "Other.cs", False),
                                   ("another member", "why", CS + "Fire.cs::Nothing", False)):
        res, _ = planted("t.seen('RM_Ember')", [CS + "Other.cs"], left_out={entry: why})
        ok("%s: %s" % (name, what), (res == {}) is want, res)
    rel = pyre(FIX)
    rel.left_out_why["sc_ashwallow"] = {SRC + "RM_JobDriver_Burrow.cs::NoSuchType": "why"}
    drop("sc_ashwallow", "RM_JobDriver_Burrow.cs")(rel.extra)
    ok(name + ": a reason for another member does not cover the planted drop", "sc_ashwallow" in DC.read(rel)[0])


def t_named_check_reruns():
    name = "named-check-reruns"
    old = FIX + "^"
    rel = pyre(FIX)
    ok(name + ": true entries, the four checks are touched by the six fixes",
       all(rel.touches(t, old)[0] == "touched" for _, t, _, _ in PLANTS))
    for what, tid, mut, f in PLANTS:
        rel = pyre(FIX)
        mut(rel.extra)
        st, why, files = rel.touches(tid, old)
        want = "unreadable" if rel.extra[tid] == ["none"] else "touched"
        ok("%s: %s" % (name, what), st == want and f in files and "leaves out" in why, (st, why, files))
    rel = pyre(FIX)
    ok(name + ": a check that the six fixes do not touch, its entry true, keeps its row",
       rel.touches("sc_flamefang_venom", old)[0] == "untouched" and rel.touches("sc_firehawk", old)[0] == "untouched")
    for what, entry, edit, want in (
            ("a change in the type left out", [CS + "Other.cs"], ("Fire.cs", "return 1;", "return 2;"), "touched"),
            ("a change in another type of that file", [CS + "Other.cs"], ("Fire.cs", "return 9;", "return 8;"), "untouched"),
            ("a change in another file", [CS + "Other.cs"], ("Far.cs", "int far = 1", "int far = 2"), "untouched"),
            ("none, refuted, a change of any C# that ships", ["none"], ("Far.cs", "int far = 1", "int far = 2"), "unreadable"),
            ("none, and the scene names no C#", None, ("Far.cs", "int far = 1", "int far = 2"), "untouched")):
        scene = "t.seen('RM_Ember')" if entry else "t.seen('nothing')"
        _, st = planted(scene, entry or ["none"], edit=edit)
        ok("%s: %s" % (name, what), st == want, st)
    sw = "t.set({'emberOn': False})"
    _, st = planted(sw, [CS + "Other.cs"], edit=("Fire.cs", 'int Ember() { return Settings.emberOn ? Find("RM_Ember") : 0; }', ""))
    ok(name + ": the one member that was left out is deleted by the change", st == "touched", st)
    _, st = planted(sw, [CS + "Other.cs"], edit=("Fire.cs", "return 1;", "return 2;"))
    ok(name + ": a change in another member of the type that holds the left-out one", st == "touched", st)
    _, st = planted("t.seen('RM_Ember')", ["none", CS + "Other.cs"], edit=("Far.cs", "int far = 1", "int far = 2"))
    ok(name + ": none beside a C# path is no claim of no C#", st == "untouched", st)


def t_scene_check_off_reruns_nothing():
    name = "scene-check-off-reruns-nothing"
    e = ("Fire.cs", "return 1;", "return 2;")
    res, st = planted("t.seen('RM_Ember')", [CS + "Other.cs"], edit=e, off="off: not judged yet")
    ok(name + ": the check keeps its row, and is still named", st == "untouched" and res != {}, (st, res))
    _, st = planted("t.seen('RM_Ember')", [CS + "Other.cs"], edit=e, off="later")
    ok(name + ": a word that is not off: leaves it on", st == "touched", st)


def t_no_scene_found_is_could_not_look():
    name = "no-scene-found-is-could-not-look"
    res, _ = planted("t.seen('RM_Ember')", [CS + "Other.cs"], start="scene_that_is_nowhere", tid="sc_lost")
    ok(name + ": a check whose scene no Python of the mod holds is unseen, not clean", res is None, res)
    res, _ = planted("t.seen('RM_Ember')", [CS + "Other.cs"], start=None, tid="sc_file")
    ok(name + ": a check with no entry is read as its whole file", bool(res), res)
    for f, txt in ((CS + "Other.cs", "class Other { /* unclosed"), ("src/RimMandrake/Planted/Defs/E.xml", "<Defs><ThingDef>"),
                   ("src/RimMandrake/Planted/scene.py", "def run_sc_t(:")):
        res, _ = planted("t.seen('RM_Ember')", [CS + "Other.cs"], broken=(f, txt))
        ok("%s: %s does not read, so nothing is known, not clean" % (name, f.rsplit("/", 1)[1]), res is None, res)
    ok(name + ": a table with no C# list exits 2, and so does a commit git does not hold",
       DC.main(["--mod", "LeaningScrub", "--new", TODAY]) == 2 and DC.main(["--mod", "Pyrelands", "--new", "0" * 40]) == 2)


CS = "src/RimMandrake/Planted/Source/"
FIRE_CS = """namespace P {
class Fire {
    public static string ProbeHeat() { return "x"; }
    public int Tick() { return 1; }
    int Ember() { return Settings.emberOn ? Find("RM_Ember") : 0; }
    void Sky() { biome.wildSkyTable = null; }
}
class Ash { int Lay() { return 9; } public static string ProbeTwice() { return "a"; } }
class Soot { public static string ProbeTwice() { return "b"; } }
}
"""


def planted(scene, entry, others=0, head="", left_out=None, edit=None, off="", tid="sc_t", **kw):
    """One check `tid` of a throwaway mod, its scene `scene` and its C# list `entry`; `others` more checks run the same
    call. -> (what it leaves out, its state after `edit`)."""
    tr = T.Tree()
    try:
        ids = [tid] + ["sc_o%d" % i for i in range(others)]
        tests = {t: {"id": t, "kind": "live_minimal", "stage": "6", "tier": "t", "file": "src/RimMandrake/Planted/scene.py",
                     "entry": kw["start"] if "start" in kw and t == tid else "run_" + t} for t in ids}
        if tests[tid]["entry"] is None:
            del tests[tid]["entry"]
        tr.write("src/RimMandrake/Planted/scene.py", head + "\n".join("def run_%s(t):\n    %s\n%s" % (
            "t_here" if t == tid and "start" in kw else t, scene, "    %s\n" % kw["mine"] if t == tid and "mine" in kw else "")
            for t in ids))
        for f, txt in (("Fire.cs", FIRE_CS), ("Other.cs", "class Other { int o = 1; }\n"), ("Far.cs", "class Far { int far = 1; }\n"),
                       ("Settings.cs", "class Settings { public static bool emberOn = true; void Draw() { Settings.emberOn = true; } }\n")):
            tr.write(CS + f, txt)
        tr.write("src/RimMandrake/Planted/Defs/E.xml",
                 "<Defs><ThingDef><defName>RM_Ember</defName><thingClass>P.Fire</thingClass></ThingDef></Defs>\n")
        tr.write("src/RimMandrake/Planted/Assemblies/P.dll.srchash",
                 "# dll: 0\n00 Fire.cs\n00 Other.cs\n00 Far.cs\n00 Settings.cs\n")
        tr.write("design/concepts/Planted/version/test_table.json", json.dumps({"tests": tests}))
        tr.write("design/concepts/Planted/version/exercises.json", json.dumps({
            "checks": {t: entry for t in ids}, "left_out": {tid: left_out or {}}, "scene_check": off}))
        if "broken" in kw:
            tr.write(*kw["broken"])
        base = tr.commit("planted")
        if edit:
            tr.edit(CS + edit[0], edit[1], edit[2])
            tr.commit("the change")
        rel = RR.Relation(tr.root, "Planted", tests)
        return DC.Evidence(rel).left_out(tid), rel.touches(tid, base)[0] if edit else None
    finally:
        tr.close()


def _mutate(kind):
    if kind == "blind":
        DC.Evidence.wanted = lambda self, tid, sha, files=None: []
    elif kind == "naming":
        DC.Evidence.held = lambda self, tid, sha, o=None: lambda f, k: False
    elif kind == "no_rerun":
        RR.Relation._left_out_touched = lambda *a: None
    else:
        raise SystemExit("unknown mutation %s" % kind)


def main():
    if "--mutate" in sys.argv:
        _mutate(sys.argv[sys.argv.index("--mutate") + 1])
    t_left_out_csharp_is_named()
    t_true_declaration_is_not_named()
    t_staging_names_nothing()
    t_left_out_with_a_reason_is_not_named()
    t_named_check_reruns()
    t_scene_check_off_reruns_nothing()
    t_no_scene_found_is_could_not_look()
    print("selftest_declaration_check: %d of %d failed" % (len(FAILS), len(SEEN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
