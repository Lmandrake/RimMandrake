using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Plants;

public class JobDriver_ExtractFlower : JobDriver
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

	protected Plant_Blooming Flower => (Plant_Blooming)(object)MinifyUtility.GetInnerIfMinified(Target);

	protected float TotalNeededWork => ((Thing)Flower).def.plant.harvestWork;

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
		ToilFailConditions.FailOnForbidden<JobDriver_ExtractFlower>(this, (TargetIndex)1);
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		Toil doWork = ToilFailConditions.FailOnCannotTouch<Toil>(ToilFailConditions.FailOnDestroyedNullOrForbidden<Toil>(ToilMaker.MakeToil("MakeNewToils"), (TargetIndex)1), (TargetIndex)1, (PathEndMode)2);
		doWork.initAction = delegate
		{
			totalNeededWork = TotalNeededWork;
			workLeft = totalNeededWork;
		};
		doWork.tickIntervalAction = delegate(int delta)
		{
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0093: Unknown result type (might be due to invalid IL or missing references)
			workLeft -= JobDriver_PlantWork.WorkDonePerTick(base.pawn, (Plant)(object)Flower) * (float)delta;
			if (base.pawn.skills != null)
			{
				base.pawn.skills.Learn(SkillDefOf.Plants, 0.085f * (float)delta, false, false);
			}
			if (workLeft <= 0f)
			{
				SoundStarter.PlayOneShot(SoundDefOf.Finish_Wood, SoundInfo.InMap(TargetInfo.op_Implicit((Thing)(object)Flower), (MaintenanceType)0));
				doWork.actor.jobs.curDriver.ReadyForNextToil();
			}
		};
		doWork.defaultCompleteMode = (ToilCompleteMode)5;
		ToilEffects.WithProgressBar(doWork, (TargetIndex)1, (Func<float>)(() => 1f - workLeft / totalNeededWork), false, -0.5f, false);
		ToilEffects.WithEffect(doWork, EffecterDefOf.Harvest_Plant, (TargetIndex)1, (Color?)null);
		ToilEffects.PlaySustainerOrSound(doWork, (Func<SoundDef>)(() => SoundDefOf.Interact_ConstructDirt), 1f);
		doWork.activeSkill = () => SkillDefOf.Plants;
		yield return doWork;
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.initAction = delegate
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 position = ((Thing)Flower).Position;
			bool num = Find.Selector.IsSelected((object)Flower);
			Thing val2 = GenSpawn.Spawn((Thing)(object)MinifyUtility.MakeMinified((Thing)(object)Flower, (DestroyMode)0), position, ((Thing)base.pawn).Map, (WipeMode)0);
			if (num && val2 != null)
			{
				Find.Selector.Select((object)val2, false, false);
			}
			((JobDriver)this).Map.designationManager.RemoveAllDesignationsOn(Target, false);
			Flower.plantAwaitingExtraction = false;
			((JobDriver)this).Map.GetComponent<MapComponent_BloomingPlants>()?.RemoveObjectFromMap((Thing)(object)Flower);
		};
		val.defaultCompleteMode = (ToilCompleteMode)1;
		yield return val;
	}
}
