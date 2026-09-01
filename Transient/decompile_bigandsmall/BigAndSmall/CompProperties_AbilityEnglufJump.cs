using Verse;

namespace BigAndSmall;

public class CompProperties_AbilityEnglufJump : CompProperties_AbilityEngluf_Abstract
{
	public CompProperties_AbilityEnglufJump()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_SlimeEnglufJump);
	}
}
