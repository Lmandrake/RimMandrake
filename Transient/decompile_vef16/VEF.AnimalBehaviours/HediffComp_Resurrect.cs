using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_Resurrect : HediffComp
{
	public int resurrectionsLeft = 1;

	public HediffCompProperties_Resurrect Props => (HediffCompProperties_Resurrect)(object)base.props;

	public override string CompLabelInBracketsExtra
	{
		get
		{
			if (AnimalBehaviours_Settings.flagResurrection)
			{
				return ((HediffComp)this).CompLabelInBracketsExtra + resurrectionsLeft + " lives";
			}
			return ((HediffComp)this).CompLabelInBracketsExtra;
		}
	}

	public override void CompExposeData()
	{
		Scribe_Values.Look<int>(ref resurrectionsLeft, "resurrectionsLeft", 1, false);
	}

	public override void CompPostMake()
	{
		((HediffComp)this).CompPostMake();
		resurrectionsLeft = Props.livesLeft;
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)((Hediff)base.parent).pawn.Corpse).Map != null && resurrectionsLeft > 1)
		{
			SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)((Hediff)base.parent).pawn.Corpse).Position, ((Thing)((Hediff)base.parent).pawn.Corpse).Map, false)));
			FleckMaker.AttachedOverlay((Thing)(object)((Hediff)base.parent).pawn, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
			ResurrectionUtility.TryResurrect(((Hediff)base.parent).pawn.Corpse.InnerPawn, (ResurrectionParams)null);
			resurrectionsLeft--;
		}
	}
}
