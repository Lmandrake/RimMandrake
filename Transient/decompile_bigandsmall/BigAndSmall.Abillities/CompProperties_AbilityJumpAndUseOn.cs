using RimWorld;
using Verse;

namespace BigAndSmall.Abillities;

public abstract class CompProperties_AbilityJumpAndUseOn : CompProperties_AbilityEffect
{
	public CompProperties_AbilityJumpAndUseOn()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_JumpAndUseOn);
	}
}
