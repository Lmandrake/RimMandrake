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

        /// <summary>Any texture's pixels, whatever its shape, rows bottom up.</summary>
        private static Color32[] ReadTexture(Texture tex, out int w, out int h)
        {
            w = tex.width;
            h = tex.height;
            RenderTexture rt = RenderTexture.GetTemporary(w, h, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Default);
            RenderTexture previous = RenderTexture.active;
            try
            {
                Graphics.Blit(tex, rt);
                RenderTexture.active = rt;
                var read = new Texture2D(w, h, TextureFormat.RGBA32, false);
                read.ReadPixels(new Rect(0, 0, w, h), 0, 0);
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

        // ---------------------------------------------------------------- weathered paint

        private static readonly Dictionary<long, Texture2D> WeatheredTex = new Dictionary<long, Texture2D>();

        /// <summary>How far the weather has eaten in at each step (RM_GraffitiKernel.WeatherStep, 1..4): the share of the noise field gone.</summary>
        /// Pass 16: eats less at each step (a blind judge read W3 and W4's faint remains as rust, grime, ash and dry grass); what's left stays paint.
        /// Pass 17: less again, so even at W4 two thirds of every stroke is there and its ends and joins still say a hand made it.
        private static readonly float[] Eaten = { 0f, 0.15f, 0.28f, 0.42f, 0.55f };
        private static readonly float[] EatenClean = { 0f, 0.09f, 0.17f, 0.25f, 0.33f };

        /// <summary>What paint soaks into a wall and keeps even where the weather has taken the coat, at each step: a share of the
        /// drawing's own opacity. Live pass 14, a blind judge on Ashgate's day-18 walls: flaked marks with nothing between the flakes
        /// read as "spilled debris", "mould", "a soot stain". With the whole shape still faintly there, it reads as an old mark.</summary>
        /// Pass 16: the stain was a thin film of the paint's own colour, and a thin dark film on a wall is grime; it's now bleached (below) and kept stronger.
        private static readonly float[] Stain = { 1f, 0.45f, 0.40f, 0.35f, 0.30f };

        /// <summary>How far the sun has chalked what's left of the coat at each step, toward white in its own hue: real old paint goes paler,
        /// grime goes darker. Live pass 15 (blind judge): greyed toward the wall's middle value, W2-W4 read as "rust or a burn", "grime or ash",
        /// "dry grass". Where only the stain is left it is chalked further (StainBleach), so the ghost of a shape is pale, not a smudge.</summary>
        internal static float BleachPerStep => RM_GraffitiStage.oldWeather ? 0.07f : 0.045f;
        private const float StainBleach = 0.5f;

        /// <summary>Paint as the weather leaves it. Live pass 13: a mark late in its life read as faint new paint, a pale ghost, because the
        /// fade only thinned it. Old paint goes in patches: blotches flake off, rain runs wash it in vertical streaks, and the edges of
        /// what's left are ragged with grit; what stays is chalkier. The same noise field at every step, eaten further each time, so a mark
        /// wears the way it began to. Four fields per texture (by mark id), so two weathered stamps of one drawing don't wear alike.</summary>
        /// Pass 17 (GPT's lead, after pass 16's blind judge read every faint mark as a stain: "the weak ones read as stains, not as clumsy paint"):
        /// a stain keeps a mark's area and loses its strokes. Now the weather takes whole pieces out with clean edges, mostly in rain's vertical runs
        /// and the grit's small chips, and leaves nothing between them; what stays is the full coat, a little chalkier. RM_GraffitiStage.oldWeather
        /// draws the pass-16 way, for a side-by-side.
        internal static Texture2D Weathered(Texture tex, int step, int id)
        {
            if (tex == null || step <= 0) return null;
            step = Math.Min(step, Eaten.Length - 1);
            bool old = RM_GraffitiStage.oldWeather;
            long key = ((long)tex.GetInstanceID() << 8) | ((long)step << 4) | (long)(id & 3) | (old ? 1L << 3 : 0L);
            if (WeatheredTex.TryGetValue(key, out Texture2D done)) return done;
            Texture2D made = null;
            try
            {
                Color32[] px = ReadTexture(tex, out int w, out int h);
                float seed = 17.3f + (id & 3) * 41.7f;
                float[] n = new float[px.Length];
                var sample = new List<float>();
                for (int y = 0; y < h; y++)
                {
                    for (int x = 0; x < w; x++)
                    {
                        float u = x / (float)h, v = y / (float)h;
                        float blot = Mathf.PerlinNoise(seed + u * 3f, seed + v * 3f);
                        float rag = Mathf.PerlinNoise(seed * 1.3f + u * 13f, seed + v * 13f);
                        float streak = Mathf.PerlinNoise(seed * 1.7f + u * 26f, seed + v * 2.2f);
                        float grit = Mathf.PerlinNoise(seed * 2.1f + u * 70f, seed + v * 70f);
                        int i = y * w + x;
                        n[i] = old ? 0.4f * blot + 0.2f * rag + 0.2f * streak + 0.2f * grit : 0.2f * blot + 0.2f * rag + 0.35f * streak + 0.25f * grit;
                        if (px[i].a > 40 && (i % 7) == 0) sample.Add(n[i]);
                    }
                }
                // Spread the field over 0..1 by the paint it actually covers, so a step eats the same share of every drawing.
                sample.Sort();
                float lo = sample.Count > 20 ? sample[sample.Count / 20] : 0.3f, hi = sample.Count > 20 ? sample[sample.Count * 19 / 20] : 0.7f;
                float span = Mathf.Max(hi - lo, 0.05f), t = old ? Eaten[step] : EatenClean[step];
                for (int i = 0; i < px.Length; i++)
                {
                    Color32 c = px[i];
                    if (c.a == 0) continue;
                    float m = Mathf.Clamp01((n[i] - lo) / span);
                    float coat, keep, bleach;
                    if (old)
                    {
                        coat = Mathf.Clamp01((m - t) / 0.04f + 0.5f) * (0.45f + 0.55f * Mathf.Clamp01((m - t - 0.06f) / 0.12f));
                        keep = Mathf.Max(Stain[step], coat);
                        bleach = BleachPerStep * step + (1f - coat) * StainBleach;
                    }
                    else
                    {
                        // A clean edge a pixel or two wide, so a chip mips to a gap at play zoom, not to a thinner film.
                        keep = Mathf.Clamp01((m - t) / 0.025f + 0.5f);
                        bleach = BleachPerStep * step;
                    }
                    px[i] = new Color32((byte)(c.r + (255 - c.r) * bleach), (byte)(c.g + (255 - c.g) * bleach), (byte)(c.b + (255 - c.b) * bleach), (byte)(c.a * keep));
                }
                made = new Texture2D(w, h, TextureFormat.RGBA32, true) { name = tex.name + "_weathered" + step, filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp };
                made.SetPixels32(px);
                made.Apply(true, false);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[Graffiti] couldn't weather " + tex.name + ": " + e.Message, tex.GetInstanceID() ^ 0x57454154);
            }
            WeatheredTex[key] = made;
            return made;
        }

        private static readonly Dictionary<long, Texture2D> DrippedTex = new Dictionary<long, Texture2D>();

        /// <summary>A clumsy hand's paint, as it runs: too much on the can or the brush, so it pools at the low edge of a stroke and runs straight
        /// down the wall in full-strength drips, each with a bead at its end, and stalls into a few fat blobs. Live pass 16, a blind judge: a poor
        /// hand shown by a thin, washed coat read as "stains, not clumsy paint". A run is the surest sign a wall has paint on it; a lot of runs is
        /// a hand that couldn't control it. load: 0 none, 1 an awful hand. The runs stay inside the drawing's canvas. Null if unreadable.</summary>
        internal static Texture2D Dripped(Texture tex, float load, int id)
        {
            if (tex == null || load <= 0f) return null;
            long key = ((long)tex.GetInstanceID() << 8) | ((long)(load * 8f) << 2) | (long)(id & 3);
            if (DrippedTex.TryGetValue(key, out Texture2D done)) return done;
            Texture2D made = null;
            try
            {
                Color32[] px = ReadTexture(tex, out int w, out int h);
                var outPx = (Color32[])px.Clone();
                uint r = (uint)(id & 3) * 2654435761u + (uint)tex.GetInstanceID() * 40503u + 977u;
                float Rnd() { r = r * 1664525u + 1013904223u; return (r >> 8) / 16777216f; }
                int cell = h;    // texture pixels per world cell of height (art is baked 256 px to the cell)
                int dripW = Math.Max(3, cell / 40);
                // Columns at random, a stroke's lowest edge in each: a drip starts where paint sits on bare wall.
                int tries = (int)(w / (float)dripW * 0.55f * load);
                for (int k = 0; k < tries; k++)
                {
                    int x = (int)(Rnd() * (w - dripW));
                    // Rows run bottom up: walk down from the top, find the lowest solid pixel above an open gap.
                    for (int y = h - 2; y > 2; y--)
                    {
                        int i = y * w + x;
                        if (px[i].a < 200 || px[i - w].a > 40) continue;
                        if (Rnd() > 0.5f) continue;
                        Color32 c = px[i];
                        c.a = 255;
                        int len = (int)(cell * (0.06f + 0.30f * load * Rnd()));
                        int width = dripW + (Rnd() < 0.3f ? dripW / 2 : 0);
                        for (int d = 1; d <= len && y - d >= 0; d++)
                        {
                            // Thins as it runs, then a bead where it stopped.
                            float taper = 1f - 0.45f * d / len;
                            int ww = Math.Max(2, (int)(width * taper));
                            if (d > len - width) ww = width + 1;
                            for (int dx = 0; dx < ww && x + dx < w; dx++)
                            {
                                int j = (y - d) * w + x + dx;
                                if (outPx[j].a < 230) outPx[j] = c;
                            }
                        }
                        break;
                    }
                }
                // Where the can stalled: a fat blob on a stroke or two.
                int blobs = load >= 1f ? 3 : (load > 0f ? 1 : 0);
                for (int b = 0, guard = 0; b < blobs && guard < 400; guard++)
                {
                    int x = (int)(Rnd() * w), y = (int)(Rnd() * h);
                    if (px[y * w + x].a < 220) continue;
                    Color32 c = px[y * w + x];
                    c.a = 255;
                    int rad = (int)(cell * (0.035f + 0.02f * Rnd()));
                    for (int dy = -rad; dy <= rad; dy++)
                    {
                        for (int dx = -rad; dx <= rad; dx++)
                        {
                            int xx = x + dx, yy = y + dy;
                            if (xx < 0 || yy < 0 || xx >= w || yy >= h || dx * dx + dy * dy > rad * rad) continue;
                            outPx[yy * w + xx] = c;
                        }
                    }
                    b++;
                }
                made = new Texture2D(w, h, TextureFormat.RGBA32, true) { name = tex.name + "_dripped", filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp };
                made.SetPixels32(outPx);
                made.Apply(true, false);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[Graffiti] couldn't run paint on " + tex.name + ": " + e.Message, tex.GetInstanceID() ^ 0x44524950);
            }
            DrippedTex[key] = made;
            return made;
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

        /// <summary>Where a point of the drawing (u, v of its texture) lies on the mark's wall plane: s along, t up.</summary>
        internal static void PointOn(Filth_Mark mark, float width, float height, float slide, float slope, float lift, bool flip, float u, float v, out float s, out float t)
        {
            int face = RM_GraffitiKernel.FaceOfSide(mark.wallSide);
            Geom geom = GeomOf(AtlasOf(mark.Position + new Rot4(mark.wallSide).FacingCell, mark.Map));
            RM_GraffitiKernel.MarkPoint(face, geom.crease, geom.side, width, height, slide, slope, lift, flip, u, v, out s, out t);
        }

        private const int GridCols = 24, GridRows = 12;
        private static readonly Dictionary<Texture, float[]> AlphaGrids = new Dictionary<Texture, float[]>();

        /// <summary>A drawing's coverage on a coarse grid (row 0 at the bottom), for finding where on it the paint is. Null if unreadable.</summary>
        internal static float[] AlphaGrid(Texture tex, out int cols, out int rows)
        {
            cols = GridCols;
            rows = GridRows;
            if (tex == null) return null;
            if (AlphaGrids.TryGetValue(tex, out float[] done)) return done;
            float[] grid = null;
            try
            {
                Color32[] px = ReadTexture(tex, out int size);
                int h = px.Length / size;
                grid = new float[GridCols * GridRows];
                for (int r = 0; r < GridRows; r++)
                {
                    for (int c = 0; c < GridCols; c++)
                    {
                        int x0 = c * size / GridCols, x1 = (c + 1) * size / GridCols, y0 = r * h / GridRows, y1 = (r + 1) * h / GridRows;
                        float sum = 0f;
                        int n = 0;
                        for (int y = y0; y < y1; y += 2)
                        {
                            for (int x = x0; x < x1; x += 2) { sum += px[y * size + x].a; n++; }
                        }
                        grid[r * GridCols + c] = n > 0 ? sum / (255f * n) : 0f;
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[Graffiti] couldn't read mark art " + tex.name + ": " + e.Message, tex.GetInstanceID() ^ 0x414c5048);
            }
            AlphaGrids[tex] = grid;
            return grid;
        }

        private static readonly Dictionary<Texture, Color> PaintColors = new Dictionary<Texture, Color>();

        /// <summary>The colour a material's paint shows overall: its texture's mean colour where there's paint, times its tint. Grey if unreadable.</summary>
        internal static Color PaintColor(Material mat)
        {
            Texture tex = mat?.mainTexture;
            if (tex == null) return new Color(0.5f, 0.5f, 0.5f);
            if (!PaintColors.TryGetValue(tex, out Color mean))
            {
                mean = new Color(0.5f, 0.5f, 0.5f);
                try
                {
                    Color32[] px = ReadTexture(tex, out int w, out int h);
                    double r = 0, g = 0, b = 0, n = 0;
                    for (int i = 0; i < px.Length; i += 3)
                    {
                        if (px[i].a < 128) continue;
                        r += px[i].r; g += px[i].g; b += px[i].b; n++;
                    }
                    if (n > 0) mean = new Color((float)(r / n / 255), (float)(g / n / 255), (float)(b / n / 255));
                }
                catch (Exception e)
                {
                    Log.WarningOnce("[Graffiti] couldn't read the paint of " + tex.name + ": " + e.Message, tex.GetInstanceID() ^ 0x50414e54);
                }
                PaintColors[tex] = mean;
            }
            return mean * mat.color;
        }

        private static Texture2D glintTex;

        /// <summary>A writer's shine: a small four-pointed white star, soft-cored, its long arms up and across. Made once, in code.</summary>
        internal static Texture2D GlintTexture()
        {
            if (glintTex != null) return glintTex;
            const int n = 64;
            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
            {
                for (int x = 0; x < n; x++)
                {
                    float dx = Mathf.Abs((x + 0.5f) / n - 0.5f) * 2f, dy = Mathf.Abs((y + 0.5f) / n - 0.5f) * 2f;
                    // Two tapered arms crossing, and a round core where they meet.
                    float arms = Mathf.Max(Mathf.Clamp01(1f - dx * 6f / Mathf.Max(0.05f, 1f - dy)) * (1f - dy), Mathf.Clamp01(1f - dy * 6f / Mathf.Max(0.05f, 1f - dx)) * (1f - dx));
                    float core = Mathf.Clamp01(1f - Mathf.Sqrt(dx * dx + dy * dy) * 3.2f);
                    float a = Mathf.Clamp01(Mathf.Max(arms * 1.4f, core * 1.6f));
                    px[y * n + x] = new Color32(255, 253, 240, (byte)(255f * a));
                }
            }
            glintTex = new Texture2D(n, n, TextureFormat.RGBA32, true) { name = "RM_Graffiti_Glint", filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp };
            glintTex.SetPixels32(px);
            glintTex.Apply(true, false);
            return glintTex;
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

        /// <summary>A colonist's head as a hand would put it on a wall: a street stencil cut from the game's own portrait, in three values, black,
        /// the can's colour and a pale. Their hair, headgear and face's shape are what a wall can show, and enough to say who it is. Null if it can't be had.</summary>
        internal static Texture2D PaintedPortrait(Pawn pawn, int pigment)
        {
            if (pawn == null) return null;
            int key = pawn.thingIDNumber * 16 + (pigment & 15);
            if (Portraits.TryGetValue(key, out Texture2D done)) return done;
            Texture2D made = null;
            try
            {
                RenderTexture rt = PortraitsCache.Get(pawn, new Vector2(PortraitPx, PortraitPx), Rot4.South, new Vector3(0f, 0f, 0.3f), 1.28205f, supersample: false, compensateForUIScale: false, healthStateOverride: PawnHealthState.Mobile);
                Color32[] px = ReadTexture(rt, out int size);
                float seed = (pawn.thingIDNumber & 1023) * 0.37f;
                // Live pass 15, a blind judge: flattened to muted tones, every head still read as "a crisp game portrait... a UI icon or sticker",
                // "lit like the UI, not like paint on brick". A face on a street wall is a stencil: its values cut to three, black for the lines and
                // shadows, the can's colour for the middle, a pale for the light, as the poster-portrait stencils are sprayed. Split at this head's own
                // middle value, so a dark face and a pale one both come out in three.
                RM_Rgb p = RM_GraffitiKernel.PigmentColor(pigment);
                if (p.r * 0.3f + p.g * 0.59f + p.b * 0.11f < 0.3f) p = RM_GraffitiKernel.PigmentColor(1);    // black under black lines is a blot
                Color32 ink = new Color32(30, 24, 24, 255);
                Color32 mid = new Color32((byte)(p.r * 255f), (byte)(p.g * 255f), (byte)(p.b * 255f), 255);
                Color32 pale = new Color32((byte)(Mathf.Lerp(p.r, 0.93f, 0.72f) * 255f), (byte)(Mathf.Lerp(p.g, 0.90f, 0.72f) * 255f), (byte)(Mathf.Lerp(p.b, 0.82f, 0.72f) * 255f), 255);
                bool[] paint = new bool[px.Length];
                var lums = new List<float>();
                for (int i = 0; i < px.Length; i++)
                {
                    paint[i] = px[i].a >= 40;
                    float l = (px[i].r + px[i].g + px[i].b) / 765f;
                    if (paint[i] && l >= InkBelow) lums.Add(l);
                }
                lums.Sort();
                float split = lums.Count > 10 ? lums[lums.Count * 9 / 20] : 0.5f;
                var outPx = new Color32[px.Length];
                for (int i = 0; i < px.Length; i++)
                {
                    int x = i % size, y = i / size;
                    float grit = Mathf.PerlinNoise(seed * 3f + x * 0.55f, seed + y * 0.55f);
                    if (!paint[i])
                    {
                        // Overspray: a faint dusting of the colour just past the stencil's edge, where the card lifted.
                        int near = NearestPaint(paint, size, x, y, 3);
                        outPx[i] = near > 0 ? new Color32(mid.r, mid.g, mid.b, (byte)(80f * (1f - near / 4f) * Mathf.Clamp01(grit * 1.6f - 0.3f))) : new Color32(0, 0, 0, 0);
                        continue;
                    }
                    Color32 c = px[i];
                    float lum = (c.r + c.g + c.b) / 765f;
                    float streak = Mathf.PerlinNoise(seed + x * 0.012f, seed + y * 0.34f);
                    float patch = Mathf.PerlinNoise(seed * 2f + x * 0.045f, seed + y * 0.05f);
                    float keep = Mathf.Clamp01((streak + patch * 0.8f - 0.5f) / 0.3f);
                    // Ragged at the rim: within two pixels of bare wall, grit decides how much paint caught.
                    float rim = NearestBare(paint, size, x, y, 2) > 0 ? Mathf.Clamp01(grit * 1.8f - 0.45f) : 1f;
                    Color32 tone = lum < InkBelow ? ink : lum < split ? mid : pale;
                    float body = lum < InkBelow ? (grit > 0.38f ? 0.95f : 0.6f) : 0.62f + 0.36f * keep;
                    tone.a = (byte)(255f * body * rim);
                    outPx[i] = tone;
                }
                px = outPx;
                made = new Texture2D(size, size, TextureFormat.RGBA32, true) { name = "RM_Graffiti_Portrait_" + pawn.thingIDNumber, filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp };
                made.SetPixels32(px);
                made.Apply(true, false);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[Graffiti] couldn't paint a portrait of " + pawn.LabelShort + ": " + e.Message, pawn.thingIDNumber ^ 0x48454144);
            }
            Portraits[key] = made;
            return made;
        }

        /// <summary>A portrait value below this is a line or a shadow, and goes to the stencil's black.</summary>
        private const float InkBelow = 0.2f;

        private const int PortraitPx = 128;

        /// <summary>Distance in pixels (1..r) from a bare pixel to the nearest painted one, 0 if none within r.</summary>
        private static int NearestPaint(bool[] paint, int size, int x, int y, int r)
        {
            for (int d = 1; d <= r; d++)
            {
                for (int dy = -d; dy <= d; dy++)
                {
                    for (int dx = -d; dx <= d; dx++)
                    {
                        if (Math.Max(Math.Abs(dx), Math.Abs(dy)) != d) continue;
                        int xx = x + dx, yy = y + dy;
                        if (xx >= 0 && yy >= 0 && xx < size && yy < size && paint[yy * size + xx]) return d;
                    }
                }
            }
            return 0;
        }

        /// <summary>Distance in pixels (1..r) from a painted pixel to the nearest bare one, 0 if none within r.</summary>
        private static int NearestBare(bool[] paint, int size, int x, int y, int r)
        {
            for (int d = 1; d <= r; d++)
            {
                for (int dy = -d; dy <= d; dy++)
                {
                    for (int dx = -d; dx <= d; dx++)
                    {
                        if (Math.Max(Math.Abs(dx), Math.Abs(dy)) != d) continue;
                        int xx = x + dx, yy = y + dy;
                        if (xx < 0 || yy < 0 || xx >= size || yy >= size || !paint[yy * size + xx]) return d;
                    }
                }
            }
            return 0;
        }

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
                Color32[] src = ReadTexture(icon, out int size);
                made = new Texture2D(size, size, TextureFormat.RGBA32, true) { name = icon.name + "_painted", filterMode = FilterMode.Trilinear, wrapMode = TextureWrapMode.Clamp };
                float seed = (icon.GetInstanceID() & 1023) * 0.37f;
                float scale = 128f / size;
                // Copied by hand off the faith's sign, not printed: the lines drift a few percent of the icon one way and back, slowly, as a
                // painter's arm does. Live pass 16: a blind judge still read the clean vector inside each frame as "an emblem or badge", "a sticker decal".
                var px = new Color32[src.Length];
                float drift = size * 0.035f, slow = 2.2f / size;
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        int sx = Mathf.Clamp(Mathf.RoundToInt(x + (Mathf.PerlinNoise(seed + x * slow, seed * 1.9f + y * slow) - 0.5f) * 2f * drift), 0, size - 1);
                        int sy = Mathf.Clamp(Mathf.RoundToInt(y + (Mathf.PerlinNoise(seed * 0.7f + x * slow, seed * 2.3f + y * slow) - 0.5f) * 2f * drift), 0, size - 1);
                        px[y * size + x] = src[sy * size + sx];
                    }
                }
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
