using System;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Corpse), "TickRare")]
public static class Pawn_TickRare_Patch
{
	public static void Postfix(Corpse __instance)
	{
		if (__instance == null || __instance.InnerPawn == null)
		{
			return;
		}
		Pawn innerPawn = __instance.InnerPawn;
		if (!innerPawn.Dead)
		{
			return;
		}
		bool flag = false;
		try
		{
			for (int num = innerPawn.health.hediffSet.hediffs.Count - 1; num >= 0; num--)
			{
				Hediff val = innerPawn.health.hediffSet.hediffs[num];
				if (val is DraculVampirism draculVampirism)
				{
					bool num2 = draculVampirism.TryReanimate();
					flag = true;
					if (num2)
					{
						break;
					}
				}
				else if (val is VUReturning vUReturning)
				{
					bool num3 = vUReturning.TryReanimate();
					flag = true;
					if (num3)
					{
						break;
					}
				}
			}
		}
		catch (IndexOutOfRangeException ex)
		{
			Log.Warning($"Caught exception while trying to reanimate {innerPawn.Name} with DraculVampirism hediff. This *may* prevent reanimation. {ex.Message}\n{ex.StackTrace}");
		}
	}
}
