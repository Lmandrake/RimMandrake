using System;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT (2026-11-02): world look 1c, the LOOK of rivers and roads (their colour is
    // FlowWorks' River Colours, RM_RiverColors.cs). Program: design/Jawa/worldbuilding/world_look_program_2026-10-24.md.
    //
    // How vanilla 1.6 draws a path (decompiled WorldDrawLayer_Paths.GeneratePaths): for each tile, a hexagon round the
    // centre sized by the widest link, then for each link a strip from the centre to the MIDPOINT of the shared hex edge,
    // node.width wide there. Each tile draws its own half of every link, so a link's width at the edge must be the same
    // from both tiles or the line steps at every hex edge. Every factor below is therefore per LINK (symmetric in its two
    // tiles), never per tile; only colour is per tile (one colour per GeneratePaths call), so a dry-end fade steps a little.
    //
    // Rivers ("Planet: drawn rivers"), from one pass over the river graph each time the river layer regenerates:
    //  * taper: a link's width x (HeadMin .. 1) by its mean distance from the nearest head, reaching 1 after TaperTiles;
    //  * mouths: a link touching a mouth (a leaf next to water, or a water tile) x MouthFan, fanning into the shore;
    //  * dry ends: a river system with no mouth dies inland; its widest leaf is the dry end, and the DryTiles links before
    //    it thin to DryMin and fade to DryTan (a thinning dry trace), with no highlight;
    //  * bank: pale (the water colour mixed BankPale toward PaleBank) instead of the dark water x bankShade;
    //  * highlight: a third mesh (queue 3535: above the water 3530, below roads 3540) down the middle of the water,
    //    HighlightWidth of its width, the water colour mixed HighlightMix toward white at HighlightAlpha.
    // Roads ("Planet: worn roads"), by a hash of the link (so the same link reads the same from both tiles):
    //  * DirtPath / DirtRoad: a DirtWornShare of links draw their dirt fill DirtWornWidth as wide, the dark casing showing
    //    through: a worn, dashed track;
    //  * StoneRoad: lighter fill (RM_WorldPaths.StoneWorn), solid;
    //  * AncientAsphaltRoad / Highway: an AncientGapShare of links are not drawn at all, every layer: broken into pieces.
    // Draw order is untouched (rivers 3520/3530 + this 3535, roads 3540), so overlays below rivers stay below.
    public static class RM_WorldPathsDrawn
    {
        public const float BankPale = 0.6f;
        public const float HighlightWidth = 0.35f;
        public const float HighlightMix = 0.3f;
        public const float HighlightAlpha = 0.5f;
        public const float DirtWornShare = 0.4f;
        public const float DirtWornWidth = 0.5f;
        public const float AncientGapShare = 0.25f;
        public static readonly Color PaleBank = new Color(0.80f, 0.74f, 0.60f);
        public static readonly Color DryTan = new Color(0.62f, 0.52f, 0.38f);

        // Weak keys: a river layer of an unloaded world takes its graph with it.
        static readonly ConditionalWeakTable<WorldDrawLayer_Rivers, RM_RiverGraph.Result> graphs = new ConditionalWeakTable<WorldDrawLayer_Rivers, RM_RiverGraph.Result>();
        static Material highlightMat;
        static MethodInfo getSubMesh;
        static bool inHighlight;
        static readonly List<WorldDrawLayer_Paths.OutputDirection> scratch = new List<WorldDrawLayer_Paths.OutputDirection>();
        static readonly List<WorldDrawLayer_Paths.OutputDirection> scratchHi = new List<WorldDrawLayer_Paths.OutputDirection>();
        static readonly List<PlanetTile> nbrs = new List<PlanetTile>();
        public static string lastGraph = "river graph never built";

        public static bool Rivers => RM_WorldPaths.applied && RM_WorldPaths.drawnRivers;
        public static bool Roads => RM_WorldPaths.applied && RM_WorldPaths.wornRoads;

        /// <summary>Called from RM_WorldPaths' static constructor with its Harmony instance; throws on a missing target.</summary>
        public static void Patch(Harmony h, Material roadMat, int waterQueue)
        {
            highlightMat = new Material(roadMat) { name = "RM_RiverHighlight", renderQueue = waterQueue + 5 };
            getSubMesh = AccessTools.Method(typeof(WorldDrawLayerBase), "GetSubMesh", new[] { typeof(Material) });
            MethodInfo regen = AccessTools.Method(typeof(WorldDrawLayer_Rivers), nameof(WorldDrawLayer_Rivers.Regenerate));
            MethodInfo gen = AccessTools.Method(typeof(WorldDrawLayer_Paths), nameof(WorldDrawLayer_Paths.GeneratePaths));
            if (getSubMesh == null || regen == null || gen == null) throw new Exception("GetSubMesh/Regenerate/GeneratePaths not found");
            h.Patch(regen, prefix: new HarmonyMethod(typeof(RM_WorldPathsDrawn), nameof(RegeneratePrefix)));
            h.Patch(gen, prefix: new HarmonyMethod(typeof(RM_WorldPathsDrawn), nameof(RoadPrefix)),
                postfix: new HarmonyMethod(typeof(RM_WorldPathsDrawn), nameof(HighlightPostfix)));
        }

        // One river layer per planet layer, and the renderer may interleave their regenerations: one graph per layer.
        static void RegeneratePrefix(WorldDrawLayer_Rivers __instance)
        {
            graphs.Remove(__instance);
            if (!Rivers) return;
            try
            {
                PlanetLayer layer = __instance.planetLayer;
                var links = new List<RM_RiverGraph.Link>();
                for (int i = 0; i < layer.TilesCount; i++)
                {
                    if (!(layer[i] is SurfaceTile st) || st.potentialRivers == null) continue;
                    foreach (SurfaceTile.RiverLink r in st.potentialRivers)
                        links.Add(new RM_RiverGraph.Link { a = i, b = r.neighbor.tileId, width = r.river?.widthOnWorld ?? 0f });
                }
                if (links.Count == 0) return;
                bool Water(int t) => t >= 0 && t < layer.TilesCount && layer[t].WaterCovered;
                bool Touches(int t)
                {
                    if (Water(t)) return true;
                    layer.GetTileNeighbors(new PlanetTile(t, layer), nbrs);
                    foreach (PlanetTile n in nbrs) if (Water(n.tileId)) return true;
                    return false;
                }
                RM_RiverGraph.Result g = RM_RiverGraph.Analyse(links, Water, Touches);
                graphs.Remove(__instance);
                graphs.Add(__instance, g);
                lastGraph = "drawn rivers: " + g.links + " links in " + g.systems + " systems, " + g.heads + " heads, "
                            + g.mouths + " mouths, " + g.dryEnds + " dry ends";
                Log.Message("[RimMandrake.Biomes] " + lastGraph);
            }
            catch (Exception e)
            {
                lastGraph = "river graph failed: " + e.Message;
                Log.Warning("[RimMandrake.Biomes] " + lastGraph + "; rivers keep one width per kind");
            }
        }

        static Color32 Mix(Color32 a, Color b, float t)
        {
            Color c = Color.Lerp(a, b, t);
            return new Color32((byte)(c.r * 255f), (byte)(c.g * 255f), (byte)(c.b * 255f), a.a);
        }

        /// <summary>Called by RM_WorldPaths.GeneratePathsPrefix once it has the final water colour of a river tile:
        /// widths per link, the pale bank, the dry fade. Returns the colour to draw.</summary>
        public static Color32 River(WorldDrawLayer_Paths layer, bool bank, PlanetTile tile,
            ref List<WorldDrawLayer_Paths.OutputDirection> nodes, Color32 water, Color32 darkBank)
        {
            if (!Rivers || nodes == null || !(layer is WorldDrawLayer_Rivers rl) || !graphs.TryGetValue(rl, out RM_RiverGraph.Result g))
                return bank ? darkBank : water;
            scratch.Clear();
            foreach (WorldDrawLayer_Paths.OutputDirection n in nodes)
            {
                WorldDrawLayer_Paths.OutputDirection m = n;
                if (g.linkFactor.TryGetValue(RM_RiverGraph.Key(tile.tileId, n.neighbor.tileId), out float f)) m.width = Mathf.Max(0f, n.width * f);
                scratch.Add(m);
            }
            nodes = scratch;
            g.dryness.TryGetValue(tile.tileId, out float dry);
            Color32 baseCol = bank ? Mix(water, PaleBank, BankPale) : water;
            return Mix(baseCol, DryTan, dry * 0.8f);
        }

        // After the water strip of a tile: the same strip again, narrower, on the highlight mesh. FlowWorks' River
        // Colours prefix recolours every river GeneratePaths call, so the highlight's colour is written over the
        // vertices it added afterwards (alpha kept 0 where vanilla fades to 0).
        static void HighlightPostfix(WorldDrawLayer_Paths __instance, LayerSubMesh subMesh, PlanetTile tile,
            List<WorldDrawLayer_Paths.OutputDirection> nodes, Color32 color, bool allowSmoothTransition)
        {
            if (inHighlight || !Rivers || subMesh == null || nodes == null || !(__instance is WorldDrawLayer_Rivers rl)) return;
            if (subMesh.material != RM_WorldPaths.WaterMaterial || !graphs.TryGetValue(rl, out RM_RiverGraph.Result g)) return;
            g.dryness.TryGetValue(tile.tileId, out float dry);
            if (dry > 0f) return;   // a dry trace has no shine
            scratchHi.Clear();
            foreach (WorldDrawLayer_Paths.OutputDirection n in nodes) { var m = n; m.width = n.width * HighlightWidth; scratchHi.Add(m); }
            Color32 hi = Mix(color, Color.white, HighlightMix);
            hi.a = (byte)(255f * HighlightAlpha);
            inHighlight = true;
            try
            {
                var hiMesh = (LayerSubMesh)getSubMesh.Invoke(__instance, new object[] { highlightMat });
                int from = hiMesh.colors.Count;
                __instance.GeneratePaths(hiMesh, tile, scratchHi, hi, allowSmoothTransition);
                for (int i = from; i < hiMesh.colors.Count; i++)
                {
                    Color32 c = hi;
                    if (hiMesh.colors[i].a == 0) c.a = 0;
                    hiMesh.colors[i] = c;
                }
            }
            finally { inHighlight = false; }
        }

        static bool RoadPrefix(WorldDrawLayer_Paths __instance, LayerSubMesh subMesh, PlanetTile tile,
            ref List<WorldDrawLayer_Paths.OutputDirection> nodes, Color32 color, ref bool allowSmoothTransition)
        {
            if (inHighlight || !Roads || nodes == null || !(__instance is WorldDrawLayer_Roads)) return true;
            RoadWorldLayerDef layerDef = RM_WorldPaths.LayerOf(color);
            if (layerDef == null || !(tile.Tile is SurfaceTile st) || st.potentialRoads == null) return true;
            scratch.Clear();
            bool any = false, gap = false;
            foreach (WorldDrawLayer_Paths.OutputDirection n in nodes)
            {
                WorldDrawLayer_Paths.OutputDirection m = n;
                RoadDef road = null;
                foreach (SurfaceTile.RoadLink rl in st.potentialRoads) if (rl.neighbor.tileId == n.neighbor.tileId) { road = rl.road; break; }
                string kind = road?.defName;
                float h = RM_RiverGraph.LinkHash(tile.tileId, n.neighbor.tileId);
                if ((kind == "AncientAsphaltRoad" || kind == "AncientAsphaltHighway") && h < AncientGapShare) { m.width = 0f; gap = true; }
                else if ((kind == "DirtPath" || kind == "DirtRoad") && layerDef.defName == "Dirt" && h < DirtWornShare) m.width = n.width * DirtWornWidth;
                if (m.width > 0f) any = true;
                scratch.Add(m);
            }
            nodes = scratch;
            // Vanilla's two-link smooth branch joins both endpoints whatever their widths, which would draw a wedge into
            // the gap; the general branch skips a zero-width link (GPT review 2026-11-02).
            if (gap) allowSmoothTransition = false;
            return any;   // every link of this tile is a gap: draw nothing here, not even the centre
        }
    }
}
