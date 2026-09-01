using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobDriver_AnimalResource : JobDriver_GatherAnimalBodyResources
{
	private float gatherProgress;

	protected override float WorkTotal => 1700f;

	protected override CompHasGatherableBodyResource GetComp(Pawn animal)
	{
		return (CompHasGatherableBodyResource)(object)ThingCompUtility.TryGetComp<CompAnimalProduct>((Thing)(object)animal);
	}

	public CompAnimalProduct GetSpecificComp(Pawn animal)
	{
		return ThingCompUtility.TryGetComp<CompAnimalProduct>((Thing)(object)animal);
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_AnimalResource>(this, (TargetIndex)1);
		ToilFailConditions.FailOnDowned<JobDriver_AnimalResource>(this, (TargetIndex)1);
		ToilFailConditions.FailOnNotCasualInterruptible<JobDriver_AnimalResource>(this, (TargetIndex)1);
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		Toil wait = ToilMaker.MakeToil("MakeNewToils");
		wait.initAction = delegate
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Expected O, but got Unknown
			Pawn actor = wait.actor;
			LocalTargetInfo target = ((JobDriver)this).job.GetTarget((TargetIndex)1);
			Pawn val = (Pawn)((LocalTargetInfo)(ref target)).Thing;
			actor.pather.StopDead();
			PawnUtility.ForceWait(val, 15000, (Thing)null, true, false);
		};
		wait.tickIntervalAction = delegate(int delta)
		{
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_008b: Expected O, but got Unknown
			Pawn actor2 = wait.actor;
			actor2.skills.Learn(SkillDefOf.Animals, 0.13f * (float)delta, false, false);
			gatherProgress += StatExtension.GetStatValue((Thing)(object)actor2, StatDefOf.AnimalGatherSpeed, true, -1) * (float)delta;
			if (gatherProgress >= ((JobDriver_GatherAnimalBodyResources)this).WorkTotal)
			{
				GetSpecificComp((Pawn)(Thing)((JobDriver)this).job.GetTarget((TargetIndex)1)).InformGathered(((JobDriver)this).pawn);
				actor2.jobs.EndCurrentJob((JobCondition)2, true, true);
				if (ModLister.HasActiveModWithName("Alpha Animals"))
				{
					actor2.health.AddHediff(HediffDef.Named("AA_GatheredResource"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
			}
		};
		wait.AddFinishAction((Action)delegate
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Expected O, but got Unknown
			LocalTargetInfo target2 = ((JobDriver)this).job.GetTarget((TargetIndex)1);
			Pawn val2 = (Pawn)((LocalTargetInfo)(ref target2)).Thing;
			if (val2 != null && val2.CurJobDef == JobDefOf.Wait_MaintainPosture)
			{
				val2.jobs.EndCurrentJob((JobCondition)16, true, true);
			}
		});
		ToilFailConditions.FailOnDespawnedOrNull<Toil>(wait, (TargetIndex)1);
		ToilFailConditions.FailOnCannotTouch<Toil>(wait, (TargetIndex)1, (PathEndMode)2);
		wait.AddEndCondition((Func<JobCondition>)(() => ((JobDriver_GatherAnimalBodyResources)this).GetComp((Pawn)(Thing)((JobDriver)this).job.GetTarget((TargetIndex)1)).ActiveAndFull ? ((JobCondition)1) : ((JobCondition)4)));
		wait.defaultCompleteMode = (ToilCompleteMode)5;
		ToilEffects.WithProgressBar(wait, (TargetIndex)1, (Func<float>)(() => gatherProgress / ((JobDriver_GatherAnimalBodyResources)this).WorkTotal), false, -0.5f, false);
		wait.activeSkill = () => SkillDefOf.Animals;
		yield return wait;
	}
}
