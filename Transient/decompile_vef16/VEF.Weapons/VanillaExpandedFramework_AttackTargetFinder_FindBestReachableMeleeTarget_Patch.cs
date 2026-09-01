using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch(typeof(AttackTargetFinder), "FindBestReachableMeleeTarget")]
public static class VanillaExpandedFramework_AttackTargetFinder_FindBestReachableMeleeTarget_Patch
{
	public static Pawn curPawn;

	public static void Prefix(Pawn searcherPawn)
	{
		curPawn = searcherPawn;
	}

	public static void Finalizer()
	{
		curPawn = null;
	}
}
