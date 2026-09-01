using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_HediffAfterHealthLoss : CompProperties
{
	public int healthPercent = 50;

	public int tickInterval = 1000;

	public HediffDef hediff;

	public float severity = 1f;

	public BodyPartDef bodyPart;

	public CompProperties_HediffAfterHealthLoss()
	{
		base.compClass = typeof(CompHediffAfterHealthLoss);
	}
}
