using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Verb), "TryFindShootLineFromTo")]
public static class VanillaExpandedFramework_Verb_TryFindShootLineFromTo_Patch
{
	public static Pawn curPawn;

	public static void Prefix(Verb __instance)
	{
		curPawn = __instance.CasterPawn;
	}

	public static void Finalizer()
	{
		curPawn = null;
	}
}
