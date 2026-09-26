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
            BiomeDef biome = map.Biome;
            if (biome == null)
            {
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

                int countForKind = Mathf.RoundToInt(totalToSpawn * commonality);
                if (countForKind <= 0)
                {
                    // A rare species (e.g. a 0.01-0.04 commonality apex
                    // creature) still deserves a CHANCE to appear rather
                    // than being rounded to zero every single dive.
                    countForKind = Rand.Chance(commonality) ? 1 : 0;
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
    }
}
