// DEEP_WATER_BUILD_REFUSED_BY_LIGHT_AFFORDANCE (owner 2026-10-25: "Gotta think about building where it's already underwater
// too: we should just let that happen, it needs to happen."). Offline checks on the production verdicts
// (RM_PitTrapMath.StandsInWater / StandsInDugWater) and the production patch source. Each case has a can-fail.
// NOT proven here: placing a wall blueprint on a flooded cut in game and a colonist building it. Live rows owed:
// deepwater_build_wall_on_flooded_cut, deepwater_build_bed_refused, deepwater_build_toggle_off_refuses.
// SUSPENSION_TOWER_DIAGNOSE_UNSUPPLIED_IN_POOL: the swim-safe delivery load (RM_SwimMath.MaxSwimCarryKg / SwimCarryCount)
// and the delivery patch source (Swimming/RM_SwimDelivery.cs). NOT proven here: a hauler swimming steel out to a mid-pool
// tower in game. Live row owed: tower_supply_swimmers_deliver (tower blueprint mid-pool, steel on the bank: Steel climbs
// in trips of about 18 and the tower completes).
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DeepWaterBuildChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Between(string src, string start, string end)
        {
            int a = src.IndexOf(start, StringComparison.Ordinal);
            Assert(a >= 0, "can-fail: '" + start + "' not found");
            int b = src.IndexOf(end, a + start.Length, StringComparison.Ordinal);
            Assert(b >= 0, "can-fail: '" + end + "' not found after '" + start + "'");
            return src.Substring(a, b - a);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("DeepWaterBuild_walls_fences_columns_stand_in_water_beds_do_not", () =>
            {
                Assert(RM_PitTrapMath.StandsInWater(true, false, false, false), "a wall stands in water");
                Assert(RM_PitTrapMath.StandsInWater(false, true, false, false), "a fence stands in water");
                Assert(RM_PitTrapMath.StandsInWater(false, false, true, false), "a column stands in water");
                Assert(RM_PitTrapMath.StandsInWater(false, false, false, true), "an opted-in def (RM_StandsInWaterExtension) stands");
                Assert(!RM_PitTrapMath.StandsInWater(false, false, false, false), "can-fail: a bed, table or machine does not");
            });

            Case("DeepWaterBuild_only_on_a_dug_cell_holding_liquid_and_only_with_the_setting_on", () =>
            {
                Assert(RM_PitTrapMath.StandsInDugWater(false, true, true, 4, 4), "a wall on a brim-full superdeep cut (run8's refusal) stands");
                Assert(RM_PitTrapMath.StandsInDugWater(false, true, true, 2, 1), "any depth of water");
                Assert(!RM_PitTrapMath.StandsInDugWater(false, true, true, 0, 4), "can-fail: a natural lake/river/sea (never dug) stays refused");
                Assert(!RM_PitTrapMath.StandsInDugWater(false, true, true, 3, 0), "can-fail: a dry cut is vanilla's (its channel floor) call");
                Assert(!RM_PitTrapMath.StandsInDugWater(false, true, false, 4, 4), "can-fail: a bed in a flooded cut stays refused");
                Assert(!RM_PitTrapMath.StandsInDugWater(false, false, true, 4, 4), "can-fail: the setting off restores vanilla");
                Assert(RM_PitTrapMath.StandsInDugWater(true, false, false, 0, 0), "vanilla's yes is never turned into a no");
            });

            Case("TowerSupply_run8_full_stack_sinks_the_capped_load_floats", () =>
            {
                const float cap = 35f, gear = 5f, pen = RM_SwimMath.DefaultWeightEndurancePenalty, steelKg = 0.5f;
                var sw = RM_SwimMath.SwimClass.Swimmer;
                // can-fail (the run8 cause, reproduced): 75 steel picked up for the tower sinks the hauler
                float runLoad = RM_SwimMath.Load(gear, 75 * steelKg, false, cap);
                Assert(RM_SwimMath.Effective(sw, RM_SwimMath.EnduranceFactor(sw, 1f, 1f, runLoad, pen)) == RM_SwimMath.SwimClass.None,
                    "can-fail: 75 steel on a 35 kg person sinks it (why the tower was never supplied)");
                float maxKg = RM_SwimMath.MaxSwimCarryKg(sw, 1f, 1f, gear, cap, pen, RM_SwimMath.SwimCarryEnduranceFloor);
                Assert(Math.Abs(maxKg - 9f) < 0.01f, "person, 5 kg gear: (1 - 0.5) / 1.25 x 35 - 5 = 9 kg, got " + maxKg);
                int n = RM_SwimMath.SwimCarryCount(75, steelKg, maxKg);
                Assert(n == 18, "75 wanted -> 18 steel per trip, got " + n);
                float capped = RM_SwimMath.Load(gear, n * steelKg, false, cap);
                float ef = RM_SwimMath.EnduranceFactor(sw, 1f, 1f, capped, pen);
                Assert(RM_SwimMath.Effective(sw, ef) == sw && ef >= RM_SwimMath.SwimCarryEnduranceFloor - 1e-4f,
                    "can-fail: the capped load keeps the hauler a swimmer at half endurance or better (ef " + ef + ")");
                Assert(RM_SwimMath.EnduranceFactor(sw, 1f, 1f, RM_SwimMath.Load(gear, (n + 1) * steelKg, false, cap), pen)
                    < RM_SwimMath.SwimCarryEnduranceFloor, "can-fail: one more unit would cross the floor (the cap is tight)");
                Assert(RM_SwimMath.SwimCarryCount(10, steelKg, maxKg) == 10, "a small need is not raised");
            });

            Case("TowerSupply_carry_cap_edges", () =>
            {
                var pen = RM_SwimMath.DefaultWeightEndurancePenalty;
                float fl = RM_SwimMath.SwimCarryEnduranceFloor;
                Assert(RM_SwimMath.MaxSwimCarryKg(RM_SwimMath.SwimClass.None, 1f, 1f, 0f, 35f, pen, fl) == 0f, "a non-swimmer carries nothing out");
                Assert(float.IsPositiveInfinity(RM_SwimMath.MaxSwimCarryKg(RM_SwimMath.SwimClass.Aquatic, 1f, 1f, 0f, 35f, pen, fl)), "the aquatic is not capped");
                Assert(RM_SwimMath.MaxSwimCarryKg(RM_SwimMath.SwimClass.Swimmer, 0.4f, 1f, 0f, 35f, pen, fl) == 0f, "can-fail: a hurt swimmer under the floor empty-handed carries nothing");
                Assert(RM_SwimMath.MaxSwimCarryKg(RM_SwimMath.SwimClass.Strong, 1f, 1f, 0f, 35f, pen, fl) > 20f, "a strong swimmer carries a lot more");
                Assert(RM_SwimMath.MaxSwimCarryKg(RM_SwimMath.SwimClass.Swimmer, 1f, 1f, 20f, 35f, pen, fl) == 0f, "gear alone over the line: nothing");
                Assert(RM_SwimMath.SwimCarryCount(1, 60f, 9f) == 0, "can-fail: a 60 kg single item cannot be swum out (no job)");
                Assert(RM_SwimMath.SwimCarryCount(75, 0f, 9f) == 75, "massless: not capped");
            });

            Case("TowerSupply_patch_caps_vanilla_delivery_only_for_swim_only_needers", () =>
            {
                string p = Src("Swimming", "RM_SwimDelivery.cs");
                Assert(Src("RimMandrake_FlowWorks.csproj").Contains("<Compile Include=\"Swimming\\RM_SwimDelivery.cs\" />"),
                    "can-fail (it was missing once): the patch is compiled into the mod");
                Assert(p.Contains("[HarmonyPatch(typeof(WorkGiver_ConstructDeliverResources), \"ResourceDeliverJobFor\")]"),
                    "patches vanilla's shared delivery (blueprints and frames)");
                Assert(p.Contains("!NeedsSwimDelivery(pawn.Map, __result)"), "can-fail: a needer touching the bank is left to vanilla");
                Assert(p.Contains("SwimOnly(map, job.targetB.Thing) || SwimOnly(map, job.targetC.Thing)") && p.Contains("job.targetQueueB"),
                    "every needer of the trip is checked");
                Assert(p.Contains("else if (n.Standable(map))") && p.Contains("RM_SwimWater.IsDeepSwimCell(map, n)"),
                    "footing rule as the non-swimmer reach veto");
                Assert(p.Contains("RM_SwimMath.SwimCarryEnduranceFloor") && p.Contains("RM_SwimSettings.swimWeightEndurancePenalty")
                    && p.Contains("MassUtility.GearAndInventoryMass(pawn)") && p.Contains("MassUtility.Capacity(pawn)"),
                    "the cap is fed the same inputs as the swim profile");
                Assert(p.Contains("if (count <= 0 || heldTooHeavy)") && p.Contains("__result = null;"), "can-fail: nothing swimmable -> no job, not a sinking trip");
                Assert(p.Contains("bool held = res == pawn.carryTracker?.CarriedThing;") && p.Contains("bool heldTooHeavy = held && CappedCount(pawn, res, res.stackCount) < res.stackCount;")
                    && p.Contains("__result.targetQueueA = null;"),
                    "can-fail: a full stack already in hand (vanilla CanUseCarriedResource; the driver skips the pickup) is not swum out");
            });

            Case("DeepWaterBuild_patch_reads_the_def_the_dug_grid_and_the_setting", () =>
            {
                string doors = Src("Superdeep", "RM_FlowDoors.cs");
                string patch = Between(doors, "[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]", "public static class RM_FlowDoorRules");
                Assert(patch.Contains("if (__result ||"), "early-out on every call vanilla already allows");
                Assert(patch.Contains("RimMandrakeFlowWorksSettings.buildInDugWaterEnabled && StandsInWater(td)"), "the setting gates the new set");
                Assert(patch.Contains("RM_PitTrapMath.StandsInDugWater(false, true, true, dug, fill)"), "the selftested verdict decides");
                Assert(patch.Contains("int dug = eng.ExcavatedDepthAt(cell), fill = eng.FillAt(cell);") && !patch.Contains("eng.DepthAt("),
                    "can-fail: the DUG depth, never DepthAt (which reads a natural lake as superdeep)");
                Assert(patch.Contains("HasTerrainOrder(cell, map, thingToIgnore)"), "a floor order under the cell keeps vanilla's refusal");
                Assert(patch.Contains("Thing thingToIgnore, ThingDef stuffDef)") && patch.Contains("td.GetTerrainAffordanceNeed(stuffDef)")
                    && patch.Contains("if (need != null && cell.GetAffordances(map).Contains(need))"),
                    "can-fail: a footprint part on supporting ground and part in the flooded cut is judged cell by cell");
                string kind = Between(doors, "public static bool StandsInWater(ThingDef td)", "/// <summary>A floor blueprint or frame under the door:");
                Assert(kind.Contains("td.category == ThingCategory.Building") && kind.Contains("td.IsWall") && kind.Contains("td.IsFence")
                    && kind.Contains("td.defName == \"Column\"") && kind.Contains("!td.HasModExtension<Pits.RM_SuspensionExtension>()")
                    && kind.Contains("HasModExtension<RM_StandsInWaterExtension>()"), "the def reading feeds every StandsInWater input; can-fail: a suspension part is left to RM_Patch_SuspensionAffordance");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("public static bool buildInDugWaterEnabled = true;")
                    && mod.Contains("Scribe_Values.Look(ref buildInDugWaterEnabled, \"buildInDugWaterEnabled\", true);")
                    && mod.Contains("ref buildInDugWaterEnabled,"), "Mod Settings toggle: field, scribe and checkbox");
            });
        }
    }
}
