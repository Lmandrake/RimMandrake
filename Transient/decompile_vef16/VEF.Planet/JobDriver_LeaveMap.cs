using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Planet;

public class JobDriver_LeaveMap : JobDriver
{
	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		return true;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		yield return Toils_Goto.GotoCell((TargetIndex)1, (PathEndMode)3);
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.initAction = delegate
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			IntVec3 position = ((Thing)base.pawn).Position;
			FleckMaker.ThrowSmoke(((IntVec3)(ref position)).ToVector3(), ((JobDriver)this).Map, 2f);
			base.pawn.ExitMap(false, Rot4.Random);
			Find.World.GetComponent<HiringContractTracker>().pawns.Remove(base.pawn);
		};
		yield return ToilFailConditions.FailOn<Toil>(val, (Func<bool>)(() => base.pawn.Dead));
	}
}
