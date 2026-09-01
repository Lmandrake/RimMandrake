using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.Cooking;

internal class HediffComp_WhileHavingThoughts : HediffComp
{
	public bool flagAmIThinking;

	public int checkingInterval = 600;

	public HediffCompProperties_WhileHavingThoughts Props => (HediffCompProperties_WhileHavingThoughts)(object)base.props;

	public override void CompExposeData()
	{
		Scribe_Values.Look<bool>(ref flagAmIThinking, "flagAmIThinking", false, false);
	}

	public override void CompPostMake()
	{
		((HediffComp)this).CompPostMake();
		if (Props.hediffReduction != "" && DefDatabase<HediffDef>.GetNamed(Props.hediffReduction, false) != null)
		{
			Hediff firstHediffOfDef = ((HediffComp)this).Pawn.health.hediffSet.GetFirstHediffOfDef(HediffDef.Named(Props.hediffReduction), false);
			if (firstHediffOfDef != null)
			{
				firstHediffOfDef.Severity -= Props.reductionAmount;
			}
		}
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, checkingInterval, delta))
		{
			return;
		}
		if (Props.thoughtDefs.Count > 0)
		{
			foreach (ThoughtDef thoughtDef in Props.thoughtDefs)
			{
				flagAmIThinking = false;
				if (((HediffComp)this).Pawn.needs.mood.thoughts.memories.GetFirstMemoryOfDef(thoughtDef) != null)
				{
					flagAmIThinking = true;
					break;
				}
			}
		}
		if (Props.removeThoughtDefs.Count > 0)
		{
			foreach (ThoughtDef removeThoughtDef in Props.removeThoughtDefs)
			{
				if (((HediffComp)this).Pawn.needs.mood.thoughts.memories.GetFirstMemoryOfDef(removeThoughtDef) != null)
				{
					((HediffComp)this).Pawn.needs.mood.thoughts.memories.GetFirstMemoryOfDef(removeThoughtDef).moodPowerFactor = 0f;
				}
			}
		}
		if (!flagAmIThinking)
		{
			((HediffComp)this).Pawn.health.RemoveHediff((Hediff)(object)base.parent);
		}
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		if (Props.resurrectionEffect && ((Thing)((Hediff)base.parent).pawn.Corpse).Map != null)
		{
			SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)((Hediff)base.parent).pawn.Corpse).Position, ((Thing)((Hediff)base.parent).pawn.Corpse).Map, false)));
			FleckMaker.AttachedOverlay((Thing)(object)((Hediff)base.parent).pawn.Corpse, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
			ResurrectionUtility.TryResurrect(((Hediff)base.parent).pawn.Corpse.InnerPawn, (ResurrectionParams)null);
		}
	}
}
