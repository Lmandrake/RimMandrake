using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

public class FactionGoodwillModifier : WorldComponent
{
	public FactionGoodwillModifier(World world)
		: base(world)
	{
	}

	public override void FinalizeInit(bool fromLoad)
	{
		ScenPartUtility.goodwillScenParts = null;
		ScenPartUtility.startingGoodwillRangeCache.Clear();
		List<FactionDef> allDefsListForReading = DefDatabase<FactionDef>.AllDefsListForReading;
		for (int i = 0; i < allDefsListForReading.Count; i++)
		{
			ScenPartUtility.FinaliseFactionGoodwillCharacteristics(allDefsListForReading[i]);
		}
	}
}
