// FlowWorks code-review batches 2-4 (2026-10-11): offline proofs for the behaviour fixes. Each reads the SHIPPED XML
// or the PRODUCTION source (whitespace collapsed, RiverSwitchFlipChecks.Src) and, where the arithmetic is Verse-free,
// runs it. NOT proven here: anything a live map decides (a hediff ticking on a caravan pawn, a bottle landing on the
// floor, the power net reading 0 W). Those need a live row.
using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ReviewFixChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Defs => Path.GetDirectoryName(ContainerMatFixture.Root());

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static void Has(string src, string pattern, string what) => RiverSwitchFlipChecks.Has(src, pattern, what);

        public static void Run(Action<string, Action> Case)
        {
            Case("ReviewFix_PitExposure_first_exposure_builds_up", () =>
            {
                XElement h = XDocument.Load(Path.Combine(Defs, "Pits", "HediffDefs", "Pit_Hediffs.xml"))
                    .Descendants("HediffDef").FirstOrDefault(e => (string)e.Element("defName") == "RM_PitExposure");
                Assert(h != null, "RM_PitExposure shipped");
                float init = float.Parse((string)h.Element("initialSeverity") ?? "0.5", System.Globalization.CultureInfo.InvariantCulture);
                float heatstruck = h.Element("stages").Elements("li")
                    .Select(li => (string)li.Element("minSeverity")).Where(v => v != null)
                    .Select(v => float.Parse(v, System.Globalization.CultureInfo.InvariantCulture)).Min();
                Assert(init > 0f && init < RM_PitExposureMath.SeverityGainPerInterval, "initialSeverity is set near 0 (engine default is 0.5): " + init);
                float s = init;
                int intervals = 0;
                while (s < heatstruck && intervals < 1000) { s = RM_PitExposureMath.NextSeverity(s, true); intervals++; }
                Assert(intervals > 20, "heatstruck takes a build-up, not the first interval (" + intervals + " intervals)");
                // can-fail: the old default would have been heatstruck on the first interval
                Assert(RM_PitExposureMath.NextSeverity(0.5f, true) >= heatstruck, "the 0.5 default would skip the build-up");
            });

            Case("ReviewFix_PitExposure_recovers_off_map_and_with_setting_off", () =>
            {
                XElement h = XDocument.Load(Path.Combine(Defs, "Pits", "HediffDefs", "Pit_Hediffs.xml"))
                    .Descendants("HediffDef").First(e => (string)e.Element("defName") == "RM_PitExposure");
                Assert(h.Element("comps")?.Elements("li").Any(li => (string)li.Attribute("Class") == "RimMandrake.FlowWorks.HediffCompProperties_PitExposureRecovery") == true,
                    "the recovery comp is on the def");
                string src = Src("RM_PitExposure.cs");
                Has(src, @"class HediffComp_PitExposureRecovery : HediffComp_SeverityModifierBase", "the comp uses the engine's severity interval");
                Has(src, @"compClass = typeof\(HediffComp_PitExposureRecovery\);", "properties point at the comp");
                Has(src, @"return RimMandrakeFlowWorksSettings\.pitExposureEnabled && Pawn\.Spawned \? 0f : -DecayPerDay;",
                    "comp decays exactly where Tick cannot (setting off, or not spawned)");
                Has(src, @"DecayPerDay = RM_PitExposureMath\.SeverityDecayPerInterval \* \(GenDate\.TicksPerDay / \(float\)RM_PitExposure\.IntervalTicks\);",
                    "off-map rate equals the on-map rate");
                Has(src, @"if \(!RimMandrakeFlowWorksSettings\.pitExposureEnabled \|\| Find\.TickManager\.TicksGame % IntervalTicks != 0\) \{ return; \}",
                    "Tick still owns spawned pawns while the setting is on");
            });

            Case("ReviewFix_BottleResidue_lands_on_the_map_when_there_is_one", () =>
            {
                string src = Src("LiquidTypes", "IngestionOutcomeDoer_BottleResidue.cs");
                int place = src.IndexOf("GenPlace.TryPlaceThing(residue, pawn.PositionHeld, map, ThingPlaceMode.Near)", StringComparison.Ordinal);
                int inv = src.IndexOf("pawn.inventory.innerContainer.TryAdd(residue)", StringComparison.Ordinal);
                Assert(place >= 0 && inv >= 0 && place < inv, "the map is tried before the inventory");
                Has(src, @"if \(map != null && pawn\.SpawnedOrAnyParentSpawned && GenPlace\.TryPlaceThing", "placed only when the drinker is on a map");
                Has(src, @"innerContainer\.TryAdd\(residue\)\) \{ return; \} residue\.Destroy\(\);", "off a map: inventory, else destroyed");
            });

            Case("ReviewFix_Drill_draws_no_power_when_switched_off", () =>
            {
                string src = Src("Drilling", "Building_LiquidDrill.cs");
                Has(src, @"power\.PowerOutput = RimMandrakeFlowWorksSettings\.liquidDrillingEnabled \? -power\.Props\.PowerConsumption : 0f;",
                    "power follows the setting");
                int set = src.IndexOf("power.PowerOutput =", StringComparison.Ordinal);
                int gate = src.IndexOf("if (!RimMandrakeFlowWorksSettings.liquidDrillingEnabled)", StringComparison.Ordinal);
                Assert(set >= 0 && gate >= 0 && set < gate, "power is set before the setting's early return");
            });

            Case("ReviewFix_Excavation_fill_to_surface_clears_fluid_key", () =>
            {
                string src = Src("RM_MapComponent_Excavation.cs");
                Has(src, @"ClearFillTerrain\(c\); RestoreOriginalTerrain\(c\); //[^\n]*?if \(fluidGrid != null\) \{ fluidGrid\[i\] = 0; \}",
                    "the surface branch clears the fluid key after ClearFillTerrain");
            });

            Case("ReviewFix_ShootingCache_forgets_a_removed_map", () =>
            {
                Has(Src("RM_MapComponent_Excavation.cs"), @"public override void MapRemoved\(\) \{ base\.MapRemoved\(\); RM_SuperdeepShooting\.Forget\(map\); \}",
                    "the component drops the static cache when its map goes");
                Has(Src("RM_Patch_SuperdeepShooting.cs"), @"if \(ReferenceEquals\(map, cachedMap\)\) \{ cachedMap = null; cachedEngine = null; \}",
                    "Forget nulls both halves of the cache");
            });

            Case("ReviewFix_Stock_recession_and_refill_count_wet_cells", () =>
            {
                string src = Src("RM_LiquidStock.cs");
                Has(src, @"while \(live\.Count > supported && live\.Count > 0 && guard\+\+ < 64\)", "Recede counts the live set");
                Has(src, @"if \(owner\.IsSourceCell\(body\.cells\[i\]\)\) \{ wet\+\+; \}", "Restore counts wet cells");
                Has(src, @"while \(body\.receded\.Count > 0 && wet < supported && guard\+\+ < 64\)", "Restore loops on wet cells");
                Has(src, @"owner\.RestoreOriginalTerrain\(c\); wet\+\+; \}", "a restored cell counts once");
                Assert(!Regex.IsMatch(src, @"ActiveCellCount [<>] supported"), "can-fail: no loop compares ActiveCellCount to supported");
            });

            Case("ReviewFix_Settings_reset_clears_disabledFluids", () =>
            {
                string src = Src("RimMandrakeFlowWorksMod.cs");
                Has(src, @"if \(n == nameof\(disabledFluids\)\) \{ disabledFluids\?\.Clear\(\); continue; \}", "ResetFields clears the list");
                Has(src, @"Section\(list, ""Pits, ladders and shooting"", new\[\] \{[^}]*""disabledFluids"" \}\)", "the section's reset names it");
            });

            Case("ReviewFix_LiquidDef_unread_fields_are_not_forms", () =>
            {
                string src = Src("LiquidTypes", "LiquidDef.cs");
                Match m = Regex.Match(src, @"bool hasForm = ([^;]*);");
                Assert(m.Success, "hasForm found");
                Assert(!m.Groups[1].Value.Contains("trade") && !m.Groups[1].Value.Contains("cuisineTags"), "trade and cuisine do not count as a form");
                Assert(m.Groups[1].Value.Contains("thirstQuality.HasValue"), "can-fail: the read forms are still there");
            });
        }
    }
}
