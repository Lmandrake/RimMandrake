using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(WorldFactionsUIUtility), "DoRow")]
public static class VanillaExpandedFramework_WorldFactionsUIUtility_DoRow_Patch
{
	private static void Postfix(FactionDef factionDef, List<FactionDef> factions, int index, bool __result)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		if (__result)
		{
			ForcedFactionData forcedFactionData = FactionDefExtension.Get((Def)(object)factionDef).forcedFactionData;
			if (forcedFactionData.preventRemovalAtWorldGeneration && forcedFactionData.UnderRequiredWorldGenFactionCount(factionDef, factions))
			{
				Messages.Message(TaggedString.op_Implicit(forcedFactionData.GetWorldGenMissingFactionMessage(factionDef, factions)), MessageTypeDefOf.RejectInput, false);
				factions.Insert(index, factionDef);
			}
		}
	}
}
