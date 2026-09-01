using BigAndSmall.Abillities;
using Verse;

namespace BigAndSmall;

public class CompProperties_ParasiteAbility : CompProperties_AbilityJumpAndUseOn
{
	public HediffDef pilotHediff;

	public CompProperties_ParasiteAbility()
	{
		((AbilityCompProperties)this).compClass = typeof(ParasiteAbility);
	}
}
