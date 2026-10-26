using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.ColdStorage
{
    // Every patch is one compare when no unit is spawned (StorageClimateRegistry.UnitCount == 0) or the item cannot be
    // sealed (CompSealed.sealableByIndex). Each class names the Mod Settings switch a failed patch turns off
    // (PatchApplier), and each gates on that switch through CompStorageClimate.Effective.

    /// <summary>
    /// Items on a chill unit's cells, or in its container, read the unit's temperature, so vanilla rot, the inspect
    /// line and the "frozen" readout all follow it. RimFridge's prefix, done our way: non-items (live pawns, buildings)
    /// are never chilled, and the lookup is one array read in a cell grid rebuilt only on spawn and despawn.
    /// </summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.AmbientTemperature), MethodType.Getter)]
    [PatchFeature("Chill units", typeof(RM_ColdStorageSettings), nameof(RM_ColdStorageSettings.chillEnabled))]
    internal static class Patch_Thing_AmbientTemperature
    {
        private static bool Prefix(Thing __instance, ref float __result)
        {
            if (StorageClimateRegistry.UnitCount == 0)
            {
                return true;
            }
            CompStorageClimate unit = StorageClimateRegistry.UnitHolding(__instance);
            if (unit != null && unit.TryGetHeldTemperature(out float t))
            {
                __result = t;
                return false;
            }
            return true;
        }
    }

    internal static class RotHold
    {
        private static int rotTickPatched = -1;

        /// <summary>Whether the rot-tick prefix (Patch_CompRottable_TickInterval) applied. Only it makes a rot factor
        /// real, so the readouts show a factor only when it did (COLDSTORAGE_SEALED_READOUT_FIX_GATE). Read after
        /// PatchApplier.Apply ran in the mod constructor, so it is final by the first readout.</summary>
        public static bool RotTickPatched
        {
            get
            {
                if (rotTickPatched < 0)
                {
                    rotTickPatched = 1;
                    foreach (PatchFailure f in PatchApplier.Failures)
                    {
                        if (f.patchClass == nameof(Patch_CompRottable_TickInterval))
                        {
                            rotTickPatched = 0;
                        }
                    }
                }
                return rotTickPatched == 1;
            }
        }

        /// <summary>The factor a readout may show: <see cref="Factor(Thing)"/>, or 1 when the rot tick is unpatched.</summary>
        public static float ReadoutFactor(Thing thing)
        {
            return ColdStorageKernel.ReadoutRotFactor(Factor(thing), RotTickPatched);
        }

        /// <summary>The fixed multiplier on <paramref name="thing"/>'s rot tick (ColdStorageKernel.RotFactor): 0 while
        /// sealed or in a true stasis field, the item's own factor for preserved goods, 1 for everything else.
        /// <paramref name="why"/> names the cause for the inspect line, or null at 1.</summary>
        public static float Factor(Thing thing, out string why)
        {
            CompSealed seal = CompSealed.SealOf(thing);
            bool sealedNow = seal != null && seal.IsSealedNow;
            float itemFactor = ColdStorageStartup.ItemRotFactor(thing);
            CompStorageClimate unit = !sealedNow && StorageClimateRegistry.UnitCount > 0 ? StorageClimateRegistry.UnitHolding(thing) : null;
            EffectiveMode eff = unit?.Effective ?? EffectiveMode.None;
            bool active = unit != null && unit.Active;
            float f = ColdStorageKernel.RotFactor(eff, active, sealedNow, unit?.StasisRotFactor ?? 0f, itemFactor);
            if (f == 1f)
            {
                why = null;
            }
            else if (sealedNow)
            {
                why = seal.Props.method?.SealedLabelCap ?? "RM_ColdStorage_Sealed".Translate().ToString();
            }
            else if (unit != null && unit.StasisHolding)
            {
                why = "RM_ColdStorage_InStasis".Translate();
            }
            else
            {
                ColdStorageMethodDef m = thing.def.GetModExtension<ColdStoragePreservedExtension>()?.method;
                why = (m?.SealedLabelCap ?? "RM_ColdStorage_Preserved".Translate().ToString());
            }
            return f;
        }

        /// <summary>The hot path: a single compare for ordinary food when no unit is spawned.</summary>
        public static float Factor(Thing thing)
        {
            if (CompSealed.IsSealed(thing))
            {
                return 0f;
            }
            float f = ColdStorageStartup.ItemRotFactor(thing);
            if (StorageClimateRegistry.UnitCount == 0)
            {
                return f;
            }
            CompStorageClimate unit = StorageClimateRegistry.UnitHolding(thing);
            if (unit != null && unit.StasisHolding)
            {
                f *= unit.StasisRotFactor;
            }
            return f;
        }
    }

    /// <summary>The rot tick (private; both CompTickRare and CompTickInterval call it) runs on a delta scaled by the
    /// fixed rot factor: skipped at 0 (sealed, true stasis), scaled with random rounding otherwise, so rot damage, rot
    /// destruction and the stage change all stay vanilla's.</summary>
    [HarmonyPatch(typeof(CompRottable), "TickInterval", new[] { typeof(int) })]
    [PatchFeature("Stasis units and sealed goods", typeof(RM_ColdStorageSettings), nameof(RM_ColdStorageSettings.stasisEnabled))]
    internal static class Patch_CompRottable_TickInterval
    {
        private static bool Prefix(CompRottable __instance, ref int delta)
        {
            float f = RotHold.Factor(__instance.parent);
            if (f == 1f)
            {
                return true;
            }
            if (f <= 0f)
            {
                return false;
            }
            delta = GenMath.RoundRandom(delta * f);
            return delta > 0;
        }
    }

    /// <summary>Caravan and trade screens ask how long food keeps: "never" while held, stretched by a rot factor.</summary>
    [HarmonyPatch(typeof(CompRottable), nameof(CompRottable.TicksUntilRotAtCurrentTemp), MethodType.Getter)]
    [PatchFeature("Stasis and sealed rot readout", typeof(RM_ColdStorageSettings), nameof(RM_ColdStorageSettings.stasisEnabled))]
    internal static class Patch_CompRottable_TicksUntilRot
    {
        private static void Postfix(CompRottable __instance, ref int __result)
        {
            float f = RotHold.ReadoutFactor(__instance.parent);
            if (f != 1f)
            {
                __result = ColdStorageKernel.TicksUntilRotWithFactor(__result, f);
            }
        }
    }

    /// <summary>The rot inspect line says why food is not rotting ("Fresh (tar-sealed)", "Fresh (in stasis)") instead
    /// of "not refrigerated"; a slowed item keeps vanilla's line (its time already stretched) plus the cause.</summary>
    [HarmonyPatch(typeof(CompRottable), nameof(CompRottable.CompInspectStringExtra))]
    [PatchFeature("Stasis and sealed rot readout", typeof(RM_ColdStorageSettings), nameof(RM_ColdStorageSettings.stasisEnabled))]
    internal static class Patch_CompRottable_Inspect
    {
        private static void Postfix(CompRottable __instance, ref string __result)
        {
            if (__result == null)
            {
                return;
            }
            float f = ColdStorageKernel.ReadoutRotFactor(RotHold.Factor(__instance.parent, out string why), RotHold.RotTickPatched);
            if (f == 1f || why == null)
            {
                return;
            }
            if (f > 0f)
            {
                __result = __result + " (" + why + ")";
                return;
            }
            string stage;
            switch (__instance.Stage)
            {
                case RotStage.Fresh:
                    stage = "RotStateFresh".Translate();
                    break;
                case RotStage.Rotting:
                    stage = "RotStateRotting".Translate();
                    break;
                default:
                    stage = "RotStateDessicated".Translate();
                    break;
            }
            __result = stage + " (" + why + ")";
        }
    }

    /// <summary>A holding stasis field stops (or, at a partial strength, slows) deterioration of what it holds.</summary>
    [HarmonyPatch(typeof(SteadyEnvironmentEffects), nameof(SteadyEnvironmentEffects.FinalDeteriorationRate),
        new[] { typeof(Thing), typeof(bool), typeof(bool), typeof(TerrainDef), typeof(System.Collections.Generic.List<string>) })]
    [PatchFeature("Stasis stops deterioration", typeof(RM_ColdStorageSettings), nameof(RM_ColdStorageSettings.stasisEnabled))]
    internal static class Patch_FinalDeteriorationRate
    {
        private static void Postfix(Thing t, System.Collections.Generic.List<string> reasons, ref float __result)
        {
            if (__result <= 0f || StorageClimateRegistry.UnitCount == 0)
            {
                return;
            }
            CompStorageClimate unit = StorageClimateRegistry.UnitHolding(t);
            if (unit != null && unit.StasisHolding)
            {
                // A field that stops deterioration also clears the causes the inspect pane would list for a zero rate.
                __result = ColdStorageKernel.ApplyStasisToDeterioration(__result, unit.StasisRotFactor, reasons);
            }
        }
    }

    /// <summary>A method switched off in Mod Settings hides its stations from the architect menu.</summary>
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.Visible), MethodType.Getter)]
    [PatchFeature("Method switches (stations)")]
    internal static class Patch_DesignatorBuild_Visible
    {
        private static void Postfix(Designator_Build __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            ColdStorageGateExtension ext = __instance.PlacingDef?.GetModExtension<ColdStorageGateExtension>();
            if (ext != null && !ColdStorageGates.Open(ext))
            {
                __result = false;
            }
            else if (__instance.PlacingDef is ThingDef td && !RM_ColdStorageSettings.UnitEnabled(td))
            {
                __result = false;
            }
        }
    }

    /// <summary>Wall units: the wall unit holding a spawned item on its own (impassable) cell, or null.</summary>
    internal static class WallUnits
    {
        internal static CompStorageClimate At(Thing thing)
        {
            if (StorageClimateRegistry.UnitCount == 0 || thing == null || !thing.Spawned
                || thing.def.category != ThingCategory.Item)
            {
                return null;
            }
            CompStorageClimate unit = StorageClimateRegistry.UnitHolding(thing);
            return unit != null && unit.Props.wallMounted ? unit : null;
        }
    }

    /// <summary>
    /// An item stored in a wall unit sits on an impassable cell, so a job that must stand ON the item's cell can never
    /// reach it. Standing next to it is enough, as for RimFridge's wall fridge: OnCell becomes Touch for such items.
    /// </summary>
    [HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach), typeof(IntVec3), typeof(LocalTargetInfo),
        typeof(PathEndMode), typeof(TraverseParms))]
    [PatchFeature("Wall units (reach)")]
    internal static class Patch_Reachability_CanReach
    {
        private static void Prefix(LocalTargetInfo dest, ref PathEndMode peMode)
        {
            if (peMode == PathEndMode.OnCell && StorageClimateRegistry.UnitCount != 0 && dest.HasThing
                && WallUnits.At(dest.Thing) != null)
            {
                peMode = PathEndMode.Touch;
            }
        }
    }

    /// <summary>The region-lister reach check (GenClosest's item searches) with the same OnCell to Touch rule.</summary>
    [HarmonyPatch(typeof(ReachabilityWithinRegion), nameof(ReachabilityWithinRegion.ThingFromRegionListerReachable))]
    [PatchFeature("Wall units (reach)")]
    internal static class Patch_ReachabilityWithinRegion_ThingFromRegionListerReachable
    {
        private static void Prefix(Thing thing, ref PathEndMode peMode)
        {
            if (peMode == PathEndMode.OnCell && StorageClimateRegistry.UnitCount != 0 && WallUnits.At(thing) != null)
            {
                peMode = PathEndMode.Touch;
            }
        }
    }

    /// <summary>
    /// Social properness reads the room of the item's cell; a wall unit's cell is wall and has no room, so a prisoner
    /// would never take food from a wall unit in his own cell. Judge such an item by the room on the unit's facing side.
    /// </summary>
    [HarmonyPatch(typeof(SocialProperness), nameof(SocialProperness.IsSociallyProper), typeof(Thing), typeof(Pawn),
        typeof(bool), typeof(bool))]
    [PatchFeature("Wall units (prisoner food)")]
    internal static class Patch_SocialProperness_IsSociallyProper
    {
        private static void Postfix(Thing t, Pawn p, bool forPrisoner, bool animalsCare, ref bool __result)
        {
            if (StorageClimateRegistry.UnitCount == 0 || !t.def.socialPropernessMatters
                || (!animalsCare && p != null && !p.RaceProps.Humanlike))
            {
                return;
            }
            CompStorageClimate unit = WallUnits.At(t);
            if (unit == null)
            {
                return;
            }
            Map map = t.Map;
            IntVec3 cell = unit.RoomSideCell;
            bool hemogenRule = !forPrisoner && ModsConfig.BiotechActive && t.def == ThingDefOf.HemogenPack;
            __result = ColdStorageKernel.WallItemSociallyProper(forPrisoner, p != null,
                forPrisoner && p != null && cell.GetRoom(map) == p.GetRoom(),
                hemogenRule, hemogenRule && SocialProperness.BloodfeedingPrisonerInRoom(cell.GetRoom(map)),
                !forPrisoner && !hemogenRule && cell.IsInPrisonCell(map));
        }
    }

    /// <summary>A method switched off in Mod Settings hides its recipes from every bill list.</summary>
    [HarmonyPatch(typeof(RecipeDef), nameof(RecipeDef.AvailableNow), MethodType.Getter)]
    [PatchFeature("Method switches (recipes)")]
    internal static class Patch_RecipeDef_AvailableNow
    {
        private static void Postfix(RecipeDef __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            if (!ColdStorageGates.RecipeOpen(__instance))
            {
                __result = false;
            }
        }
    }

    /// <summary>AvailableNow only hides a recipe from the add-bill list; a bill made before the switch went off would
    /// keep running (WorkGiver_DoBill asks ShouldDoNow, never AvailableNow). A switched-off method pauses its bills.</summary>
    [HarmonyPatch(typeof(Bill_Production), nameof(Bill_Production.ShouldDoNow))]
    [PatchFeature("Method switches (existing bills)")]
    internal static class Patch_BillProduction_ShouldDoNow
    {
        private static void Postfix(Bill_Production __instance, ref bool __result)
        {
            if (__result && __instance.recipe != null && !ColdStorageGates.RecipeOpen(__instance.recipe))
            {
                __result = false;
            }
        }
    }
}
