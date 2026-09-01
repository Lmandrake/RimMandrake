using RimWorld;
using Verse;

namespace BigAndSmall;

public class Genderbender_AbilityEffect : CompProperties_AbilityEffect
{
	public Genderbender_AbilityEffect()
	{
		((AbilityCompProperties)this).compClass = typeof(Genderbender);
	}
}
