using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Webwork
{
	// BIOME PLACEMENT — mirrors the sibling BiomeWorker_Greentide/Pyrelands
	// pattern exactly (src/RimMandrake/Greentide/Source/RM_BiomeWorker_Greentide.cs).
	// BiomeDef has no temperature/rainfall/elevation field; RimWorld scores
	// every BiomeDef's workerClass per tile and keeps the highest. This worker
	// is what lets RM_Webwork generate naturally on OTHER players' worlds — it
	// does not touch this repo's own frozen, hand-authored campaign world
	// (CLAUDE.md "no worldgen feature" is about that world specifically; this
	// mod ships for everyone else's generated planets).
	//
	// The frozen twin's own donor workerClass
	// (AlphaBiomes.BiomeWorker_FeraliskInfestedJungle) is a hard third-party
	// dependency this RM-tier mod may not assume — reimplemented generically
	// against a hot, very wet, low-elevation jungle band instead (its measured
	// live tile stats: sun median +51 deg, temp p10/median/p90 38.6/49.2/58.2
	// C, per RUT_Webwork.xml's own header). Competes only inside that band;
	// returns 0 (or a hard -100 on water) everywhere else so it never fights
	// vanilla biomes anywhere it doesn't belong.
	public class RM_BiomeWorker_Webwork : BiomeWorker
	{
		public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
		{
			if (!RM_WebworkSettings.generateOnWorldgen)
			{
				return 0f;
			}
			if (tile == null)
			{
				return -100f;
			}
			return RM_WebworkBiomeKernel.Score(true, false, tile.WaterCovered, tile.temperature, tile.rainfall, tile.elevation,
				tile.hilliness == Hilliness.Mountainous || tile.hilliness == Hilliness.Impassable);
		}
	}
}
