using Verse;

namespace VEF.AnimalBehaviours;

public class CompDropOnDeath : ThingComp
{
	public CompProperties_DropOnDeath Props => (CompProperties_DropOnDeath)(object)base.props;
}
