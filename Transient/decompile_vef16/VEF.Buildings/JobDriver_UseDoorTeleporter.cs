using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class JobDriver_UseDoorTeleporter : JobDriver
{
	public IntVec3 targetCell;

	public DoorTeleporter Origin => ((LocalTargetInfo)(ref base.job.targetA)).Thing as DoorTeleporter;

	public DoorTeleporter Dest => ((GlobalTargetInfo)(ref base.job.globalTarget)).Thing as DoorTeleporter;

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		return true;
	}

	public override string GetReport()
	{
		return JobUtility.GetResolvedJobReportRaw(base.job.def.reportString, Origin.Name, (object)Origin, Dest.Name, (object)Dest, (string)null, (object)null);
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_UseDoorTeleporter>(this, (TargetIndex)1);
		((JobDriver)this).AddEndCondition((Func<JobCondition>)(() => (Dest != null && ((Thing)Dest).Spawned && !((Thing)Dest).Destroyed) ? ((JobCondition)1) : ((JobCondition)4)));
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		Toil val = ToilEffects.WithEffect(ToilEffects.WithProgressBarToilDelay(Toils_General.Wait(16, (TargetIndex)1), (TargetIndex)1, false, -0.5f), EffecterDefOf.Skip_Entry, (TargetIndex)1, (Color?)null);
		val.AddPreTickAction((Action)delegate
		{
			Origin.DoTeleportEffects((Thing)(object)base.pawn, base.ticksLeftThisToil, ((GlobalTargetInfo)(ref base.job.globalTarget)).Map, ref targetCell, Dest);
		});
		yield return val;
		yield return Toils_General.DoAtomic((Action)delegate
		{
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			Origin.Teleport((Thing)(object)base.pawn, ((GlobalTargetInfo)(ref base.job.globalTarget)).Map, targetCell);
		});
	}

	public override void ExposeData()
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		((JobDriver)this).ExposeData();
		Scribe_Values.Look<IntVec3>(ref targetCell, "targetCell", default(IntVec3), false);
	}
}
