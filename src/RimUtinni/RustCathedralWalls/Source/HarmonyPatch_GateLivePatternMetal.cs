using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.RustCathedralWalls
{
	// RUST_CATHEDRAL_MECHANICS_1 §2, Tier 4. See RUT_LivePatternMetal.xml's
	// own header for the full "why a Harmony patch was unavoidable here"
	// reasoning: vanilla's deep-resource pick (CompDeepScanner.
	// ChooseLumpThingDef, RimWorld/CompDeepScanner.cs) is a flat, GLOBAL
	// weighted-random pool over every ThingDef with deepCommonality set —
	// there is no biome or per-map filter anywhere in that call chain, and
	// this repo's existing biome-exclusive deep resources (Kyber, Pyrinth)
	// solve the equivalent leak by riding a dedicated pocket-map generator,
	// which an ordinary overworld biome like the Rust Cathedral does not
	// have. A postfix on the one method that makes the pick is the
	// smallest fix that actually restricts it.
	[StaticConstructorOnStartup]
	public static class RustCathedralWallsMod
	{
		static RustCathedralWallsMod()
		{
			new Harmony("mandrake.rut.rustcathedralwalls").PatchAll();
		}
	}

	[HarmonyPatch(typeof(CompDeepScanner), "ChooseLumpThingDef")]
	public static class HarmonyPatch_GateLivePatternMetal
	{
		private const string LivePatternMetalDefName = "RUT_LivePatternMetal";

		private const string CathedralBiomeDefName = "RUT_RustCathedral";

		public static void Postfix(CompDeepScanner __instance, ref ThingDef __result)
		{
			if (__result == null || __result.defName != LivePatternMetalDefName)
			{
				return;
			}
			Map map = __instance?.parent?.Map;
			if (map != null && map.Biome != null && map.Biome.defName == CathedralBiomeDefName)
			{
				return;
			}
			// Off the Cathedral, substitute the closest vanilla equivalent
			// rather than re-rolling the whole weighted pool — a single
			// substitution is enough to close the leak and keeps this patch
			// to one small, auditable branch.
			ThingDef fallback = ThingDefOf.Steel;
			if (fallback != null)
			{
				__result = fallback;
			}
		}
	}
}
