using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class Pawn_HealthScale
{
	private static readonly Dictionary<Hediff_Injury, float> injuryRescaling = new Dictionary<Hediff_Injury, float>();

	private static int lastTick = 0;

	public static void Postfix(ref float __result, Pawn __instance)
	{
		BSCache cachePrepatched = __instance.GetCachePrepatched();
		if (cachePrepatched == null || cachePrepatched.IsTempCache)
		{
			return;
		}
		float num = __result * cachePrepatched.healthMultiplier;
		if (!cachePrepatched.injuriesRescaled)
		{
			int ticksGame = Find.TickManager.TicksGame;
			if (ticksGame != lastTick)
			{
				lastTick = ticksGame;
				injuryRescaling.Clear();
			}
			else
			{
				List<Hediff_Injury> list = injuryRescaling.Keys.Where((Hediff_Injury x) => ((Hediff)x).pawn == __instance).ToList();
				for (int num2 = list.Count - 1; num2 >= 0; num2--)
				{
					Hediff_Injury val = list[num2];
					try
					{
						((Hediff)val).severityInt = injuryRescaling[val];
					}
					catch (Exception ex)
					{
						Log.Error($"Error while restoring injuries: {ex}\n{ex.StackTrace}");
					}
				}
			}
			float num3 = __result * cachePrepatched.healthMultiplier_previous;
			float num4 = num / num3;
			List<Hediff_Injury> list2 = new List<Hediff_Injury>();
			__instance.health.hediffSet.GetHediffs<Hediff_Injury>(ref list2, (Predicate<Hediff_Injury>)null);
			foreach (Hediff_Injury item in list2)
			{
				float val2 = num4;
				injuryRescaling[item] = ((Hediff)item).Severity;
				if (!HediffUtility.CanHealNaturally(item) && (!cachePrepatched.creationTick.HasValue || cachePrepatched.creationTick == BS.Tick))
				{
					val2 = Math.Min(1f, val2);
				}
				((Hediff)item).severityInt = ((Hediff)item).Severity * num4;
				if (((Hediff)item).Severity < 0.05f)
				{
					((Hediff)item).severityInt = 0f;
				}
			}
			cachePrepatched.injuriesRescaled = true;
		}
		__result = num;
	}
}
