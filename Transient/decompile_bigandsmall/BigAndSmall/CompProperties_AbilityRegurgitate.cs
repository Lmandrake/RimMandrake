using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_AbilityRegurgitate : CompProperties_AbilityEffect
{
	public CompProperties_AbilityRegurgitate()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_SlimeRegurgitate);
	}
}
