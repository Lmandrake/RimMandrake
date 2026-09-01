using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class Flagger : DefModExtension
{
	public float priority;

	public FlagStringList flags = new FlagStringList();

	public static List<FlagString> GetTagStrings(Pawn pawn, bool includeInactive)
	{
		if (pawn == null)
		{
			return new List<FlagString>();
		}
		List<Flagger> list = new List<Flagger>(20);
		list.AddRange(includeInactive ? pawn.GetAllExtensionsPlusInactive<Flagger>() : pawn.GetAllExtensions<Flagger>(null, null, doSort: false));
		FactionDef val = ((Thing)pawn).Faction?.def;
		if (val != null)
		{
			list.AddRange(val.ExtensionsOnDef<Flagger, FactionDef>((List<Type>)null, (List<Type>)null, doSort: false));
		}
		if (pawn.kindDef != null)
		{
			list.AddRange(pawn.kindDef.ExtensionsOnDef<Flagger, PawnKindDef>((List<Type>)null, (List<Type>)null, doSort: false));
		}
		list.AddRange(pawn.GetAllExtensionsOnBackStories<Flagger>());
		Pawn_RoyaltyTracker royalty = pawn.royalty;
		List<RoyalTitle> list2 = ((royalty != null) ? royalty.AllTitlesInEffectForReading : null);
		if (list2 != null)
		{
			foreach (RoyalTitle item in list2)
			{
				List<Flagger> list3 = item.def.ExtensionsOnDef<Flagger, RoyalTitleDef>((List<Type>)null, (List<Type>)null, doSort: false);
				if (GenCollection.Any<Flagger>(list3))
				{
					list.AddRange(list3);
				}
			}
		}
		if (list.Count > 0)
		{
			return list.OrderByDescending((Flagger x) => x.priority).SelectMany((Flagger x) => x.flags).ToList();
		}
		return new List<FlagString>();
	}
}
