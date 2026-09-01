using Verse;

namespace VEF.AnimalBehaviours;

public class CompNoTamingDecay : ThingComp
{
	public CompProperties_NoTamingDecay Props => (CompProperties_NoTamingDecay)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddNoTamingDecayAnimalToList(((Thing)base.parent).def);
	}
}
