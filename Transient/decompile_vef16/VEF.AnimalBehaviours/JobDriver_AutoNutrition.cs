using System;
using System.Collections.Generic;
using System.Diagnostics;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobDriver_AutoNutrition : JobDriver
{
	private const int EatingDuration = 1000;

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		return true;
	}

	[DebuggerHidden]
	protected override IEnumerable<Toil> MakeNewToils()
	{
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.defaultCompleteMode = (ToilCompleteMode)3;
		val.defaultDuration = 1000;
		val.socialMode = (RandomSocialMode)0;
		ToilFailConditions.FailOnCannotTouch<Toil>(val, (TargetIndex)1, (PathEndMode)2);
		yield return ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)1, true, -0.5f);
		yield return Toils_General.Do((Action)delegate
		{
			if (base.pawn?.needs?.food != null)
			{
				Need_Food food = base.pawn.needs.food;
				((Need)food).CurLevel = ((Need)food).CurLevel + 1f;
			}
		});
	}
}
