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
            harmony.PatchAll(Assembly.GetExecutingAssembly());
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
}
