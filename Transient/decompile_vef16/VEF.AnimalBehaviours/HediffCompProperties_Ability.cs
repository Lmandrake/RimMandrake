using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Ability : HediffCompProperties
{
	public AbilityDef ability;

	public int checkingInterval = 6000;

	public HediffCompProperties_Ability()
	{
		base.compClass = typeof(HediffComp_Ability);
	}
}
