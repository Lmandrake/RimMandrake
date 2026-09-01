using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Site), "ShouldRemoveMapNow")]
public static class Site_ShouldRemoveMapNow_Patch
{
	public static void Postfix(Site __instance, ref bool __result, ref bool alsoRemoveWorldObject)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Invalid comparison between Unknown and I4
		if (!(__result & alsoRemoveWorldObject) || __instance.parts == null)
		{
			return;
		}
		foreach (Quest item in Find.QuestManager.QuestsListForReading)
		{
			if ((int)item.State != 1)
			{
				continue;
			}
			foreach (QuestPart item2 in item.PartsListForReading)
			{
				if (item2 is QuestPart_KeepSite questPart_KeepSite && questPart_KeepSite.mapParent == __instance)
				{
					alsoRemoveWorldObject = false;
					return;
				}
			}
		}
	}
}
