using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.Grammar;

namespace VEF.Research;

public static class ResearchProjectUtility
{
	public static void AutoAssignRules()
	{
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Expected O, but got Unknown
		RulePack value = Traverse.Create((object)VEFDefOf.VEF_Description_Schematic_Defaults).Field<RulePack>("rulePack").Value;
		foreach (ResearchProjectDef allDef in DefDatabase<ResearchProjectDef>.AllDefs)
		{
			if (allDef.tab != ResearchTabDefOf.Anomaly && allDef.generalRules == null)
			{
				allDef.generalRules = value;
			}
		}
		ResearchTabDef namedSilentFail = DefDatabase<ResearchTabDef>.GetNamedSilentFail("VanillaExpanded");
		if (namedSilentFail != null)
		{
			((CompProperties_Readable)ThingDefOf.Schematic.GetCompProperties<CompProperties_Book>()).doers.OfType<BookOutcomeProperties_GainResearch>().FirstOrDefault()?.tabs.Add(new BookTabItem
			{
				tab = namedSilentFail
			});
		}
	}
}
