using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class JobGiver_XenophobicRage : ThinkNode_JobGiver
{
	protected override Job TryGiveJob(Pawn pawn)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		if (!(pawn.MentalState is MentalState_XenophobicRage mentalState_XenophobicRage) || !mentalState_XenophobicRage.IsTargetStillValidAndReachable())
		{
			return null;
		}
		Thing spawnedParentOrMe = ((Thing)mentalState_XenophobicRage.target).SpawnedParentOrMe;
		Job val = JobMaker.MakeJob(JobDefOf.AttackMelee, LocalTargetInfo.op_Implicit(spawnedParentOrMe));
		val.canBashDoors = true;
		val.canBashFences = true;
		val.killIncappedTarget = true;
		if (spawnedParentOrMe != mentalState_XenophobicRage.target)
		{
			val.maxNumMeleeAttacks = 2;
		}
		return val;
	}
}
