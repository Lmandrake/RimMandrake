// MINERAL_POLICY_CODE_STARTUP_ZEROING L0. Run: python3 src/RimMandrake/Utils/selftest_minerals.py
// The production kernel over the shipped registry XML, DeepDrill's shipped home table and the def-dump fixture (real weights).
// args: <RM_MineralRegistry.xml> <RM_DeepHomeTable.xml> <mineral_defs.tsv> [<def dump StructureLayoutDef.json>]
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
                    QuarryLocal = (string)d.Element("quarryLocal") == "true",
                    QuarryPer100Jobs = d.Element("quarryPer100Jobs") != null ? F((string)d.Element("quarryPer100Jobs")) : -1f,
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

            // --- surface placer active: every governed mineable with scatter is zeroed when the placer can place its row instead;
            // a row it cannot place (not EPM, no yield per cell) keeps vanilla scatter, or its veins would vanish
            Dictionary<string, PolicyDecision> placed = ByName(RM_MineralPolicyKernel.Decide(rows, Clone(defs), new PolicyOptions { SurfacePlacerActive = true }));
            var rowById = rows.ToDictionary(r => r.MaterialId);
            int keptBefore = 0;
            foreach (PolicyDecision p in placed.Values)
            {
                if (p.Unregistered || !orig[p.DefName].IsBuilding) continue;
                bool placeable = RM_MineralSurfaceKernel.Placeable(rowById[p.MaterialId]);
                if (placeable || on[p.DefName].Scatter == 0f)
                    Check(p.Scatter == 0f, "placer active but governed " + p.DefName + " keeps scatter " + p.Scatter);
                else Check(p.Scatter == on[p.DefName].Scatter && !p.SurfacePlaced, "placer active zeroed unplaceable " + p.DefName);
                Check(p.SurfacePlaced == (p.Scatter == 0f && on[p.DefName].Scatter > 0f && placeable), p.DefName + " SurfacePlaced flag disagrees");
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

            // --- re-assert of a def we never wrote: a mineable that bore nothing at the snapshot (so no decision, no lastApplied)
            // and an unknown mod's late static constructor gave it scatter -> adopted, so suppression and the unregistered count see it
            var lateOrig = new Dictionary<string, MineralDefInfo> { { "XX_LateOre", new MineralDefInfo("XX_LateOre", 0f, 0f, "XX_LateItem", true) } };
            var lateLast = new Dictionary<string, float[]>();
            Check(RM_MineralPolicyKernel.Readopt(lateOrig, lateLast, new[] { new MineralDefInfo("XX_LateOre", 0f, 0f, "XX_LateItem", true) }).Count == 0,
                  "re-assert adopted an unwritten def that did not change");
            List<string> late = RM_MineralPolicyKernel.Readopt(lateOrig, lateLast, new[] { new MineralDefInfo("XX_LateOre", 0.6f, 0f, "XX_LateItem", true) });
            Check(late.Contains("XX_LateOre") && lateOrig["XX_LateOre"].Scatter == 0.6f, "late weight on a never-written def must be adopted (got " + string.Join(",", late) + ")");
            var lateSup = ByName(RM_MineralPolicyKernel.Decide(rows, lateOrig.Values.ToList(), new PolicyOptions { SuppressUnregistered = true }));
            Check(lateSup.ContainsKey("XX_LateOre") && lateSup["XX_LateOre"].Unregistered && lateSup["XX_LateOre"].Scatter == 0f,
                  "suppression on must reach an ore that got its weight after the snapshot");

            // --- settings screen edit rule: an unfocused field re-parses its own 2-decimal display every frame
            Check(RM_MineralPolicyKernel.SettingsEdit(1.234f, "1.23", 1.23f, true, 40f) == null, "viewing must not rewrite a stored 1.234 deposits as 1.23");
            Check(RM_MineralPolicyKernel.SettingsEdit(0.125f, RM_MineralPolicyKernel.ShowNumber(0.125f), F(RM_MineralPolicyKernel.ShowNumber(0.125f)), true, 40f) == null,
                  "a .xx5 rounding edge must not mint an override");
            float? typed2 = RM_MineralPolicyKernel.SettingsEdit(1.234f, "2", 2f, true, 40f);
            Check(typed2 != null && Math.Abs(typed2.Value - 2400f) < 1e-2f, "typing 2 deposits of a 40/cell ore stores 2400 EPM");
            Check(RM_MineralPolicyKernel.SettingsEdit(5f, "7", 7f, false, 0f) == 7f, "non-deposit rows store what is typed");
            Check(RM_MineralPolicyKernel.SameAsShown(1.33f, 1.3333f) && !RM_MineralPolicyKernel.SameAsShown(1.4f, 1.3333f), "same-as-registry is judged on the shown number");

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
            // owner card 2026-10-03: the settings unit is deposits per map; the screen converts and stores EPM
            Check(Math.Abs(RM_MineralPolicyKernel.EpmForLumps(1f, 40f) - 1200f) < 1e-3f, "one deposit of a 40/cell ore is 1200 EPM");
            Check(Math.Abs(RM_MineralPolicyKernel.EpmForLumps(RM_MineralPolicyKernel.LumpsForEpm(1777f, 25f), 25f) - 1777f) < 1e-2f, "deposits <-> EPM round trip");
            Check(RM_MineralPolicyKernel.EpmForLumps(3f, 0f) == 0f && RM_MineralPolicyKernel.EpmForLumps(-1f, 40f) == 0f, "EpmForLumps guards");
            Check(RM_MineralPolicyKernel.DescribeEpm(0f, 40f) == "none" && RM_MineralPolicyKernel.LumpsForEpm(100f, 0f) == 0f, "zero guards");

            // --- quarry pool (MINERAL_QUARRY_WIRE_LOCAL_POOL, design §6.4) over the shipped registry
            var qdict = new List<KeyValuePair<string, float>> {   // the Quarry mod's dictionary shape: mined item -> int weight
                new KeyValuePair<string, float>("Steel", 100f), new KeyValuePair<string, float>("Gold", 10f),
                new KeyValuePair<string, float>("Silver", 20f), new KeyValuePair<string, float>("Plasteel", 5f),
                new KeyValuePair<string, float>("ComponentIndustrial", 15f), new KeyValuePair<string, float>("Jade", 0f) };
            HashSet<string> gov = RM_QuarryKernel.GovernedItems(rows);
            Check(gov.Contains("ComponentIndustrial") && gov.Contains("Plasteel") && !gov.Contains("Steel"),
                  "governed items: components and plasteel governed, steel not (its row is unemitted)");
            QuarryPlan vanilla = RM_QuarryKernel.Plan(rows, "TemperateForest", null, qdict, false);
            Check(vanilla.Local.Count == 0, "a vanilla biome has no local quarry rows today (every local row has OTHER 0): " + string.Join(",", vanilla.Local.Select(e => e.MaterialId)));
            Check(vanilla.Unregistered.Select(e => e.Item).OrderBy(s => s, StringComparer.Ordinal).SequenceEqual(new[] { "Gold", "Silver", "Steel" }),
                  "unregistered slice = Quarry's own entries no row governs, weight > 0: " + string.Join(",", vanilla.Unregistered.Select(e => e.Item)));
            Check(Math.Abs(vanilla.UnregisteredShare - 130f / 150f) < 1e-5f, "unregistered keep their exact share of Quarry's draws: " + vanilla.UnregisteredShare);
            QuarryEntry inShare = RM_QuarryKernel.Draw(vanilla, 0.10, 0.0);
            Check(inShare != null && inShare.MaterialId == null, "a draw inside the unregistered share yields an unregistered ore");
            Check(RM_QuarryKernel.Draw(vanilla, 0.95, 0.5) == null, "the governed share on a biome with no local row yields local rock (null)");
            QuarryPlan qsup = RM_QuarryKernel.Plan(rows, "TemperateForest", null, qdict, true);
            Check(qsup.Unregistered.Count == 0 && qsup.UnregisteredShare == 0f && RM_QuarryKernel.Draw(qsup, 0.0, 0.0) == null,
                  "suppress unregistered: nothing but local rows and rock");
            // an unreadable Quarry dictionary (reflection drift: null, or nothing with weight > 0) must not silently give unknown ores
            // a share of 0 (owner card 2026-10-03); the adapter keeps Quarry's own draw. A readable one never sets the flag (probe).
            Check(!vanilla.KeepQuarryDraw && !RM_QuarryKernel.Plan(rows, "RM_GreySea", null, qdict, false).KeepQuarryDraw,
                  "a readable Quarry dictionary keeps the registry draw (probe)");
            Check(RM_QuarryKernel.Plan(rows, "TemperateForest", null, null, false).KeepQuarryDraw
                  && RM_QuarryKernel.Plan(rows, "RM_GreySea", null, new List<KeyValuePair<string, float>>(), false).KeepQuarryDraw
                  && RM_QuarryKernel.Plan(rows, "RM_GreySea", null, new List<KeyValuePair<string, float>> { new KeyValuePair<string, float>("Jade", 0f) }, false).KeepQuarryDraw,
                  "an unreadable or weightless Quarry dictionary keeps Quarry's own draw instead of zeroing unknown ores");
            Check(!RM_QuarryKernel.Plan(rows, "RM_GreySea", null, null, true).KeepQuarryDraw,
                  "suppressing unregistered ores needs no dictionary: the local pool still applies");

            QuarryPlan grey = RM_QuarryKernel.Plan(rows, "RM_GreySea", null, qdict, false);
            Check(grey.Local.Count == 5 && grey.Local.All(e => e.MaterialId.StartsWith("salt_") && Math.Abs(e.Weight - 300f) < 1e-3f),
                  "Grey Sea pool = five salts at 6000 EPM / 20 per cell: " + string.Join(",", grey.Local.Select(e => e.MaterialId + "=" + e.Weight)));
            var seen = new HashSet<string>();
            for (int i = 0; i < 200; i++) { QuarryEntry e = RM_QuarryKernel.Draw(grey, (i % 10) / 10.0, (i * 0.618) % 1.0); if (e != null) seen.Add(e.Item); }
            Check(!seen.Contains("ComponentIndustrial") && !seen.Contains("Plasteel"), "components and plasteel never come out of a quarry");
            Check(seen.Contains("RM_RawSalt") && seen.Contains("Steel"), "both slices reachable on the Grey Sea (probe): " + string.Join(",", seen));
            var ovq = new Dictionary<string, float> { { RM_MineralPolicyKernel.OverrideKey("salt_raw", "RM_GreySea"), 0f } };
            Check(RM_QuarryKernel.Plan(rows, "RM_GreySea", ovq, qdict, false).Local.All(e => e.MaterialId != "salt_raw"), "an override of 0 removes the row from the pool");
            QuarryPlan lantern = RM_QuarryKernel.Plan(rows, "RM_LanternDeeps", null, qdict, false);
            Check(lantern.Local.Any(e => e.MaterialId == "pyrinth" && Math.Abs(e.Weight - 60f) < 1e-3f) && lantern.Local.Any(e => e.MaterialId == "lanternstone"),
                  "Lantern Deeps pool has pyrinth (600/10) and lanternstone");
            Check(RM_QuarryKernel.Plan(rows, "RM_RustCathedral", null, qdict, false).Local.All(e => e.MaterialId != "live_pattern_metal"),
                  "a deep-share/token row never enters the quarry pool");
            int localRows = 0;
            var biomesSeen = new HashSet<string>(rows.SelectMany(r => r.Cells.Keys)) { "TemperateForest", "RUT_GreySea" };
            foreach (string bm in biomesSeen)
                foreach (QuarryEntry e in RM_QuarryKernel.Plan(rows, bm, null, qdict, false).Local)
                {
                    localRows++;
                    MineralRow src = rows.First(r => r.MaterialId == e.MaterialId);
                    Check(src.QuarryLocal && src.Items.Contains(e.Item), bm + ": " + e.MaterialId + " entered the pool but is not quarry=local");
                }
            Check(localRows >= 10, "the pool sweep saw only " + localRows + " entries (probe)");
            // planted: a row with a positive cell but quarry=no must stay out
            var qno = new MineralRow { MaterialId = "qno", UnitsPerCellOrFind = 10f }; qno.Items.Add("QNo"); qno.Cells["RM_X"] = 500f;
            Check(RM_QuarryKernel.Plan(new List<MineralRow> { qno }, "RM_X", null, null, false).Local.Count == 0, "quarry=no row with a cell stays out (planted)");
            qno.QuarryLocal = true;
            Check(RM_QuarryKernel.Plan(new List<MineralRow> { qno }, "RM_X", null, null, false).Local.Count == 1, "same row with quarry=local enters (probe)");
            // QUARRYSHARE_FIX_ZEROED_GOVERNED_WEIGHTS: Quarry's stored dictionary depends on whether it was built before Minerals was
            // installed (vanilla weights) or after the policy zeroed a governed item (weight 0, and ComponentIndustrial = 1.5 x min = 0).
            // The share must not: governed entries are reweighed from the originals with Quarry's own formula.
            Check(Math.Abs(RM_QuarryKernel.QuarryCurve(0.03f) - 8.5f) < 1e-5f && RM_QuarryKernel.QuarryCurve(0f) == 10f
                  && Math.Abs(RM_QuarryKernel.QuarryCurve(1f) - 3f) < 1e-4f, "Quarry's commonality curve");
            Check(RM_QuarryKernel.QuarryOreWeight(4f, 1f, 1.9f) == 112 && RM_QuarryKernel.QuarryOreWeight(0f, 1f, 1.9f) == 0
                  && RM_QuarryKernel.QuarryOreWeight(1f, 0.05f, 10f) == (int)(1f * 0.05f * 7f * 50f / 2f),
                  "Quarry's ValueForMineableOre: steel 112, zero deep 0, plasteel-like 8: " + RM_QuarryKernel.QuarryOreWeight(4f, 1f, 1.9f));
            var qrocks = new List<RM_QuarryKernel.QuarryRock> {   // originals, as the policy snapshotted them
                new RM_QuarryKernel.QuarryRock("Steel", 1f, 4f, 1.9f), new RM_QuarryKernel.QuarryRock("Gold", 0.1f, 1f, 10f),
                new RM_QuarryKernel.QuarryRock("Silver", 0.2f, 1f, 1f), new RM_QuarryKernel.QuarryRock("Plasteel", 0.05f, 1f, 10f) };
            Func<string, float> vw = it => { var r = qrocks.First(x => x.Item == it); return RM_QuarryKernel.QuarryOreWeight(r.Deep, r.Scatter, r.MarketValue); };
            int vmin = new[] { "Steel", "Gold", "Silver", "Plasteel" }.Select(it => (int)vw(it)).Min();
            var builtBefore = new List<KeyValuePair<string, float>> {   // Quarry built before Minerals: vanilla weights throughout
                new KeyValuePair<string, float>("Steel", vw("Steel")), new KeyValuePair<string, float>("Gold", vw("Gold")),
                new KeyValuePair<string, float>("Silver", vw("Silver")), new KeyValuePair<string, float>("Plasteel", vw("Plasteel")),
                new KeyValuePair<string, float>("ComponentIndustrial", vmin + vmin / 2) };
            var builtAfter = new List<KeyValuePair<string, float>> {    // built after the policy zeroed Plasteel's deepCommonality
                new KeyValuePair<string, float>("Steel", vw("Steel")), new KeyValuePair<string, float>("Gold", vw("Gold")),
                new KeyValuePair<string, float>("Silver", vw("Silver")), new KeyValuePair<string, float>("Plasteel", 0f),
                new KeyValuePair<string, float>("ComponentIndustrial", 0f) };
            float rawBefore = RM_QuarryKernel.Plan(rows, "TemperateForest", null, builtBefore, false).UnregisteredShare;
            float rawAfter = RM_QuarryKernel.Plan(rows, "TemperateForest", null, builtAfter, false).UnregisteredShare;
            Check(rawAfter == 1f && rawBefore < 0.99f, "probe: the stored dictionaries really give order-dependent shares unrepaired (" + rawBefore + " vs " + rawAfter + ")");
            List<KeyValuePair<string, float>> pBefore = RM_QuarryKernel.PristineDictionary(builtBefore, qrocks, gov, "ComponentIndustrial");
            List<KeyValuePair<string, float>> pAfter = RM_QuarryKernel.PristineDictionary(builtAfter, qrocks, gov, "ComponentIndustrial");
            Func<List<KeyValuePair<string, float>>, string> show = l => string.Join(",", l.OrderBy(e => e.Key, StringComparer.Ordinal).Select(e => e.Key + "=" + e.Value));
            Check(show(pBefore) == show(pAfter) && show(pBefore) == show(builtBefore),
                  "both install orders repair to the vanilla dictionary: " + show(pAfter) + " | " + show(builtBefore));
            float shBefore = RM_QuarryKernel.Plan(rows, "TemperateForest", null, pBefore, false).UnregisteredShare;
            float shAfter = RM_QuarryKernel.Plan(rows, "TemperateForest", null, pAfter, false).UnregisteredShare;
            Check(shBefore == shAfter && Math.Abs(shBefore - rawBefore) < 1e-6f, "the unregistered share is the same in both orders: " + shBefore + " / " + shAfter);
            var stale = new List<KeyValuePair<string, float>>(builtAfter.Where(e => e.Key != "Plasteel"));   // built before Plasteel's mod
            Check(!RM_QuarryKernel.PristineDictionary(stale, qrocks, gov, "ComponentIndustrial").Any(e => e.Key == "Plasteel"),
                  "a governed item Quarry never listed is not invented");
            var odd = new List<KeyValuePair<string, float>> { new KeyValuePair<string, float>("Steel", 7f), new KeyValuePair<string, float>("Plasteel", 99f) };
            Check(RM_QuarryKernel.PristineDictionary(odd, qrocks, gov, "ComponentIndustrial").Single(e => e.Key == "Steel").Value == 7f,
                  "unregistered entries keep Quarry's stored weight (owner card 2026-10-03)");
            Check(RM_QuarryKernel.PristineDictionary(null, qrocks, gov, "ComponentIndustrial") == null, "an unreadable dictionary stays unreadable");

            // --- PLASTEEL_AUDIT_EXPLICIT_MINEABLE_LISTS: explicit placement lists drop what the registry disables
            var mineableBuildings = new HashSet<string>(defs.Where(d => d.IsBuilding && d.MinedItem != null).Select(d => d.DefName));
            HashSet<string> disOn = RM_ExplicitListKernel.Disabled(on.Values, mineableBuildings.Contains);
            HashSet<string> disOff = RM_ExplicitListKernel.Disabled(off, mineableBuildings.Contains);
            Check(disOn.Contains("MineablePlasteel") && disOn.Contains("MineableComponentsIndustrial"),
                  "the disabled set must hold Core's plasteel and component mineables: " + string.Join(",", disOn));
            Check(disOff.Count == 0, "master toggle off disables nothing: " + string.Join(",", disOff));
            Check(disOn.All(mineableBuildings.Contains) && !disOn.Contains("MineableSteel"),
                  "only mineable buildings are disabled, never an item or steel: " + string.Join(",", disOn));
            Check(RM_ExplicitListKernel.Disabled(on.Values, null).Count >= disOn.Count, "instrument: the unfiltered disabled set is no smaller");
            // Core GenStepDef PreciousLump.mineables, as the 2026-10-28 dump holds it
            string[] lump = { "MineableGold", "MineableSilver", "MineableSteel", "MineablePlasteel", "MineableComponentsIndustrial",
                              "MineableUranium", "MineableJade", "MineableDiamond", "MineableRuby", "MineableSapphire" };
            List<IList<string>> lumpEntries = lump.Select(n => (IList<string>)new[] { n }).ToList();
            ListPrune lp = RM_ExplicitListKernel.Prune(lumpEntries, disOn);
            List<string> lumpKept = lp.Keep.Select(i => lump[i]).ToList();
            Console.WriteLine("PreciousLump keeps: " + string.Join(",", lumpKept) + "; drops: " + string.Join(",", lp.Dropped));
            Check(!lumpKept.Contains("MineablePlasteel") && !lumpKept.Contains("MineableComponentsIndustrial") && lumpKept.Contains("MineableSteel")
                  && !lp.FellBack && lp.Keep.SequenceEqual(lp.Keep.OrderBy(i => i)), "PreciousLump drops plasteel and components, keeps steel, in order");
            Check(RM_ExplicitListKernel.Prune(lumpEntries, disOff).Keep.Count == lump.Length, "master toggle off restores the whole list");
            // a MineableCountConfig / ThingWeight entry carries its ThingDef fields: any disabled one drops the entry
            var counts = new List<IList<string>> { new[] { "MineableGold" }, new[] { "MineablePlasteel" }, new string[0], new[] { "x", "MineableComponentsIndustrial" } };
            ListPrune cp = RM_ExplicitListKernel.Prune(counts, disOn);
            Check(cp.Keep.SequenceEqual(new[] { 0, 2 }) && cp.Dropped.SequenceEqual(new[] { "MineablePlasteel", "MineableComponentsIndustrial" }),
                  "config entries: drop the ones naming a disabled mineable: keep " + string.Join(",", cp.Keep));
            ListPrune only = RM_ExplicitListKernel.Prune(new List<IList<string>> { new[] { "MineablePlasteel" } }, disOn);
            Check(only.FellBack && only.Keep.SequenceEqual(new[] { 0 }) && only.Dropped.Count == 0,
                  "a list that would empty is kept whole (RandomElement of nothing throws)");
            Check(!RM_ExplicitListKernel.Prune(new List<IList<string>>(), disOn).FellBack, "an empty list is not a fallback");

            // --- MINESITES_GRIDS_BUILD_STEEL_FOR_BANNED_ORE: authored ruin grids swap plasteel/components cells to steel
            HashSet<string> swapOn = RM_LayoutGridKernel.SwapOut(disOn), swapOff = RM_LayoutGridKernel.SwapOut(disOff);
            Check(swapOn.SetEquals(RM_LayoutGridKernel.Scope) && swapOff.Count == 0,
                  "policy on swaps both scope mineables, master toggle off swaps none: " + string.Join(",", swapOn));
            Check(!disOn.Contains(RM_LayoutGridKernel.Replacement), "the replacement ore is never itself disabled");
            var grid = new List<IList<string>> {
                new List<string> { ".,MineablePlasteel,Wall_Plasteel,,MineableComponentsIndustrial", "Plasteel,MineablePlasteelX,MineableSteel,." },
                new List<string> { "MineableComponentsIndustrial", "." } };
            List<GridCell> gc = RM_LayoutGridKernel.Find(grid, new HashSet<string>(RM_LayoutGridKernel.Scope));
            Check(gc.Count == 3 && gc[0].Layer == 0 && gc[0].Row == 0 && gc[0].Col == 1 && gc[1].Col == 4 && gc[2].Layer == 1 && gc[2].Col == 0,
                  "Find sees exact tokens only (not Wall_Plasteel, Plasteel, MineablePlasteelX) at KCSG's split positions: " + gc.Count);
            List<List<string>> rw = RM_LayoutGridKernel.Rewrite(grid, swapOn, RM_LayoutGridKernel.Replacement);
            Check(rw[0][0] == ".,MineableSteel,Wall_Plasteel,,MineableSteel" && rw[0][1] == (string)grid[0][1] && rw[1][0] == "MineableSteel" && rw[1][1] == ".",
                  "Rewrite swaps tokens and keeps every other character: " + rw[0][0]);
            Check((string)grid[0][0] == ".,MineablePlasteel,Wall_Plasteel,,MineableComponentsIndustrial", "Rewrite never writes its input");
            List<IList<string>> rwI = rw.Select(l => (IList<string>)l).ToList();
            Check(RM_LayoutGridKernel.Rewrite(rwI, swapOn, RM_LayoutGridKernel.Replacement).Zip(rw, (a, b) => a.SequenceEqual(b)).All(x => x),
                  "Rewrite applied twice equals once");
            Check(RM_LayoutGridKernel.Rewrite(grid, swapOff, RM_LayoutGridKernel.Replacement).Zip(grid, (a, b) => a.SequenceEqual(b)).All(x => x),
                  "an empty swap set restores the rows as shipped");
            var onlyP = new HashSet<string> { "MineablePlasteel" };
            Check(RM_LayoutGridKernel.Rewrite(grid, onlyP, RM_LayoutGridKernel.Replacement)[0][0] == ".,MineableSteel,Wall_Plasteel,,MineableComponentsIndustrial",
                  "a scope mineable the registry keeps is left alone");
            Check(RM_LayoutGridKernel.SwapOut(new HashSet<string> { "MineableGold", "MineablePlasteel" }).SetEquals(onlyP), "a disabled mineable outside the scope is never swapped");
            if (args.Length > 3) LayoutDump(args[3]);
            else Console.WriteLine("UNMEASURED dump layouts: pass the def dump's StructureLayoutDef.json as a 4th argument for the full-grid count");

            var two = new List<QuarryEntry> { new QuarryEntry("a", 1f, "a"), new QuarryEntry("b", 3f, "b") };
            Check(RM_QuarryKernel.PickWeighted(two, 0.2).Item == "a" && RM_QuarryKernel.PickWeighted(two, 0.3).Item == "b"
                  && RM_QuarryKernel.PickWeighted(two, 1.0).Item == "b", "weighted pick boundaries");
            Check(RM_QuarryKernel.PickWeighted(new List<QuarryEntry>(), 0.5) == null
                  && RM_QuarryKernel.PickWeighted(new List<QuarryEntry> { new QuarryEntry("z", 0f, "z") }, 0.5) == null, "empty / zero-weight pool picks nothing");

            // --- surface adapter (MINERAL_SURFACE_BUILD_PER_BIOME, design §4)
            // kept share: vanilla's RocksFromGrid scatter picks each lump by RELATIVE weight. Zeroing governed veins without scaling
            // the count hands their lumps to the rest (owner card 2026-10-03: an unregistered ore behaves as its mod intended).
            var eligible = defs.Where(d => d.IsBuilding && d.Scatter > 0f).ToList();
            float sumOrig = eligible.Sum(d => d.Scatter);
            float sumCur = eligible.Sum(d => on[d.DefName].Scatter);
            float share = RM_MineralSurfaceKernel.KeptShare(eligible.Select(d => new KeyValuePair<float, float>(on[d.DefName].Scatter, d.Scatter)));
            const float vanillaCount = 69f;   // CountFromPer10kCells on a 250² large-hills map (design §4)
            float steelVanilla = RM_MineralSurfaceKernel.ExpectedVanillaLumps(vanillaCount, orig["MineableSteel"].Scatter, sumOrig);
            float steelOld = RM_MineralSurfaceKernel.ExpectedVanillaLumps(vanillaCount, on["MineableSteel"].Scatter, sumCur);
            float steelNew = RM_MineralSurfaceKernel.ExpectedVanillaLumps(vanillaCount * share, on["MineableSteel"].Scatter, sumCur);
            Check(sumCur < sumOrig && steelOld > steelVanilla * 1.01f,
                  "probe: the default policy zeroes some vein weight, so unscaled vanilla scatter inflates steel (" + steelVanilla + " -> " + steelOld + ")");
            Check(Math.Abs(steelNew - steelVanilla) < 1e-3f, "kept share must keep unregistered steel at its vanilla lumps: " + steelVanilla + " vs " + steelNew);
            Console.WriteLine("kept share " + share.ToString("0.000") + ": steel lumps vanilla " + steelVanilla.ToString("0.00") + ", unscaled "
                            + steelOld.ToString("0.00") + ", scaled " + steelNew.ToString("0.00"));
            Check(RM_MineralSurfaceKernel.KeptShare(eligible.Select(d => new KeyValuePair<float, float>(d.Scatter, d.Scatter))) == 1f, "nothing zeroed: share 1");
            Check(RM_MineralSurfaceKernel.KeptShare(new KeyValuePair<float, float>[0]) == 1f
                  && RM_MineralSurfaceKernel.KeptShare(new[] { new KeyValuePair<float, float>(0f, 2f) }) == 0f, "share guards: empty 1, all zeroed 0");

            // lump counts: 1200 EPM of a 40/cell ore is one lump on the reference map; hilliness and area scale it; nomadic too
            Check(Math.Abs(RM_MineralSurfaceKernel.ExpectedLumps(1200f, 40f, 11f, 62500, 1f) - 1f) < 1e-5f, "reference map: 1200 EPM / 40 per cell = 1 lump");
            Check(Math.Abs(RM_MineralSurfaceKernel.ExpectedLumps(1200f, 40f, 4f, 62500, 1f) - 4f / 11f) < 1e-5f, "flat map scales by 4/11");
            Check(Math.Abs(RM_MineralSurfaceKernel.ExpectedLumps(1200f, 40f, 11f, 40000, 1f) - 0.64f) < 1e-5f, "200² map scales by area");
            Check(Math.Abs(RM_MineralSurfaceKernel.ExpectedLumps(1200f, 40f, 11f, 62500, 0.5f) - 0.5f) < 1e-5f, "nomadic factor applies");
            Check(RM_MineralSurfaceKernel.ExpectedLumps(0f, 40f, 11f, 62500, 1f) == 0f && RM_MineralSurfaceKernel.ExpectedLumps(1200f, 0f, 11f, 62500, 1f) == 0f,
                  "lump guards");
            int sum = 0;
            for (int i = 0; i < 1000; i++) sum += RM_MineralSurfaceKernel.StochasticRound(0.5f, (i + 0.5) / 1000.0);
            Check(sum == 500, "stochastic rounding keeps the expectation of half a lump: " + sum + "/1000");
            Check(RM_MineralSurfaceKernel.StochasticRound(2.25f, 0.2) == 3 && RM_MineralSurfaceKernel.StochasticRound(2.25f, 0.3) == 2
                  && RM_MineralSurfaceKernel.StochasticRound(-1f, 0.0) == 0, "stochastic rounding boundaries");

            // targets over the shipped registry with the placer active. Every governed vein with vanilla scatter today belongs to a
            // row it cannot place or with no surface source; the GUESS rows (steel, gold, silver) are not emitted yet. So: none.
            List<SurfaceTarget> shippedTargets = RM_MineralSurfaceKernel.SurfaceTargets(rows, placed.Values, orig);
            Console.WriteLine("surface targets on the shipped registry: " + shippedTargets.Count + " (" + string.Join(",", shippedTargets.Select(t => t.MaterialId)) + ")");
            foreach (SurfaceTarget t in shippedTargets)
                Check(t.Mineables.All(m => placed[m.Key].SurfacePlaced && placed[m.Key].Scatter == 0f), t.MaterialId + ": target mineable still scatters");
            // synthetic: an EPM row with two vein defs; a non-EPM row; a 0-scatter vein (its own GenStep places it)
            var ep = new MineralRow { MaterialId = "ep", UnitsPerCellOrFind = 40f }; ep.Items.Add("EP"); ep.Cells["RM_X"] = 2400f;
            var ups = new MineralRow { MaterialId = "ups", Unit = "UPY", UnitsPerCellOrFind = 40f }; ups.Items.Add("UP"); ups.Cells["RM_X"] = 50f;
            var synDefs = new List<MineralDefInfo> {
                new MineralDefInfo("MineableEP1", 0.3f, 0f, "EP", true), new MineralDefInfo("MineableEP2", 0.1f, 0f, "EP", true),
                new MineralDefInfo("MineableEP0", 0f, 0f, "EP", true), new MineralDefInfo("MineableUP", 0.2f, 0f, "UP", true),
                new MineralDefInfo("MineableSteel", 1f, 0f, "Steel", true) };
            List<PolicyDecision> synPlaced = RM_MineralPolicyKernel.Decide(new List<MineralRow> { ep, ups }, synDefs, new PolicyOptions { SurfacePlacerActive = true });
            Dictionary<string, PolicyDecision> sp = ByName(synPlaced);
            Check(sp["MineableEP1"].SurfacePlaced && sp["MineableEP1"].Scatter == 0f && sp["MineableEP2"].SurfacePlaced, "EPM veins are placed, vanilla scatter zeroed");
            Check(!sp["MineableEP0"].SurfacePlaced, "a 0-scatter vein is left to its own GenStep (no double placement)");
            // failing on old: R2 zeroed every governed vein once a placer registered, so a row the placer cannot place lost its veins
            Check(!sp["MineableUP"].SurfacePlaced && sp["MineableUP"].Scatter == 0.2f, "a non-EPM row keeps vanilla scatter under the placer");
            Check(sp["MineableSteel"].Unregistered && sp["MineableSteel"].Scatter == 1f, "unregistered steel untouched by the placer");
            // failing on old: an EPM row whose only surface source is a token (herd/unbounded) was zeroed for the placer, which reads
            // a token as no value and places nothing - its veins vanished from every biome
            var tokOnly = new MineralRow { MaterialId = "tok", UnitsPerCellOrFind = 1f }; tokOnly.Items.Add("TK"); tokOnly.Tokens["RM_X"] = "unbounded";
            var tokDec = ByName(RM_MineralPolicyKernel.Decide(new List<MineralRow> { tokOnly }, new List<MineralDefInfo> {
                new MineralDefInfo("MineableTK", 0.2f, 0f, "TK", true) }, new PolicyOptions { SurfacePlacerActive = true }));
            Check(tokOnly.HasSurfacePresence && !RM_MineralSurfaceKernel.Placeable(tokOnly), "a token-only EPM row has surface presence but nothing to place");
            Check(!tokDec["MineableTK"].SurfacePlaced && tokDec["MineableTK"].Scatter == 0.2f, "a token-only EPM row keeps vanilla scatter under the placer");
            Check(RM_MineralSurfaceKernel.Placeable(ep), "probe: an EPM row with a positive cell is placeable");
            var synOrig = synDefs.ToDictionary(d => d.DefName);
            List<SurfaceTarget> st = RM_MineralSurfaceKernel.SurfaceTargets(new List<MineralRow> { ep, ups }, synPlaced, synOrig);
            Check(st.Count == 1 && st[0].MaterialId == "ep" && st[0].Mineables.Count == 2 && st[0].UnitsPerCell == 40f, "one target, two weighted mineables");
            Check(RM_MineralSurfaceKernel.PickMineable(st[0].Mineables, 0.70) == "MineableEP1" && RM_MineralSurfaceKernel.PickMineable(st[0].Mineables, 0.80) == "MineableEP2"
                  && RM_MineralSurfaceKernel.PickMineable(st[0].Mineables, 1.0) == "MineableEP2", "lump mineable keeps the original 3:1 split");
            Check(RM_MineralSurfaceKernel.PickMineable(new List<KeyValuePair<string, float>>(), 0.5) == null, "empty pick");
            float? epEpm = RM_MineralPolicyKernel.EffectiveValue(ep, "RM_X", null, 1f);
            Check(epEpm == 2400f && Math.Abs(RM_MineralSurfaceKernel.ExpectedLumps(epEpm.Value, 40f, 11f, 62500, 1f) - 2f) < 1e-5f, "2400 EPM is two lumps on RM_X");
            Check(RM_MineralPolicyKernel.EffectiveValue(ep, "TemperateForest", null, 1f) == 0f, "a biome the row does not bear gets no lumps");
            Check(Math.Abs(RM_MineralSurfaceKernel.OrePer1000Rock(30, 6000) - 5f) < 1e-5f && RM_MineralSurfaceKernel.OrePer1000Rock(5, 0) == 0f, "diagnostic per 1000 rock");

            // --- meteorites (owner card 2026-10-25: only metals and space-ish ores fall, stone types never)
            var meteorWl = new List<string>();
            foreach (XElement d in XDocument.Load(args[0]).Root.Elements("RimMandrake.Minerals.RM_MineralMeteoriteDef"))
                foreach (XElement li in d.Element("mineables")?.Elements("li") ?? Enumerable.Empty<XElement>()) meteorWl.Add(li.Value.Trim());
            Check(XDocument.Load(args[0]).Root.Elements("RimMandrake.Minerals.RM_MineralMeteoriteDef").Count() == 1, "registry holds exactly one meteorite def");
            Check(meteorWl.Contains("MineableSteel") && meteorWl.Contains("MineableGold") && meteorWl.Count >= 4, "shipped meteorite list sees steel and gold (" + meteorWl.Count + ")");
            Check(!meteorWl.Any(n => n.Contains("Plasteel") || n.Contains("Jade") || n.Contains("Granite") || n.Contains("Marble")
                                  || n.Contains("Sandstone") || n.Contains("Slate") || n.Contains("Limestone") || n.Contains("Components")),
                  "shipped meteorite list holds no stone, jade, plasteel or components");
            var vanillaMeteor = new List<MeteorCandidate>
            {
                new MeteorCandidate("Granite", false, 0f), new MeteorCandidate("Marble", false, 0f),
                new MeteorCandidate("MineableSteel", true, 1.9f), new MeteorCandidate("MineableJade", true, 5f),
                new MeteorCandidate("MineableGold", true, 10f), new MeteorCandidate("MineableComponentsIndustrial", true, 32f),
                new MeteorCandidate("MineablePlasteel", true, 9f), new MeteorCandidate("MineableUranium", true, 6f),
            };
            MeteorFilter mf = RM_MineralMeteoriteKernel.Filter(vanillaMeteor, meteorWl, true);
            Check(mf.Active && !mf.FellBack && mf.Kept.SequenceEqual(new[] { "MineableSteel", "MineableGold", "MineableUranium" }),
                  "meteorite filter keeps whitelisted ores in vanilla order: " + string.Join(",", mf.Kept));
            Check(mf.Dropped.Count == 5 && mf.Dropped.Contains("Granite") && mf.Dropped.Contains("MineablePlasteel"), "meteorite filter drops stone, jade, plasteel, components");
            MeteorFilter mOff = RM_MineralMeteoriteKernel.Filter(vanillaMeteor, meteorWl, false);
            Check(!mOff.Active && mOff.Kept.Count == vanillaMeteor.Count && mOff.Dropped.Count == 0, "master toggle off keeps the vanilla list");
            MeteorFilter mNone = RM_MineralMeteoriteKernel.Filter(vanillaMeteor, new[] { "RSW_MineableNothing" }, true);
            Check(mNone.FellBack && !mNone.Active && mNone.Kept.Count == vanillaMeteor.Count, "no whitelisted ore present: vanilla list kept, adapter inactive");
            MeteorFilter mStone = RM_MineralMeteoriteKernel.Filter(vanillaMeteor, new[] { "Granite", "MineableSteel" }, true);
            Check(mStone.Kept.SequenceEqual(new[] { "MineableSteel" }), "a whitelisted stone type is refused");
            List<MeteorCandidate> keptC = vanillaMeteor.Where(c => mf.Kept.Contains(c.DefName)).ToList();
            bool pickOk = true;
            var pickSeen = new HashSet<string>();
            for (int i = 0; i < 100; i++) for (int j = 0; j < 10; j++)
            {
                MeteorCandidate pc = RM_MineralMeteoriteKernel.Pick(keptC, i / 99f, j / 9f);
                if (pc == null || !pc.ResourceRock) pickOk = false; else pickSeen.Add(pc.DefName);
            }
            Check(pickOk && pickSeen.Count == 3, "pick never returns null or stone and reaches every kept ore (" + pickSeen.Count + ")");
            Check(RM_MineralMeteoriteKernel.Pick(new List<MeteorCandidate>(), 0.5f, 0.5f) == null, "pick of an empty list is null");
            float[] shares = RM_MineralMeteoriteKernel.BucketShares(keptC);
            Check(shares[0] == 0f && Math.Abs(shares[1] - 0.35f / 0.6f) < 1e-5f && Math.Abs(shares[2] - 0.25f / 0.6f) < 1e-5f, "bucket shares renormalise without stone");
            float[] vShares = RM_MineralMeteoriteKernel.BucketShares(vanillaMeteor);
            Check(Math.Abs(vShares[0] - 0.4f) < 1e-5f && Math.Abs(vShares[2] - 0.25f) < 1e-5f, "probe: the vanilla list keeps vanilla shares");
            Check(RM_MineralMeteoriteKernel.Pick(keptC, 0f, 0f).DefName == "MineableSteel" && RM_MineralMeteoriteKernel.Pick(keptC, 1f, 0f).DefName == "MineableGold",
                  "pick boundaries: roll 0 cheap ore, roll 1 precious ore");

            Console.WriteLine((fails == 0 ? "PASS " : "FAIL ") + (checks - fails) + "/" + checks + " checks; " + rows.Count + " registry rows, "
                            + defs.Count + " fixture defs, " + on.Count + " decided");
            return fails == 0 ? 0 : 1;
        }

        /// <summary>The production Rewrite over every KCSG layout of a def dump: before and after counts of the scope and steel cells.
        /// Optional (the driver passes 3 args); a by-hand run with the dump path is the exact offline scan of the decision's numbers.</summary>
        static void LayoutDump(string path)
        {
            using var doc = System.Text.Json.JsonDocument.Parse(File.ReadAllText(path));
            string[] tok = { RM_LayoutGridKernel.Scope[0], RM_LayoutGridKernel.Scope[1], RM_LayoutGridKernel.Replacement };
            var before = tok.ToDictionary(t => t, t => 0); var after = tok.ToDictionary(t => t, t => 0);
            int defsSeen = 0, touched = 0, cells = 0;
            var swap = new HashSet<string>(RM_LayoutGridKernel.Scope);
            foreach (var d in doc.RootElement.GetProperty("defs").EnumerateArray())
            {
                defsSeen++;
                if (!d.GetProperty("fields").TryGetProperty("layouts", out var ls) || ls.ValueKind != System.Text.Json.JsonValueKind.Array) continue;
                var layers = ls.EnumerateArray().Select(l => (IList<string>)l.EnumerateArray().Select(r => r.GetString()).ToList()).ToList();
                List<GridCell> found = RM_LayoutGridKernel.Find(layers, swap);
                List<IList<string>> rw = RM_LayoutGridKernel.Rewrite(layers, swap, RM_LayoutGridKernel.Replacement).Select(l => (IList<string>)l).ToList();
                Dictionary<string, int> b = RM_LayoutGridKernel.Count(layers, tok), a = RM_LayoutGridKernel.Count(rw, tok);
                foreach (string t in tok) { before[t] += b[t]; after[t] += a[t]; }
                if (found.Count > 0) { touched++; cells += found.Count; Console.WriteLine("  layout " + d.GetProperty("defName").GetString() + ": " + found.Count + " cells"); }
                Check(rw.Zip(layers, (x, y) => x.Count == y.Count && x.Zip(y, (p, q) => p.Split(',').Length == q.Split(',').Length).All(z => z)).All(z => z),
                      "dump: rewrite keeps every row's width in " + d.GetProperty("defName").GetString());
            }
            Console.WriteLine("dump layouts: " + defsSeen + " defs, " + touched + " touched, " + cells + " cells; before "
                            + string.Join(" ", tok.Select(t => t + "=" + before[t])) + "; after " + string.Join(" ", tok.Select(t => t + "=" + after[t])));
            Check(defsSeen >= 100 && before[RM_LayoutGridKernel.Replacement] > 1000, "dump: instrument can see layouts and steel cells");
            Check(before[tok[0]] + before[tok[1]] == cells && after[tok[0]] == 0 && after[tok[1]] == 0
                  && after[tok[2]] == before[tok[2]] + cells, "dump: every scope cell becomes steel, nothing else moves");
        }
    }
}
