using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F1/F5 spike (fever_wood_kit_spec.md). Marks a
    // TerrainDef as part of the Tenant's registered pool network — every
    // marked terrain on a map is treated as ONE shared aquifer body by
    // RUT_MapComponent_TheTenant (the sheet's "one aquifer, one entity",
    // §4). Also doubles as F5's "pool water grants no buildable affordance"
    // marker so the linter-checkable half of ban §6.4 can be asserted from
    // one hook rather than a terrain-name string match.
    //
    // Generic (no Fever Wood string inside): any biome's still-water kit
    // can carry this extension on its own pool terrains.
    public class RM_LurkingWaterExtension : DefModExtension
    {
        /// <summary>Adjacency, in cells, at which a pawn standing near (not
        /// necessarily on) this terrain accrues Tenant exposure. INVENTED
        /// default per the kit spec (1 cell).</summary>
        public int exposureAdjacency = 1;
    }
}
