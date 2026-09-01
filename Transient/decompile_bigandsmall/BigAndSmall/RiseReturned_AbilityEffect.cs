using RimWorld;
using Verse;

namespace BigAndSmall;

public class RiseReturned_AbilityEffect : CompProperties_AbilityEffect
{
	public RiseReturned_AbilityEffect()
	{
		((AbilityCompProperties)this).compClass = typeof(RiseReturned);
	}
}
