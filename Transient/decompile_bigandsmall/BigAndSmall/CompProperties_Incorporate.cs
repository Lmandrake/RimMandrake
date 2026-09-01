using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_Incorporate : CompProperties_AbilityEffect
{
	public int pickCount = 2;

	public bool stealTraits = true;

	public CompProperties_Incorporate()
	{
		((AbilityCompProperties)this).compClass = typeof(CompProperties_IncorporateEffect);
	}
}
