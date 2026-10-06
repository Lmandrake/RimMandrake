using RimWorld;
using Verse;

namespace RimMandrake.RustCathedral
{
    // RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 §2. Places AT MOST ONE borehulk on
    // a Rust Cathedral map at generation, with a chance (Mod Settings, default
    // 0.6). Not a wildAnimals entry, so the wild spawner never respawns it: a
    // map that rolls none has none, ever. Self-gated on RM_RustCathedral the
    // same way as GenStep_ScatterSacredWalls (Walls assembly), and patched
    // into MapCommonBase the same way (Patches/RM_Borehulk_MapGenPatch.xml).
    //
    // Cell rule: standable, no building on it, no water, not within
    // sacredClearance of any sacred-wall Thing (sacredWallDef). The item's
    // "never inside a sacred wall ring" is implemented as that clearance —
    // PROVISIONAL, since the shipped sacred tier is a single 1-cell conduit,
    // not a ring.
    public class RM_GenStep_BorehulkPlacement : GenStep
    {
        public const string CathedralBiomeDefName = "RM_RustCathedral";

        public PawnKindDef pawnKind;

        public ThingDef sacredWallDef;

        public int sacredClearance = 8;

        public int minEdgeDistance = 12;

        public override int SeedPart => 1460728193;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_RustCathedralSettings.borehulkEnabled)
            {
                return;
            }
            if (map.Biome == null || map.Biome.defName != CathedralBiomeDefName)
            {
                return;
            }
            if (pawnKind == null)
            {
                Log.Error("[RustCathedral] RM_GenStep_BorehulkPlacement has no pawnKind configured.");
                return;
            }
            if (!Rand.Chance(UnityEngine.Mathf.Clamp01(RM_RustCathedralSettings.borehulkSpawnChance)))
            {
                return;
            }
            if (!CellFinderLoose.TryFindRandomNotEdgeCellWith(minEdgeDistance, c => CanPlaceAt(c, map), map, out IntVec3 cell))
            {
                return;
            }
            Pawn borehulk = PawnGenerator.GeneratePawn(pawnKind, null);
            GenSpawn.Spawn(borehulk, cell, map, WipeMode.Vanish);
        }

        private bool CanPlaceAt(IntVec3 c, Map map)
        {
            if (!c.Standable(map))
            {
                return false;
            }
            TerrainDef terrain = c.GetTerrain(map);
            if (terrain == null || terrain.IsWater)
            {
                return false;
            }
            if (c.GetFirstBuilding(map) != null)
            {
                return false;
            }
            if (sacredWallDef != null)
            {
                foreach (Thing t in map.listerThings.ThingsOfDef(sacredWallDef))
                {
                    if (t.Position.InHorDistOf(c, sacredClearance))
                    {
                        return false;
                    }
                }
            }
            return true;
        }
    }
}
