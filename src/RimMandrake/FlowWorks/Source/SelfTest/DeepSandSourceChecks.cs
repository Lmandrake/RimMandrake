// DEEP_SAND_FIX_READS_AS_FRESHWATER, source half (bundle WB-mod-FlowWorks-20261128-020147, item
// RIMMANDRAKE_MEND_FLOWWORKS_LIQUID_RULES_FIVE_OLD_DEFECTS). RM_DeepSand carries vanilla's "Water" tag so that a fishing
// zone forms on it, and TerrainDef.IsWater is HasTag("Water"). FlowWorks' one natural-liquid read
// (RM_MapComponent_Excavation.IsNaturalLiquid) took IsWater alone, so a deep sand square read as a natural water source
// (IsSourceCell), a SUPERDEEP lake square (DepthAt), a pond body square (IsWaterNow, read by RM_LiquidStock) and a square
// that liquid may enter: a pit dug beside deep sand filled with free fresh water. The rule: a terrain that carries the
// RM_NotLiquidExtension marker holds no liquid, whatever its tags. These checks read the wiring, the marker on deep sand,
// and that no real liquid terrain carries the marker (a marker on water would dry every lake).
using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DeepSandSourceChecks
    {
        private const string Marker = "RimMandrake.FlowWorks.ManyWaters.RM_NotLiquidExtension";

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string ModRoot => Path.GetFullPath(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")), ".."));

        private static bool HasMarker(XElement terrain) =>
            terrain.Element("modExtensions")?.Elements("li").Any(li => (string)li.Attribute("Class") == Marker) == true;

        private static bool HasWaterTag(XElement terrain) =>
            terrain.Element("tags")?.Elements("li").Any(li => li.Value.Trim() == "Water") == true;

        public static void Run(Action<string, Action> Case)
        {
            Case("deep sand holds no liquid: IsNaturalLiquid refuses a terrain marked RM_NotLiquidExtension", () =>
            {
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                Match m = Regex.Match(ex, @"private bool IsNaturalLiquid\(IntVec3 c\) \{(.*?)\} /// <summary>A cell that supplies liquid");
                Assert(m.Success, "IsNaturalLiquid(IntVec3) found, followed by IsSourceCell's summary");
                string body = m.Groups[1].Value;
                Assert(Regex.IsMatch(body, @"return baseTerrain != null && baseTerrain\.IsWater && !baseTerrain\.HasModExtension<(ManyWaters\.)?RM_NotLiquidExtension>\(\);"),
                    "IsNaturalLiquid returns IsWater AND NOT the RM_NotLiquidExtension marker (deep sand's Water tag is for fishing); body: " + body);
                RiverSwitchFlipChecks.Has(ex, @"public bool IsSourceCell\(IntVec3 c\) \{ if \(!c\.InBounds\(map\)\) \{ return false; \} return depthGrid\[map\.cellIndices\.CellToIndex\(c\)\] == 0 && IsNaturalLiquid\(c\); \}",
                    "IsSourceCell reads the one adapter, so the marker reaches the supply");
                RiverSwitchFlipChecks.Has(ex, @"public bool IsWaterNow\(IntVec3 c\) \{ return IsNaturalLiquid\(c\); \}",
                    "IsWaterNow (RM_LiquidStock's pond read) reads the one adapter, so deep sand forms no pond body");
                RiverSwitchFlipChecks.Has(ex, @"bool RM_IFlowWorld\.IsNaturalLiquid\(int idx\) \{ return IsNaturalLiquid\(map\.cellIndices\.IndexToCell\(idx\)\); \}",
                    "the flow kernel's natural-liquid read goes through the one adapter");
            });

            Case("deep sand holds no liquid: the marker class exists and the mod build compiles it", () =>
            {
                string cls = Path.Combine(ModRoot, "Source", "ManyWaters", "RM_NotLiquidExtension.cs");
                Assert(File.Exists(cls), "Source/ManyWaters/RM_NotLiquidExtension.cs exists");
                string src = RiverSwitchFlipChecks.Flat(File.ReadAllText(cls));
                Assert(Regex.IsMatch(src, @"namespace RimMandrake\.FlowWorks\.ManyWaters \{.*public class RM_NotLiquidExtension : DefModExtension"),
                    "RM_NotLiquidExtension is a DefModExtension in RimMandrake.FlowWorks.ManyWaters (the XML Class names that namespace)");
                string proj = File.ReadAllText(Path.Combine(ModRoot, "Source", "RimMandrake_FlowWorks.csproj"));
                Assert(proj.Contains(@"<Compile Include=""ManyWaters\RM_NotLiquidExtension.cs"" />"),
                    "RimMandrake_FlowWorks.csproj compiles ManyWaters\\RM_NotLiquidExtension.cs (EnableDefaultCompileItems is false)");
            });

            Case("deep sand holds no liquid: RM_DeepSand carries the marker and keeps its Water tag; no liquid terrain carries it", () =>
            {
                XDocument sand = XDocument.Load(Path.Combine(ModRoot, "Defs", "ManyWaters", "TerrainDefs", "RM_DeepSand.xml"));
                XElement deep = sand.Root.Elements("TerrainDef").Single(t => (string)t.Element("defName") == "RM_DeepSand");
                Assert(HasWaterTag(deep), "RM_DeepSand keeps the Water tag (fishing reads it)");
                Assert(HasMarker(deep), "RM_DeepSand carries " + Marker);

                int read = 0, waterTagged = 0;
                string defs = Path.Combine(ModRoot, "Defs");
                foreach (string f in Directory.EnumerateFiles(defs, "*.xml", SearchOption.AllDirectories))
                {
                    XDocument d;
                    try { d = XDocument.Load(f); } catch { continue; }
                    foreach (XElement t in d.Root.Elements("TerrainDef"))
                    {
                        read++;
                        string name = (string)t.Element("defName") ?? (string)t.Attribute("Name") ?? "?";
                        if (name == "RM_DeepSand") continue;
                        if (HasWaterTag(t)) waterTagged++;
                        Assert(!HasMarker(t), "only deep sand is marked: " + name + " in " + Path.GetFileName(f) + " carries " + Marker);
                    }
                }
                Assert(read > 20, "the walk read FlowWorks' TerrainDefs (read " + read + ")");
                Assert(waterTagged > 0, "the walk saw Water-tagged liquid terrains it left unmarked (saw " + waterTagged + ")");
                foreach (string f in Directory.EnumerateFiles(Path.Combine(ModRoot, "Patches"), "*.xml", SearchOption.AllDirectories))
                {
                    Assert(!File.ReadAllText(f).Contains("RM_NotLiquidExtension"), "no patch adds the marker: " + Path.GetFileName(f));
                }
                Console.WriteLine("    deep sand marker: " + read + " TerrainDefs read, " + waterTagged + " other Water-tagged left unmarked");
            });
        }
    }
}
