using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn), "SpawnSetup")]
public static class Pawn_SpawnSetup
{
	public static void Postfix(Pawn __instance, bool respawningAfterLoad)
	{
		if (respawningAfterLoad)
		{
			return;
		}
		float? obj;
		if (__instance == null)
		{
			obj = null;
		}
		else
		{
			Pawn_NeedsTracker needs = __instance.needs;
			if (needs == null)
			{
				obj = null;
			}
			else
			{
				Need_Food food = needs.food;
				obj = ((food != null) ? new float?(((Need)food).CurLevelPercentage) : ((float?)null));
			}
		}
		float? num = obj;
		Pawn_PostMapInit.RefreshPawnGenes(__instance);
		if (num.HasValue)
		{
			((Need)__instance.needs.food).CurLevelPercentage = num.Value;
		}
		((Def)((Thing)__instance).def).modExtensions?.OfType<RaceExtension>()?.FirstOrDefault()?.ApplyTrackerIfMissing(__instance);
		int? num2 = __instance.GetAllPawnExtensions().Max((PawnExtension x) => x.babyStartAge);
		if (num2.HasValue && __instance.ageTracker.AgeBiologicalYears < num2)
		{
			__instance.ageTracker.AgeBiologicalTicks = (long)(num2 * 3600000).Value + 1000L;
			DictCache<Pawn, BSCache>.Cache.TryRemove(__instance, out var _);
			HumanoidPawnScaler.GetCache(__instance, forceRefresh: true);
		}
	}
}
