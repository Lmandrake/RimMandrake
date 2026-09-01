using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class JobDriver_Loot : JobDriver
{
	public int totalTimeCached = -1;

	public int totalTimer;

	public int TotalTime
	{
		get
		{
			if (totalTimeCached == -1)
			{
				float num = 1f;
				if (Building.LootableExtension.useHackingSpeed)
				{
					num *= StatExtension.GetStatValue((Thing)(object)base.pawn, StatDefOf.HackingSpeed, true, -1);
				}
				totalTimeCached = (int)((float)(60 * Building.LootableExtension.secondsToOpen) / num);
			}
			return totalTimeCached;
		}
	}

	private LootableBuilding_Custom Building
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return (LootableBuilding_Custom)(object)((LocalTargetInfo)(ref target)).Thing;
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = base.pawn;
		LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
		return ReservationUtility.Reserve(pawn, LocalTargetInfo.op_Implicit(((LocalTargetInfo)(ref target)).Thing), base.job, 1, -1, (ReservationLayerDef)null, true, false);
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		LocalTargetInfo val = base.job.GetTarget((TargetIndex)1);
		_ = ((LocalTargetInfo)(ref val)).Thing;
		ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_Loot>(this, (TargetIndex)1);
		ToilFailConditions.FailOnBurningImmobile<JobDriver_Loot>(this, (TargetIndex)1);
		val = ((JobDriver)this).TargetA;
		if (((LocalTargetInfo)(ref val)).Thing.def.hasInteractionCell)
		{
			yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)4, false);
		}
		else
		{
			yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		}
		Toil study = ToilMaker.MakeToil("MakeNewToils");
		study.tickIntervalAction = delegate(int delta)
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			Pawn actor = study.actor;
			actor.rotationTracker.FaceTarget(actor.CurJob.GetTarget((TargetIndex)1));
			totalTimer += delta;
			if (totalTimer > TotalTime)
			{
				Building.Open();
				actor.jobs.EndCurrentJob((JobCondition)2, true, true);
			}
		};
		ToilFailConditions.FailOnCannotTouch<Toil>(study, (TargetIndex)1, (PathEndMode)2);
		ToilEffects.WithProgressBar(study, (TargetIndex)1, (Func<float>)(() => (float)totalTimer / (float)TotalTime), false, -0.5f, false);
		study.defaultCompleteMode = (ToilCompleteMode)5;
		study.handlingFacing = true;
		yield return study;
	}
}
