#!/usr/bin/env python3
"""T_SETTINGS_SWEEP_OFFLINE (Pyrelands 0.1.0, RIMMANDRAKE_MOVE_PYRE_SETTINGS_SWEEP_OFFLINE): the settings sweep, off the game.

Static reads of the C# (comments stripped), for every public static bool/float/int/string of RM_PyrelandsSettings:
  scribed          exactly one Scribe_Values.Look, its key unique, its default equal to the field initializer
  shipped          the initializer equals the shipped behaviour: every switch on, except the ruled-off ones (world switch,
                   cross-biome, heavy ambient ash), and the ruled numbers (dry ash 0.70, watered 1.40, fresh-burn +0.50
                   on a 6-day clock)
  read             the field is read (RM_PyrelandsSettings.<name>) in a mechanic file outside the settings file
  gated            every switch the "Mod enabled" master declares is read only in files that consult
                   PyrelandsMechanicsGate.On (the static half of g10), and the declared set is the pinned set
  gate_wired       PyrelandsMechanicsGate.On feeds "Mod enabled" (pyrelandsEnabled) and the Baroque Biomes toggle under the
                   key "Pyrelands" into RM_FireEcoKernel.MechanicsOn (blind challenge cycle 2: a gate that ignored either
                   left every other check green)
  entry_gated      each pinned mechanic entry point (a Harmony postfix) consults the gate in ITS OWN body, not merely
                   somewhere in its file (cycle 2: an ungated postfix in a gated file stayed green)
  sliders          every slider's range holds its field's shipped default (a range that excludes it moves the value the
                   first time the settings window draws)
Every planted fault must go red and the clean copy stay green.
Run: python3 <this file>      exit 0 = PASS, 1 = FAIL
"""
import glob
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_REL = "Source"
SETTINGS = "RM_PyrelandsMod.cs"
GATE = "PyrelandsMechanicsGate.On"
# Ruled values (owner): world switch OFF (card 2026-11-13); cross-biome off, labelled unsupported (2026-10-15);
# 6-day fresh-burn clock (card 2026-11-05); dry 70%, watered 140%, fresh-burn +50% (code values the g3 correction pinned).
RULED = {"biomeGenerationEnabled": False, "crossBiomeEnabled": False, "crossBiomeEverywhere": False, "ambientAshHeavy": False,
         "ashDryFertility": 0.70, "ashWateredFertility": 1.40, "freshBurnBonus": 0.50, "freshBurnDays": 6.0}
# The switches "Mod enabled" stops (RM_PyrelandsSettings.Masters, SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST, 2026-10-14).
GATED = {"ashDustingEnabled", "scorchFruitEnabled", "ashfallAccumulationEnabled", "freshBurnBonusEnabled", "ambientAshEnabled",
         "plantGrowthStagesEnabled", "wildPlantAllowlistEnabled", "scorchedRuinsEnabled", "burnLineEnabled",
         "fireHawkSpreadEnabled", "furnaceThermalEnabled", "fireClockEnabled", "burrowOnFireEnabled", "ashWaterFertilityEnabled",
         "blackRainDousingEnabled"}


