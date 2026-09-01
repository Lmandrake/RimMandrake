using System.Collections.Generic;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_EnrageOtherPawns : CompProperties
{
	public List<PawnKindDef> pawnkinddefsToAffect;

	public int checkingInterval = 200;

	public CompProperties_EnrageOtherPawns()
	{
		base.compClass = typeof(CompEnrageOtherPawns);
	}
}
