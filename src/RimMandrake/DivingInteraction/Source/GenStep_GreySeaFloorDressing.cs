using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_FLOOR_FORMATIONS_1 / _BRINE_POOL_DEFENCE_1 / _BRINE_ELDERS_1 /
    // _CRYSTAL_FLORA_1 — the Grey Sea floor's terrain dressing, in one step.
    //
    // WHAT IT DOES, and which owner ruling each part serves (all 2026-09-26,
    // design/Jawa/worldbuilding/biomes/the_grey_deep.md §4b/§4d/§4e):
    //
    //   1. THE BASIN. Carves the deepest pool of the floor at the map's
    //      lowest-elevation cell: RM_BrinePoolDeep in the middle,
    //      RM_BrinePoolShallow as its margin. "The pools have shores, and
    //      their stillness is the deadliest thing in the biome."
    //   2. THE JACKET. Rings the pool margin with scattered RM_BrineJacket —
    //      the salt twin of Odyssey's SolidIce. This is the sheet's
    //      "jacketed salvage … chiseled free" and the drop's "loot within the
    //      pools is ultra-protected until the player figures out how to get
    //      at it", in the only form it can take before the encasement C#
    //      exists: the mineral is there, and digging it is the first key.
    //   3. THE ELDER. RULED (Q10): "ONLY grey sea, but there's one per grey
    //      sea tile." One RM_BrineElder rises from that basin. Sessile, so
    //      it is a 7x7 Thing placed here and never a pawn.
    //   4. THE SEEP APRONS. RM_ChimneySeepFloor around every RM_SaltChimney
    //      the scatter step already placed.
    //   5. THE BRINE CHANNELS. RULED (Q3): "brine rivers" are a CHANNEL
    //      TERRAIN STRIP running from the chimney field downhill into a pool.
    //      No vanilla river machinery — the pocket map has no river genstep
    //      and the surface sea is allowRivers false. Each chimney runs one
    //      channel to the basin.
    //
    // 🔑 WHY TERRAIN AND NOT PLANTS. Steps 4 and 5 paint terrain and place
    // NO flora at all, and that is the design. RM_SaltChimneyVine is gated
    // by wildTerrainTags RM_GreyChimneySeep and RM_GlassVeilKelp by
    // RM_GreyBrineChannel, so once this step has painted, the VANILLA Plants
    // genstep (order 900, listed after this one) grows both by itself. The
    // owner's specs — "grow ONLY around warm mineral seeps", "over trenches
    // and brine rivers" — are enforced by the terrain, which means they stay
    // enforced for every later spawn too, not just at map gen.
    //
    // ⚠️ WHY THIS LIVES IN mandrake.rm.divinginteraction AND NOT IN THE
    // BIOME'S OWN MOD. mandrake.rm.terminalbiomes owns RM_GreySea and would
    // be the natural home, but its assembly was under concurrent edit when
    // this was written and two agents rebuilding one DLL is how a merge
    // silently drops half a build (DLL_SOURCE_STAMP_GUARD_1 exists because
    // that happened). This mod already owns every other sea-dive genstep
    // (GenStep_SeaFloorTerrain / _SeaFloorFauna / _PlaceSeaDiveExit), so the
    // step is at home here. It takes no hard reference to the biome mod:
    // every def is resolved by name with GetNamedSilentFail and a missing one
    // skips that part of the dressing rather than throwing.
    //
    // ⛔ SCOPE. The step is listed ONLY on RM_SeaDiveGenerator_GreySea, and
    // it additionally refuses to run on a map whose biome is not RM_GreySea.
    // The belt-and-braces matters: the floor terrain tag RM_SeaFloorGround is
    // shared by all four sea floors, so nothing in the terrain can tell the
    // Grey apart from the Scald.
    //
    // 🔴 WHAT IS STILL NOT BUILT, so nobody reads a carved pool as a finished
    // mechanism: touching the pool does NOTHING yet. The crystallisation
    // defence — RULED (Q1b) a crystallised pawn is ENCASED AS AN OBJECT that
    // must be mined out, not given a hediff — is GREYSEA_BRINE_POOL_DEFENCE_1
    // and needs its own C#. Same for the chimney plume's shorter-range
    // version of it (Q2), and for everything the Elder does (its discharge,
    // its persisted per-tile seen-set, its novelty trade). This step builds
    // the PLACE. The mechanisms are owed.
    // ════════════════════════════════════════════════════════════════════
    public class GenStep_GreySeaFloorDressing : GenStep
    {
        // Tuned to read like reference image 01/04, not measured. A live look
        // is owed; do not cite these as anything but a first guess.
        private const float PoolDeepRadius = 5.4f;
        private const float PoolMarginRadius = 8.6f;
        private const float JacketRingOuter = 11.5f;
        private const float JacketChance = 0.22f;
        private const float SeepApronRadius = 3.4f;
        private const int ElderSize = 7;

        public override int SeedPart => 5140937;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (map?.Biome == null || map.Biome.defName != "RM_GreySea")
            {
                return;
            }

            TerrainDef poolDeep = Named<TerrainDef>("RM_BrinePoolDeep");
            TerrainDef poolShallow = Named<TerrainDef>("RM_BrinePoolShallow");
            TerrainDef channel = Named<TerrainDef>("RM_BrineChannel");
            TerrainDef apron = Named<TerrainDef>("RM_ChimneySeepFloor");
            ThingDef jacket = Named<ThingDef>("RM_BrineJacket");
            ThingDef elder = Named<ThingDef>("RM_BrineElder");
            ThingDef chimney = Named<ThingDef>("RM_SaltChimney");

            IntVec3 basin = FindBasinCell(map);
            if (basin.IsValid && poolDeep != null && poolShallow != null)
            {
                CarveBasin(map, basin, poolDeep, poolShallow, jacket);
                if (elder != null)
                {
                    PlaceElder(map, basin, elder);
                }
            }

            if (chimney == null)
            {
                return;
            }

            // The chimneys were placed by RM_GreySeaScatterChimneys (order
            // 864); this step is 880, so they are on the map now. Copy the
            // list before touching terrain, because painting can destroy
            // edifices and mutate the source list underneath an enumerator.
            List<Thing> chimneys = new List<Thing>(map.listerThings.ThingsOfDef(chimney));
            foreach (Thing c in chimneys)
            {
                if (apron != null)
                {
                    PaintApron(map, c.Position, apron);
                }
                if (channel != null && basin.IsValid)
                {
                    CarveChannel(map, c.Position, basin, channel);
                }
            }
        }

        private static T Named<T>(string defName) where T : Def
        {
            return DefDatabase<T>.GetNamedSilentFail(defName);
        }

        // The deepest pool is the lowest ground. GenStep_ElevationFertility
        // (order 10) has already filled MapGenerator.Elevation by the time
        // this runs, so the basin is read off the map's own shape rather than
        // dropped at random — which is what makes "follow the channel
        // downhill and you arrive at the thing that kills you" true.
        private static IntVec3 FindBasinCell(Map map)
        {
            MapGenFloatGrid elevation = MapGenerator.Elevation;
            IntVec3 best = IntVec3.Invalid;
            float bestVal = float.MaxValue;
            int margin = Mathf.RoundToInt(JacketRingOuter) + 4;

            foreach (IntVec3 c in map.AllCells)
            {
                if (c.x < margin || c.z < margin || c.x >= map.Size.x - margin || c.z >= map.Size.z - margin)
                {
                    continue;
                }
                float v = elevation[c];
                if (v < bestVal)
                {
                    bestVal = v;
                    best = c;
                }
            }
            return best;
        }

        private static void CarveBasin(Map map, IntVec3 centre, TerrainDef deep, TerrainDef shallow, ThingDef jacket)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, JacketRingOuter, useCenter: true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                float d = c.DistanceTo(centre);

                if (d <= PoolMarginRadius)
                {
                    // Formations scattered at 860-876 may already stand here.
                    // The basin wins: a pool with a salt pillar in the middle
                    // of it is not a pool.
                    c.GetEdifice(map)?.Destroy();
                    map.terrainGrid.SetTerrain(c, d <= PoolDeepRadius ? deep : shallow);
                    continue;
                }

                // The jacket ring: scattered, never a solid wall, so the pool
                // has an approach and the "harvest happens at their shores"
                // ruling stays playable.
                if (jacket != null && c.GetEdifice(map) == null && Rand.Chance(JacketChance)
                    && GenSpawn.CanSpawnAt(jacket, c, map))
                {
                    GenSpawn.Spawn(jacket, c, map);
                }
            }
        }

        private static void PlaceElder(Map map, IntVec3 basin, ThingDef elder)
        {
            CellRect rect = CellRect.CenteredOn(basin, ElderSize / 2);
            if (!rect.InBounds(map))
            {
                return;
            }
            foreach (IntVec3 c in rect)
            {
                c.GetEdifice(map)?.Destroy();
            }
            GenSpawn.Spawn(elder, basin, map, Rot4.North);
        }

        private static void PaintApron(Map map, IntVec3 centre, TerrainDef apron)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, SeepApronRadius, useCenter: true))
            {
                if (!c.InBounds(map) || c.GetTerrain(map).IsWater)
                {
                    continue;
                }
                map.terrainGrid.SetTerrain(c, apron);
            }
        }

        // A straight run from the chimney to the basin, one to two cells
        // wide. Straight rather than gradient-followed on purpose: the basin
        // IS the low point, so downhill and towards-the-basin are the same
        // direction, and a line is legible from the air in a way a
        // meandering gradient walk is not.
        private static void CarveChannel(Map map, IntVec3 from, IntVec3 to, TerrainDef channel)
        {
            foreach (IntVec3 c in GenSight.PointsOnLineOfSight(from, to))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                // Stop at the pool: the channel feeds it, it does not cross it.
                if (c.GetTerrain(map).IsWater)
                {
                    return;
                }
                c.GetEdifice(map)?.Destroy();
                map.terrainGrid.SetTerrain(c, channel);

                IntVec3 side = c + (Rand.Bool ? IntVec3.East : IntVec3.North);
                if (side.InBounds(map) && !side.GetTerrain(map).IsWater)
                {
                    side.GetEdifice(map)?.Destroy();
                    map.terrainGrid.SetTerrain(side, channel);
                }
            }
        }
    }
}
