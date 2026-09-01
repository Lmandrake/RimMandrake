using System;
using System.Linq;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(PawnGenerator), "GeneratePawnRelations")]
[HarmonyPriority(int.MaxValue)]
public static class PawnGenerator_GeneratePawnRelations_Patch
{
	[HarmonyPrefix]
	public static bool DisableRelationsForForceGenderedPawns(Pawn pawn)
	{
		if (pawn == null)
		{
			return true;
		}
		if (pawn.HasActiveGene(BSDefs.Body_FemaleOnly) || pawn.HasActiveGene(BSDefs.Body_MaleOnly))
		{
			return false;
		}
		try
		{
			ThingDef def = ((Thing)pawn).def;
			if (def != null)
			{
				RaceExtension raceExtension = def.GetRaceExtensions()?.FirstOrDefault();
				if (raceExtension != null && raceExtension.femaleGenderChance.HasValue)
				{
					return false;
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error("Managed error in PawnGenerator_GeneratePawnRelations_Patch:\n" + ex.Message + "\n" + ex.StackTrace);
		}
		return true;
	}
}
