using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_AsexualReproduction : CompProperties
{
	public int reproductionIntervalDays = 1;

	public string customString = "";

	public bool produceEggs;

	public string eggDef = "";

	public bool isGreenGoo;

	public int GreenGooLimit;

	public string GreenGooTarget = "";

	public string asexualHatchedMessage = "VEF_AsexualHatched";

	public string asexualCloningMessage = "VEF_AsexualCloning";

	public string asexualEggMessage = "VEF_AsexualHatchedEgg";

	public bool convertsIntoAnotherDef;

	public string newDef = "";

	public CompProperties_AsexualReproduction()
	{
		base.compClass = typeof(CompAsexualReproduction);
	}
}
