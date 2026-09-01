using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Resurrect : HediffCompProperties
{
	public int livesLeft = 1;

	public HediffCompProperties_Resurrect()
	{
		base.compClass = typeof(HediffComp_Resurrect);
	}
}
