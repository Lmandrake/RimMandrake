using HarmonyLib;
using Verse;

namespace Spinning_Projectile;

// 🔴 KNOWN GAP: nothing in this assembly ever sets ThingComp_ReturningWeapon.
// IsThrowingWeapon to true - no ThingDef points a Verb at
// SpinningWeaponProjectile, and no Verb class for launching one was ported
// (the absorption carried the projectile/mote/comp but not whatever Verb
// the donor DLL used to fire it - not decompiled, not guessed). The postfix
// below is therefore currently a no-op even once it actually runs: this fix
// only closes the half of the bug that WAS reachable (the patch never
// applying at all), not the half that makes the feature complete.
[StaticConstructorOnStartup]
internal class HarmonyPatches
{
    [HarmonyPatch(typeof(PawnRenderUtility), "CarryWeaponOpenly")]
    internal static class PawnRenderUtility_CarryWeaponOpenly_Postfix
    {
        [HarmonyPostfix]
        private static void HideLightsaberWhenThrown(ref bool __result, Pawn pawn)
        {
            if (__result)
            {
                ThingComp_ReturningWeapon comp = pawn.equipment?.Primary?.TryGetComp<ThingComp_ReturningWeapon>();
                if (comp != null && comp.IsThrowingWeapon)
                {
                    __result = false;
                }
            }
        }
    }

    public static Harmony harmonyPatch;

    // A class with an explicit static constructor is NOT beforefieldinit, so
    // without [StaticConstructorOnStartup] on the class (above) this cctor
    // only runs on first access to the type - and nothing in the assembly
    // ever references HarmonyPatches, so it never ran at all and the
    // postfix above was never applied.
    static HarmonyPatches()
    {
        harmonyPatch = new Harmony("Weapon_Spinning_Projectile");
        // Scoped to this mod's own nested class, not a bare PatchAll(): the
        // assembly hosts several unrelated [HarmonyPatch] classes with their
        // own entry points (SelfHediffVerb's own PatchAll among them), and a
        // bare PatchAll() here would double-scan and double-patch those too.
        harmonyPatch.CreateClassProcessor(typeof(PawnRenderUtility_CarryWeaponOpenly_Postfix)).Patch();
    }
}
