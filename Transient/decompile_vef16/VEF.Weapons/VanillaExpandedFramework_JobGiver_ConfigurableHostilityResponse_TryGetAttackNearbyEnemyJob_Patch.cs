using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(JobGiver_ConfigurableHostilityResponse), "TryGetAttackNearbyEnemyJob")]
public static class VanillaExpandedFramework_JobGiver_ConfigurableHostilityResponse_TryGetAttackNearbyEnemyJob_Patch
{
	public static Pawn curPawn;

	public static void Prefix(Pawn pawn)
	{
		curPawn = pawn;
	}

	public static void Finalizer()
	{
		curPawn = null;
	}
}
