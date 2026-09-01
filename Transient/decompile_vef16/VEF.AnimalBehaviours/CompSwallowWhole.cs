using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompSwallowWhole : ThingComp
{
	public CompProperties_SwallowWhole Props => (CompProperties_SwallowWhole)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		if (Props.filthToMake == null)
		{
			Props.filthToMake = ThingDefOf.Filth_AmnioticFluid;
		}
	}
}
