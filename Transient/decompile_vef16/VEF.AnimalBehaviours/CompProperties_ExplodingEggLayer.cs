using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_ExplodingEggLayer : CompProperties
{
	public float eggLayIntervalDays = 1f;

	public IntRange eggCountRange = IntRange.One;

	public ThingDef eggUnfertilizedDef;

	public ThingDef eggFertilizedDef;

	public int eggFertilizationCountMax = 1;

	public bool eggLayFemaleOnly = true;

	public float eggProgressUnfertilizedMax = 1f;

	public CompProperties_ExplodingEggLayer()
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(CompExplodingEggLayer);
	}
}
