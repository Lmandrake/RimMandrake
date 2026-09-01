using Verse;

namespace VEF.Abilities;

public class CompAbilitySpawn : ThingComp
{
	public Pawn pawn;

	public Ability source;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Pawn>(ref pawn, "spawningPawn", false);
		Scribe_References.Look<Ability>(ref source, "abilitySource", false);
	}
}
