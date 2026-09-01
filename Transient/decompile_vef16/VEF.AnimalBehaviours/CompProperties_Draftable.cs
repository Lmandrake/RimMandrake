using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_Draftable : CompProperties
{
	public bool makeNonFleeingToo;

	public bool canHandleWeapons;

	public bool conditionalOnTrainability;

	public int checkingInterval = 500;

	public CompProperties_Draftable()
	{
		base.compClass = typeof(CompDraftable);
	}
}
