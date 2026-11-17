#!/usr/bin/env python3
# selftest-timeout: 780   (winbuild.run_interop may repeat a lost WSL launch, ~2 min each)
"""T_ASH_PROBE_OFFLINE (Pyrelands 0.1.0, RIMMANDRAKE_PIN_PYRE_ASH_PROBE_OFFLINE), bar ash_fertility_probe.

The probe line is RM_FireEcoKernel.ProbeLine (game-free). This test compiles the PRODUCTION RM_FireEcoKernel.cs with a small
harness and runs ProbeLine over a table: a dry old cell and a burned wet cell read differently part by part (base, watered
lift, fresh-burn bonus with its age and days left, black rain on the cell); a probe that hands back the base for a wet cell
reads consistent=False (the leaf's false pass); with ashWaterFertilityEnabled off, or the mechanics gate off, the line
starts refused=<reason> and still lists the parts. The same kernel text is compiled again with one planted fault per
namespace and each must fail the table; a fault whose pattern no longer matches fails the test. Static reads check that
PyrelandsAshField.ProbeCell hands ProbeLine the real grid fertility, the cell's own parts (watered, bonus, burn tick, black-rain
stamp, the bonus clock), the switch and the gate, that ProbeRect exists, and
that validation.py's _probe still finds its keys.
Run: python3 <this file>
"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path.insert(0, UTILS)
import winbuild  # noqa: E402

# PYRE_PROBE_KERNEL / PYRE_PROBE_FIELD point at other copies (the red-first run against the base commit)
KERNEL = os.environ.get("PYRE_PROBE_KERNEL") or os.path.join(HERE, "Source", "Kernel", "RM_FireEcoKernel.cs")
FIELD = os.environ.get("PYRE_PROBE_FIELD") or os.path.join(HERE, "Source", "PyrelandsAshField.cs")
VALIDATION = os.path.join(HERE, "validation.py")
MUTANTS = [
    ("water_refusal_dropped", ': !waterOn ? "the ash field is off (ashWaterFertilityEnabled)" : null', ": null"),
    ("gate_refusal_dropped", "string refused = !gateOn ?", "string refused = false ?"),
    ("lift_is_the_whole_wet_value", "wateredFertility - baseFertility : 0f", "wateredFertility : 0f"),
    ("age_in_hours_not_days", "((now - burnTick) / 60000f)", "((now - burnTick) / 2500f)"),
    ("always_consistent", '(Math.Abs(fertility - expected) < 0.001f ? "True" : "False")', '"True"'),
    ("rain_ignores_the_roof", "blackRainFalling && !roofed, expected", "blackRainFalling, expected"),
    ("watered_shown_with_water_off", "bool wetNow = waterOn && watered;", "bool wetNow = watered;"),
    ("expected_ignores_bonus", "AshFertility(baseFertility, wateredFertility, watered, waterOn, bonus, cap)",
     "AshFertility(baseFertility, wateredFertility, watered, waterOn, 0f, cap)"),
]
HARNESS = r"""
using System;
using System.Collections.Generic;
using System.Globalization;
namespace Harness
{
    delegate string Probe(float fertility, string terrain, bool ashField, bool watered, float b, float wf, float bonus, int burnTick,
        int now, int dur, bool rain, bool roofed, int rainUntil, bool active, bool waterOn, bool gateOn, float cap);
    static class Program
    {
        static Dictionary<string, string> P(string line)
        {
            var d = new Dictionary<string, string>();
            foreach (var kv in line.Split(';')) { int i = kv.IndexOf('='); if (i > 0) d[kv.Substring(0, i)] = kv.Substring(i + 1); }
            return d;
        }
        static float F(Dictionary<string, string> d, string k) => d.ContainsKey(k) ? float.Parse(d[k], CultureInfo.InvariantCulture) : float.NaN;
        static int Check(Probe probe, List<string> why)
        {
            const int Day = 60000, Dur = 6 * Day, Now = 1000000; const float Cap = 2f;
            int bad = 0;
            Action<bool, string> need = (ok, w) => { if (!ok) { bad++; if (why.Count < 4) why.Add(w); } };
            // A: dry old cell
            var a = P(probe(0.7f, "RM_FE_Ash_Deep", true, false, 0.7f, 1.4f, 0f, -1, Now, Dur, false, false, -1, true, true, true, Cap));
            need(!a.ContainsKey("refused"), "dry cell refused");
            need(Math.Abs(F(a, "lift")) < 1e-4 && Math.Abs(F(a, "bonus")) < 1e-4 && a["bonusAgeDays"] == "-1", "dry cell shows lift/bonus/age");
            need(Math.Abs(F(a, "expected") - 0.7f) < 1e-3 && a["consistent"] == "True" && a["rainOnCell"] == "False", "dry cell expected/consistent");
            // B: burned a day ago and watered
            float bonus = 0.5f * (1f - 1f / 6f), wet = Math.Min(Cap, 1.4f + bonus);
            var b = P(probe(wet, "RM_FE_Ash_Deep", true, true, 0.7f, 1.4f, bonus, Now - Day, Now, Dur, false, false, -1, true, true, true, Cap));
            need(Math.Abs(F(b, "lift") - 0.7f) < 1e-3, "wet lift not 0.7: " + (b.ContainsKey("lift") ? b["lift"] : "?"));
            need(Math.Abs(F(b, "bonusAgeDays") - 1f) < 0.01f && Math.Abs(F(b, "bonusDaysLeft") - 5f) < 0.01f, "burn age/left wrong: " + b["bonusAgeDays"]);
            need(Math.Abs(F(b, "expected") - wet) < 1e-3 && b["consistent"] == "True", "wet expected " + b["expected"]);
            need(b["watered"] == "True" && a["watered"] == "False" && F(a, "lift") != F(b, "lift") && F(a, "bonus") != F(b, "bonus"),
                 "the two cells do not differ part by part");
            // C: the false pass, the grid reports the base on the wet fresh cell
            var c = P(probe(0.7f, "RM_FE_Ash_Deep", true, true, 0.7f, 1.4f, bonus, Now - Day, Now, Dur, false, false, -1, true, true, true, Cap));
            need(c["consistent"] == "False", "base-for-every-cell reads consistent");
            // D: ash field switch off
            var d = P(probe(0.7f, "RM_FE_Ash_Deep", true, true, 0.7f, 1.4f, 0f, -1, Now, Dur, false, false, -1, true, false, true, Cap));
            need(d.ContainsKey("refused") && d["refused"].Contains("ashWaterFertilityEnabled"), "no refusal with the ash field off");
            need(d.ContainsKey("fertility") && d["watered"] == "False" && Math.Abs(F(d, "lift")) < 1e-4 && d["consistent"] == "n/a", "switch-off parts wrong");
            // E: mechanics gate off
            var e = P(probe(0.7f, "RM_FE_Ash_Deep", true, false, 0.7f, 1.4f, 0f, -1, Now, Dur, false, false, -1, true, true, false, Cap));
            need(e.ContainsKey("refused") && e["refused"].Contains("mechanics"), "no refusal with the gate off");
            // F: black rain on an open and a roofed cell
            var f1 = P(probe(1.4f, "RM_FE_Ash_Deep", true, true, 0.7f, 1.4f, 0f, -1, Now, Dur, true, false, Now + 9, true, true, true, Cap));
            var f2 = P(probe(0.7f, "RM_FE_Ash_Deep", true, false, 0.7f, 1.4f, 0f, -1, Now, Dur, true, true, Now + 9, true, true, true, Cap));
            need(f1["rainOnCell"] == "True" && f2["rainOnCell"] == "False" && f2["raining"] == "True", "rain on the cell ignores the roof");
            // G: the cap
            var g = P(probe(2f, "RM_FE_Ash_Deep", true, true, 0.7f, 1.9f, 0.5f, Now, Now, Dur, false, false, -1, true, true, true, Cap));
            need(Math.Abs(F(g, "expected") - 2f) < 1e-3, "cap not applied");
            return bad;
        }
        static int Main()
        {
            foreach (var (label, probe) in Variants.All)
            {
                var why = new List<string>();
                int bad;
                try { bad = Check(probe, why); } catch (Exception ex) { bad = 1; why.Add(ex.GetType().Name + " " + ex.Message); }
                Console.WriteLine("VARIANT " + label + " bad=" + bad + " | " + string.Join("; ", why));
            }
            return 0;
        }
    }
}
"""
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>disable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
    <TreatWarningsAsErrors>false</TreatWarningsAsErrors>
    <AssemblyName>AshProbe</AssemblyName>
  </PropertyGroup>
</Project>
"""


