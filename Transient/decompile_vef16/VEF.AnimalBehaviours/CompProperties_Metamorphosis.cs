using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Metamorphosis : CompProperties
{
	public float timeInYears;

	public string pawnToTurnInto;

	public string reportString = "VEF_TimeToMetamorphosis";

	public CompProperties_Metamorphosis()
	{
		base.compClass = typeof(CompMetamorphosis);
	}
}
