using HarmonyLib;
using VEF.Things;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(DeepResourceGrid))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_DeepResourceGrid_DeepResourcesOnGUI
{
	public static void Postfix(DeepResourceGrid __instance, CellBoolDrawer ___drawer, Map ___map)
	{
		if (___map != Find.CurrentMap)
		{
			return;
		}
		Thing singleSelectedThing = Find.Selector.SingleSelectedThing;
		if (singleSelectedThing != null && singleSelectedThing.Map == ___map)
		{
			ThingDefExtension modExtension = ((Def)singleSelectedThing.def).GetModExtension<ThingDefExtension>();
			if (modExtension != null && modExtension.deepResourcesOnGUI && (!modExtension.deepResourcesOnGUIRequireScanner || __instance.AnyActiveDeepScannersOnMap()))
			{
				___drawer.MarkForDraw();
				NonPublicMethods.RenderMouseAttachments(__instance);
			}
		}
	}
}
