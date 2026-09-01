using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_InitialHediff : CompProperties
{
	public string hediffname = "";

	public float hediffseverity;

	public bool applyToAGivenBodypart;

	public BodyPartDef part;

	public bool addRandomHediffs;

	public int numberOfHediffs = 1;

	public CompProperties_InitialHediff()
	{
		base.compClass = typeof(CompInitialHediff);
	}
}
