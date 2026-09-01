using System;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HotSwappable]
[HarmonyPatch(typeof(ReachabilityImmediate), "CanReachImmediate", new Type[]
{
	typeof(IntVec3),
	typeof(LocalTargetInfo),
	typeof(Map),
	typeof(PathEndMode),
	typeof(Pawn)
})]
public static class VanillaExpandedFramework_ReachabilityImmediate_CanReachImmediate_Patch
{
	public static void Postfix(ref bool __result, IntVec3 start, LocalTargetInfo target, Map map, PathEndMode peMode, Pawn pawn)
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = VanillaExpandedFramework_Toils_Combat_FollowAndMeleeAttack_Patch.curPawn ?? VanillaExpandedFramework_JobGiver_ConfigurableHostilityResponse_TryGetAttackNearbyEnemyJob_Patch.curPawn ?? VanillaExpandedFramework_AttackTargetFinder_FindBestReachableMeleeTarget_Patch.curPawn ?? VanillaExpandedFramework_Verb_TryFindShootLineFromTo_Patch.curPawn;
		if (VanillaExpandedFramework_Pawn_PathFollower_AtDestinationPosition_Patch.curPawn != val && !__result && val != null)
		{
			Verb meleeVerb = val.GetMeleeVerb();
			float meleeReachRange = val.GetMeleeReachRange(meleeVerb);
			float num = IntVec3Utility.DistanceTo(((LocalTargetInfo)(ref target)).Cell, start);
			__result = num <= meleeReachRange && GenSight.LineOfSight(start, ((LocalTargetInfo)(ref target)).Cell, map);
		}
	}
}
