using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FeverWood
{
	// FEVERWOOD_RM_MOD_BUILD_1 step 3: the def's own workerClass may not assume a donor type (the twin shipped
	// ReGrowthCore.UniversalBiomeWorker, a dependency the RimMandrake tier does not lean on), so the class has to exist and
	// resolve for RM_FeverWood (and Utinni's RUT_FeverWood) to load at all.
	//
	// It never places the biome. The Fever Wood is hand-placed on the one fixed world (generatesNaturally=false; the owner,
	// 2026-08-15: there is no worldgen feature, in any version), so the temperature/rainfall scoring body it used to carry
	// could never run and was CUT 2026-10-23 (design/RimMandrake/fluff_cuts_2026-10-23.md). A score below zero never wins.
	public class RM_BiomeWorker_FeverWood : BiomeWorker
	{
		public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
		{
			return -100f;
		}
	}
}
