// JawaBenchPawnRenderTools.cs - jawa/pawn_render_nodes: how one pawn is drawn this frame, and the drawn height of each draw.
// RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER: to tell whether a map mesh draws over or under a pawn, read the
// pawn's own draws beside the mesh's (jawa/cell_draw_census probeY). Generic: any pawn, any mod. jawa/material_queue reads or sets
// a section material's renderQueue for a session: the experiment that tells a queue order from a depth order.
//
// ENGINE (decompiled 1.6, read 2026-11-27): PawnRenderer keeps `private PreRenderResults results` (valid, draw, useCached, bodyPos,
// ...), set each frame by ParallelPreRenderPawnAt and RESET to default at the end of RenderPawnAt, so a read between frames sees
// valid=false (live, SteveDesktop 2026-11-27). This read asks the engine's own ParallelGetPreRenderResults for the path instead,
// at the last drawn body position (`silhouettePos`, written from results.bodyPos in the same draw). useCached (a humanlike pawn with CameraDriver.ZoomRootSize > 18 and no
// animation, carry or crawl) draws ONE quad of the pawn's cached atlas frame (ShaderDatabase.Cutout) at bodyPos, and the render
// nodes are not drawn; else PawnRenderTree keeps `private readonly List<PawnGraphicDrawRequest> drawRequests`, one per node,
// each drawn by GenDraw.DrawMeshNowOrLater(mesh, preDrawnComputedMatrix, material): the matrix's translation is the drawn spot.
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
            "jawa/pawn_render_nodes",
            Description =
                "READ ONLY. How one pawn is drawn in the last frame: drawPath (notPreRendered, hidden, cachedAtlas = one quad of " +
                "the cached frame at bodyPos with the render nodes NOT drawn, or nodes = one draw per render node), the camera's " +
                "zoom root size (the engine draws a humanlike pawn as cachedAtlas above 18), bodyPos, and for each draw request " +
                "of the render tree: node label, tag, worker, material (name, id, shader, renderQueue) and the drawn spot (the " +
                "translation of its matrix: y is its height, larger = nearer the camera). Under cachedAtlas the requests are the " +
                "last ones built and are not drawn. framesSinceDraw counts frames since the pawn's tweener last placed it " +
                "(PawnTweener.lastDrawFrame); the map's cull pass places EVERY spawned pawn each frame, on screen or not, so a low " +
                "value does not prove a draw: bodyPos and the requests are from the last frame that drew the pawn, so put the " +
                "camera on the pawn and let a frame pass before the read. A pawn never placed (or teleported since) reads " +
                "notPreRendered. The requests are read first, as the last frame built them; then the path comes from the engine's " +
                "own PawnRenderer.ParallelGetPreRenderResults at the last drawn body position, which rebuilds the requests as " +
                "every frame does. nodesY spans the requests that have a material (the drawn ones). With probeY >= 0 (a vertex " +
                "height from jawa/cell_draw_census) each draw says vsProbe: above, below or level. Calls no DrawPos.",
            ResultDescription =
                "success, ticksGame, pawn{thingId, x, z}, framesSinceDraw (-1 = never placed), cameraRootSize, drawPath, " +
                "bodyPos[x,y,z], cachedQuad{shader, renderQueue, y, vsProbe} (cachedAtlas only), requests[] {node, tag, worker, " +
                "material, materialId, shader, renderQueue, drawn[x,y,z], vsProbe}, nodesY{n, min, max} (n=0: no request read), probeY.")]
        public static async Task<object> PawnRenderNodes(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "the pawn's ThingID (e.g. Human1234)")] string pawnId = "",
            [ToolParameter(Description = "a height (world y) to read each draw against, e.g. a sub-mesh's bounds centre; -1 = none", DefaultValue = -1f)] float probeY = -1f)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = Current.Game == null ? null : Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                string want = (pawnId ?? "").Trim();
                if (want.Length == 0) return Fail("pawnId is required (a ThingID, e.g. Human1234)");
                Pawn pawn = null;
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
                {
                    if (p.ThingID == want) { pawn = p; break; }
                }
                if (pawn == null) return Fail("no spawned pawn " + want + " on the current map");
                PawnRenderer renderer = pawn.Drawer?.renderer;
                if (renderer == null) return Fail(want + " has no renderer: the read cannot see");
                MethodInfo preMethod = AccessTools.Method(typeof(PawnRenderer), "ParallelGetPreRenderResults");
                FieldInfo silField = AccessTools.Field(typeof(PawnRenderer), "silhouettePos");
                FieldInfo requestsField = AccessTools.Field(typeof(PawnRenderTree), "drawRequests");
                FieldInfo lastFrame = AccessTools.Field(typeof(PawnTweener), "lastDrawFrame");
                if (preMethod == null || silField == null || requestsField == null)
                    return Fail("Verse.PawnRenderer.ParallelGetPreRenderResults, PawnRenderer.silhouettePos or " +
                                "PawnRenderTree.drawRequests not found: the read cannot see");
                int f = lastFrame != null && pawn.Drawer?.tweener != null ? (int)lastFrame.GetValue(pawn.Drawer.tweener) : -1;
                Vector3 bodyPos = (Vector3)silField.GetValue(renderer);
                bool probe = probeY >= 0f;
                float eps = JawaBenchDrawOrderCore.Eps;
                var rows = new List<object>();
                var ys = new List<float>();
                var reqs = renderer.renderTree != null ? requestsField.GetValue(renderer.renderTree) as List<PawnGraphicDrawRequest> : null;
                if (reqs != null)
                {
                    foreach (PawnGraphicDrawRequest q in reqs)
                    {
                        Matrix4x4 mx = q.preDrawnComputedMatrix;
                        Material m = q.material;
                        if (m != null) ys.Add(mx.m13);
                        rows.Add(new
                        {
                            node = q.node != null ? q.node.ToString() : null,
                            tag = q.node?.Props?.tagDef?.defName,
                            worker = q.node?.Worker?.GetType().Name,
                            material = m != null ? m.name : null,
                            materialId = m != null ? m.GetInstanceID() : 0,
                            shader = m != null && m.shader != null ? m.shader.name : null,
                            renderQueue = m != null ? m.renderQueue : -1,
                            drawn = new[] { R(mx.m03), R(mx.m13), R(mx.m23) },
                            vsProbe = probe ? JawaBenchDrawOrderCore.Relation(mx.m13, probeY, eps) : null,
                        });
                    }
                }
                JawaBenchDrawOrderCore.YSpan nodes = JawaBenchDrawOrderCore.Span(ys);
                // the path, after the requests are read (the engine's call rebuilds them, as every frame does)
                bool valid = false, draw = false, useCached = false;
                if (f >= 0)
                {
                    object res = preMethod.Invoke(renderer, new object[] { bodyPos, null, false, false });
                    Type rt = preMethod.ReturnType;
                    valid = (bool)rt.GetField("valid").GetValue(res);
                    draw = (bool)rt.GetField("draw").GetValue(res);
                    useCached = (bool)rt.GetField("useCached").GetValue(res);
                }
                string path = JawaBenchDrawOrderCore.DrawPath(valid, draw, useCached);
                Shader cut = ShaderDatabase.Cutout;
                return (object)new
                {
                    success = true,
                    ticksGame = TicksGameSafe(),
                    pawn = new { thingId = pawn.ThingID, x = pawn.Position.x, z = pawn.Position.z },
                    framesSinceDraw = f < 0 ? -1 : RealTime.frameCount - f,
                    cameraRootSize = Find.CameraDriver != null ? R(Find.CameraDriver.ZoomRootSize) : -1f,
                    drawPath = path,
                    bodyPos = new[] { R(bodyPos.x), R(bodyPos.y), R(bodyPos.z) },
                    cachedQuad = path == "cachedAtlas" ? new
                    {
                        shader = cut != null ? cut.name : null,
                        renderQueue = cut != null ? cut.renderQueue : -1,
                        y = R(bodyPos.y),
                        vsProbe = probe ? JawaBenchDrawOrderCore.Relation(bodyPos.y, probeY, eps) : null,
                    } : null,
                    requests = rows,
                    requestsRead = reqs != null,
                    nodesY = YOut(nodes),
                    probeY = probe ? (float?)probeY : null,
                };
            }, cancellationToken);
        }

        [Tool(
            "jawa/material_queue",
            Description =
                "Reads, or for this session sets, the Unity renderQueue of the materials that the current map's section layers " +
                "draw with, picked by materialId (from jawa/cell_draw_census) or by a part of the material's name. An experiment " +
                "tool for draw order: the renderer draws a lower queue first, so a draw set below a pawn's queue (see " +
                "jawa/pawn_render_nodes) is drawn before the pawn. setQueue -2 (default) only reads; -1 gives the material back " +
                "its shader's own queue; 0..5000 sets it. The change lives on the shared Material: every thing drawn with it moves, " +
                "nothing is saved, and the next game load forgets it. Picks nothing when neither key is given.",
            ResultDescription =
                "success, ticksGame, setQueue, sectionsRead, materials[] {material, materialId, shader, shaderQueue, before, " +
                "after, subMeshes (how many sub-meshes of the map draw with it)}, refused (why a set was refused, else null).")]
        public static async Task<object> MaterialQueue(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "a material's instance id (cell_draw_census materialId); 0 = pick by name", DefaultValue = 0)] int materialId = 0,
            [ToolParameter(Description = "a case-blind part of the material name, used only when materialId is 0", DefaultValue = "")] string nameContains = "",
            [ToolParameter(Description = "-2 read only, -1 the shader's own queue, 0..5000 set", DefaultValue = -2)] int setQueue = -2)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = Current.Game == null ? null : Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                string refused = JawaBenchDrawOrderCore.QueueRefusal(setQueue);
                if (refused != null) return Fail(refused);
                if (materialId == 0 && string.IsNullOrEmpty(nameContains))
                    return Fail("name a material: materialId (from jawa/cell_draw_census) or nameContains");
                FieldInfo sectionsField = AccessTools.Field(typeof(MapDrawer), "sections");
                FieldInfo layersField = AccessTools.Field(typeof(Section), "layers");
                if (sectionsField == null || layersField == null)
                    return Fail("Verse.MapDrawer.sections or Section.layers not found: the tool cannot see");
                var grid = sectionsField.GetValue(map.mapDrawer) as Section[,];
                if (grid == null) return Fail("the map has no sections yet: the tool cannot see");
                var found = new Dictionary<Material, int>();
                int read = 0;
                foreach (Section s in grid)
                {
                    if (s == null) continue;
                    read++;
                    var layers = layersField.GetValue(s) as List<SectionLayer>;
                    if (layers == null) continue;
                    foreach (SectionLayer layer in layers)
                    {
                        foreach (LayerSubMesh sm in layer.subMeshes)
                        {
                            Material m = sm.material;
                            if (m == null || !JawaBenchDrawOrderCore.Picks(m.GetInstanceID(), m.name, materialId, nameContains)) continue;
                            found.TryGetValue(m, out int k);
                            found[m] = k + 1;
                        }
                    }
                }
                var rows = new List<object>();
                foreach (var kv in found)
                {
                    Material m = kv.Key;
                    int before = m.renderQueue;
                    if (setQueue != JawaBenchDrawOrderCore.ReadOnly) m.renderQueue = setQueue;
                    rows.Add(new
                    {
                        material = m.name,
                        materialId = m.GetInstanceID(),
                        shader = m.shader != null ? m.shader.name : null,
                        shaderQueue = m.shader != null ? m.shader.renderQueue : -1,
                        before,
                        after = m.renderQueue,
                        subMeshes = kv.Value,
                    });
                }
                return (object)new
                {
                    success = rows.Count > 0,
                    message = rows.Count > 0 ? null : "no section sub-mesh of the current map draws with that material",
                    ticksGame = TicksGameSafe(),
                    setQueue,
                    sectionsRead = read,
                    materials = rows,
                    refused = (string)null,
                };
            }, cancellationToken);
        }
    }
}
