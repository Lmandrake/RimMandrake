#!/usr/bin/env python3
"""selftest_shipped_defs.py -- offline proof for modcheck/shipped_defs.py (the every-shipped-def readback chain).

Run bare: python3 src/RimMandrake/Utils/modcheck/selftest_shipped_defs.py   (exit 0 = clean)

A synthetic mod (abstract parent, three defs of two types, a nested element, a bool) is read back through a mock
`jawa/get_defs` that serves the XML's own values. Clean must be green; each break reddens exactly the component
that owns it. Then every real mod wired to the helper is parsed, and must find its own sanity names.
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(UTILS, "..", "..", ".."))
for p in (UTILS, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
from modcheck import Suite, shipped_defs                       # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
XML = """<Defs>
  <ThingDef Name="ParentX" Abstract="True"><defName>AbstractNeverRead</defName><label>no</label></ThingDef>
  <ThingDef ParentName="ParentX"><defName>T_One</defName><label>one</label><statBases><Mass>2</Mass></statBases></ThingDef>
  <ThingDef><defName>T_Two</defName><label>two</label><stackLimit>75</stackLimit></ThingDef>
  <RecipeDef><defName>R_Make</defName><label>make one</label><workAmount>800</workAmount><allowMixingIngredients>true</allowMixingIngredients></RecipeDef>
  <ThingDef MayRequire="Other.Mod"><defName>G_A</defName><label>guarded a</label></ThingDef>
  <ThingDef MayRequire="other.mod"><defName>G_B</defName><label>guarded b</label></ThingDef>
  <ThingDef MayRequire="Ludeon.RimWorld.Royalty"><defName>G_Dlc</defName><label>dlc thing</label></ThingDef>
