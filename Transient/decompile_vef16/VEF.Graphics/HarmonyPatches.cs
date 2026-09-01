using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Graphics;

[HarmonyPatch]
public static class HarmonyPatches
{
	[HarmonyPatch(typeof(FactionGenerator), "NewGeneratedFaction")]
	public static void NewGeneratedFactionPostfix(ref Faction __result, FactionGeneratorParms parms)
	{
		foreach (TaggedDefProperties modExtension in ((Def)(object)__result.def).GetModExtensions<TaggedDefProperties>())
		{
			modExtension.GenerateTags(__result);
		}
	}
}
