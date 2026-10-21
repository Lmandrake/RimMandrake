using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // WORLDMAP_BORDER_BLEND / sea depth (2026-10-20, design/Jawa/worldbuilding/worldmap_in_game_audit_2026-10-20.md §6).
    //
    // How vanilla 1.6 draws the planet (RimSage, WorldDrawLayer_Terrain.Regenerate): one submesh per biome material, each
    // tile a polygon fan of its own vertices, UV0 = (vertex elevation, unclamped elevation, 0). Nothing crosses a tile
    // edge, so every biome border is a hard hex line. Two additions here, both appended to the SURFACE terrain layer
    // after vanilla has built it (a postfix that wraps the Regenerate iterator):
    //
    // 1. BORDER BLEND. For each land tile next to a land tile of another biome, the tile's polygon is drawn again, once per
    //    neighbouring biome, with that biome's face texture on a transparent lit overlay shader. Vertex alpha is the share
    //    of that biome among the 3 tiles meeting at each corner (0 on an inner ring), so the colour at a shared corner is
    //    the same seen from either side and the border becomes a gradient (the map's own terrain-edge fade, done the
    //    pollution layer's way: WorldDrawLayer_Pollution draws per-tile polygons with vertex alpha and uv = position*0.1).
    //    Water tiles take no part: coasts belong to the ocean shader.
    // 2. SEA SHADING. Seas draw as one flat colour (the WorldOcean shader takes no depth; see BuildSea). Each water tile
    //    gets a pale shore film fading out from the coast and a dark deep film fading in away from it, coloured by
    //    distance to the coast. Tile elevations are not touched; no texture carries depth.
    //
    // Tunables are public statics so a bridge session can tune live: jawa/static_call RimMandrake.Biomes.RM_WorldLook Set
    // "key|value", then jawa/world_commit (redraw only). Mod Settings expose on/off for each.
    [StaticConstructorOnStartup]
    public static class RM_WorldLook
    {
        public static float blendStrength = 1f;     // alpha = strength * share of the neighbour biome at a corner
        public static float blendInner = 0.35f;     // inner ring (alpha 0) at this fraction of centre->corner
        public static float blendLift = 0.01f;      // drawn this far above the terrain surface
        public static float blendUvScale = 0.1f;    // uv = position * scale (the pollution layer's value)
        public static string blendShader = "WorldOverlayTransparentLit";
        public static int blendQueue = 3505;        // above terrain (3500), under hills (3510) and rivers (3520)

        public static string seaShoreColor = "0.40,0.62,0.72";  // pale film near the coast
        public static float seaShoreAlpha = 0.40f;
        public static float seaShoreTiles = 1.0f;
        public static string seaDeepColor = "0.05,0.09,0.20";   // dark film far from it
        public static float seaDeepAlpha = 0.5f;
        public static float seaDeepTiles = 4f;
        public static string seaShader = "WorldOverlayTransparentLit";
        public static int seaQueue = 3502;          // above the ocean (3500), under the border blend (3505)

        public static string lastInfo = "never built";

        static readonly FieldInfo SubMeshesField = AccessTools.Field(typeof(WorldDrawLayerBase), "subMeshes");
        static readonly Dictionary<WorldDrawLayer_Terrain, List<LayerSubMesh>> Ours = new Dictionary<WorldDrawLayer_Terrain, List<LayerSubMesh>>();
        static readonly Dictionary<BiomeDef, Material> BlendMats = new Dictionary<BiomeDef, Material>();

        static RM_WorldLook()
        {
            try
            {
                MethodInfo target = AccessTools.Method(typeof(WorldDrawLayer_Terrain), "Regenerate");
                new Harmony("mandrake.rm.biomes.worldlook").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_WorldLook), nameof(RegeneratePostfix)));
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Biomes] world look patch failed, planet keeps vanilla borders: " + e.Message);
            }
        }

        static void RegeneratePostfix(ref IEnumerable __result, WorldDrawLayer_Terrain __instance)
        {
            __result = Wrap(__result, __instance);
        }

        static IEnumerable Wrap(IEnumerable inner, WorldDrawLayer_Terrain layer)
        {
            RemoveOurs(layer);
            foreach (object o in inner) yield return o;
            if (layer.planetLayer == null || !layer.planetLayer.IsRootSurface) yield break;
            try
            {
                var sb = new StringBuilder();
                var mine = new List<LayerSubMesh>();
                if (RM_BiomesSettings.worldSeaDepth) sb.Append(BuildSea(layer, mine));
                if (RM_BiomesSettings.worldBorderBlend) sb.Append(" ").Append(BuildBlend(layer, mine));
                var subs = SubMeshes(layer);
                foreach (LayerSubMesh sm in mine)
                {
                    if (sm.verts.Count == 0) continue;
                    sm.FinalizeMesh(MeshParts.All);
                    subs.Add(sm);
                }
                Ours[layer] = mine;
                lastInfo = sb.ToString().Trim();
            }
            catch (Exception e)
            {
                lastInfo = "failed: " + e;
                Log.ErrorOnce("[RimMandrake.Biomes] world look failed, planet keeps vanilla borders: " + e, 0x52574c31);
            }
        }

        static List<LayerSubMesh> SubMeshes(WorldDrawLayerBase layer) => (List<LayerSubMesh>)SubMeshesField.GetValue(layer);

        static void RemoveOurs(WorldDrawLayer_Terrain layer)
        {
            if (!Ours.TryGetValue(layer, out var mine)) return;
            var subs = SubMeshes(layer);
            foreach (LayerSubMesh s in mine)
            {
                subs.Remove(s);
                if (s.mesh != null) UnityEngine.Object.Destroy(s.mesh);
            }
            Ours.Remove(layer);
        }

        // ---------------------------------------------------------------- sea shading
        // MEASURED 2026-10-20: the WorldOcean shader ignores UV0 (Custom/WorldOcean has only _MainTex and _MacroTex; a sea
        // re-fed depths from 0 to -100000 m drew byte-identical pixels), so depth cannot be given to it. Instead each water
        // tile is drawn again twice on a lit transparent overlay over a white texture: a pale shore film whose alpha falls
        // off over seaShoreTiles from the coast, and a dark deep film whose alpha rises over seaDeepTiles.
        static string BuildSea(WorldDrawLayer_Terrain layer, List<LayerSubMesh> mine)
        {
            PlanetLayer pl = layer.planetLayer;
            var verts = new List<Vector3>();
            var nbs = new List<PlanetTile>();
            var nbVerts = new List<List<Vector3>>();
            var coast = new HashSet<Vector3>();
            var water = new List<int>();
            for (int i = 0; i < pl.TilesCount; i++)
            {
                BiomeDef a = pl[i].PrimaryBiome;
                if (a == null || !a.isWaterBiome) continue;
                water.Add(i);
                pl.GetTileNeighbors(i, nbs);
                pl.GetTileVertices(i, verts);
                while (nbVerts.Count < nbs.Count) nbVerts.Add(new List<Vector3>());
                for (int k = 0; k < nbs.Count; k++)
                {
                    BiomeDef nb = pl[nbs[k].tileId].PrimaryBiome;
                    if (nb != null && nb.isWaterBiome) continue;
                    pl.GetTileVertices(nbs[k].tileId, nbVerts[k]);
                    foreach (Vector3 v in verts) if (nbVerts[k].Contains(v)) coast.Add(v);
                }
            }
            if (water.Count == 0) return "sea: no water tiles";
            float cell = 0.05f;
            var buckets = new Dictionary<long, List<Vector3>>();
            foreach (Vector3 c in coast) Bucket(buckets, Key(c.normalized, cell)).Add(c.normalized);
            float radius = pl.GetTileCenter(water[0]).magnitude;
            float tileSpacing = Mathf.Sqrt(4f * Mathf.PI * radius * radius / Mathf.Max(1, pl.TilesCount));
            float maxTiles = Mathf.Max(seaShoreTiles, seaDeepTiles, 0.5f);
            float reach = maxTiles * tileSpacing / radius;
            int search = Mathf.CeilToInt(reach / cell) + 1;
            System.Func<Vector3, float> distTiles = p =>
            {
                Vector3 d = p.normalized;
                float best = reach;
                int kx = Mathf.FloorToInt(d.x / cell), ky = Mathf.FloorToInt(d.y / cell), kz = Mathf.FloorToInt(d.z / cell);
                for (int x = -search; x <= search; x++)
                    for (int y = -search; y <= search; y++)
                        for (int z = -search; z <= search; z++)
                        {
                            if (!buckets.TryGetValue(Pack(kx + x, ky + y, kz + z), out var list)) continue;
                            foreach (Vector3 c in list) { float dd = (c - d).magnitude; if (dd < best) best = dd; }
                        }
                return best * radius / tileSpacing;
            };
            Material shoreMat = FlatMat(seaShoreColor, seaQueue);
            Material deepMat = FlatMat(seaDeepColor, seaQueue + 1);
            LayerSubMesh shore = null, deep = null;
            float windSign = 0f;
            int n = 0;
            foreach (int i in water)
            {
                pl.GetTileVertices(i, verts);
                if (verts.Count < 3) continue;
                Vector3 center = pl.GetTileCenter(i);
                if (windSign == 0f)
                    windSign = Mathf.Sign(Vector3.Dot(Vector3.Cross(verts[1] - verts[2], verts[0] - verts[2]), center));
                if (shore == null || shore.verts.Count > 38000) { shore = new LayerSubMesh(new Mesh(), shoreMat); mine.Add(shore); }
                if (deep == null || deep.verts.Count > 38000) { deep = new LayerSubMesh(new Mesh(), deepMat); mine.Add(deep); }
                // rings: centre, half-way, corner
                var pts = new List<Vector3> { center };
                foreach (Vector3 v in verts) pts.Add(center + (v - center) * 0.5f);
                foreach (Vector3 v in verts) pts.Add(v);
                var dist = new float[pts.Count];
                for (int q = 0; q < pts.Count; q++) dist[q] = coast.Contains(pts[q]) ? 0f : distTiles(pts[q]);
                EmitSeaTile(shore, pts, verts.Count, center, windSign, d => seaShoreAlpha * Mathf.Pow(1f - Mathf.Clamp01(d / Mathf.Max(0.01f, seaShoreTiles)), 2f), dist);
                EmitSeaTile(deep, pts, verts.Count, center, windSign, d => seaDeepAlpha * Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(d / Mathf.Max(0.01f, seaDeepTiles))), dist);
                n++;
            }
            return "sea: " + n + " water tiles shaded from " + coast.Count + " coast vertices";
        }

        static void EmitSeaTile(LayerSubMesh sm, List<Vector3> pts, int ring, Vector3 center, float windSign, System.Func<float, float> alphaOf, float[] dist)
        {
            int b = sm.verts.Count;
            for (int q = 0; q < pts.Count; q++)
            {
                Vector3 p = pts[q] + pts[q].normalized * blendLift;
                sm.verts.Add(p); sm.uvs.Add(p * blendUvScale);
                sm.colors.Add(new Color32(255, 255, 255, (byte)Mathf.RoundToInt(Mathf.Clamp01(alphaOf(dist[q])) * 255f)));
            }
            for (int j = 0; j < ring; j++)
            {
                int j1 = (j + 1) % ring;
                int m0 = b + 1 + j, m1 = b + 1 + j1, o0 = b + 1 + ring + j, o1 = b + 1 + ring + j1;
                Tri(sm, b, m0, m1, center, windSign);
                Tri(sm, m0, o0, o1, center, windSign);
                Tri(sm, m0, o1, m1, center, windSign);
            }
        }

        static readonly Dictionary<string, Material> FlatMats = new Dictionary<string, Material>();
        static Material FlatMat(string rgb, int queue)
        {
            string key = rgb + "@" + queue + "@" + seaShader;
            if (FlatMats.TryGetValue(key, out Material m) && m != null) return m;
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            string[] p = rgb.Split(',');
            m = new Material(ResolveShader(seaShader)) { mainTexture = BaseContent.WhiteTex, renderQueue = queue };
            m.color = new Color(float.Parse(p[0], inv), float.Parse(p[1], inv), float.Parse(p[2], inv), 1f);
            FlatMats[key] = m;
            return m;
        }

        static long Pack(int x, int y, int z) => ((long)(x & 0x1FFFFF) << 42) | ((long)(y & 0x1FFFFF) << 21) | (long)(z & 0x1FFFFF);
        static long Key(Vector3 v, float cell) => Pack(Mathf.FloorToInt(v.x / cell), Mathf.FloorToInt(v.y / cell), Mathf.FloorToInt(v.z / cell));
        static List<Vector3> Bucket(Dictionary<long, List<Vector3>> b, long k)
        {
            if (!b.TryGetValue(k, out var l)) { l = new List<Vector3>(); b[k] = l; }
            return l;
        }

        // ---------------------------------------------------------------- border blend
        static bool Blends(BiomeDef b) => b != null && !b.isWaterBiome && b.DrawMaterial != null && b.DrawMaterial.mainTexture != null
                                          && b.DrawMaterial.shader != ShaderDatabase.WorldOcean;

        static Material BlendMat(BiomeDef b)
        {
            if (BlendMats.TryGetValue(b, out Material m) && m != null) return m;
            Shader sh = ResolveShader(blendShader);
            m = new Material(sh) { mainTexture = b.DrawMaterial.mainTexture, renderQueue = blendQueue };
            BlendMats[b] = m;
            return m;
        }

        static Shader ResolveShader(string name)
        {
            if (name.StartsWith("mat:"))
            {
                FieldInfo mf = typeof(WorldMaterials).GetField(name.Substring(4), BindingFlags.Static | BindingFlags.Public);
                if (mf?.GetValue(null) is Material mm) return mm.shader;
            }
            FieldInfo f = typeof(ShaderDatabase).GetField(name, BindingFlags.Static | BindingFlags.Public);
            if (f?.GetValue(null) is Shader s) return s;
            return ShaderDatabase.WorldOverlayTransparentLit;
        }

        static string BuildBlend(WorldDrawLayer_Terrain layer, List<LayerSubMesh> mine)
        {
            PlanetLayer pl = layer.planetLayer;
            int before = mine.Count;
            var current = new Dictionary<Material, LayerSubMesh>();
            var verts = new List<Vector3>();
            var nbs = new List<PlanetTile>();
            var nbVerts = new List<List<Vector3>>();
            var shares = new Dictionary<BiomeDef, float[]>();
            float windSign = 0f;
            int tilesTouched = 0, polys = 0;
            for (int i = 0; i < pl.TilesCount; i++)
            {
                BiomeDef a = pl[i].PrimaryBiome;
                if (!Blends(a)) continue;
                pl.GetTileNeighbors(i, nbs);
                bool any = false;
                foreach (PlanetTile n in nbs)
                {
                    BiomeDef nb = pl[n.tileId].PrimaryBiome;
                    if (nb != a && Blends(nb)) { any = true; break; }
                }
                if (!any) continue;
                pl.GetTileVertices(i, verts);
                if (verts.Count < 3) continue;
                Vector3 center = pl.GetTileCenter(i);
                if (windSign == 0f)
                {
                    // vanilla emits (v[j+2], v[j+1], v[0]); copy its facing
                    Vector3 n0 = Vector3.Cross(verts[1] - verts[2], verts[0] - verts[2]);
                    windSign = Mathf.Sign(Vector3.Dot(n0, center));
                }
                while (nbVerts.Count < nbs.Count) nbVerts.Add(new List<Vector3>());
                for (int k = 0; k < nbs.Count; k++) pl.GetTileVertices(nbs[k].tileId, nbVerts[k]);
                shares.Clear();
                for (int j = 0; j < verts.Count; j++)
                {
                    int total = 1;
                    var here = new List<BiomeDef>(2);
                    for (int k = 0; k < nbs.Count; k++)
                    {
                        if (!nbVerts[k].Contains(verts[j])) continue;
                        BiomeDef nb = pl[nbs[k].tileId].PrimaryBiome;
                        total++;
                        if (nb != a && Blends(nb)) here.Add(nb);
                    }
                    foreach (BiomeDef nb in here)
                    {
                        if (!shares.TryGetValue(nb, out float[] arr)) { arr = new float[verts.Count]; shares[nb] = arr; }
                        arr[j] += 1f / total;
                    }
                }
                tilesTouched++;
                foreach (var kv in shares)
                {
                    Material mat = BlendMat(kv.Key);
                    if (!current.TryGetValue(mat, out LayerSubMesh sm) || sm.verts.Count > 38000)
                    {
                        sm = new LayerSubMesh(new Mesh(), mat);
                        current[mat] = sm;
                        mine.Add(sm);
                    }
                    EmitRing(sm, verts, center, kv.Value, windSign);
                    polys++;
                }
            }
            return "blend: " + polys + " overlays on " + tilesTouched + " border tiles, " + (mine.Count - before) + " submeshes, shader "
                   + ResolveShader(blendShader).name;
        }

        static void EmitRing(LayerSubMesh sm, List<Vector3> verts, Vector3 center, float[] share, float windSign)
        {
            int n = verts.Count;
            int baseIdx = sm.verts.Count;
            for (int j = 0; j < n; j++)
            {
                Vector3 outer = verts[j] + verts[j].normalized * blendLift;
                Vector3 innerP = center + (verts[j] - center) * blendInner;
                innerP += innerP.normalized * blendLift;
                byte alpha = (byte)Mathf.RoundToInt(Mathf.Clamp01(blendStrength * share[j]) * 255f);
                sm.verts.Add(outer); sm.uvs.Add(outer * blendUvScale); sm.colors.Add(new Color32(255, 255, 255, alpha));
                sm.verts.Add(innerP); sm.uvs.Add(innerP * blendUvScale); sm.colors.Add(new Color32(255, 255, 255, 0));
            }
            for (int j = 0; j < n; j++)
            {
                int o0 = baseIdx + 2 * j, i0 = o0 + 1;
                int o1 = baseIdx + 2 * ((j + 1) % n), i1 = o1 + 1;
                Tri(sm, o0, o1, i0, center, windSign);
                Tri(sm, i0, o1, i1, center, windSign);
            }
        }

        static void Tri(LayerSubMesh sm, int a, int b, int c, Vector3 center, float windSign)
        {
            // order (c, b, a) like vanilla, then flip if the facing differs from vanilla's
            Vector3 pa = sm.verts[a], pb = sm.verts[b], pc = sm.verts[c];
            float s = Mathf.Sign(Vector3.Dot(Vector3.Cross(pb - pc, pa - pc), center));
            if (s == windSign) { sm.tris.Add(c); sm.tris.Add(b); sm.tris.Add(a); }
            else { sm.tris.Add(a); sm.tris.Add(b); sm.tris.Add(c); }
        }

        // ---------------------------------------------------------------- bridge helpers (jawa/static_call)
        public static string Set(string key, string value)
        {
            FieldInfo f = typeof(RM_WorldLook).GetField(key, BindingFlags.Static | BindingFlags.Public);
            if (f == null) return "no field " + key;
            object v = f.FieldType == typeof(float) ? (object)float.Parse(value, System.Globalization.CultureInfo.InvariantCulture)
                     : f.FieldType == typeof(int) ? int.Parse(value)
                     : f.FieldType == typeof(bool) ? bool.Parse(value)
                     : (object)value;
            f.SetValue(null, v);
            BlendMats.Clear();
            FlatMats.Clear();
            return key + " = " + f.GetValue(null);
        }

        public static string Info()
        {
            var sb = new StringBuilder(lastInfo);
            foreach (FieldInfo f in typeof(RM_WorldLook).GetFields(BindingFlags.Static | BindingFlags.Public))
                if (f.Name != "lastInfo") sb.Append(" | ").Append(f.Name).Append('=').Append(f.GetValue(null));
            sb.Append(" | blend=").Append(RM_BiomesSettings.worldBorderBlend).Append(" seaDepth=").Append(RM_BiomesSettings.worldSeaDepth);
            return sb.ToString();
        }

        // Shader properties of a WorldMaterials material ("WorldOcean", "WorldTerrain", ...) with their current values.
        public static string ShaderProps(string materialField)
        {
            FieldInfo mf = typeof(WorldMaterials).GetField(materialField, BindingFlags.Static | BindingFlags.Public);
            if (!(mf?.GetValue(null) is Material m)) return "no material " + materialField;
            var sb = new StringBuilder(m.shader.name + " queue " + m.renderQueue + ":");
            int n = m.shader.GetPropertyCount();
            for (int i = 0; i < n; i++)
            {
                string pn = m.shader.GetPropertyName(i);
                var t = m.shader.GetPropertyType(i);
                sb.Append(' ').Append(pn).Append('(').Append(t).Append(")=");
                switch (t)
                {
                    case UnityEngine.Rendering.ShaderPropertyType.Color: sb.Append(m.GetColor(pn)); break;
                    case UnityEngine.Rendering.ShaderPropertyType.Vector: sb.Append(m.GetVector(pn)); break;
                    case UnityEngine.Rendering.ShaderPropertyType.Float:
                    case UnityEngine.Rendering.ShaderPropertyType.Range: sb.Append(m.GetFloat(pn)); break;
                    case UnityEngine.Rendering.ShaderPropertyType.Texture: sb.Append(m.GetTexture(pn)?.name ?? "null"); break;
                }
                sb.Append(';');
            }
            return sb.ToString();
        }

        // Set a float ("0.5") or colour ("r,g,b,a") on the ocean material of every water BiomeDef of ours.
        public static string SetOceanProp(string prop, string value)
        {
            int n = 0;
            string[] p = value.Split(',');
            foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                if (!b.isWaterBiome) continue;
                Material m = b.DrawMaterial;
                if (m == null || m.shader != ShaderDatabase.WorldOcean || !m.HasProperty(prop)) continue;
                var inv = System.Globalization.CultureInfo.InvariantCulture;
                if (p.Length >= 3) m.SetColor(prop, new Color(float.Parse(p[0], inv), float.Parse(p[1], inv), float.Parse(p[2], inv), p.Length > 3 ? float.Parse(p[3], inv) : 1f));
                else m.SetFloat(prop, float.Parse(value, inv));
                n++;
            }
            return prop + " set on " + n + " water materials";
        }
    }
}
