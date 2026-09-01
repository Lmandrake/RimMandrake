using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_DraculInfect : CompProperties_AbilityBloodfeederBite
{
	public CompProperties_DraculInfect()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_DraculInfect);
	}
}
