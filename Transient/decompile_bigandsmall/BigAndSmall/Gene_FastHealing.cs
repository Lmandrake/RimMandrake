using Verse;

namespace BigAndSmall;

public class Gene_FastHealing : TickdownGene
{
	public override void ResetCountdown()
	{
		tickDown = Rand.Range(30000, 90000);
	}

	public override void TickEvent()
	{
		HealthHelpers.CureWorstInjury(((Gene)this).pawn);
	}
}
