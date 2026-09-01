using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Abilities;

public class JobDriver_GotoTargetAndCastAbilityOnce : JobDriver_CastAbilityOnce
{
	protected override IEnumerable<Toil> MakeNewToils()
	{
		Pawn pawn = ((JobDriver)this).pawn;
		LocalTargetInfo targetA = ((JobDriver)this).TargetA;
		if (pawn != ((LocalTargetInfo)(ref targetA)).Thing)
		{
			foreach (Toil item in GotoToils())
			{
				yield return item;
			}
		}
		foreach (Toil item2 in base.MakeNewToils())
		{
			yield return item2;
		}
		((JobDriver)this).AddFinishAction((Action<JobCondition>)delegate
		{
			Thing thing = ((LocalTargetInfo)(ref ((JobDriver)this).job.targetA)).Thing;
			Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val != null && val.CurJobDef == VFE_DefOf_Abilities.VFEA_StandAndFaceTarget)
			{
				val.jobs.EndCurrentJob((JobCondition)2, true, true);
			}
		});
	}

	private IEnumerable<Toil> GotoToils()
	{
		Toil val = ToilMaker.MakeToil("GotoToils");
		val.initAction = delegate
		{
			((JobDriver)this).pawn.pather.StopDead();
		};
		val.tickAction = delegate
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0039: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_015a: Unknown result type (might be due to invalid IL or missing references)
			//IL_015f: Unknown result type (might be due to invalid IL or missing references)
			//IL_014e: Unknown result type (might be due to invalid IL or missing references)
			//IL_00be: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
			//IL_0096: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
			//IL_022d: Unknown result type (might be due to invalid IL or missing references)
			//IL_022e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0168: Unknown result type (might be due to invalid IL or missing references)
			//IL_0170: Unknown result type (might be due to invalid IL or missing references)
			//IL_0175: Unknown result type (might be due to invalid IL or missing references)
			//IL_017a: Unknown result type (might be due to invalid IL or missing references)
			//IL_017c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0186: Unknown result type (might be due to invalid IL or missing references)
			//IL_0190: Unknown result type (might be due to invalid IL or missing references)
			//IL_0198: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
			//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
			//IL_01b7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
			//IL_01f8: Unknown result type (might be due to invalid IL or missing references)
			//IL_01d7: Unknown result type (might be due to invalid IL or missing references)
			//IL_01dc: Unknown result type (might be due to invalid IL or missing references)
			//IL_01e9: Unknown result type (might be due to invalid IL or missing references)
			//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 cell = ((LocalTargetInfo)(ref ((JobDriver)this).job.targetA)).Cell;
			((JobDriver)this).pawn.rotationTracker.FaceTarget(LocalTargetInfo.op_Implicit(cell));
			Map map = ((Thing)((JobDriver)this).pawn).Map;
			if (GenSight.LineOfSight(((Thing)((JobDriver)this).pawn).Position, cell, map, true, (Func<IntVec3, bool>)null, 0, 0) && IntVec3Utility.DistanceTo(((Thing)((JobDriver)this).pawn).Position, cell) <= base.CompAbilities.currentlyCasting.def.distanceToTarget && (!((JobDriver)this).pawn.pather.Moving || GridsUtility.GetDoor(((JobDriver)this).pawn.pather.nextCell, map) == null))
			{
				((JobDriver)this).pawn.pather.StopDead();
				((JobDriver)this).pawn.rotationTracker.FaceTarget(LocalTargetInfo.op_Implicit(cell));
				Thing thing = ((LocalTargetInfo)(ref ((JobDriver)this).job.targetA)).Thing;
				Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
				if (val2 != null)
				{
					val2.jobs.TryTakeOrderedJob(JobMaker.MakeJob(VFE_DefOf_Abilities.VFEA_StandAndFaceTarget, LocalTargetInfo.op_Implicit((Thing)(object)((JobDriver)this).pawn)), (JobTag?)(JobTag)0, false);
				}
				((JobDriver)this).ReadyForNextToil();
			}
			else if (!((JobDriver)this).pawn.pather.Moving)
			{
				if (base.CompAbilities.currentlyCasting.def.distanceToTarget <= 1.5f)
				{
					((JobDriver)this).pawn.pather.StartPath(((JobDriver)this).TargetA, (PathEndMode)2);
				}
				else
				{
					IntVec3 val3 = IntVec3.Invalid;
					for (int i = 0; i < 9 && (i != 8 || !((IntVec3)(ref val3)).IsValid); i++)
					{
						IntVec3 val4 = cell + GenAdj.AdjacentCellsAndInside[i];
						if (GenGrid.InBounds(val4, map) && GenGrid.Walkable(val4, map) && val4 != ((Thing)((JobDriver)this).pawn).Position && SocialInteractionUtility.IsGoodPositionForInteraction(val4, cell, map) && ReachabilityUtility.CanReach(((JobDriver)this).pawn, LocalTargetInfo.op_Implicit(val4), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0) && (!((IntVec3)(ref val3)).IsValid || IntVec3Utility.DistanceToSquared(((Thing)((JobDriver)this).pawn).Position, val4) < IntVec3Utility.DistanceToSquared(((Thing)((JobDriver)this).pawn).Position, val3)))
						{
							val3 = val4;
						}
					}
					if (((IntVec3)(ref val3)).IsValid)
					{
						((JobDriver)this).pawn.pather.StartPath(LocalTargetInfo.op_Implicit(val3), (PathEndMode)1);
					}
					else
					{
						((JobDriver)this).ReadyForNextToil();
					}
				}
			}
		};
		val.handlingFacing = true;
		val.socialMode = (RandomSocialMode)0;
		val.defaultCompleteMode = (ToilCompleteMode)5;
		yield return val;
	}
}