def static_checks():
    bad = []
    f = open(FIELD, encoding="utf-8").read()
    m = re.search(r"public static string ProbeCell\(IntVec3 c\)\s*\{(.*?)\n        \}", f, re.S)
    body = m.group(1) if m else ""
    call = body[body.find("RM_FireEcoKernel.ProbeLine("):] if "RM_FireEcoKernel.ProbeLine(" in body else ""
    if not call:
        bad.append("ProbeCell does not return RM_FireEcoKernel.ProbeLine")
    elif not call[len("RM_FireEcoKernel.ProbeLine("):].lstrip().startswith("m.fertilityGrid.FertilityAt(c)"):
        bad.append("ProbeCell does not hand ProbeLine the grid's fertility first")
    # The parts come from the cell too (blind challenge cycle 3: ProbeCell handing ProbeLine 0 for the bonus stayed green,
    # and the probe then read bonus=0 on a fresh scar while the grid's fertility carried it).
    for need in ("RM_PyrelandsSettings.ashWaterFertilityEnabled", "PyrelandsMechanicsGate.On", "c.Roofed(m)", "FertilityCap",
                 "comp?.BonusAt(c, now)", "comp.IsWatered(c, now)", "comp.burnTick[i]", "comp?.blackRainWateredUntil",
                 "RM_PyrelandsSettings.freshBurnDays"):
        if need not in call:
            bad.append("ProbeCell does not pass %s" % need)
    if not re.search(r"public static string ProbeRect\(string rect\)[\s\S]{0,900}ProbeCell\(", f):
        bad.append("no ProbeRect over ProbeCell (the leaf asks for a rectangle)")
    v = open(VALIDATION, encoding="utf-8").read()
    if 'method="ProbeCell"' not in v:
        bad.append("validation.py no longer reads ProbeCell")
    return bad


