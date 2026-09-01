using Verse;

namespace VEF.Genes;

public class HediffCompProperties_HumanEggLayer : HediffCompProperties
{
	public ThingDef eggUnfertilizedDef;

	public ThingDef eggFertilizedDef;

	public float eggLayIntervalDays = 1f;

	public bool eggLayFemaleOnly = true;

	public float eggProgressUnfertilizedMax = 1f;

	public bool maleDominant;

	public bool femaleDominant;

	public HediffCompProperties_HumanEggLayer()
	{
		base.compClass = typeof(HediffComp_HumanEggLayer);
	}
}
