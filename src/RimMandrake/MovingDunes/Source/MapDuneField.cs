using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>The real sand grid of one map, seen through the Verse-free kernel's IDuneField.</summary>
    public sealed class MapDuneField : IDuneField
    {
        private readonly Map map;

        public Map Map { get { return map; } }
        private readonly SandGrid grid;

        public MapDuneField(Map map)
        {
            this.map = map;
            grid = map.sandGrid;
        }

        public int Width { get { return map.Size.x; } }
        public int Height { get { return map.Size.z; } }
        public float MaxDepth { get { return SandGrid.MaxDepth; } }
        public float TotalDepth { get { return grid.TotalDepth; } }

        public float GetDepth(int x, int z) { return grid.GetDepth(new IntVec3(x, 0, z)); }
        public void SetDepth(int x, int z, float depth) { grid.SetDepth(new IntVec3(x, 0, z), depth); }
        public bool Roofed(int x, int z) { return map.roofGrid.Roofed(new IntVec3(x, 0, z)); }

        /// <summary>The terrain half of Patch_SandGrid_CanHaveSand (water and space refuse sand); the edifice half is BlocksSand.</summary>
        public bool CanHoldSand(int x, int z)
        {
            TerrainDef terrain = map.terrainGrid.TerrainAt(new IntVec3(x, 0, z));
            return terrain == null || terrain.holdSnowOrSand;
        }

        public bool BlocksSand(int x, int z)
        {
            Building edifice = new IntVec3(x, 0, z).GetEdifice(map);
            return edifice != null && !SandGrid.CanCoexistWithSand(edifice.def);
        }
    }
}
