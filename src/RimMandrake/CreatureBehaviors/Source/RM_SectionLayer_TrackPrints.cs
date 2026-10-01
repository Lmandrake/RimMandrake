using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 — the draw.
    //
    // One SectionLayer printing a rotated print sprite per record in its
    // section. Section's constructor instantiates every non-abstract
    // SectionLayer subclass per section per map (MovingDunes'
    // SectionLayer_DuneSand is the shipped precedent), and it rebuilds only
    // when its section carries the RM_TrackPrints mesh flag, which
    // RM_MapComponent_TrackGrid raises per written/cleared cell. Prints sit
    // just above the Filth altitude so they read ON the settled film.
    // ════════════════════════════════════════════════════════════════════
    public class RM_SectionLayer_TrackPrints : SectionLayer
    {
        private static readonly Dictionary<string, Material> matCache = new Dictionary<string, Material>();
        private static float matCacheOpacity = -1f;

        public RM_SectionLayer_TrackPrints(Section section) : base(section)
        {
            relevantChangeTypes = RM_TrackDefOf.RM_TrackPrints;
        }

        public override bool Visible => RM_CreatureBehaviorsSettings.tracksEnabled;

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            RM_MapComponent_TrackGrid grid = RM_MapComponent_TrackGrid.For(Map);
            RM_TrackPool pool = grid?.Pool;
            if (pool == null || pool.Count == 0) return;

            float y = AltitudeLayer.Filth.AltitudeFor(5f);
            CellRect rect = section.CellRect;
            CellIndices indices = Map.cellIndices;
            for (int z = rect.minZ; z <= rect.maxZ; z++)
            {
                for (int x = rect.minX; x <= rect.maxX; x++)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (!pool.TryGet(indices.CellToIndex(c), out RM_TrackRecord rec)) continue;
                    if (!grid.TryGetStyle(rec.style, out string texPath, out float size)) continue;
                    Material mat = MaterialFor(texPath);
                    if (mat == null) continue;
                    Vector3 center = c.ToVector3Shifted();
                    center.y = y;
                    Printer_Plane.PrintPlane(this, center, new Vector2(size, size), mat, rec.Angle);
                }
            }
            FinalizeMesh(MeshParts.All);
        }

        private static Material MaterialFor(string texPath)
        {
            float opacity = Mathf.Clamp01(RM_CreatureBehaviorsSettings.trackPrintOpacity);
            if (opacity != matCacheOpacity)
            {
                matCache.Clear();
                matCacheOpacity = opacity;
            }
            if (!matCache.TryGetValue(texPath, out Material mat))
            {
                mat = MaterialPool.MatFrom(texPath, ShaderDatabase.Transparent, new Color(1f, 1f, 1f, opacity));
                matCache[texPath] = mat;
            }
            return mat;
        }
    }
}