def _strip(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def _val(v, typ, consts):
    v = v.strip()
    v = consts.get(v, v)
    if typ == "bool":
        return v == "true"
    if typ == "string":
        return v.strip('"')
    return round(float(v.rstrip("fFdD")), 6)


GATE_FILE = "PyrelandsMechanicsGate.cs"
GATE_EXPR = "RM_FireEcoKernel.MechanicsOn(RM_PyrelandsSettings.pyrelandsEnabled, ShellPresent, ShellOn)"
# (file, class, method): mechanic entry points that must consult the gate themselves.
ENTRY_POINTS = [("PyrelandsAshField.cs", "PyrelandsAshFieldPatches", "FertilityPostfix"),
                ("FireEcologyHook.cs", "Patch_FireTick_BlackRainDouses", "Postfix"),
                ("FireEcologyHook.cs", "Patch_FireTick_AshAndScorchFruit", "Postfix"),
                ("FireEcologyHook.cs", "Patch_FilthMaker_NoAshOnAsh", "Postfix"),
                ("PyrelandsNoOrdinaryRain.cs", "PyrelandsNoOrdinaryRain", "Postfix_ChooseNextWeather")]


def _block(s, start):
    """The brace-matched body that opens at or after index start, or None."""
    i = s.find("{", start)
    if i < 0:
        return None
    d, j = 1, i + 1
    while d and j < len(s):
        d += {"{": 1, "}": -1}.get(s[j], 0)
        j += 1
    return s[i + 1:j - 1] if d == 0 else None


def _method_body(s, cls, meth):
    m = re.search(r"\bclass %s\b" % re.escape(cls), s)
    body = _block(s, m.end()) if m else None
    if body is None:
        return None
    mm = re.search(r"\b%s\s*\([^;{}]*\)\s*\{" % re.escape(meth), body)
    return _block(body, mm.end() - 1) if mm else None


def _num(v, consts):
    v = consts.get(v.strip(), v.strip())
    m = re.match(r"^(\w+)\s*\*\s*([\d.]+)f?$", v)
    if m and m.group(1) in consts:
        return float(consts[m.group(1)].rstrip("fFdD")) * float(m.group(2))
    try:
        return float(v.rstrip("fFdD"))
    except ValueError:
        return None


def facts(mod):
    out = []

    def fact(name, bad, detail=""):
        out.append((name, not bad, "; ".join(bad)[:400] if bad else detail))

    src_dir = os.path.join(mod, SRC_REL)
    ms = _strip(open(os.path.join(src_dir, SETTINGS)).read())
    consts = dict(re.findall(r"public const \w+ (\w+)\s*=\s*([^;]+);", ms))
    fields = {n: (t, _val(v, t, consts)) for t, n, v in re.findall(r"public static (bool|float|int|string) (\w+)\s*=\s*([^;]+);", ms)}
    looks = re.findall(r"Scribe_Values\.Look\(ref (\w+),\s*\"(\w+)\",\s*([^)]+)\)", ms)
    bad = []
    for n, (t, v) in fields.items():
        mine = [l for l in looks if l[0] == n]
        if len(mine) != 1:
            bad.append("%s: %d Scribe lines" % (n, len(mine)))
        elif _val(mine[0][2], t, consts) != v:
            bad.append("%s: Scribe default %s, initializer %s" % (n, mine[0][2].strip(), v))
    keys = [l[1] for l in looks]
    bad += ["duplicate Scribe key %s" % k for k in set(keys) if keys.count(k) > 1]
    bad += ["Scribe of unknown field %s" % l[0] for l in looks if l[0] not in fields]
    fact("scribed", bad, "%d fields, %d Scribe lines" % (len(fields), len(looks)))
    bad = []
    for n, (t, v) in fields.items():
        want = RULED.get(n, True if t == "bool" else None)
        if want is not None and v != want:
            bad.append("%s ships %s, ruled %s" % (n, v, want))
    fact("shipped", bad, "%d switches on, %d ruled values" % (sum(1 for t, v in fields.values() if t == "bool" and v), len(RULED)))
    code = {}
    for f in glob.glob(os.path.join(src_dir, "**", "*.cs"), recursive=True):
        if os.path.basename(f) == SETTINGS or os.sep + "SelfTest" + os.sep in f:
            continue
        code[os.path.relpath(f, src_dir)] = _strip(open(f, errors="replace").read())
    readers = {n: [f for f, s in code.items() if re.search(r"\bRM_PyrelandsSettings\.%s\b" % n, s)] for n in fields}
    fact("read", ["%s has no reader outside the settings file" % n for n, r in readers.items() if not r and n != "pyrelandsEnabled"]
         + ([] if any("pyrelandsEnabled" in s and "MechanicsOn" in s for s in code.values()) else ["pyrelandsEnabled not fed to the gate"]),
         "%d fields read" % sum(1 for r in readers.values() if r))
    m = re.search(r'\.Declare\("pyrelandsEnabled",([^)]*)\)', ms)
    declared = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
    bad = ["declared gated set differs: +%s -%s" % (sorted(declared - GATED), sorted(GATED - declared))] if declared != GATED else []
    for n in sorted(GATED):
        for f in readers.get(n, []):
            if GATE not in code[f]:
                bad.append("%s read in %s, which never consults %s" % (n, f, GATE))
    fact("gated", bad, "%d gated switches, %d read sites" % (len(GATED), sum(len(readers.get(n, [])) for n in GATED)))
    g = code.get(GATE_FILE, "")
    bad = []
    if not re.search(r"\bOn\s*=>\s*" + re.escape(GATE_EXPR), g):
        bad.append("PyrelandsMechanicsGate.On is not " + GATE_EXPR)
    if not re.search(r'RosterKey\s*=\s*"Pyrelands"\s*;', g):
        bad.append('the roster key is not "Pyrelands"')
    fact("gate_wired", bad, "On = MechanicsOn(Mod enabled, shell, toggle \"Pyrelands\")")
    bad = []
    for f, cls, meth in ENTRY_POINTS:
        body = _method_body(code.get(f, ""), cls, meth)
        if body is None:
            bad.append("%s.%s not found in %s" % (cls, meth, f))
        elif GATE not in body:
            bad.append("%s.%s never consults %s" % (cls, meth, GATE))
    fact("entry_gated", bad, "%d entry points consult the gate" % len(ENTRY_POINTS))
    bad = []
    sliders = re.findall(r"(\w+)\s*=\s*(?:Mathf\.RoundToInt\(|\(int\)\s*)?list\.Slider\((\w+),\s*([^,]+),\s*([^)]+)\)", ms)
    for target, arg, lo, hi in sliders:
        if target not in fields:
            continue
        d, l, h = fields[target][1], _num(lo, consts), _num(hi, consts)
        if l is None or d < l - 1e-6 or (h is not None and d > h + 1e-6):
            bad.append("%s ships %s outside its slider [%s, %s]" % (target, d, lo.strip(), hi.strip()))
    fact("sliders", bad if sliders else ["no slider found"], "%d sliders hold their defaults" % len(sliders))
    return out


S = "Source/"
MUTANTS = [
    ("Scribe default flipped", S + SETTINGS, 'Look(ref burnLineEnabled, "burnLineEnabled", true)', 'Look(ref burnLineEnabled, "burnLineEnabled", false)'),
    ("initializer flipped", S + SETTINGS, "public static bool burnLineEnabled = true;", "public static bool burnLineEnabled = false;"),
    ("world switch shipped on", S + SETTINGS, "public static bool biomeGenerationEnabled = false;", "public static bool biomeGenerationEnabled = true;"),
    ("dry ash 0.6", S + SETTINGS, "public static float ashDryFertility = 0.70f;", "public static float ashDryFertility = 0.60f;"),
    ("Scribe line dropped", S + SETTINGS, 'Scribe_Values.Look(ref ullaiEnabled, "ullaiEnabled", true);', ""),
    ("duplicate Scribe key", S + SETTINGS, '"ullaiHerdSizeMultiplier", 1f', '"ullaiEnabled", 1f'),
    ("reader dropped", S + "RM_TerrainDig.cs", "RM_PyrelandsSettings.sandShovelYieldMultiplier", "1f"),
    ("reader only in a comment", S + "RM_PyrelandsGiants.cs", "RM_PyrelandsSettings.furnaceBeastGiant", "true /* RM_PyrelandsSettings.furnaceBeastGiant */"),
    ("gate dropped at a read site", S + "PlantGrowthStages.cs", GATE, "true"),
    ("switch undeclared from the master", S + SETTINGS, '"burrowOnFireEnabled", "ashWaterFertilityEnabled", "blackRainDousingEnabled")', '"ashWaterFertilityEnabled", "blackRainDousingEnabled")'),
    ("gate ignores Mod enabled", S + GATE_FILE, "MechanicsOn(RM_PyrelandsSettings.pyrelandsEnabled,", "MechanicsOn(true,"),
    ("roster key misspelt", S + GATE_FILE, 'RosterKey = "Pyrelands";', 'RosterKey = "Pyrelandz";'),
    ("ash-field postfix ungated", S + "PyrelandsAshField.cs", "if (___map == null || !PyrelandsMechanicsGate.On) return;", "if (___map == null) return;"),
    ("black-rain douse ungated", S + "FireEcologyHook.cs", "BlackRainDouseAmount(PyrelandsMechanicsGate.On,", "BlackRainDouseAmount(true,"),
    ("rain swap ungated", S + "PyrelandsNoOrdinaryRain.cs", "pyre, PyrelandsMechanicsGate.On)", "pyre, true)"),
    ("slider range excludes its default", S + SETTINGS, "list.Slider(blackRainDousing, 0f, 100f)", "list.Slider(blackRainDousing, 50f, 100f)"),
]


def main():
    bad = 0
    for name, ok, det in facts(HERE):
        print("%-10s %s  %s" % (name, "ok  " if ok else "FAIL", det))
        bad += not ok
    tmp = tempfile.mkdtemp(prefix="pyre_settings_mut_")
    red = 0
    try:
        base = os.path.join(tmp, "base")
        shutil.copytree(os.path.join(HERE, "Source"), os.path.join(base, "Source"))
        if not all(ok for _, ok, _ in facts(base)):
            print("FAIL: the unchanged copy is not green")
            return 1
        for i, (label, rel, old, new) in enumerate(MUTANTS):
            m = os.path.join(tmp, "m%d" % i)
            shutil.copytree(base, m)
            p = os.path.join(m, rel)
            t = open(p, errors="replace").read()
            if old not in t:
                print("mutant %-36s ANCHOR MISSING (%r)" % (label, old))
                bad += 1
                continue
            open(p, "w").write(t.replace(old, new))
            fails = [n for n, ok, _ in facts(m) if not ok]
            print("mutant %-36s %s %s" % (label, "red " if fails else "NOT CAUGHT", ",".join(fails)))
            bad += not fails
            red += bool(fails)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("FAIL: %d fact(s) or mutant(s) wrong" % bad)
        return 1
    print("PASS: every Pyrelands setting scribed, shipped as ruled, read and gated; %d of %d mutants red, the clean copy green"
          % (red, len(MUTANTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
