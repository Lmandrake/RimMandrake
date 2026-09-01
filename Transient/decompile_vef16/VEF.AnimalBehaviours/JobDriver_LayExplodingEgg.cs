using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobDriver_LayExplodingEgg : JobDriver
{
	private const int LayEgg = 500;

	private const TargetIndex LaySpotInd = 1;

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		return true;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		yield return Toils_Goto.GotoCell((TargetIndex)1, (PathEndMode)1);
		yield return Toils_General.Wait(500, (TargetIndex)0);
		yield return Toils_General.Do((Action)delegate
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			ForbidUtility.SetForbiddenIfOutsideHomeArea(GenSpawn.Spawn(((ThingWithComps)base.pawn).GetComp<CompExplodingEggLayer>().ProduceEgg(), ((Thing)base.pawn).Position, ((JobDriver)this).Map, (WipeMode)0));
		});
	}
}
