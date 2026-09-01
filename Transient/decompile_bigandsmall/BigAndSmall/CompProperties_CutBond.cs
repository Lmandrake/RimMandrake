using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_CutBond : CompProperties_AbilityEffect
{
	public CompProperties_CutBond()
	{
		((AbilityCompProperties)this).compClass = typeof(CompProperties_CutBondEffect);
	}
}
