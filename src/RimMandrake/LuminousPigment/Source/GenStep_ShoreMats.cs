using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §2.2, first bullet: wild crowncarpet on any ocean shore, standalone,
    // rare. Runs on every map (self-gates on shoreMatsEnabled and on there
    // being any qualifying cell) rather than being restricted by biome -- the
    // Scald's own dense population is a separate wildPlants row on that
    // BiomeDef, unaffected by this GenStep. Legality is entirely the terrain
    // tag: Patches/CrowncarpetBedTag.xml adds RM_CrowncarpetBed to vanilla
    // WaterOceanShallow, so checking the tag on a cell IS checking "is this a
    // legal ocean shore cell" -- no separate land-adjacency test needed.
    public class GenStep_ShoreMats : GenStep
    {
        public override int SeedPart => 8006854;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!LuminousPigmentSettings.shoreMatsEnabled) return;

            ThingDef plantDef = ThingDef.Named("RM_Crowncarpet");
            if (plantDef == null) return;

            float chance = LuminousPigmentSettings.shoreMatChance;
            if (chance <= 0f) return;

            foreach (IntVec3 cell in map.AllCells)
            {
                if (!CanHostMat(map, cell)) continue;
                if (!Rand.Chance(chance)) continue;

                int count = Rand.RangeInclusive(1, 3);
                int placed = 0;
                for (int i = 0; i < count; i++)
                {
                    IntVec3 target = (i == 0) ? cell : FindNearbyHost(map, cell);
                    if (target == IntVec3.Invalid || !CanHostMat(map, target)) continue;
                    Thing plant = ThingMaker.MakeThing(plantDef);
                    GenSpawn.Spawn(plant, target, map);
                    placed++;
                }
                if (placed > 0)
                {
                    // Don't re-roll the same cell as the anchor of another
                    // cluster on this same pass -- Rand.Chance already makes
                    // clusters rare; this just avoids double-anchoring.
                }
            }
        }

        private static IntVec3 FindNearbyHost(Map map, IntVec3 near)
        {
            if (CellFinder.TryFindRandomCellNear(near, map, 2, c => CanHostMat(map, c), out IntVec3 found))
                return found;
            return IntVec3.Invalid;
        }

        private static bool CanHostMat(Map map, IntVec3 c)
        {
            if (!c.InBounds(map)) return false;
            TerrainDef t = map.terrainGrid.TerrainAt(c);
            if (t == null || t.tags == null) return false;
            if (!t.tags.Contains("RM_CrowncarpetBed") && !t.tags.Contains("RUT_ScaldMarginMat")) return false;
            return c.GetPlant(map) == null;
        }
    }
}
