using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// Loose ash drawn as ground cover, the way a terrain lies over its neighbour. Eight redraws of the loose-ash filth as sprites
    /// (Graphic_Cluster blobs, 1.25-1.6 cells) all read at play zoom as smoke puffs, cotton or stickers on the ground (owner
    /// 2026-11-07: "blurry grey stuff ... looks low-res and ugly"; map x day 3, first_look_8, eight cuts in). Tried live on map x
    /// (shots/cover1, cover2, t1-t16): vanilla's snow path (half-cell vertices, Custom/Snow with its cloudy macro texture) lays
    /// each clump as a soft fog cloud; what reads as ash is a pale sheet with a frayed, gritty margin, as a terrain edge is drawn.
    /// Its texture is the deep-ash terrain's own, lifted pale (ash_cover_gen.py): both map by world position, so the drift lies in
    /// the ground's own ripples. Pass 20's flat powder read as fog, snow or concrete to two blind readers; this one as "grey sand
    /// or fine gravel ... ash or grey dust drifted by wind", crisp (pass 21, map x, shots p21c0_base against p21r1).
    /// So: a mesh of 4x4 quads a cell, each vertex's alpha from the bilinear field of the cells holding ash, cut at its 0.5
    /// contour after an edge noise bends it (so clumps do not keep the cell grid's straight sides), drawn with the terrain
    /// fade-rough shader, whose edge texture (RM_FE_AshCoverEdge) frays the margin. The depth of each cell comes from its
    /// loose-ash filth thickness, so every mechanic stays the filth's (fire and ash fall lay it, rain washes it, it expires,
    /// colonists sweep it indoors) and only the look changes. The filth's own sprite prints nothing (Graphic_RM_AshCoverHidden);
    /// its spawn, thickening and removal already dirty the Things mesh of its section and the adjacent ones, which rebuilds this.
    /// </summary>
    [StaticConstructorOnStartup]
    public class SectionLayer_PyrelandsAsh : SectionLayer
    {
        private const string TexPath = "Things/Filth/RM_FE_AshCover";
        private const string EdgeTexPath = "Things/Filth/RM_FE_AshCoverEdge";
        // 2026-11-08, owner on map x ("the black soil of the initial map was very cool ... all the ash's should be darker, and wet ash
        // should be downright blackened"): dry loose ash was a 0.70 tint (~117 grey on the 47 grey ground), now 0.48 (~80); loose ash
        // where the ground is watered is 0.30 (~50), and the watered ground itself is the deep-ash terrain's own texture at 0.40 (~20).
        private static readonly Color Tint = new Color(0.48f, 0.48f, 0.48f, 1f);
        private static readonly Color WetTint = new Color(0.30f, 0.30f, 0.30f, 1f);
        private static readonly Color WetGroundTint = new Color(0.40f, 0.40f, 0.40f, 1f);
        private const string GroundTexPath = "Terrain/Surfaces/RM_FE_Ash_Deep";
        // Alpha for thickness 1..4: below 1 the rough shader opens grit-sized holes, so a thin drift shows a little char.
        private static readonly float[] DepthAlpha = { 0f, 0.9f, 1f, 1f, 1f };

        // Fine quads per cell side: a 16 px step at play zoom, where vanilla's half-cell vertex grid fades over a whole cell.
        private const int Sub = 4;
        // Half-width of the alpha ramp around the contour; the rough shader turns the ramp into the frayed edge (0.3 read as fog).
        private const float EdgeBand = 0.15f;
        // Edge noise on the fine lattice, wrapping every NoiseSide vertices (24 cells): a 3-cell octave bends the clump, a
        // 0.75-cell one frays it. Spacings must divide NoiseSide.
        private const int NoiseSide = 96;
        private const int Spacing1 = 12, Spacing2 = 3;
        private const float Amp1 = 0.6f, Amp2 = 0.15f;
        private static float[] noise;
        private static Material mat, matWet, matGround;

        // The section's ash thickness with one ring of neighbours, and the last one built (rebuild only on a change).
        private int[] thick, lastThick;
        private float[] alphas;

        public SectionLayer_PyrelandsAsh(Section section) : base(section)
        {
            relevantChangeTypes = MapMeshFlagDefOf.Things;
        }

        public override bool Visible => true;

        private static Material MakeMat(string name, string tex, Color tint, int queue)
        {
            var m = new Material(ShaderDatabase.TerrainFadeRough) { name = name };
            m.mainTexture = ContentFinder<Texture2D>.Get(tex);
            Texture2D edge = ContentFinder<Texture2D>.Get(EdgeTexPath, false);
            m.SetTexture("_AlphaAddTex", edge != null ? (Texture)edge : MatBases.Snow.GetTexture("_AlphaAddTex"));
            m.color = tint;
            // Over every terrain (2000 + renderPrecedence), beside vanilla's snow; wet ground under the drifts.
            m.renderQueue = queue;
            return m;
        }

        private static Material Mat => mat ?? (mat = MakeMat("RM_PyrelandsAshCover", TexPath, Tint, 2401));
        private static Material MatWet => matWet ?? (matWet = MakeMat("RM_PyrelandsAshCoverWet", TexPath, WetTint, 2402));
        private static Material MatGround => matGround ?? (matGround = MakeMat("RM_PyrelandsAshWetGround", GroundTexPath, WetGroundTint, 2400));

        // Per cell in the ring: ash thickness 0..4, plus WetBit where the ground is watered ash terrain.
        private const int WetBit = 8;

        public override void Regenerate()
        {
            ThingDef ash = PyrelandsDriftField.AshDef;
            LayerSubMesh smDry = GetSubMesh(Mat), smWet = GetSubMesh(MatWet), smGround = GetSubMesh(MatGround);
            int now = Find.TickManager.TicksGame;
            MapComponent_PyrelandsAshField field = MapComponent_PyrelandsAshField.For(Map);
            bool mayBeWet = field != null && field.MayBeWet(now);
            bool hasAsh = ash != null && Map.listerThings.ThingsOfDef(ash).Count > 0;
            if (!hasAsh && !mayBeWet)
            {
                lastThick = null;
                smDry.Clear(MeshParts.All); smDry.disabled = true;
                smWet.Clear(MeshParts.All); smWet.disabled = true;
                smGround.Clear(MeshParts.All); smGround.disabled = true;
                return;
            }
            CellRect rect = section.CellRect;
            int bw = rect.Width + 2, bh = rect.Height + 2;
            int ox = rect.minX - 1, oz = rect.minZ - 1;
            if (thick == null || thick.Length != bw * bh) thick = new int[bw * bh];
            for (int i = 0; i < bw; i++)
            {
                for (int j = 0; j < bh; j++)
                {
                    IntVec3 c = new IntVec3(Mathf.Clamp(ox + i, 0, Map.Size.x - 1), 0, Mathf.Clamp(oz + j, 0, Map.Size.z - 1));
                    int t = hasAsh ? Mathf.Clamp(PyrelandsDriftField.Thickness(Map, c), 0, 4) : 0;
                    if (mayBeWet && field.IsWetAshGround(c, now)) t |= WetBit;
                    thick[i * bh + j] = t;
                }
            }
            // Plants growing, fires and items dirty the same Things flag far more often than ash changes: rebuild only on a change.
            if (lastThick != null && lastThick.Length == thick.Length && SameAs(lastThick, thick)) return;
            if (lastThick == null || lastThick.Length != thick.Length) lastThick = new int[thick.Length];
            Array.Copy(thick, lastThick, thick.Length);
            if (dry == null || dry.Length != thick.Length) { dry = new int[thick.Length]; wet = new int[thick.Length]; ground = new int[thick.Length]; }
            for (int k = 0; k < thick.Length; k++)
            {
                int t = thick[k] & 7;
                bool w = (thick[k] & WetBit) != 0;
                dry[k] = w ? 0 : t;
                wet[k] = w ? t : 0;
                ground[k] = w ? 4 : 0;
            }
            Build(smGround, ground, rect, ox, oz, bh);
            Build(smDry, dry, rect, ox, oz, bh);
            Build(smWet, wet, rect, ox, oz, bh);
        }

        private int[] dry, wet, ground;

        private void Build(LayerSubMesh sm, int[] cells, CellRect rect, int ox, int oz, int bh)
        {
            sm.Clear(MeshParts.All);
            bool any = false;
            for (int k = 0; k < cells.Length; k++)
            {
                if (cells[k] > 0) { any = true; break; }
            }
            if (!any)
            {
                sm.disabled = true;
                return;
            }
            float y = AltitudeLayer.Terrain.AltitudeFor();
            int vw = rect.Width * Sub + 1, vh = rect.Height * Sub + 1;
            if (alphas == null || alphas.Length < vw * vh) alphas = new float[vw * vh];
            for (int a = 0; a < vw; a++)
            {
                for (int b = 0; b < vh; b++)
                {
                    float wx = rect.minX + (float)a / Sub, wz = rect.minZ + (float)b / Sub;
                    float alpha = AlphaAt(cells, bh, wx - 0.5f - ox, wz - 0.5f - oz, rect.minX * Sub + a, rect.minZ * Sub + b);
                    alphas[a * vh + b] = alpha;
                    sm.verts.Add(new Vector3(wx, y, wz));
                    sm.colors.Add(new Color32(255, 255, 255, (byte)(alpha * 255f)));
                }
            }
            for (int a = 0; a < vw - 1; a++)
            {
                for (int b = 0; b < vh - 1; b++)
                {
                    int v00 = a * vh + b, v01 = v00 + 1, v10 = v00 + vh, v11 = v10 + 1;
                    if (alphas[v00] <= 0f && alphas[v01] <= 0f && alphas[v10] <= 0f && alphas[v11] <= 0f) continue;
                    sm.tris.Add(v00); sm.tris.Add(v01); sm.tris.Add(v11);
                    sm.tris.Add(v00); sm.tris.Add(v11); sm.tris.Add(v10);
                }
            }
            if (sm.tris.Count == 0)
            {
                sm.Clear(MeshParts.All);
                sm.disabled = true;
                return;
            }
            sm.disabled = false;
            sm.FinalizeMesh(MeshParts.All);
        }

        private static bool SameAs(int[] a, int[] b)
        {
            for (int i = 0; i < a.Length; i++)
            {
                if (a[i] != b[i]) return false;
            }
            return true;
        }

        /// <summary>The cover's alpha at a fine vertex. (u, v) is the vertex in block cell-centre space. Where ash lies is the 0.5
        /// contour of the bilinear presence field, pushed in and out by the edge noise; inside, opacity follows thickness,
        /// averaged over the ash cells only so a patch does not thin towards its rim.</summary>
        private static float AlphaAt(int[] thick, int bh, float u, float v, int fx, int fz)
        {
            int i0 = Mathf.FloorToInt(u), j0 = Mathf.FloorToInt(v);
            float fu = u - i0, fv = v - j0;
            float pres = 0f, op = 0f;
            for (int di = 0; di < 2; di++)
            {
                for (int dj = 0; dj < 2; dj++)
                {
                    float w = (di == 0 ? 1f - fu : fu) * (dj == 0 ? 1f - fv : fv);
                    int t = thick[(i0 + di) * bh + (j0 + dj)];
                    if (t <= 0) continue;
                    pres += w;
                    op += w * DepthAlpha[t];
                }
            }
            if (pres <= 0f) return 0f;
            float cover = Mathf.Clamp01((pres + EdgeNoise(fx, fz) - 0.5f + EdgeBand) / (2f * EdgeBand));
            return cover * op / pres;
        }

        private static float EdgeNoise(int fx, int fz)
        {
            if (noise == null) noise = BuildNoise();
            int x = ((fx % NoiseSide) + NoiseSide) % NoiseSide, z = ((fz % NoiseSide) + NoiseSide) % NoiseSide;
            return noise[x * NoiseSide + z];
        }

        /// <summary>A wrapping table of value noise on the fine-vertex lattice. Fixed seed: the same ash always has the same edge.</summary>
        private static float[] BuildNoise()
        {
            var rng = new System.Random(4127);
            var table = new float[NoiseSide * NoiseSide];
            AddOctave(table, rng, Spacing1, Amp1);
            AddOctave(table, rng, Spacing2, Amp2);
            return table;
        }

        private static void AddOctave(float[] table, System.Random rng, int spacing, float amp)
        {
            int n = NoiseSide / spacing;
            var lattice = new float[n * n];
            for (int i = 0; i < lattice.Length; i++) lattice[i] = (float)rng.NextDouble() * 2f - 1f;
            for (int x = 0; x < NoiseSide; x++)
            {
                for (int z = 0; z < NoiseSide; z++)
                {
                    int lx = x / spacing, lz = z / spacing;
                    float fx = Smooth((x % spacing) / (float)spacing), fz = Smooth((z % spacing) / (float)spacing);
                    float a = lattice[lx * n + lz], b = lattice[((lx + 1) % n) * n + lz];
                    float c = lattice[lx * n + (lz + 1) % n], d = lattice[((lx + 1) % n) * n + (lz + 1) % n];
                    table[x * NoiseSide + z] += amp * Mathf.Lerp(Mathf.Lerp(a, b, fx), Mathf.Lerp(c, d, fx), fz);
                }
            }
        }

        private static float Smooth(float t) => t * t * (3f - 2f * t);
    }

    /// <summary>The loose-ash filth's graphic: the inspect icon only. The ground cover (SectionLayer_PyrelandsAsh) draws the ash.</summary>
    public class Graphic_RM_AshCoverHidden : Graphic_Single
    {
        public override void Print(SectionLayer layer, Thing thing, float extraRotation)
        {
        }
    }
}
