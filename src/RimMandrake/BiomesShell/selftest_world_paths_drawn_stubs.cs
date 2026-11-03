// Offline execution harness for Source/RM_WorldPathsDrawn.cs (RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT).
// selftest_world_paths_drawn.py compiles the REAL RM_WorldPathsDrawn.cs and RM_RiverGraph.cs together with this file,
// which stands in for the engine: just enough of UnityEngine / HarmonyLib / Verse / RimWorld(.Planet) and of
// RM_WorldPaths for the drawn-path code to compile and run. Shapes follow the decompiled 1.6 types
// (OutputDirection is a struct; GetSubMesh(Material) is protected with an (out int) overload). Never shipped: the
// mod's csproj lists its sources by name. The harness reads commands from a file and prints raw results; the Python
// side decides what is right, from constants parsed out of the C#.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;

namespace UnityEngine
{
    public struct Color
    {
        public float r, g, b, a;
        public Color(float r, float g, float b, float a = 1f) { this.r = r; this.g = g; this.b = b; this.a = a; }
        public static Color white => new Color(1f, 1f, 1f, 1f);
        public static Color Lerp(Color x, Color y, float t)
        {
            t = Mathf.Clamp01(t);
            return new Color(x.r + (y.r - x.r) * t, x.g + (y.g - x.g) * t, x.b + (y.b - x.b) * t, x.a + (y.a - x.a) * t);
        }
        public static implicit operator Color32(Color c) => new Color32((byte)Math.Round(Mathf.Clamp01(c.r) * 255f),
            (byte)Math.Round(Mathf.Clamp01(c.g) * 255f), (byte)Math.Round(Mathf.Clamp01(c.b) * 255f), (byte)Math.Round(Mathf.Clamp01(c.a) * 255f));
    }

    public struct Color32
    {
        public byte r, g, b, a;
        public Color32(byte r, byte g, byte b, byte a) { this.r = r; this.g = g; this.b = b; this.a = a; }
        public static implicit operator Color(Color32 c) => new Color(c.r / 255f, c.g / 255f, c.b / 255f, c.a / 255f);
    }

    public static class Mathf
    {
        public static float Max(float a, float b) => a > b ? a : b;
        public static float Clamp01(float v) => v < 0f ? 0f : v > 1f ? 1f : v;
    }

    public class Material
    {
        public string name;
        public int renderQueue;
        public Material() { }
        public Material(Material m) { name = m.name; renderQueue = m.renderQueue; }
    }
}

namespace HarmonyLib
{
    public class Harmony
    {
        public readonly List<string> patched = new List<string>();
        public void Patch(MethodBase original, HarmonyMethod prefix = null, HarmonyMethod postfix = null)
            => patched.Add(original.DeclaringType.Name + "." + original.Name + " pre=" + (prefix?.Name ?? "-") + " post=" + (postfix?.Name ?? "-"));
    }

    public class HarmonyMethod
    {
        public readonly string Name;
        // Resolves like Harmony does: a missing method is an error, so a renamed callback cannot pass silently.
        public HarmonyMethod(Type t, string name)
        {
            if (t.GetMethod(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static) == null) throw new MissingMethodException(t.Name, name);
            Name = name;
        }
    }

    public static class AccessTools
    {
        const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static;
        public static MethodInfo Method(Type t, string name, Type[] args = null)
            => args == null ? t.GetMethod(name, All) : t.GetMethod(name, All, null, args, null);
    }
}

namespace Verse
{
    public class Def { public string defName; }

    public static class Log
    {
        public static void Message(string s) { }
        public static void Warning(string s) { }
    }
}

namespace RimWorld
{
    public class RoadDef : Verse.Def { }
    public class RiverDef : Verse.Def { public float widthOnWorld; }
    public class RoadWorldLayerDef : Verse.Def { public UnityEngine.Color color; }
}

namespace RimWorld.Planet
{
    using UnityEngine;