</Defs>"""

# real mods wired to the helper: (mod folder under src, sanity names, min_count)
WIRED = [
    ("RimStarWars/Cuisine", ("RSW_SaltCuredRation_White", "RSW_CureWithAmberSalt", "RSW_AteCrystalSaltCured"), 30),
    ("RimUtinni/Antiquities", ("RUT_AntiquityCipherBench",), 8),
    ("RimUtinni/Rites", ("RUT_Rites", "RUT_Rites_GodsSpeakBack"), 6),
    ("RimMandrake/SacredGraffiti", ("RM_Ishko_RitualOutcome_PlaceSacredMark", "RM_ViewedSacredMark_Ishko"), 5),
    ("RimUtinni/UtinniStatues", ("RUT_StatueGrand_Shkaar",), 4),
    ("RimUtinni/ScarlandsLadder", ("RUT_PilgrimCamps", "RUT_ScarlandsLadder", "RUT_PilgrimJournal"), 3),
    ("RimMandrake/Scarlands", ("RM_Warscar", "RM_OldLineTurret", "RM_Chatrak"), 90),
    ("RimStarWars/StarWarsRaces", ("RSW_RimMandrakeJawa", "RSW_MandrakeJawa", "Head_Bone"), 500),
    ("RimUtinni/ResearchRetag", ("RR_LateralThinking", "GravForge"), 40),
    ("RimUtinni/PawnFlavor", ("RUT_Jawa_CisternHatched", "RUT_Jawa_WaterWarden"), 85),
    ("RimMandrake/CreatureBehaviors", ("RM_PincerCrush", "RM_Mirage"), 35),
    ("RimMandrake/DivingInteraction", ("RM_SeaFloorTerrain", "RM_ProbeGalleryOutlet"), 50),
    ("RimMandrake/RimProperty", ("RM_AnimalSteal",), 5),
    ("RimMandrake/Pyrinth", ("DV_PyrinthHeater", "DV_Mote_PyrinthSpark"), 12),
    ("RimStarWars/StarWarsPatches", ("Heron_ResearchTab", "ProjectHeron_Swdoors"), 30),
]


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def make_ext(brk, mod_dir):
    parsed = dict((n, leaf) for _t, n, leaf in shipped_defs.parse(mod_dir))

    def ext(game, tool, p):
        if tool != "jawa/get_defs":
            return None
        want = [s.split("/", 1)[1] for s in str(p.get("defs") or "").split(";") if "/" in s]
        fields = [f for f in str(p.get("fields") or "").split(",") if f]
        rows, missing = [], []
        for n in want:
            if n not in parsed or ("missing" in brk and n == "T_Two") or ("guard_off" in brk and n in ("G_A", "G_B")) \
                    or ("guard_partial" in brk and n == "G_B") or ("dlc_missing" in brk and n == "G_Dlc"):
                missing.append(n)
                continue
            vals = dict((f, parsed[n].get(f)) for f in fields if f in parsed[n])
            if "drift" in brk and n == "R_Make" and "workAmount" in vals:
                vals["workAmount"] = "1"
            if "label_shadow" in brk and n == "T_One":
                vals["label"] = "someone else's one"
            if "allowMixingIngredients" in vals:
                vals["allowMixingIngredients"] = "True"        # live bools print capitalised
            if "workAmount" in vals:
                vals["workAmount"] = "800.0" if "drift" not in brk else vals["workAmount"]
            rows.append({"defName": n, "fields": vals})
        found = len(rows) + (1 if "count_lies" in brk else 0)
        if "tool_fails" in brk:
            return {"success": False, "message": "InvalidCastException"}
        return {"success": True, "foundCount": found, "notFound": missing, "defs": rows}
    return ext


def run(brk=(), fields_by_type=None, sanity=("T_One",), min_count=3, skip=()):
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "Defs", "Misc"))
        with open(os.path.join(tmp, "Defs", "Misc", "a.xml"), "w") as fh:
            fh.write(XML)
        val = os.path.join(tmp, "validation.py")
        suite = Suite("Synthetic")
        shipped_defs.add_chain(suite, val, fields_by_type=fields_by_type, sanity=sanity, min_count=min_count,
                               skip=skip)
        game = MockGame()
        game.ext = make_ext(set(brk), tmp)
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = {}
    for ch in res["chains"]:
        for c in ch["components"]:
            out[c["name"]] = (c["verdict"], c.get("detail") or "")
    return out


def reds(r):
    return sorted(k for k, (v, _d) in r.items() if v == "FAIL")


def _components(res):
    out = {}
    for ch in res["chains"]:
        for c in ch["components"]:
            out[c["name"]] = (c["verdict"], c.get("detail") or "")
    return out


def run_real(rel, brk=()):
    """Import the wired mod's own validation.py, take the chain it registered, and run it against a mock serving
    that mod's own XML. Clean must be green (its fields_by_type really compares something); 'missing' drops one def
    from the game and must redden the loaded component; 'drift' changes every served value and must redden the
    fields component. None = the validation.py registers no such chain."""
    import importlib.util
    mod_dir = os.path.join(ROOT, "src", rel)
    spec = importlib.util.spec_from_file_location("v_" + rel.replace("/", "_"), os.path.join(mod_dir, "validation.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    fns = [fn for n, fn in (m.suite.chains if getattr(m, "suite", None) else []) if n == "every_shipped_def_reads_back"]
    if len(fns) != 1:
        return None
    # keyed by "Type/name": names collide across types (Warscar's RM_Chotrix is a ThingDef AND a PawnKindDef)
    parsed = dict(("%s/%s" % (t, n), leaf) for t, n, leaf in shipped_defs.parse(mod_dir))
    guarded = shipped_defs.guards(mod_dir)
    plain = sorted(k for k in parsed if tuple(k.split("/", 1)) not in guarded)
    drop = set(plain[:1]) if "missing" in brk else set()
    if "guard_off" in brk:     # every def under one guard missing = that mod inactive: must stay green
        g0 = sorted(set(guarded.values()))[0]
        drop = set("%s/%s" % k for k, g in guarded.items() if g == g0)

    def ext(game, tool, p):
        if tool != "jawa/get_defs":
            return None
        want = [x for x in str(p.get("defs") or "").split(";") if "/" in x]
        fields = [x for x in str(p.get("fields") or "").split(",") if x]
        rows = []
        for spec in want:
            if spec in parsed and spec not in drop:
                vals = dict((f, parsed[spec][f]) for f in fields if f in parsed[spec])
                if "drift" in brk:
                    vals = dict((f, v if f == "defName" else "drifted-" + v) for f, v in vals.items())
                rows.append({"defName": spec.split("/", 1)[1], "fields": vals})
        return {"success": True, "foundCount": len(rows), "notFound": [x.split("/", 1)[1] for x in want if x in drop],
                "defs": rows}

    suite = Suite("Real_" + rel.replace("/", "_"))
    suite.chain("every_shipped_def_reads_back")(fns[0])
    game = MockGame()
    game.ext = ext
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return _components(res)


LOADED, FIELDS = "every_shipped_def_is_loaded", "shipped_scalar_fields_match_xml"


def main():
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "Defs"))
        with open(os.path.join(tmp, "Defs", "a.xml"), "w") as fh:
            fh.write(XML)
        got = shipped_defs.parse(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("parse skips the abstract def and keeps the rest", [n for _t, n, _l in got] == ["T_One", "T_Two", "R_Make", "G_A", "G_B", "G_Dlc"], got)
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "Defs"))
        with open(os.path.join(tmp, "Defs", "a.xml"), "w") as fh:
            fh.write(XML)
        gd = shipped_defs.guards(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("guards(): MayRequire case-folded, a DLC-only guard is not a guard",
          gd == {("ThingDef", "G_A"): "other.mod", ("ThingDef", "G_B"): "other.mod"}, gd)
    check("parse keeps leaves only (no statBases block)", "statBases" not in got[0][2], got[0][2])
    check("same_value: 800 == 800.0, true == True, 'a' != 'b'",
          shipped_defs.same_value("800", "800.0") and shipped_defs.same_value("true", "True")
          and not shipped_defs.same_value("a", "b") and not shipped_defs.same_value("1", None))

    rec = {"RecipeDef": ("label", "workAmount", "allowMixingIngredients")}
    clean = run(fields_by_type=rec)
    check("clean run: both components PASS", all(v == "PASS" for v, _d in clean.values()) and len(clean) == 2, clean)
    cases = [
        (("missing",), {}, [LOADED]),
        (("drift",), {}, [FIELDS]),
        (("label_shadow",), {}, [FIELDS]),
        (("count_lies",), {}, [LOADED]),
        (("tool_fails",), {}, [LOADED]),
    ]
    for brk, _kw, want in cases:
        res = run(brk, fields_by_type=rec)
        got = reds(res)
        check("break %-13s reddens exactly %s" % (brk[0], want), got == sorted(want), "got %s" % got)
        check("break %-13s leaves no component PASSing on a lying tool" % brk[0],
              brk[0] not in ("count_lies", "tool_fails") or all(v != "PASS" for v, _d in res.values()), res)
    off = run(("guard_off",), fields_by_type=rec)
    check("a guard whose mod is inactive (all its defs absent) stays green", reds(off) == [], off)
    part = reds(run(("guard_partial",), fields_by_type=rec))
    check("a guarded def lost while its guard sibling loaded reddens the loaded component", part == [LOADED], part)
    dlc = reds(run(("dlc_missing",), fields_by_type=rec))
    check("a DLC-guarded def missing is a real loss (every DLC is assumed present)", dlc == [LOADED], dlc)
    blind = reds(run(sanity=("NotThere",), fields_by_type=rec))
    check("a sanity name the parse cannot see reddens the loaded component", blind == [LOADED], blind)
    small = reds(run(min_count=10, fields_by_type=rec))
    check("fewer defs than min_count reddens the loaded component", small == [LOADED], small)
    nothing = reds(run(fields_by_type={"ThingDef": ("nonexistentField",), "RecipeDef": ("nonexistentField",)}))
    check("a readback that compares nothing is red, not vacuously green", nothing == [FIELDS], nothing)
    skipped = reds(run(("drift",), fields_by_type=rec, skip=("R_Make.workAmount",)))
    check("skip names a deliberately patched field and clears only it", skipped == [], skipped)

    for rel, sanity, min_count in WIRED:
        mod = os.path.join(ROOT, "src", rel)
        names = [n for _t, n, _l in shipped_defs.parse(mod)]
        check("wired %s: parse finds %d >= %d defs and its sanity names" % (rel, len(names), min_count),
              len(names) >= min_count and all(s in names for s in sanity), (len(names), [s for s in sanity if s not in names]))
        clean = run_real(rel)
        check("wired %s: its validation.py registers the chain and it is green on its own XML" % rel,
              clean is not None and all(v == "PASS" for v, _d in clean.values()) and len(clean) == 2, clean)
        if clean is not None:
            check("wired %s: a def the game lacks reddens exactly the loaded component" % rel,
                  reds(run_real(rel, ("missing",))) == [LOADED], reds(run_real(rel, ("missing",))))
            check("wired %s: drifted values redden exactly the fields component" % rel,
                  reds(run_real(rel, ("drift",))) == [FIELDS], reds(run_real(rel, ("drift",))))
            if shipped_defs.guards(mod):
                off = run_real(rel, ("guard_off",))
                check("wired %s: one MayRequire mod inactive (its whole guard group absent) stays green" % rel,
                      reds(off) == [] and all(v == "PASS" for v, _d in off.values()), off)

    if FAILS:
        print("\n%d shipped_defs selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall shipped_defs selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
