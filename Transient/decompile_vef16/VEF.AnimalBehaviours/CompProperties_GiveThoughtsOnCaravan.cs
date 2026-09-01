using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_GiveThoughtsOnCaravan : CompProperties
{
	public int intervalTicks = 30000;

	public ThoughtDef thought;

	public bool causeNegativeAtRandom;

	public float randomNegativeChance = 0.1f;

	public ThoughtDef negativeThought;

	public CompProperties_GiveThoughtsOnCaravan()
	{
		base.compClass = typeof(CompGiveThoughtsOnCaravan);
	}
}
