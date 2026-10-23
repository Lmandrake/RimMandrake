using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.DeepDrill
{
	// DEEP_DRILL_HOME_BIOME_1. CompDeepScanner.ChooseLumpThingDef is a flat weighted pick with no biome filter, so a drill anywhere could strike
	// any donor mineral. Off a deposit's home biome (RM_DeepHomeTable) the pick becomes steel, the planet-wide deep resource.
	[HarmonyPatch(typeof(CompDeepScanner), "ChooseLumpThingDef")]
	[RimMandrake.Shared.PatchFeature("Deep deposits follow the biome", typeof(RM_DeepDrillSettings), "homeFilterEnabled")]
	public static class Patch_DeepHome
	{
		private static Dictionary<string, HashSet<string>> table;

		public static Dictionary<string, HashSet<string>> Table =>
			table ?? (table = RM_DeepHomeDef.Merge(DefDatabase<RM_DeepHomeDef>.AllDefsListForReading));

		public static void Postfix(CompDeepScanner __instance, ref ThingDef __result)
		{
			if (__result == null) return;
			string biome = __instance?.parent?.Map?.Biome?.defName;
			if (RM_DeepDrillKernel.ShouldReplace(RM_DeepDrillSettings.homeFilterEnabled, __result.defName, biome, Table) && ThingDefOf.Steel != null)
				__result = ThingDefOf.Steel;
		}
	}
}
