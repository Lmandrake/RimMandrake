using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_ConsumeSoul : CompProperties_AbilityEffect
{
	public SiphonSoul siphonSoul = new SiphonSoul();

	public bool doKill = true;

	public bool doEnslave;

	public CompProperties_ConsumeSoul()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_ConsumeSoul);
	}
}
