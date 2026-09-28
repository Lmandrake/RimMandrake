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
            Thing parent = __instance.parent;
            if (parent?.Map == null)
            {
                return;
            }
            if (!RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent))
            {
                __result = false;
            }
        }
    }

    [HarmonyPatch(typeof(CompHeatPusherPowered), nameof(CompHeatPusherPowered.ShouldPushHeatNow), MethodType.Getter)]
    public static class Patch_CompHeatPusherPowered_ShouldPushHeatNow
    {
        public static void Postfix(CompHeatPusherPowered __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            Thing parent = __instance.parent;
            if (parent?.Map == null)
            {
                return;
            }
            // Only a FUEL-burning heater is in scope — an electric one has
            // no CompRefuelable and must keep working (heat becomes
            // electric-only is the point, not "heat becomes nothing").
            // Thing.TryGetComp<T>() (ThingCompUtility) works on a plain
            // Thing without an unsafe cast to ThingWithComps.
            if (parent.TryGetComp<CompRefuelable>() == null)
            {
                return;
            }
            if (!RM_ChillFireGate.IsIgnitionAllowed(parent.Map, parent.Position, parent))
            {
                __result = false;
            }
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