    public class Tile { public bool water; public bool WaterCovered => water; }

    public class SurfaceTile : Tile
    {
        public struct RiverLink { public PlanetTile neighbor; public RiverDef river; }
        public struct RoadLink { public PlanetTile neighbor; public RoadDef road; }
        public List<RiverLink> potentialRivers;
        public List<RoadLink> potentialRoads;
    }

    public class PlanetLayer
    {
        public readonly Dictionary<int, Tile> tiles = new Dictionary<int, Tile>();
        public int TilesCount = 1000000;
        public Tile this[int i] => tiles.TryGetValue(i, out Tile t) ? t : null;
        public void GetTileNeighbors(PlanetTile t, List<PlanetTile> outList) { outList.Clear(); }
    }

    public struct PlanetTile
    {
        public int tileId;
        public PlanetLayer layer;
        public PlanetTile(int id, PlanetLayer l) { tileId = id; layer = l; }
        public Tile Tile => layer?[tileId];
    }

    public class LayerSubMesh
    {
        public Material material;
        public readonly List<Color32> colors = new List<Color32>();
    }

    public class WorldDrawLayerBase
    {
        public PlanetLayer planetLayer;
        public readonly Dictionary<Material, LayerSubMesh> subMeshes = new Dictionary<Material, LayerSubMesh>();
        protected LayerSubMesh GetSubMesh(Material material) => GetSubMesh(material, out _);
        protected LayerSubMesh GetSubMesh(Material material, out int subMeshIndex)
        {
            subMeshIndex = 0;
            if (!subMeshes.TryGetValue(material, out LayerSubMesh m)) subMeshes[material] = m = new LayerSubMesh { material = material };
            return m;
        }
    }

    public class WorldDrawLayer_Paths : WorldDrawLayerBase
    {
        public struct OutputDirection { public PlanetTile neighbor; public float width; public float distortionFrequency, distortionIntensity; }

        // One record per call; per node two vertices, the outer one faded to alpha 0 as vanilla's edge fade does.
        // recolor: stands for FlowWorks' River Colours prefix, which recolours every river call before vanilla writes it.
        public readonly List<string> calls = new List<string>();
        public Color32? recolor;
        public void GeneratePaths(LayerSubMesh subMesh, PlanetTile tile, List<OutputDirection> nodes, Color32 color, bool allowSmoothTransition)
        {
            var inv = CultureInfo.InvariantCulture;
            var sb = new StringBuilder();
            sb.Append(subMesh.material.name).Append(' ').Append(tile.tileId).Append(' ')
              .Append(color.r).Append(',').Append(color.g).Append(',').Append(color.b).Append(',').Append(color.a)
              .Append(' ').Append(allowSmoothTransition ? 1 : 0);
            Color32 v = recolor ?? color;
            foreach (OutputDirection n in nodes)
            {
                sb.Append(' ').Append(n.neighbor.tileId).Append(':').Append(n.width.ToString("R", inv));
                subMesh.colors.Add(v);
                subMesh.colors.Add(new Color32(v.r, v.g, v.b, 0));
            }
            calls.Add(sb.ToString());
        }
    }

    public class WorldDrawLayer_Rivers : WorldDrawLayer_Paths { public void Regenerate() { } }
    public class WorldDrawLayer_Roads : WorldDrawLayer_Paths { }
}

namespace RimMandrake.Biomes
{
    using RimWorld;
    using UnityEngine;

    // Stand-in for the real RM_WorldPaths (which needs the whole engine): the switches and the hooks RM_WorldPathsDrawn reads.
    public static class RM_WorldPaths
    {
        public static bool applied, drawnRivers, wornRoads;
        public static Material WaterMaterial = new Material { name = "water" };
        public static readonly List<RoadWorldLayerDef> layers = new List<RoadWorldLayerDef>();
        public static RoadWorldLayerDef LayerOf(Color32 color)
        {
            foreach (RoadWorldLayerDef l in layers)
            {
                Color32 c = l.color;
                if (c.r == color.r && c.g == color.g && c.b == color.b) return l;
            }
            return null;
        }
    }
}

