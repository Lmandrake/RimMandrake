using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_SlimeProliferation : CompProperties_AbilityEffect
{
	public CompProperties_SlimeProliferation()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_SlimeProliferation);
	}
}
