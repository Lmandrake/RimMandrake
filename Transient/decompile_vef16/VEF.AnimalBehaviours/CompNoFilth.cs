using Verse;

namespace VEF.AnimalBehaviours;

internal class CompNoFilth : ThingComp
{
	public CompProperties_NoFilth Props => (CompProperties_NoFilth)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddNoFilthAnimalToList((Thing)(object)base.parent);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveNoFilthAnimalFromList((Thing)(object)base.parent);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveNoFilthAnimalFromList((Thing)(object)base.parent);
	}
}
