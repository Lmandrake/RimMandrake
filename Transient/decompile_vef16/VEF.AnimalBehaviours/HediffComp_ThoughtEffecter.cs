using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_ThoughtEffecter : HediffComp
{
	public List<Pawn> pawnList = new List<Pawn>();

	public Pawn thisPawn;

	public HediffCompProperties_ThoughtEffecter Props => (HediffCompProperties_ThoughtEffecter)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_01da: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.tickInterval, delta))
		{
			return;
		}
		thisPawn = ((Hediff)base.parent).pawn;
		if (thisPawn == null || ((Thing)thisPawn).Map == null || thisPawn.Dead || thisPawn.Downed || (Props.needsToBeTamed && (!Props.needsToBeTamed || ((Thing)thisPawn).Faction == null || !((Thing)thisPawn).Faction.IsPlayer)))
		{
			return;
		}
		foreach (Thing item in GenRadial.RadialDistinctThingsAround(((Thing)thisPawn).Position, ((Thing)thisPawn).Map, (float)Props.radius, true))
		{
			Pawn val = (Pawn)(object)((item is Pawn) ? item : null);
			if (val == null || val.needs?.mood?.thoughts == null || WildManUtility.AnimalOrWildMan(val) || !val.RaceProps.IsFlesh || val == ((Hediff)base.parent).pawn || val.Dead || val.Downed || !(StatExtension.GetStatValue((Thing)(object)val, StatDefOf.PsychicSensitivity, true, -1) > 0f))
			{
				continue;
			}
			if (Props.showEffect)
			{
				Find.TickManager.slower.SignalForceNormalSpeedShort();
				SoundStarter.PlayOneShot(SoundDefOf.PsychicPulseGlobal, SoundInfo.op_Implicit(new TargetInfo(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, false)));
				FleckMaker.AttachedOverlay((Thing)(object)((Hediff)base.parent).pawn, DefDatabase<FleckDef>.GetNamed("PsycastPsychicEffect", true), Vector3.zero, 1f, -1f);
			}
			if (!Props.conditionalOnWellBeing)
			{
				val.needs.mood.thoughts.memories.TryGainMemory(ThoughtDef.Named(Props.thoughtDef), (Pawn)null, (Precept)null);
				continue;
			}
			Pawn_NeedsTracker needs = thisPawn.needs;
			if (needs != null)
			{
				Need_Food food = needs.food;
				if (((food != null) ? new bool?(food.Starving) : ((bool?)null)) == true)
				{
					goto IL_0287;
				}
			}
			if (!(thisPawn.health.hediffSet.PainTotal > 0f))
			{
				val.needs.mood.thoughts.memories.TryGainMemory(ThoughtDef.Named(Props.thoughtDef), (Pawn)null, (Precept)null);
				continue;
			}
			goto IL_0287;
			IL_0287:
			val.needs.mood.thoughts.memories.RemoveMemoriesOfDef(ThoughtDef.Named(Props.thoughtDef));
			val.needs.mood.thoughts.memories.TryGainMemory(ThoughtDef.Named(Props.thoughtDefWhenSuffering), (Pawn)null, (Precept)null);
		}
	}
}
