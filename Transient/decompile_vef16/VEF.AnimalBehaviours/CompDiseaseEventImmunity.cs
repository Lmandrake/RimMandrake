using Verse;

namespace VEF.AnimalBehaviours;

internal class CompDiseaseEventImmunity : ThingComp
{
	public CompProperties_DiseaseEventImmunity Props => (CompProperties_DiseaseEventImmunity)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		StaticCollectionsClass.AddNoDiseasesAnimalToList((Thing)(object)base.parent);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		StaticCollectionsClass.RemoveNoDiseasesAnimalFromList((Thing)(object)base.parent);
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		StaticCollectionsClass.RemoveNoDiseasesAnimalFromList((Thing)(object)base.parent);
	}
}
