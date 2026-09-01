using Verse;

namespace VEF.AnimalBehaviours;

public class CompInfecter : ThingComp
{
	public CompProperties_Infecter Props => (CompProperties_Infecter)(object)base.props;

	public int GetChance => Props.infectionChance;
}
