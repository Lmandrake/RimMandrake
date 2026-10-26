using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_FIRE_BAN_1 — the four real engine hook points, read off the
    // decompiled 1.6 source (RimSage), not assumed:
    //
    // 1) FireUtility.TryStartFireIn(IntVec3, Map, float, Thing, SimpleCurve)
    //    is the SINGLE chokepoint every actual `Fire` Thing spawns through
    //    — confirmed by grepping every call site in the decompiled source:
    //    DamageWorker_Flame (incendiary/molotov explosions),
    //    DamageWorker_Vaporize, Explosion.cs's own spread, PowerBeam,
    //    Verb_ShootBeam, Bullet (incendiary ammo), Bombardment,
    //    Verb_Ignite (the hand-ignite verb/psycast), FlameThrower,
    //    SteadyEnvironmentEffects (lightning), Spark, ShortCircuitUtility,
    //    Fire.cs's own TrySpread/TryBurnFloor, FireArrow. One prefix here
    //    covers "molotovs/incendiaries splash inert" AND fire's own spread
    //    AND every other ignition source in one place — nothing on this
    //    list needs its own patch.
    //
    // 2) CompRefuelable.ShouldBeLitNow() is NOT wired through
    //    TryStartFireIn at all — a campfire/torch/brazier never spawns a
    //    `Fire` Thing; "lit" is a pure `HasFuel` read, polled live wherever
    //    it's asked. It IS what CompGlower checks (CompGlower.ShouldBeLitNow
    //    loops every IThingGlower comp on the parent and calls its
    //    ShouldBeLitNow(), and CompRefuelable declares
    //    `: ThingComp_VacuumAware, IThingGlower` precisely so that loop
    //    reaches it) — so this postfix is what actually turns the light/
    //    glow off, and by extension what starves FocusStrengthOffset_Lit's
    //    meditation bonus. Postfixing this one non-virtual method also
    //    answers BOTH halves of the item's open question at once, because
    //    nothing here is a cached flag: a fuel-burning building never
    //    lights on the Chill seabed, AND one already burning when the map
    //    is entered/loaded goes dark on its very next query — there is no
    //    separate "already lit" state to chase down and clear.
    //
    // 3) CompHeatPusherPowered.ShouldPushHeatNow reads refuelableComp.HasFuel
    //    DIRECTLY (not ShouldBeLitNow()), so patch (2) alone does NOT stop
    //    a fuel-burning heater's actual heat output — confirmed by reading
    //    CompHeatPusherPowered.cs itself. This third postfix is what makes
    //    "heat becomes electric-only" literally true: it only fires when
    //    the comp is fuel-driven (refuelableComp present via
    //    parent.TryGetComp<CompRefuelable>()); a pure CompPowerTrader-driven
    //    (electric) heater is untouched, on the Chill seabed or anywhere
    //    else — that's the whole point CHILL_THERMAL_ENGINE_1 needs to
    //    hold.
    //
    // 4) CompFireOverlay.PostDraw ALSO reads refuelableComp.HasFuel
    //    DIRECTLY, bypassing ShouldBeLitNow() a second time — confirmed by
    //    reading CompFireOverlay.cs itself (its PostDraw and CompTick both
    //    check `refuelableComp == null || refuelableComp.HasFuel`, never
    //    ShouldBeLitNow()). Without this fourth prefix a campfire that is
    //    genuinely unlit (no glow, no heat, patch 2/3 both firing) would
    //    still visually draw its flame sprite every frame — a real
    //    fizzle has no flame to look at either, so this prefix skips the
    //    draw call outright on a banned cell.
    //
    // All four route through RM_ChillFireGate.IsIgnitionAllowed, so the
    // map-identity check (RM_TheChill AND IsPocketMap), the settings
    // toggles, the oxygenated-zone override and the self-oxidizing
    // (Fuselight) exemption all live in exactly one place.
    // ════════════════════════════════════════════════════════════════════

    [HarmonyPatch(typeof(FireUtility), nameof(FireUtility.TryStartFireIn))]
    public static class Patch_FireUtility_TryStartFireIn
    {
        public static bool Prefix(IntVec3 c, Map map, Thing instigator, ref bool __result)
        {
            if (RM_ChillFireGate.IsIgnitionAllowed(map, c, instigator))
            {
                return true; // run the vanilla method normally
            }
            __result = false; // no oxygen down here — the fire simply never catches
            return false;
        }
    }

    [HarmonyPatch(typeof(CompRefuelable), nameof(CompRefuelable.ShouldBeLitNow))]
    public static class Patch_CompRefuelable_ShouldBeLitNow
    {
        public static void Postfix(CompRefuelable __instance, ref bool __result)
        {
            if (!__result)
            {
                return; // already unlit (out of fuel etc) — nothing to override
            }
            // Gate(): only a flame building goes dark. A fuelled powered machine's glow is an electric status light
            // (KoltoTank; CHILLFIREBAN_FIX_POWERED_MACHINE_FREE_FUEL) and a non-combustion plant keeps its glow while it
            // keeps making power (RUT_VaultHeart; CHILLFIREBAN_FIX_NONCOMBUSTION_PLANT_BANNED).
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance.parent, __result);
        }
    }

    // Patch (3) covers CompHeatPusher.ShouldPushHeatNow AND every loaded override of it (ChillFireBanTargets), not
    // CompHeatPusherPowered's alone: VQE The Generator's CompHeatPusherPowered_Overdrive derives from CompHeatPusher and
    // never reaches CompHeatPusherPowered's getter (IL read of the owner's assemblies, CHILLFIREBAN_FIX_MODDED_OVERRIDES_BYPASS;
    // VFE Tribals' CompHeatPusher_LargeFire does call base, so it was always covered). Only a FLAME building is gated (Gate): an electric
    // heater has no CompRefuelable and keeps working — heat becomes electric-only, not nothing.
    [HarmonyPatch]
    public static class Patch_CompHeatPusherPowered_ShouldPushHeatNow
    {
        public static IEnumerable<MethodBase> TargetMethods()
        {
            return ChillFireBanTargets.WithOverrides(
                AccessTools.PropertyGetter(typeof(CompHeatPusher), nameof(CompHeatPusher.ShouldPushHeatNow)));
        }

        public static void Postfix(CompHeatPusher __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance.parent, __result);
        }
    }

    /// <summary>
    /// A vanilla method plus every override of it in the loaded assemblies. A Harmony patch on a virtual method patches
    /// that one body: an override that does not call base never runs it. The owner's list has such overrides on all three
    /// methods the ban gates (CHILLFIREBAN_FIX_MODDED_OVERRIDES_BYPASS): VQE The Generator's CompPowerPlantGenetron
    /// replaces UpdateDesiredPowerOutput and CompRefuelableWithOverdrive replaces CompTick, so a wood-fired Genetron on the
    /// seabed had its fuel frozen (CompRefuelable.CompTick, patched) while it kept making power (the override, unpatched).
    /// Patching an override that does call base runs the postfix twice; every postfix here is idempotent. Runs at mod
    /// construction, after every mod assembly is loaded.
    /// </summary>
    internal static class ChillFireBanTargets
    {
        internal static IEnumerable<MethodBase> WithOverrides(MethodInfo root)
        {
            yield return root;
            Type rootType = root.DeclaringType;
            Type baseDeclarer = root.GetBaseDefinition().DeclaringType;
            Type[] parameters = Array.ConvertAll(root.GetParameters(), p => p.ParameterType);
            foreach (Type t in AccessTools.AllTypes())
            {
                MethodInfo m;
                try
                {
                    if (t == rootType || t.ContainsGenericParameters || !rootType.IsAssignableFrom(t))
                    {
                        continue;
                    }
                    m = AccessTools.DeclaredMethod(t, root.Name, parameters);
                    if (m == null || m.IsAbstract || m.GetBaseDefinition().DeclaringType != baseDeclarer)
                    {
                        continue; // not declared here, or a `new` method that hides rather than overrides
                    }
                }
                catch (Exception)
                {
                    continue; // a type whose dependencies did not load: it cannot be instantiated either
                }
                yield return m;
            }
        }
    }

    // CHILLFIREBAN_DECIDE_FUELLED_COOKING_POWER (delegated: design, follows CHILL_FIRE_BAN_1's card ruling "total ban —
    // no flame works on the Chill seabed map. Campfires fizzle, chemfuel won't light"). A fuelled bill-giver (campfire,
    // fuelled stove, fuelled smithy) cannot work bills while the ban holds. Building_WorkTable.CurrentlyUsableForBills and
    // UsableForBillsAfterFueling both read refuelableComp.HasFuel, never ShouldBeLitNow, so patch (2) alone left them
    // cooking. BOTH are gated: WorkGiver_DoBill offers the job on UsableForBillsAfterFueling and JobDriver_DoBill drops it
    // on CurrentlyUsableForBills — gating only the second would loop pawns into a job that fails every tick. With both
    // gated a pawn never takes the bill, and never hauls fuel to it (the refuel giver is fed by the same bill scan).
    // An electric stove has no CompRefuelable and is untouched. Pumped air lifts the gate (IsIgnitionAllowed).
    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.CurrentlyUsableForBills))]
    public static class Patch_BuildingWorkTable_CurrentlyUsableForBills
    {
        public static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance, __result);
        }
    }

    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.UsableForBillsAfterFueling))]
    public static class Patch_BuildingWorkTable_UsableForBillsAfterFueling
    {
        public static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            __result = Patch_ChillFireBan_Fuelled.Gate(__instance, __result);
        }
    }

    // Same item: a fuelled generator (wood-fired, chemfuel) makes no power while the ban holds.
    // CompPowerPlant.UpdateDesiredPowerOutput reads refuelableComp.HasFuel directly and runs every CompTick. No vanilla
    // subclass overrides it, but modded ones do (VQE's CompPowerPlantGenetron, without a base call), so the postfix goes
    // on every override too (ChillFireBanTargets). Solar, wind, geothermal, watermill, aurora collector: no CompRefuelable,
    // untouched.
    [HarmonyPatch]
    public static class Patch_CompPowerPlant_UpdateDesiredPowerOutput
    {
        public static IEnumerable<MethodBase> TargetMethods()
        {
            return ChillFireBanTargets.WithOverrides(
                AccessTools.Method(typeof(CompPowerPlant), nameof(CompPowerPlant.UpdateDesiredPowerOutput)));
        }

        public static void Postfix(CompPowerPlant __instance)
        {
            if (__instance.PowerOutput <= 0f)
            {
                return;
            }
            if (!Patch_ChillFireBan_Fuelled.Gate(__instance.parent, true))
            {
                __instance.PowerOutput = 0f;
            }
        }
    }

    // Same item: the player sees WHY the stove, campfire or generator is dead — a line on its inspect pane.
    [HarmonyPatch(typeof(CompRefuelable), nameof(CompRefuelable.CompInspectStringExtra))]
    public static class Patch_CompRefuelable_CompInspectStringExtra
    {
        public static void Postfix(CompRefuelable __instance, ref string __result)
        {
            ThingWithComps parent = __instance.parent;
            if (parent == null || !parent.Spawned)
            {
                return;
            }
            bool usesFlame = Patch_ChillFireBan_Fuelled.UsesFlame(parent);
            if (!usesFlame)
            {
                return; // cheap reject first: the gate is only asked about flame buildings
            }
            if (RM_ChillFireBanKernel.ShowNoAirNote(usesFlame,
                RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent)))
            {
                string note = "RM_ChillFireBan_NoAir".Translate();
                __result = string.IsNullOrEmpty(__result) ? note : __result + "\n" + note;
            }
        }
    }

    internal static class Patch_ChillFireBan_Fuelled
    {
        private static readonly System.Collections.Generic.Dictionary<ThingDef, bool> usesFlame =
            new System.Collections.Generic.Dictionary<ThingDef, bool>();

        /// <summary>Per-def cache of RM_ChillFireBanKernel.UsesFlame (a def's comps are fixed).</summary>
        internal static bool UsesFlame(ThingWithComps thing)
        {
            ThingDef def = thing.def;
            if (!usesFlame.TryGetValue(def, out bool result))
            {
                CompPowerTrader trader = thing.GetComp<CompPowerTrader>();
                result = RM_ChillFireBanKernel.UsesFlame(
                    thing.GetComp<CompRefuelable>() != null,
                    thing.GetComp<CompGlower>() != null,
                    thing.GetComp<CompHeatPusher>() != null,
                    thing.GetComp<CompFireOverlay>() != null,
                    def.IsWorkTable,
                    trader is CompPowerPlant,
                    trader != null);
                usesFlame[def] = result;
            }
            return result;
        }

        /// <summary>Gate one vanilla output of a building by the ban; anything that is not a flame building passes through.</summary>
        internal static bool Gate(ThingWithComps thing, bool vanillaOn)
        {
            if (!vanillaOn || thing?.Map == null || !Patch_ChillFireBan_Fuelled.UsesFlame(thing))
            {
                return vanillaOn;
            }
            return RM_ChillFireBanKernel.Output(vanillaOn, true,
                RM_ChillFireGate.IsIgnitionAllowed(thing.Map, thing.Position, thing));
        }
    }

    // CHILLFIREBAN_FIX_UNLIT_REFUELABLE_BURNS_FUEL: patch (2) puts the flame out, but
    // CompRefuelable.CompTick still burns ConsumptionRatePerTick whenever it is switched on — it
    // never asks ShouldBeLitNow. So a dark, cold torch, brazier or fuelled heater on the seabed
    // emptied itself and pawns hauled wood to it forever. While the ban holds, the passive burn of a
    // flame building is skipped (RM_ChillFireBanKernel.UsesFlame): a fuelled generator, or an unpowered
    // building that glows, heats, draws a flame or works bills. Work tables and generators joined the set with
    // CHILLFIREBAN_DECIDE_FUELLED_COOKING_POWER — they no longer cook or make power while banned (patches
    // above), so freezing their fuel gives nothing away. A powered consumer (kolto tank, autobong, fuel
    // processor: CHILLFIREBAN_FIX_POWERED_MACHINE_FREE_FUEL) is a machine, not a fire, and keeps burning.
    // The skip is done at ConsumeFuel, scoped to this comp during its own CompTick, so the fuel never
    // reaches 0 and Notify_RanOutOfFuel (destroyOnNoFuel) cannot fire from a burn that did not happen.
    // Every override of CompTick is patched too (VQE's CompRefuelableWithOverdrive burns fuel in its own CompTick and never
    // calls base). An override that DOES call base (VGE's CompRefuelable_IgnoreFlickableComp) nests one tick inside the
    // other, so the finalizer restores the outer scope (__state) instead of clearing it: clearing would let the override's
    // own ConsumeFuel calls after base.CompTick() burn fuel the ban froze.
    [HarmonyPatch]
    public static class Patch_CompRefuelable_CompTick
    {
        internal static CompRefuelable suppressing;

        public static IEnumerable<MethodBase> TargetMethods()
        {
            return ChillFireBanTargets.WithOverrides(
                AccessTools.Method(typeof(CompRefuelable), nameof(CompRefuelable.CompTick)));
        }

        public static void Prefix(CompRefuelable __instance, out CompRefuelable __state)
        {
            __state = suppressing;
            ThingWithComps parent = __instance.parent;
            if (parent == null || !parent.Spawned || !IsFireOnly(parent))
            {
                return;
            }
            if (RM_ChillFireBanKernel.SkipFuelBurn(true,
                RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent)))
            {
                suppressing = __instance;
            }
        }

        public static void Finalizer(CompRefuelable __state)
        {
            suppressing = __state;
        }

        private static bool IsFireOnly(ThingWithComps parent)
        {
            return Patch_ChillFireBan_Fuelled.UsesFlame(parent);
        }
    }

    [HarmonyPatch(typeof(CompRefuelable), nameof(CompRefuelable.ConsumeFuel))]
    public static class Patch_CompRefuelable_ConsumeFuel
    {
        public static bool Prefix(CompRefuelable __instance)
        {
            return !ReferenceEquals(__instance, Patch_CompRefuelable_CompTick.suppressing);
        }
    }

    [HarmonyPatch(typeof(CompFireOverlay), nameof(CompFireOverlay.PostDraw))]
    public static class Patch_CompFireOverlay_PostDraw
    {
        public static bool Prefix(CompFireOverlay __instance)
        {
            Thing parent = __instance.parent;
            if (parent?.Map == null)
            {
                return true;
            }
            if (!RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent))
            {
                return false; // it really is out — no flame sprite to draw
            }
            return true;
        }
    }
}
