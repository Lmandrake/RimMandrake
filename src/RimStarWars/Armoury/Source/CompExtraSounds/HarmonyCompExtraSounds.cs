using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace CompExtraSounds;

[StaticConstructorOnStartup]
internal static class HarmonyCompExtraSounds
{
    static HarmonyCompExtraSounds()
    {
        Harmony harmony = new Harmony("jecstools.jecrell.comps.sounds");
        harmony.Patch(AccessTools.Method(typeof(Verb_MeleeAttack), "SoundMiss"), postfix: new HarmonyMethod(typeof(HarmonyCompExtraSounds), nameof(SoundMissPostfix)));
        harmony.Patch(AccessTools.Method(typeof(Verb_MeleeAttack), "SoundHitPawn"), postfix: new HarmonyMethod(typeof(HarmonyCompExtraSounds), nameof(SoundHitPawnPostfix)));
        harmony.Patch(AccessTools.Method(typeof(Verb_MeleeAttack), "SoundHitBuilding"), postfix: new HarmonyMethod(typeof(HarmonyCompExtraSounds), nameof(SoundHitBuildingPostfix)));
    }

    public static void SoundHitPawnPostfix(ref SoundDef __result, Verb_MeleeAttack __instance)
    {
        if (__instance.caster is Pawn pawn)
        {
            SoundDef fromKind = pawn.kindDef?.GetModExtensionExtraSounds()?.soundHitPawn;
            if (fromKind != null)
            {
                __result = fromKind;
            }
            SoundDef fromWeapon = pawn.equipment?.Primary?.GetCompExtraSounds()?.Props.soundHitPawn;
            if (fromWeapon != null)
            {
                __result = fromWeapon;
            }
        }
    }

    public static void SoundMissPostfix(ref SoundDef __result, Verb_MeleeAttack __instance)
    {
        if (__instance.caster is Pawn pawn)
        {
            SoundDef fromWeapon = pawn.equipment?.Primary?.GetCompExtraSounds()?.Props.soundMiss;
            if (fromWeapon != null)
            {
                __result = fromWeapon;
            }
        }
    }

    public static void SoundHitBuildingPostfix(ref SoundDef __result, Verb_MeleeAttack __instance)
    {
        if (__instance.caster is Pawn pawn)
        {
            SoundDef fromWeapon = pawn.equipment?.Primary?.GetCompExtraSounds()?.Props.soundHitBuilding;
            if (fromWeapon != null)
            {
                __result = fromWeapon;
            }
        }
    }
}
