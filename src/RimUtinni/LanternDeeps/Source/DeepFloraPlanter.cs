using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
	// CAVERNS_PARITY_BUILD_1 — the one chooser behind both flora routes in a
	// Lantern Deep: GenStep_DeepFloraGate (initial planting at map gen) and
	// MapComponent_DeepFloraRegrowth (slow regrowth during play).
	//
	// WHY THIS EXISTS (MEASURED, RimWorld 1.6 decompiled source 2026-09-18):
	// WildPlantSpawner.CheckSpawnWildPlantAt computes
	//     cavePlants = c.GetRoof(map)?.isNatural ?? false
	// and when that is true CalculatePlantsWhichCanGrowAt draws ONLY from the
	// static `allCavePlants` list (every def with plant.cavePlant &&
	// cavePlantWeight > 0, planet-wide) — the biome's wildPlants are never
	// consulted. A Deep is a pocket map entirely under natural rock roof, so
	// vanilla's Plants GenStep and its regrowth tick both ignore
	// RUT_LanternDeeps.wildPlants completely. Flagging our defs cavePlant would
	// leak them into every roofed cave on the planet (the donor's own reason for
	// cavePlantWeight 0), so instead we choose from the biome's list ourselves.
	//
	// What is deliberately vanilla here: the per-cell desired count
	// (WildPlantSpawner.GetDesiredPlantsCountAt — plantDensity * fertility with
	// the 0.5 natural-roof factor), the whole-map desired total
	// (WildPlantSpawner.CurrentWholeMapNumDesiredPlants), plantability
	// (PlantUtility.CanEverPlantAt — fertilityMin, wildTerrainTags, blockers), the
	// distance-to-shore roll for water plants, and WildPlantSpawner.SpawnPlant
	// with its InitialGrowthRandomRange. What is NOT replicated: wildOrder
	// lower-order gating and wildCluster nucleation — the chooser is a flat
	// commonality-weighted pick among the plants that can grow at the cell.
	public static class DeepFloraPlanter
	{
		public const string DeepBiomeDefName = "RUT_LanternDeeps";

		private static readonly List<KeyValuePair<ThingDef, float>> tmpCandidates =
			new List<KeyValuePair<ThingDef, float>>();

		public static bool IsDeep(Map map)
		{
			return map != null && map.Biome != null && map.Biome.defName == DeepBiomeDefName;
		}

		// Vanilla's own whole-map target. WildPlantSpawner.cs:
		//   foreach (IntVec3 item in cellRect) num += GetDesiredPlantsCountAt(item, currentPlantDensityFactor);
		// where GetDesiredPlantsCountAt = min(baseDesired(c) * biome.plantDensity * densityFactor * fertility, 1)
		// and baseDesired halves under a natural roof. Whole-map walk — call
		// rarely (once at gen, ~daily in play), never per tick.
		public static float DesiredWholeMapCount(Map map)
		{
			return map.wildPlantSpawner.CurrentWholeMapNumDesiredPlants;
		}

		public static int CurrentPlantCount(Map map)
		{
			return map.listerThings.ThingsInGroup(ThingRequestGroup.Plant).Count;
		}

		// Cheap pre-filter mirroring the head of CheckSpawnWildPlantAt. Water is
		// let through because the biome's hydrophytes (VellokReed, KuvraSpout,
		// NurrikGill) are completelyIgnoreFertility + wildTerrainTags plants;
		// CanEverPlantAt is what actually decides for them.
		public static bool CellIsOpen(Map map, IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			if (c.GetPlant(map) != null || c.GetCover(map) != null || c.GetEdifice(map) != null)
			{
				return false;
			}
			if (map.fertilityGrid.FertilityAt(c) <= 0f && !c.GetTerrain(map).IsWater)
			{
				return false;
			}
			if (!PlantUtility.SnowAllowsPlanting(c, map) || !PlantUtility.SandAllowsPlanting(c, map))
			{
				return false;
			}
			return true;
		}

		// One attempt at one cell. Returns true only when a plant was spawned.
		// Uses whatever Rand state is current: MapGenerator's pushed seed during
		// a GenStep, the game's during play.
		public static bool TryPlantAt(Map map, IntVec3 c, bool setRandomGrowth)
		{
			if (!CellIsOpen(map, c))
			{
				return false;
			}
			List<BiomePlantRecord> records = map.Biome.wildPlants;
			if (records == null || records.Count == 0)
			{
				return false;
			}

			tmpCandidates.Clear();
			for (int i = 0; i < records.Count; i++)
			{
				BiomePlantRecord rec = records[i];
				ThingDef def = rec.plant;
				if (def == null || rec.commonality <= 0f || def.plant == null || def.IsDeadPlant)
				{
					continue;
				}
				// checkMapTemperature: false — a Deep is a fixed-temperature pocket
				// (pocketMapProperties.temperature 17) and its PlanetTile is not a
				// surface tile; the surface min/max the check reads is not this
				// cavern's climate.
				if (!def.CanEverPlantAt(c, map, canWipePlantsExceptTree: false, checkMapTemperature: false))
				{
					continue;
				}
				tmpCandidates.Add(new KeyValuePair<ThingDef, float>(def, rec.commonality));
			}
			if (tmpCandidates.Count == 0)
			{
				return false;
			}
			if (!tmpCandidates.TryRandomElementByWeight(x => x.Value, out KeyValuePair<ThingDef, float> pick))
			{
				return false;
			}
			ThingDef chosen = pick.Key;
			// Same shore roll vanilla applies to water plants (CheckSpawnWildPlantAt).
			if (chosen.plant.wildPlantUseDistanceToShore
				&& !Rand.Chance(map.wildPlantSpawner.GetWaterPlantDistanceToShoreWeight(c)))
			{
				return false;
			}
			WildPlantSpawner.SpawnPlant(chosen, map, c, setRandomGrowth);
			return true;
		}

		// Initial fill at map gen. Every open cell is rolled once at vanilla's own
		// per-cell desired count (fertility- and roof-weighted), in a Rand-shuffled
		// order so a whole-map cap lands evenly rather than in raster order.
		// Returns the number of plants spawned.
		public static int PlantInitial(Map map)
		{
			WildPlantSpawner spawner = map.wildPlantSpawner;
			float densityFactor = spawner.CurrentPlantDensityFactor;
			if (densityFactor <= 0f)
			{
				return 0;
			}
			float desiredTotal = spawner.CurrentWholeMapNumDesiredPlants;
			int have = CurrentPlantCount(map);
			if (desiredTotal <= 0f || have >= desiredTotal)
			{
				return 0;
			}

			List<IntVec3> cells = new List<IntVec3>(map.Area);
			foreach (IntVec3 c in map.AllCells)
			{
				if (CellIsOpen(map, c))
				{
					cells.Add(c);
				}
			}
			cells.Shuffle();

			int spawned = 0;
			for (int i = 0; i < cells.Count; i++)
			{
				if (have + spawned >= desiredTotal)
				{
					break;
				}
				IntVec3 c = cells[i];
				float chance = spawner.GetDesiredPlantsCountAt(c, densityFactor);
				if (chance <= 0f || !Rand.Chance(chance))
				{
					continue;
				}
				if (TryPlantAt(map, c, setRandomGrowth: true))
				{
					spawned++;
				}
			}
			return spawned;
		}
	}
}
