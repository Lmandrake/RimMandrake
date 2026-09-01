using Verse;

namespace VEF.Abilities;

public class CompAbilityProjectile : ThingComp
{
	public Ability ability;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Ability>(ref ability, "ability", false);
	}
}
