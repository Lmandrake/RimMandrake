using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_InitialAbility : CompProperties
{
	public AbilityDef initialAbility;

	public CompProperties_InitialAbility()
	{
		base.compClass = typeof(CompInitialAbility);
	}
}
