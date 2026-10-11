// RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED: offline flip proofs for the eleven Rivers Mod Settings toggles that no
// component claimed (validation.py RIVER_TOGGLES_OWED), on the GimmeSomeSlack SwitchFlipChecks pattern. Each case
// flips one setting through its Verse-free RM_RiverMath gate and requires the outcome to change, then reads the
// PRODUCTION source and requires the call site to pass that setting into that gate (so the flip proven here is the
// flip the game makes). Case names are `RiverSwitchFlip_<toggle>`; validation.py's rivers_switch_flips chain reads
// them by that name. Also the offline halves of three walk lines (flier never carried, stake snap order, size).
// NOT proven here: anything a live map decides (a vanilla flood actually spawning, a pawn actually routing, the
// bruise roll landing). Those stay owed as live rows.
using System;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks.Rivers;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class RiverSwitchFlipChecks
    {
        private static string dir;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>Production source, whitespace collapsed so a call split across lines matches one regex.</summary>
        internal static string Src(string rel)
        {
            if (dir == null)
            {
                for (DirectoryInfo d = new DirectoryInfo(AppContext.BaseDirectory); d != null && dir == null; d = d.Parent)
                {
                    foreach (string cand in new[] { d.FullName, Path.Combine(d.FullName, "Source"),
                                                    Path.Combine(d.FullName, "src", "RimMandrake", "FlowWorks", "Source") })
                    {
                        if (File.Exists(Path.Combine(cand, "Rivers", "RM_RiverMath.cs")))
                        {
                            dir = cand;
                            break;
                        }
                    }
                }
                Assert(dir != null, "found FlowWorks Source/Rivers above " + AppContext.BaseDirectory);
            }
            return Regex.Replace(File.ReadAllText(Path.Combine(dir, rel)), @"\s+", " ");
        }

        internal static void Has(string src, string pattern, string what)
        {
            Assert(Regex.IsMatch(src, pattern), "call site: " + what + "  (pattern " + pattern + ")");
        }

        private const string S = @"RM_RiversSettings\.";

        public static void Run(Action<string, Action> Case)
        {
            const int M = RM_RiverMath.LaneMargin, C = RM_RiverMath.LaneCentre;

            Case("RiverSwitchFlip_riverWorksEnabled", () =>
            {
                Assert(RM_RiverMath.CurrentOn(true, true) && !RM_RiverMath.CurrentOn(false, true), "master off stops the current");
                Assert(RM_RiverMath.WorksOn(true, true) && !RM_RiverMath.WorksOn(false, true), "master off stops the works");
                Assert(RM_RiverMath.AvoidanceCost(true, true, true, true, 600, 120) == 600
                       && RM_RiverMath.AvoidanceCost(false, true, true, true, 600, 120) == 0, "master off adds no path cost");
                string set = Src(Path.Combine("Rivers", "RM_RiversSettings.cs"));
                Has(set, @"CurrentActive => RM_RiverMath\.CurrentOn\(riverWorksEnabled, surfaceCurrentEnabled\)", "CurrentActive passes riverWorksEnabled");
                Has(set, @"WorksActive => RM_RiverMath\.WorksOn\(riverWorksEnabled, bankWorksEnabled\)", "WorksActive passes riverWorksEnabled");
                Has(Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs")), @"MapComponentTick\(\) \{ if \(!" + S + @"CurrentActive\) \{",
                    "the current's tick returns first on !CurrentActive");
                Has(Src(Path.Combine("Rivers", "RM_RiverWorks.cs")), @"AvoidanceCost\(" + S + @"riverWorksEnabled,", "path cost passes riverWorksEnabled");
                string q = Src(Path.Combine("Quarry", "RM_QuarrySettings.cs"));
                Has(q, @"SluiceActive => sluiceBoxEnabled && Rivers\." + S + @"riverWorksEnabled;", "sluice gated on riverWorksEnabled");
                Has(q, @"PanningActive => panningEnabled && Rivers\." + S + @"riverWorksEnabled;", "panning gated on riverWorksEnabled");
            });

            Case("RiverSwitchFlip_scaleWithRiverSize", () =>
            {
                float creek = RM_RiverMath.SizeFactor(4f), huge = RM_RiverMath.SizeFactor(30f);
                Assert(creek < 1f && RM_RiverMath.SizeFactor(14f) > 1f && huge > 1f, "creek < 1 < large/huge (walk: bigger rivers shove harder)");
                int On(float f) => RM_RiverMath.Cadence(C, false, true, 1f, RM_RiverMath.EffectiveSizeFactor(true, f), 45, 90, 2f);
                int Off(float f) => RM_RiverMath.Cadence(C, false, true, 1f, RM_RiverMath.EffectiveSizeFactor(false, f), 45, 90, 2f);
                Assert(On(huge) < On(creek), "on: a huge river shoves faster than a creek (" + On(huge) + " vs " + On(creek) + ")");
                Assert(Off(huge) == Off(creek) && Off(huge) == 45, "off: every river shoves the same (" + Off(huge) + "," + Off(creek) + ")");
                Has(Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs")),
                    @"RM_RiverMath\.Cadence\([^;]*RM_RiverMath\.EffectiveSizeFactor\(" + S + @"scaleWithRiverSize, sizeFactor\)", "CadenceFor passes scaleWithRiverSize");
                Has(Src(Path.Combine("Quarry", "RM_PlacerWorks.cs")), @"if \(comp == null \|\| !" + S + @"scaleWithRiverSize\) \{ return 1f; \}",
                    "the placer's size factor is 1 with scaling off");
            });

            Case("RiverSwitchFlip_floodSurgeEnabled", () =>
            {
                Assert(RM_RiverMath.Surges(true, true) && !RM_RiverMath.Surges(false, true) && !RM_RiverMath.Surges(true, false), "surge needs the setting and a flood");
                int marginOn = RM_RiverMath.Cadence(M, RM_RiverMath.Surges(true, true), true, 1f, 1f, 45, 90, 2f);
                int marginOff = RM_RiverMath.Cadence(M, RM_RiverMath.Surges(false, true), true, 1f, 1f, 45, 90, 2f);
                int centreOn = RM_RiverMath.Cadence(C, RM_RiverMath.Surges(true, true), true, 1f, 1f, 45, 90, 2f);
                Assert(marginOn == 45 && marginOff == 90 && centreOn < 45, "in a flood: on -> edge lane runs as fast lane and fast lane doubles (" + marginOn + "/" + marginOff + "/" + centreOn + ")");
                Assert(RM_RiverMath.BehavesAsCentre(M, RM_RiverMath.Surges(true, true)) && !RM_RiverMath.BehavesAsCentre(M, RM_RiverMath.Surges(false, true)),
                       "in a flood: on -> the edge lane is inescapable, off -> it is not");
                string cur = Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs"));
                Has(cur, @"surge = RM_RiverMath\.Surges\(" + S + @"floodSurgeEnabled, RM_RiverWorks\.FloodActive\(map\)\);", "the scan passes floodSurgeEnabled");
                Has(cur, @"RM_RiverMath\.Cadence\(LaneAt\(c\), surge,", "CadenceFor passes surge");
                Has(cur, @"bool centre = RM_RiverMath\.BehavesAsCentre\(lane, surge\);", "StepOne passes surge");
            });

            Case("RiverSwitchFlip_countSeasonalFloods", () =>
            {
                Assert(RM_RiverMath.FloodCounts(true, true, true, false) && !RM_RiverMath.FloodCounts(false, true, true, false),
                       "a seasonal flood alone counts only with countSeasonalFloods on");
                Assert(RM_RiverMath.FloodCounts(false, false, true, true), "seasonal off never hides a torrential flood");
                string rw = Src(Path.Combine("Rivers", "RM_RiverWorks.cs"));
                Has(rw, @"seasonalFlood = DefDatabase<ThingDef>\.GetNamedSilentFail\(""SeasonalFlood""\);", "SeasonalFlood def looked up");
                Has(rw, @"bool seasonal = seasonalFlood != null && map\.listerThings\.ThingsOfDef\(seasonalFlood\)\.Count > 0;", "presence read off the map");
                Has(rw, @"RM_RiverMath\.FloodCounts\(" + S + @"countSeasonalFloods, seasonal,", "FloodActive passes countSeasonalFloods");
            });

            Case("RiverSwitchFlip_countTorrentialRainFloods", () =>
            {
                Assert(RM_RiverMath.FloodCounts(true, false, true, true) && !RM_RiverMath.FloodCounts(true, false, false, true),
                       "a torrential flood alone counts only with countTorrentialRainFloods on");
                Assert(RM_RiverMath.FloodCounts(true, true, false, false), "torrential off never hides a seasonal flood");
                string rw = Src(Path.Combine("Rivers", "RM_RiverWorks.cs"));
                Has(rw, @"torrentialFlood = DefDatabase<ThingDef>\.GetNamedSilentFail\(""TorrentialRainFlood""\);", "TorrentialRainFlood def looked up");
                Has(rw, @"bool torrential = torrentialFlood != null && map\.listerThings\.ThingsOfDef\(torrentialFlood\)\.Count > 0;", "presence read off the map");
                Has(rw, @"FloodCounts\([^;]*" + S + @"countTorrentialRainFloods, torrential\)", "FloodActive passes countTorrentialRainFloods");
            });

            // CarriedKind(isBuilding, isPawn, flying, riverNative, players, animal, carryAnimals, carryStrangers, carryItems)
            Case("RiverSwitchFlip_carryAnimals", () =>
            {
                Assert(RM_RiverMath.CarriedKind(false, true, false, false, false, true, true, true, true)
                       && !RM_RiverMath.CarriedKind(false, true, false, false, false, true, false, true, true), "a wild animal: on carried, off not");
                Assert(RM_RiverMath.CarriedKind(false, true, false, false, true, true, true, true, true)
                       && !RM_RiverMath.CarriedKind(false, true, false, false, true, true, false, true, true), "the colony's animal: on carried, off not");
                Assert(RM_RiverMath.CarriedKind(false, true, false, false, true, false, false, false, false), "carryAnimals off never spares a colonist");
                CarrySite("carryAnimals");
            });

            Case("RiverSwitchFlip_carryStrangers", () =>
            {
                Assert(RM_RiverMath.CarriedKind(false, true, false, false, false, false, true, true, true)
                       && !RM_RiverMath.CarriedKind(false, true, false, false, false, false, true, false, true), "a stranger: on carried, off not");
                Assert(RM_RiverMath.CarriedKind(false, true, false, false, true, false, true, false, true), "carryStrangers off still carries our own (and prisoners/guests)");
                Assert(!RM_RiverMath.CarriedKind(false, true, false, false, false, true, false, true, true), "carryStrangers on does not carry a wild animal with carryAnimals off");
                CarrySite("carryStrangers");
                Has(Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs")),
                    @"if \(!player && p\.HostFaction != null && p\.HostFaction\.IsPlayer\) \{ player = true;", "prisoners and guests count as ours");
            });

            Case("RiverSwitchFlip_carryItems", () =>
            {
                Assert(RM_RiverMath.CarriedKind(false, false, false, false, false, false, true, true, true)
                       && !RM_RiverMath.CarriedKind(false, false, false, false, false, false, true, true, false), "an item: on carried, off not");
                Assert(RM_RiverMath.CarriedKind(false, true, false, false, false, false, true, true, false), "carryItems off still carries pawns");
                CarrySite("carryItems");
                Has(Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs")),
                    @"if \(" + S + @"carryItems\) \{ candidates\.AddRange\(map\.listerThings\.ThingsInGroup\(ThingRequestGroup\.HaulableEver\)\);",
                    "the scan gathers loose items only with carryItems on");
            });

            Case("RiverSwitchFlip_crossingHazardsEnabled", () =>
            {
                Assert(RM_RiverMath.HazardsApply(true, true) && !RM_RiverMath.HazardsApply(true, false), "fast lane: on rolls hazards, off does not");
                Assert(!RM_RiverMath.HazardsApply(RM_RiverMath.BehavesAsCentre(M, false), true)
                       && RM_RiverMath.HazardsApply(RM_RiverMath.BehavesAsCentre(M, true), true), "the edge lane rolls hazards only in a surge");
                string cur = Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs"));
                Has(cur, @"if \(t is Pawn hp && RM_RiverMath\.HazardsApply\(centre, " + S + @"crossingHazardsEnabled\)\) \{ ApplyHazards\(hp\);",
                    "StepOne passes crossingHazardsEnabled and then rolls");
                Has(cur, @"Rand\.Chance\(" + S + @"bruiseChancePerStep\)\) \{ p\.TakeDamage", "the bruise roll");
                Has(cur, @"Rand\.Chance\(" + S + @"dropChancePerStep\)\) \{ p\.carryTracker\.TryDropCarriedThing", "the drop roll");
            });

            Case("RiverSwitchFlip_pathfinderAvoidsCurrents", () =>
            {
                Assert(RM_RiverMath.AvoidanceCost(true, true, true, true, 600, 120) == 600
                       && RM_RiverMath.AvoidanceCost(true, true, true, false, 600, 120) == 120, "on: fast lane +600, edge lane +120");
                Assert(RM_RiverMath.AvoidanceCost(true, true, false, true, 600, 120) == 0
                       && RM_RiverMath.AvoidanceCost(true, true, false, false, 600, 120) == 0, "off: no extra cost");
                Assert(RM_RiverMath.AvoidanceCost(true, false, true, true, 600, 120) == 0, "no current, nothing to avoid");
                Has(Src(Path.Combine("Rivers", "RM_RiverWorks.cs")),
                    @"extraNonDraftedPerceivedPathCost \+= RM_RiverMath\.AvoidanceCost\(" + S + @"riverWorksEnabled, " + S + @"surfaceCurrentEnabled, "
                    + S + @"pathfinderAvoidsCurrents, RM_RiverCurrentLanes\.IsFastLane\(t\), ExtraFastLane, ExtraEdgeLane\);",
                    "every river terrain's undrafted path cost passes pathfinderAvoidsCurrents");
            });

            Case("RiverSwitchFlip_weirCatchesDrift", () =>
            {
                Assert(RM_RiverMath.DriftRollChance(true, 0.25f) == 0.25f && RM_RiverMath.DriftRollChance(false, 0.25f) < 0f, "on rolls at the drift chance, off never rolls");
                Assert(RM_RiverMath.DriftRollChance(true, 0f) == 0f && RM_RiverMath.DriftRollChance(true, 2f) == 1f, "the chance is clamped, not switched");
                string w = Src(Path.Combine("Rivers", "RM_Weir.cs"));
                Has(w, @"float driftChance = RM_RiverMath\.DriftRollChance\(" + S + @"weirCatchesDrift, " + S + @"weirDriftChance\); if \(driftChance >= 0f\) \{ driftResult = Rand\.Chance\(driftChance\) \? TryCatchDrift\(\)",
                    "TryCatch passes weirCatchesDrift and rolls only when on");
            });

            // ── walk lines' offline halves ─────────────────────────────────────
            Case("RiverWalk_flier_never_carried", () =>
            {
                Assert(!RM_RiverMath.CarriedKind(false, true, true, false, true, false, true, true, true)
                       && !RM_RiverMath.CarriedKind(false, true, true, false, false, true, true, true, true), "a flier is never carried, whatever the toggles");
                Assert(!RM_RiverMath.CarriedKind(false, true, false, true, false, true, true, true, true), "a river-native race is never carried");
                Assert(!RM_RiverMath.CarriedKind(true, false, false, false, false, false, true, true, true), "a building is never carried");
                Has(Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs")),
                    @"CarriedKind\(building, p != null, p != null && p\.Flying, p != null && p\.def\.GetModExtension<RM_RiverNativeExtension>\(\) != null,",
                    "IsCarried passes Pawn.Flying and the river-native extension");
            });

            Case("RiverWalk_stake_line_snaps_nearest_downstream_first", () =>
            {
                // dir 0 = east: stakes 1, 3, 5 cells downstream snap in that order; 3 cells upstream never snaps
                float a = RM_RiverMath.StakeSnapOrder(1, 0, 0), b = RM_RiverMath.StakeSnapOrder(3, 1, 0), c = RM_RiverMath.StakeSnapOrder(5, -1, 0);
                Assert(0f < a && a < b && b < c, "downstream order 1 < 3 < 5 (" + a + "," + b + "," + c + ")");
                Assert(RM_RiverMath.StakeSnapOrder(-3, 0, 0) < 0f && RM_RiverMath.StakeSnapOrder(-1, 0, 0) == 0f, "upstream skipped; the weir's own row snaps first");
                Assert(RM_RiverMath.StakeSnapOrder(0, 4, 2) == 4f && RM_RiverMath.StakeSnapOrder(0, -4, 2) < 0f, "dir 2 = north: order follows the flow, not the axis");
                Assert(Math.Abs(RM_RiverMath.StakeSnapOrder(3, 4, -1) - 5f) < 1e-5, "no flow direction: plain distance");
                Has(Src(Path.Combine("Rivers", "RM_Weir.cs")),
                    @"float order = RM_RiverMath\.StakeSnapOrder\(t\.Position\.x - Position\.x, t\.Position\.z - Position\.z, dir\); if \(order < 0f\) \{ continue;",
                    "the breach cascade orders by StakeSnapOrder and skips upstream");
                Has(Src(Path.Combine("Rivers", "RM_Weir.cs")),
                    @"cascadeFireTicks\.Add\(now \+ Mathf\.RoundToInt\(order\) \* " + S + @"stakeSnapTicksPerCell\);", "snap tick = order x stakeSnapTicksPerCell");
            });
        }

        private static void CarrySite(string toggle)
        {
            Has(Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs")),
                @"if \(!RM_RiverMath\.CarriedKind\([^;]*" + S + @"carryAnimals, " + S + @"carryStrangers, " + S + @"carryItems\)\) \{ return false; \}",
                "IsCarried passes " + toggle + " (all three carry toggles, in order)");
            string cur = Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs"));
            Assert(Regex.Matches(cur, @"!IsCarried\(t\)").Count >= 2, "the scan and every shove ask IsCarried");
        }
    }
}
