using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_MAPS_BUILD_1. ENGINE ANSWER, MEASURED live 2026-09-26 (this
    // item's own ledger): a sea BiomeDef's <wildAnimals> never ambient-
    // spawns at a spawnable cell — the vanilla spawn chooser reads
    // BiomeAt(cell) per cell, and a sea biome's only cells are its
    // unstandable water, so its own wildAnimals list is never consulted at
    // a cell an animal could actually stand on. Design consequence, same
    // note: "dive/floor maps must seed their own cast via their generator
    // or a map component." This GenStep is that seeding.
    //
    // One class, reused by all four RM_SeaDiveGenerator_* defs —
    // parameterized purely by map.Biome (set per-generator via
    // pocketMapProperties.biome), never four copies.
    public class GenStep_SeaFloorFauna : GenStep
    {
        // Tuned low deliberately: these are pocket maps ~50x50, not a full
        // world tile, and every sea's animalDensity here is already small
        // (0.1-0.15). This is a placeholder population size — the exact
        // "how many bottom-walkers should a diver actually meet" number is
        // owed to a live walk with the owner, same posture as every other
        // sea-floor content decision on this item.
        public float countPerAnimalDensity = 20f;

        public override int SeedPart => 8362342;

        public override void Generate(Map map, GenStepParams parms)
        {
            // SEABED_FLOOR_GENERATORS_1: on the seabed layer map.Biome is the floor biome (no cast);
            // the cast lives on the sea above, which SeaBiomeOf returns for both paths.
            BiomeDef biome = RM_SeaFloorIdentity.SeaBiomeOf(map) ?? map.Biome;
            if (biome == null)
            {
                return;
            }

            if (biome.defName == "RM_TheChill" && RM_DivingSettings.chillDensityDrawEnabled)
            {
                GenerateWeightedDraw(map, biome);
                return;
            }

            int totalToSpawn = Mathf.Max(1, Mathf.RoundToInt(countPerAnimalDensity * Mathf.Max(biome.animalDensity, 0.05f)));

            foreach (PawnKindDef kind in biome.AllWildAnimals)
            {
                float commonality = biome.CommonalityOfAnimal(kind);
                if (commonality <= 0f)
                {
                    continue;
                }

                // Stochastic rounding: floor(expected) plus a roll on the fraction, so a rare
                // species (0.01-0.04 commonality apex creature) keeps its chance and the count
                // has no jump at the old RoundToInt 0.5 boundary.
                float expected = totalToSpawn * commonality;
                int countForKind = Mathf.FloorToInt(expected);
                if (Rand.Chance(expected - countForKind))
                {
                    countForKind++;
                }

                for (int i = 0; i < countForKind; i++)
                {
                    if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && !c.Fogged(map), out IntVec3 cell))
                    {
                        continue;
                    }

                    PawnGenerationRequest request = new PawnGenerationRequest(
                        kind,
                        null,
                        PawnGenerationContext.NonPlayer,
                        forceGenerateNewPawn: true,
                        canGeneratePawnRelations: false);
                    Pawn pawn = PawnGenerator.GeneratePawn(request);
                    GenSpawn.Spawn(pawn, cell, map);
                }
            }
        }

        // CHILL_DIVE_DENSITY_SAMPLER_1. The Chill's animalDensity (0.08) rounds the legacy path to one of nearly
        // every species. Here the dive instead meets chillDiveAnimalCount animals, each drawn by commonality
        // weight with replacement. The count is a PROVISIONAL setting (default 3), tuned later on a live walk.
        // Mirrored offline by density_sampler.py.
        private static void GenerateWeightedDraw(Map map, BiomeDef biome)
        {
            var kinds = new System.Collections.Generic.List<PawnKindDef>();
            var weights = new System.Collections.Generic.List<float>();
            foreach (PawnKindDef kind in biome.AllWildAnimals)
            {
                float w = biome.CommonalityOfAnimal(kind);
                if (w > 0f)
                {
                    kinds.Add(kind);
                    weights.Add(w);
                }
            }
            if (kinds.Count == 0)
            {
                return;
            }

            int count = Mathf.Clamp(RM_DivingSettings.chillDiveAnimalCount, 1, 8);
            for (int n = 0; n < count; n++)
            {
                float total = 0f;
                for (int i = 0; i < weights.Count; i++) total += weights[i];
                float roll = Rand.Value * total;
                int pick = kinds.Count - 1;
                for (int i = 0; i < weights.Count; i++)
                {
                    roll -= weights[i];
                    if (roll <= 0f) { pick = i; break; }
                }

                if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && !c.Fogged(map), out IntVec3 cell))
                {
                    continue;
                }
                PawnGenerationRequest request = new PawnGenerationRequest(
                    kinds[pick],
                    null,
                    PawnGenerationContext.NonPlayer,
                    forceGenerateNewPawn: true,
                    canGeneratePawnRelations: false);
                GenSpawn.Spawn(PawnGenerator.GeneratePawn(request), cell, map);
            }
        }
    }
}
