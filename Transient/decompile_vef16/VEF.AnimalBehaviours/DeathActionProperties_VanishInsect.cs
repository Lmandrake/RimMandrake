using Verse;

namespace VEF.AnimalBehaviours;

public class DeathActionProperties_VanishInsect : DeathActionProperties
{
	public FleckDef fleck;

	public ThingDef filth;

	public IntRange filthCountRange = IntRange.One;

	public DeathActionProperties_VanishInsect()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.workerClass = typeof(DeathActionWorker_VanishInsect);
	}
}
