using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn), "MakeCorpse", new Type[]
{
	typeof(Building_Grave),
	typeof(bool),
	typeof(float)
})]
public static class MakeCorpse_Patch
{
	public static Corpse corpse;

	public static void Postfix(ref Corpse __result, Pawn __instance)
	{
		corpse = __result;
	}
}
