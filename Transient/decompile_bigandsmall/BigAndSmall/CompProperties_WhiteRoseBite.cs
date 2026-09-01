using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_WhiteRoseBite : CompProperties_AbilityBloodfeederBite
{
	public CompProperties_WhiteRoseBite()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_WhiteRoseBite);
	}
}
