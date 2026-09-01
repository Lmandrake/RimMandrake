using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class CompAbilityEffect_SlimeRegurgitate : CompAbilityEffect
{
	public CompProperties_AbilityRegurgitate Props => (CompProperties_AbilityRegurgitate)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		Pawn pawn = ((AbilityComp)this).parent.pawn;
		IEnumerable<HediffDef> source = DefDatabase<HediffDef>.AllDefsListForReading.Where((HediffDef x) => ((Def)x).defName == "BS_Engulfed");
		Hediff firstHediffOfDef = pawn.health.hediffSet.GetFirstHediffOfDef(source.FirstOrDefault(), false);
		if (firstHediffOfDef != null)
		{
			pawn.health.RemoveHediff(firstHediffOfDef);
		}
		Job val = JobMaker.MakeJob(JobDefOf.Vomit);
		pawn.jobs.StopAll(false, true);
		pawn.jobs.StartJob(val, (JobCondition)16, (ThinkNode)null, true, true, (ThinkTreeDef)null, (JobTag?)null, false, false, (bool?)null, false, true, false);
	}
}
