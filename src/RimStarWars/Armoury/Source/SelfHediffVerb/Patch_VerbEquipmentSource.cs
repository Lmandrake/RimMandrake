using HarmonyLib;
using Verse;

namespace SelfHediffVerb;

[HarmonyPatch(typeof(Verb), "EquipmentSource")]
[HarmonyAfter("kaitorisenkou.ModularWeapons")]
public static class Patch_VerbEquipmentSource
{
    [HarmonyPostfix]
    public static void Postfix(ref Verb __instance, ref ThingWithComps __result)
    {
        if (__result == null && __instance.DirectOwner is CompVerbWithCooltime compVerbWithCooltime)
        {
            __result = compVerbWithCooltime.parent;
        }
    }
}