def main():
    failures = static_checks()
    text = open(KERNEL, encoding="utf-8").read().replace("\r\n", "\n")
    if "public static string ProbeLine(" not in text:
        print("FAIL: RM_FireEcoKernel has no ProbeLine (the probe is missing)")
        return 1
    variants = [("real", text)]
    for label, old, new in MUTANTS:
        n = text.count(old)
        if n != 1:
            failures.append("mutant %s: pattern matches %dx, it can no longer be planted" % (label, n))
            continue
        variants.append((label, text.replace(old, new)))
    os.makedirs(winbuild.BUILD_ROOT, exist_ok=True)
    work = tempfile.mkdtemp(prefix="AshProbe_", dir=winbuild.BUILD_ROOT)
    try:
        rows = []
        for i, (label, body) in enumerate(variants):
            ns = "RimMandrake.Pyrelands.V%d" % i
            with open(os.path.join(work, "K%d.cs" % i), "w", encoding="utf-8") as fh:
                fh.write(body.replace("namespace RimMandrake.Pyrelands", "namespace " + ns, 1))
            rows.append('("%s", (Probe)%s.RM_FireEcoKernel.ProbeLine)' % (label, ns))
        with open(os.path.join(work, "Variants.cs"), "w", encoding="utf-8") as fh:
            fh.write("namespace Harness { static class Variants { public static readonly (string, Probe)[] All = {\n%s\n}; } }\n" % ",\n".join(rows))
        for name, body in (("Harness.cs", HARNESS), ("t.csproj", CSPROJ)):
            with open(os.path.join(work, name), "w", encoding="utf-8") as fh:
                fh.write(body)
        win = winbuild.win(work)
        r = winbuild.run_interop_captured([winbuild.dotnet_exe(), "build", win + "\\t.csproj", "-c", "Release", "--nologo", "-v", "quiet"],
                                          cwd=work, capture_output=True, text=True, timeout=300)
        if r.returncode:
            print((r.stdout + r.stderr)[-3000:])
            print("FAIL: the kernel does not compile with the harness")
            return 1
        r = winbuild.run_interop_captured([winbuild.dotnet_exe(), win + "\\bin\\Release\\net8.0\\AshProbe.dll"],
                                          cwd=work, capture_output=True, text=True, timeout=120)
        out = r.stdout.replace("\r\n", "\n")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    results = dict((m[0], (int(m[1]), m[2])) for m in re.findall(r"^VARIANT (\w+) bad=(\d+) \| (.*)$", out, re.M))
    names = [v[0] for v in variants]
    if r.returncode or set(results) != set(names):
        print(out[-2000:], (r.stderr or "")[-1000:])
        print("FAIL: the harness did not report every variant")
        return 1
    print("real: %d bad | %s" % results["real"])
    if results["real"][0]:
        failures.append("the real ProbeLine misses the bar: " + results["real"][1])
    for name in names[1:]:
        print("mutant %-30s %s" % (name, "RED %d" % results[name][0] if results[name][0] else "SURVIVED"))
        if not results[name][0]:
            failures.append("mutant %s survived" % name)
    for f in failures:
        print("FAIL:", f)
    if failures:
        return 1
    print("PASS: the probe reads cells part by part and refuses with the ash field off; %d mutants red" % (len(names) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
