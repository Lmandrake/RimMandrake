using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Polluter : HediffCompProperties
{
	public int amount;

	public int timer;

	public HediffCompProperties_Polluter()
	{
		base.compClass = typeof(HediffComp_Polluter);
	}
}
