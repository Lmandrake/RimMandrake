using Verse;

namespace VEF.AnimalBehaviours;

public class CompInitialMentalState : ThingComp
{
	private bool addStateOnce = true;

	public CompProperties_InitialMentalState Props => (CompProperties_InitialMentalState)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref addStateOnce, "addStateOnce", true, false);
	}

	public override void CompTickRare()
	{
		((ThingComp)this).CompTickRare();
		if (addStateOnce)
		{
			ThingWithComps parent = base.parent;
			((Pawn)((parent is Pawn) ? parent : null)).mindState.mentalStateHandler.TryStartMentalState(Props.mentalstate, (string)null, true, false, false, (Pawn)null, false, false, false);
			addStateOnce = false;
		}
	}
}
