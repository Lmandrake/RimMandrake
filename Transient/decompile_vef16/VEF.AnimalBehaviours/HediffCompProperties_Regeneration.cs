using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_Regeneration : HediffCompProperties
{
	public int rateInTicks = 1000;

	public float healAmount = 0.1f;

	public bool healAll = true;

	public bool needsSun;

	public bool needsWater;

	public bool onlyBleeding;

	public bool onlyTendButNotHeal;

	public float tendMin = 0.7f;

	public float tendMax = 1f;

	public BodyPartDef bodypart;

	public HediffCompProperties_Regeneration()
	{
		base.compClass = typeof(HediffComp_Regeneration);
	}
}
