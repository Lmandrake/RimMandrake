using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_StageByVacuum : HediffCompProperties
{
	public float notVacuumStageIndex = 0.1f;

	public float vacuumStageIndex = 1f;

	public bool vacuumResistanceInArmorDisablesHediff;

	public float vacuumResistanceValueToDisable = 0.8f;

	public bool reverseVacuumResistanceEffects;

	public HediffCompProperties_StageByVacuum()
	{
		base.compClass = typeof(HediffComp_StageByVacuum);
	}
}
