using UnityEngine;
using Verse;

namespace RimMandrake.Spikes
{
    // SPIKE 1 — a pit cover that renders as the terrain of its own cell.
    //
    // VERIFIED-IN-SOURCE (1.6):
    //   BuildableDef.graphic            : public Graphic          (BuildableDef.cs:122)
    //   BuildableDef.DrawMatSingle      : => graphic?.MatSingle   (BuildableDef.cs:146)
    //   TerrainDef : BuildableDef, so cell.GetTerrain(map).graphic.MatSingle is the
    //   exact material the terrain section layer uses (TerrainDef.cs:415 uses the
    //   same graphic.MatSingle for its own DrawMatPolluted).
    //   Thing.Print(SectionLayer layer) : public virtual          (Thing.cs:1333)
    //   Printer_Plane.PrintPlane(MapDrawLayer layer, Vector3 center, Vector2 size,
    //     Material mat, float rot, bool flipUv, Vector2[] uvs, Color32[] colors,
    //     float topVerticesAltitudeBias, float uvzPayload)        (Printer_Plane.cs:50)
    //     NOTE: 1.6 takes MapDrawLayer here, not SectionLayer — SectionLayer is
    //     accepted because it derives from MapDrawLayer.
    //
    // THE TRICK: buildings are PRINTED into a static section mesh, so the cover
    // overrides Print() and prints a plane with the TERRAIN'S OWN MATERIAL instead
    // of its def graphic. No texture copying, no atlas work — the terrain's
    // material already exists and tiles by world position in its shader.
    //
    // UNPROVEN UNTIL RUNTIME (FOUNDRY quicktest questions in README):
    //   - altitude: the cover must print ABOVE terrain but BELOW pawns/items;
    //     def.altitudeLayer (e.g. FloorCoverings) governs the section, and the
    //     printed plane's y comes from the layer — verify no z-fighting.
    //   - terrain shaders tile by world uv, so a 1x1 plane likely blends
    //     seamlessly — verify the seam actually disappears.
    //   - re-print on terrain change: Map.mapDrawer.MapMeshDirty on the cell when
    //     terrain under the cover changes (hook TerrainGrid or accept staleness).
    public class Building_TerrainMimicCover : Building
    {
        public override void Print(SectionLayer layer)
        {
            TerrainDef terrain = Position.GetTerrain(Map);
            Material mat = terrain?.graphic?.MatSingle;
            if (mat == null)
            {
                base.Print(layer); // fallback: def graphic (the BadGraphic pink square in the worst case)
                return;
            }
            Vector2 size = new Vector2(def.size.x, def.size.z);
            Printer_Plane.PrintPlane(layer, DrawPos, size, mat);
        }
    }
}
