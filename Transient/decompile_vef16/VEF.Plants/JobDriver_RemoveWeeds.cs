using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Plants;

public class JobDriver_RemoveWeeds : JobDriver
{
	private float workLeft;

	private float totalNeededWork;

	public const TargetIndex FlowerInd = 1;

	protected Thing Target
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	protected Plant_Blooming Flower => Target as Plant_Blooming;

	protected float TotalNeededWork => 4000f;

	public override void ExposeData()
	{
		((JobDriver)this).ExposeData();
		Scribe_Values.Look<float>(ref workLeft, "workLeft", 0f, false);
		Scribe_Values.Look<float>(ref totalNeededWork, "totalNeededWork", 0f, false);
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		return ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(Target), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnForbidden<JobDriver_RemoveWeeds>(this, (TargetIndex)1);
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		Toil doWork = ToilFailConditions.FailOnCannotTouch<Toil>(ToilFailConditions.FailOnDestroyedNullOrForbidden<Toil>(ToilMaker.MakeToil("MakeNewToils"), (TargetIndex)1), (TargetIndex)1, (PathEndMode)2);
		doWork.initAction = delegate
		{
			totalNeededWork = TotalNeededWork;
			workLeft = totalNeededWork;
		};
		doWork.tickIntervalAction = delegate(int delta)
		{
			workLeft -= JobDriver_PlantWork.WorkDonePerTick(base.pawn, (Plant)(object)Flower) * (float)delta;
			if (base.pawn.skills != null)
			{
				base.pawn.skills.Learn(SkillDefOf.Plants, 0.085f * (float)delta, false, false);
			}
			if (workLeft <= 0f)
			{
				doWork.actor.jobs.curDriver.ReadyForNextToil();
			}
		};
		doWork.defaultCompleteMode = (ToilCompleteMode)5;
		ToilEffects.WithProgressBar(doWork, (TargetIndex)1, (Func<float>)(() => 1f - workLeft / totalNeededWork), false, -0.5f, false);
		ToilEffects.WithEffect(doWork, EffecterDefOf.Harvest_Plant, (TargetIndex)1, (Color?)null);
		ToilEffects.PlaySustainerOrSound(doWork, (Func<SoundDef>)(() => SoundDefOf.Interact_Sow), 1f);
		doWork.activeSkill = () => SkillDefOf.Plants;
		yield return doWork;
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.initAction = delegate
		{
			Flower.plantAwaitingWeedRemoval = false;
			Flower.hasWeeds = false;
			((JobDriver)this).Map.GetComponent<MapComponent_BloomingPlants>()?.RemoveWeedFromMap((Thing)(object)Flower);
		};
		val.defaultCompleteMode = (ToilCompleteMode)1;
		yield return val;
	}
}
