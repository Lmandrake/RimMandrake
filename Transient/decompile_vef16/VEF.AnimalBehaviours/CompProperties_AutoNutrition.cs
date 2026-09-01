using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_AutoNutrition : CompProperties
{
	public int tickInterval = 250;

	public string consumingFoodReportString = "Eating food";

	public CompProperties_AutoNutrition()
	{
		base.compClass = typeof(CompAutoNutrition);
	}
}
