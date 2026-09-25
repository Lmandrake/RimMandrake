using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.FeverWood
{
	// FEVERWOOD_RM_MOD_BUILD_1 step 3 — the def's own workerClass may not
	// assume a donor type (the twin shipped ReGrowthCore.UniversalBiomeWorker,
	// a hard dependency the RimMandrake tier does not get to lean on). Same
	// shape as the sibling RM_BiomeWorker_Greentide
	// (src/RimMandrake/Greentide/Source/RM_BiomeWorker_Greentide.cs): a plain
	// temperature/rainfall/elevation score band, hardcoded rather than a
	// separate DefModExtension since nothing else needs to override it.
	//
	// generatesNaturally is false on RM_FeverWood (carried over unchanged
	// from the twin — this is a campaign-placed biome, not a worldgen-scored
	// one), so RimWorld's own BiomeDef placement scan never actually calls
	// GetScore here today. The class still has to exist and resolve for the
	// def to load at all, and a real scoring body (rather than a stub) means
	// the biome is not accidentally broken for a future generatesNaturally=true
	// flip on someone else's world.
	//
	// Ranges are INVENTED, calibrated off the item's own MEASURED sheet data
	// for the live Fever Wood tiles (FEVERWOOD_RM_MOD_BUILD_1's "The def
	// today": sun median +43 deg, temp median 45.5 C, flat lowland at ~22 m) —
	// a hot, low, humid band, not re-derived from any donor biome's own score
	// band.
	public class RM_BiomeWorker_FeverWood : BiomeWorker
	{
		private static readonly FloatRange TemperatureRange = new FloatRange(30f, 65f);
		private static readonly FloatRange RainfallRange = new FloatRange(1800f, 5500f);
		private static readonly FloatRange ElevationRange = new FloatRange(0f, 400f);
		private const float BaseScore = 25f;
		private const float DegreeWeight = 1.2f;
		private const float RainfallDivisor = 220f;

		public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
		{
			if (!RM_FeverWoodSettings.naturalPlacementEnabled)
			{
				return 0f;
			}
			if (tile == null || tile.WaterCovered)
			{
				return -100f;
			}
			if (tile.temperature < TemperatureRange.min || tile.temperature > TemperatureRange.max)
			{
				return 0f;
			}
			if (tile.rainfall < RainfallRange.min || tile.rainfall >= RainfallRange.max)
			{
				return 0f;
			}
			if (tile.elevation < ElevationRange.min || tile.elevation > ElevationRange.max)
			{
				return 0f;
			}
			if (tile.hilliness == Hilliness.Mountainous || tile.hilliness == Hilliness.Impassable)
			{
				return 0f;
			}

			return BaseScore
				 + (tile.temperature - TemperatureRange.min) * DegreeWeight
				 + (tile.rainfall - RainfallRange.min) / RainfallDivisor;
		}
	}
}
