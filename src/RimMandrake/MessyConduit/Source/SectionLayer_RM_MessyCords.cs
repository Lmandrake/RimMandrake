using System;
using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>
    /// Prints the cords OWNED by this section into a static section mesh (design §8.1): the engine
    /// instantiates every non-abstract SectionLayer subclass for every 17x17 section
    /// (Section's constructor, decompiled 1.6), so no Harmony is needed. Zero cost per frame; the
    /// mesh is rebuilt only when a relevant change flag dirties the section.
    ///
    /// A cord is owned by the section of its lower endpoint cell, so it is printed exactly once.
    /// GetBoundaryRect returns the real printed extent, so Section.Bounds keeps a long cord drawn
    /// whenever any of it is on screen (not SectionLayer_Dynamic: dynamic layers are excluded from
    /// Section.Bounds).
    /// </summary>
    public class SectionLayer_RM_MessyCords : SectionLayer
    {
        private CellRect bounds;
        public const float StrandWidth = 0.11f;
        public const float ShadowWidth = 0.17f;
        public const float FaceLift = 0.01f;
        public static int LastPrintedVerts;
        private const int MaxMeshVerts = 65000;

        public SectionLayer_RM_MessyCords(Section section) : base(section)
        {
            relevantChangeTypes = (ulong)RimWorld.MapMeshFlagDefOf.Buildings | (ulong)RimWorld.MapMeshFlagDefOf.PowerGrid |
                                  (ulong)RimWorld.MapMeshFlagDefOf.Terrain | (ulong)RimWorld.MapMeshFlagDefOf.FogOfWar |
                                  (ulong)MessyConduitDefOf.RM_MessyCords;
            bounds = section.CellRect;
        }

        public override bool Visible => MessyConduitSettings.enabled;

        public override CellRect GetBoundaryRect() => bounds;

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            bounds = section.CellRect;
            var comp = Map.GetComponent<RM_MapComponent_CordGraph>();
            List<LaidPiece> owned = comp?.PiecesForSection(section.botLeft);
            int verts = 0;
            if (owned != null && CordMaterials.Strand != null)
            {
                float baseY = AltitudeLayer.Conduits.AltitudeFor();
                // face pieces sit ABOVE the wall/rock sprite: a stub drawn at Building altitude was
                // hidden by the wall (live pass 2). BuildingOnTop is the engine's own layer for things
                // drawn on top of a building (Building_MechCharger, CompRitualFireOverlay).
                float faceY = AltitudeLayer.BuildingOnTop.AltitudeFor() + FaceLift;
                int k = 0;
                foreach (LaidPiece p in owned)
                {
                    foreach (CordStrand s in p.Strands)
                    {
                        float y = s.OverFace ? faceY : baseY + 0.0006f * (k % 12);
                        if (!s.OverFace && CordMaterials.Shadow != null)
                            verts += Ribbon(CordMaterials.Shadow, s.Pts, ShadowWidth, y - 0.0003f, s.S0, new Vector2(0.03f, -0.045f));
                        verts += Ribbon(s.OverFace && CordMaterials.StrandFace != null ? CordMaterials.StrandFace : CordMaterials.Strand,
                                        s.Pts, StrandWidth, y, s.S0, Vector2.zero);
                        k++;
                    }
                    foreach (CordDecal d in p.Decals)
                    {
                        Material m = CordMaterials.Decal(d.Kind);
                        if (m == null) continue;
                        bool face = CordMaterials.IsFace(d.Kind);
                        float y = face ? faceY + 0.002f : baseY + 0.009f;
                        float aspect = d.Kind == DecalKind.PowerStrip ? 0.5f : 1f;
                        verts += Quad(m, d.Pos, (float)d.Angle, (float)d.Scale, (float)d.Scale * aspect, y);
                    }
                }
            }
            LastPrintedVerts = verts;
            FinalizeMesh(MeshParts.All);
        }

        private void Grow(double x, double z)
        {
            var c = new IntVec3((int)Math.Floor(x), 0, (int)Math.Floor(z));
            if (!bounds.Contains(c)) bounds = bounds.Encapsulate(c);
        }

        /// <summary>A textured ribbon along a polyline; u runs along the cord (the strip tiles every
        /// 4 widths), v across it. Winding matches Printer_Plane.</summary>
        private int Ribbon(Material mat, List<V2> pts, float width, float y, double s0, Vector2 offset)
        {
            if (pts.Count < 2) return 0;
            LayerSubMesh sm = GetSubMesh(mat);
            int start = sm.verts.Count;
            if (start + 2 * pts.Count > MaxMeshVerts) return 0;   // 16-bit index mesh: drop, never corrupt
            float hw = width / 2f;
            double tile = width * 4.0;
            double u = s0 * 4.0;
            for (int i = 0; i < pts.Count; i++)
            {
                Geo.TanNorm(pts, i, out V2 t, out V2 n);
                if (i > 0) u += V2.Dist(pts[i - 1], pts[i]) / tile;
                V2 l = pts[i] + n * hw, r = pts[i] - n * hw;
                sm.verts.Add(new Vector3((float)l.X + offset.x, y, (float)l.Z + offset.y));
                sm.verts.Add(new Vector3((float)r.X + offset.x, y, (float)r.Z + offset.y));
                sm.uvs.Add(new Vector3((float)u, 1f, 0f));
                sm.uvs.Add(new Vector3((float)u, 0f, 0f));
                sm.colors.Add(new Color32(255, 255, 255, 255));
                sm.colors.Add(new Color32(255, 255, 255, 255));
                Grow(pts[i].X, pts[i].Z);
                if (i == 0) continue;
                int a = start + 2 * (i - 1);
                // previous-left, current-left, current-right, previous-right
                sm.tris.Add(a); sm.tris.Add(a + 2); sm.tris.Add(a + 3);
                sm.tris.Add(a); sm.tris.Add(a + 3); sm.tris.Add(a + 1);
            }
            return 2 * pts.Count;
        }

        /// <summary>A decal quad centred on p, its +X (the art's long axis) turned to angle (radians, CCW).</summary>
        private int Quad(Material mat, V2 p, float angle, float sx, float sz, float y)
        {
            LayerSubMesh sm = GetSubMesh(mat);
            int start = sm.verts.Count;
            if (start + 4 > MaxMeshVerts) return 0;
            float ca = Mathf.Cos(angle), sa = Mathf.Sin(angle);
            Vector2[] corners = { new Vector2(-sx, -sz), new Vector2(-sx, sz), new Vector2(sx, sz), new Vector2(sx, -sz) };
            Vector2[] uv = { new Vector2(0, 0), new Vector2(0, 1), new Vector2(1, 1), new Vector2(1, 0) };
            for (int i = 0; i < 4; i++)
            {
                float x = corners[i].x / 2f, z = corners[i].y / 2f;
                float wx = (float)p.X + x * ca - z * sa, wz = (float)p.Z + x * sa + z * ca;
                sm.verts.Add(new Vector3(wx, y, wz));
                sm.uvs.Add(new Vector3(uv[i].x, uv[i].y, 0f));
                sm.colors.Add(new Color32(255, 255, 255, 255));
                Grow(wx, wz);
            }
            sm.tris.Add(start); sm.tris.Add(start + 1); sm.tris.Add(start + 2);
            sm.tris.Add(start); sm.tris.Add(start + 2); sm.tris.Add(start + 3);
            return 4;
        }
    }
}
