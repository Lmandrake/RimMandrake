using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_WHALE_FILTERFEED_1. The other half of the megafauna's
	/// ecology — desert.md §4c: "They leave massive dung at shade patches, and
	/// that dung immediately seeds young plants and young creatures around it.
	/// So the megafauna are the biome's circulatory system — the only
	/// long-distance vector, carrying seeds, riders and parasites between
	/// patch-networks that are otherwise sealed from each other, and fertilising
	/// every harbour they stop at."
	///
	/// One periodic event, three effects, all gated on where the carrier is
	/// STANDING when it fires:
	///
	///   1. DUNG — filth at the carrier's cell, always, shade or no shade. A
	///      body in the open still voids; that is just not where it matters.
	///   2. FERTILISE — every plant within seedRadius gains growthBoost, but
	///      only when RM_MapComponent_ShadeGrid.ShadeAt clears minShadeToSeed.
	///   3. SEED — young plants, and at wildlifeSpawnChance a young creature,
	///      placed in the same radius under the same shade gate.
	///
	/// 🔑 The shade gate is the mechanic, not a flavour condition on it. "Leaves
	/// massive dung AT SHADE PATCHES" is what makes the megafauna a vector
	/// between harbours rather than a fertiliser spreader over open sand, so a
	/// dung event in the sun is deliberately a no-op beyond the filth. Shade is
	/// read from RM_MapComponent_ShadeGrid — the one keystone grid every
	/// consumer in this assembly reads (DESERT_SHADE_GRID_KEYSTONE_1); nothing
	/// here re-derives its own version, and a map with no grid degrades to
	/// "dung, no seeding" rather than to a guessed shade value.
	///
	/// Not vanilla CompSpawnerPawn or CompSpawnSubplant: the first always builds
	/// a Lord for its spawns (the same reason this assembly's own
	/// RM_CompVerminBreeder exists), and the second spawns one fixed subplant off
	/// a plant's own growth with no notion of shade, radius weighting, or fauna.
	/// </summary>
	public class RM_CompDungSeeder : ThingComp
	{
		private int nextDungTick = -1;

		/// <summary>
		/// Biome fallback rosters, resolved once per biome and shared across every
		/// carrier on every map. Keyed by BiomeDef because that is what decides
		/// the answer; DefDatabase is immutable after load, so this never goes
		/// stale within a session.
		/// </summary>
		private static readonly Dictionary<BiomeDef, List<PawnKindDef>> cachedBiomeWildlife
			= new Dictionary<BiomeDef, List<PawnKindDef>>();

		private RM_CompProperties_DungSeeder Props => (RM_CompProperties_DungSeeder)props;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (nextDungTick < 0)
			{
				ScheduleNext();
			}
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref nextDungTick, "nextDungTick", -1);
		}

		public override void CompTick()
		{
			base.CompTick();

			if (!RM_CreatureBehaviorsSettings.dungSeedingEnabled)
			{
				return; // mod option: the carrier still voids like any animal, it just fertilises nothing
			}

			if (!parent.Spawned || parent.Map == null)
			{
				return;
			}

			if (parent is Pawn pawn && pawn.Dead)
			{
				return;
			}

			if (Find.TickManager.TicksGame < nextDungTick)
			{
				return;
			}

			DoDungEvent();
			ScheduleNext();
		}

		private void ScheduleNext()
		{
			int interval = Mathf.Max(1, Props.intervalTicksRange.RandomInRange);
			nextDungTick = Find.TickManager.TicksGame + interval;
		}

		private void DoDungEvent()
		{
			Map map = parent.Map;
			IntVec3 center = parent.Position;

			if (Props.dungFilthDef != null && Props.dungFilthCount > 0 && center.InBounds(map))
			{
				FilthMaker.TryMakeFilth(center, map, Props.dungFilthDef, Props.dungFilthCount);
			}

			RM_MapComponent_ShadeGrid grid = map.GetComponent<RM_MapComponent_ShadeGrid>();
			if (grid == null || grid.ShadeAt(center) < Props.minShadeToSeed)
			{
				return; // dropped in the open (or on a map with no shade grid) — nothing takes
			}

			FertiliseNearbyPlants(map, center);
			SeedYoungPlants(map, center);
			SeedYoungCreature(map, center);
		}

		private void FertiliseNearbyPlants(Map map, IntVec3 center)
		{
			float boost = Props.growthBoost * Mathf.Max(0f, RM_CreatureBehaviorsSettings.dungSeedingMultiplier);
			if (boost <= 0f)
			{
				return;
			}

			int boosted = 0;
			foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, Props.seedRadius, useCenter: true))
			{
				if (boosted >= Props.maxPlantsBoosted)
				{
					break;
				}
				if (!cell.InBounds(map))
				{
					continue;
				}
				Plant plant = cell.GetPlant(map);
				if (plant == null || plant.Growth >= 1f)
				{
					continue;
				}
				plant.Growth = Mathf.Clamp01(plant.Growth + boost);
				boosted++;
			}
		}

		private void SeedYoungPlants(Map map, IntVec3 center)
		{
			int wanted = Mathf.RoundToInt(Props.seedPlantCount.RandomInRange
				* Mathf.Max(0f, RM_CreatureBehaviorsSettings.dungSeedingMultiplier));
			if (wanted <= 0)
			{
				return;
			}

			int placed = 0;
			foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, Props.seedRadius, useCenter: false))
			{
				if (placed >= wanted)
				{
					break;
				}
				if (!cell.InBounds(map) || cell.GetPlant(map) != null)
				{
					continue;
				}
				ThingDef plantDef = PickSeedPlant(map);
				if (plantDef == null)
				{
					return; // nothing this biome grows — no point walking the rest of the radius
				}
				if (!plantDef.CanEverPlantAt(cell, map))
				{
					continue;
				}
				if (GenSpawn.Spawn(plantDef, cell, map) is Plant seedling)
				{
					seedling.Growth = Mathf.Clamp01(Props.seedPlantGrowth);
					placed++;
				}
			}
		}

		/// <summary>
		/// The comp's own list if it has one, otherwise a plant the MAP'S biome
		/// already grows wild, weighted by its biome commonality — so a vector
		/// carries what belongs where it stopped rather than a fixed cargo.
		/// </summary>
		private ThingDef PickSeedPlant(Map map)
		{
			if (!Props.seedPlants.NullOrEmpty())
			{
				return Props.seedPlants.RandomElement();
			}

			BiomeDef biome = map.Biome;
			if (biome == null)
			{
				return null;
			}

			List<ThingDef> wild = biome.AllWildPlants;
			if (wild.NullOrEmpty())
			{
				return null;
			}

			float total = 0f;
			for (int i = 0; i < wild.Count; i++)
			{
				total += Mathf.Max(0f, biome.CommonalityOfPlant(wild[i]));
			}
			if (total <= 0f)
			{
				return null; // every weight zero — RandomElementByWeight would throw on this
			}

			return wild.RandomElementByWeight((ThingDef p) => Mathf.Max(0f, biome.CommonalityOfPlant(p)));
		}

		private void SeedYoungCreature(Map map, IntVec3 center)
		{
			float chance = Props.wildlifeSpawnChance * Mathf.Max(0f, RM_CreatureBehaviorsSettings.dungSeedingMultiplier);
			if (!Rand.Chance(chance))
			{
				return;
			}

			PawnKindDef kind = PickSeedWildlife(map);
			if (kind == null)
			{
				return;
			}

			if (!CellFinder.TryFindRandomCellNear(center, map, Mathf.Max(1, Mathf.RoundToInt(Props.seedRadius)),
				(IntVec3 c) => c.Standable(map)
					&& map.reachability.CanReach(center, c, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)),
				out IntVec3 spawnCell))
			{
				return;
			}

			float age = Mathf.Max(0.01f, Props.seededWildlifeAgeYears);
			PawnGenerationRequest request = new PawnGenerationRequest(kind, null,
				fixedBiologicalAge: age, fixedChronologicalAge: age);
			Pawn young = PawnGenerator.GeneratePawn(request);
			GenSpawn.Spawn(young, spawnCell, map);
		}

		private PawnKindDef PickSeedWildlife(Map map)
		{
			if (!Props.seedWildlife.NullOrEmpty())
			{
				return Props.seedWildlife.RandomElement();
			}

			BiomeDef biome = map.Biome;
			if (biome == null)
			{
				return null;
			}

			// The body-size cap is a PROPERTY OF THE COMP, not of the biome, so it
			// is applied here rather than baked into the cached roster — two
			// carriers with different caps must not poison each other's answer.
			List<PawnKindDef> roster = BiomeWildlife(biome);
			List<PawnKindDef> eligible = new List<PawnKindDef>();
			for (int i = 0; i < roster.Count; i++)
			{
				if (roster[i].RaceProps.baseBodySize <= Props.maxWildlifeBodySize)
				{
					eligible.Add(roster[i]);
				}
			}
			if (eligible.Count == 0)
			{
				return null;
			}

			return eligible.RandomElementByWeight((PawnKindDef k) => Mathf.Max(0f, biome.CommonalityOfAnimal(k)));
		}

		/// <summary>
		/// Every animal kind this biome spawns wild. BiomeDef publishes no
		/// wild-animal roster (only CommonalityOfAnimal, which answers per-kind
		/// and folds in every race declaring the biome in its own
		/// RaceProps.wildBiomes), so the roster is built by asking it once per
		/// kind and cached per biome — DefDatabase is immutable after load, so
		/// the answer cannot go stale within a session.
		/// </summary>
		private static List<PawnKindDef> BiomeWildlife(BiomeDef biome)
		{
			if (cachedBiomeWildlife.TryGetValue(biome, out List<PawnKindDef> cached))
			{
				return cached;
			}

			List<PawnKindDef> roster = new List<PawnKindDef>();
			foreach (PawnKindDef kind in DefDatabase<PawnKindDef>.AllDefs)
			{
				if (kind.race?.race == null || !kind.RaceProps.Animal)
				{
					continue;
				}
				if (biome.CommonalityOfAnimal(kind) <= 0f)
				{
					continue;
				}
				roster.Add(kind);
			}

			cachedBiomeWildlife[biome] = roster;
			return roster;
		}
	}
}
