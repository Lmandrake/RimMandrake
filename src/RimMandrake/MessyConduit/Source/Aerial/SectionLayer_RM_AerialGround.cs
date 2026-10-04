using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// The aerial lines' static ground layer (design 2.5, 2.6): per section, for every anchor standing in it,
    ///  * the soft cast SHADOW of each UP span it owns (AerialMath.SpanShadow: offset by the wire's height, swinging in
    ///    under the sag; wide and faint, B24) -- what makes a span read as overhead rather than as a cord on the floor;
    ///  * the frayed end (live / dead art) at the break of every FALLEN wire (a span whose far anchor died, or a cut
    ///    half). The wire itself is ONE per-frame cable from the insulator to that break (RM_MapComponent_Aerial, B21).
    /// The span itself is drawn per frame from a cached mesh (RM_MapComponent_Aerial) so it can sway; this layer costs
    /// nothing per frame. GetBoundaryRect grows to the printed extent so long shadows/cords stay drawn.
    /// </summary>
    public class SectionLayer_RM_AerialGround : SectionLayer
    {
        private CellRect bounds;
        public static int LastPrintedVerts, LastFallenPrinted, LastShadowsPrinted;
        /// <summary>Wide and faint (B24): a soft shadow band under the wires, not a line that reads as a cable.</summary>
        public const float ShadowWidth = 0.42f;

        public SectionLayer_RM_AerialGround(Section section) : base(section)
        {
            relevantChangeTypes = (ulong)AerialDefOf.RM_AerialLines | (ulong)RimWorld.MapMeshFlagDefOf.Buildings;
            bounds = section.CellRect;
        }

        public override bool Visible => AerialSettings.enabled;

        public override CellRect GetBoundaryRect() => bounds;

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            bounds = section.CellRect;
            RM_MapComponent_Aerial comp = Map.GetComponent<RM_MapComponent_Aerial>();
            int verts = 0, fallenN = 0, shadowN = 0;
            if (comp != null)
            {
                float shadowY = AltitudeLayer.Shadows.AltitudeFor();
                float cordY = AltitudeLayer.Conduits.AltitudeFor() + 0.004f;
                foreach (CompAerialAnchor a in comp.Anchors)
                {
                    if (!section.CellRect.Contains(a.Position)) continue;
                    if (AerialMaterials.Shadow != null)
                        foreach (SpanLink l in a.links)
                        {
                            if (l.state != SpanState.Up || l.other == null || !l.other.Spawned || !AerialMath.Owns(a.thingIDNumber, l.other.thingIDNumber)) continue;
                            Vector3 pa = a.BasePoint, pb = l.other.BasePoint;
                            // B24: a soft cast shadow that follows the sag, never a straight wire-like line on the ground
                            List<P2> sh = AerialMath.SpanShadow(new P2(pa.x, pa.z), new P2(pb.x, pb.z), a.Ext.attachZ, l.other.Ext.attachZ, AerialSettings.sag);
                            verts += Ribbon(AerialMaterials.Shadow, sh, ShadowWidth, shadowY);
                            shadowN++;
                        }
                    if (a.fallen.Count == 0) continue;
                    bool live = comp.FallenLiveCached(a) ?? comp.AnchorLive(a);
                    foreach (FallenCord f in a.fallen)
                    {
                        // round 3: every wire of the broken span lies here; each gets its own frayed end
                        foreach (FallenLay lay in comp.Lays(a, f))
                        {
                            if (lay.Pts.Count < 2) continue;      // the wire itself is drawn per frame (one piece, B21); only its frayed end here
                            Material fray = live ? AerialMaterials.FrayLive : AerialMaterials.FrayDead;
                            if (fray != null)
                            {
                                P2 p0 = lay.Pts[lay.Pts.Count - 2], p1 = lay.Tip;
                                verts += Quad(fray, p1, (float)Math.Atan2(p1.Z - p0.Z, p1.X - p0.X), 0.55f, 0.55f, cordY + 0.002f);
                            }
                        }
                        fallenN++;
                    }
                }
            }
            LastPrintedVerts = verts;
            LastFallenPrinted = fallenN;
            LastShadowsPrinted = shadowN;
            FinalizeMesh(MeshParts.All);
        }

        private void Grow(double x, double z)
        {
            var c = new IntVec3((int)Math.Floor(x), 0, (int)Math.Floor(z));
            if (!bounds.Contains(c)) bounds = bounds.Encapsulate(c);
        }

        private int Ribbon(Material mat, List<P2> pts, float width, float y)
        {
            if (pts.Count < 2) return 0;
            LayerSubMesh sm = GetSubMesh(mat);
            int start = sm.verts.Count;
            if (start + 2 * pts.Count > 65000) return 0;
            double u = 0;
            for (int i = 0; i < pts.Count; i++)
            {
                P2 prev = i > 0 ? pts[i - 1] : pts[i], next = i < pts.Count - 1 ? pts[i + 1] : pts[i];
                double tx = next.X - prev.X, tz = next.Z - prev.Z, tl = Math.Sqrt(tx * tx + tz * tz);
                if (tl < 1e-9) { tx = 1; tz = 0; tl = 1; }
                double nx = -tz / tl * width / 2, nz = tx / tl * width / 2;
                if (i > 0) u += P2.Dist(pts[i - 1], pts[i]) / (width * 4);
                sm.verts.Add(new Vector3((float)(pts[i].X + nx), y, (float)(pts[i].Z + nz)));
                sm.verts.Add(new Vector3((float)(pts[i].X - nx), y, (float)(pts[i].Z - nz)));
                sm.uvs.Add(new Vector3((float)u, 1f, 0f));
                sm.uvs.Add(new Vector3((float)u, 0f, 0f));
                sm.colors.Add(new Color32(255, 255, 255, 255));
                sm.colors.Add(new Color32(255, 255, 255, 255));
                Grow(pts[i].X, pts[i].Z);
                if (i == 0) continue;
                int a = start + 2 * (i - 1);
                sm.tris.Add(a); sm.tris.Add(a + 2); sm.tris.Add(a + 3);
                sm.tris.Add(a); sm.tris.Add(a + 3); sm.tris.Add(a + 1);
            }
            return 2 * pts.Count;
        }

        private int Quad(Material mat, P2 p, float angle, float sx, float sz, float y)
        {
            LayerSubMesh sm = GetSubMesh(mat);
            int start = sm.verts.Count;
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
