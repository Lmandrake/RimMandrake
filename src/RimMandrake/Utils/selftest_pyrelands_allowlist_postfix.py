#!/usr/bin/env python3
# selftest-timeout: 420
"""The Harmony Postfix of the Pyrelands wild-plant allowlist, run offline (ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES).

selftest_pyrelands_fuzz reaches the kernel ApplyWildAllowlist, never the Postfix that decides foreignOpenCell, so restoring
the bug in the Postfix stayed green. This test cuts the class Patch_EnforcePyrelandsWildPlantAllowlist out of the production
WildPlantAllowlist.cs as text, compiles that text with the production RM_FireEcoKernel.cs against small stub Verse types, and
calls the real Postfix over an exhaustive table: every combination of gate, setting, map biome, cell biome, cave flag,
candidate list and grass fitness, against a spec written here and nowhere else. A throwing grass check must be swallowed.

The instrument proves it can see: the same text is compiled again with one planted defect per namespace (MUTANTS, including
the bug itself), and each must fail the table. A mutant whose pattern no longer matches once fails the test, so it cannot
rot into a silent skip. The hook wiring and signature, which the stubs cannot run, and the allowlist's agreement with
Pyrelands.xml <wildPlants> are read from the production files.

    python3 src/RimMandrake/Utils/selftest_pyrelands_allowlist_postfix.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

PYR = os.path.join(os.path.dirname(HERE), "Pyrelands")
SOURCE = os.path.join(PYR, "Source", "WildPlantAllowlist.cs")
KERNEL = os.path.join(PYR, "Source", "Kernel", "RM_FireEcoKernel.cs")
BIOME = os.path.join(PYR, "Defs", "BiomeDefs", "Pyrelands.xml")
CLASS = "public static class Patch_EnforcePyrelandsWildPlantAllowlist"
SIGNATURE = "public static void Postfix(IntVec3 c, List<ThingDef> outPlants, bool cavePlants, Map ___map)"
FOREIGN = "!cavePlants && map.BiomeAt(c) != map.Biome"

# (label, exact text in the class, replacement)
MUTANTS = [
    ("never_supply_the_bug_itself", FOREIGN + ")", "false)"),
    ("always_supply", FOREIGN + ")", "true)"),
    ("cave_cells_supplied", FOREIGN, "map.BiomeAt(c) != map.Biome"),
    ("native_cells_supplied", FOREIGN, "!cavePlants"),
    ("foreign_test_inverted", "map.BiomeAt(c) != map.Biome", "map.BiomeAt(c) == map.Biome"),
    ("fitness_ignored", "d => d.CanEverPlantAt(c, map)", "d => true"),
    ("fitness_asked_of_wrong_cell", "d.CanEverPlantAt(c, map)", "d.CanEverPlantAt(IntVec3.Zero, map)"),
    ("allowlist_ignored", "d => Allowlist.Contains(d.defName)", "d => true"),
    ("gate_ignored", "!PyrelandsMechanicsGate.On || ", ""),
    ("setting_ignored", " || !RM_PyrelandsSettings.wildPlantAllowlistEnabled", ""),
    ("any_biome_enforced", "if (___map.Biome == null || ___map.Biome.defName != PyrelandsDefName) return;", ""),
    ("biome_name_wrong", '"RM_Pyrelands"', '"Pyrelands"'),
    ("null_list_not_guarded", "___map == null || outPlants == null", "___map == null"),
    ("exception_escapes", "catch (Exception e)", "catch (DivideByZeroException e)"),
    ("native_grass_dropped", '            "RM_FE_Plant_Quickgrass",\n', ""),
]

STUBS = r"""
namespace HarmonyLib { public static class Stub { } }
namespace Verse
{
    public struct IntVec3 : System.IEquatable<IntVec3>
    {
        public int x, z;
        public IntVec3(int x, int z) { this.x = x; this.z = z; }
        public static IntVec3 Zero => new IntVec3(0, 0);
        public bool Equals(IntVec3 o) => x == o.x && z == o.z;
        public override bool Equals(object o) => o is IntVec3 v && Equals(v);
        public override int GetHashCode() => x * 397 ^ z;
    }
    public class BiomeDef { public string defName; }
    public class Map
    {
        public BiomeDef Biome;
        public System.Func<IntVec3, BiomeDef> Cell;
        public BiomeDef BiomeAt(IntVec3 c) => Cell(c);
    }
    public class ThingDef
    {
        public string defName;
        public System.Func<IntVec3, Map, bool> Fit = (c, m) => true;
        public bool CanEverPlantAt(IntVec3 c, Map m) => Fit(c, m);
    }
    public static class DefDatabase<T> where T : class
    {
        public static System.Func<string, T> Named;
        public static T GetNamedSilentFail(string n) => Named(n);
    }
    public static class Log
    {
        public static int Warnings;
        public static void WarningOnce(string text, int key) { Warnings++; }
    }
}
namespace RimWorld { public static class Stub { } }
namespace RimMandrake.Pyrelands
{
    public static class PyrelandsMechanicsGate { public static bool On = true; }
    public static class RM_PyrelandsSettings { public static bool wildPlantAllowlistEnabled = true; }
}
"""

HARNESS = r"""
namespace RimMandrake.Pyrelands.Harness
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using Verse;

    delegate void Hook(IntVec3 c, List<ThingDef> outPlants, bool cavePlants, Map map);

    static class Table
    {
        static readonly ThingDef Ember = new ThingDef { defName = "RM_FE_Plant_EmberGrass" };
        static readonly ThingDef Quick = new ThingDef { defName = "RM_FE_Plant_Quickgrass" };
        static readonly ThingDef Oak = new ThingDef { defName = "Plant_TreeOak" };
        static readonly ThingDef Berry = new ThingDef { defName = "Plant_Berry" };
        static readonly BiomeDef Pyre = new BiomeDef { defName = "RM_Pyrelands" };
        static readonly BiomeDef Forest = new BiomeDef { defName = "TemperateForest" };
        static readonly IntVec3 Here = new IntVec3(5, 7);

        // the spec: gate, setting and map biome decide whether anything happens; then off-list plants go; then a foreign open
        // cell gains every allowlisted grass that fits this cell. Nothing else is ever added or lost.
        static List<ThingDef> Spec(bool gate, bool setting, BiomeDef mapBiome, BiomeDef cellBiome, bool cave, List<ThingDef> cand, bool emberFits, bool quickFits)
        {
            if (!gate || !setting || mapBiome != Pyre) return new List<ThingDef>(cand);
            var o = cand.Where(d => d == Ember || d == Quick).ToList();
            if (!cave && cellBiome != mapBiome)
            {
                if (emberFits && !o.Contains(Ember)) o.Add(Ember);
                if (quickFits && !o.Contains(Quick)) o.Add(Quick);
            }
            return o;
        }

        public static int Run(Hook hook, out string first)
        {
            DefDatabase<ThingDef>.Named = n => n == Ember.defName ? Ember : n == Quick.defName ? Quick : null;
            int bad = 0, cases = 0, supplied = 0;
            string f = null;
            void Bad(string why) { bad++; f = f ?? why; }
            var bools = new[] { true, false };
            foreach (bool gate in bools) foreach (bool setting in bools)
            foreach (var mapBiome in new[] { Pyre, Forest }) foreach (var cellBiome in new[] { Pyre, Forest })
            foreach (bool cave in bools) foreach (bool emberFits in bools) foreach (bool quickFits in bools)
            for (int mask = 0; mask < 16; mask++)
            {
                cases++;
                var cand = new List<ThingDef>();
                if ((mask & 1) != 0) cand.Add(Oak);
                if ((mask & 2) != 0) cand.Add(Berry);
                if ((mask & 4) != 0) cand.Add(Ember);
                if ((mask & 8) != 0) cand.Add(Quick);
                PyrelandsMechanicsGate.On = gate;
                RM_PyrelandsSettings.wildPlantAllowlistEnabled = setting;
                // a grass fits only as told, and only at THIS cell on THIS map: Zero and any other map read the opposite
                var map = new Map { Biome = mapBiome, Cell = c => c.Equals(Here) ? cellBiome : mapBiome };
                Ember.Fit = (c, m) => c.Equals(Here) && m == map ? emberFits : !emberFits;
                Quick.Fit = (c, m) => c.Equals(Here) && m == map ? quickFits : !quickFits;
                var want = Spec(gate, setting, mapBiome, cellBiome, cave, cand, emberFits, quickFits);
                var got = new List<ThingDef>(cand);
                string label = $"gate={gate} setting={setting} map={mapBiome.defName} cell={cellBiome.defName} cave={cave} ember={emberFits} quick={quickFits} mask={mask}";
                try { hook(Here, got, cave, map); }
                catch (Exception e) { Bad(label + " threw " + e.GetType().Name); continue; }
                if (want.Count > cand.Count(d => d == Ember || d == Quick)) supplied++;
                if (got.Count != want.Count || want.Except(got).Any())
                    Bad(label + " want [" + string.Join(",", want.Select(d => d.defName)) + "] got [" + string.Join(",", got.Select(d => d.defName)) + "]");
            }
            PyrelandsMechanicsGate.On = true;
            RM_PyrelandsSettings.wildPlantAllowlistEnabled = true;
            if (supplied == 0) Bad("the table never asked for a supply (sanity probe)");

            // the guards: a null map or list is not a crash, and a throwing fitness check stays inside the postfix
            var once = new Map { Biome = Pyre, Cell = c => Forest };
            Ember.Fit = Quick.Fit = (c, m) => true;
            var kept = new List<ThingDef> { Oak };
            try { hook(Here, kept, false, null); if (kept.Count != 1) Bad("a null map changed the list"); }
            catch (Exception e) { Bad("null map threw " + e.GetType().Name); }
            int warned = Log.Warnings;
            try { hook(Here, null, false, once); if (Log.Warnings != warned) Bad("a null list reached the kernel"); }
            catch (Exception e) { Bad("null list threw " + e.GetType().Name); }
            Ember.Fit = (c, m) => { throw new InvalidOperationException("fitness"); };
            warned = Log.Warnings;
            try { hook(Here, new List<ThingDef>(), false, once); if (Log.Warnings != warned + 1) Bad("a throwing grass check was not logged"); }
            catch (Exception e) { Bad("a throwing grass check escaped: " + e.GetType().Name); }
            first = f;
            Console.WriteLine("  cases " + cases + ", supplied " + supplied);
            return bad;
        }
    }

    static class Program
    {
        static int Main()
        {
            foreach (var (name, hook) in Variants.All)
            {
                int bad = Table.Run(hook, out string first);
                Console.WriteLine("VARIANT " + name + " bad=" + bad + " | " + first);
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
    <AssemblyName>AllowlistPostfix</AssemblyName>
  </PropertyGroup>
</Project>
"""


def cut_class(text):
    """The class's full text. Braces inside comments, strings and chars do not count."""
    start = text.index(CLASS)
    i, depth, opened = start, 0, False
    while i < len(text):
        two = text[i:i + 2]
        if two == "//":
            i = text.index("\n", i)
        elif two == "/*":
            i = text.index("*/", i) + 2
        elif text[i] in "\"'":
            q, i = text[i], i + 1
            while text[i] != q:
                i += 2 if text[i] == "\\" else 1
            i += 1
        else:
            if text[i] == "{":
                depth, opened = depth + 1, True
            elif text[i] == "}":
                depth -= 1
                if opened and depth == 0:
                    return text[start:i + 1]
            i += 1
    raise SystemExit("FAIL: the class has no end")


def static_checks(text, cls):
    """-> failures in what the stubs cannot run."""
    bad = []
    if SIGNATURE not in cls:
        bad.append("the Postfix signature moved; Harmony injects these names: " + SIGNATURE)
    if not re.search(r'AccessTools\.Method\(typeof\(WildPlantSpawner\), "CalculatePlantsWhichCanGrowAt"\)', text):
        bad.append("the hook no longer targets WildPlantSpawner.CalculatePlantsWhichCanGrowAt")
    if not re.search(r'h\.Patch\(target, postfix: new HarmonyMethod\(typeof\(Patch_EnforcePyrelandsWildPlantAllowlist\), "Postfix"\)\)', text):
        bad.append("the Postfix is not patched onto the target")
    if not re.search(r"\[StaticConstructorOnStartup\]\s*public static class WildPlantAllowlistHookMod", text):
        bad.append("the hook class no longer runs at startup")
    body = cls[cls.index("Allowlist = new HashSet<string>"):]
    listed = set(re.findall(r'"(\w+)"', body[:body.index("};")]))
    root = ET.parse(BIOME).getroot()
    biome = [d for d in root if d.findtext("defName") == "RM_Pyrelands"]
    wild = {e.tag for e in biome[0].find("wildPlants")} if len(biome) == 1 else set()
    if not wild:
        bad.append("Pyrelands.xml gives no wildPlants (sanity probe)")
    if listed != wild:
        bad.append("Allowlist %s differs from Pyrelands.xml wildPlants %s" % (sorted(listed), sorted(wild)))
    return bad


def build_source(text, cls):
    usings = "".join(l + "\n" for l in text.splitlines() if re.match(r"using [\w.]+;$", l))
    variants = [("real", cls)]
    bad = []
    for label, old, new in MUTANTS:
        n = cls.count(old)
        if n != 1:
            bad.append("mutant %s: pattern matches %dx, it can no longer be planted" % (label, n))
            continue
        variants.append((label, cls.replace(old, new)))
    src = [usings]
    for i, (label, body) in enumerate(variants):
        src.append("namespace RimMandrake.Pyrelands.V%d {\n%s\n}\n" % (i, body))
    rows = ",\n".join('("%s", (c, l, cave, m) => RimMandrake.Pyrelands.V%d.Patch_EnforcePyrelandsWildPlantAllowlist.Postfix(c, l, cave, m))' % (label, i)
                      for i, (label, _) in enumerate(variants))
    src.append("namespace RimMandrake.Pyrelands.Harness { static class Variants { public static readonly (string, Hook)[] All = {\n%s\n}; } }\n" % rows)
    return "".join(src), [v[0] for v in variants], bad


def main():
    text = open(SOURCE, encoding="utf-8").read().replace("\r\n", "\n")
    cls = cut_class(text)
    failures = static_checks(text, cls)
    source, names, bad = build_source(text, cls)
    failures += bad
    os.makedirs(winbuild.BUILD_ROOT, exist_ok=True)
    work = tempfile.mkdtemp(prefix="AllowlistPostfix_", dir=winbuild.BUILD_ROOT)
    try:
        for name, body in (("Stubs.cs", STUBS), ("Harness.cs", HARNESS), ("Variants.cs", source), ("t.csproj", CSPROJ)):
            with open(os.path.join(work, name), "w", encoding="utf-8") as f:
                f.write(body)
        shutil.copy(KERNEL, work)
        win = winbuild.win(work)
        r = subprocess.run([winbuild.dotnet_exe(), "build", win + "\\t.csproj", "-c", "Release", "--nologo", "-v", "quiet"],
                           cwd=work, capture_output=True, text=True, timeout=300)
        if r.returncode:
            print((r.stdout + r.stderr)[-3000:])
            print("FAIL: the Postfix text does not compile against the stubs")
            return 1
        r = subprocess.run([winbuild.dotnet_exe(), win + "\\bin\\Release\\net8.0\\AllowlistPostfix.dll"],
                           cwd=work, capture_output=True, text=True, timeout=120)
        out = r.stdout.replace("\r\n", "\n")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    results = dict((m[0], (int(m[1]), m[2])) for m in re.findall(r"^VARIANT (\w+) bad=(\d+) \| (.*)$", out, re.M))
    if r.returncode or set(results) != set(names):
        print(out[-2000:], r.stderr[-1000:])
        print("FAIL: the harness did not report every variant")
        return 1
    print("real: %d bad | %s" % results["real"])
    if results["real"][0]:
        failures.append("the real Postfix misses the spec: " + results["real"][1])
    for name in names[1:]:
        print("mutant %-30s %s" % (name, "RED %d" % results[name][0] if results[name][0] else "SURVIVED"))
        if not results[name][0]:
            failures.append("mutant %s survived: the table cannot see that clause" % name)
    for f in failures:
        print("FAIL:", f)
    if failures:
        return 1
    print("PASS: the real Postfix meets the spec, %d mutants red" % (len(names) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
