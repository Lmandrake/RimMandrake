using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_ExplodingHatcher : CompProperties
{
	public float hatcherDaystoHatch = 1f;

	public PawnKindDef hatcherPawn;

	public float range = 3f;

	public int damage = 10;

	public string damageDef = "Flame";

	public string soundDef = "AA_GooPop";

	public CompProperties_ExplodingHatcher()
	{
		base.compClass = typeof(CompExplodingHatcher);
	}
}
