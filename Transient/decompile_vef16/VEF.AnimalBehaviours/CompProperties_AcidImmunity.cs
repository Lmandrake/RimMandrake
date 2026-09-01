using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_AcidImmunity : CompProperties
{
	public CompProperties_AcidImmunity()
	{
		base.compClass = typeof(CompAcidImmunity);
	}
}
