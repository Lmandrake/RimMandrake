using System;
using Verse;

namespace BigAndSmall;

public class Gene_SelfRestoration : TickdownGene
{
	public override void ResetCountdown()
	{
		tickDown = Rand.Range(30000, 90000);
	}

	public override void TickEvent()
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		HealthUtility.FixWorstHealthCondition(((Gene)this).pawn, Array.Empty<HediffDef>());
	}
}
