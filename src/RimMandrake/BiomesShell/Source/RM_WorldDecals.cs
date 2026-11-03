using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // BIOME DECALS (WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE, world look 4a; design/Jawa/worldbuilding/world_look_program_2026-10-24.md).
    //
    // Infrastructure kept through the Baroque redo; the per-biome art is throwaway and swapped by re-running the generator
    // (contract: design/Jawa/worldbuilding/world_decal_atlas_contract.md, generator src/RimMandrake/Utils/art/world_decal_atlas.py).
    //
    // - Every FLAT land tile of a biome that ships an atlas gets 2 or 3 small glyph quads, tangent to the planet and upright
    //   (their "up" is planet north projected onto the tile), so the light side and shadow baked into the art agree
    //   everywhere. Which cells and where on the tile come from a stable hash of the tile id: the same planet always draws
    //   the same glyphs.
    // - One atlas per biome: World/Decals/<BiomeDef defName>, square, cells of CellPx pixels, so a 512 px atlas is 2x2 and
    //   a 1024 px atlas is 4x4. A biome with no atlas draws nothing and logs nothing; the roster fills in gradually.
    // - Drawn into the root-surface terrain layer by RM_WorldLook.Wrap, over the swirls (3506, +0.004) and under the hills
    //   (3510, +0.005) and rivers (3520, +0.01).
    // - LOD: the decal materials' colour alpha is set every frame from the world camera altitude (full at or below
    //   decalFullAlt, gone at or above decalGoneAlt). The terrain layer draws with Alpha 1, so Graphics.DrawMesh uses the
    //   material itself and its colour is what the shader sees. No mesh is rebuilt for the fade.
    //
    // The arithmetic (hash, count, cell, slot, fade, atlas UVs) is mirrored in Python by
    // src/RimMandrake/Utils/selftest_world_decals.py; change both together.
    [StaticConstructorOnStartup]
    public static class RM_WorldDecals
    {
        public const int CellPx = 256;

        public static float decalSize = 0.30f;      // glyph edge, in tile spacings
        public static float decalSpread = 0.22f;    // glyph centre distance from the tile centre, in tile spacings
        public static float decalJitter = 0.06f;    // extra random offset, in tile spacings
        public static float decalLift = 0.0045f;    // over the swirls (+0.004), under hills (+0.005) and rivers (+0.01)
        public static int decalQueue = 3507;        // over the swirls (3506), under hills (3510)
        public static float decalFullAlt = 380f;    // camera altitude (125..1100) at or below which decals draw at full alpha
        public static float decalGoneAlt = 620f;    // at or above which they are gone (mid zoom)
        public static bool decalFlipX = false;      // mirror every glyph, if a live look shows the light on the wrong side

        public static string lastInfo = "never built";
        public static float lastAlpha = -1f;

        // null is cached too: a biome without an atlas is looked up once
        static readonly Dictionary<BiomeDef, Material> Mats = new Dictionary<BiomeDef, Material>();
        static readonly Dictionary<BiomeDef, int> Grid = new Dictionary<BiomeDef, int>();

        static RM_WorldDecals()
        {
            try
            {
                new Harmony("mandrake.rm.biomes.worlddecals").Patch(AccessTools.PropertyGetter(typeof(WorldDrawLayerBase), "Alpha"),
                    postfix: new HarmonyMethod(typeof(RM_WorldDecals), nameof(AlphaPostfix)));
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Biomes] biome decal fade patch failed, decals draw at full strength: " + e.Message);
            }
        }

        // ---------------------------------------------------------------- pure arithmetic (mirrored in the selftest)
        public static uint Hash(int tileId, uint salt)
        {
            unchecked
            {
                uint h = (uint)tileId * 0x9E3779B1u + salt * 0x85EBCA77u;
                h ^= h >> 16; h *= 0x85EBCA6Bu;
                h ^= h >> 13; h *= 0xC2B2AE35u;
                h ^= h >> 16;
                return h;
            }
        }

        public static int GlyphCount(int tileId) => 2 + (int)(Hash(tileId, 0) % 2u);

        // cell of glyph k on the tile; never the same cell as the glyph before it when the atlas has more than one
        public static int Cell(int tileId, int k, int cells)
        {
            if (cells <= 1) return 0;
            int c = (int)(Hash(tileId, 11u + (uint)k) % (uint)cells);
            if (k > 0 && c == Cell(tileId, k - 1, cells)) c = (c + 1) % cells;
            return c;
        }

        // slot of glyph k: (angle in radians around the tile, distance from the centre in tile spacings)
        public static Vector2 Slot(int tileId, int k, int count)
        {
            float turn = (Hash(tileId, 1) % 3600u) / 3600f;
            float angle = (turn + (float)k / count) * 2f * Mathf.PI;
            float jitter = ((Hash(tileId, 21u + (uint)k) % 1000u) / 999f) * decalJitter;
            return new Vector2(angle, decalSpread + jitter);
        }

        // atlas grid side from the texture width; 0 = not an atlas this contract accepts
        public static int GridSide(int width, int height)
        {
            if (width != height || width < CellPx || width % CellPx != 0) return 0;
            int g = width / CellPx;
            return g == 1 || g == 2 || g == 4 ? g : 0;
        }

        // UV rectangle (u0, v0, u1, v1) of a cell: cells run left to right, top row first; Unity's v runs bottom up
        public static Vector4 CellUv(int cell, int side)
        {
            float inset = 1f / (side * CellPx);   // one texel, so a neighbouring cell never bleeds in
            int col = cell % side, row = cell / side;
            float u0 = (float)col / side, u1 = (float)(col + 1) / side;
            float v1 = 1f - (float)row / side, v0 = 1f - (float)(row + 1) / side;
            return new Vector4(u0 + inset, v0 + inset, u1 - inset, v1 - inset);
        }

        public static float FadeAlpha(float altitude, float fullAt, float goneAt)
        {
            if (goneAt <= fullAt) return altitude <= fullAt ? 1f : 0f;
            return 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(fullAt, goneAt, altitude));
        }

        // ---------------------------------------------------------------- atlases
        static Material MatFor(BiomeDef b, out int side)
        {
            side = 0;
            if (Mats.TryGetValue(b, out Material m))
            {
                if (m != null) side = Grid[b];
                return m;
            }
            Texture2D tex = ContentFinder<Texture2D>.Get("World/Decals/" + b.defName, false);
            int g = tex == null ? 0 : GridSide(tex.width, tex.height);
            if (tex != null && g == 0)
                Log.WarningOnce("[RimMandrake.Biomes] biome decals: World/Decals/" + b.defName + " is " + tex.width + "x" + tex.height
                    + ", not a square 256/512/1024 atlas (world_decal_atlas_contract.md); no decals there", 0x52444331 + b.defName.GetHashCode());
            if (g > 0)
            {
                tex.wrapMode = TextureWrapMode.Clamp;
                m = new Material(ShaderDatabase.WorldOverlayTransparentLit) { mainTexture = tex, renderQueue = decalQueue };
                m.color = new Color(1f, 1f, 1f, lastAlpha < 0f ? 1f : lastAlpha);
                Grid[b] = g;
                side = g;
            }
            Mats[b] = m;
            return m;
        }

        // after a Set: the SAME materials take the new queue and the fade is re-applied next frame. Materials are kept, never
        // replaced, so submeshes built earlier keep fading (and none leak); textures cannot change while the game runs.
        public static void Refresh()
        {
            foreach (Material m in Mats.Values)
                if (m != null) m.renderQueue = decalQueue;
            lastAlpha = -1f;
        }

        // ---------------------------------------------------------------- build (called from RM_WorldLook.Wrap)
        public static string Build(WorldDrawLayer_Terrain layer, List<LayerSubMesh> mine)
        {
            PlanetLayer pl = layer.planetLayer;
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var current = new Dictionary<Material, LayerSubMesh>();
            var verts = new List<Vector3>();
            float tileSpacing = 0f, windSign = 0f;
            int tiles = 0, glyphs = 0;
            var withAtlas = new HashSet<BiomeDef>();
            var without = new HashSet<BiomeDef>();
            for (int i = 0; i < pl.TilesCount; i++)
            {
                Tile t = pl[i];
                BiomeDef b = t.PrimaryBiome;
                if (b == null || b.isWaterBiome || t.hilliness != Hilliness.Flat) continue;
                Material mat = MatFor(b, out int side);
                if (mat == null) { without.Add(b); continue; }
                withAtlas.Add(b);
                pl.GetTileVertices(i, verts);
                if (verts.Count < 3) continue;
                Vector3 center = pl.GetTileCenter(i);
                if (tileSpacing == 0f)
                {
                    float radius = center.magnitude;
                    tileSpacing = Mathf.Sqrt(4f * Mathf.PI * radius * radius / Mathf.Max(1, pl.TilesCount));
                    windSign = Mathf.Sign(Vector3.Dot(Vector3.Cross(verts[1] - verts[2], verts[0] - verts[2]), center));
                }
                Vector3 n = center.normalized;
                Vector3 up = Vector3.up - n * Vector3.Dot(n, Vector3.up);
                if (up.sqrMagnitude < 1e-6f) up = Vector3.forward - n * Vector3.Dot(n, Vector3.forward);
                up.Normalize();
                Vector3 right = Vector3.Cross(n, up).normalized;   // camera outside looking down -n: right = n x up
                if (decalFlipX) right = -right;
                if (!current.TryGetValue(mat, out LayerSubMesh sm) || sm.verts.Count > 38000)
                {
                    sm = new LayerSubMesh(new Mesh(), mat);
                    current[mat] = sm;
                    mine.Add(sm);
                }
                int count = GlyphCount(i);
                float half = decalSize * tileSpacing * 0.5f;
                for (int k = 0; k < count; k++)
                {
                    Vector2 slot = Slot(i, k, count);
                    float d = slot.y * tileSpacing;
                    Vector3 c = center + (right * Mathf.Cos(slot.x) + up * Mathf.Sin(slot.x)) * d;
                    // the quad lies in the tangent plane AT the glyph (no tilt); its corners still stand a sagitta above the
                    // sphere, harmless because decals go on flat tiles only, where no hill quad is drawn
                    Vector3 gn = c.normalized;
                    c = gn * (center.magnitude + decalLift);
                    Vector3 gup = (up - gn * Vector3.Dot(gn, up)).normalized;
                    Vector3 gright = Vector3.Cross(gn, gup).normalized;
                    if (decalFlipX) gright = -gright;
                    Vector4 uv = CellUv(Cell(i, k, side * side), side);
                    int b0 = sm.verts.Count;
                    // bottom-left, top-left, top-right, bottom-right
                    sm.verts.Add(c - gright * half - gup * half); sm.uvs.Add(new Vector3(uv.x, uv.y, 0f));
                    sm.verts.Add(c - gright * half + gup * half); sm.uvs.Add(new Vector3(uv.x, uv.w, 0f));
                    sm.verts.Add(c + gright * half + gup * half); sm.uvs.Add(new Vector3(uv.z, uv.w, 0f));
                    sm.verts.Add(c + gright * half - gup * half); sm.uvs.Add(new Vector3(uv.z, uv.y, 0f));
                    for (int q = 0; q < 4; q++) sm.colors.Add(new Color32(255, 255, 255, 255));
                    Tri(sm, b0, b0 + 1, b0 + 2, center, windSign);
                    Tri(sm, b0, b0 + 2, b0 + 3, center, windSign);
                    glyphs++;
                }
                tiles++;
            }
            lastInfo = "decals: " + glyphs + " glyphs on " + tiles + " flat tiles of " + withAtlas.Count + " biomes with an atlas ("
                       + without.Count + " land biomes without one), " + sw.ElapsedMilliseconds + " ms";
            return lastInfo;
        }

        static void Tri(LayerSubMesh sm, int a, int b, int c, Vector3 center, float windSign)
        {
            // same facing rule as RM_WorldLook.Tri: vanilla's (c, b, a), flipped if the facing differs
            Vector3 pa = sm.verts[a], pb = sm.verts[b], pc = sm.verts[c];
            float s = Mathf.Sign(Vector3.Dot(Vector3.Cross(pb - pc, pa - pc), center));
            if (s == windSign) { sm.tris.Add(c); sm.tris.Add(b); sm.tris.Add(a); }
            else { sm.tris.Add(a); sm.tris.Add(b); sm.tris.Add(c); }
        }

        // ---------------------------------------------------------------- per-frame fade
        static void AlphaPostfix(WorldDrawLayerBase __instance)
        {
            if (!(__instance is WorldDrawLayer_Terrain) || Mats.Count == 0) return;
            try
            {
                WorldCameraDriver cam = Find.WorldCameraDriver;
                float a = cam == null ? 1f : FadeAlpha(cam.altitude, decalFullAlt, decalGoneAlt);
                if (Mathf.Abs(a - lastAlpha) < 0.002f) return;
                lastAlpha = a;
                foreach (Material m in Mats.Values)
                    if (m != null) m.color = new Color(1f, 1f, 1f, a);
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RimMandrake.Biomes] biome decal fade failed: " + e, 0x52444332);
            }
        }

        // ---------------------------------------------------------------- bridge helpers (jawa/static_call)
        public static string Set(string key, string value)
        {
            var f = typeof(RM_WorldDecals).GetField(key, System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
            if (f == null || f.IsLiteral) return "no field " + key;
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            object v = f.FieldType == typeof(float) ? (object)float.Parse(value, inv)
                     : f.FieldType == typeof(int) ? int.Parse(value)
                     : f.FieldType == typeof(bool) ? bool.Parse(value)
                     : (object)value;
            f.SetValue(null, v);
            Refresh();
            return key + " = " + f.GetValue(null) + " (jawa/world_commit to rebuild; the fade follows at once)";
        }

        // read-only: is there an atlas for this biome, and what grid does the contract read from it (no caching, no build)
        public static string Probe(string defName)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get("World/Decals/" + (defName ?? "").Trim(), false);
            if (tex == null) return "atlas " + defName + " none";
            int g = GridSide(tex.width, tex.height);
            return "atlas " + defName + " " + tex.width + "x" + tex.height + " grid=" + g;
        }

        public static string Info()
        {
            return lastInfo + " | enabled=" + RM_BiomesSettings.worldBiomeDecals + " alpha=" + lastAlpha
                   + " altitude=" + (Find.WorldCameraDriver?.altitude ?? -1f) + " atlases=" + Grid.Count
                   + " | size=" + decalSize + " spread=" + decalSpread + " lift=" + decalLift + " queue=" + decalQueue
                   + " fullAlt=" + decalFullAlt + " goneAlt=" + decalGoneAlt + " flipX=" + decalFlipX;
        }
    }
}
