using HarmonyLib;
using Verse;
using Verse.AI.Group;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Lord), "AddPawn")]
public static class VanillaExpandedFramework_Lord_AddPawn_Patch
{
	public static void Postfix(Lord __instance, Pawn p)
	{
		StorytellerWatcher component = Current.Game.GetComponent<StorytellerWatcher>();
		if (component.raidGroups == null)
		{
			return;
		}
		foreach (RaidGroup raidGroup in component.raidGroups)
		{
			if (raidGroup.pawns.Contains(p))
			{
				raidGroup.lords.Add(__instance);
			}
		}
	}
}
