using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public class CanBeStunnedByDamagePatch
{
	[HarmonyPatch(typeof(StunHandler), "CanBeStunnedByDamage")]
	[HarmonyPrefix]
	public static bool CanBeStunnedByDamage_Prefix(ref bool __result, StunHandler __instance, DamageDef def)
	{
		if (def.causeStun)
		{
			Thing parent = __instance.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val != null)
			{
				BSCache cachePrepatched = val.GetCachePrepatched();
				if (cachePrepatched != null && def == DamageDefOf.EMP && cachePrepatched.empVulnerable)
				{
					__result = true;
					return false;
				}
			}
		}
		return true;
	}
}
