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

    // shd:particulate-screen's remaining half: "vapor, bio contamination...
    // damage completely". The only concrete vanilla mechanism matching that
    // description is airborne Toxic Fallout exposure -- vanilla has no other
    // direct-damage weather effect (Sandstorm/rain/etc. only touch accuracy,
    // move speed and mood, never hit points; confirmed by reading WeatherDef
    // and the vanilla GameCondition sources, not guessed). Ground-pollution
    // toxicity (ToxicUtility.PawnToxicTickInterval) is a different, non-
    // airborne hazard and is deliberately left untouched -- a particulate
    // screen filters what's in the air, not what's already in the dirt.
    [HarmonyPatch(typeof(ToxicUtility), nameof(ToxicUtility.DoAirbornePawnToxicDamage))]
    public static class Patch_ToxicUtility_DoAirbornePawnToxicDamage
    {
        [HarmonyPrefix]
        public static bool Prefix(Pawn p)
        {
            if (p?.Spawned != true || p.Map == null)
            {
                return true;
            }

            return !CompShieldParticulateScreen.IsPositionProtected(p.Position, p.Map);
        }
    }

    // Same ruling row, the plant-kill/item-rot half of Toxic Fallout's
    // per-cell effect (GameCondition_ToxicFallout.DoCellSteadyEffects).
    [HarmonyPatch(typeof(GameCondition_ToxicFallout), nameof(GameCondition_ToxicFallout.DoCellSteadyEffects))]
    public static class Patch_GameConditionToxicFallout_DoCellSteadyEffects
    {
        [HarmonyPrefix]
        public static bool Prefix(IntVec3 c, Map map)
        {
            if (map == null)
            {
                return true;
            }

            return !CompShieldParticulateScreen.IsPositionProtected(c, map);
        }
    }

    // shd:no-hard-landing-gate. Scenario.PostGravshipLanded is a confirmed-
    // live, fires-for-every-gravship-landing hook (GIZKA_HOLD_HOOK_SPIKE_1,
    // 2026-09-12) -- a postfix here is a one-time advisory check, never a
    // per-tick hazard system.
    [HarmonyPatch(typeof(Scenario), nameof(Scenario.PostGravshipLanded))]
    public static class Patch_Scenario_PostGravshipLanded
    {
        [HarmonyPostfix]
        public static void Postfix(Map map)
        {
            ShieldLandingAdvisory.Evaluate(map);
        }
    }
}
