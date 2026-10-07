"""selftest_rustcathedral_basefinish.py -- validation.basefinish_problems is clean on the shipped mod and reddens on each
break it exists to catch, planted in a temp copy of Defs/Patches/Source and of the campaign patch folder (never the
shipped files). RUSTCATHEDRAL_BASE_FINISH_BUILD_1, L0."""
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
    bad, unmeasured = v.basefinish_problems()
    check("shipped: base finish clean", bad == [], bad)
    check("shipped: mynock patch measured", unmeasured == [], unmeasured)

    def planted(label, rel, old, new, expect, in_utinni=False, remove=None):
        tmp = tempfile.mkdtemp()
        try:
            for d in ("Defs", "Patches", "Source"):
                shutil.copytree(os.path.join(HERE, d), os.path.join(tmp, d),
                                ignore=shutil.ignore_patterns("obj", "bin", "__pycache__"))
            up = os.path.join(tmp, "utinni")
            shutil.copytree(v.UTINNI_PATCHES, up)
            root = up if in_utinni else tmp
            if remove:
                os.remove(os.path.join(root, remove))
            if rel:
                _sub(os.path.join(root, rel), old, new)
            got, _u = v.basefinish_problems(mod_root=tmp, utinni_patches=up)
            check(label, any(expect in g for g in got), got)
        finally:
            shutil.rmtree(tmp)

    j = os.path.join
    planted("incident as a threat", j("Defs", "IncidentDefs", "RM_LineCycle.xml"),
            "<category>Misc</category>", "<category>ThreatBig</category>", "category is not Misc")
    planted("storyteller can pick it", j("Defs", "IncidentDefs", "RM_LineCycle.xml"),
            "<baseChance>0</baseChance>", "<baseChance>1</baseChance>", "baseChance is not 0")
    planted("trait rolls at generation", j("Defs", "TraitDefs", "RM_HumReader.xml"),
            "<commonality>0</commonality>", "<commonality>1</commonality>", "commonality is not 0")
    planted("trait grows a stat", j("Defs", "TraitDefs", "RM_HumReader.xml"),
            "</description>", "</description><statOffsets><ShootingAccuracyPawn>1</ShootingAccuracyPawn></statOffsets>",
            "carries a stat")
    planted("recipe ungated", j("Defs", "RecipeDefs", "RM_WriteHumPrimer.xml"),
            "<trait>RM_HumReader</trait>", "<trait>Nimble</trait>", "not gated on RM_HumReader")
    planted("eel tameable", j("Defs", "ThingDefs_Races", "RM_CoolantEel.xml"),
            "<trainability>None</trainability>", "<trainability>Simple</trainability>", "trainability is not None")
    planted("eel loses the backstop", j("Defs", "ThingDefs_Races", "RM_CoolantEel.xml"),
            "CompProperties_WaterLocked", "CompProperties_Nothing", "lost the RM_CompWaterLocked backstop")
    planted("eel in wildAnimals", j("Defs", "BiomeDefs", "RM_RustCathedral_Biome.xml"),
            "<RM_LivingBolt>0.06</RM_LivingBolt>", "<RM_LivingBolt>0.06</RM_LivingBolt><RM_CoolantEel>0.1</RM_CoolantEel>",
            "is in wildAnimals")
    planted("sun kind wrong", j("Defs", "BiomeDefs", "RM_RustCathedral_Biome.xml"),
            "<heatKind>overhead</heatKind>", "<heatKind>ambient</heatKind>", "heatKind overhead")
    planted("bolt loses readout", j("Defs", "ThingDefs_Races", "RM_LivingBolt.xml"),
            "CompProperties_HumReadout", "CompProperties_Nothing", "hum readout comp")
    planted("strays never run", j("Patches", "RM_CathedralFinish_MapGenPatch.xml"),
            "<li>RM_CathedralStrays</li>", "", "RM_CathedralStrays is not added to MapCommonBase")
    planted("eel step ungated", j("Source", "RustCathedral", "RM_CathedralFinish.cs"),
            "map.Biome.defName != CathedralBiomeDefName || pawnKind == null",
            "pawnKind == null", "RM_GenStep_CoolantEels no longer self-gates")
    planted("strays ignore toggle", j("Source", "RustCathedral", "RM_CathedralFinish.cs"),
            "if (!RM_RustCathedralSettings.straysEnabled || RM_RustCathedralSettings.strayCount <= 0)",
            "if (RM_RustCathedralSettings.strayCount <= 0)", "RM_GenStep_CathedralStrays ignores its toggle")
    planted("line-cycle stops colonists", j("Source", "Hum", "RM_LineCycle.cs"),
            "p.IsColonist || ", "", "exempts colonists")
    planted("primer gate removed", j("Source", "Hum", "RM_HumReading.cs"),
            "nameof(Bill.PawnAllowedToStartAnew)", '"Other"', "the primer's trait gate")
    planted("mynock patch inert MayRequire", "WildAnimals_RustCathedral.xml",
            '<Operation Class="PatchOperationFindMod">',
            '<Operation Class="PatchOperationFindMod" MayRequire="mandrake.rsw.swbestiary">', "MayRequire", in_utinni=True)
    planted("mynock patch gone", None, None, None, "WildAnimals_RustCathedral.xml is missing", in_utinni=True,
            remove="WildAnimals_RustCathedral.xml")
    planted("warscar note dropped", "WildAnimals_Warscar.xml", "(WildAnimals_RustCathedral.xml,", "(elsewhere,",
            "multi-homing note", in_utinni=True)

    print("%d/%d checks passed" % (20 - len(FAILS), 20))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
