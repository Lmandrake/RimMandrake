using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
    // Terrain-mimic printing: a cover (PIT_COVER_FALL_REWIRE_1) prints the
    // terrain under it so the hole it hides cannot be seen. Verified API
    // shape: src/RimMandrake/Spikes/Spike1_TerrainMimic.cs (BuildableDef.graphic,
    // TerrainDef : BuildableDef, Thing.Print(SectionLayer), Printer_Plane.PrintPlane).
    //
    // UNPROVEN UNTIL RUNTIME (inherited from the spike, not resolved here):
    // altitude/z-fighting against the terrain layer, whether the seam actually
    // vanishes at play zoom, and whether a dirty-mesh hook is needed when the
    // terrain under the cover changes. FOUNDRY quicktest questions.
    public static class TerrainMimicPrinter
    {
        public static void PrintTerrainMimic(Thing thing, SectionLayer layer)
        {
            Map map = thing.Map;
            if (map == null) return;

            CellRect rect = thing.OccupiedRect();
            foreach (IntVec3 cell in rect)
            {
                TerrainDef terrain = cell.GetTerrain(map);
                Material mat = terrain?.graphic?.MatSingle;
                if (mat == null) continue;

                Vector3 center = cell.ToVector3Shifted();
                center.y = thing.DrawPos.y;
                Printer_Plane.PrintPlane(layer, center, Vector2.one, mat);
            }
        }
    }
}
