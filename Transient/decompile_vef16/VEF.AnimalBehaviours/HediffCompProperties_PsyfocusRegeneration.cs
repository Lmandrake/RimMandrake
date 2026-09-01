using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_PsyfocusRegeneration : HediffCompProperties
{
	public int rateInTicks = 1000;

	public float regenAmount = 0.1f;

	public HediffCompProperties_PsyfocusRegeneration()
	{
		base.compClass = typeof(HediffComp_PsyfocusRegeneration);
	}
}
