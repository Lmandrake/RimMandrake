using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_ReducePrisonerResistance : HediffCompProperties
{
	public float resistancePerTick;

	public int checkingInterval = 250;

	public HediffCompProperties_ReducePrisonerResistance()
	{
		base.compClass = typeof(HediffComp_ReducePrisonerResistance);
	}
}
