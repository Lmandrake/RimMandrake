using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Greentide
{
	// BIOME PLACEMENT — mirrors the sibling BiomeWorker_Pyrelands pattern
	// exactly (src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs). BiomeDef has
	// no temperature/rainfall/elevation field; RimWorld scores every BiomeDef's
	// workerClass per tile and keeps the highest. This worker is what lets
	// RM_Greentide generate naturally on OTHER players' worlds — it does not
	// touch this repo's own frozen, hand-authored campaign world (CLAUDE.md
	// "no worldgen feature" is about that world specifically; this mod ships
	// for everyone else's generated planets, same reconciliation the sibling
	// GelatinousSlime mod's own worker comment already states).
	//
	// TRIGGERED BY: <modExtensions><li Class="...RM_GreentideBiomeRanges"> on
	// the RM_Greentide BiomeDef.
	public class RM_GreentideBiomeRanges : DefModExtension
	{
		public FloatRange temperature = new FloatRange(28f, 60f);
		public FloatRange rainfall = new FloatRange(2200f, 6000f);
		public FloatRange elevation = new FloatRange(0f, 1200f);
		public float baseScore = 30f;
		public float degreeWeight = 1.4f;
		public float rainfallDivisor = 220f;
	}

	// Scored against vanilla BiomeWorker_TropicalRainforest, which owns the
	// hot/very-wet corridor today. Competes only inside the modExtension's
	// band above; returns 0 outside it so it never fights vanilla biomes
	// anywhere it doesn't belong.
	public class RM_BiomeWorker_Greentide : BiomeWorker
	{
		private static readonly RM_GreentideBiomeRanges FallbackRanges = new RM_GreentideBiomeRanges();

		public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
		{
			if (tile == null || tile.WaterCovered)
			{
				return -100f;
			}

			RM_GreentideBiomeRanges r = biome.GetModExtension<RM_GreentideBiomeRanges>() ?? FallbackRanges;

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
			if (tile.hilliness == Hilliness.Mountainous || tile.hilliness == Hilliness.Impassable)
			{
				return 0f;
			}

			float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
			return r.baseScore
				 + (tile.temperature - r.temperature.min) * r.degreeWeight
				 + (tile.rainfall - r.rainfall.min) / divisor;
		}
	}
}
