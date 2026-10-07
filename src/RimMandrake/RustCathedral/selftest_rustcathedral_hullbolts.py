"""selftest_rustcathedral_hullbolts.py -- validation.hullbolts_problems is clean on the shipped mod and reddens on each
break it exists to catch, planted in a temp copy of Defs/Source (never the shipped files).
RUSTCATHEDRAL_HULL_BOLTS_BUILD_1, L0."""
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
    bad = v.hullbolts_problems()
    check("shipped: hull bolts clean", bad == [], bad)

    def planted(label, rel, old, new, expect):
        tmp = tempfile.mkdtemp()
        try:
            for d in ("Defs", "Source"):
                shutil.copytree(os.path.join(HERE, d), os.path.join(tmp, d),
                                ignore=shutil.ignore_patterns("obj", "bin", "__pycache__"))
            _sub(os.path.join(tmp, rel), old, new)
            got = v.hullbolts_problems(mod_root=tmp)
            check(label, any(expect in g for g in got), got)
        finally:
            shutil.rmtree(tmp)

    j = os.path.join
    xml = j("Defs", "ThingDefs_Races", "RM_HullBolt.xml")
    cs = j("Source", "Hum", "RM_HullBolts.cs")
    planted("burns like anything else", xml, "<damageDef>Flame</damageDef><multiplier>0.05</multiplier>",
            "<damageDef>Flame</damageDef><multiplier>1</multiplier>", "damage factor for Flame")
    planted("EMP stuns it", xml, "<damageDef>EMP</damageDef><multiplier>0.05</multiplier>",
            "<damageDef>EMP</damageDef><multiplier>0.5</multiplier>", "damage factor for EMP")
    planted("dies in vacuum", xml, '<VacuumResistance MayRequire="Ludeon.RimWorld.Odyssey">1</VacuumResistance>', "",
            "VacuumResistance")
    planted("nothing keeps it on the hull", xml, '<li Class="RimMandrake.RustCathedral.Hum.CompProperties_HullBound" />', "",
            "CompProperties_HullBound")
    planted("it wanders into the ship", xml, '<li Class="RimMandrake.RustCathedral.Hum.RM_JobGiver_HullIdle" />',
            '<li Class="JobGiver_WanderAnywhere" />', "wanders")
    planted("it learned to fight", xml, '<li Class="JobGiver_IdleError" />',
            '<li Class="JobGiver_AIFightEnemies" /><li Class="JobGiver_IdleError" />', "fight branch")
    planted("a sale with no things hears everything", xml, "<things><li>RM_CoolantEelCatch</li></things>", "",
            "Sell with no <things>")
    planted("prying is never heard", xml, "<kind>PryHullBolt</kind>", "<kind>Butcher</kind>", "kind PryHullBolt")
    planted("the memory sours", xml, "<baseMoodEffect>2</baseMoodEffect>", "<baseMoodEffect>-2</baseMoodEffect>",
            "not a positive memory")
    planted("text names the listener", xml, "It keeps to the outer plating", "It listens for the Cathedral from the outer plating",
            "names the listener")
    planted("no boarding hook", cs, "nameof(GravshipUtility.GenerateGravship)", "\"GenerateGravship\"", "boarding at liftoff")
    planted("no sale hook", cs, "nameof(Tradeable.ResolveTrade)", "\"ResolveTrade\"", "hearing a sale")
    planted("landing ignores the cap", cs, "RustCathedralHumSettings.hullBoltIrritationCap", "100f", "hullBoltIrritationCap")
    planted("witness toggle ignored", cs, "!RustCathedralHumSettings.hullBoltWitnessEnabled", "false", "hullBoltWitnessEnabled")
    planted("setting not saved", j("Source", "RustCathedral", "RM_RustCathedralMod.cs"), '"hum_hullBoltRevealDays"',
            '"hum_x"', "hullBoltRevealDays is not saved")
    planted("dropped from the csproj", j("Source", "Hum", "RimMandrake.RustCathedral.Hum.csproj"),
            '<Compile Include="RM_HullBolts.cs" />', "", "not in the Hum csproj")

    print("%d/%d checks passed" % (17 - len(FAILS), 17))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
