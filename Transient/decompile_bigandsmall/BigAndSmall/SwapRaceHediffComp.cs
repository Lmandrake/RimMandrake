using System;
using Verse;

namespace BigAndSmall;

public class SwapRaceHediffComp : HediffComp
{
	public SwapRaceHediffCompProperties Props => (SwapRaceHediffCompProperties)(object)base.props;

	public override void CompPostPostRemoved()
	{
		((HediffComp)this).CompPostPostRemoved();
		BigAndSmallCache.queuedJobs.Enqueue((Action)delegate
		{
			if (Props.xenotype != null)
			{
				((Hediff)base.parent).pawn.genes.SetXenotype(Props.xenotype);
			}
			if (Props.swapTarget != null)
			{
				((Hediff)base.parent).pawn.SwapThingDef(Props.swapTarget, state: true, 100, force: true);
			}
		});
	}
}
