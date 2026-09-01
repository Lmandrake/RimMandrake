using Verse;

namespace VEF.AnimalBehaviours;

internal class CompDoesntFlee : ThingComp
{
	public CompProperties_DoesntFlee Props => (CompProperties_DoesntFlee)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddNotFleeingAnimalToList((Thing)(object)base.parent);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)base.parent);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveNotFleeingAnimalFromList((Thing)(object)base.parent);
	}
}
