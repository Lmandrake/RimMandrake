using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.LanternDeeps
{
	// MINERAL_BIOME_LEAKS_1. CompDeepScanner.ChooseLumpThingDef is a flat global weighted pick over every
	// ThingDef with deepCommonality set, so lanternstone (deepCommonality 1) turned up under a drill on any
	// map. Same shape and same substitute as RustCathedral's HarmonyPatch_GateLivePatternMetal: off the Deeps
	// the pick becomes steel, which is the planet-wide deep resource.
	[HarmonyPatch(typeof(CompDeepScanner), "ChooseLumpThingDef")]
	public static class Patch_GateLanternstoneDeep
	{
		public const string HomeBiomeDefName = "RM_LanternDeeps";

		public static bool IsLanternstone(ThingDef def)
		{
			return def != null && (def.defName == "RM_Lanternstone");
		}

		public static void Postfix(CompDeepScanner __instance, ref ThingDef __result)
		{
			if (!LanternDeepsSettings.lanternstoneDeepGateEnabled || !IsLanternstone(__result))
			{
				return;
			}
			Map map = __instance?.parent?.Map;
			if (map != null && map.Biome != null && map.Biome.defName == HomeBiomeDefName)
			{
				return;
			}
			if (ThingDefOf.Steel != null)
			{
				__result = ThingDefOf.Steel;
			}
		}
	}
}
