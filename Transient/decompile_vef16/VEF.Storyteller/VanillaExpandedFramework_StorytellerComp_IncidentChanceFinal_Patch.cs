using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(StorytellerComp), "IncidentChanceFinal")]
public static class VanillaExpandedFramework_StorytellerComp_IncidentChanceFinal_Patch
{
	public static void Postfix(ref float __result, IncidentDef def)
	{
		if (!(__result > 0f))
		{
			return;
		}
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension != null && modExtension.incidentSpawnOptions != null)
		{
			IncidentSpawnOptions incidentSpawnOptions = modExtension.incidentSpawnOptions;
			float num = (from x in Find.FactionManager.GetFactions(false, false, true, (TechLevel)0, false)
				where (int)x.PlayerRelationKind == 2
				select x).Count();
			float num2 = (from x in Find.FactionManager.GetFactions(false, false, true, (TechLevel)0, false)
				where (int)x.PlayerRelationKind == 0
				select x).Count();
			if (num > 9f)
			{
				num = 9f;
			}
			if (num2 > 9f)
			{
				num2 = 9f;
			}
			if (num == 0f)
			{
				num = 0.1f;
			}
			if (num2 == 0f)
			{
				num2 = 0.1f;
			}
			if (incidentSpawnOptions.alliesIncreaseGoodIncidents && IsGoodIncident(def, incidentSpawnOptions))
			{
				__result *= num;
			}
			else if (incidentSpawnOptions.alliesReduceThreats && IsBadIncident(def, incidentSpawnOptions))
			{
				__result /= num;
			}
			if (incidentSpawnOptions.enemiesIncreaseGoodIncidents && IsGoodIncident(def, incidentSpawnOptions))
			{
				__result *= num2;
			}
			else if (incidentSpawnOptions.enemiesReduceThreats && IsBadIncident(def, incidentSpawnOptions))
			{
				__result /= num2;
			}
		}
	}

	private static bool IsGoodIncident(IncidentDef def, IncidentSpawnOptions incidentOptions)
	{
		if (def.letterDef != LetterDefOf.PositiveEvent)
		{
			return incidentOptions.goodIncidents.Contains(((Def)def).defName);
		}
		return true;
	}

	private static bool IsBadIncident(IncidentDef def, IncidentSpawnOptions incidentOptions)
	{
		if (def.category != IncidentCategoryDefOf.ThreatBig && def.category != IncidentCategoryDefOf.ThreatSmall && def.letterDef != LetterDefOf.ThreatBig && def.letterDef != LetterDefOf.ThreatSmall)
		{
			return incidentOptions.negativeIncidents.Contains(((Def)def).defName);
		}
		return true;
	}
}
