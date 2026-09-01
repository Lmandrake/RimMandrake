using Verse;

namespace VEF.AnimalBehaviours;

public class CompAcidImmunity : ThingComp
{
	public CompProperties_AcidImmunity Props => (CompProperties_AcidImmunity)(object)base.props;
}
