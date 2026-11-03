#!/usr/bin/env python3
# selftest-timeout: 60
"""THERMOSTAT_FIX_IGNORES_SUBNOTCH_LIQUID: offline structural proof that the liquid thermostat counts a part-notch
sheet (WaterDlAt > 0, FillAt == 0) and that each pin can go red. No game, no bridge, no dotnet (the C# cases
MapControl_thermostat_energy / MapControl_thermostat_subnotch_liquid run the arithmetic under dotnet; this file is
the independent second instrument, and --dotnet-mutant replays a mutant through them).

Every check reads comment-stripped, whitespace-normalised source, so a pin cannot be satisfied by a comment.

  T1  HeatInterval never calls FillAt (whole notches: a 0.3-notch sheet reads 0)
  T2  HeatInterval counts a dug square by ex.WaterDlAt(c) through ThermostatCellNotches, divisor RM_LevelSolve.U,
      natural fallback NaturalCellLevels
  T3  HeatInterval reads the natural body's dL with ex.NaturalWaterDlAt(c, out _, out floor)
  T4  `float levels = ...ThermostatCellNotches(...)` is followed at once by the only sub-notch-safe skip,
      `if (!(levels > 0f)) { continue; }`, levels is assigned once, and there are exactly two `continue;`
  T5  nothing in HeatInterval rounds (Floor/Round/Ceil/(int)/(long)/FloorToInt/RoundToInt/CeilToInt)
  T6  the room sum adds the square's own levels into a Dictionary<Room, float>
  T7  ThermostatEnergy takes the room's summed float levels (kv.Value) and its parameter is `float levels`
  T8  ThermostatCellNotches: a dug square returns waterDl / (float)dlPerNotch for any waterDl > 0 (float division,
      no rounding, no whole-notch guard), guards dlPerNotch <= 0, and a natural square divides naturalDl the same way
  T9  ThermostatEnergy skips only !(levels > 0f) and multiplies the unrounded levels (per * levels * ...)
  T10 both callers drive it: the heat pulse (t.HeatInterval(ex, strength)) and HeatNow
  T11 same unit as RM_LiquidHeat.Push (ex.WaterDlAt(c) / (float)RM_LevelSolve.U) and NaturalLevels' floor rule;
      the thermostat's NaturalCellLevels equals RM_LiquidHeatMath.NaturalCellLevels
  T12 the C# case file (--cases) still holds both cases with the 0.3-notch assertions and the call-site pins, and
      Program.cs runs MapControlChecks; the SelfTest csproj compiles RM_MapControlMath.cs and MapControlChecks.cs

  python3 selftest_thermostat_subnotch.py [--cases <MapControlChecks.cs>] [--root <dir>] [--no-mutants]
  python3 selftest_thermostat_subnotch.py --dotnet-mutant M5      # mutate in tree, run the C# cases, restore

A run with no --root also runs every built-in mutant against a temporary copy and fails unless each mutant turns at
least one pin red (and its expected pin among them). Evidence: infrastructure/state/evidence/<item>/.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = "src/RimMandrake/FlowWorks/Source/"
THERMO = SRC + "MapControls/RM_LiquidThermostat.cs"
MATH = SRC + "MapControls/RM_MapControlMath.cs"
CONTROLS = SRC + "MapControls/RM_MapControls.cs"
HEAT = SRC + "RM_LiquidHeat.cs"
HEATMATH = SRC + "RM_LiquidHeatMath.cs"
CASES = SRC + "SelfTest/MapControlChecks.cs"
PROGRAM = SRC + "SelfTest/Program.cs"
TESTPROJ = SRC + "SelfTest/RimMandrakeFlowWorks.SelfTest.csproj"
FILES = [THERMO, MATH, CONTROLS, HEAT, HEATMATH, CASES, PROGRAM, TESTPROJ]


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"//[^\n]*", " ", src)


def norm(src):
    return re.sub(r"\s+", " ", strip_comments(src)).strip()


def between(s, a, b):
    i = s.find(a)
    if i < 0:
        return ""
    j = s.find(b, i + len(a))
    return s[i:j] if j >= 0 else ""


def method(s, sig):
    """Body of the method whose (normalised) signature starts with sig: brace-matched, '' when absent."""
    i = s.find(sig)
    if i < 0:
        return ""
    j = s.find("{", i)
    depth = 0
    for k in range(j, len(s)):
        depth += {"{": 1, "}": -1}.get(s[k], 0)
        if depth == 0:
            return s[i:k + 1]
    return ""


# Rounding calls and integer casts, by token: a bare "Floor" would also hit the parameter naturalFloor.
ROUND_RE = re.compile(r"\b(?:Math|Mathf)\.(?:Floor|Round|Ceiling|Ceil|Truncate)\b|\b(?:FloorToInt|RoundToInt|CeilToInt)\b"
                      r"|\(\s*(?:int|long|short)\s*\)")


def rounders(body):
    return ROUND_RE.findall(body)


def checks(root, cases_rel):
    th, mt, mc = norm(read(root, THERMO)), norm(read(root, MATH)), norm(read(root, CONTROLS))
    heat, heatmath = norm(read(root, HEAT)), norm(read(root, HEATMATH))
    hi = method(th, "public void HeatInterval(")
    cn = method(mt, "public static float ThermostatCellNotches(")
    en = method(mt, "public static float ThermostatEnergy(")
    out = []

    def check(tid, ok, why):
        out.append((tid, bool(ok), why))

    check("T0", hi and cn and en, "HeatInterval / ThermostatCellNotches / ThermostatEnergy not found (instrument blind)")
    check("T1", hi and "FillAt(" not in hi, "HeatInterval calls FillAt (whole notches only)")
    check("T2", "RM_MapControlMath.ThermostatCellNotches(dug, dug ? ex.WaterDlAt(c) : 0L, natural, naturalDl, floor, "
          "RM_LevelSolve.U, NaturalCellLevels)" in hi, "HeatInterval does not count a dug square by its WaterDlAt dL")
    check("T3", "naturalDl = ex.NaturalWaterDlAt(c, out _, out floor);" in hi,
          "HeatInterval does not read the natural body's dL")
    assigns = re.findall(r"\blevels\s*(?:=|\+=|-=|\*=|/=)(?!=)", hi)
    check("T4", re.search(r"float levels = RM_MapControlMath\.ThermostatCellNotches\([^;]*\); "
                          r"if \(!\(levels > 0f\)\) \{ continue; \} lastLevels \+= levels;", hi)
          and len(assigns) == 1 and hi.count("continue;") == 2 and "lastOutdoorCells++; continue; }" in hi,
          "HeatInterval's skip is not exactly !(levels > 0f) right after the count, or levels is reassigned, "
          "or another skip appeared (%d assigns, %d continue)" % (len(assigns), hi.count("continue;")))
    check("T5", not rounders(hi), "HeatInterval rounds: %s" % rounders(hi))
    check("T6", "levelsByRoom.TryGetValue(room, out float had); levelsByRoom[room] = had + levels;" in hi
          and "Dictionary<Room, float> levelsByRoom" in th, "the room sum does not add the square's float levels")
    check("T7", "RM_MapControlMath.ThermostatEnergy(kv.Value, kv.Key.Temperature, kv.Key.CellCount, targetC, strength)"
          in hi and "foreach (KeyValuePair<Room, float> kv in levelsByRoom)" in hi
          and en.startswith("public static float ThermostatEnergy(float levels,"),
          "ThermostatEnergy does not take the room's summed float levels")
    exc = between(cn, "if (excavated) {", "}")
    nat = cn[cn.find("if (naturalFloor <= 0)"):] if "if (naturalFloor <= 0)" in cn else ""
    check("T8", cn.startswith("public static float ThermostatCellNotches(bool excavated, long waterDl, bool source, "
                              "double naturalDl, int naturalFloor, int dlPerNotch, float naturalFallback)")
          and "if (dlPerNotch <= 0) { return 0f; }" in cn
          and exc.strip() == "if (excavated) { return waterDl > 0 ? waterDl / (float)dlPerNotch : 0f;"
          and "return naturalDl > 0 ? (float)(naturalDl / dlPerNotch) : 0f;" in nat
          and "return naturalFallback;" in nat and not rounders(cn),
          "ThermostatCellNotches does not return waterDl / (float)dlPerNotch for every waterDl > 0 "
          "(or the natural branch / dlPerNotch guard changed, or it rounds)")
    check("T9", "if (!(levels > 0f) ||" in en and "float e = per * levels * ThermoSecondsPerInterval * strength;" in en
          and not rounders(en), "ThermostatEnergy drops or rounds part-notch levels")
    pulse = method(mc, "public static void HeatAll(") or mc
    check("T10", "t.HeatInterval(ex, strength);" in mc and "if (scratch[i] is Building_RM_LiquidThermostat t && "
          "t.Spawned && t.active) { t.HeatInterval(ex, strength); }" in mc
          and "th.HeatInterval(ex, RimMandrakeFlowWorksSettings.liquidHeatStrength);" in mc,
          "a caller no longer drives HeatInterval (%d chars read)" % len(pulse))
    check("T11", "float f = ex.WaterDlAt(c) / (float)RM_LevelSolve.U;" in heat
          and "return floor > 0 ? (float)(dl / RM_LevelSolve.U) : RM_LiquidHeatMath.NaturalCellLevels;" in heat
          and re.search(r"public const int NaturalCellLevels = (\d+);", th)
          and re.search(r"public const int NaturalCellLevels = (\d+);", th).group(1)
          == (re.search(r"public const int NaturalCellLevels = (\d+);", heatmath) or [None, "?"])[1]
          and "if (naturalFloor <= 0) { return naturalFallback; }" in cn,
          "the thermostat's unit or natural rule no longer matches RM_LiquidHeat")
    cs = norm(read(root, cases_rel))
    sub = between(cs, 'Case("MapControl_thermostat_subnotch_liquid"', 'Case("')
    ene = between(cs, 'Case("MapControl_thermostat_energy"', 'Case("')
    need = ["RM_MapControlMath.ThermostatCellNotches(true, 30, false, 0, 0, U, 2f)", "Math.Abs(sheet - 0.3f) < 1e-5",
            "RM_MapControlMath.ThermostatEnergy(sheet * 9, 21f, 9, 40f, 1f)", "Assert(e > 0f &&",
            "Assert(!hi.Contains(\"FillAt(\")", "Math.Abs(temp - 40f) < 0.01f",
            "if (!(levels > 0f)) { continue; } lastLevels += levels;"]
    missing = [n for n in need if n not in sub]
    prog, proj = norm(read(root, PROGRAM)), read(root, TESTPROJ)
    check("T12", ene and sub and not missing and "MapControlChecks.Run(Case);" in prog
          and '<Compile Include="..\\MapControls\\RM_MapControlMath.cs" />' in proj
          and '<Compile Include="MapControlChecks.cs" />' in proj,
          "the C# cases lost their sub-notch assertions or registration: missing %s" % missing)
    return out


# (id, file, old, new, pin that must go red). Each `old` must occur in the file (an absent anchor is an error).
MUTANTS = [
    ("M1", THERMO, "dug ? ex.WaterDlAt(c) : 0L", "dug ? ex.FillAt(c) * (long)RM_LevelSolve.U : 0L", "T1"),
    ("M2", THERMO, "if (!(levels > 0f))", "if (!(levels >= 1f))", "T4"),
    ("M3", THERMO, "float levels = RM_MapControlMath", "float levels = (int)RM_MapControlMath", "T5"),
    ("M4", THERMO, "levelsByRoom[room] = had + levels;", "levelsByRoom[room] = had + (float)Math.Floor(levels);", "T5"),
    ("M5", MATH, "return waterDl > 0 ? waterDl / (float)dlPerNotch : 0f;", "return waterDl > 0 ? waterDl / dlPerNotch : 0f;", "T8"),
    ("M6", MATH, "return waterDl > 0 ? waterDl", "return waterDl >= dlPerNotch ? waterDl", "T8"),
    ("M7", MATH, "public static float ThermostatEnergy(float levels,", "public static float ThermostatEnergy(int levels,", "T7"),
    ("M8", MATH, "if (!(levels > 0f) || roomCells", "if (levels < 1f || roomCells", "T9"),
    ("M9", CONTROLS, "t.HeatInterval(ex, strength);", ";", "T10"),
    ("M10", THERMO, "lastLevels += levels;", "lastLevels += levels; if (levels < 1f) { continue; }", "T4"),
    ("M11", THERMO, "RM_MapControlMath.ThermostatEnergy(kv.Value,", "RM_MapControlMath.ThermostatEnergy((int)kv.Value,", "T5"),
    ("M12", THERMO, "float levels = RM_MapControlMath.ThermostatCellNotches(dug, dug ? ex.WaterDlAt(c) : 0L,",
     "// float levels = RM_MapControlMath.ThermostatCellNotches(dug, dug ? ex.WaterDlAt(c) : 0L,\n"
     "\t\t\t\tfloat levels = ex.FillAt(c); float unused = RM_MapControlMath.ThermostatCellNotches(dug, 0L,", "T2"),
    ("M13", MATH, "return naturalDl > 0 ? (float)(naturalDl / dlPerNotch) : 0f;",
     "return naturalDl > 0 ? (float)Math.Floor(naturalDl / dlPerNotch) : 0f;", "T8"),
    ("M14", MATH, "float e = per * levels * ThermoSecondsPerInterval", "float e = per * (float)Math.Floor(levels) * ThermoSecondsPerInterval", "T9"),
    ("M15", THERMO, "naturalDl = ex.NaturalWaterDlAt(c, out _, out floor);", "naturalDl = 0;", "T3"),
    ("M16", CASES, "Assert(Math.Abs(sheet - 0.3f) < 1e-5,", "Assert(true,", "T12"),
]


def apply_mutant(root, m):
    mid, rel, old, new, _ = m
    p = os.path.join(root, rel)
    s = read(root, rel)
    if old not in s:
        raise SystemExit("mutant %s: anchor missing in %s: %r (the source moved; update the mutant)" % (mid, rel, old))
    with open(p, "w", encoding="utf-8") as f:
        f.write(s.replace(old, new, 1))


def run_mutants(cases_rel):
    bad = []
    tmp = tempfile.mkdtemp(prefix="thermo_mut_")
    try:
        for m in MUTANTS:
            root = os.path.join(tmp, m[0])
            for rel in FILES + [cases_rel]:
                os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
                shutil.copyfile(os.path.join(REPO, rel), os.path.join(root, rel))
            apply_mutant(root, m)
            red = [t for t, ok, _ in checks(root, cases_rel) if not ok]
            killed = m[4] in red
            print("%s %-4s %-28s red=%s (expected %s)" % ("KILLED" if killed else "SURVIVED", m[0],
                                                       os.path.basename(m[1]), ",".join(red) or "none", m[4]))
            if not killed:
                bad.append(m[0])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return bad


def dotnet_mutant(mid):
    """Mutate the clone in place, run the contract's C# cases, restore byte-for-byte. Exit 0 = the C# cases went red."""
    m = [x for x in MUTANTS if x[0] == mid]
    if not m:
        raise SystemExit("no mutant %s" % mid)
    m = m[0]
    p = os.path.join(REPO, m[1])
    with open(p, "rb") as f:
        orig = f.read()
    try:
        apply_mutant(REPO, m)
        r = subprocess.run([sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/selftest_flowworks_stock.py"),
                            "--only", "MapControl_thermostat_energy,MapControl_thermostat_subnotch_liquid"],
                           capture_output=True, text=True, timeout=500)
    finally:
        with open(p, "wb") as f:
            f.write(orig)
    with open(p, "rb") as f:
        assert hashlib.sha1(f.read()).digest() == hashlib.sha1(orig).digest(), "restore failed: " + p
    fails = [ln.strip() for ln in r.stdout.splitlines() if ln.startswith("FAIL") or "error CS" in ln][:4]
    built = "error CS" not in r.stdout + r.stderr and "build of" not in r.stderr
    print("%s %s dotnet rc=%d %s %s" % ("KILLED" if r.returncode else "SURVIVED", mid, r.returncode,
                                       "built" if built else "BUILD-FAILED", " | ".join(fails)[:400]))
    return 0 if r.returncode else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=REPO, help="read the source from a copy (mutants use it)")
    ap.add_argument("--cases", default=CASES, help="repo-relative path of the C# case file (MapControlChecks.cs)")
    ap.add_argument("--no-mutants", action="store_true", help="skip the built-in mutant sweep")
    ap.add_argument("--dotnet-mutant", default=None, help="Mn: mutate in tree, run the C# cases, restore")
    a = ap.parse_args(argv)
    cases_rel = os.path.relpath(os.path.join(REPO, a.cases), REPO) if not os.path.isabs(a.cases) else os.path.relpath(a.cases, REPO)
    if a.dotnet_mutant:
        return dotnet_mutant(a.dotnet_mutant)
    res = checks(a.root, cases_rel)
    for t, ok, why in res:
        print("%s %s%s" % ("ok  " if ok else "FAIL", t, "" if ok else "  " + why))
    fails = [t for t, ok, _ in res if not ok]
    survived = []
    if not fails and a.root == REPO and not a.no_mutants:
        survived = run_mutants(cases_rel)
    ran = not fails and a.root == REPO and not a.no_mutants
    print("%d/%d pins hold%s" % (len(res) - len(fails), len(res),
                                 "; %d/%d mutants killed" % (len(MUTANTS) - len(survived), len(MUTANTS)) if ran else
                                 "; mutants not run" + (" (a pin is red)" if fails else "")))
    return 1 if fails or survived else 0


if __name__ == "__main__":
    sys.exit(main())
