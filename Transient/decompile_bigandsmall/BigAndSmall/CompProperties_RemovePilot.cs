using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_RemovePilot : CompProperties_AbilityEffect
{
	public CompProperties_RemovePilot()
	{
		((AbilityCompProperties)this).compClass = typeof(RemovePilotComp);
	}
}
