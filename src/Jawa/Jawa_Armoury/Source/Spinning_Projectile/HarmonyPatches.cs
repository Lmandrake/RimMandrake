using HarmonyLib;
using Verse;

namespace Spinning_Projectile;

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

    static HarmonyPatches()
    {
        harmonyPatch = new Harmony("Weapon_Spinning_Projectile");
        // Ported source used bare PatchAll(), safe when this mod was its own
        // assembly. Merged into JawaArmoury.dll alongside SelfHediffVerb's own
        // PatchAll(), a bare PatchAll() here would double-scan the whole
        // assembly for [HarmonyPatch] classes and patch SelfHediffVerb's too.
        // Scoped to this mod's own nested class to preserve the original,
        // narrower effect.
        harmonyPatch.CreateClassProcessor(typeof(PawnRenderUtility_CarryWeaponOpenly_Postfix)).Patch();
    }
}
