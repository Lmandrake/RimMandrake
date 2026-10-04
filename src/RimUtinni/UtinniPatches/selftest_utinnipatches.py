"""selftest_utinnipatches.py -- the two UTINNIPATCHES_COVERAGE_GAPS_1 static bars are clean on the shipped mod
and redden on each break they exist to catch (planted in temp copies, never the shipped files)."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _edit(p, a, b):
    s = open(p, encoding="utf-8").read()
    assert a in s, (p, a)
    open(p, "w", encoding="utf-8").write(s.replace(a, b, 1))


def main():
    spec = importlib.util.spec_from_file_location("up_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    bad, seen = v.setting_gate_problems()
    check("shipped: setting gates clean", bad == [] and seen >= 2, (bad, seen))
    tmp = tempfile.mkdtemp()
    try:
        m = os.path.join(tmp, "UtinniPatches")
        os.makedirs(m)
        for d in ("Source", "Patches"):
            shutil.copytree(os.path.join(HERE, d), os.path.join(m, d))
        _edit(os.path.join(m, "Patches", "UtinniWorldIcon.xml"),
              "<setting>utinniWorldIconEnabled</setting>", "<setting>utinniWorldIconEnabledX</setting>")
        got, _ = v.setting_gate_problems(m)
        check("break: unknown setting name", any("not a case" in g for g in got), got)
        shutil.copy(os.path.join(HERE, "Patches", "UtinniWorldIcon.xml"), os.path.join(m, "Patches", "UtinniWorldIcon.xml"))
        _edit(os.path.join(m, "Source", "UtinniPatchesSettings.cs"),
              'Scribe_Values.Look(ref holyFlameActEnabled, "holyFlameActEnabled"', 'Scribe_Values.Look(ref holyFlameActEnabled, "holyFlameAct"')
        got, _ = v.setting_gate_problems(m)
        check("break: toggle not Scribed under its key", any("never persists" in g for g in got) and len(got) == 1, got)

        core = os.path.join(tmp, "CoreDefs")
        os.makedirs(core)
        check("shipped: infestation ban clean on real Core", v.infestation_ban_problems() in ([], None),
              v.infestation_ban_problems())
        open(os.path.join(core, "a.xml"), "w").write(
            "<Defs><IncidentDef><defName>Infestation</defName><baseChanceWithRoyalty>2</baseChanceWithRoyalty>"
            "</IncidentDef></Defs>")
        got = v.infestation_ban_problems(core) or []
        check("break: Core lost baseChance", any("no <baseChance>" in g for g in got), got)
        check("break: Core gained baseChanceWithRoyalty", any("baseChanceWithRoyalty" in g for g in got), got)
        os.remove(os.path.join(core, "a.xml"))
        got = v.infestation_ban_problems(core) or []
        check("break: Core def absent -> sanity red, never clean", any("sanity" in g for g in got), got)
        check("unreachable Core -> None (UNMEASURED), never clean", v.infestation_ban_problems(os.path.join(tmp, "nope")) is None)
    finally:
        shutil.rmtree(tmp)
    print("selftest_utinnipatches: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
