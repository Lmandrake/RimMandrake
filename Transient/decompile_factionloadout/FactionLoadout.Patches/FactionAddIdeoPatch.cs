using HarmonyLib;
using RimWorld;

namespace FactionLoadout.Patches;

public static class FactionAddIdeoPatch
{
	[HarmonyPostfix]
	public static void Postfix(Faction faction)
	{
		if (ForcedIdeoGameComponent.AnyIdeologyEditsActive)
		{
			ForcedIdeoGameComponent.Current?.EnsurePrimaryIdeo(faction);
		}
	}
}
