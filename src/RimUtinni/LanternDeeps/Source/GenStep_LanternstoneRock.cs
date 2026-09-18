using System.Linq;
using RimWorld;
using Verse;
using Verse.Noise;

namespace RimMandrake.Utinni.LanternDeeps
{
	// CAVERNS_PARITY_BUILD_1 — makes lanternstone one of the Deep's natural rocks.
	//
	// Why this exists (MEASURED from World.cs 2026-09-18): rock types for a map come
	// from World.NaturalRockTypesIn(tile), and RockAllowedInBiome() returns FALSE for
	// every `biomeSpecific` rock when the tile is invalid — which a pocket map's
	// always is. forceRockTypes is likewise only read for a valid tile. So a pocket
	// map's BiomeDef.extraRockTypes is dead data: the Deep was generating as marble
	// and granite with zero lanternstone, however the biome was written.
	//
	// The fix rides the engine's own mechanism instead of fighting it.
	// MapGenerator.GenerateContentsIntoMap calls RockNoises.Init(map) ONCE before
	// any GenStep, and RockNoises.rockNoises is a public static list nothing else
	// mutates. This step runs at order 190 — before Underground_RocksFromGrid (200)
	// — and appends a noise for the lanternstone wall. From there RockDefAt, the
	// Terrain step (naturalTerrain), RockChunks, deep drilling and every other
	// consumer see lanternstone exactly as they would on a surface tile whose biome
	// listed it in extraRockTypes: one rock among the two or three the map rolled.
	//
	// ⚠️ Deep maps only, by the same biome gate as GenStep_ScatterLanternstone —
	// this step would otherwise put lanternstone into any map whose generator
	// listed it.
	public class GenStep_LanternstoneRock : GenStep
	{
		private const string DeepBiomeDefName = "RUT_LanternDeeps";
		private const string RockDefName = "RUT_LanternstoneWall";

		public override int SeedPart => 1237834912;

		public override void Generate(Map map, GenStepParams parms)
		{
			if (map.Biome == null || map.Biome.defName != DeepBiomeDefName)
			{
				return;
			}
			ThingDef rock = DefDatabase<ThingDef>.GetNamedSilentFail(RockDefName);
			if (rock == null)
			{
				Log.Error("[LanternDeeps] " + RockDefName + " is not loaded; the Deep will have no lanternstone rock.");
				return;
			}
			if (RockNoises.rockNoises == null)
			{
				Log.Error("[LanternDeeps] RockNoises not initialised before GenStep_LanternstoneRock; is this step ordered before Underground_RocksFromGrid?");
				return;
			}
			if (RockNoises.rockNoises.Any(n => n.rockDef == rock))
			{
				return;
			}
			RockNoises.rockNoises.Add(new RockNoises.RockNoise
			{
				rockDef = rock,
				// Same parameters RockNoises.Init uses for every other rock, so the
				// lanternstone lobes are the same scale as the marble ones.
				noise = new Perlin(0.004999999888241291, 2.0, 0.5, 6, Rand.Range(0, int.MaxValue), QualityMode.Medium)
			});
		}
	}
}
