using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.TheRot
{
	// BIOME PLACEMENT — mirrors RM_BiomeWorker_Greentide
	// (src/RimMandrake/Greentide/Source/RM_BiomeWorker_Greentide.cs) exactly.
	// BiomeDef has no temperature/rainfall/elevation field; RimWorld scores
	// every BiomeDef's workerClass per tile and keeps the highest. This is what
	// lets RM_TheRot generate naturally on OTHER players' worlds — it does not
	// touch this repo's own frozen, hand-authored campaign world (CLAUDE.md "no
	// worldgen feature" is about that world specifically; this mod ships for
	// everyone else's generated planets).
	//
	// The Rot's own header (RUT_TheRot.xml) measures the live campaign tiles at
	// arc 74-135 (night side of the stormwall) with temp p10/median/p90
	// -35.5/-18.8/+12.9 C — a COLD, low-light band, the opposite end of the
	// spectrum from Greentide's hot/very-wet corridor. Scored against vanilla
	// BiomeWorker_IceSheet/_Tundra, which own the cold end today; returns 0
	// outside its own band so it never fights a vanilla biome anywhere it
	// doesn't belong.
	//
	// TRIGGERED BY: <modExtensions><li Class="...RM_TheRotBiomeRanges"> on the
	// RM_TheRot BiomeDef.
	public class RM_TheRotBiomeRanges : DefModExtension
	{
		public FloatRange temperature = new FloatRange(-40f, 15f);
		public FloatRange rainfall = new FloatRange(0f, 1600f);
		public FloatRange elevation = new FloatRange(0f, 1200f);
		public float baseScore = 30f;
		public float degreeWeight = 1.2f;
		public float rainfallDivisor = 220f;
	}

	public class RM_BiomeWorker_TheRot : BiomeWorker
	{
		private static readonly RM_TheRotBiomeRanges FallbackRanges = new RM_TheRotBiomeRanges();

		public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
		{
			if (tile == null || tile.WaterCovered)
			{
				return -100f;
			}

			RM_TheRotBiomeRanges r = biome.GetModExtension<RM_TheRotBiomeRanges>() ?? FallbackRanges;

			if (tile.temperature < r.temperature.min || tile.temperature > r.temperature.max)
			{
				return 0f;
			}
			if (tile.rainfall < r.rainfall.min || tile.rainfall >= r.rainfall.max)
			{
				return 0f;
			}
			if (tile.elevation < r.elevation.min || tile.elevation > r.elevation.max)
			{
				return 0f;
			}
			if (tile.hilliness == Hilliness.Impassable)
			{
				return 0f;
			}

			float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
			return r.baseScore
				 + (r.temperature.max - tile.temperature) * r.degreeWeight
				 + (r.rainfall.max - tile.rainfall) / divisor;
		}
	}
}
