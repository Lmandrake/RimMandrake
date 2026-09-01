using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(TerrorUtility), "GetTerrorLevel", new Type[] { typeof(Pawn) })]
public static class GetTerrorLevel_Patch
{
	public static bool Prefix(ref float __result, Pawn pawn)
	{
		if (pawn?.needs?.mood == null)
		{
			__result = 0f;
			return false;
		}
		return true;
	}
}
