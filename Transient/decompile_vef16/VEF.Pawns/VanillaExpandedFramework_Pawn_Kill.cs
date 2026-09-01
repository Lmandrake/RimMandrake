using HarmonyLib;
using VEF.Things;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(Pawn), "Kill")]
public static class VanillaExpandedFramework_Pawn_Kill
{
	private static void Postfix(Pawn __instance)
	{
		if (__instance.Dead)
		{
			ThingDefExtension modExtension = ((Def)((Thing)__instance).def).GetModExtension<ThingDefExtension>();
			if (modExtension != null && modExtension.destroyCorpse && __instance.Corpse != null && !((Thing)__instance.Corpse).Destroyed)
			{
				((Thing)__instance.Corpse).Destroy((DestroyMode)0);
			}
		}
	}
}
