using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Pawn_PathFollower), "AtDestinationPosition")]
public static class VanillaExpandedFramework_Pawn_PathFollower_AtDestinationPosition_Patch
{
	public static Pawn curPawn;

	public static void Prefix(Pawn_PathFollower __instance, Pawn ___pawn)
	{
		curPawn = ___pawn;
	}

	public static void Finalizer(Pawn_PathFollower __instance)
	{
		curPawn = null;
	}
}
