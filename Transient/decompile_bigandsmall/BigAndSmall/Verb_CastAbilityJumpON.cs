using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class Verb_CastAbilityJumpON : Verb_CastAbilityJump
{
	public override void OrderForceTarget(LocalTargetInfo target)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		DoJump(((Verb)this).CasterPawn, target, (Verb)(object)this, ((Verb)this).EffectiveRange);
	}

	public static void DoJump(Pawn pawn, LocalTargetInfo target, Verb verb, float range)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		Map map = ((Thing)pawn).Map;
		IntVec3 cell = ((LocalTargetInfo)(ref target)).Cell;
		Job val = JobMaker.MakeJob(JobDefOf.CastJump, target);
		val.verbToUse = verb;
		if (pawn.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)0, false))
		{
			FleckMaker.Static(cell, map, FleckDefOf.FeedbackGoto, 1f);
		}
	}

	public override bool ValidateTarget(LocalTargetInfo target, bool showMessages = true)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		for (int i = 0; i < ((Verb_CastAbility)this).ability.EffectComps.Count; i++)
		{
			if (!((Verb_CastAbility)this).ability.EffectComps[i].Valid(target, showMessages))
			{
				return false;
			}
		}
		return ((Verb_CastAbilityJump)this).ValidateTarget(target, showMessages);
	}
}
