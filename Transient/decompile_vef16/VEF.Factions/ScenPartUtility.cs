using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Factions;

public static class ScenPartUtility
{
	public static List<ScenPart_ForcedFactionGoodwill> goodwillScenParts;

	public static Dictionary<FactionDef, bool> orginalPermanentEnemyCache;

	public static Dictionary<FactionDef, IntRange> startingGoodwillRangeCache;

	public static void SetCache()
	{
		orginalPermanentEnemyCache = new Dictionary<FactionDef, bool>();
		startingGoodwillRangeCache = new Dictionary<FactionDef, IntRange>();
		List<FactionDef> allDefsListForReading = DefDatabase<FactionDef>.AllDefsListForReading;
		for (int i = 0; i < allDefsListForReading.Count; i++)
		{
			FactionDef val = allDefsListForReading[i];
			orginalPermanentEnemyCache.Add(val, val.permanentEnemy);
		}
	}

	public static void FinaliseFactionGoodwillCharacteristics(FactionDef faction)
	{
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		if (goodwillScenParts == null)
		{
			goodwillScenParts = Find.Scenario.AllParts.Where((ScenPart p) => p.def == ScenPartDefOf.VFEC_ForcedFactionGoodwill).Cast<ScenPart_ForcedFactionGoodwill>().ToList();
		}
		for (int num = goodwillScenParts.Count - 1; num >= 0; num--)
		{
			ScenPart_ForcedFactionGoodwill scenPart_ForcedFactionGoodwill = goodwillScenParts[num];
			if (scenPart_ForcedFactionGoodwill.AffectsFaction(faction))
			{
				faction.permanentEnemy = scenPart_ForcedFactionGoodwill.alwaysHostile;
				if (scenPart_ForcedFactionGoodwill.affectStartingGoodwill)
				{
					startingGoodwillRangeCache.Add(faction, scenPart_ForcedFactionGoodwill.startingGoodwillRange);
				}
				return;
			}
		}
		if (orginalPermanentEnemyCache.TryGetValue(faction, out var _))
		{
			faction.permanentEnemy = orginalPermanentEnemyCache[faction];
		}
	}
}
