// JawaBenchDrawCensusTools.cs - jawa/cell_draw_census: every map-mesh draw that puts a pixel on one map square.
// RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE (owner walk 2026-11-25: "I suspect you're applying multiple
// layers over each other instead of calculating a single one"): a picture cannot say how many layers tint a square, so this
// read counts them. Generic: it reads any mod's section layers, never one mod's state.
//
// ENGINE (RimSage, 1.6, read 2026-11-25): Verse.Section keeps `private readonly List<SectionLayer> layers`; SectionLayer keeps
// `protected List<LayerSubMesh> subMeshes`; LayerSubMesh.FinalizeMesh hands verts/tris/colors to the Mesh and KEEPS the lists,
// so the CPU copy is the drawn geometry. MapDrawer.SectionAt(IntVec3) finds the section. Realtime-drawn things (a door, a
// pawn) are NOT in a section mesh: they are listed by thing, with their drawerType, so a caller can tell the census is blind there.
// THREAD AFFINITY: all game access inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections.Generic;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/cell_draw_census",
            Description =
                "READ ONLY. Every section-layer draw that covers part of one map square: for each layer of the square's section " +
                "(and of the sections beside it when the square sits on a section edge), each sub-mesh whose triangles overlap the " +
                "square, with the layer type, its Visible flag, the material (name, shader, renderQueue, colour), the clipped area " +
                "it covers inside the square (0..1 per triangle, summed: >1 means it draws over itself), its clipped extent in " +
                "square-local units, and the min/max/mean of its vertex colours there. A disabled sub-mesh or a hidden layer is " +
                "listed with drawn=false. Realtime-drawn things on the square (doors, pawns) are NOT in any mesh: they come back " +
                "in realtime[] by def and drawerType, so a caller sees where the census is blind.",
            ResultDescription =
                "success, ticksGame, cell{x,z}, sectionsRead, draws[] {layer, visible, disabled, drawn, material, shader, " +
                "renderQueue, matColour[r,g,b,a], tris, area, ext[x0,z0,x1,z1], aMin, aMax, rgbMean[r,g,b], aMean}, realtime[] " +
                "{def, thingClass, drawerType}, layersWithNoMeshData[].")]
        public static async Task<object> CellDrawCensus(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "the square's x")] int x = -1,
            [ToolParameter(Description = "the square's z")] int z = -1,
            [ToolParameter(Description = "substring filter on the layer type name; empty = every layer", DefaultValue = "")] string layerFilter = "")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = Current.Game == null ? null : Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                IntVec3 c = new IntVec3(x, 0, z);
                if (!c.InBounds(map)) return Fail("square out of bounds: " + x + "," + z);
                FieldInfo layersField = AccessTools.Field(typeof(Section), "layers");
                FieldInfo subField = AccessTools.Field(typeof(SectionLayer), "subMeshes");
                if (layersField == null || subField == null)
                    return Fail("Verse.Section.layers or SectionLayer.subMeshes not found: the census cannot see");
                // a square's draws can live in a neighbour section (a layer may draw past its section's edge by a square)
                var sections = new List<Section>();
                foreach (IntVec3 off in GenAdj.AdjacentCellsAndInside)
                {
                    IntVec3 q = c + off;
                    if (!q.InBounds(map)) continue;
                    Section s = map.mapDrawer.SectionAt(q);
                    if (s != null && !sections.Contains(s)) sections.Add(s);
                }
                var draws = new List<object>();
                var empty = new List<string>();
                string filter = (layerFilter ?? "").Trim();
                foreach (Section s in sections)
                {
                    var layers = layersField.GetValue(s) as List<SectionLayer>;
                    if (layers == null) continue;
                    foreach (SectionLayer layer in layers)
                    {
                        string lname = layer.GetType().Name;
                        if (filter.Length > 0 && lname.IndexOf(filter, StringComparison.OrdinalIgnoreCase) < 0) continue;
                        var subs = subField.GetValue(layer) as List<LayerSubMesh>;
                        if (subs == null) continue;
                        bool visible = layer.Visible;
                        foreach (LayerSubMesh sm in subs)
                        {
                            if (sm.verts.Count == 0 && sm.tris.Count > 0)
                            {
                                if (!empty.Contains(lname)) empty.Add(lname);
                                continue;
                            }
                            Stat st = Clip(sm, x, z);
                            if (st.tris == 0) continue;
                            Material m = sm.material;
                            Color mc = m != null && m.HasProperty("_Color") ? m.color : Color.white;
                            draws.Add(new
                            {
                                layer = lname,
                                visible,
                                disabled = sm.disabled,
                                drawn = visible && !sm.disabled,
                                material = m != null ? m.name : null,
                                shader = m != null && m.shader != null ? m.shader.name : null,
                                renderQueue = m != null ? m.renderQueue : -1,
                                matColour = new[] { R(mc.r), R(mc.g), R(mc.b), R(mc.a) },
                                tris = st.tris,
                                area = R(st.area),
                                ext = new[] { R(st.x0), R(st.z0), R(st.x1), R(st.z1) },
                                aMin = st.aMin,
                                aMax = st.aMax,
                                aMean = st.n > 0 ? R(st.aSum / st.n) : 0f,
                                rgbMean = st.n > 0 ? new[] { R(st.rSum / st.n), R(st.gSum / st.n), R(st.bSum / st.n) } : new float[0],
                            });
                        }
                    }
                }
                var realtime = new List<object>();
                foreach (Thing t in c.GetThingList(map))
                {
                    if (t.def.drawerType == DrawerType.RealtimeOnly || t.def.drawerType == DrawerType.MapMeshAndRealTime)
                        realtime.Add(new { def = t.def.defName, thingClass = t.GetType().Name, drawerType = t.def.drawerType.ToString() });
                }
                return (object)new
                {
                    success = true,
                    ticksGame = TicksGameSafe(),
                    cell = new { x, z },
                    sectionsRead = sections.Count,
                    draws,
                    realtime,
                    layersWithNoMeshData = empty,
                };
            }, cancellationToken);
        }

        private static float R(float v) => (float)Math.Round(v, 4);

        private struct Stat
        {
            public int tris, n, aMin, aMax;
            public float area, x0, z0, x1, z1, aSum, rSum, gSum, bSum;
        }

        /// <summary>The part of a sub-mesh inside square (x, z): each triangle clipped to the square (Sutherland-Hodgman), its area
        /// summed (overdraw counts twice), the extent of the clipped parts, and the vertex colours of the triangles that reach in.</summary>
        private static Stat Clip(LayerSubMesh sm, int x, int z)
        {
            var st = new Stat { aMin = 256, aMax = -1, x0 = 2f, z0 = 2f, x1 = -1f, z1 = -1f };
            var poly = new List<Vector2>(8);
            var tmp = new List<Vector2>(8);
            bool colours = sm.colors.Count == sm.verts.Count;
            for (int i = 0; i + 2 < sm.tris.Count; i += 3)
            {
                int a = sm.tris[i], b = sm.tris[i + 1], d = sm.tris[i + 2];
                if (a >= sm.verts.Count || b >= sm.verts.Count || d >= sm.verts.Count) continue;
                poly.Clear();
                poly.Add(new Vector2(sm.verts[a].x - x, sm.verts[a].z - z));
                poly.Add(new Vector2(sm.verts[b].x - x, sm.verts[b].z - z));
                poly.Add(new Vector2(sm.verts[d].x - x, sm.verts[d].z - z));
                for (int edge = 0; edge < 4 && poly.Count > 0; edge++)
                {
                    tmp.Clear();
                    for (int k = 0; k < poly.Count; k++)
                    {
                        Vector2 p = poly[k], q = poly[(k + 1) % poly.Count];
                        bool pin = Inside(p, edge), qin = Inside(q, edge);
                        if (pin) tmp.Add(p);
                        if (pin != qin) tmp.Add(Cross(p, q, edge));
                    }
                    poly.Clear();
                    poly.AddRange(tmp);
                }
                if (poly.Count < 3) continue;
                float ar = 0f;
                for (int k = 0; k < poly.Count; k++)
                {
                    Vector2 p = poly[k], q = poly[(k + 1) % poly.Count];
                    ar += p.x * q.y - q.x * p.y;
                }
                ar = Math.Abs(ar) * 0.5f;
                if (ar < 1e-5f) continue;
                st.tris++;
                st.area += ar;
                foreach (Vector2 p in poly)
                {
                    st.x0 = Math.Min(st.x0, p.x); st.z0 = Math.Min(st.z0, p.y);
                    st.x1 = Math.Max(st.x1, p.x); st.z1 = Math.Max(st.z1, p.y);
                }
                if (colours)
                {
                    foreach (int vi in new[] { a, b, d })
                    {
                        Color32 col = sm.colors[vi];
                        st.n++;
                        st.aMin = Math.Min(st.aMin, col.a);
                        st.aMax = Math.Max(st.aMax, col.a);
                        st.aSum += col.a; st.rSum += col.r; st.gSum += col.g; st.bSum += col.b;
                    }
                }
            }
            if (st.n == 0) { st.aMin = -1; st.aMax = -1; }
            return st;
        }

        // edges of the unit square: 0 x>=0, 1 x<=1, 2 z>=0, 3 z<=1
        private static bool Inside(Vector2 p, int edge) =>
            edge == 0 ? p.x >= 0f : edge == 1 ? p.x <= 1f : edge == 2 ? p.y >= 0f : p.y <= 1f;

        private static Vector2 Cross(Vector2 p, Vector2 q, int edge)
        {
            float t;
            if (edge < 2)
            {
                float bound = edge == 0 ? 0f : 1f;
                t = (bound - p.x) / (q.x - p.x);
            }
            else
            {
                float bound = edge == 2 ? 0f : 1f;
                t = (bound - p.y) / (q.y - p.y);
            }
            return p + (q - p) * t;
        }
    }
}
