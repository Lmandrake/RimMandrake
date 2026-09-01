using System;
using System.Collections.Generic;
using Verse;

namespace VEF.Apparels;

public class CapacityImpactorGearMinLevel : CapacityImpactor
{
	public Thing gear;

	public ApparelExtension extension;

	public PawnCapacityDef capacity;

	public override bool IsDirect => false;

	public override string Readable(Pawn pawn)
	{
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		List<PawnCapacityMinLevel> pawnCapacityMinLevels = extension.pawnCapacityMinLevels;
		PawnCapacityMinLevel pawnCapacityMinLevel = ((pawnCapacityMinLevels != null) ? GenCollection.FirstOrDefault<PawnCapacityMinLevel>(pawnCapacityMinLevels, (Predicate<PawnCapacityMinLevel>)((PawnCapacityMinLevel x) => x.capacity == capacity)) : null);
		if (pawnCapacityMinLevel == null)
		{
			return ((Entity)gear).LabelCap;
		}
		return string.Format("{0}: {1}", ((Entity)gear).LabelCap, TranslatorFormattedStringExtensions.Translate("VEF.MinCapacityLevel", NamedArgumentUtility.Named((object)(GenMath.RoundedHundredth(pawnCapacityMinLevel.minLevel) * 100f), "MIN")));
	}
}
