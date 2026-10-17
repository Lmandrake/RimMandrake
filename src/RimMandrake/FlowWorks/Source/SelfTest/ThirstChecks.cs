// THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (design/RimMandrake/thirst_bottles_design_2026-10-16.md, OQ-1..OQ-5 ruled by card
// 2026-10-16). Offline halves of the design's T-rows: the production arithmetic (Thirst/RM_ThirstMath.cs, compiled in) and
// the shipped XML (need, hediff, generated bottles, DBH patch, think tree) plus the Harmony target and call sites. Each case
// has a can-fail. NOT proven here (live, owed): the provider log line on three mod lists (T1), one need per colonist (T2),
// the fall in game (T3), a drink raising the need (T4), salt-water poisoning odds (T5), dehydration on a live pawn (T6), a
// clean log without DBH (T7) and animals drinking (T9).
using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Thirst;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ThirstChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool Near(float a, float b, float tol) => Math.Abs(a - b) <= tol;

        private static string LiquidDefs => ContainerMatFixture.Root();
        private static string ModRoot => Path.GetDirectoryName(Path.GetDirectoryName(LiquidDefs));

        private static XElement Def(XDocument d, string type, string defName) =>
            d.Descendants(type).FirstOrDefault(e => (string)e.Element("defName") == defName);

        public static void Run(Action<string, Action> Case)
        {
            Case("Thirst_provider_rule", () =>
            {
                Assert(RM_ThirstMath.ProviderMode(false, false, false, out _) == RM_ThirstProviderMode.Own, "no DBH: Own");
                Assert(RM_ThirstMath.ProviderMode(true, true, false, out string r) == RM_ThirstProviderMode.Dbh && r.Contains("Thirst"), "Lite + Thirst add-on: Dbh");
                Assert(RM_ThirstMath.ProviderMode(true, false, true, out _) == RM_ThirstProviderMode.Dbh, "full DBH: Dbh");
                Assert(RM_ThirstMath.ProviderMode(true, false, false, out _) == RM_ThirstProviderMode.Own, "Lite without the Thirst add-on: Own");
                Assert(RM_ThirstMath.ProviderMode(false, true, true, out _) == RM_ThirstProviderMode.Own, "can-fail: DBH active but no DBHThirst def (thirst off in DBH): Own");
            });
            Case("Thirst_fall_rate_ruled", () =>
            {
                // T3 offline: 0.25 day at 20 C (comfy max 26 C: no heat) drops 0.2 x multiplier
                float perDay = RM_ThirstMath.FallPerDay(1f, RM_ThirstMath.HeatFactor(20f, 26f, true), false, false);
                float drop = RM_ThirstMath.FallPerInterval(perDay) * (0.25f * RM_ThirstMath.TicksPerDay / RM_ThirstMath.NeedIntervalTicks);
                Assert(Near(drop, 0.2f, 0.001f), "0.25 day drops 0.2, got " + drop);
                Assert(Near(1f / RM_ThirstMath.FallPerDay(1f, 1f, false, false), 1.25f, 0.001f), "OQ-3: empty in 1.25 days");
                Assert(Near(RM_ThirstMath.FallPerDay(2f, 1f, false, false), 1.6f, 0.001f), "multiplier scales the rate");
                Assert(Near(RM_ThirstMath.FallPerDay(1f, 1f, true, false), 1.04f, 0.001f), "hard labour x1.3");
                Assert(Near(RM_ThirstMath.FallPerDay(1f, 1f, false, true), 0.4f, 0.001f), "asleep x0.5");
                Assert(!Near(drop, 0.4f, 0.01f), "can-fail: not the hard-labour-asleep-blind rate");
            });
            Case("Thirst_heat_cap_ruled", () =>
            {
                Assert(RM_ThirstMath.HeatFactor(26f, 26f, true) == 1f && RM_ThirstMath.HeatFactor(10f, 26f, true) == 1f, "no heat at or below comfy max");
                Assert(Near(RM_ThirstMath.HeatFactor(36f, 26f, true), 1.5f, 0.001f), "10 C over: x1.5");
                Assert(RM_ThirstMath.HeatFactor(90f, 26f, true) == 3f, "OQ-3: capped at x3");
                Assert(RM_ThirstMath.HeatFactor(90f, 26f, false) == 1f, "heat scaling off: flat");
            });
            Case("Thirst_bottle_and_quality", () =>
            {
                Assert(Near(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Potable, true), 0.5f, 0.001f), "a 1.5 L bottle restores 0.5");
                Assert(Near(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Fouled, true), 0.35f, 0.001f), "T5 offline: fouled x0.7");
                Assert(Near(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Toxic, true), 0.25f, 0.001f), "toxic x0.5");
                Assert(Near(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Toxic, false), 0.5f, 0.001f), "quality off: all potable");
                Assert(RM_ThirstMath.Effective(RM_WaterQuality.Toxic, false) == RM_WaterQuality.Potable, "quality off: toxic counts as potable");
                Assert(!RM_ThirstMath.Acceptable(RM_WaterQuality.Toxic, 0.2f) && RM_ThirstMath.Acceptable(RM_WaterQuality.Toxic, 0.05f), "toxic only when parched");
                Assert(RM_ThirstMath.Better(RM_WaterQuality.Potable, 100f, RM_WaterQuality.Fouled, 1f), "quality before distance");
                Assert(RM_ThirstMath.Better(RM_WaterQuality.Potable, 1f, RM_WaterQuality.Potable, 2f) && !RM_ThirstMath.Better(RM_WaterQuality.Toxic, 0f, RM_WaterQuality.Distilled, 99f), "then distance; can-fail");
                Assert(RM_ThirstMath.FouledPoisonChance == 0.2f && RM_ThirstMath.ToxicBuildupPerDrink == 0.12f, "design §3 numbers");
            });
            Case("Thirst_dehydration_ruled", () =>
            {
                // T6 offline: need held at 0 for 1 day -> 0.30
                float sev = 0f;
                for (int i = 0; i < (int)(RM_ThirstMath.TicksPerDay / RM_ThirstMath.NeedIntervalTicks); i++)
                {
                    sev += RM_ThirstMath.DehydrationDelta(0f, RM_ThirstMath.NeedIntervalTicks);
                }
                Assert(Near(sev, 0.30f, 0.001f), "1 day at zero: 0.30, got " + sev);
                Assert(Near(RM_ThirstMath.DehydrationLethal / RM_ThirstMath.DehydrationGainPerDay, 3.33f, 0.01f), "OQ-3: death about 3 days after empty");
                Assert(RM_ThirstMath.DehydrationDelta(0.2f, 150f) == 0f, "between 0 and 0.3: holds");
                Assert(RM_ThirstMath.DehydrationDelta(0.5f, 150f) < 0f, "above 0.3: heals");
                Assert(RM_ThirstMath.Category(0f) == 3 && RM_ThirstMath.Category(0.05f) == 2 && RM_ThirstMath.Category(0.2f) == 1 && RM_ThirstMath.Category(0.5f) == 0, "thresholds 0 / 0.1 / 0.3");
            });
            Case("Thirst_defs_shipped", () =>
            {
                string dir = Path.Combine(ModRoot, "Defs", "Thirst");
                XDocument need = XDocument.Load(Path.Combine(dir, "RM_Thirst_Need.xml"));
                XElement n = Def(need, "NeedDef", "RM_Thirst");
                Assert(n != null && (string)n.Element("needClass") == "RimMandrake.FlowWorks.Thirst.Need_RM_Thirst", "RM_Thirst NeedDef");
                Assert((string)n.Element("minIntelligence") == "Animal", "OQ-5: animals are on the need list");
                XDocument hd = XDocument.Load(Path.Combine(dir, "RM_Dehydration.xml"));
                XElement h = Def(hd, "HediffDef", "RM_Dehydration");
                Assert(h != null && (string)h.Element("lethalSeverity") == "1", "readable, lethal dehydration hediff");
                Assert(h.Element("stages").Elements("li").Count() == 5, "five stages (DBH's shape)");
                XDocument th = XDocument.Load(Path.Combine(dir, "RM_Thirst_Thoughts.xml"));
                foreach (var (d, mood) in new[] { ("RM_Thought_Thirsty", "-4"), ("RM_Thought_Parched", "-10"), ("RM_Thought_Dehydrated", "-18"), ("RM_Thought_DrankDistilled", "2") })
                {
                    XElement t = Def(th, "ThoughtDef", d);
                    Assert(t != null && (string)t.Descendants("baseMoodEffect").First() == mood, d + " " + mood);
                }
                XDocument tree = XDocument.Load(Path.Combine(dir, "RM_Thirst_ThinkTree.xml"));
                var tags = tree.Descendants("insertTag").Select(e => (string)e).ToList();
                Assert(tags.Contains("Humanlike_PostDuty") && tags.Contains("Animal_PreMain"), "drink givers for humanlikes and animals");
                Assert(tree.ToString().Contains("JobGiver_RM_AnimalDrink"), "can-fail: the animal giver is wired");
            });
            Case("Thirst_bottles_generated", () =>
            {
                // T8 offline: coloured bottles exist without DBH, ingestible, Potable; only bottles are drunk
                XDocument gen = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidBottles.xml"));
                XElement rust = Def(gen, "ThingDef", "RM_Bottle_RustWater");
                Assert(rust != null && rust.Element("ingestible") != null, "RM_Bottle_RustWater: present, ingestible");
                var doers = rust.Element("ingestible").Element("outcomeDoers").Elements("li").Select(e => (string)e.Attribute("Class")).ToList();
                Assert(doers.Contains("RimMandrake.FlowWorks.Thirst.IngestionOutcomeDoer_RM_Hydrate") && doers.Contains("RimMandrake.FlowWorks.LiquidTypes.IngestionOutcomeDoer_BottleResidue"), "hydrate + residue");
                Assert((string)rust.Element("ingestible").Element("maxNumToIngestAtOnce") == "1", "one bottle per drink");
                var drinkables = gen.Descendants("ThingDef").Where(t => t.Element("ingestible") != null).Select(t => (string)t.Element("defName")).ToList();
                Assert(drinkables.Count >= 9 && drinkables.All(d => d.StartsWith("RM_Bottle_")), "only bottles are drunk: " + string.Join(",", drinkables.Where(d => !d.StartsWith("RM_Bottle_"))));
                XDocument reg = XDocument.Load(Path.Combine(LiquidDefs, "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                XElement row = reg.Root.Elements().FirstOrDefault(e => (string)e.Element("defName") == "RM_Liquid_RustWater");
                Assert(row != null && (string)row.Element("thirstQuality") == "Potable" && (string)row.Element("terrainSuite").Element("shallow") == "RM_Water_Rust", "Potable row adopting RM_Water_Rust");
                Assert(Def(gen, "ThingDef", "RM_Bucket_FreshWater").Element("ingestible") == null, "can-fail: a bucket is not drunk");
            });
            Case("Thirst_dbh_bridge_patch", () =>
            {
                string p = Path.Combine(ModRoot, "Patches", "LiquidTypes", "RM_DBH_BottleWaterExt.xml");
                XDocument d = XDocument.Load(p);
                XElement op = d.Root.Element("Operation");
                Assert((string)op.Attribute("Class") == "PatchOperationFindMod" && op.Attribute("MayRequire") == null, "FindMod-gated, no top-level MayRequire");
                var mods = op.Element("mods").Elements("li").Select(e => (string)e).ToList();
                Assert(mods.Contains("Dubs Bad Hygiene Lite") && mods.Contains("Dubs Bad Hygiene"), "Lite and full DBH by name");
                XElement gate = op.Element("match");
                Assert((string)gate.Attribute("Class") == "RimMandrake.FlowWorks.Thirst.RM_PatchOperation_ThirstBridge", "behind the dbhBottleBridge setting");
                var adds = gate.Element("operations").Elements("li").ToList();
                Assert(adds.Count >= 9 && adds.All(a => (string)a.Attribute("Class") == "PatchOperationAddModExtension"), "one AddModExtension per drinkable bottle (" + adds.Count + ")");
                Assert(adds.All(a => a.Descendants("li").Any(x => (string)x.Attribute("Class") == "DubsBadHygiene.WaterExt")), "DBH's WaterExt");
                XElement fresh = adds.First(a => ((string)a.Element("xpath")).Contains("RM_Bottle_FreshWater"));
                XElement salt = adds.First(a => ((string)a.Element("xpath")).Contains("RM_Bottle_SaltWater"));
                Assert(fresh.Descendants("SeekForThirst").First().Value == "true" && salt.Descendants("SeekForThirst").First().Value == "false", "seek only potable water");
                Assert(!d.ToString().Contains("CompContamination"), "can-fail: no second contamination system");
                Assert(!File.Exists(Path.Combine(ModRoot, "Patches", "LiquidTypes", "RM_DBH_FreshWaterDrinkables.xml")), "the hand patch it supersedes is deleted");
            });
            Case("Thirst_harmony_target_and_call_sites", () =>
            {
                string prov = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstProvider.cs"));
                RiverSwitchFlipChecks.Has(prov, @"\[HarmonyPatch\(typeof\(Pawn_NeedsTracker\), ""ShouldHaveNeed""\)\]", "postfix on Pawn_NeedsTracker.ShouldHaveNeed");
                RiverSwitchFlipChecks.Has(prov, @"__result = RM_ThirstProvider\.Eligible\(___pawn\);", "the postfix only narrows (runs when vanilla said yes)");
                RiverSwitchFlipChecks.Has(prov, @"""\[FlowWorks\] thirst provider: "" \+ mode", "T1's log line");
                // the decompiled 1.6 source, when this machine has it: the signature the patch names
                string dec = Path.Combine("/mnt/d/Luke/dev/reference/rimworld-decompiled", "RimWorld", "Pawn_NeedsTracker.cs");
                if (!File.Exists(dec)) dec = @"D:\Luke\dev\reference\rimworld-decompiled\RimWorld\Pawn_NeedsTracker.cs";
                if (File.Exists(dec))
                {
                    Assert(File.ReadAllText(dec).Contains("private bool ShouldHaveNeed(NeedDef nd)"), "1.6 signature: private bool ShouldHaveNeed(NeedDef nd)");
                }
                string need = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "Need_RM_Thirst.cs"));
                RiverSwitchFlipChecks.Has(need, @"HealthUtility\.AdjustSeverity\(pawn, RM_ThirstDefOf\.RM_Dehydration, delta\)", "the need drives the readable hediff");
                string jobs = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstJobs.cs"));
                RiverSwitchFlipChecks.Has(jobs, @"if \(pawn\.RaceProps\.Humanlike \|\| !RM_ThirstUtility\.IsThirsty\(pawn\)", "the animal giver is for animals only");
                int animal = jobs.IndexOf("class JobGiver_RM_AnimalDrink", StringComparison.Ordinal);
                int next = jobs.IndexOf("class JobGiver_RM_PackBottles", StringComparison.Ordinal);
                string animalBody = jobs.Substring(animal, next - animal);
                Assert(!animalBody.Contains("BestBottle") && !animalBody.Contains("BestTank"), "can-fail: animals drink terrain only (OQ-5)");
            });

            Case("Thirst_review_fixes_B2_B3_in_source", () =>
            {
                string util = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstUtility.cs"));
                RiverSwitchFlipChecks.Has(util, @"until - now <= NoTerrainMarkTicks\) return false;", "B2: a mark more than 600 ticks ahead is stale (thing IDs repeat across saves)");
                RiverSwitchFlipChecks.Has(util, @"noTerrainUntil\.Remove\(pawn\.thingIDNumber\);", "B2: expired and stale marks are dropped");
                string jobs = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstJobs.cs"));
                RiverSwitchFlipChecks.Has(jobs, @"!patient\.HostileTo\(pawn\)", "B3: no water for downed hostiles");
                Assert(!jobs.Contains("patient.guest != null"), "can-fail: the vacuous guest test is gone (every humanlike has a guest tracker)");
            });
        }
    }
}
