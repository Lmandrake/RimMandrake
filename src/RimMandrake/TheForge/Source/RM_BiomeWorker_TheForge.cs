using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.TheForge
{
	// BIOME PLACEMENT — mirrors RM_BiomeWorker_TheRot
	// (src/RimMandrake/TheRot/Source/RM_BiomeWorker_TheRot.cs) exactly.
	// BiomeDef has no temperature/rainfall/elevation field; RimWorld scores
	// every BiomeDef's workerClass per tile and keeps the highest. This is what
	// lets RM_TheForge generate naturally on OTHER players' worlds — it does
	// not touch this repo's own frozen, hand-authored campaign world (CLAUDE.md
	// "no worldgen feature" is about that world specifically; this mod ships
	// for everyone else's generated planets).
	//
	// The frozen twin's own header (RUT_TheForge.xml, the_forge.md §0) measures
	// the live campaign massif at temps 42-56 C and elevation median 1,382-2,010 m
	// (max 2,266 m across all three zones) — a narrow HOT, HIGH, seismically
	// active band. allowRivers is false on the twin (ban 6: "no ordinary rain"),
	// so the rainfall band here is kept low/dry rather than copying a wetter
	// biome's range. Scored against vanilla's own arid/mountain workers, which
	// do not carve out this narrow a temperature ceiling; returns 0 outside its
	// own band so it never fights a vanilla biome anywhere it doesn't belong.
	//
	// TRIGGERED BY: <modExtensions><li Class="...RM_TheForgeBiomeRanges"> on the
	// RM_TheForge BiomeDef.
	public class RM_TheForgeBiomeRanges : DefModExtension
	{
		public FloatRange temperature = new FloatRange(38f, 65f);
		public FloatRange rainfall = new FloatRange(0f, 200f);
		public FloatRange elevation = new FloatRange(1100f, 2400f);
		public float baseScore = 34f;
		public float degreeWeight = 1.0f;
		public float rainfallDivisor = 150f;
	}

	public class RM_BiomeWorker_TheForge : BiomeWorker
	{
		private static readonly RM_TheForgeBiomeRanges FallbackRanges = new RM_TheForgeBiomeRanges();

		public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
		{
			if (tile == null || tile.WaterCovered)
			{
				return -100f;
			}

			RM_TheForgeBiomeRanges r = biome.GetModExtension<RM_TheForgeBiomeRanges>() ?? FallbackRanges;

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

			float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
			return r.baseScore
				 + (tile.temperature - r.temperature.min) * r.degreeWeight
				 + (r.elevation.max - tile.elevation) / divisor;
		}
	}
}
