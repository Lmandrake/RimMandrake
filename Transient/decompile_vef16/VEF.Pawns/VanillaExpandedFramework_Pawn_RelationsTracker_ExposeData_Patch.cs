using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(Pawn_RelationsTracker), "ExposeData")]
public static class VanillaExpandedFramework_Pawn_RelationsTracker_ExposeData_Patch
{
	public static Dictionary<Pawn_RelationsTracker, PregnancyApproachData> pawnPregnancyApproachData = new Dictionary<Pawn_RelationsTracker, PregnancyApproachData>();

	public static void Postfix(Pawn_RelationsTracker __instance)
	{
		PregnancyApproachData additionalPregnancyApproachData = __instance.GetAdditionalPregnancyApproachData();
		Scribe_Deep.Look<PregnancyApproachData>(ref additionalPregnancyApproachData, "additionalPregnancyApproachData", Array.Empty<object>());
		if (additionalPregnancyApproachData != null)
		{
			pawnPregnancyApproachData[__instance] = additionalPregnancyApproachData;
		}
	}

	public static PregnancyApproachData GetAdditionalPregnancyApproachData(this Pawn_RelationsTracker tracker)
	{
		if (tracker != null)
		{
			if (!pawnPregnancyApproachData.TryGetValue(tracker, out var value) || value == null)
			{
				value = (pawnPregnancyApproachData[tracker] = new PregnancyApproachData());
			}
			PregnancyApproachData pregnancyApproachData2 = value;
			if (pregnancyApproachData2.partners == null)
			{
				pregnancyApproachData2.partners = new Dictionary<Pawn, PregnancyApproachDef>();
			}
			return value;
		}
		throw new Exception("Pawn_RelationsTracker was null by some reason");
	}
}
