using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class LockedNeed
{
	public static void UpdateLockedNeeds(Gene gene)
	{
		List<PawnExtension> list = gene.def.ExtensionsOnDef<PawnExtension, GeneDef>((List<Type>)null, (List<Type>)null, doSort: true);
		if (!GenCollection.Any<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension x) => x.lockedNeeds != null && GenCollection.Any<LockedNeedClass>(x.lockedNeeds, (Predicate<LockedNeedClass>)((LockedNeedClass x) => x.need != null)))))
		{
			return;
		}
		foreach (LockedNeedClass item in from x in list.Where((PawnExtension x) => x.lockedNeeds != null).SelectMany((PawnExtension x) => x.lockedNeeds)
			where x.need != null
			select x)
		{
			float value = item.value;
			bool minValue = item.minValue;
			NeedDef need = item.need;
			Pawn pawn = gene.pawn;
			object obj;
			if (pawn == null)
			{
				obj = null;
			}
			else
			{
				Pawn_NeedsTracker needs = pawn.needs;
				obj = ((needs != null) ? needs.TryGetNeed(need) : null);
			}
			Need val = (Need)obj;
			if (val == null)
			{
				continue;
			}
			if (minValue)
			{
				if (val.CurLevelPercentage < value)
				{
					val.CurLevel = val.MaxLevel * value;
				}
			}
			else
			{
				val.CurLevel = val.MaxLevel * value;
			}
		}
	}
}
