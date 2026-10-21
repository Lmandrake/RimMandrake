using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // SUN-LIT PEAKS (WORLD_MOUNTAINS_REDRAW_PEAKS_NOT_FIELDS, owner by card 2026-10-20: "Peaks lit toward the sun").
    //
    // Vanilla WorldDrawLayer_Hills prints one quad per hilly tile from four shared materials with Rand.Range(0, 360)
    // rotation, so no sprite can carry a light direction (RimSage, WorldDrawLayer_Hills.Regenerate). Here a postfix lets
    // vanilla build, then empties the vanilla hill submeshes and prints our own quads: the same tiles (hilly, no landmark),
    // but each quad TURNED so its texture +V axis points along the ground toward the substellar point. The atlases
    // (World/RM_Peaks/<Kind>[_Snowy], src/RimMandrake/Utils/art/world_peak_decals.py) are plan-view peak clusters lit from
    // +V, so every lit face on the planet faces the one sun (standing ruling "One Direct Sun, a pure function of geometry").
    //   * atlas row (indexY) 0 = high sun (arc < highSunArc, and the night side, which casts no shadow); row 1 = low sun,
    //     long shadows (highSunArc <= arc <= 90);
    //   * "_Snowy" where the tile's mean temperature is below snowBelowC;
    //   * tiles carrying a road or river get no peak (skipRoadsRivers), so routes stay legible;
    //   * a hero biome can ship its own set at World/RM_Peaks/<BiomeDefName>/<Kind>[_Snowy] (optional, falls back).
    // Off (Mod Settings "Planet: sun-lit mountain peaks") leaves vanilla's quads alone (and the soft hill textures).
    // Tunables are public statics: jawa/static_call RimMandrake.Biomes.RM_WorldPeaks Set "key|value", then world_commit.
    [StaticConstructorOnStartup]
    public static class RM_WorldPeaks
    {
        public static float substellarLat = 0f;     // Ash'karr: (0, 0), PlanetGeometryDef in AshkarrWeatherSuite
        public static float substellarLon = 0f;
        public static float highSunArc = 40f;
        public static float snowBelowC = -8f;
        public static bool skipRoadsRivers = true;
        public static float sizeSmall = 1.1f, sizeLarge = 1.2f, sizeMountains = 1.32f, sizeImpassable = 1.42f;   // the art fills ~0.88 of its cell: >1 lets a range overlap into a massif
        public static float jitterScale = 0.5f;     // times vanilla's centre jitter
        public static float lift = 0.005f;          // vanilla's hill lift (border blend sits under it at 0.003)
        public static string lastInfo = "never built";

        static readonly string[] Kinds = { "SmallHills", "LargeHills", "Mountains", "Impassable" };
        static readonly float[] Jitter = { 0.37f, 0.2f, 0.08f, 0.08f };
        static readonly FieldInfo SubMeshesField = AccessTools.Field(typeof(WorldDrawLayerBase), "subMeshes");
        static readonly Dictionary<string, Material> Mats = new Dictionary<string, Material>();

        static RM_WorldPeaks()
        {
            try
            {
                new Harmony("mandrake.rm.biomes.worldpeaks").Patch(AccessTools.Method(typeof(WorldDrawLayer_Hills), "Regenerate"),
                    postfix: new HarmonyMethod(typeof(RM_WorldPeaks), nameof(RegeneratePostfix)));
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Biomes] sun-lit peaks patch failed, planet keeps vanilla hills: " + e.Message);
            }
        }

        static void RegeneratePostfix(ref IEnumerable __result, WorldDrawLayer_Hills __instance)
        {
            __result = Wrap(__result, __instance);
        }

        static IEnumerable Wrap(IEnumerable inner, WorldDrawLayer_Hills layer)
        {
            foreach (object o in inner) yield return o;
            if (!RM_BiomesSettings.worldSunPeaks || layer.planetLayer == null || !layer.planetLayer.IsRootSurface) yield break;
            try
            {
                lastInfo = Build(layer);
            }
            catch (Exception e)
            {
                lastInfo = "failed: " + e.Message;
                Log.Warning("[RimMandrake.Biomes] sun-lit peaks failed, planet keeps vanilla hills: " + e);
            }
        }

        static Material Mat(string key)
        {
            if (Mats.TryGetValue(key, out Material m)) return m;
            Texture2D tex = ContentFinder<Texture2D>.Get("World/RM_Peaks/" + key, false);
            m = tex != null ? MaterialPool.MatFrom("World/RM_Peaks/" + key, ShaderDatabase.WorldOverlayTransparentLit, 3510) : null;
            Mats[key] = m;
            return m;
        }

        static Material MatFor(BiomeDef biome, int kind, bool snowy)
        {
            string k = Kinds[kind] + (snowy ? "_Snowy" : "");
            Material m = biome != null ? Mat(biome.defName + "/" + k) : null;
            return m ?? Mat(k) ?? (snowy ? Mat(Kinds[kind]) : null);
        }

        public static Vector3 SubstellarDir()
        {
            // inverse of PlanetLayer.LongLatOf: long = atan2(x, -z), lat = asin(y / r)
            float la = substellarLat * Mathf.Deg2Rad, lo = substellarLon * Mathf.Deg2Rad;
            return new Vector3(Mathf.Cos(la) * Mathf.Sin(lo), Mathf.Sin(la), -Mathf.Cos(la) * Mathf.Cos(lo));
        }

        static string Build(WorldDrawLayer_Hills layer)
        {
            PlanetLayer pl = layer.planetLayer;
            if (Mat("Mountains") == null)
            {
                Log.WarningOnce("[RimMandrake.Biomes] sun-lit peaks: World/RM_Peaks/Mountains not found (is TerminalBiomes loaded?); vanilla hills kept", 0x524d504b);
                return "no textures; vanilla kept";
            }
            var subs = (List<LayerSubMesh>)SubMeshesField.GetValue(layer);
            var vanilla = new HashSet<Material> { WorldMaterials.SmallHills, WorldMaterials.LargeHills, WorldMaterials.Mountains, WorldMaterials.ImpassableMountains };
            foreach (LayerSubMesh sm in subs)
                if (vanilla.Contains(sm.material)) sm.Clear(MeshParts.All);   // unfinalized = not drawn; vanilla refills it next time

            Vector3 sun = SubstellarDir();
            int drawn = 0, skippedPath = 0, snowyN = 0, lowSun = 0;
            var touched = new HashSet<LayerSubMesh>();
            Rand.PushState();
            Rand.Seed = Find.World.info.Seed ^ 0x5eed;
            try
            {
                for (int i = 0; i < pl.TilesCount; i++)
                {
                    Tile tile = pl[i];
                    int kind;
                    switch (tile.hilliness)
                    {
                        case Hilliness.SmallHills: kind = 0; break;
                        case Hilliness.LargeHills: kind = 1; break;
                        case Hilliness.Mountainous: kind = 2; break;
                        case Hilliness.Impassable: kind = 3; break;
                        default: continue;
                    }
                    if (tile.Landmark != null) continue;
                    if (skipRoadsRivers && tile is SurfaceTile st && ((st.Roads != null && st.Roads.Count > 0) || (st.Rivers != null && st.Rivers.Count > 0)))
                    {
                        skippedPath++;
                        continue;
                    }
                    bool snowy = tile.temperature < snowBelowC;
                    Material mat = MatFor(tile.PrimaryBiome, kind, snowy);
                    if (mat == null) continue;
                    LayerSubMesh sm = GetOrAdd(subs, mat);
                    touched.Add(sm);

                    PlanetTile pt = new PlanetTile(i, pl);
                    Vector3 c = pl.GetTileCenter(pt);
                    Vector3 n = c.normalized;
                    float arc = Mathf.Acos(Mathf.Clamp(Vector3.Dot(n, sun), -1f, 1f)) * Mathf.Rad2Deg;
                    int row = (arc >= highSunArc && arc <= 90f) ? 1 : 0;
                    float rot = SunRotation(c, n, sun);
                    float mag = c.magnitude;
                    Vector3 pos = (c + Rand.UnitVector3 * (Rand.Value * Jitter[kind] * jitterScale * pl.AverageTileSize)).normalized * mag;
                    float size = (kind == 0 ? sizeSmall : kind == 1 ? sizeLarge : kind == 2 ? sizeMountains : sizeImpassable) * pl.GetTileSize(pt);
                    WorldRendererUtility.PrintQuadTangentialToPlanet(pos, c, size, lift, sm, counterClockwise: false, rot, printUVs: false);
                    WorldRendererUtility.PrintTextureAtlasUVs(Rand.Range(0, 2), row, 2, 2, sm);
                    drawn++;
                    if (snowy) snowyN++;
                    if (row == 1) lowSun++;
                }
            }
            finally
            {
                Rand.PopState();
            }
            foreach (LayerSubMesh sm in touched)
                if (sm.verts.Count > 0 && !sm.finalized) sm.FinalizeMesh(MeshParts.All);
            return "peaks " + drawn + " (low sun " + lowSun + ", snowy " + snowyN + ", skipped on road/river " + skippedPath + ")";
        }

        // The rotation (degrees, about the tile normal) that turns the quad's second tangent (texture +V) onto the ground
        // direction toward the sun. GetTangentsToPlanet applies AngleAxis(rotation, normal) to the rotation-0 frame, so the
        // sign is settled by trying both and keeping the one that lands on the sun direction.
        static float SunRotation(Vector3 c, Vector3 n, Vector3 sun)
        {
            Vector3 t = sun - Vector3.Dot(sun, n) * n;
            if (t.sqrMagnitude < 1e-8f) return 0f;   // the substellar / antistellar tile: the sun has no ground direction
            t.Normalize();
            WorldRendererUtility.GetTangentsToPlanet(c, out Vector3 first, out Vector3 second, 0f);
            float a = Vector3.Angle(second, t);
            float best = a, bestDot = Vector3.Dot(Quaternion.AngleAxis(a, n) * second, t);
            float d2 = Vector3.Dot(Quaternion.AngleAxis(-a, n) * second, t);
            if (d2 > bestDot) best = -a;
            return best;
        }

        static LayerSubMesh GetOrAdd(List<LayerSubMesh> subs, Material mat)
        {
            for (int i = 0; i < subs.Count; i++)
                if (subs[i].material == mat && !subs[i].finalized && subs[i].verts.Count < 40000) return subs[i];
            var sm = new LayerSubMesh(new Mesh(), mat);
            subs.Add(sm);
            return sm;
        }

        public static string Set(string key, string value)
        {
            FieldInfo f = typeof(RM_WorldPeaks).GetField(key, BindingFlags.Static | BindingFlags.Public);
            if (f == null) return "no field " + key;
            f.SetValue(null, Convert.ChangeType(value, f.FieldType, System.Globalization.CultureInfo.InvariantCulture));
            if (key != "lastInfo") Mats.Clear();
            return key + " = " + f.GetValue(null);
        }

        public static string Info() => lastInfo + "; on=" + RM_BiomesSettings.worldSunPeaks + " substellar=(" + substellarLat + "," + substellarLon + ")";
    }
}
