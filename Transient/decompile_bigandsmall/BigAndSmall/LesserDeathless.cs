using RimWorld;
using Verse;

namespace BigAndSmall;

public class LesserDeathless : TickdownGene
{
	public override void PostRemove()
	{
		((Gene)this).PostRemove();
		Hediff firstHediffOfDef = ((Gene)this).pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.BS_LesserDeathless_Death, false);
		if (firstHediffOfDef != null)
		{
			((Gene)this).pawn.health.RemoveHediff(firstHediffOfDef);
		}
	}

	public override void TickEvent()
	{
		bool num = SanguophageUtility.ShouldBeDeathrestingOrInComaInsteadOfDead(((Gene)this).pawn);
		Hediff firstHediffOfDef = ((Gene)this).pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.BS_LesserDeathless_Death, false);
		if (num)
		{
			if (firstHediffOfDef == null)
			{
				Hediff val = HediffMaker.MakeHediff(BSDefs.BS_LesserDeathless_Death, ((Gene)this).pawn, (BodyPartRecord)null);
				((Gene)this).pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
		else if (firstHediffOfDef != null)
		{
			((Gene)this).pawn.health.RemoveHediff(firstHediffOfDef);
		}
	}

	public override void ResetCountdown()
	{
		tickDown = 0;
	}
}
