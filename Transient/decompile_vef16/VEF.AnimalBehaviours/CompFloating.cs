using Verse;

namespace VEF.AnimalBehaviours;

public class CompFloating : ThingComp
{
	public CompProperties_Floating Props => (CompProperties_Floating)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddFloatingAnimalToList((Thing)(object)base.parent);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveFloatingAnimalFromList((Thing)(object)base.parent);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveFloatingAnimalFromList((Thing)(object)base.parent);
	}
}
