using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(Pawn_GuestTracker), "SetupRecruitable")]
public static class PawnGenPatchRecruitable
{
	[HarmonyPrefix]
	public static bool Prefix(Pawn_GuestTracker __instance, Pawn ___pawn)
	{
		if (((Thing)___pawn).Faction == null)
		{
			return true;
		}
		float? num = null;
		foreach (PawnKindEdit item in PawnKindEdit.GetEditsFor(___pawn.kindDef, ((Thing)___pawn).Faction?.def))
		{
			if (item.UnwaveringlyLoyalChance.HasValue && (!item.IsGlobal || !num.HasValue))
			{
				num = item.UnwaveringlyLoyalChance.GetValueOrDefault();
			}
		}
		if (!num.HasValue)
		{
			return true;
		}
		__instance.Recruitable = !Rand.Chance(num.Value);
		return false;
	}
}
