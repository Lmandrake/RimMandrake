using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(TerrorUtility), "GetTerrorThoughts", new Type[] { typeof(Pawn) })]
public static class GetTerrorThoughts_Patch
{
	public static bool Prefix(ref IEnumerable<Thought_MemoryObservationTerror> __result, Pawn pawn)
	{
		if (pawn?.needs?.mood == null)
		{
			__result = Array.Empty<Thought_MemoryObservationTerror>();
			return false;
		}
		return true;
	}
}
