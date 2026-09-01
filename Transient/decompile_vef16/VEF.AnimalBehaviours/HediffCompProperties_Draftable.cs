using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Draftable : HediffCompProperties
{
	public int checkingInterval = 500;

	public bool makeNonFleeingToo;

	public bool canHandleWeapons;

	public HediffCompProperties_Draftable()
	{
		base.compClass = typeof(HediffComp_Draftable);
	}
}
