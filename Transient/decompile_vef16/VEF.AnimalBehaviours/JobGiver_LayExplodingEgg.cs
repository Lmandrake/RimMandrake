using System;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobGiver_LayExplodingEgg : ThinkNode_JobGiver
{
	private const float LayRadius = 5f;

	protected override Job TryGiveJob(Pawn pawn)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		CompExplodingEggLayer compExplodingEggLayer = ThingCompUtility.TryGetComp<CompExplodingEggLayer>((Thing)(object)pawn);
		if (compExplodingEggLayer == null || !compExplodingEggLayer.CanLayNow)
		{
			return null;
		}
		IntVec3 val = RCellFinder.RandomWanderDestFor(pawn, ((Thing)pawn).Position, 5f, (Func<Pawn, IntVec3, IntVec3, bool>)null, (Danger)2, false);
		return JobMaker.MakeJob(InternalDefOf.VEF_LayExplodingEgg, LocalTargetInfo.op_Implicit(val));
	}
}
