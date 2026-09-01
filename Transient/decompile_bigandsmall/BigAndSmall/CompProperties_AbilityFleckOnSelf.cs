using Verse;

namespace BigAndSmall;

public class CompProperties_AbilityFleckOnSelf : CompProperties_AbilityFleckOnTargetFixed
{
	public CompProperties_AbilityFleckOnSelf()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_FleckOnSelfFixed);
	}
}
