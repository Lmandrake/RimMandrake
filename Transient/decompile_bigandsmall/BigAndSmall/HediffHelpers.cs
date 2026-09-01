using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public static class HediffHelpers
{
	public static bool TryAddToAllMatchingParts(this HediffDef hediffDef, Pawn pawn, List<BodyPartDef> targetPart, IEnumerable<BodyPartRecord> partsToConsider)
	{
		IEnumerable<BodyPartRecord> enumerable = partsToConsider.Where((BodyPartRecord x) => targetPart.Contains(x.def) && !pawn.health.hediffSet.HasHediff(hediffDef, x, false));
		foreach (BodyPartRecord item in enumerable)
		{
			pawn.health.AddHediff(hediffDef, item, (DamageInfo?)null, (DamageResult)null);
		}
		return enumerable.Any();
	}

	public static bool TryRemoveAllOfType(this HediffDef hediffDef, Pawn pawn)
	{
		IEnumerable<Hediff> source = pawn.health.hediffSet.hediffs.Where((Hediff x) => x.def == hediffDef);
		for (int num = source.Count() - 1; num >= 0; num--)
		{
			pawn.health.RemoveHediff(source.ElementAt(num));
		}
		return source.Any();
	}
}
