// DEEP_DRILL_HOME_BIOME_1 L0. Run: python3 src/RimMandrake/Utils/selftest_deepdrill.py
// Weighted picks over the 23 deepCommonality carriers of the 2026-10-19 def dump (steel and the table rows), filtered by the production kernel.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace RimMandrake.DeepDrill.SelfTest
{
    internal static class Program
    {
        static readonly Dictionary<string, double> Weights = new Dictionary<string, double> {
            {"Silver", 0.5},
            {"Gold", 0.5},
            {"Steel", 4},
            {"Plasteel", 1},
            {"Uranium", 1},
            {"Jade", 0.5},
            {"GLO_GlowstoneCluster", 0.1},
            {"BMT_AmberResource", 0.4},
            {"BMT_FossilResource", 0.8},
            {"DV_Pyrinth", 0.4},
            {"Diamond", 0.4},
            {"Ruby", 0.5},
            {"Sapphire", 0.5},
            {"VCE_Salt", 0.5},
            {"VHGE_Helixien", 1},
            {"VCHE_Deepchem", 2},
            {"OuterRim_Tibanna", 2},
            {"KOTOR_IngotCortosis", 0.75},
            {"KOTOR_RawRhydonium", 1},
            {"Gravitonium", 0.4},
            {"RM_LivePatternMetal", 4},
            {"RM_Lanternstone", 1},
            {"RSW_ResourceBlueCrystal", 1},
        };
        static int fails;
        static void Check(bool ok, string what) { if (!ok) { fails++; Console.WriteLine("FAIL " + what); } }

        static Dictionary<string, HashSet<string>> Load(string xml)
        {
            var d = new Dictionary<string, HashSet<string>>();
            foreach (var li in XDocument.Load(xml).Descendants("rows").First().Elements("li"))
                d[(string)li.Element("thing")] = new HashSet<string>(li.Element("homes").Elements("li").Select(x => (string)x));
            return d;
        }

        static string Pick(Random rng, string biome, Dictionary<string, HashSet<string>> homes, bool enabled)
        {
            double total = Weights.Values.Sum(), r = rng.NextDouble() * total;
            string picked = Weights.Keys.Last();
            foreach (var kv in Weights) { r -= kv.Value; if (r <= 0) { picked = kv.Key; break; } }
            return RM_DeepDrillKernel.ShouldReplace(enabled, picked, biome, homes) ? RM_DeepDrillKernel.FallbackDefName : picked;
        }

        // VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR: the ported resource mutators' decisions.
        static void TileResourceChecks()
        {
            var none = new RM_DeepOreKind[0];
            var rich = new[] { RM_DeepOreKind.None, RM_DeepOreKind.Rich };
            var devoid = new[] { RM_DeepOreKind.Devoid };
            var both = new[] { RM_DeepOreKind.Rich, RM_DeepOreKind.Devoid };
            float rf = RM_TileResourceKernel.DefaultRichFactor;
            Check(Math.Abs(rf - 1.25f) < 1e-6, "shipped rich factor is not VEE's 1.25");
            Check(RM_TileResourceKernel.DeepOreFactor(none, rf, true) == 1f, "ordinary tile factor != 1");
            Check(RM_TileResourceKernel.DeepOreFactor(rich, rf, true) == rf, "rich tile factor != rich setting");
            Check(RM_TileResourceKernel.DeepOreFactor(new[] { RM_DeepOreKind.Rich, RM_DeepOreKind.Rich }, rf, true) == rf, "two Rich stacked");
            Check(RM_TileResourceKernel.DeepOreFactor(devoid, rf, true) == 0f, "devoid tile factor != 0");
            Check(RM_TileResourceKernel.DeepOreFactor(both, rf, true) == 0f, "devoid does not win over rich");
            Check(RM_TileResourceKernel.DeepOreFactor(devoid, rf, false) == 1f && RM_TileResourceKernel.DeepOreFactor(rich, rf, false) == 1f, "setting off is not vanilla");
            Check(RM_TileResourceKernel.DeepOreFactor(null, rf, true) == 1f, "null mutators != 1");
            // Every vanilla-scale deepCountPerCell (1..200): rich gives round(1.25 n) >= n, never 0; factor 1 is identity.
            for (int n = 1; n <= 200; n++)
            {
                int r = RM_TileResourceKernel.ScaledCount(n, 1.25f);
                Check(r >= n && r >= 1 && Math.Abs(r - n * 1.25) <= 0.5, "rich count " + n + " -> " + r);
                Check(RM_TileResourceKernel.ScaledCount(n, 1f) == n, "factor 1 changed " + n);
                Check(RM_TileResourceKernel.ScaledCount(n, 0.01f) >= 1, "a tiny factor emptied a cell " + n);
            }
            Check(RM_TileResourceKernel.ScaledCount(60000, 2f) == 65535, "count escapes the grid's ushort");
            Check(RM_TileResourceKernel.ScaledCount(0, 1.25f) == 0, "an empty cell gained ore");
            Check(RM_TileResourceKernel.ScatterPer10k(10f, 0.05f, 1f) == 0.5f && RM_TileResourceKernel.ScatterPer10k(10f, 0.05f, 0f) == 0f, "scatter scale");
            var keep = new HashSet<string> { "ComponentIndustrial", "ComponentSpacer" };
            Check(RM_TileResourceKernel.StripsToPlainRock(true, 1f, "Steel", keep), "devoid keeps a steel vein");
            Check(RM_TileResourceKernel.StripsToPlainRock(true, 0.2f, "Gold", keep), "devoid keeps a gold vein");
            Check(!RM_TileResourceKernel.StripsToPlainRock(true, 1f, "ComponentIndustrial", keep), "devoid strips compacted machinery");
            Check(!RM_TileResourceKernel.StripsToPlainRock(true, 0f, "ComponentSpacer", keep), "devoid strips a scatter-only deposit");
            Check(!RM_TileResourceKernel.StripsToPlainRock(false, 0f, null, keep), "devoid strips plain rock");
        }

        private static int Main(string[] args)
        {
            string xml = args.Length > 0 ? args[0] : Path.Combine("..", "..", "Defs", "RM_DeepHomeTable.xml");
            var homes = Load(xml);
            Check(homes.Count >= 20, "table has " + homes.Count + " rows (expected >= 20)");
            Check(!homes.ContainsKey("Steel"), "Steel must not be in the table");
            foreach (var k in Weights.Keys) if (k != "Steel") Check(homes.ContainsKey(k), "carrier " + k + " has no row");
            var rng = new Random(12345);
            // A biome that is nobody's home: only steel, ever.
            var seen = new HashSet<string>();
            for (int i = 0; i < 20000; i++) seen.Add(Pick(rng, "RUT_AridShrubland", homes, true));
            Check(seen.Count == 1 && seen.Contains("Steel"), "non-home biome yielded: " + string.Join(",", seen));
            // Every home biome: steel plus exactly the deposits listing that biome; and each such deposit can be chosen.
            var biomes = homes.Values.SelectMany(x => x).Distinct().ToList();
            Check(biomes.Count >= 8, "only " + biomes.Count + " home biomes found");
            foreach (var b in biomes)
            {
                var expect = new HashSet<string>(homes.Where(kv => kv.Value.Contains(b) && Weights.ContainsKey(kv.Key)).Select(kv => kv.Key)) { "Steel" };
                var got = new HashSet<string>();
                for (int i = 0; i < 60000; i++) got.Add(Pick(rng, b, homes, true));
                Check(got.SetEquals(expect), b + ": got {" + string.Join(",", got.OrderBy(x => x)) + "} expected {" + string.Join(",", expect.OrderBy(x => x)) + "}");
            }
            // Setting off: vanilla, every carrier reachable on a plain biome.
            var all = new HashSet<string>();
            for (int i = 0; i < 200000; i++) all.Add(Pick(rng, "RUT_AridShrubland", homes, false));
            Check(all.Count == Weights.Count, "filter off reached " + all.Count + " of " + Weights.Count);
            // Edges: unlisted def and null biome pass through.
            Check(!RM_DeepDrillKernel.ShouldReplace(true, "SomethingElse", "X", homes), "unlisted def replaced");
            Check(!RM_DeepDrillKernel.ShouldReplace(true, "Gold", null, homes), "null biome replaced");
            Check(!RM_DeepDrillKernel.ShouldReplace(true, null, "X", homes), "null pick replaced");
            TileResourceChecks();
            Console.WriteLine(fails == 0 ? "DEEPDRILL SELFTEST PASS" : "DEEPDRILL SELFTEST FAILED " + fails);
            return fails == 0 ? 0 : 1;
        }
    }
}
