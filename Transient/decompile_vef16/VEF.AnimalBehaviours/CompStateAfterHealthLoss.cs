using Verse;

namespace VEF.AnimalBehaviours;

public class CompStateAfterHealthLoss : ThingComp
{
	public CompProperties_StateAfterHealthLoss Props => (CompProperties_StateAfterHealthLoss)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		if (Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			ThingWithComps parent = base.parent;
			Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
			if (val != null && ((Thing)val).Map != null && !val.Dead && !val.Downed && val.health.summaryHealth.SummaryHealthPercent < (float)Props.healthPercent / 100f)
			{
				val.mindState.mentalStateHandler.TryStartMentalState(DefDatabase<MentalStateDef>.GetNamed(Props.mentalState, true), (string)null, true, false, false, (Pawn)null, false, false, false);
			}
		}
	}
}
