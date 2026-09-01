using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class GameUtils
{
	public static void RecacheStatsForThing(this Thing someThing)
	{
		CollectionExtensions.Do<StatDef>(DefDatabase<StatDef>.AllDefsListForReading.Where((StatDef x) => x.immutable), (Action<StatDef>)delegate(StatDef x)
		{
			x.Worker.ClearCacheForThing(someThing);
		});
	}

	public static void UnhealingRessurection(Pawn pawn)
	{
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Expected O, but got Unknown
		List<(HediffDef, BodyPartRecord)> list = new List<(HediffDef, BodyPartRecord)>();
		foreach (Hediff hediff in pawn.health.hediffSet.hediffs)
		{
			if (hediff is Hediff_MissingPart)
			{
				BodyPartRecord part = ((hediff is Hediff_MissingPart) ? hediff : null).Part;
				list.Add((hediff.def, part));
			}
		}
		ResurrectionUtility.TryResurrect(pawn, new ResurrectionParams
		{
			restoreMissingParts = false
		});
	}
}
