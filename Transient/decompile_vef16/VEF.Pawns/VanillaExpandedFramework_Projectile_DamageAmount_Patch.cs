using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_Projectile_DamageAmount_Patch
{
	public static void Postfix(Projectile __instance, ref int __result)
	{
		Thing launcher = __instance.Launcher;
		Pawn val = (Pawn)(object)((launcher is Pawn) ? launcher : null);
		if (val != null)
		{
			__result = (int)((float)__result * StatExtension.GetStatValue((Thing)(object)val, VEFDefOf.VEF_RangeAttackDamageFactor, true, -1));
		}
	}
}
