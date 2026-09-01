using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class GeneSetupHarmonyPatches
{
	[HarmonyPatch(typeof(PawnGenerator), "GenerateGenes")]
	[HarmonyPostfix]
	public static void GenerateGenes_Postfix(Pawn pawn, XenotypeDef xenotype, PawnGenerationRequest request)
	{
		if (!ModsConfig.BiotechActive)
		{
			return;
		}
		(ThingDef, bool) forcedRace = xenotype.GetForcedRace();
		var (val, _) = forcedRace;
		if (val != null)
		{
			bool item = forcedRace.Item2;
			try
			{
				pawn.SwapThingDef(val, state: true, 0, item);
			}
			catch (Exception ex)
			{
				Log.Error($"Error while trying to swap {pawn.Name} to {((Def)val).defName} during GenerateGenes step.\n{ex.Message}\n{ex.StackTrace}");
			}
		}
	}
}
