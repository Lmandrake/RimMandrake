using RimWorld;
using Verse;

namespace BigAndSmall;

public class ShortPregnancy : TickdownGene
{
	public override void ResetCountdown()
	{
		tickDown = Rand.Range(6000, 120000);
	}

	public override void TickEvent()
	{
		Hediff val = default(Hediff);
		if (((Gene)this).pawn.health.hediffSet.TryGetHediff(HediffDefOf.PregnantHuman, ref val) && (double)val.Severity > 0.65)
		{
			val.Severity = 0.98f;
		}
	}
}
