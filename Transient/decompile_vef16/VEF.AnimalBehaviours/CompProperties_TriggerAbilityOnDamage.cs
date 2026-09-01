using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_TriggerAbilityOnDamage : CompProperties
{
	public AbilityDef ability;

	public float minDamageToTrigger;

	public CompProperties_TriggerAbilityOnDamage()
	{
		base.compClass = typeof(CompTriggerAbilityOnDamage);
	}
}
