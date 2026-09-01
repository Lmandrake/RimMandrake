using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class JobDriver_StudyBuilding : JobDriver
{
	public const int totalTime = 1200;

	public int totalTimer;

	private StudiableBuilding Building
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return (StudiableBuilding)(object)((LocalTargetInfo)(ref target)).Thing;
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
		StudiableBuildingDetails contentDetails = ((Def)((Thing)Building).def).GetModExtension<StudiableBuildingDetails>();
		LocalTargetInfo val = base.job.GetTarget((TargetIndex)1);
		_ = ((LocalTargetInfo)(ref val)).Thing;
		ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_StudyBuilding>(this, (TargetIndex)1);
		ToilFailConditions.FailOnBurningImmobile<JobDriver_StudyBuilding>(this, (TargetIndex)1);
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
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			Pawn actor = study.actor;
			if (actor.skills != null && contentDetails.skillForStudying != null)
			{
				actor.skills.Learn(contentDetails.skillForStudying, 0.025f * (float)delta, false, false);
			}
			actor.rotationTracker.FaceTarget(actor.CurJob.GetTarget((TargetIndex)1));
			totalTimer += delta;
			if (totalTimer > 1200)
			{
				Building.Study(base.pawn);
				actor.jobs.EndCurrentJob((JobCondition)2, true, true);
			}
		};
		if (contentDetails.showProgressBar)
		{
			ToilEffects.WithProgressBar(study, (TargetIndex)1, (Func<float>)(() => (float)totalTimer / 1200f), false, -0.5f, false);
		}
		ToilFailConditions.FailOnCannotTouch<Toil>(study, (TargetIndex)1, (PathEndMode)2);
		if (contentDetails.showResearchEffecter)
		{
			ToilEffects.WithEffect(study, EffecterDefOf.Research, (TargetIndex)1, (Color?)null);
		}
		study.defaultCompleteMode = (ToilCompleteMode)5;
		if (contentDetails.skillForStudying != null)
		{
			study.activeSkill = () => contentDetails.skillForStudying;
		}
		study.handlingFacing = true;
		yield return study;
	}
}
