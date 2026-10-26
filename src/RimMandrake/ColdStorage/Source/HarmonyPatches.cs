using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using Verse;

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
            float f = ColdStorageKernel.RotFactor(eff, active, sealedNow, unit?.Props.stasisRotFactor ?? 0f, itemFactor);
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
                f *= unit.Props.stasisRotFactor;
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
            float f = RotHold.Factor(__instance.parent);
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
            float f = RotHold.Factor(__instance.parent, out string why);
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

    /// <summary>A holding stasis field stops deterioration of what it holds.</summary>
    [HarmonyPatch(typeof(SteadyEnvironmentEffects), nameof(SteadyEnvironmentEffects.FinalDeteriorationRate),
        new[] { typeof(Thing), typeof(bool), typeof(bool), typeof(TerrainDef), typeof(System.Collections.Generic.List<string>) })]
    [PatchFeature("Stasis stops deterioration", typeof(RM_ColdStorageSettings), nameof(RM_ColdStorageSettings.stasisEnabled))]
    internal static class Patch_FinalDeteriorationRate
    {
        private static void Postfix(Thing t, ref float __result)
        {
            if (__result <= 0f || StorageClimateRegistry.UnitCount == 0)
            {
                return;
            }
            CompStorageClimate unit = StorageClimateRegistry.UnitHolding(t);
            if (unit != null && unit.StasisHolding)
            {
                __result *= unit.Props.stasisRotFactor;
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
            if (ext != null && !RM_ColdStorageSettings.GateOpen(ext.gate))
            {
                __result = false;
            }
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
            ColdStorageGateExtension ext = __instance.GetModExtension<ColdStorageGateExtension>();
            if (ext != null && !RM_ColdStorageSettings.GateOpen(ext.gate))
            {
                __result = false;
            }
        }
    }
}
