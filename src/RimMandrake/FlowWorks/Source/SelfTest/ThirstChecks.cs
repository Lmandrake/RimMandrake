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
                var P = RM_DrinkUse.Potable;
                Assert(RM_ThirstMath.Better(P, RM_WaterQuality.Potable, 100f, P, RM_WaterQuality.Fouled, 1f), "quality before distance");
                Assert(RM_ThirstMath.Better(P, RM_WaterQuality.Potable, 1f, P, RM_WaterQuality.Potable, 2f) && !RM_ThirstMath.Better(P, RM_WaterQuality.Toxic, 0f, P, RM_WaterQuality.Distilled, 99f), "then distance; can-fail");
                Assert(Near(RM_ThirstMath.Hydration(1.5f, RM_WaterQuality.Slime, true), 0.3f, 0.001f), "slime x0.6");
                Assert(RM_ThirstMath.ToxicBuildupPerDrink == 0.12f, "design §3 numbers");
            });
            Case("Thirst_use_class_gate_ruled", () =>
            {
                // THIRST_RULES_BUILD_SALT_OFF_THE_MENU, 04-merged.md §8 (owner 2026-10-17). Rule break 2: salt was drunk
                // routinely by any thirsty pawn. Now: salt/brine (BreakOnly) only inside the salt break.
                var B = RM_DrinkUse.BreakOnly; var L = RM_DrinkUse.LastResort; var P = RM_DrinkUse.Potable; var N = RM_DrinkUse.Never;
                Assert(!RM_ThirstMath.MayDrink(B, 0.2f, true, false, false, true), "a thirsty human never drinks salt routinely");
                Assert(!RM_ThirstMath.MayDrink(B, 0f, true, false, false, true), "not even dehydrated (salt is break-only, Q8)");
                Assert(RM_ThirstMath.MayDrink(B, 0.05f, true, false, true, true), "inside the salt break it is drunk");
                Assert(!RM_ThirstMath.MayDrink(L, 0.05f, true, false, false, true), "slime/toxic not while merely parched");
                Assert(RM_ThirstMath.MayDrink(L, 0f, true, false, false, true), "Q5: slime/toxic when desperate (need empty, vanilla's rotten-food rule)");
                Assert(!RM_ThirstMath.MayDrink(L, 0f, true, false, false, false), "last-resort setting off: never");
                Assert(!RM_ThirstMath.MayDrink(N, 0f, true, true, true, true), "Never is never, break or not");
                Assert(RM_ThirstMath.MayDrink(P, 0.29f, false, false, false, true), "Q12: all animals drink potable water");
                Assert(!RM_ThirstMath.MayDrink(B, 0f, false, false, false, true) && !RM_ThirstMath.MayDrink(L, 0f, false, false, false, true), "a non-native animal never drinks terrible water");
                Assert(RM_ThirstMath.MayDrink(B, 0.2f, false, true, false, true) && RM_ThirstMath.MayDrink(L, 0.2f, false, true, false, true), "Q12: a native animal drinks its biome's terrible water");
                Assert(RM_ThirstMath.Better(P, RM_WaterQuality.Potable, 999f, L, RM_WaterQuality.Toxic, 0f), "any potable beats a last resort at any distance");
                Assert(!RM_ThirstMath.Better(L, RM_WaterQuality.Distilled, 0f, P, RM_WaterQuality.Fouled, 99f), "can-fail: class before quality");
                // the shipped rows (generated registry)
                XDocument reg = XDocument.Load(Path.Combine(LiquidDefs, "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                string Use(string d) => (string)reg.Root.Elements().First(e => (string)e.Element("defName") == d).Element("useClass");
                Assert(Use("RM_Liquid_SaltWater") == "BreakOnly" && Use("RM_Liquid_Brine") == "BreakOnly", "Q8: salt and brine break-only");
                Assert(Use("RM_Liquid_ToxicWater") == "LastResort" && Use("RM_Liquid_SlimeRed") == "LastResort", "Q8/Q5: toxic and slime last resort");
                Assert(Use("RM_Liquid_FreshWater") == "Potable" && Use("RM_Liquid_IcyWater") == "Potable" && Use("RM_Liquid_RustWater") == "Potable", "fresh, icy, coloured potable");
                Assert(Use("RM_Liquid_AcidWater") == "Never" && Use("RM_Liquid_BoilingWater") == "Never" && Use("RM_Liquid_Chemfuel") == "Never", "acid, boiling (until cooled), fuel never");
                Assert(reg.Root.Elements().All(e => e.Element("useClass") != null), "every row carries a use class");
            });
            Case("Thirst_autofill_potable_only_in_source", () =>
            {
                // rule break 1: auto-fill gathered ANY liquid. The unforced fill and fill-from-tank now take Potable only.
                string b = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "RM_LiquidBottleUtility.cs"));
                RiverSwitchFlipChecks.Has(b, @"potableOnly: !ordered\)", "the fill search is potable-only unless ordered");
                RiverSwitchFlipChecks.Has(b, @"if \(potableOnly && !candidate\.AutoGathered", "non-potable cells are skipped");
                string g = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "WorkGiver_FillBottle.cs"));
                Assert(System.Text.RegularExpressions.Regex.Matches(g, @"TryFindFillCell\(pawn, t, out cell, out liquid, out refusal, forced\)").Count == 2, "both fill-giver calls pass forced as the order");
                string t = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "RM_LiquidTankUtility.cs"));
                RiverSwitchFlipChecks.Has(t, @"if \(!ordered && !candidate\.storedLiquid\.AutoGathered\)", "a brine tank drains into containers only by order");
                string tg = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "WorkGiver_FillBottleFromTank.cs"));
                Assert(System.Text.RegularExpressions.Regex.Matches(tg, @"out refusal, forced\)").Count == 2, "can-fail: both drain calls pass forced");
                string u = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstUtility.cs"));
                Assert(!u.Contains("Acceptable("), "the old quality-only gate is gone from the drink searches");
            });
            Case("Thirst_slime_last_resort_ruled", () =>
            {
                // Q5/Q6/Q7 (owner 2026-10-17): slime is a desperate drink, "Much worse", bottled only by order.
                XDocument reg = XDocument.Load(Path.Combine(LiquidDefs, "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                XElement Row(string d) => reg.Root.Elements().First(e => (string)e.Element("defName") == d);
                string RimRoot = Path.GetDirectoryName(ModRoot);
                // a COMPOSED biome member's own packageId never loads: its MayRequire must name Baroque Biomes' id
                string compose = File.ReadAllText(Path.Combine(RimRoot, "Biomes.compose.json"));
                int wave = int.Parse(System.Text.RegularExpressions.Regex.Match(compose, @"""compose_wave""\s*:\s*(\d+)").Groups[1].Value);
                string Pkg(string mod)
                {
                    var m = System.Text.RegularExpressions.Regex.Match(compose, @"""key"":\s*""" + mod + @""",\s*""source"":\s*""[^""]+"",\s*""group"":\s*""[^""]+"",\s*""wave"":\s*(\d+)");
                    if (m.Success && int.Parse(m.Groups[1].Value) <= wave) return "mandrake.rm.biomes";
                    return (string)XDocument.Load(Path.Combine(RimRoot, mod, "About", "About.xml")).Root.Element("packageId");
                }
                Assert(Pkg("TheRot") == "mandrake.rm.biomes", "can-fail: The Rot is composed (its own id would never load)");
                bool DefOnDisk(string mod, string type, string def) => Directory.GetFiles(Path.Combine(RimRoot, mod, "Defs"), "*.xml", SearchOption.AllDirectories)
                    .Any(f => XDocument.Load(f).Descendants(type).Any(e => (string)e.Element("defName") == def));
                var want = new[] { ("RM_Liquid_SlimeRed", "RM_ContagionTouched", "Contagion"), ("RM_Liquid_SlimeWhite", "RM_SporeFlesh", "TheRot"),
                                   ("RM_Liquid_SlimeYellow", "RM_SlimeNausea", null), ("RM_Liquid_SlimeGreen", null, "GelatinousSlime"), ("RM_Liquid_LivingSlime", null, "GelatinousSlime") };
                foreach (var (d, hediff, mod) in want)
                {
                    XElement r = Row(d);
                    Assert((string)r.Element("thirstQuality") == "Slime" && (string)r.Element("useClass") == "LastResort", d + ": slime, last resort");
                    Assert((string)r.Element("drinkThought") == "RM_Thought_DrankSlime", d + ": the massive mood hit");
                    var outs = r.Element("drinkOutcomes").Elements("li").ToList();
                    Assert(outs.Any(o => (string)o.Element("hediffDef") == "RM_SlimePurge"), d + ": the day of purging");
                    if (hediff != null)
                    {
                        XElement o = outs.First(x => (string)x.Element("hediffDef") == hediff);
                        if (mod != null)
                        {
                            Assert((string)o.Attribute("MayRequire") == Pkg(mod), d + ": " + hediff + " guarded by " + mod + "'s packageId");
                            Assert(DefOnDisk(mod, "HediffDef", hediff), "can-fail: " + hediff + " is a real HediffDef in " + mod);
                        }
                    }
                    else
                    {
                        XElement o = outs.First(x => ((string)x.Attribute("Class")).EndsWith("IngestionOutcomeDoer_SlimeDose"));
                        Assert((string)o.Attribute("MayRequire") == Pkg("GelatinousSlime"), d + ": slime dose guarded");
                        Assert(File.ReadAllText(Path.Combine(RimRoot, "GelatinousSlime", "Source", "SlimeIngestion.cs")).Contains("public class IngestionOutcomeDoer_SlimeDose : IngestionOutcomeDoer"), "the slime-dose doer exists and is public");
                        Assert((string)r.Element("drinkOutcomeCount") == "5", d + ": full exposure = five doses");
                    }
                }
                Assert((string)Row("RM_Liquid_SlimeRed").Descendants("severity").First() == "1", "red: Contagion at full right away");
                Assert((string)Row("RM_Liquid_LivingSlime").Attribute("MayRequire") == Pkg("GelatinousSlime"), "the living-slime row only with Gelatinous Slime");
                XDocument p = XDocument.Load(Path.Combine(ModRoot, "Patches", "Thirst", "RM_LivingSlimeDrinkable.xml"));
                Assert((string)p.Root.Element("Operation").Attribute("Class") == "PatchOperationConditional" && p.Descendants("liquid").First().Value == "RM_Liquid_LivingSlime", "RM_Slime_Liquid points at the living-slime row, conditionally");
                Assert(DefOnDisk("GelatinousSlime", "TerrainDef", "RM_Slime_Liquid"), "can-fail: the patched terrain exists");
                XDocument lr = XDocument.Load(Path.Combine(ModRoot, "Defs", "Thirst", "RM_Thirst_LastResort.xml"));
                XElement purge = Def(lr, "HediffDef", "RM_SlimePurge");
                Assert(purge.Descendants("disappearsAfterTicks").First().Value == "60000" && purge.Descendants("factor").First().Value == "1.5", "purge: one day, thirst x1.5");
                Assert((string)Def(lr, "ThoughtDef", "RM_Thought_DrankSlime").Descendants("baseMoodEffect").First() == "-20", "massive: -20");
                Assert(Def(lr, "HediffDef", "RM_SlimeNausea").Descendants("vomitMtbDays").Any(), "yellow: nausea and vomiting");
                XDocument gen = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidBottles.xml"));
                Assert(Def(gen, "ThingDef", "RM_Bottle_SlimeRed")?.Element("ingestible") != null && Def(gen, "ThingDef", "RM_Barrel_SlimeYellow") != null, "Q7: slime bottles/buckets/barrels exist");
                string u = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstUtility.cs"));
                RiverSwitchFlipChecks.Has(u, @"QualityEffects\(pawn, q, source\);\s*RowEffects\(pawn, liquid, source\);", "every drink route runs the row's effects");
                RiverSwitchFlipChecks.Has(u, @"GetModExtension<RM_DrinkableTerrainExtension>\(\)\?\.liquid", "the terrain adapter is read by DrinkLiquidAt");
            });
            Case("Thirst_salt_break_ruled", () =>
            {
                // Q8 (owner 2026-10-17): a mood break that also needs thirst; brine = salt; no re-entry while poisoned.
                Assert(RM_ThirstMath.SaltBreakCan(0.05f, false, false, true), "parched, no potable, salt in reach: can break");
                Assert(!RM_ThirstMath.SaltBreakCan(0.2f, false, false, true), "merely thirsty: no");
                Assert(!RM_ThirstMath.SaltBreakCan(0.05f, true, false, true), "still salt-poisoned: no re-entry");
                Assert(!RM_ThirstMath.SaltBreakCan(0.05f, false, true, true), "fresh water in reach: no");
                Assert(!RM_ThirstMath.SaltBreakCan(0.0f, false, false, false), "can-fail: no salt to drink: no");
                XDocument d = XDocument.Load(Path.Combine(ModRoot, "Defs", "Thirst", "RM_Thirst_SaltBreak.xml"));
                XElement br = Def(d, "MentalBreakDef", "RM_Break_DrinkBrine");
                Assert(br != null && (string)br.Element("intensity") == "Major" && (string)br.Element("mentalState") == "RM_DrinkBrine", "an ordinary mood-pool break (Q8 b: low mood like other breaks)");
                XElement st = Def(d, "MentalStateDef", "RM_DrinkBrine");
                Assert((string)st.Element("workerClass") == "RimMandrake.FlowWorks.Thirst.MentalStateWorker_RM_DrinkBrine", "the thirst half is the state worker");
                XElement sp = Def(d, "HediffDef", "RM_SaltPoisoning");
                Assert((string)sp.Element("lethalSeverity") == "1" && sp.Descendants("factor").First().Value == "3", "salt poisoning: lethal untreated, thirst x3");
                Assert((string)sp.Element("tendable") == "true" && sp.Descendants("severityPerDayTended").Any(), "a doctor brings it down");
                XDocument reg = XDocument.Load(Path.Combine(LiquidDefs, "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                foreach (string row in new[] { "RM_Liquid_SaltWater", "RM_Liquid_Brine" })
                {
                    XElement r = reg.Root.Elements().First(e => (string)e.Element("defName") == row);
                    Assert((string)r.Element("drinkThought") == "RM_Thought_SaltRelief" && r.Descendants("hediffDef").Any(h => h.Value == "RM_SaltPoisoning"), row + ": relief then poisoning");
                }
                XDocument tt = XDocument.Load(Path.Combine(ModRoot, "Patches", "Thirst", "RM_SaltBreakThinkTree.xml"));
                Assert(tt.Descendants("xpath").First().Value.Contains("MentalStateNonCritical") && tt.Descendants("state").First().Value == "RM_DrinkBrine"
                    && tt.ToString().Contains("JobGiver_RM_DrinkBrine"), "the state's job giver is wired into vanilla's mental-state tree");
                // EnableDefaultCompileItems is false: a .cs missing from the Compile list builds into nothing, silently
                string csproj = File.ReadAllText(Path.Combine(ModRoot, "Source", "RimMandrake_FlowWorks.csproj"));
                foreach (string f in Directory.GetFiles(Path.Combine(ModRoot, "Source", "Thirst"), "*.cs"))
                {
                    Assert(csproj.Contains(@"Include=""Thirst\" + Path.GetFileName(f) + @""""), "csproj compiles Thirst\\" + Path.GetFileName(f));
                }
                string sb = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_SaltBreak.cs"));
                RiverSwitchFlipChecks.Has(sb, @"RM_ThirstMath\.SaltBreakCan\(level, poisoned, RM_SaltBreakUtility\.PotableReachable\(pawn, level\)", "the worker asks the tested rule");
                RiverSwitchFlipChecks.Has(sb, @"float level = RM_ThirstUtility\.LevelAny\(pawn\);", "Q11: the break reads whichever thirst runs (Dubs' too)");
                Assert(!RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstUtility.cs")).Contains("AddFoodPoisoningHediff"), "can-fail: salt's routine food poisoning is gone (its harm is salt poisoning now)");
            });
            Case("Thirst_awkward_access_ruled", () =>
            {
                // Q1-Q4 (owner 2026-10-17): civilized access is free, awkward access costs a little; hardy and wild never mind.
                Assert(!RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, true) && !RM_ThirstMath.Awkward(RM_DrinkSource.Tank, true), "Q1: a bottle or a tap at home is free");
                Assert(!RM_ThirstMath.Awkward(RM_DrinkSource.Terrain, false) && !RM_ThirstMath.Awkward(RM_DrinkSource.Terrain, true), "Q2: ponds and rivers are free, anywhere");
                Assert(RM_ThirstMath.Awkward(RM_DrinkSource.Caravan, true) && RM_ThirstMath.Awkward(RM_DrinkSource.Container, true), "travel and scooping from a bucket/barrel are awkward");
                Assert(RM_ThirstMath.Awkward(RM_DrinkSource.Bottle, false), "can-fail: a bottle out in the field is awkward");
                Assert(RM_ThirstMath.RoughExempt(false, false, false) && RM_ThirstMath.RoughExempt(true, true, false) && RM_ThirstMath.RoughExempt(true, false, true), "Q4: animals, wild people, tribals exempt");
                Assert(!RM_ThirstMath.RoughExempt(true, false, false), "a civilized colonist is not");
                var P = RM_DrinkUse.Potable; var q = RM_WaterQuality.Potable;
                Assert(RM_ThirstMath.BetterPick(P, false, q, 900f, P, true, q, 1f), "a free tap far away beats a bucket at the feet");
                Assert(RM_ThirstMath.BetterPick(P, true, q, 1f, RM_DrinkUse.LastResort, false, q, 1f), "can-fail: but use class still comes first");
                XDocument th = XDocument.Load(Path.Combine(ModRoot, "Defs", "Thirst", "RM_Thirst_Thoughts.xml"));
                XElement rough = Def(th, "ThoughtDef", "RM_Thought_DrankRough");
                var nul = rough.Element("nullifyingTraits").Elements("li").Select(e => e.Value).ToList();
                Assert(nul.Count == 3 && nul.Contains("Ascetic") && nul.Contains("Tough") && nul.Contains("Undergrounder"), "Q3: Ascetic, Tough, Undergrounder (and no genes)");
                Assert((string)rough.Descendants("baseMoodEffect").First() == "-3", "small");
                XDocument b = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidBottles_Base.xml"));
                foreach (string bse in new[] { "RM_BucketItemBase", "RM_BarrelItemBase" })
                {
                    XElement d = b.Descendants("ThingDef").First(e => (string)e.Attribute("Name") == bse);
                    Assert(d.Element("comps").Elements("li").Any(li => (string)li.Attribute("Class") == "RimMandrake.FlowWorks.Thirst.CompProperties_RM_DrawnLitres"), bse + ": remembers what was drawn");
                }
                XElement bottleBase = b.Descendants("ThingDef").First(e => (string)e.Attribute("Name") == "RM_BottleItemBase");
                Assert(!bottleBase.ToString().Contains("DrawnLitres"), "can-fail: a bottle is drunk whole, no partial state");
                string m = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "RM_ContainerMaterials.cs"));
                RiverSwitchFlipChecks.Has(m, @"full - Thirst\.CompRM_DrawnLitres\.DrawnUnits\(container\)", "every content read subtracts what was drunk");
                string j = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_ThirstJobs.cs"));
                RiverSwitchFlipChecks.Has(j, @"RM_ThirstMath\.BetterPick\(u, a, q, d, pu, pa, pq, pd\)", "the giver ranks awkward sources after free ones");
                RiverSwitchFlipChecks.Has(j, @"RM_DrinkSource\.Terrain\);", "a pond drink is marked terrain (free)");
            });
            Case("Thirst_reserve_orders_sprinklers_ruled", () =>
            {
                // Q10: drinkers first on a shared net; Q9: a Fill tank holding the liquid is the standing order; Q12: no brine spray
                Assert(RM_ThirstMath.Spendable(5000, 2000, true) == 3000 && RM_ThirstMath.Spendable(1500, 2000, true) == 0, "potable: the reserve is kept back");
                Assert(RM_ThirstMath.Spendable(1500, 2000, false) == 1500, "can-fail: salt/fuel keep no reserve");
                Assert(RM_ThirstMath.Spendable(1500, 0, true) == 1500, "reserve 0 = off");
                string r = RiverSwitchFlipChecks.Src(Path.Combine("Thirst", "RM_DrinkReserve.cs"));
                RiverSwitchFlipChecks.Has(r, @"RM_ThirstMath\.Spendable\(available, ReserveUnits, liquid != null && liquid\.AutoGathered\)", "the reserve applies to potable liquid only");
                foreach (var (file, what) in new[] { ("Machinery/CompLiquidConverter.cs", "stills and converters"), ("Machinery/Kits/RM_LiquidBath.cs", "baths"),
                                                     ("Machinery/Kits/RM_LiquidReaction.cs", "reaction vats"), ("Sprinklers/RM_Sprinkle.cs", "sprinklers") })
                {
                    Assert(RiverSwitchFlipChecks.Src(file.Replace('/', Path.DirectorySeparatorChar)).Contains("RM_DrinkReserve.Spendable("), what + " read the reserve");
                }
                Assert(!RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "CompLiquidPipeAdapter.cs")).Contains("RM_DrinkReserve"), "the VE pipe adapter may be feeding taps: not held back");
                string sp = RiverSwitchFlipChecks.Src(Path.Combine("Sprinklers", "RM_Sprinkle.cs"));
                RiverSwitchFlipChecks.Has(sp, @"t\.storedLiquid\.neverSprayed\) continue;", "a sprinkler never picks salt or brine");
                XDocument reg = XDocument.Load(Path.Combine(LiquidDefs, "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                var sprayless = reg.Root.Elements().Where(e => (string)e.Element("neverSprayed") == "true").Select(e => (string)e.Element("defName")).OrderBy(x => x).ToList();
                Assert(sprayless.SequenceEqual(new[] { "RM_Liquid_Brine", "RM_Liquid_SaltWater" }), "exactly salt and brine are never sprayed: " + string.Join(",", sprayless));
                string b = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "RM_LiquidBottleUtility.cs"));
                RiverSwitchFlipChecks.Has(b, @"if \(potableOnly && !candidate\.AutoGathered && !standing\.Contains\(candidate\)\)", "Q9: a standing order lets pawns gather that liquid");
                RiverSwitchFlipChecks.Has(b, @"!l\.AutoGathered && t\.TakesBottles\(false\) && t\.CanAccept\(", "the order is a Fill tank already holding it, with room");
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
