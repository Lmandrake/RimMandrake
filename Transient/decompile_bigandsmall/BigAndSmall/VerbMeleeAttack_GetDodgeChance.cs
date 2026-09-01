using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Verb_MeleeAttack), "GetDodgeChance")]
public static class VerbMeleeAttack_GetDodgeChance
{
	public static void Postfix(ref float __result, LocalTargetInfo target)
	{
		Thing thing = ((LocalTargetInfo)(ref target)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val == null || !(__result < 0.99f))
		{
			return;
		}
		BSCache cachePrepatched = val.GetCachePrepatched();
		if (cachePrepatched != null)
		{
			__result /= cachePrepatched.scaleMultiplier.linear;
			if ((double)__result >= 0.98)
			{
				__result = 0.98f;
			}
		}
	}
}
