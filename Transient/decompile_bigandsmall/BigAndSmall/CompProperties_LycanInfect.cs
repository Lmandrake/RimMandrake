using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_LycanInfect : CompProperties_AbilityBloodfeederBite
{
	public CompProperties_LycanInfect()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_LycanInfect);
	}
}