namespace DrawnHarness
{
    using HarmonyLib;
    using RimMandrake.Biomes;
    using RimWorld;
    using RimWorld.Planet;
    using UnityEngine;
    using Dir = RimWorld.Planet.WorldDrawLayer_Paths.OutputDirection;

    static class P
    {
        const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;
        static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
        static readonly Type T = typeof(RM_WorldPathsDrawn);
        static readonly PlanetLayer Layer = new PlanetLayer();
        static readonly StringBuilder O = new StringBuilder();
        // One river layer for every HI command, as in game: its highlight mesh accumulates tile after tile.
        static readonly WorldDrawLayer_Rivers HiLayer = new WorldDrawLayer_Rivers { planetLayer = Layer, recolor = new Color32(1, 2, 3, 200) };

        static string C(Color32 c) => c.r + "," + c.g + "," + c.b + "," + c.a;
        static Color32 ParseC(string s) { string[] p = s.Split(','); return new Color32(byte.Parse(p[0]), byte.Parse(p[1]), byte.Parse(p[2]), byte.Parse(p[3])); }
        static string Widths(List<Dir> nodes) { var sb = new StringBuilder(); foreach (Dir n in nodes) sb.Append(' ').Append(n.neighbor.tileId).Append(':').Append(n.width.ToString("R", Inv)); return sb.ToString(); }

        // "n:w" or "n:w:f" tokens from position 'from'.
        static List<Dir> Nodes(string[] p, int from, RM_RiverGraph.Result g, int tile)
        {
            var nodes = new List<Dir>();
            for (int i = from; i < p.Length; i++)
            {
                string[] q = p[i].Split(':');
                int n = int.Parse(q[0]);
                nodes.Add(new Dir { neighbor = new PlanetTile(n, Layer), width = float.Parse(q[1], Inv) });
                if (q.Length > 2 && g != null) g.linkFactor[RM_RiverGraph.Key(tile, n)] = float.Parse(q[2], Inv);
            }
            return nodes;
        }

        static void SetGraph(WorldDrawLayer_Rivers rl, RM_RiverGraph.Result g)
        {
            object table = T.GetField("graphs", All).GetValue(null);
            table.GetType().GetMethod("AddOrUpdate").Invoke(table, new object[] { rl, g });
        }

