using Verse;

namespace VEF.Abilities;

public class Hediff_Ability : HediffWithComps
{
	public Ability ability;

	public override void ExposeData()
	{
		((HediffWithComps)this).ExposeData();
		Scribe_References.Look<Ability>(ref ability, "ability", false);
	}
}
