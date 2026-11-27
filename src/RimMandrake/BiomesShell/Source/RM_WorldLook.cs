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
    // "key|value"; Set marks every world layer dirty, so the planet and the sea floor redraw on the next frame. Mod
    // Settings expose on/off for each.
    [StaticConstructorOnStartup]
    public static class RM_WorldLook
    {
        public static float blendStrength = 1f;     // alpha = strength * share of the neighbour biome at a corner
        public static float blendInner = 0.35f;     // inner ring (alpha 0) at this fraction of centre->corner
        // Drawn this far above the terrain surface. MUST stay under hills (+0.005, WorldDrawLayer_Hills) and rivers
        // (+0.01, WorldDrawLayer_Rivers.FinalizePoint): these overlays write depth, so at 0.01 they hid every river and
        // hill on a biome-border tile and rivers drew as dashes (RIVER_DASHES_MEASURE_MORSE_CODE_WATER, 2026-10-20).
        public static float blendLift = 0.003f;
        public static float blendUvScale = 0.1f;    // uv = position * scale (the pollution layer's value)
        public static string blendShader = "WorldOverlayTransparentLit";
        public static int blendQueue = 3505;        // above terrain (3500), under hills (3510) and rivers (3520)

        // Film numbers = the "wider shelf" row the owner confirmed (2026-10-24, WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP);
        // world_water_variants.FILMS["shelf"] is the source and selftest_sea_films_picked.py holds the two equal.
        public static string seaShoreColor = "0.40,0.62,0.72";  // pale film near the coast
        public static float seaShoreAlpha = 0.45f;
        public static float seaShoreTiles = 2f;
        public static string seaDeepColor = "0.05,0.09,0.20";   // dark film far from it
        public static float seaDeepAlpha = 0.62f;
        public static float seaDeepTiles = 6f;
        // Per-sea film overrides (SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT; grammar in RM_WorldLookLists.FilmScale). The owner wants
        // The Chill "ominously dark compared to other bodies" (2026-10-24); the films lift its abyss face (value 22 reads 39)
        // and ring its islands, so it ships unlit (his round-3 pick, approved 2026-10-25). Applied while worldChillUnlit.
        public static string seaFilmOverrides = "RM_TheChill=off";
        public static string seaShader = "WorldOverlayTransparentLit";
        // the sea-floor view (SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR): basins darken away from the coast ABOVE (the land layer's
        // twin tile, "tile N under tile N"); the floor under dry land is dimmed as the continent above. Coast distance, not
        // elevation, keys the depth: the 2026-09-12 record's 1,448 water tiles have elev_m median -350 = its minimum, so an
        // elevation tint would be one flat colour.
        public static string seabedDepthColor = "0.02,0.03,0.08";
        public static float seabedDepthAlpha = 0.55f;
        public static float seabedDepthTiles = 8f;
        public static string seabedLandColor = "0,0,0";
        public static float seabedLandAlpha = 0.55f;
        public static string lastSeabedInfo = "never built";
        public static int seaQueue = 3502;          // above the ocean (3500), under the border blend (3505)

        // 3. BIOME SWIRLS (owner by card 2026-10-20, WORLD_FACES_REDRAW_ABYSS_ROT_RUST: "Biome-wide swirl layer"). Every tile
        //    of a listed biome is drawn again with that biome's swirl texture (World/RM_Swirls/<name>, RGBA, alpha = the
        //    swirl) on the transparent lit overlay. UVs are the vertex position projected onto ONE tangent plane per biome
        //    (at the mean of its tile centres), so the swirls run continuously across the whole biome with no tile seams and
        //    no pole stretch. Vertex alpha = swirlStrength x share of that biome among the tiles meeting at the corner, so
        //    the layer fades out across the biome border instead of stopping on a hex line.
        public static string swirlBiomes = "RM_Abyss=Abyss,RM_TheRot=TheRot";
        // 4. SEA GLASS (TWILIGHT_GLASS_WIRE_INTO_SWIRL_LAYER): the same layer over a sea. The owner, 2026-10-24: the Twilight
        //    Sea has "a stained glass window-like layer of life growing just below it's surface everywhere"; his pick is the
        //    round-3 "panes v3" texture (world_water_variants PANES3), one repeat = 40 tile widths (@40, centre to centre).
        //    It sits over the face ripple at low alpha (the ripple shows through). Drawn while worldTwilightGlass.
        public static string glassBiomes = "RM_TwilightSea=TwilightGlass@40";
        public static float swirlStrength = 1f;
        public static float swirlUvScale = 0.035f;  // texture repeats per world unit (radius 100 planet): ~25 units per repeat
        public static float swirlLift = 0.004f;     // over the border blend (+0.003), under hills (+0.005) and rivers (+0.01)
        public static int swirlQueue = 3506;        // over the border blend (3505), under hills (3510)

        public static string lastInfo = "never built";

        static readonly FieldInfo SubMeshesField = AccessTools.Field(typeof(WorldDrawLayerBase), "subMeshes");
        // weak: a world reload drops its layers (WorldDrawLayerBase.Dispose destroys their meshes); a strong map would pin every dead layer
        static readonly System.Runtime.CompilerServices.ConditionalWeakTable<WorldDrawLayer_Terrain, List<LayerSubMesh>> Ours = new System.Runtime.CompilerServices.ConditionalWeakTable<WorldDrawLayer_Terrain, List<LayerSubMesh>>();
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
            ApplyHills("startup");
        }

        // SOFT HILLS (2026-10-20). Vanilla draws every hilly tile's decal from four SHARED materials
        // (WorldMaterials.SmallHills/LargeHills/Mountains/ImpassableMountains, World/Hills/*, a 2x2 atlas, white colour, no
        // biome tint; WorldDrawLayer_Hills). Their brown outlined blots read as stamped hexes on our faces. Ours
        // (World/RM_Hills/*, src/RimMandrake/Utils/art/world_hill_decals.py) are a dark neutral whose alpha carries soft,
        // rotation-invariant relief, so a hill takes its biome's own hue. Swapping the texture on the shared material
        // takes effect at once, without a redraw. Off restores the textures captured here.
        static readonly string[][] HillMats = {
            new[] { "SmallHills", "SmallHills" }, new[] { "LargeHills", "LargeHills" },
            new[] { "Mountains", "Mountains" }, new[] { "ImpassableMountains", "Impassable" } };
        static readonly Dictionary<string, Texture> VanillaHillTex = new Dictionary<string, Texture>();
        public static bool hillsApplied;

        public static string ApplyHills(string why)
        {
            bool on = RM_BiomesSettings.worldSoftHills;
            int n = 0;
            try
            {
                foreach (string[] h in HillMats)
                {
                    FieldInfo f = typeof(WorldMaterials).GetField(h[0], BindingFlags.Static | BindingFlags.Public);
                    if (!(f?.GetValue(null) is Material m)) continue;
                    if (!VanillaHillTex.ContainsKey(h[0])) VanillaHillTex[h[0]] = m.mainTexture;
                    Texture2D ours = on ? ContentFinder<Texture2D>.Get("World/RM_Hills/" + h[1], false) : null;
                    if (on && ours == null)
                        Log.WarningOnce("[RimMandrake.Biomes] soft hills: World/RM_Hills/" + h[1] + " not found (is the mod that ships it loaded?); vanilla " + h[0] + " kept", 0x524c4833 + h[0].GetHashCode());
                    m.mainTexture = ours != null ? ours : VanillaHillTex[h[0]];
                    if (ours != null) n++;
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Biomes] soft hills failed, planet keeps vanilla hills: " + e.Message);
            }
            hillsApplied = on;
            return "hills " + (on ? n + "/4 ours" : "vanilla") + " (" + why + ")";
        }

        static void RegeneratePostfix(ref IEnumerable __result, WorldDrawLayer_Terrain __instance)
        {
            __result = Wrap(__result, __instance);
        }

        static IEnumerable Wrap(IEnumerable inner, WorldDrawLayer_Terrain layer)
        {
            RemoveOurs(layer);
            foreach (object o in inner) yield return o;
            if (layer.planetLayer == null) yield break;
            bool floor = IsSeabedLayer(layer.planetLayer);
            if (!layer.planetLayer.IsRootSurface && !(floor && RM_BiomesSettings.worldSeabedShading)) yield break;
            List<LayerSubMesh> lastMine = new List<LayerSubMesh>();
            try
            {
                var sb = new StringBuilder();
                var mine = new List<LayerSubMesh>();
                lastMine = mine;
                if (floor)
                {
                    sb.Append(BuildSeabed(layer, mine));
                    if (RM_BiomesSettings.worldBorderBlend) sb.Append(" ").Append(BuildBlend(layer, mine));
                }
                else
                {
                    if (RM_BiomesSettings.worldSeaDepth) sb.Append(BuildSea(layer, mine));
                    if (RM_BiomesSettings.worldBorderBlend) sb.Append(" ").Append(BuildBlend(layer, mine));
                    if (RM_BiomesSettings.worldBiomeSwirls) sb.Append(" ").Append(BuildSwirls(layer, mine, swirlBiomes, false, "swirls"));
                    if (RM_BiomesSettings.worldTwilightGlass) sb.Append(" ").Append(BuildSwirls(layer, mine, glassBiomes, true, "glass"));
                    if (RM_BiomesSettings.worldBiomeDecals) sb.Append(" ").Append(RM_WorldDecals.Build(layer, mine));
                }
                var subs = SubMeshes(layer);
                foreach (LayerSubMesh sm in mine)
                {
                    if (sm.verts.Count == 0) continue;
                    sm.FinalizeMesh(MeshParts.All);
                    subs.Add(sm);
                }
                Ours.Remove(layer);
                Ours.Add(layer, mine);
                if (floor) lastSeabedInfo = sb.ToString().Trim();
                else lastInfo = sb.ToString().Trim();
            }
            catch (Exception e)
            {
                foreach (LayerSubMesh sm in lastMine) { SubMeshes(layer).Remove(sm); if (sm.mesh != null) UnityEngine.Object.Destroy(sm.mesh); }
                if (floor) lastSeabedInfo = "failed: " + e;
                else lastInfo = "failed: " + e;
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
        /// <summary>The water tiles of a layer (by isWater), the corners they share with dry tiles (the coast), one tile
        /// spacing measured from the water tiles themselves, and the distance of a point to the coast in tile spacings
        /// (capped at maxTiles). Null when the layer has no water tile. Shared by the sea films and the sea-floor view.</summary>
        sealed class CoastField
        {
            public List<int> water;
            public HashSet<Vector3> coast;
            public float tileSpacing;
            public System.Func<Vector3, float> distTiles;
        }

        static CoastField BuildCoastField(PlanetLayer pl, System.Func<int, bool> isWater, float maxTiles)
        {
            var verts = new List<Vector3>();
            var nbs = new List<PlanetTile>();
            var nbVerts = new List<List<Vector3>>();
            var coast = new HashSet<Vector3>();
            var water = new List<int>();
            for (int i = 0; i < pl.TilesCount; i++)
            {
                if (!isWater(i)) continue;
                water.Add(i);
                pl.GetTileNeighbors(i, nbs);
                pl.GetTileVertices(i, verts);
                while (nbVerts.Count < nbs.Count) nbVerts.Add(new List<Vector3>());
                for (int k = 0; k < nbs.Count; k++)
                {
                    if (isWater(nbs[k].tileId)) continue;
                    pl.GetTileVertices(nbs[k].tileId, nbVerts[k]);
                    foreach (Vector3 v in verts) if (nbVerts[k].Contains(v)) coast.Add(v);
                }
            }
            if (water.Count == 0) return null;
            float cell = 0.05f;
            var buckets = new Dictionary<long, List<Vector3>>();
            foreach (Vector3 c in coast) Bucket(buckets, Key(c.normalized, cell)).Add(c.normalized);
            float radius = pl.GetTileCenter(water[0]).magnitude;
            // the water tiles' own mean size, not 4 pi r^2 / TilesCount: a partial-coverage planet (Ash'karr) holds
            // fewer tiles than its sphere, so that formula over-states the spacing and draws every film too narrow.
            float spacingSum = 0f;
            int spacingN = 0;
            foreach (int i in water)
            {
                pl.GetTileVertices(i, verts);
                if (verts.Count < 3) continue;
                spacingSum += TileSpacingOf(verts, pl.GetTileCenter(i));
                spacingN++;
            }
            float tileSpacing = spacingN > 0 ? spacingSum / spacingN : 1f;
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
            return new CoastField { water = water, coast = coast, tileSpacing = tileSpacing, distTiles = distTiles };
        }

        static string BuildSea(WorldDrawLayer_Terrain layer, List<LayerSubMesh> mine)
        {
            PlanetLayer pl = layer.planetLayer;
            CoastField cf = BuildCoastField(pl, i => { BiomeDef a = pl[i].PrimaryBiome; return a != null && a.isWaterBiome; },
                Mathf.Max(seaShoreTiles, seaDeepTiles, 0.5f));
            if (cf == null) return "sea: no water tiles";
            var verts = new List<Vector3>();
            List<int> water = cf.water;
            HashSet<Vector3> coast = cf.coast;
            System.Func<Vector3, float> distTiles = cf.distTiles;
            Material shoreMat = FlatMat(seaShoreColor, seaQueue);
            Material deepMat = FlatMat(seaDeepColor, seaQueue + 1);
            LayerSubMesh shore = null, deep = null;
            float windSign = 0f;
            int n = 0, unlit = 0;
            var filmScales = new Dictionary<BiomeDef, float>();
            foreach (int i in water)
            {
                BiomeDef wb = pl[i].PrimaryBiome;
                if (!filmScales.TryGetValue(wb, out float filmScale))
                    filmScales[wb] = filmScale = RM_BiomesSettings.worldChillUnlit ? RM_WorldLookLists.FilmScale(seaFilmOverrides, wb.defName) : 1f;
                if (filmScale <= 0f) { unlit++; continue; }
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
                EmitSeaTile(shore, pts, verts.Count, center, windSign, d => filmScale * seaShoreAlpha * Mathf.Pow(1f - Mathf.Clamp01(d / Mathf.Max(0.01f, seaShoreTiles)), 2f), dist);
                EmitSeaTile(deep, pts, verts.Count, center, windSign, d => filmScale * seaDeepAlpha * Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(d / Mathf.Max(0.01f, seaDeepTiles))), dist);
                n++;
            }
            return "sea: " + n + " water tiles shaded from " + coast.Count + " coast vertices" + (unlit > 0 ? ", " + unlit + " unlit" : "");
        }

        /// <summary>The sea-floor layer of DivingInteraction, by def name: this assembly takes no reference to that mod.</summary>
        public static bool IsSeabedLayer(PlanetLayer pl) => pl?.Def != null && pl.Def.defName == "RM_SeabedLayer";

        // ---------------------------------------------------------------- the sea-floor view
        // Each floor tile i lies under land-layer tile i. Under water: a dark film whose alpha rises with the distance from
        // the coast above (the deep basins), over seabedDepthTiles. Under dry land: a flat dim film, so the continents
        // above read as shapes on the floor instead of as bedrock noise.
        static string BuildSeabed(WorldDrawLayer_Terrain layer, List<LayerSubMesh> mine)
        {
            PlanetLayer pl = layer.planetLayer;
            PlanetLayer surf = Find.WorldGrid?.Surface;
            if (surf == null || surf.TilesCount != pl.TilesCount) return "seabed: no land layer of the same tiles above";
            System.Func<int, bool> wet = i => { BiomeDef a = surf[i].PrimaryBiome; return a != null && a.isWaterBiome; };
            CoastField cf = BuildCoastField(pl, wet, Mathf.Max(seabedDepthTiles, 0.5f));
            Material deepMat = FlatMat(seabedDepthColor, seaQueue + 1);
            Material landMat = FlatMat(seabedLandColor, seaQueue + 2);
            var verts = new List<Vector3>();
            LayerSubMesh deep = null, land = null;
            float windSign = 0f;
            int basin = 0, above = 0;
            for (int i = 0; i < pl.TilesCount; i++)
            {
                bool w = wet(i);
                if (w && cf == null) continue;
                pl.GetTileVertices(i, verts);
                if (verts.Count < 3) continue;
                Vector3 center = pl.GetTileCenter(i);
                if (windSign == 0f)
                    windSign = Mathf.Sign(Vector3.Dot(Vector3.Cross(verts[1] - verts[2], verts[0] - verts[2]), center));
                var pts = new List<Vector3> { center };
                foreach (Vector3 v in verts) pts.Add(center + (v - center) * 0.5f);
                foreach (Vector3 v in verts) pts.Add(v);
                var dist = new float[pts.Count];
                if (w)
                {
                    if (deep == null || deep.verts.Count > 38000) { deep = new LayerSubMesh(new Mesh(), deepMat); mine.Add(deep); }
                    for (int q = 0; q < pts.Count; q++) dist[q] = cf.coast.Contains(pts[q]) ? 0f : cf.distTiles(pts[q]);
                    EmitSeaTile(deep, pts, verts.Count, center, windSign,
                        d => seabedDepthAlpha * Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(d / Mathf.Max(0.01f, seabedDepthTiles))), dist);
                    basin++;
                }
                else
                {
                    if (land == null || land.verts.Count > 38000) { land = new LayerSubMesh(new Mesh(), landMat); mine.Add(land); }
                    EmitSeaTile(land, pts, verts.Count, center, windSign, d => seabedLandAlpha, dist);
                    above++;
                }
            }
            return "seabed: " + basin + " basin tiles, " + above + " under land";
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

        // ---------------------------------------------------------------- biome swirls
        static readonly Dictionary<string, Material> SwirlMats = new Dictionary<string, Material>();

        static Dictionary<BiomeDef, RM_WorldLookLists.Entry> SwirlMap(string list, bool allowWater)
        {
            var map = new Dictionary<BiomeDef, RM_WorldLookLists.Entry>();
            foreach (RM_WorldLookLists.Entry e in RM_WorldLookLists.Entries(list))
            {
                BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail(e.biome);
                if (b != null && (allowWater || !b.isWaterBiome)) map[b] = e;
            }
            return map;
        }

        static Material SwirlMat(string name)
        {
            if (SwirlMats.TryGetValue(name, out Material m)) return m;
            Texture2D tex = ContentFinder<Texture2D>.Get("World/RM_Swirls/" + name, false);
            if (tex == null)
                Log.WarningOnce("[RimMandrake.Biomes] biome swirls: World/RM_Swirls/" + name + " not found (is the mod that ships it loaded?); no swirls there", 0x52535731 + name.GetHashCode());
            else
            {
                tex.wrapMode = TextureWrapMode.Repeat;
                m = new Material(ResolveShader(blendShader)) { mainTexture = tex, renderQueue = swirlQueue };
            }
            SwirlMats[name] = m;   // null is cached too: one warning, then skip
            return m;
        }

        static string BuildSwirls(WorldDrawLayer_Terrain layer, List<LayerSubMesh> mine, string list, bool allowWater, string label)
        {
            PlanetLayer pl = layer.planetLayer;
            Dictionary<BiomeDef, RM_WorldLookLists.Entry> map = SwirlMap(list, allowWater);
            if (map.Count == 0) return label + ": no listed biome loaded";
            var sw = System.Diagnostics.Stopwatch.StartNew();
            // one tangent frame per biome, at the mean of its tile centres
            var sum = new Dictionary<BiomeDef, Vector3>();
            var spacingSum = new Dictionary<BiomeDef, float>();   // summed TileSpacingOf of the biome's tiles
            var count = new Dictionary<BiomeDef, int>();
            var tiles = new List<int>();
            var tv = new List<Vector3>();
            for (int i = 0; i < pl.TilesCount; i++)
            {
                BiomeDef a = pl[i].PrimaryBiome;
                if (a == null || !map.ContainsKey(a)) continue;
                tiles.Add(i);
                Vector3 c = pl.GetTileCenter(i);
                sum.TryGetValue(a, out Vector3 s);
                sum[a] = s + c;
                if (map[a].widthsPerRepeat > 0f)
                {
                    pl.GetTileVertices(i, tv);
                    spacingSum.TryGetValue(a, out float ss);
                    spacingSum[a] = ss + TileSpacingOf(tv, c);
                    count.TryGetValue(a, out int cn);
                    count[a] = cn + 1;
                }
            }
            if (tiles.Count == 0) return label + ": 0 tiles of " + map.Count + " listed biomes";
            // texture repeats per world unit, per biome. A hex's centre-to-centre width is sqrt(3) x its circumradius, and
            // TileSpacingOf is 1.612 x it, so width = spacing x 1.7320508 / 1.612.
            var uvScale = new Dictionary<BiomeDef, float>();
            foreach (var kv in map)
            {
                float width = count.TryGetValue(kv.Key, out int cn) && cn > 0 ? (1.7320508f / 1.612f) * spacingSum[kv.Key] / cn : 0f;
                uvScale[kv.Key] = RM_WorldLookLists.UvScale(kv.Value.widthsPerRepeat, width, swirlUvScale);
            }
            var frame = new Dictionary<BiomeDef, Vector3[]>();
            foreach (var kv in sum)
            {
                Vector3 n = kv.Value.sqrMagnitude > 1e-6f ? kv.Value.normalized : Vector3.up;
                Vector3 t = Vector3.Cross(n, Mathf.Abs(n.y) < 0.9f ? Vector3.up : Vector3.right).normalized;
                frame[kv.Key] = new[] { t, Vector3.Cross(n, t).normalized };
            }
            var current = new Dictionary<Material, LayerSubMesh>();
            var verts = new List<Vector3>();
            var nbs = new List<PlanetTile>();
            var nbVerts = new List<List<Vector3>>();
            float windSign = 0f;
            int drawn = 0, missing = 0;
            foreach (int i in tiles)
            {
                BiomeDef a = pl[i].PrimaryBiome;
                Material mat = SwirlMat(map[a].texture);
                float uvs = uvScale[a];
                if (mat == null) { missing++; continue; }
                pl.GetTileVertices(i, verts);
                if (verts.Count < 3) continue;
                Vector3 center = pl.GetTileCenter(i);
                if (windSign == 0f)
                    windSign = Mathf.Sign(Vector3.Dot(Vector3.Cross(verts[1] - verts[2], verts[0] - verts[2]), center));
                pl.GetTileNeighbors(i, nbs);
                while (nbVerts.Count < nbs.Count) nbVerts.Add(new List<Vector3>());
                for (int k = 0; k < nbs.Count; k++) pl.GetTileVertices(nbs[k].tileId, nbVerts[k]);
                if (!current.TryGetValue(mat, out LayerSubMesh sm) || sm.verts.Count > 38000)
                {
                    sm = new LayerSubMesh(new Mesh(), mat);
                    current[mat] = sm;
                    mine.Add(sm);
                }
                Vector3[] f = frame[a];
                int b0 = sm.verts.Count;
                Vector3 pc = center + center.normalized * swirlLift;
                sm.verts.Add(pc);
                sm.uvs.Add(new Vector3(Vector3.Dot(center, f[0]) * uvs, Vector3.Dot(center, f[1]) * uvs, 0f));
                sm.colors.Add(new Color32(255, 255, 255, (byte)Mathf.RoundToInt(Mathf.Clamp01(swirlStrength) * 255f)));
                for (int j = 0; j < verts.Count; j++)
                {
                    int total = 1, same = 1;
                    for (int k = 0; k < nbs.Count; k++)
                    {
                        if (!nbVerts[k].Contains(verts[j])) continue;
                        total++;
                        if (pl[nbs[k].tileId].PrimaryBiome == a) same++;
                    }
                    Vector3 p = verts[j] + verts[j].normalized * swirlLift;
                    sm.verts.Add(p);
                    sm.uvs.Add(new Vector3(Vector3.Dot(verts[j], f[0]) * uvs, Vector3.Dot(verts[j], f[1]) * uvs, 0f));
                    sm.colors.Add(new Color32(255, 255, 255, (byte)Mathf.RoundToInt(Mathf.Clamp01(swirlStrength * same / total) * 255f)));
                }
                for (int j = 0; j < verts.Count; j++)
                    Tri(sm, b0, b0 + 1 + j, b0 + 1 + (j + 1) % verts.Count, center, windSign);
                drawn++;
            }
            return label + ": " + drawn + " tiles in " + sum.Count + " biomes" + (missing > 0 ? ", " + missing + " without texture" : "")
                   + ", " + sw.ElapsedMilliseconds + " ms";
        }

        static void Tri(LayerSubMesh sm, int a, int b, int c, Vector3 center, float windSign)
        {
            // order (c, b, a) like vanilla, then flip if the facing differs from vanilla's
            Vector3 pa = sm.verts[a], pb = sm.verts[b], pc = sm.verts[c];
            float s = Mathf.Sign(Vector3.Dot(Vector3.Cross(pb - pc, pa - pc), center));
            if (s == windSign) { sm.tris.Add(c); sm.tris.Add(b); sm.tris.Add(a); }
            else { sm.tris.Add(a); sm.tris.Add(b); sm.tris.Add(c); }
        }

        // ---------------------------------------------------------------- tile geometry
        // The size of one tile from its own corners: sqrt(area) of a regular hex = 1.612 x its mean circumradius. The one
        // definition of "a tile spacing" for every world overlay of this assembly (sea films here, glyphs in RM_WorldDecals).
        public static float TileSpacingOf(List<Vector3> verts, Vector3 center)
        {
            if (verts == null || verts.Count == 0) return 0f;
            float circ = 0f;
            foreach (Vector3 v in verts) circ += (v - center).magnitude;
            return 1.612f * circ / verts.Count;
        }

        static void DestroyAll(IEnumerable<Material> mats)
        {
            foreach (Material m in mats) if (m != null) UnityEngine.Object.Destroy(m);
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
            // destroy, not only forget: each Set (a bridge tuning) would otherwise leak one Material per cached entry
            DestroyAll(BlendMats.Values);
            DestroyAll(FlatMats.Values);
            DestroyAll(SwirlMats.Values);
            BlendMats.Clear();
            FlatMats.Clear();
            SwirlMats.Clear();
            // every built layer still draws with the destroyed Materials: redraw them all, the sea-floor layer included
            // (jawa/world_commit regenerates the surface layer only, so the floor would keep them until its next redraw)
            if (Current.ProgramState == ProgramState.Playing) Find.World?.renderer?.SetAllLayersDirty();
            return key + " = " + f.GetValue(null) + " (every world layer redraws next frame)";
        }

        public static string Info()
        {
            var sb = new StringBuilder(lastInfo);
            foreach (FieldInfo f in typeof(RM_WorldLook).GetFields(BindingFlags.Static | BindingFlags.Public))
                if (f.Name != "lastInfo") sb.Append(" | ").Append(f.Name).Append('=').Append(f.GetValue(null));
            sb.Append(" | blend=").Append(RM_BiomesSettings.worldBorderBlend).Append(" seaDepth=").Append(RM_BiomesSettings.worldSeaDepth)
              .Append(" swirls=").Append(RM_BiomesSettings.worldBiomeSwirls).Append(" decals=").Append(RM_BiomesSettings.worldBiomeDecals)
              .Append(" chillUnlit=").Append(RM_BiomesSettings.worldChillUnlit).Append(" glass=").Append(RM_BiomesSettings.worldTwilightGlass);
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
