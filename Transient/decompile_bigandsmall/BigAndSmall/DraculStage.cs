using Verse;

namespace BigAndSmall;

public class DraculStage : Gene
{
	public override void PostAdd()
	{
		((Gene)this).PostAdd();
		int draculStage = ((Def)base.def).GetModExtension<DraculStageExtension>().draculStage;
		int durationDays = ((Def)base.def).GetModExtension<DraculStageExtension>().durationDays;
		if (draculStage > 3 || base.pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_DraculAge, false) != null)
		{
			return;
		}
		DraculStageProgression draculStageProgression = (DraculStageProgression)(object)HediffMaker.MakeHediff(BSDefs.VU_DraculAge, base.pawn, (BodyPartRecord)null);
		int num = 60000;
		int ticksToDisappear = durationDays * num;
		foreach (HediffComp comp in ((HediffWithComps)draculStageProgression).comps)
		{
			HediffComp_Disappears val = (HediffComp_Disappears)(object)((comp is HediffComp_Disappears) ? comp : null);
			if (val != null)
			{
				val.ticksToDisappear = ticksToDisappear;
			}
		}
		base.pawn.health.AddHediff((Hediff)(object)draculStageProgression, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
	}
}
