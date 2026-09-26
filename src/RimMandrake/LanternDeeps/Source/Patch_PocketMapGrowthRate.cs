using System.Reflection;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.LanternDeeps
{
	// CAVERNS_PARITY_BUILD_1 — the Deep pocket map could never finish generating.
	//
	// MEASURED on the first live quicktest (2026-09-18, Player.log ref E6BB2EFD):
	// Map.FinalizeInit -> MapPlantGrowthRateCalculator.BuildFor(Map) ->
	// SimulateGrowthRateForDay -> TileTemperaturesComp.OutdoorTemperatureAt(tile)
	// throws IndexOutOfRange, because a pocket map's parent (PocketMapParent) never
	// gets a tile — MapInfo.Tile is PlanetTile.Invalid — and the calculator
	// simulates a year of outdoor temperatures for every wild plant that pasture
	// animals can eat (ComputeIfDirty: biome.AllWildPlants.Where(IsEdibleByPasture
	// Animals)). Vanilla's own Undercave survives only because its biome lists no
	// wild plants; any pocket-map biome with grazable flora — ours, and the donor's
	// before it — dies here, and the map is left half-initialised (waterBodyTracker
	// and mapDrawer null), which is the per-frame NRE storm the log then fills with.
	//
	// The prefix substitutes the SOURCE map's tile — the surface the entrance stands
	// on — so the calculator has real climate data to simulate against. It is only
	// ever consulted for pen-animal grazing estimates, and the Deep's real
	// temperature still comes from pocketMapProperties (MapTemperature checks
	// IsPocketMap first). Scoped to pocket maps whose parent has no valid tile; a
	// normal map is untouched.
	[StaticConstructorOnStartup]
	public static class LanternDeepsHarmony
	{
		public const string HarmonyId = "mandrake.rm.lanterndeeps";

		static LanternDeepsHarmony()
		{
			Harmony harmony = new Harmony(HarmonyId);
			harmony.PatchAll(Assembly.GetExecutingAssembly());
		}
	}

	[HarmonyPatch(typeof(MapPlantGrowthRateCalculator), nameof(MapPlantGrowthRateCalculator.BuildFor), new[] { typeof(Map) })]
	public static class Patch_MapPlantGrowthRateCalculator_BuildFor
	{
		public static bool Prefix(MapPlantGrowthRateCalculator __instance, Map map)
		{
			if (map == null || !map.IsPocketMap || map.Tile.Valid)
			{
				return true;
			}
			Map source = map.PocketMapParent?.sourceMap;
			if (source == null || !source.Tile.Valid)
			{
				// Nothing sane to simulate against; leave the calculator empty
				// rather than let FinalizeInit throw. Grazing estimates read as
				// zero on this map, which is the honest answer.
				return false;
			}
			__instance.BuildFor(source.Tile);
			return false;
		}
	}
}
