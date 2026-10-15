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
            Case("ReviewFix_PitExposure_marker_narrows_comfort_and_leaves_off_map", () =>
            {
                // Redesign 2026-10-11 (design/RimMandrake/pit_exposure_to_the_elements_2026-10-11.md): a flat marker whose one
                // stage narrows the comfortable range; the random heatstroke stage, the severity maths and the recovery comp are gone.
                XElement h = XDocument.Load(Path.Combine(Defs, "Pits", "HediffDefs", "Pit_Hediffs.xml"))
                    .Descendants("HediffDef").First(e => (string)e.Element("defName") == "RM_PitExposure");
                var stages = h.Element("stages").Elements("li").ToList();
                Assert(stages.Count == 1, "one stage (the heatstruck stage is deleted): " + stages.Count);
                Assert(!h.Descendants("hediffGivers").Any() && !h.Descendants("painOffset").Any(), "can-fail: no random Heatstroke giver, no pain");
                Assert(h.Element("initialSeverity") == null && h.Element("maxSeverity") == null, "no severity build-up");
                XElement so = stages[0].Element("statOffsets");
                Assert(so != null && (string)so.Element("ComfyTemperatureMin") == "8" && (string)so.Element("ComfyTemperatureMax") == "-8",
                    "the stage narrows the comfort range 8 C each way (owner Q1)");
                Assert(h.Element("comps")?.Elements("li").Any(li => (string)li.Attribute("Class") == "RimMandrake.FlowWorks.HediffCompProperties_PitExposureMarker") == true,
                    "the marker comp is on the def");
                string src = Src("RM_PitExposure.cs");
                Assert(!src.Contains("HediffComp_PitExposureRecovery") && !src.Contains("NextSeverity"), "can-fail: the recovery comp and severity maths are deleted");
                Has(src, @"public override bool CompShouldRemove => base\.CompShouldRemove \|\| !RimMandrakeFlowWorksSettings\.pitExposureEnabled \|\| !Pawn\.Spawned;",
                    "the marker goes off the map and with the setting off");
                Has(src, @"if \(!RimMandrakeFlowWorksSettings\.pitExposureEnabled \|\| Find\.TickManager\.TicksGame % IntervalTicks != 0\) \{ return; \}",
                    "Tick owns spawned pawns while the setting is on");
                Has(src, @"if \(ElementsHurting\(p\)\) \{ p\.guest\.resistance = RM_PitExposureMath\.NextResistance\(",
                    "resistance falls only while the elements hurt (owner Q2)");
                Has(src, @"RM_Patch_PitRoomCoupling", "the pit-room coupling patch is KEPT until its live check");
                Has(src, @"if \(offsets\[i\]\.stat == StatDefOf\.ComfyTemperatureMin\) \{ offsets\[i\]\.value = n; \} else if \(offsets\[i\]\.stat == StatDefOf\.ComfyTemperatureMax\) \{ offsets\[i\]\.value = -n; \}",
                    "ApplyNarrowing raises the comfort minimum by n and lowers the maximum by n (the setting reaches the stage)");
                Has(src, @"ApplyNarrowing\(def\); IReadOnlyList<Pawn> pawns", "Tick applies the setting every interval");
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
                Has(src, @"ClearFillTerrain\(c\); if \(!ReattachIfDetachedBed\(c, i\) && !ReturnUndetachedBedCut\(c, i\)\) \{ RestoreOriginalTerrain\(c\); \} //[^\n]*?if \(fluidGrid != null\) \{ fluidGrid\[i\] = 0; \}",
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
                // POND_ELEVATION_BUILD_LAKES_RUN_DEEP: the live set moved to RM_RecessionSet (the wet squares, IsSourceCell) and the
                // counts to levels (RM_BedMath.ShouldShed / CanRestore); the review's point, count WET squares, still holds.
                Has(src, @"while \(RM_BedMath\.ShouldShed\(recession\.WetLevels, recession\.Count, supported, body\.stock, keepLast\) && guard\+\+ < 64\)", "Recede counts the live set");
                Has(src, @"i => owner\.IsSourceCell\(map\.cellIndices\.IndexToCell\(i\)\),", "the live set is the wet squares");
                Has(src, @"long wetLevels = recession\.WetLevels; int wet = recession\.Count;", "Restore counts wet cells");
                Has(src, @"while \(body\.receded\.Count > 0 && guard\+\+ < 64\)", "Restore loops on the stack");
                Has(src, @"if \(!owner\.IsExcavated\(c\) && !RM_BedMath\.CanRestore\(wetLevels, wet, bed, supported, body\.stock, keepLast\)\) \{ break; \}", "and stops when the next square's bed does not fit");
                Has(src, @"RM_RestoreResult r = owner\.RestoreOriginalTerrain\(c\); if \(r == RM_RestoreResult\.Restored\) \{ wet\+\+; wetLevels \+= bed; \}", "a restored cell counts once, and only when the write took");
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
