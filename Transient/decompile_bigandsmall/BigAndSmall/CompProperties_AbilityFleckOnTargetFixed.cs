using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_AbilityFleckOnTargetFixed : CompProperties_AbilityFleckOnTarget
{
	public CompProperties_AbilityFleckOnTargetFixed()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_FleckOnTargetFixed);
	}
}
