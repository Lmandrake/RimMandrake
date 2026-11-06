"""Offline selftest for suite_set.py (SUITE_REGISTRY_WIDEN_FORTY_SEVEN_STRAYS). Every pass case has a failing twin."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import suite_set as S   # noqa: E402

FAILS = []


def check(name, ok):
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    MIN, OURS = {"brrainz.harmony", "mandrake.rm.jawabench"}, {"mandrake.rm.aftermath", "mandrake.rut.rites"}
    # classify: the three rules and their twins
    check("a `list: full` walk doc is OUT", not S.classify("X", "full     # needs donors", [], MIN, OURS)[0])
    check("`list: full Utinni list` is OUT", not S.classify("X", "full Utinni list", [], MIN, OURS)[0])
    check("`list: minimal+full...` is not mistaken for full", S.classify("X", "minimal (x) | full needed", [], MIN, OURS)[0])
    check("a word starting with full is not `full`", S.classify("X", "fullerene", [], MIN, OURS)[0])
    check("Ludeon + minimal + our own closure is IN",
          S.classify("X", "minimal+mandrake.rm.aftermath", ["ludeon.rimworld.biotech", "brrainz.harmony",
                                                             "mandrake.rm.aftermath", "mandrake.rut.rites"], MIN, OURS)[0])
    ok, why = S.classify("X", "minimal+speakup", ["jpt.speakup", "mandrake.rm.aftermath"], MIN, OURS)
    check("a donor in the closure is OUT and named", not ok and "jpt.speakup" in why)
    check("no walk doc and a clean closure is IN", S.classify("X", None, ["mandrake.rut.rites"], MIN, OURS)[0])
    check("an unreadable closure stays IN (the pass reports it)", S.classify("X", None, RuntimeError("no About"), MIN, OURS)[0])
    check("`list: full` beats an unreadable closure", not S.classify("X", "full", RuntimeError("x"), MIN, OURS)[0])
    # transitive: a donor two levels down (SithLine -> Armoury -> ebsg) is seen; cycles and compose targets end cleanly
    deps = {"Sith": ["rsw.armoury", "rsw.sith"], "Armoury": ["ebsg.framework", "rsw.armoury"],
            "A": ["rm.b", "rm.a"], "B": ["rm.a", "rm.b"], "Leaf": ["rm.biomes", "rm.leaf"]}

    def direct(n):
        if n not in deps:
            raise RuntimeError("no closure for %s" % n)
        return deps[n]
    ours = {"rsw.armoury": "Armoury", "rsw.sith": "Sith", "rm.a": "A", "rm.b": "B", "rm.biomes": "RimMandrake.Biomes",
            "rm.leaf": "Leaf"}
    t = S.transitive("Sith", direct, ours)
    check("transitive reaches a donor two levels down, deps first", t == ["ebsg.framework", "rsw.armoury", "rsw.sith"])
    check("one level (the old read) would have missed it", "ebsg.framework" not in deps["Sith"])
    ok, why = S.classify("Sith", "minimal+armoury", t, MIN, set(ours))
    check("the transitive donor makes the suite OUT", not ok and "ebsg.framework" in why)
    check("a dependency cycle ends", sorted(S.transitive("A", direct, ours)) == ["rm.a", "rm.b"])
    deps["RimMandrake.Biomes"] = ["donor.x", "rm.biomes"]     # what direct_fn returns for the target: its sources' union
    check("a dependency on the composed target follows the folded sources' donors",
          S.transitive("Leaf", direct, ours) == ["donor.x", "rm.biomes", "rm.leaf"])
    try:
        S.transitive("Missing", direct, ours)
        check("the suite's own unreadable closure raises (classify keeps it IN)", False)
    except RuntimeError:
        check("the suite's own unreadable closure raises (classify keeps it IN)", True)
    # disk_suites / walk_list / minimal_ids over a fake tree
    with tempfile.TemporaryDirectory() as t:
        for tier, mod, body in (("RimMandrake", "Alpha", "suite = Suite('a')\n"), ("RimUtinni", "Beta", "x=1\nsuite=S()\n"),
                                ("RimMandrake", "Script", "def main(): pass\n"), ("RimStarWars", "Gamma", "  suite = 1\n")):
            write(os.path.join(t, "src", tier, mod, "validation.py"), body)
        check("disk_suites finds module-level suites in every tier and nothing else",
              S.disk_suites(t) == {"Alpha": "RimMandrake", "Beta": "RimUtinni"})
        write(os.path.join(t, "design", "validation_walks", "RimMandrake", "Alpha.md"),
              "# Alpha\n\nlist: full   # donors\n\nlist: minimal\n")
        write(os.path.join(t, "design", "validation_walks", "RimStarWars", "Beta.md"), "# Beta\nlist: minimal+traces\n")
        write(os.path.join(t, "design", "validation_walks", "RimUtinni", "Gamma.md"), "# Gamma\n  - minimal list: body\n")
        check("walk_list reads the FIRST header line", S.walk_list("Alpha", "RimMandrake", t) == "full   # donors")
        check("walk_list finds a walk doc left in its old tier", S.walk_list("Beta", "RimUtinni", t) == "minimal+traces")
        check("walk_list ignores an indented body line", S.walk_list("Gamma", "RimUtinni", t) is None)
        check("walk_list of no walk doc is None", S.walk_list("Nope", "RimMandrake", t) is None)
        write(os.path.join(t, S.MINIMAL_REL),
              "<ModsConfigData><activeMods><li>Ludeon.RimWorld</li><li> brrainz.harmony </li></activeMods></ModsConfigData>")
        check("minimal_ids parses and lower-cases activeMods", S.minimal_ids(t) == {"ludeon.rimworld", "brrainz.harmony"})
    # the real tree: the set is the derived one, and the instrument can see
    import jobs
    import rollout_gate
    rows = S.table()
    ins = [r[0] for r in rows if r[2]]
    out = {r[0] for r in rows if not r[2]}
    check("the real tree has suites both IN and OUT (instrument sees)", len(ins) > 20 and len(out) >= 1)
    check("jobs.suite_mods() is the derived set", jobs.suite_mods() == ins)
    check("rollout_gate owes exactly the derived set", rollout_gate.disk_suites() == set(ins))
    check("a former stray with an own-mod closure is IN (AftermathRites)", "AftermathRites" in ins)
    check("a `list: full` patch layer is OUT (UtinniPatches)", "UtinniPatches" in out)
    check("a suite whose own dependency needs donors is OUT (SithLine -> Armoury)", "SithLine" in out)
    cl = S.closure("HostileFlora")
    check("a suite needing the composed Biomes mod carries the folded mods' deps (flowworks)",
          "mandrake.rm.biomes" in cl and "mandrake.rm.flowworks" in cl and cl.index("mandrake.rm.flowworks") < cl.index("mandrake.rm.biomes"))
    check("every disk suite is classified once", sorted(r[0] for r in rows) == sorted(S.disk_suites()))
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
