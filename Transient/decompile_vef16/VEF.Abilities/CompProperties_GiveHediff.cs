using RimWorld;
using Verse;

namespace VEF.Abilities;

public class CompProperties_GiveHediff : CompProperties_AbilityEffect
{
	public HediffDef hediffDef;

	public bool applyToCaster = true;

	public bool applyToRadius;

	public CompProperties_GiveHediff()
	{
		((AbilityCompProperties)this).compClass = typeof(CompGiveHediff);
	}
}
