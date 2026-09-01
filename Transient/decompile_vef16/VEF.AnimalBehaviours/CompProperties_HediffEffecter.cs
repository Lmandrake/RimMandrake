using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_HediffEffecter : CompProperties
{
	public int radius = 1;

	public float severity = 1f;

	public int tickInterval = 1000;

	public string hediff = "Plague";

	public bool notOnlyAffectColonists;

	public CompProperties_HediffEffecter()
	{
		base.compClass = typeof(CompHediffEffecter);
	}
}
