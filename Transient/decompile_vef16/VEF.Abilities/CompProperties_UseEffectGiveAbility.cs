using RimWorld;
using Verse;

namespace VEF.Abilities;

public class CompProperties_UseEffectGiveAbility : CompProperties_UseEffect
{
	public AbilityDef ability;

	public int level = 1;

	public HediffDef requiredHediff;

	public CompProperties_UseEffectGiveAbility()
	{
		((CompProperties)this).compClass = typeof(CompUseEffect_GiveAbility);
	}
}
