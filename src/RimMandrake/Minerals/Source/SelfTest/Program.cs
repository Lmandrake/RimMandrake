// MINERAL_POLICY_CODE_STARTUP_ZEROING L0. Run: python3 src/RimMandrake/Utils/selftest_minerals.py
// The production kernel over the shipped registry XML, DeepDrill's shipped home table and the def-dump fixture (real weights).
// args: <RM_MineralRegistry.xml> <RM_DeepHomeTable.xml> <mineral_defs.tsv>
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace RimMandrake.Minerals.SelfTest
{
    internal static class Program
    {
        static int fails, checks;
        static void Check(bool ok, string what) { checks++; if (!ok) { fails++; Console.WriteLine("FAIL " + what); } }
        static float F(string s) { return float.Parse(s, NumberStyles.Float, CultureInfo.InvariantCulture); }

        static IEnumerable<string> Lis(XElement def, string tag)
        {
            XElement e = def.Element(tag);
            return e == null ? Enumerable.Empty<string>() : e.Elements("li").Select(x => ((string)x).Trim());
        }

        // Mirrors RM_MineralRegistryDef.ToRow with every MayRequire mod present.
        static List<MineralRow> LoadRows(string xml, out List<string> units)
        {
            var rows = new List<MineralRow>();
            units = new List<string>();
            foreach (XElement d in XDocument.Load(xml).Root.Elements("RimMandrake.Minerals.RM_MineralRegistryDef"))
            {
                var r = new MineralRow
                {
                    MaterialId = (string)d.Element("materialId"),
                    Unit = (string)d.Element("unit"),
                    UnitsPerCellOrFind = d.Element("unitsPerCellOrFind") != null ? F((string)d.Element("unitsPerCellOrFind")) : 0f,
                    DeepWeight = d.Element("deepWeight") != null ? F((string)d.Element("deepWeight")) : 0f,
                    OtherBiomes = d.Element("otherBiomes") != null ? F((string)d.Element("otherBiomes")) : 0f,
                };
                units.Add(r.Unit);
                foreach (string n in Lis(d, "items")) r.Items.Add(n);
                foreach (string n in Lis(d, "mineables")) r.Mineables.Add(n);
                foreach (string n in Lis(d, "producers")) r.Producers.Add(n);
                foreach (string n in Lis(d, "zeroProducers")) r.ZeroProducers.Add(n);
                foreach (string n in Lis(d, "retiredItems")) r.RetiredItems.Add(n);
                XElement b = d.Element("biomes");
                if (b != null)
                    foreach (XElement c in b.Elements("li"))
                    {
                        string biome = (string)c.Element("biome");
                        if (c.Element("token") != null) r.Tokens[biome] = (string)c.Element("token");
                        else r.Cells[biome] = F((string)c.Element("value"));
                    }
                rows.Add(r);
            }
            return rows;
        }

        static Dictionary<string, HashSet<string>> LoadDeep(string xml)
        {
            var d = new Dictionary<string, HashSet<string>>();
            foreach (var li in XDocument.Load(xml).Descendants("rows").First().Elements("li"))
                d[(string)li.Element("thing")] = new HashSet<string>(li.Element("homes").Elements("li").Select(x => (string)x));
            return d;
        }

        static List<MineralDefInfo> LoadFixture(string tsv)
        {
            var list = new List<MineralDefInfo>();
            foreach (string line in File.ReadAllLines(tsv))
            {
                if (line.StartsWith("#") || line.Trim().Length == 0) continue;
                string[] p = line.Split('\t');
                list.Add(new MineralDefInfo(p[0], F(p[1]), F(p[2]), p[3].Length > 0 ? p[3] : null, p[4] == "1"));
            }
            return list;
        }

        static Dictionary<string, PolicyDecision> ByName(List<PolicyDecision> l) { return l.ToDictionary(p => p.DefName); }
        static List<MineralDefInfo> Clone(List<MineralDefInfo> l) { return l.Select(RM_MineralPolicyKernel.Copy).ToList(); }

        static int Main(string[] args)
        {
            List<MineralRow> rows = LoadRows(args[0], out List<string> units);
            Dictionary<string, HashSet<string>> deep = LoadDeep(args[1]);
            List<MineralDefInfo> defs = LoadFixture(args[2]);
            var orig = defs.ToDictionary(d => d.DefName);

            // --- sanity: the instruments can see
            Check(rows.Count >= 20, "registry parsed only " + rows.Count + " rows");
            Check(defs.Count >= 50, "fixture has only " + defs.Count + " defs");
            Check(orig.ContainsKey("MineableSteel") && orig["MineableSteel"].Scatter > 0f && orig.ContainsKey("Steel") && orig["Steel"].Deep > 0f,
                  "fixture cannot see MineableSteel scatter / Steel deep");
            Check(deep.Count >= 10, "DeepDrill table parsed only " + deep.Count + " rows");

            // --- registry shape
            var ids = rows.Select(r => r.MaterialId).ToList();
            Check(ids.Count == ids.Distinct().Count(), "duplicate materialId");
            string[] known = { "EPM", "EPM/yr", "UPY", "deep share", "—" };
            foreach (string u in units) Check(Array.IndexOf(known, u) >= 0, "unknown unit " + u);

            var zeroNames = new HashSet<string>(rows.SelectMany(r => r.ZeroProducers.Concat(r.RetiredItems)));
            var opts = new PolicyOptions();

            // --- master off: every target is the original
            List<PolicyDecision> off = RM_MineralPolicyKernel.Decide(rows, Clone(defs), new PolicyOptions { Enabled = false });
            Check(off.Count >= defs.Count(RM_MineralPolicyKernel.Bearing), "master off decided fewer defs than are bearing");
            foreach (PolicyDecision p in off)
                Check(p.Scatter == orig[p.DefName].Scatter && p.Deep == orig[p.DefName].Deep, "master off changed " + p.DefName);

            // --- default policy
            Dictionary<string, PolicyDecision> on = ByName(RM_MineralPolicyKernel.Decide(rows, Clone(defs), opts));
            // owner 2026-09-25: "fix that absurd thing in Vanilla where components and plasteel can be mined from rock"
            foreach (string n in new[] { "MineableComponentsIndustrial", "MineablePlasteel" })
                Check(on.ContainsKey(n) && on[n].Scatter == 0f, n + " must have zero scatter, got " + (on.ContainsKey(n) ? on[n].Scatter.ToString() : "no decision"));
            // safety: steel's row is not emitted (GUESS), so steel is unregistered and must keep vanilla weights by default
            Check(on["MineableSteel"].Unregistered && on["MineableSteel"].Scatter == 1f, "MineableSteel must stay vanilla while its row is unemitted");
            Check(on["Steel"].Deep == 4f, "Steel deep weight must stay 4");
            foreach (PolicyDecision p in on.Values)
            {
                MineralDefInfo o = orig[p.DefName];
                if (zeroNames.Contains(p.DefName)) Check(p.Scatter == 0f && p.Deep == 0f, p.DefName + " is zero/retire but kept weight");
                if (p.Unregistered) Check(p.Scatter == o.Scatter && p.Deep == o.Deep, "unregistered " + p.DefName + " changed with suppression off");
                Check(p.Scatter <= o.Scatter && p.Deep <= o.Deep, p.DefName + " weight raised (the policy only zeroes)");
            }
            Console.WriteLine("zeroed by default: " + string.Join(", ", on.Values.Where(p => (orig[p.DefName].Scatter > 0f && p.Scatter == 0f)
                || (orig[p.DefName].Deep > 0f && p.Deep == 0f)).Select(p => p.DefName + "[" + p.MaterialId + "]")));
            int unregCount = on.Values.Count(p => p.Unregistered);
            Check(unregCount > 0, "no unregistered defs at all: the governed/unregistered split is blind");

            // --- deep channel agrees with DeepDrill's generated home table (both come from the same CSV)
            int deepChecked = 0;
            foreach (MineralRow r in rows)
                foreach (string item in r.Items)
                {
                    if (item == "Steel" || !deep.TryGetValue(item, out HashSet<string> homes)) continue;
                    deepChecked++;
                    Check(r.HasDeepHome == (homes.Count > 0), item + ": kernel HasDeepHome=" + r.HasDeepHome + " but DeepDrill homes=" + homes.Count);
                    if (on.TryGetValue(item, out PolicyDecision p) && orig[item].Deep > 0f)
                        Check((p.Deep > 0f) == (homes.Count > 0), item + ": deep target " + p.Deep + " disagrees with DeepDrill homes " + homes.Count);
                }
            Check(deepChecked >= 5, "only " + deepChecked + " registry items found in the DeepDrill table");

            // --- suppression on: unregistered zeroed, governed unchanged
            Dictionary<string, PolicyDecision> sup = ByName(RM_MineralPolicyKernel.Decide(rows, Clone(defs), new PolicyOptions { SuppressUnregistered = true }));
            foreach (PolicyDecision p in sup.Values)
            {
                if (p.Unregistered) Check(p.Scatter == 0f && p.Deep == 0f, "suppression on kept " + p.DefName);
                else Check(p.Scatter == on[p.DefName].Scatter && p.Deep == on[p.DefName].Deep, "suppression changed governed " + p.DefName);
            }

            // --- surface placer active: every governed mineable with scatter is zeroed (the placer scatters it instead)
            Dictionary<string, PolicyDecision> placed = ByName(RM_MineralPolicyKernel.Decide(rows, Clone(defs), new PolicyOptions { SurfacePlacerActive = true }));
            int keptBefore = 0;
            foreach (PolicyDecision p in placed.Values)
            {
                if (p.Unregistered || !orig[p.DefName].IsBuilding) continue;
                Check(p.Scatter == 0f, "placer active but governed " + p.DefName + " keeps scatter " + p.Scatter);
                if (on[p.DefName].Scatter > 0f) keptBefore++;
            }
            Console.WriteLine("governed veins kept until R3: " + keptBefore + "; unregistered: " + unregCount);

            // --- idempotence: the decision from the written values' originals is the same
            List<PolicyDecision> again = RM_MineralPolicyKernel.Decide(rows, Clone(defs), opts);
            Check(again.Select(p => p.DefName + p.Scatter + "/" + p.Deep).SequenceEqual(on.Values.OrderBy(p => p.DefName, StringComparer.Ordinal).Select(p => p.DefName + p.Scatter + "/" + p.Deep)),
                  "Decide is not deterministic");

            // --- re-assert: another mod writes after us -> adopted, and master off returns ITS value
            var originals = Clone(defs).ToDictionary(d => d.DefName);
            var last = on.Values.ToDictionary(p => p.DefName, p => new[] { p.Scatter, p.Deep });
            var current = on.Values.Select(p => new MineralDefInfo(p.DefName, p.Scatter, p.Deep, orig[p.DefName].MinedItem, orig[p.DefName].IsBuilding)).ToList();
            Check(RM_MineralPolicyKernel.Readopt(originals, last, current).Count == 0, "re-assert with nothing changed adopted something");
            current.First(c => c.DefName == "MineableGold").Scatter = 0.5f;
            current.Add(new MineralDefInfo("XX_NewOre", 0.3f, 0f, "XX_Item", true));
            List<string> adopted = RM_MineralPolicyKernel.Readopt(originals, last, current);
            Check(adopted.Contains("MineableGold") && adopted.Contains("XX_NewOre") && adopted.Count == 2, "re-assert adopted " + string.Join(",", adopted));
            var offAfter = ByName(RM_MineralPolicyKernel.Decide(rows, originals.Values.ToList(), new PolicyOptions { Enabled = false }));
            Check(offAfter["MineableGold"].Scatter == 0.5f, "master off after re-assert must restore the other mod's 0.5");
            Check(offAfter["XX_NewOre"].Unregistered, "a new unknown ore is unregistered");

            // --- synthetic: zero beats item; inferred governance through the mined item; retired yield
            var a = new MineralRow { MaterialId = "a", DeepWeight = 1f }; a.Items.Add("A"); a.Cells["RM_X"] = 100f;
            var z = new MineralRow { MaterialId = "z" }; z.ZeroProducers.Add("A"); z.RetiredItems.Add("R");
            var syn = ByName(RM_MineralPolicyKernel.Decide(new List<MineralRow> { a, z }, new List<MineralDefInfo> {
                new MineralDefInfo("A", 0f, 2f, null, false),
                new MineralDefInfo("MineableA", 0.4f, 0f, "A", true),
                new MineralDefInfo("MineableR", 0.4f, 0f, "R", true) }, opts));
            Check(syn["A"].Deep == 0f && syn["A"].MaterialId == "z", "zero role must beat item role");
            Check(syn["MineableA"].MaterialId == "a" && syn["MineableA"].Scatter == 0.4f, "mineable yielding a governed item is governed (kept until R3)");
            Check(syn["MineableR"].Scatter == 0f, "mineable yielding a retired item is zeroed");
            var noSurf = new MineralRow { MaterialId = "d", DeepWeight = 1f }; noSurf.Items.Add("D"); noSurf.Tokens["RM_X"] = "deep-only";
            var syn2 = ByName(RM_MineralPolicyKernel.Decide(new List<MineralRow> { noSurf }, new List<MineralDefInfo> {
                new MineralDefInfo("D", 0f, 1f, null, false), new MineralDefInfo("MineableD", 0.2f, 0f, "D", true) }, opts));
            Check(syn2["D"].Deep == 1f && syn2["MineableD"].Scatter == 0f, "deep-only: deep kept, surface zeroed");

            // --- effective values
            MineralRow num = rows.FirstOrDefault(r => r.Cells.Any(kv => kv.Key.StartsWith("RM_") && kv.Value > 0f));
            Check(num != null, "no row with a positive RM_ cell");
            if (num != null)
            {
                var cell = num.Cells.First(kv => kv.Key.StartsWith("RM_") && kv.Value > 0f);
                Check(RM_MineralPolicyKernel.RegistryValue(num, cell.Key) == cell.Value, "registry value of own cell");
                string twin = "RUT_" + cell.Key.Substring(3);
                if (!num.Cells.ContainsKey(twin) && !num.Tokens.ContainsKey(twin))
                    Check(RM_MineralPolicyKernel.RegistryValue(num, twin) == cell.Value, "RUT twin must read its RM column");
                Check(RM_MineralPolicyKernel.RegistryValue(num, "TemperateForest") == num.OtherBiomes, "vanilla biome reads OTHER_vanilla_biomes");
                var ov = new Dictionary<string, float> { { RM_MineralPolicyKernel.OverrideKey(num.MaterialId, cell.Key), 7f } };
                Check(RM_MineralPolicyKernel.EffectiveValue(num, cell.Key, ov, 2f) == 14f, "override x multiplier");
                Check(RM_MineralPolicyKernel.EffectiveValue(num, cell.Key, null, 0.5f) == cell.Value * 0.5f, "registry x multiplier");
                Check(RM_MineralPolicyKernel.RegistryValue(num, "RM_NoSuchBiomeColumn") == 0f, "an RM_ biome without a cell is 0");
            }
            MineralRow tok = rows.FirstOrDefault(r => r.Tokens.Count > 0);
            Check(tok != null && RM_MineralPolicyKernel.RegistryValue(tok, tok.Tokens.Keys.First()) == null, "token cell must be null (not a number)");
            Check(Math.Abs(RM_MineralPolicyKernel.LumpsForEpm(1200f, 40f) - 1f) < 1e-5f, "1200 EPM of a 40/cell ore is one lump");
            Check(RM_MineralPolicyKernel.DescribeEpm(1200f, 40f) == "~1.0 deposits of ~30 cells", "describe: " + RM_MineralPolicyKernel.DescribeEpm(1200f, 40f));
            Check(RM_MineralPolicyKernel.DescribeEpm(0f, 40f) == "none" && RM_MineralPolicyKernel.LumpsForEpm(100f, 0f) == 0f, "zero guards");

            Console.WriteLine((fails == 0 ? "PASS " : "FAIL ") + (checks - fails) + "/" + checks + " checks; " + rows.Count + " registry rows, "
                            + defs.Count + " fixture defs, " + on.Count + " decided");
            return fails == 0 ? 0 : 1;
        }
    }
}
