using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Floating : HediffCompProperties
{
	public int checkingInterval = 500;

	public HediffCompProperties_Floating()
	{
		base.compClass = typeof(HediffComp_Floating);
	}
}
