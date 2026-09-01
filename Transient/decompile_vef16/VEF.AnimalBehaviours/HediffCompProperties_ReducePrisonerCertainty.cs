using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_ReducePrisonerCertainty : HediffCompProperties
{
	public float certaintyPerTick;

	public int checkingInterval = 250;

	public HediffCompProperties_ReducePrisonerCertainty()
	{
		base.compClass = typeof(HediffComp_ReducePrisonerCertainty);
	}
}
