using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_CutBondEffect : CompAbilityEffect
{
	public CompProperties_CutBond Props => (CompProperties_CutBond)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		Pawn pawn = ((AbilityComp)this).parent.pawn;
		Pawn val = null;
		Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicBond, false);
		Hediff_PsychicBond val2 = (Hediff_PsychicBond)(object)((firstHediffOfDef is Hediff_PsychicBond) ? firstHediffOfDef : null);
		if (val2 != null)
		{
			Thing target2 = ((HediffWithTarget)val2).target;
			val = (Pawn)(object)((target2 is Pawn) ? target2 : null);
			pawn.health.RemoveHediff((Hediff)(object)val2);
		}
		Hediff firstHediffOfDef2 = pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_SuccubusBond, false);
		if (firstHediffOfDef2 != null)
		{
			pawn.health.RemoveHediff(firstHediffOfDef2);
		}
		if (val != null)
		{
			Hediff firstHediffOfDef3 = val.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicBond, false);
			Hediff_PsychicBond val3 = (Hediff_PsychicBond)(object)((firstHediffOfDef3 is Hediff_PsychicBond) ? firstHediffOfDef3 : null);
			if (val3 != null)
			{
				val.health.RemoveHediff((Hediff)(object)val3);
			}
			Hediff firstHediffOfDef4 = val.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_SuccubusBond_Victim, false);
			if (firstHediffOfDef4 != null)
			{
				val.health.RemoveHediff(firstHediffOfDef4);
			}
		}
	}
}