        static void Main(string[] a)
        {
            var h = new Harmony();
            T.GetMethod("Patch", All).Invoke(null, new object[] { h, new Material { name = "roads", renderQueue = 3540 }, 3530 });
            O.Append("PATCHED ").Append(string.Join(",", h.patched)).Append('\n');
            MethodInfo road = T.GetMethod("RoadPrefix", All), hiPost = T.GetMethod("HighlightPostfix", All), river = T.GetMethod("River", All);
            foreach (string raw in File.ReadAllLines(a[0]))
            {
                string[] p = raw.Split(' ');
                if (p[0] == "SET") { RM_WorldPaths.applied = p[1] == "1"; RM_WorldPaths.drawnRivers = p[2] == "1"; RM_WorldPaths.wornRoads = p[3] == "1"; }
                else if (p[0] == "LAYER") RM_WorldPaths.layers.Add(new RoadWorldLayerDef { defName = p[1], color = ParseC(p[2]) });
                else if (p[0] == "ROAD")
                {
                    // ROAD id layerColour - tile n:w:roadDef ... (each link its own road kind, listed in reverse order)
                    int tile = int.Parse(p[4]);
                    var nodes = new List<Dir>();
                    var st = new SurfaceTile { potentialRoads = new List<SurfaceTile.RoadLink>() };
                    for (int i = 5; i < p.Length; i++)
                    {
                        string[] q = p[i].Split(':');
                        var nb = new PlanetTile(int.Parse(q[0]), Layer);
                        nodes.Add(new Dir { neighbor = nb, width = float.Parse(q[1], Inv) });
                        st.potentialRoads.Insert(0, new SurfaceTile.RoadLink { neighbor = nb, road = new RoadDef { defName = q[2] } });
                    }
                    Layer.tiles[tile] = st;
                    var rl = new WorldDrawLayer_Roads { planetLayer = Layer };
                    var sub = new LayerSubMesh { material = new Material { name = "roads" } };
                    object[] args = { rl, sub, new PlanetTile(tile, Layer), nodes, ParseC(p[2]), true };
                    bool ret = (bool)road.Invoke(null, args);
                    O.Append("ROAD ").Append(p[1]).Append(' ').Append(ret ? 1 : 0).Append(' ').Append((bool)args[5] ? 1 : 0)
                     .Append(Widths((List<Dir>)args[3])).Append('\n');
                }
                else if (p[0] == "RIVER")
                {
                    // RIVER id bank(0/1) graph(0/1) tile dry water dark n:w[:f] ...
                    int tile = int.Parse(p[4]);
                    var rl = new WorldDrawLayer_Rivers { planetLayer = Layer };
                    var g = p[3] == "1" ? new RM_RiverGraph.Result() : null;
                    var nodes = Nodes(p, 8, g, tile);
                    if (g != null) { float dry = float.Parse(p[5], Inv); if (dry > 0f) g.dryness[tile] = dry; SetGraph(rl, g); }
                    object[] args = { rl, p[2] == "1", new PlanetTile(tile, Layer), nodes, ParseC(p[6]), ParseC(p[7]) };
                    Color32 c = (Color32)river.Invoke(null, args);
                    O.Append("RIVER ").Append(p[1]).Append(' ').Append(C(c)).Append(Widths((List<Dir>)args[3])).Append('\n');
                }
                else if (p[0] == "HI")
                {
                    // HI id material(water|bank) graph(0/1) tile dry colour n:w ...
                    int tile = int.Parse(p[4]);
                    var rl = HiLayer;
                    rl.calls.Clear();
                    var g = p[3] == "1" ? new RM_RiverGraph.Result() : null;
                    if (g != null) { float dry = float.Parse(p[5], Inv); if (dry > 0f) g.dryness[tile] = dry; SetGraph(rl, g); }
                    else T.GetField("graphs", All).GetValue(null).GetType().GetMethod("Remove").Invoke(T.GetField("graphs", All).GetValue(null), new object[] { rl });
                    var before = new List<Color32>();
                    foreach (LayerSubMesh m in rl.subMeshes.Values) before.AddRange(m.colors);
                    var mat = p[2] == "water" ? RM_WorldPaths.WaterMaterial : new Material { name = "bank" };
                    var sub = new LayerSubMesh { material = mat };
                    var nodes = Nodes(p, 7, null, tile);
                    hiPost.Invoke(null, new object[] { rl, sub, new PlanetTile(tile, Layer), nodes, ParseC(p[6]), true });
                    O.Append("HI ").Append(p[1]).Append(' ').Append(rl.calls.Count);
                    foreach (string call in rl.calls) O.Append(" | ").Append(call);
                    // earlier tiles' highlight vertices must come through untouched; only this call's are listed
                    var after = new List<Color32>();
                    foreach (LayerSubMesh m in rl.subMeshes.Values) after.AddRange(m.colors);
                    bool prior = after.Count >= before.Count;
                    for (int i = 0; prior && i < before.Count; i++) prior = C(after[i]) == C(before[i]);
                    O.Append(" | prior ").Append(prior ? 1 : 0).Append(" verts");
                    foreach (LayerSubMesh m in rl.subMeshes.Values)
                        for (int i = 0; i < m.colors.Count; i++) if (i >= before.Count) O.Append(' ').Append(m.material.name).Append('=').Append(C(m.colors[i]));
                    O.Append('\n');
                }
            }
            Console.Out.Write(O.ToString());
        }
    }
}
