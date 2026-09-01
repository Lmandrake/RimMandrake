using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class NotifyEvents
{
	[HarmonyPatch(typeof(Pawn), "Kill")]
	[HarmonyPrefix]
	public static void PawnKillPrefix(Pawn __instance)
	{
		foreach (Hediff hediff in __instance.health.hediffSet.hediffs)
		{
			if (hediff is Piloted piloted)
			{
				piloted.RemovePilots(mayRemoveHediff: false);
			}
		}
	}
}
