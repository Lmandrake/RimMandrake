using UnityEngine;
using Verse;

namespace RimMandrake.Pits
{
    // Terrain-mimic printing, factored out of Building_OpenPit so any future
    // building (not just pits) can cheaply read the same trick. Verified API
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

    // Standalone example building kept for compile-shape parity with the spike;
    // Building_OpenPit is the one actually placed in Defs (it needs the trigger/
    // holder machinery too, so it inlines the same TerrainMimicPrinter call
    // rather than inheriting from here).
    public class Building_TerrainMimicCover : Building
    {
        public override void Print(SectionLayer layer)
        {
            TerrainMimicPrinter.PrintTerrainMimic(this, layer);
        }
    }
}
