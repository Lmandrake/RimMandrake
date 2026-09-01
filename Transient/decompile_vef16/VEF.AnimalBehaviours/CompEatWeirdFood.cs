using Verse;

namespace VEF.AnimalBehaviours;

public class CompEatWeirdFood : ThingComp
{
	public int currentFeedings;

	public CompProperties_EatWeirdFood Props => (CompProperties_EatWeirdFood)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref currentFeedings, "currentFeedings", 0, false);
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddWeirdEaterAnimalToList((Thing)(object)base.parent);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveWeirdEaterAnimalFromList((Thing)(object)base.parent);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveWeirdEaterAnimalFromList((Thing)(object)base.parent);
	}
}
