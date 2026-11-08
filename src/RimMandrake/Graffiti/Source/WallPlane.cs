using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    /// <summary>Prints a mark in the plane of the wall face it is painted on, cut to that face, with the wall's own surface drawn back
    /// over the paint. The polygons come from RM_GraffitiKernel; this adds what needs the game: reading the wall and its atlas.</summary>
    internal static class WallPlane
    {
        private struct Geom { public float crease, side; }

        private static readonly Dictionary<Texture, Geom> Geoms = new Dictionary<Texture, Geom>();
        private static readonly Dictionary<long, Material> ThroughMats = new Dictionary<long, Material>();
        private static readonly Color32 White = new Color32(255, 255, 255, 255);
        private const float TopThrough = 0.45f;
        /// <summary>Option D (owner, 2026-11-07: "bolder paint inside the wall face"). The face is the wall's lit surface: a spray's soft
        /// alpha over it composited pastel, and the wall blended back at full show-through washed it further, so the paint on the face read
        /// as a pale ghost of the paint climbing onto the dark top (live, Ashgate, pass 10). The face takes a second coat of the same paint
        /// and half the show-through; holes in the paint stay holes, so the wall still shows where the can missed.</summary>
        private const float FaceThrough = 0.5f;
        private const int FaceCoats = 2;

        /// <summary>The wall's link bits as its own graphic computes them; negative where no paintable wall stands.</summary>
        internal static int LinksAt(IntVec3 c, Map map)
        {
            if (!GraffitiJobUtility.IsFullWallAt(c, map)) return -1;
            Building wall = c.GetEdifice(map);
            if (!(wall.Graphic is Graphic_Linked linked)) return 0;
            int bits = 0;
            if (linked.ShouldLinkWith(c + IntVec3.North, wall)) bits |= RM_GraffitiKernel.LinkN;
            if (linked.ShouldLinkWith(c + IntVec3.East, wall)) bits |= RM_GraffitiKernel.LinkE;
            if (linked.ShouldLinkWith(c + IntVec3.South, wall)) bits |= RM_GraffitiKernel.LinkS;
            if (linked.ShouldLinkWith(c + IntVec3.West, wall)) bits |= RM_GraffitiKernel.LinkW;
            return bits;
        }

        /// <summary>The colour of the wall's face: its tint on the atlas's near-white face. A middling grey with no wall.</summary>
        internal static Color FaceColor(IntVec3 c, Map map)
        {
            Material atlas = c.InBounds(map) && GraffitiJobUtility.IsFullWallAt(c, map) ? AtlasOf(c, map) : null;
            return atlas == null ? new Color(0.5f, 0.5f, 0.5f) : atlas.color * 0.9f;
        }

        /// <summary>Is there a face of this kind on the wall at c?</summary>
        internal static bool FaceAt(IntVec3 c, Map map, int face)
        {
            return RM_GraffitiKernel.FaceExists(LinksAt(c, map), face);
        }

        /// <summary>The atlas material a wall is drawn from, colour and all. Null for a wall with no atlas.</summary>
        private static Material AtlasOf(IntVec3 c, Map map)
        {
            Building wall = c.GetEdifice(map);
            return wall?.Graphic is Graphic_Linked linked ? linked.SubGraphic?.MatSingleFor(wall) : null;
        }

        /// <summary>Where this wall's crease and side faces fall, read off its atlas once per texture, so a modded wall's mark stops at
        /// that wall's crease. A texture the game won't let us read falls back to the Core measurements.</summary>
        private static Geom GeomOf(Material atlas)
        {
            Texture tex = atlas?.mainTexture;
            if (tex == null) return new Geom { crease = RM_GraffitiKernel.DefaultCrease, side = RM_GraffitiKernel.DefaultSideWidth };
            if (Geoms.TryGetValue(tex, out Geom g)) return g;
            g = new Geom { crease = RM_GraffitiKernel.DefaultCrease, side = RM_GraffitiKernel.DefaultSideWidth };
            try
            {
                Color32[] px = ReadTexture(tex, out int size);
                // Tile 10 (E+W): cap to front, down the middle. Tile 5 (N+S): cap to side, across the middle.
                float[] down = TileProfile(px, size, RM_GraffitiKernel.LinkE | RM_GraffitiKernel.LinkW, vertical: true);
                float[] across = TileProfile(px, size, RM_GraffitiKernel.LinkN | RM_GraffitiKernel.LinkS, vertical: false);
                int n = down.Length;
                int row = RM_GraffitiKernel.CreaseCrossing(down, n / 4, (int)(n * 0.8f), (int)(n * 0.93f));
                int col = RM_GraffitiKernel.CreaseCrossing(across, n / 2, (int)(n * 0.86f), (int)(n * 0.94f));
                if (row >= 0) g.crease = RM_GraffitiKernel.SaneOr(1f - (float)row / n, 0.25f, 0.45f, RM_GraffitiKernel.DefaultCrease);
                if (col >= 0) g.side = RM_GraffitiKernel.SaneOr(1f - (float)col / n, 0.12f, 0.30f, RM_GraffitiKernel.DefaultSideWidth);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[Graffiti] couldn't read wall atlas " + tex.name + ": " + e.Message, tex.GetInstanceID() ^ 0x47524146);
            }
            Geoms[tex] = g;
            return g;
        }

        private static Color32[] ReadTexture(Texture tex, out int size)
        {
            size = tex.width;
            RenderTexture rt = RenderTexture.GetTemporary(size, size, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Default);
            RenderTexture previous = RenderTexture.active;
            try
            {
                Graphics.Blit(tex, rt);
                RenderTexture.active = rt;
                var read = new Texture2D(size, size, TextureFormat.RGBA32, false);
                read.ReadPixels(new Rect(0, 0, size, size), 0, 0);
                read.Apply(false, false);
                Color32[] px = read.GetPixels32();
                UnityEngine.Object.Destroy(read);
                return px;
            }
            finally
            {
                RenderTexture.active = previous;
                RenderTexture.ReleaseTemporary(rt);
            }
        }

        /// <summary>A luminance profile through the engine's window on one atlas tile: north to south, or west to east, the median of
        /// the middle third at each step. Texture rows run bottom up.</summary>
        private static float[] TileProfile(Color32[] px, int size, int links, bool vertical)
        {
            int win = Mathf.RoundToInt(size * 0.1875f);
            int x0 = Mathf.RoundToInt(((links % 4) * 0.25f + 1f / 32f) * size);
            int y0 = Mathf.RoundToInt(((links / 4) * 0.25f + 1f / 32f) * size);
            var profile = new float[win];
            var band = new float[win / 3];
            for (int i = 0; i < win; i++)
            {
                for (int j = 0; j < band.Length; j++)
                {
                    int across = win / 3 + j;
                    int x = vertical ? x0 + across : x0 + i;
                    int y = vertical ? y0 + win - 1 - i : y0 + win - 1 - across;
                    Color32 c = px[y * size + x];
                    band[j] = (c.r + c.g + c.b) / 3f;
                }
                Array.Sort(band);
                profile[i] = band[band.Length / 2];
            }
            return profile;
        }

        /// <summary>The wall's own atlas in its own colour, at `through` opacity, drawn after the paint. Over bare wall it changes nothing
        /// (wall over wall is wall); over paint it brings back the wall's courses, grain and colour, and its light.</summary>
        private static Material ThroughMat(Material atlas, float through, int queue)
        {
            long key = ((long)atlas.GetInstanceID() << 16) ^ (long)(through * 100f) ^ ((long)queue << 8);
            if (ThroughMats.TryGetValue(key, out Material mat) && mat != null) return mat;
            Color c = atlas.color;
            c.a = through;
            mat = MaterialPool.MatFrom(new MaterialRequest((Texture2D)atlas.mainTexture, ShaderDatabase.Mote, c) { renderQueue = queue });
            ThroughMats[key] = mat;
            return mat;
        }

        /// <summary>Where the middle of this mark sits on its wall's plane, so a head or an emblem can be placed against it.</summary>
        internal static float CenterT(Filth_Mark mark, float width, float height, float slope, float lift)
        {
            int face = RM_GraffitiKernel.FaceOfSide(mark.wallSide);
            Geom geom = GeomOf(AtlasOf(mark.Position + new Rot4(mark.wallSide).FacingCell, mark.Map));
            return RM_GraffitiKernel.MarkCenterT(face, geom.crease, geom.side, width, height, slope, lift);
        }

        /// <summary>Print a mark on its wall, on the face and bent over onto the top. width and height are world cells on the wall's plane; through is the wall's show-through.</summary>
        internal static void Print(SectionLayer layer, Filth_Mark mark, Material mat, float width, float height, float slide, float slope, float lift, bool flip, float through, float bump = 0f, float centerT = -1f)
        {
            Map map = mark.Map;
            int side = mark.wallSide;
            int face = RM_GraffitiKernel.FaceOfSide(side);
            IntVec3 anchor = mark.Position + new Rot4(side).FacingCell;
            Material atlas = AtlasOf(anchor, map);
            Geom geom = GeomOf(atlas);
            float y = mark.DrawPos.y + bump;
            if (face == RM_GraffitiKernel.FaceHidden)
            {
                PrintLip(layer, anchor, mat, y);
                return;
            }
            RM_GraffitiKernel.AlongOf(face, out int ax, out int az);
            List<RM_MarkPiece> pieces = RM_GraffitiKernel.MarkPieces(k => LinksAt(anchor + new IntVec3(ax * k, 0, az * k), map), face, geom.crease, geom.side, width, height, slide, slope, lift, flip, centerT);
            foreach (RM_MarkPiece piece in pieces)
            {
                for (int coat = piece.onTop ? 1 : FaceCoats; coat > 0; coat--) Emit(layer.GetSubMesh(mat), piece.poly, anchor.x, anchor.z, y, null);
            }
            if (through <= 0f) return;
            foreach (RM_MarkPiece piece in pieces)
            {
                IntVec3 cell = anchor + new IntVec3(ax * piece.k, 0, az * piece.k);
                Material wallAtlas = AtlasOf(cell, map);
                if (wallAtlas == null) continue;
                int links = LinksAt(cell, map);
                // The top is a dark surface with no grain: less of it comes back, so the paint up there stays the same paint.
                Material over = ThroughMat(wallAtlas, through * (piece.onTop ? TopThrough : FaceThrough), mat.renderQueue + 1);
                Vector2 off = new Vector2((links % 4) * 0.25f + 1f / 32f, (links / 4) * 0.25f + 1f / 32f);
                Emit(layer.GetSubMesh(over), piece.poly, anchor.x, anchor.z, y + 0.002f, v => new Vector2(off.x + (v.x - ax * piece.k) * 0.1875f, off.y + (v.z - az * piece.k) * 0.1875f));
            }
        }

        /// <summary>The far side of a wall can't be seen. An old save's mark there keeps only the paint that caught the cap's far edge.</summary>
        private static void PrintLip(SectionLayer layer, IntVec3 wall, Material mat, float y)
        {
            var lip = new List<RM_PlaneVert>
            {
                new RM_PlaneVert(0.08f, 0.90f, 0.05f, 0.35f),
                new RM_PlaneVert(0.92f, 0.90f, 0.95f, 0.35f),
                new RM_PlaneVert(0.92f, 0.97f, 0.95f, 0.65f),
                new RM_PlaneVert(0.08f, 0.97f, 0.05f, 0.65f),
            };
            Emit(layer.GetSubMesh(mat), lip, wall.x, wall.z, y, null);
        }

        private static void Emit(LayerSubMesh sm, List<RM_PlaneVert> poly, int ox, int oz, float y, Func<RM_PlaneVert, Vector2> uvOf)
        {
            int start = sm.verts.Count;
            foreach (RM_PlaneVert v in poly)
            {
                sm.verts.Add(new Vector3(ox + v.x, y, oz + v.z));
                Vector2 uv = uvOf != null ? uvOf(v) : new Vector2(v.u, v.v);
                sm.uvs.Add(new Vector3(uv.x, uv.y, 0f));
                sm.colors.Add(White);
            }
            // Polygons wind counter-clockwise seen from above; the camera wants clockwise.
            for (int i = 1; i + 1 < poly.Count; i++)
            {
                sm.tris.Add(start);
                sm.tris.Add(start + i + 1);
                sm.tris.Add(start + i);
            }
        }

        // ---------------------------------------------------------------- someone's head, painted

        private static readonly Dictionary<int, Texture2D> Portraits = new Dictionary<int, Texture2D>();

        /// <summary>A colonist's head as a hand would put it on a wall: the game's own portrait, its colours flattened to a few broad values and dragged through
        /// a dry brush. Their hair and their face's shape are what a wall can show, and enough to say who it is. Null if it can't be had.</summary>
        internal static Texture2D PaintedPortrait(Pawn pawn)
        {
            if (pawn == null) return null;
            if (Portraits.TryGetValue(pawn.thingIDNumber, out Texture2D done)) return done;
            Texture2D made = null;
            try
            {
                RenderTexture rt = PortraitsCache.Get(pawn, new Vector2(PortraitPx, PortraitPx), Rot4.South, new Vector3(0f, 0f, 0.3f), 1.28205f, supersample: false, compensateForUIScale: false, healthStateOverride: PawnHealthState.Mobile);
                Color32[] px = ReadTexture(rt, out int size);
                float seed = (pawn.thingIDNumber & 1023) * 0.37f;
                for (int i = 0; i < px.Length; i++)
                {
                    Color32 c = px[i];
                    if (c.a < 40) { px[i] = new Color32(c.r, c.g, c.b, 0); continue; }
                    int x = i % size, y = i / size;
                    float lum = (c.r + c.g + c.b) / 765f;
                    float band = Mathf.Round(lum * 3.4f) / 3.4f / Mathf.Max(lum, 0.08f);
                    float streak = Mathf.PerlinNoise(seed + x * 0.012f, seed + y * 0.34f);
                    float patch = Mathf.PerlinNoise(seed * 2f + x * 0.045f, seed + y * 0.05f);
                    float keep = Mathf.Clamp01((streak + patch * 0.8f - 0.5f) / 0.3f);
                    float grey = (c.r + c.g + c.b) / 3f;
                    px[i] = new Color32(
                        (byte)Mathf.Clamp((grey + (c.r - grey) * 1.15f) * band * 0.92f, 0f, 255f),
                        (byte)Mathf.Clamp((grey + (c.g - grey) * 1.15f) * band * 0.92f, 0f, 255f),
                        (byte)Mathf.Clamp((grey + (c.b - grey) * 1.15f) * band * 0.92f, 0f, 255f),
                        (byte)(255f * (0.55f + 0.45f * keep)));
                }
                made = new Texture2D(size, size, TextureFormat.RGBA32, true) { name = "RM_Graffiti_Portrait_" + pawn.thingIDNumber, filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp };
                made.SetPixels32(px);
                made.Apply(true, false);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[Graffiti] couldn't paint a portrait of " + pawn.LabelShort + ": " + e.Message, pawn.thingIDNumber ^ 0x48454144);
            }
            Portraits[pawn.thingIDNumber] = made;
            return made;
        }

        private const int PortraitPx = 128;

        // ---------------------------------------------------------------- a clean ideoligion icon, painted

        private static readonly Dictionary<Texture, Texture2D> Painted = new Dictionary<Texture, Texture2D>();

        /// <summary>The game's ideoligion icons are crisp vectors with soft UI shading (a blind judge saw "a shaded grey-white dome, rendered
        /// and dropped in"). Here each is cut like a stencil and dragged through a dry brush: its shading goes to two flat tones of one
        /// paint, its strokes keep their shape, its coverage goes streaky and patched like everything else on a wall. Null if unreadable.</summary>
        internal static Texture2D PaintedIcon(Texture2D icon)
        {
            if (icon == null) return null;
            if (Painted.TryGetValue(icon, out Texture2D done)) return done;
            Texture2D made = null;
            try
            {
                Color32[] px = ReadTexture(icon, out int size);
                made = new Texture2D(size, size, TextureFormat.RGBA32, true) { name = icon.name + "_painted", filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp };
                float seed = (icon.GetInstanceID() & 1023) * 0.37f;
                float scale = 128f / size;
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        Color32 c = px[y * size + x];
                        // Two tones, never a gradient: the light of the icon is the paint's full colour, its shade the same paint thinned.
                        float lum = (c.r + c.g + c.b) / 765f;
                        byte tone = (byte)(lum > 0.55f ? 255 : 150);
                        c.r = c.g = c.b = tone;
                        c.a = (byte)(c.a > 110 ? 255 : (c.a > 40 ? 120 : 0));
                        float streak = Mathf.PerlinNoise(seed + x * scale * 0.012f, seed + y * scale * 0.34f);
                        float patch = Mathf.PerlinNoise(seed * 2f + x * scale * 0.045f, seed + y * scale * 0.05f);
                        float grit = Mathf.PerlinNoise(seed + x * scale * 0.6f, seed * 3f + y * scale * 0.6f);
                        float keep = Mathf.Clamp01((streak + patch * 0.8f - 0.62f) / 0.28f) * Mathf.Clamp01((grit + 0.35f) / 0.6f);
                        c.a = (byte)(c.a * (0.22f + 0.78f * keep));
                        px[y * size + x] = c;
                    }
                }
                made.SetPixels32(px);
                made.Apply(true, false);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[Graffiti] couldn't paint icon " + icon.name + ": " + e.Message, icon.GetInstanceID() ^ 0x49434f4e);
            }
            Painted[icon] = made;
            return made;
        }
    }
}
