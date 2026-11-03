using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using Verse;

namespace RimMandrake.Bones
{
    [DefOf]
    public static class RM_BonesDefOf
    {
        public static StatDef RM_BoneAmount;
        public static ThingDef RM_Bones;

        static RM_BonesDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_BonesDefOf));
        }
    }

    // BONES_LEAN_PORT_BUILD_TREELESS_WORLD: butchering yields bone. Pawn.ButcherProducts(Pawn butcher, float
    // efficiency) is the one entry every corpse butchery reaches (Corpse.ButcherProducts calls it); HugeThings'
    // Titanic prefix scales efficiency first, so bone follows the same yield curve as meat. The products are
    // passed through untouched and the bones are appended last.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.ButcherProducts))]
    [PatchFeature("Butcher bones", typeof(RM_BonesSettings), nameof(RM_BonesSettings.butcherBones))]
    public static class RM_Patch_ButcherBones
    {
        public static IEnumerable<Thing> Postfix(IEnumerable<Thing> __result, Pawn __instance, float efficiency)
        {
            int meat = 0;
            ThingDef meatDef = __instance?.RaceProps?.meatDef;
            foreach (Thing t in __result)
            {
                if (meatDef != null && t != null && t.def == meatDef)
                {
                    meat += t.stackCount;
                }
                yield return t;
            }
            if (__instance == null || __instance.RaceProps == null)
            {
                yield break;
            }
            RaceProperties race = __instance.RaceProps;
            float expected = RM_BonesKernel.ExpectedBones(RM_BonesSettings.butcherBones, race.IsFlesh,
                race.FleshType == FleshTypeDefOf.Insectoid, meat,
                __instance.GetStatValue(RM_BonesDefOf.RM_BoneAmount), RM_BonesSettings.boneMultiplier, efficiency);
            int count = GenMath.RoundRandom(expected);
            if (count > 0)
            {
                Thing bones = ThingMaker.MakeThing(RM_BonesDefOf.RM_Bones);
                bones.stackCount = count;
                yield return bones;
            }
        }
    }
}
