"""selftest_rustcathedral_borehulk.py -- validation.borehulk_problems is clean on the shipped mod and reddens on each
break it exists to catch, planted in a temp copy of Defs/Patches/Source (never the shipped files).
RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1, L0."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _sub(path, old, new):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    assert old in text, (path, old)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new, 1))


def main():
    spec = importlib.util.spec_from_file_location("rc_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    bad, unmeasured = v.borehulk_problems()
    check("shipped: borehulk clean", bad == [], bad)
    print("     (unmeasured on this machine: %s)" % (unmeasured or "none"))

    def planted(label, rel, old, new, expect, src_root=None, vanilla=None):
        tmp = tempfile.mkdtemp()
        try:
            for d in ("Defs", "Patches", "Source"):
                shutil.copytree(os.path.join(HERE, d), os.path.join(tmp, d),
                                ignore=shutil.ignore_patterns("obj", "bin", "__pycache__"))
            if rel:
                _sub(os.path.join(tmp, rel), old, new)
            got, _u = v.borehulk_problems(mod_root=tmp, src_root=src_root or v.SRC_ROOT,
                                          vanilla_data=vanilla if vanilla is not None else v.VANILLA_DATA)
            check(label, any(expect in g for g in got), got)
        finally:
            shutil.rmtree(tmp)

    races = os.path.join("Defs", "ThingDefs_Races", "RM_Borehulk.xml")
    tree = os.path.join("Defs", "ThinkTreeDefs", "RM_ThinkTree_Borehulk.xml")
    planted("missing SoundDef reddens", os.path.join("Defs", "SoundDefs", "RM_BorehulkSounds.xml"),
            "<defName>RM_BorehulkGrind</defName>", "<defName>RM_BorehulkGrindX</defName>", "SoundDef/RM_BorehulkGrind")
    planted("small body reddens", races, "<baseBodySize>6</baseBodySize>", "<baseBodySize>2</baseBodySize>", "baseBodySize")
    planted("retaliation reddens", races, "<manhunterOnDamageChance>0</manhunterOnDamageChance>",
            "<manhunterOnDamageChance>0.5</manhunterOnDamageChance>", "manhunterOnDamageChance")
    planted("fight node reddens", tree, '<li Class="ThinkNode_QueuedJob" />',
            '<li Class="ThinkNode_QueuedJob" /><li Class="JobGiver_AIFightEnemies" />', "fight branch")
    planted("lost back-away reddens", tree, 'Class="RimMandrake.RustCathedral.RM_JobGiver_BorehulkBackAway"',
            'Class="RimMandrake.RustCathedral.RM_JobGiver_SomethingElse"', "BorehulkBackAway")
    planted("ungated genstep reddens", os.path.join("Source", "RustCathedral", "RM_GenStep_BorehulkPlacement.cs"),
            "map.Biome.defName != CathedralBiomeDefName", "false", "self-gates")
    planted("unpatched genstep reddens", os.path.join("Patches", "RM_Borehulk_MapGenPatch.xml"),
            "<li>RM_BorehulkPlacement</li>", "<li>RM_SomethingElse</li>", "MapCommonBase")
    if os.path.isdir(v.VANILLA_DATA):
        planted("thin armour reddens", races, "<ArmorRating_Sharp>1.40</ArmorRating_Sharp>",
                "<ArmorRating_Sharp>0.50</ArmorRating_Sharp>", "ArmorRating_Sharp")
    else:
        print("     (armour plant skipped: no vanilla install here)")
    # roster ban: a temp src root holding a BiomeDef that rosters both the probe and the borehulk
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "b.xml"), "w", encoding="utf-8") as fh:
            fh.write("<Defs><BiomeDef><defName>X</defName><wildAnimals><RM_CathedralRoach>1</RM_CathedralRoach>"
                     "<RM_Borehulk>0.1</RM_Borehulk></wildAnimals></BiomeDef></Defs>")
        got, _u = v.borehulk_problems(src_root=tmp)
        check("rostered borehulk reddens", any("rostered" in g for g in got), got)
        os.remove(os.path.join(tmp, "b.xml"))
        got, u = v.borehulk_problems(src_root=tmp)
        check("empty src root says UNMEASURED, not clean", any("probe" in x for x in u), u)
    finally:
        shutil.rmtree(tmp)
    check("vanilla unreachable says UNMEASURED", any("vanilla" in x for x in
                                                      v.borehulk_problems(vanilla_data="/nonexistent")[1]))
    print("%s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
