using Verse;

namespace VEF.AnimalBehaviours;

public class CompLastStand : ThingComp
{
	public CompProperties_LastStand Props => (CompProperties_LastStand)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddLastStandAnimalToList((Thing)(object)base.parent, Props.finalCoolDownMultiplier);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveLastStandAnimalFromList((Thing)(object)base.parent);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveLastStandAnimalFromList((Thing)(object)base.parent);
	}
}
