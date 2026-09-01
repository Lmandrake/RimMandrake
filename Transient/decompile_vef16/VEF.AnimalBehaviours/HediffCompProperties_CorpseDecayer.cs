using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffCompProperties_CorpseDecayer : HediffCompProperties
{
	public int radius = 5;

	public int tickInterval = 500;

	public int decayOnHitPoints = 1;

	public float nutritionGained = 0.2f;

	public string corpseSound = "";

	public bool causeThoughtNearby;

	public int radiusForThought;

	public ThoughtDef thought;

	public HediffCompProperties_CorpseDecayer()
	{
		base.compClass = typeof(HediffComp_CorpseDecayer);
	}
}
