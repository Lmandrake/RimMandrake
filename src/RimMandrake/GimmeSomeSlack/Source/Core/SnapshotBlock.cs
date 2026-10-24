using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>GSS_WATER_STUB_FIX_PASSED_LAST_WEEK: what one map cell is to the cord model (CordWorldAdapter.Snapshot).
    /// The adapter used to read "walkable on the path grid = open ground" before it looked at water. FlowWorks R12
    /// (DEEP_WATER_BUILD_SWIM_OR_SINK, 2026-10-17) makes deep water swimmable by the PATH GRID only (PathGrid.CalculatedCostAt),
    /// keeping WaterDeep's def passability Impassable; with FlowWorks loaded every deep-water cell read as open ground, so a
    /// waterproof conduit crossing a canal lay on the water as a plain cord instead of diving (matrix MX_F60_T15_S0: 0 of 2
    /// water stubs). Rule: water terrain whose DEF is impassable is Water whatever the path grid says (a swimmer crosses
    /// it; a cord still cannot lie on it). Verse-free so the selftest runs the production rule.</summary>
    internal static class SnapshotBlock
    {
        /// <summary>null = open ground (the cord may lie there), else the block kind.
        /// walkable: the path grid's answer; hasEdifice/edificeRock/edificePowered: the edifice on the cell;
        /// water: TerrainDef.IsWater; terrainImpassable: TerrainDef.passability == Impassable.</summary>
        internal static BlockKind? Of(bool walkable, bool hasEdifice, bool edificeRock, bool edificePowered,
                                    bool water, bool terrainImpassable)
        {
            if (!hasEdifice && water && terrainImpassable) return BlockKind.Water;
            if (walkable) return null;
            if (hasEdifice) return edificeRock ? BlockKind.Rock : edificePowered ? BlockKind.Device : BlockKind.Wall;
            return water ? BlockKind.Water : BlockKind.Wall;
        }
    }
}
