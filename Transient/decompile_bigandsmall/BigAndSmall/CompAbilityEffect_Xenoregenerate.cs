using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_Xenoregenerate : CompProperties_AbilityEffect
{
	public CompAbilityEffect_Xenoregenerate()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_FixWorstHealthCondition);
	}
}
