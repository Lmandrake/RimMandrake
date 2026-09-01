using Verse;

namespace BigAndSmall;

internal class TrulyAgeless : TickdownGene
{
	private const int ticksPerYear = 3600000;

	public override void ResetCountdown()
	{
		tickDown = 500;
	}

	public override void TickEvent()
	{
		Pawn pawn = ((Gene)this).pawn;
		if (pawn == null)
		{
			return;
		}
		Pawn_AgeTracker ageTracker = pawn.ageTracker;
		if (ageTracker != null)
		{
			_ = ageTracker.AgeBiologicalYears;
			if (true && Gen.IsHashIntervalTick((Thing)(object)((Gene)this).pawn, 500) && ((Gene)this).pawn.ageTracker.AgeBiologicalYears > 25)
			{
				((Gene)this).pawn.ageTracker.AgeBiologicalTicks = 90000000L;
			}
		}
	}
}
