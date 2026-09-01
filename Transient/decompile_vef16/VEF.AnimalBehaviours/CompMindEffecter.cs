using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompMindEffecter : ThingComp
{
	public List<Pawn> pawnList = new List<Pawn>();

	public Pawn thisPawn;

	public CompProperties_MindEffecter Props => (CompProperties_MindEffecter)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!AnimalBehaviours_Settings.flagEffecters || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ref Pawn reference = ref thisPawn;
		ThingWithComps parent = base.parent;
		reference = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (thisPawn == null || ((Thing)thisPawn).Map == null || thisPawn.Dead || thisPawn.Downed)
		{
			return;
		}
		foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)thisPawn).Position, ((Thing)thisPawn).Map, (float)Props.radius, true))
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val != null && (val.IsColonist || Props.notOnlyAffectColonists) && !val.Dead && !val.Downed && StatExtension.GetStatValue((Thing)(object)val, StatDefOf.PsychicSensitivity, true, -1) > 0f)
			{
				Find.TickManager.slower.SignalForceNormalSpeedShort();
				SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
				FleckMaker.AttachedOverlay((Thing)(object)base.parent, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
				val.mindState.mentalStateHandler.TryStartMentalState(DefDatabase<MentalStateDef>.GetNamed(Props.mentalState, true), (string)null, true, false, false, (Pawn)null, false, false, false);
			}
		}
	}
}
