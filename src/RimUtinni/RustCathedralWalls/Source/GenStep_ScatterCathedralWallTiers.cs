using RimWorld;
using Verse;

namespace RimMandrake.Utinni.RustCathedralWalls
{
	// RUST_CATHEDRAL_MECHANICS_1 §2, Tiers 1-2. Pattern copied from
	// src/RimUtinni/FungalSoilTrade/Source/GenStep_ScatterFungalGround.cs /
	// src/RimUtinni/LanternDeeps/Source/GenStep_ScatterCavePortal.cs: a plain
	// GenStep_ScatterGroup subclass, self-gated by map.Biome.defName —
	// "GenStepDef has no biome field and vanilla ships no
	// ScattererValidator_Biome" (LanternDeeps' own header, confirmed absent
	// again for this build). Discovered by RimWorld's own GenStepDef the
	// moment the XML names it in genStep Class - no Harmony, no
	// registration call needed for the scatter itself.
	public class GenStep_ScatterCathedralWallTiers : GenStep_ScatterGroup
	{
		public const string CathedralBiomeDefName = "RUT_RustCathedral";

		public override void Generate(Map map, GenStepParams parms)
		{
			if (!RustCathedralWallsSettings.wallTiersEnabled)
			{
				return;
			}
			if (map.Biome == null || map.Biome.defName != CathedralBiomeDefName)
			{
				return;
			}
			base.Generate(map, parms);
		}
	}
}
