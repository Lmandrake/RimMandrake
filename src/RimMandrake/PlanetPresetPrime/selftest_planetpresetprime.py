#!/usr/bin/env python3
"""selftest_planetpresetprime.py -- PLANETPRESETPRIME_COVERAGE_GAPS_1 offline half: signatures_static is green against the mod
source, the decompiled engine and My Little Planet's source, and goes red on every planted rename/shape change (in-memory text
edits; nothing on disk is written). python3 src/RimMandrake/PlanetPresetPrime/selftest_planetpresetprime.py"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    spec = importlib.util.spec_from_file_location("ppp_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    mlp = v.mlp_source_dir()
    eng = os.path.join(v.DECOMPILED, "RimWorld")
    if mlp is None or not os.path.isfile(os.path.join(eng, "Page_CreateWorldParams.cs")):
        print("UNMEASURED  decompiled engine tree or MLP source not reachable")
        return 2
    cs = v._rd(v._HERE, "Source", "PlanetPresetPrime.cs")
    page, layer = v._rd(eng, "Page_CreateWorldParams.cs"), v._rd(eng, "PlanetLayerSettings.cs")
    defs, defof = v._rd(eng, "PlanetLayerSettingsDef.cs"), v._rd(eng, "PlanetLayerSettingsDefOf.cs")
    tile = v._rd(mlp, "MyLittlePlanet", "TileSize.cs")
    check("sanity probe: all five sources read and non-trivial", all(len(x) > 100 for x in (cs, page, layer, defs, defof, tile)), [len(x) for x in (cs, page, layer, defs, defof, tile)])
    check("shipped mod source: clean", v.mod_findings(cs) == [], v.mod_findings(cs))
    check("shipped engine tree: clean", v.engine_findings(page, layer, defs, defof, 1.0, 7) == [], v.engine_findings(page, layer, defs, defof, 1.0, 7))
    check("shipped MLP source: clean", v.mlp_findings(tile, 7) == [], v.mlp_findings(tile, 7))

    def brk(tag, text, old, new, finder, must, *extra):
        assert old in text, "planted break target missing: %r" % old       # a break that matches nothing proves nothing
        got = finder(text.replace(old, new, 1), *extra)
        check("break %-52s -> %s" % (tag, must[:28]), any(must in g for g in got), got)

    brk("coverage primed to 0.5", cs, "Coverage    = 1.0f", "Coverage    = 0.5f", v.mod_findings, "coverage 1.0")
    brk("subdivisions primed to 10", cs, "Subdivisions = 7;", "Subdivisions = 10;", v.mod_findings, "subdivisions 7")
    brk("patch retargeted to PreOpen", cs, '"Reset")]', '"PreOpen")]', v.mod_findings, "postfix on Page_CreateWorldParams.Reset")
    brk("field name guessed wrong", cs, '"planetCoverage")', '"coverage")', v.mod_findings, "planetCoverage")
    got = v.mod_findings(cs.replace('TypeByName("WorldGenRules.WorldGenRules")', 'TypeByName("WorldGenRules.Rules")'))
    check("break MLP type name drifts (both uses) -> TypeByName", any("TypeByName" in g for g in got), got)
    brk("boot line removed", cs, "loaded: will prime coverage", "loaded", v.mod_findings, "boot line")
    brk("vanilla set before MLP", cs, "f.SetValue(null, n);", "", v.mod_findings, "BEFORE")
    for tag, old, new, must in (("Reset renamed in the engine", "public void Reset()", "public void ResetAll()", "Reset is gone"),
                                ("Reset gains a parameter", "public void Reset()", "public void Reset(bool all)", "Reset is gone"),
                                ("planetCoverage becomes public", "private float planetCoverage;", "public float planetCoverage;", "no longer a private float"),
                                ("planetCoverage field renamed", "planetCoverage;", "coverage;", "no longer a private float"),
                                ("1.0 leaves the legal coverages", "{ 0.3f, 0.5f, 1f }", "{ 0.3f, 0.5f, 0.8f }", "legal PlanetCoverages"),
                                ("once-only guard removed", "if (!initialized)", "if (true)", "initialized"),
                                ("Reset stops assigning coverage", "planetCoverage = ((Prefs.DevMode", "var _x = ((Prefs.DevMode", "no longer assigns planetCoverage")):
        brk(tag, page, old, new, lambda t_: v.engine_findings(t_, layer, defs, defof, 1.0, 7), must)
    brk("subdivisions becomes a property", layer, "public int subdivisions = 10;", "public int subdivisions { get; set; }", lambda t_: v.engine_findings(page, t_, defs, defof, 1.0, 7), "subdivisions")
    brk("settings field renamed", defs, "public PlanetLayerSettings settings;", "public PlanetLayerSettings layerSettings;", lambda t_: v.engine_findings(page, layer, t_, defof, 1.0, 7), "settings")
    brk("Surface DefOf removed", defof, "public static PlanetLayerSettingsDef Surface;", "", lambda t_: v.engine_findings(page, layer, defs, t_, 1.0, 7), "Surface")
    brk("MLP subcount made private", tile, "public static int subcount", "private static int subcount", v.mlp_findings, "subcount", 7)
    brk("MLP slider no longer reaches 7", tile, "subcount, 6f, 10f", "subcount, 8f, 10f", v.mlp_findings, "outside MLP's slider", 7)
    brk("MLP class renamed", tile, "class WorldGenRules", "class WorldRules", v.mlp_findings, "class WorldGenRules", 7)
    brk("MLP stops copying subcount to the engine", tile, "Surface.settings.subdivisions = subcount", "var q = subcount", v.mlp_findings, "no longer copies", 7)

    import runner
    from northstar_driver.session import FastSession
    from northstar_driver.transport import MockGame, MockTransport

    def chain(patch=None):
        saved = {}
        for k, fn in (patch or {}).items():
            saved[k] = getattr(v, k)
            setattr(v, k, fn)
        try:
            own = v.Suite("PlanetPresetPrime")
            own.toggles = []
            own.chains = [(n, f) for n, f in v.suite.chains if n == "signatures_static"]
            with FastSession(transport=MockTransport(MockGame()), strict=False) as s:
                res = runner.run_suite(own, s, anchor=None, mod=None)
        finally:
            for k, fn in saved.items():
                setattr(v, k, fn)
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
    got = chain()
    check("chain PASSes on the shipped trees", list(got.values()) == ["PASS"], got)
    real = v._rd
    got = chain({"_rd": lambda *p: real(*p).replace("public void Reset()", "public void ResetAll()") if p[-1] == "Page_CreateWorldParams.cs" else real(*p)})
    check("chain reddens when the engine renames Reset", list(got.values()) == ["FAIL"], got)
    got = chain({"mlp_source_dir": lambda: None})
    check("chain is UNMEASURED (never PASS) when the MLP source is unreachable", list(got.values()) != ["PASS"], got)

    if FAILS:
        print("\n%d PlanetPresetPrime selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall PlanetPresetPrime selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
