using System;
using System.Collections.Generic;
using RimMandrake.GimmeSomeSlack.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
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
        /// <summary>Round 5 (owner 2026-10-04, station 4: "need to make the wires thinner"): 0.11 -> 0.08, shadow 0.17 -> 0.13.</summary>
        public const float StrandWidth = 0.08f;
        public const float ShadowWidth = 0.13f;
        public const float FaceLift = 0.01f;
        public static int LastPrintedVerts;
        /// <summary>Shader-path sway weight scale: vertex alpha = 255 x weight x this x strength (a plant's top carries
        /// 255 x topWindExposure 0.25; a hanging cord tip is a little looser).</summary>
        public const float ShaderAlphaScale = 0.35f;
        /// <summary>State read (probe "motion"): what THIS section printed with the plant shader at its last
        /// Regenerate -- vertices, lifted strands open / roofed, the largest vertex alpha written open / roofed -- and
        /// how many floor strands it left out for the per-frame ripple.</summary>
        public int plantVerts, plantOpenStrands, plantRoofedStrands, alphaMaxOpen, alphaMaxRoofed, rippleSkipped;
        private const int MaxMeshVerts = 65000;
        /// <summary>Ribbons/quads dropped because a sub-mesh hit MaxMeshVerts (cumulative; probe-readable).</summary>
        public static int OverflowDrops;

        public SectionLayer_RM_MessyCords(Section section) : base(section)
        {
            relevantChangeTypes = (ulong)RimWorld.MapMeshFlagDefOf.Buildings | (ulong)RimWorld.MapMeshFlagDefOf.PowerGrid |
                                  (ulong)RimWorld.MapMeshFlagDefOf.Terrain | (ulong)RimWorld.MapMeshFlagDefOf.FogOfWar | (ulong)RimWorld.MapMeshFlagDefOf.Roofs |
                                  (ulong)GimmeSomeSlackDefOf.RM_MessyCords;
            bounds = section.CellRect;
        }

        public override bool Visible => GimmeSomeSlackSettings.enabled;

        /// <summary>Phase 1b B9 (gravship cutscene guard, risk 14): while the cutscene runs the map is not
        /// drawn as a map; the cords stay only in the gravship capture pass, exactly like
        /// SectionLayer_Things (decompiled 1.6: CutsceneInProgress &amp;&amp; !GravshipRenderInProgess hides it).</summary>
        public static bool CutsceneHides => Verse.WorldComponent_GravshipController.CutsceneInProgress &&
                                            !Verse.WorldComponent_GravshipController.GravshipRenderInProgess;

        /// <summary>Phase 1b B8: far zoom shows only the decimated LOD sub-mesh.</summary>
        public static bool FarNow => GimmeSomeSlackSettings.lod && Find.CameraDriver != null &&
                                     Find.CameraDriver.CurrentZoom >= CameraZoomRange.Far;
        public static bool LastDrawFar;
        public static int LastLodSubMeshes, LastFullSubMeshes, CutsceneSkips;
        /// <summary>Lane C state read: pieces printed per strand variant since the last StyleProbe reset.</summary>
        public static readonly Dictionary<int, int> PrintedVariants = new Dictionary<int, int>();
        /// <summary>CORD_STATIC_DYNAMIC_HANDOFF_1 state read: per section (map id + botLeft), the strands ("pieceKey#index")
        /// this layer printed into its static mesh at its LAST regenerate (plain ribbon or shader-sway print). The probe's
        /// strands: command joins it with the per-frame predicates, so a strand drawn by neither path or by both is visible
        /// without a screenshot.</summary>
        public static readonly Dictionary<string, HashSet<string>> PrintedStatic = new Dictionary<string, HashSet<string>>();
        public static string SectionKey(Map map, IntVec3 botLeft) => map.uniqueID + ":" + botLeft.x + "," + botLeft.z;

        public override void DrawLayer()
        {
            if (!Visible) return;
            if (CutsceneHides) { CutsceneSkips++; return; }
            bool far = FarNow;
            LastDrawFar = far;
            for (int i = 0; i < subMeshes.Count; i++)
            {
                LayerSubMesh sm = subMeshes[i];
                bool isLod = CordMaterials.IsLod(sm.material);
                sm.disabled = GimmeSomeSlackSettings.lod ? (isLod ? !far : far) : isLod;
            }
            base.DrawLayer();
        }

        public override CellRect GetBoundaryRect() => bounds;

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            bounds = section.CellRect;
            plantVerts = plantOpenStrands = plantRoofedStrands = alphaMaxOpen = alphaMaxRoofed = rippleSkipped = 0;
            var comp = Map.GetComponent<RM_MapComponent_CordGraph>();
            List<LaidPiece> owned = comp?.PiecesForSection(section.botLeft);
            int verts = 0;
            var printed = new HashSet<string>();
            PrintedStatic[SectionKey(Map, section.botLeft)] = printed;
            if (owned != null && CordMaterials.Strand != null)
            {
                float baseY = AltitudeLayer.Conduits.AltitudeFor();
                // face pieces sit ABOVE the wall/rock sprite: a stub drawn at Building altitude was
                // hidden by the wall (live pass 2). BuildingOnTop is the engine's own layer for things
                // drawn on top of a building (Building_MechCharger, CompRitualFireOverlay).
                float faceY = AltitudeLayer.BuildingOnTop.AltitudeFor() + FaceLift;
                int k = 0;
                bool whip = GimmeSomeSlackSettings.whip && GimmeSomeSlackSettings.breakReadout;
                foreach (LaidPiece p in owned)
                {
                    bool lodDone = false;
                    // stage 2: the piece's material by its run's style and colour / kind (a legacy piece: the default
                    // look's per-net pick, the same Material as before); lane C's per-variant tally keeps its legacy meaning
                    int g = comp.MatIndexOf(p);
                    int variant = comp.VariantOf(p);
                    Material strand = CordMaterials.StrandG(g), strandFace = CordMaterials.StrandFaceG(g),
                             strandLod = CordMaterials.StrandLodG(g);
                    if (strand != null) PrintedVariants[variant] = PrintedVariants.TryGetValue(variant, out int pv) ? pv + 1 : 1;
                    int si = -1;
                    foreach (CordStrand s in p.Strands)
                    {
                        si++;
                        float y = s.OverFace ? faceY : baseY + 0.0006f * (k % 12);
                        // a lifted piece that sways is drawn per frame by the component, not printed
                        if (s.Lifted && RM_MapComponent_CordGraph.SwaysNow(Map, s)) { k++; continue; }
                        // optional shader route: printed ONCE with the CutoutPlant strand, vertex alpha = sway weight
                        // (0 at the pin, 0 everywhere under a roof), uv.z = per-piece phase; the GPU moves it
                        if (RM_MapComponent_CordGraph.ShaderSwayPrints(s))
                        {
                            Material plant = CordMaterials.StrandPlantG(g);
                            if (plant != null)
                            {
                                bool roofed = RM_MapComponent_CordGraph.PinRoofed(Map, s);
                                byte[] alpha = CordMotion.ShaderSwayAlpha(s.SwayW, roofed, ShaderAlphaScale * Mathf.Clamp(GimmeSomeSlackSettings.swayAmplitude, 0f, 2f));
                                float phase = (float)(CordRng.Hash("sway", p.Key) % 1024UL);
                                int n = Ribbon(plant, s.Pts, StrandWidth, y, s.S0, Vector2.zero, alpha, phase);
                                verts += n;
                                plantVerts += n;
                                foreach (byte b in alpha) { if (roofed) alphaMaxRoofed = Math.Max(alphaMaxRoofed, b); else alphaMaxOpen = Math.Max(alphaMaxOpen, b); }
                                if (roofed) plantRoofedStrands++; else plantOpenStrands++;
                                if (n > 0) printed.Add(p.Key + "#" + si);
                                k++;
                                continue;
                            }
                        }
                        // optional floor ripple: an unroofed plain floor strand is drawn per frame by the component
                        bool ripples = RM_MapComponent_CordGraph.RipplesNow(Map, s);
                        if (ripples) rippleSkipped++;
                        List<V2> pts = s.Pts;
                        if (whip && (s.WhipA > 0 || s.WhipB > 0))
                        {
                            int a = Math.Max(0, s.WhipA - 1), b = Math.Min(s.Pts.Count, s.Pts.Count - s.WhipB + 1);
                            pts = b - a >= 2 ? s.Pts.GetRange(a, b - a) : new List<V2>();
                        }
                        if (!s.OverFace && CordMaterials.Shadow != null)
                            verts += Ribbon(CordMaterials.Shadow, pts, ShadowWidth, y - 0.0003f, s.S0, new Vector2(0.03f, -0.045f));
                        // round 5: a random-mix piece is ONE colour node to node (its material index), like any other piece
                        if (!ripples)
                        {
                            int rn = Ribbon(s.OverFace && strandFace != null ? strandFace : strand,
                                            pts, StrandWidth, y, s.S0, Vector2.zero);
                            verts += rn;
                            if (rn > 0) printed.Add(p.Key + "#" + si);
                        }
                        if (GimmeSomeSlackSettings.lod && !lodDone && !s.OverFace && strandLod != null && s.Pts.Count >= 2)
                        {
                            // B8: one strand per piece, every 3rd point, a little thinner, no decals
                            var dec = new List<V2>(s.Pts.Count / 3 + 2);
                            for (int i = 0; i < s.Pts.Count; i += 3) dec.Add(s.Pts[i]);
                            if ((s.Pts.Count - 1) % 3 != 0) dec.Add(s.Pts[s.Pts.Count - 1]);
                            // a mix piece's far-zoom strand is its own single colour too (round 5), so far and near agree
                            verts += Ribbon(strandLod, dec, StrandWidth * 0.9f, baseY, s.S0, Vector2.zero);
                            lodDone = true;
                        }
                        k++;
                    }
                    foreach (CordDecal d in p.Decals)
                    {
                        if (whip && d.OnWhip) continue;          // the live fray rides the whipping tail
                        Material m = CordMaterials.DecalG(d.Kind, g);
                        if (m == null) continue;
                        bool face = CordMaterials.IsFace(d.Kind);
                        float y = face ? faceY + 0.002f : baseY + 0.009f;
                        float aspect = DecalAspect.Of(d.Kind);
                        verts += d.Cropped
                            ? Quad(m, d.Pos, (float)d.Angle, (float)d.ScaleX, (float)d.Scale * aspect, y, (float)d.U0, (float)d.U1, (float)d.V0, (float)d.V1)
                            : Quad(m, d.Pos, (float)d.Angle, (float)d.ScaleX, (float)d.Scale * aspect, y);
                    }
                }
            }
            LastPrintedVerts = verts;
            FinalizeMesh(MeshParts.All);
            int lodN = 0, fullN = 0;
            foreach (LayerSubMesh sm in subMeshes) if (sm.verts.Count > 0) { if (CordMaterials.IsLod(sm.material)) lodN++; else fullN++; }
            LastLodSubMeshes = lodN;
            LastFullSubMeshes = fullN;
        }

        private void Grow(double x, double z)
        {
            var c = new IntVec3((int)Math.Floor(x), 0, (int)Math.Floor(z));
            if (!bounds.Contains(c)) bounds = bounds.Encapsulate(c);
        }

        /// <summary>A textured ribbon along a polyline; u runs along the cord (the strip tiles every
        /// 4 widths), v across it. Winding matches Printer_Plane.</summary>
        /// <summary>The same ribbon written into plain lists (the component's per-frame meshes use it).</summary>
        public static void RibbonInto(List<Vector3> verts, List<Vector2> uvs, List<int> tris, List<V2> pts, float width, float y, double s0)
        {
            if (pts.Count < 2) return;
            int start = verts.Count;
            float hw = width / 2f;
            double tile = width * 4.0, u = s0 * 4.0;
            for (int i = 0; i < pts.Count; i++)
            {
                Geo.TanNorm(pts, i, out V2 t, out V2 n);
                if (i > 0) u += V2.Dist(pts[i - 1], pts[i]) / tile;
                V2 l = pts[i] + n * hw, r = pts[i] - n * hw;
                verts.Add(new Vector3((float)l.X, y, (float)l.Z));
                verts.Add(new Vector3((float)r.X, y, (float)r.Z));
                uvs.Add(new Vector2((float)u, 1f));
                uvs.Add(new Vector2((float)u, 0f));
                if (i == 0) continue;
                int a = start + 2 * (i - 1);
                tris.Add(a); tris.Add(a + 2); tris.Add(a + 3);
                tris.Add(a); tris.Add(a + 3); tris.Add(a + 1);
            }
        }

        private int Ribbon(Material mat, List<V2> pts, float width, float y, double s0, Vector2 offset,
                           byte[] alpha = null, float uvz = 0f)
        {
            if (pts.Count < 2) return 0;
            LayerSubMesh sm = GetSubMesh(mat);
            int start = sm.verts.Count;
            if (start + 2 * pts.Count > MaxMeshVerts) { OverflowDrops++; return 0; }   // 16-bit index mesh: drop, never corrupt (counted: GPT review #15)
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
                sm.uvs.Add(new Vector3((float)u, 1f, uvz));
                sm.uvs.Add(new Vector3((float)u, 0f, uvz));
                byte al = alpha != null && i < alpha.Length ? alpha[i] : (byte)255;
                sm.colors.Add(new Color32(255, 255, 255, al));
                sm.colors.Add(new Color32(255, 255, 255, al));
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
        private int Quad(Material mat, V2 p, float angle, float sx, float sz, float y, float u0 = 0f, float u1 = 1f, float v0 = 0f, float v1 = 1f)
        {
            LayerSubMesh sm = GetSubMesh(mat);
            int start = sm.verts.Count;
            if (start + 4 > MaxMeshVerts) { OverflowDrops++; return 0; }
            float ca = Mathf.Cos(angle), sa = Mathf.Sin(angle);
            Vector2[] corners = { new Vector2(-sx, -sz), new Vector2(-sx, sz), new Vector2(sx, sz), new Vector2(sx, -sz) };
            Vector2[] uv = { new Vector2(u0, v0), new Vector2(u0, v1), new Vector2(u1, v1), new Vector2(u1, v0) };
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
