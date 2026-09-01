using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_DraculBite : CompProperties_AbilityBloodfeederBite
{
	public CompProperties_DraculBite()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_DraculBite);
	}
}
