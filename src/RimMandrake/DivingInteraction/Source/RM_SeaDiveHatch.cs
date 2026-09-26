using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_MAPS_BUILD_1. A MapPortal built into a gravship's own
    // structure: right-click "Enter" while the ship sits over one of the
    // four terminal seas to descend to that sea's own floor pocket map,
    // where its BiomeDef's wildAnimals cast is explicitly seeded (see
    // GenStep_SeaFloorFauna — ambient per-cell spawning never reaches a
    // sea biome's own cast, MEASURED live 2026-09-26, this item's ledger).
    //
    // One ThingDef, one class: the pocket-map generator is picked at
    // GENERATE time from whichever sea biome the parent map's tile
    // currently carries (Map.Biome), not baked into four separate hatch
    // defs — "one mechanism parameterized by biome," per this item's brief.
    //
    // SHIP-ONLY ACCESS (owner ruling 2026-09-26, mid-turn, this item's
    // ledger, recorded by BENCH as the provenance guard cannot see
    // mid-turn chat): the gravship is the sole dive/resurface mechanism, so
    // this building is placeable only where PlaceWorker_NeedsGravEngine
    // allows it — inside a structure that already carries a GravEngine.
    // There is no shore-terrain entry point any more: RM_DiveEligible,
    // the float-menu provider and both shore JobDrivers are removed from
    // this mod entirely (see the deletions in this same commit).
    public class RM_SeaDiveHatch : MapPortal
    {
        // Sea BiomeDef defName -> its dedicated pocket-map generator defName.
        // Kept as strings, resolved lazily, so this file never hard-fails
        // if a given sea's mod is absent from an install — it just isn't
        // enterable there (IsEnterable already requires the map's own
        // biome be one of these four).
        private static readonly Dictionary<string, string> SeaGenerators = new Dictionary<string, string>
        {
            { "RM_TheScald", "RM_SeaDiveGenerator_TheScald" },
            { "RM_GreySea", "RM_SeaDiveGenerator_GreySea" },
            { "RM_TwilightSea", "RM_SeaDiveGenerator_TwilightSea" },
            { "RM_PropaneLake", "RM_SeaDiveGenerator_PropaneLake" },
        };

        private MapGeneratorDef ResolveGeneratorForCurrentTile()
        {
            BiomeDef biome = base.Spawned ? base.Map.Biome : null;
            if (biome != null && SeaGenerators.TryGetValue(biome.defName, out string genName))
            {
                MapGeneratorDef gen = DefDatabase<MapGeneratorDef>.GetNamedSilentFail(genName);
                if (gen != null)
                {
                    return gen;
                }
            }
            // Falls back to whatever the ThingDef itself declares (kept
            // non-null purely to satisfy MapPortalProperties' own
            // ConfigErrors — see RM_SeaDiveHatch.xml's comment). This path
            // is only reached if the hatch is somehow entered from a
            // non-sea tile, which IsEnterable already refuses.
            return def.portal.pocketMapGenerator;
        }

        public override bool IsEnterable(out string reason)
        {
            if (!RM_DivingSettings.masterEnabled)
            {
                reason = "RM_SeaDiveDisabled".Translate();
                return false;
            }
            BiomeDef biome = base.Spawned ? base.Map.Biome : null;
            if (biome == null || !SeaGenerators.ContainsKey(biome.defName))
            {
                reason = "RM_SeaDiveNotAtSea".Translate();
                return false;
            }
            return base.IsEnterable(out reason);
        }

        protected override Map GeneratePocketMapInt()
        {
            MapGeneratorDef generator = ResolveGeneratorForCurrentTile();
            return PocketMapUtility.GeneratePocketMap(
                new IntVec3(def.portal.pocketMapSize, 1, def.portal.pocketMapSize),
                generator,
                GetExtraGenSteps(),
                base.Map);
        }
    }
}
