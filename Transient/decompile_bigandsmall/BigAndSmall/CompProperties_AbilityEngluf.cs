using Verse;

namespace BigAndSmall;

public class CompProperties_AbilityEngluf : CompProperties_AbilityEngluf_Abstract
{
	public CompProperties_AbilityEngluf()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_SlimeEngluf);
	}
}
