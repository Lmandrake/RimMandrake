using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_GiveHediffsInRangeExpanded : HediffComp
{
	private Mote mote;

	public HediffCompProperties_GiveHediffsInRangeExpanded Props => (HediffCompProperties_GiveHediffsInRangeExpanded)(object)base.props;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_0175: Unknown result type (might be due to invalid IL or missing references)
		//IL_019b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0201: Unknown result type (might be due to invalid IL or missing references)
		if (!RestUtility.Awake(((Hediff)base.parent).pawn) || ((Hediff)base.parent).pawn.health == null || ((Hediff)base.parent).pawn.health.InPainShock || !((Thing)((Hediff)base.parent).pawn).Spawned)
		{
			return;
		}
		if (!Props.hideMoteWhenNotDrafted || ((Hediff)base.parent).pawn.Drafted)
		{
			if (Props.mote != null && (mote == null || ((Thing)mote).Destroyed))
			{
				mote = MoteMaker.MakeAttachedOverlay((Thing)(object)((Hediff)base.parent).pawn, Props.mote, Vector3.zero, 1f, -1f);
			}
			if (mote != null)
			{
				mote.Maintain();
			}
		}
		List<Pawn> list = null;
		list = ((!Props.onlyItsFaction) ? ((Thing)((Hediff)base.parent).pawn).Map.mapPawns.AllPawns : ((Thing)((Hediff)base.parent).pawn).Map.mapPawns.PawnsInFaction(((Thing)((Hediff)base.parent).pawn).Faction));
		foreach (Pawn item in list)
		{
			if (item.Dead || item.health == null || item == ((Hediff)base.parent).pawn || !(IntVec3Utility.DistanceTo(((Thing)item).Position, ((Thing)((Hediff)base.parent).pawn).Position) <= Props.range) || !Props.targetingParameters.CanTarget(TargetInfo.op_Implicit((Thing)(object)item), (ITargetingSource)null) || (Props.affectSameDef && ((Thing)item).def != ((Thing)((Hediff)base.parent).pawn).def) || !Props.needLOS || (Props.needLOS && !GenSight.LineOfSight(((Thing)item).Position, ((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map)))
			{
				continue;
			}
			Hediff val = item.health.hediffSet.GetFirstHediffOfDef(Props.hediff, false);
			if (val == null)
			{
				val = item.health.AddHediff(Props.hediff, item.health.hediffSet.GetBrain(), (DamageInfo?)null, (DamageResult)null);
				val.Severity = Props.initialSeverity;
				HediffComp_Link val2 = HediffUtility.TryGetComp<HediffComp_Link>(val);
				if (val2 != null)
				{
					val2.drawConnection = true;
					val2.other = (Thing)(object)((Hediff)base.parent).pawn;
				}
			}
			HediffComp_Disappears val3 = HediffUtility.TryGetComp<HediffComp_Disappears>(val);
			if (val3 == null)
			{
				Log.Error("HediffComp_GiveHediffsInRange has a hediff in props which does not have a HediffComp_Disappears");
			}
			else
			{
				val3.ticksToDisappear = 5;
			}
		}
	}
}
