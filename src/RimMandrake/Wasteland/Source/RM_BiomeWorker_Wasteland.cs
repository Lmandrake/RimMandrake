using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Wasteland
{
	// BIOME PLACEMENT — mirrors RM_BiomeWorker_Greentide/RM_BiomeWorker_TheRot
	// (src/RimMandrake/Greentide/Source/RM_BiomeWorker_Greentide.cs,
	// src/RimMandrake/TheRot/Source/RM_BiomeWorker_TheRot.cs) exactly. BiomeDef
	// has no temperature/rainfall/elevation field; RimWorld scores every
	// BiomeDef's workerClass per tile and keeps the highest. RM_Wasteland ships
	// with generatesNaturally=false (matching its frozen campaign twin,
	// RUT_Wasteland.xml — "one def... vary only by mutators and Inhabited
	// injections, never by BiomeDef"), so this worker is currently inert for
	// ordinary worldgen; it exists so workerClass resolves to a real type (an
	// unresolvable class is a hard load error regardless of generatesNaturally)
	// and so a future toggle to enable natural generation has real scoring
	// logic to lean on, rather than nothing.
	//
	// Ranges sourced from design/Jawa/worldbuilding/biomes/wasteland.md §0's
	// own measured per-family table (dayside basins +10..+27C, the margin
	// -9..-1C, the dark scour -13..-35C — the whole biome spans roughly
	// -35..+27C) and its own "bone-dry" description (near-zero rainfall).
	// Scored against vanilla BiomeWorker_Desert/_ExtremeDesert, which own the
	// hot-dry corridor today; returns 0 outside its own band so it never
	// fights a vanilla biome anywhere it doesn't belong.
	//
	// TRIGGERED BY: <modExtensions><li Class="...RM_WastelandBiomeRanges"> on
	// the RM_Wasteland BiomeDef.
	public class RM_WastelandBiomeRanges : DefModExtension
	{
		public FloatRange temperature = new FloatRange(-35f, 30f);
		public FloatRange rainfall = new FloatRange(0f, 500f);
		public FloatRange elevation = new FloatRange(0f, 600f);
		public float baseScore = 28f;
		public float degreeWeight = 1.0f;
		public float rainfallDivisor = 150f;
	}

	public class RM_BiomeWorker_Wasteland : BiomeWorker
	{
		private static readonly RM_WastelandBiomeRanges FallbackRanges = new RM_WastelandBiomeRanges();

		public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
		{
			if (tile == null || tile.WaterCovered)
			{
				return -100f;
			}

			RM_WastelandBiomeRanges r = biome.GetModExtension<RM_WastelandBiomeRanges>() ?? FallbackRanges;

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
				 + (r.rainfall.max - tile.rainfall) / divisor
				 + (r.temperature.max - tile.temperature) * r.degreeWeight * 0.05f;
		}
	}
}
