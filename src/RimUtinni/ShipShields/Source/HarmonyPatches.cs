using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    [StaticConstructorOnStartup]
    public static class ShipShieldsMod
    {
        public const string HarmonyId = "mandrake.rut.shipshields";

        static ShipShieldsMod()
        {
            Harmony harmony = new Harmony(HarmonyId);
            RimMandrake.Shared.PatchApplier.Apply(harmony, Assembly.GetExecutingAssembly(), "RimMandrake.Utinni.ShipShields");
            Log.Message("[RimMandrake.Utinni.ShipShields] ready.");
        }
    }

    // shd:shield-collapse-evacuate ("Slow pressing things move through all
    // shields is long-standing canon") + shd:loadout-tradeoff (only the
    // currently-selected field should ever intercept anything).
    //
    // CompProjectileInterceptor.CheckIntercept is a normal instance method,
    // not virtual, so CompShieldGenerator cannot override it -- a Harmony
    // prefix is the only way to add the speed gate and the mode gate.
    // Scoped to CompShieldGenerator by type check: vanilla's own native
    // gravship/mech shields, and any other mod's interceptor, run
    // unmodified. Extending the slow-pass-through rule canon-wide (the
    // owner's note reads as "including the crew," i.e. every shield, not
    // just ours) is a separate, larger call the survey deliberately left
    // for a follow-up rather than quietly patching vanilla's own systems
    // here.
    [RimMandrake.Shared.PatchFeature("Patch_CompProjectileInterceptor_CheckIntercept", typeof(ShipShieldsSettings), "bubbleSlowPassThroughEnabled")]
    [HarmonyPatch(typeof(CompProjectileInterceptor), nameof(CompProjectileInterceptor.CheckIntercept))]
    public static class Patch_CompProjectileInterceptor_CheckIntercept
    {
        [HarmonyPrefix]
        public static bool Prefix(CompProjectileInterceptor __instance, Projectile projectile, ref bool __result)
        {
            if (!(__instance is CompShieldGenerator shield))
            {
                return true;
            }

            if (!shield.BubbleModeActive)
            {
                __result = false;
                return false;
            }

            if (ShipShieldsSettings.bubbleSlowPassThroughEnabled)
            {
                float speed = projectile?.def?.projectile != null ? projectile.def.projectile.SpeedTilesPerTick : 0f;
                if (speed < shield.Props.slowPassThroughSpeed)
                {
                    __result = false;
                    return false;
                }
            }

            return true;
        }
    }

    // shd:particulate-screen's toxic half (airborne Toxic Fallout exposure and the
    // fallout per-cell plant kill / item rot) is handled by ONE prefix set in
    // mandrake.rm.warscar (RM_AerosolScreenPatches_*), which reads every live
    // RM_CompAerosolScreen -- CompShieldParticulateScreen derives from it, so this
    // mod carries no ToxicUtility / GameCondition_ToxicFallout patches of its own.

    // shd:no-hard-landing-gate. Scenario.PostGravshipLanded is a confirmed-
    // live, fires-for-every-gravship-landing hook (GIZKA_HOLD_HOOK_SPIKE_1,
    // 2026-09-12) -- a postfix here fires two independent, additive
    // one-time landing checks: the advisory letter (unchanged since
    // 2026-09-12) and the lava-landing immediate damage burst (2026-09-18,
    // ShieldHazardExposureTracker.cs's class header). Neither is a per-tick
    // hazard system; the per-tick escalating-damage half is
    // ShieldHazardExposureTracker's own MapComponentTick, running
    // independently every map tick regardless of this hook.
    [HarmonyPatch(typeof(Scenario), nameof(Scenario.PostGravshipLanded))]
    public static class Patch_Scenario_PostGravshipLanded
    {
        [HarmonyPostfix]
        public static void Postfix(Map map)
        {
            ShieldLandingAdvisory.Evaluate(map);
            ShieldHazardExposureTracker.OnGravshipLanded(map);
        }
    }
}
