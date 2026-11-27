// JawaBenchPawnRenderTools.cs - jawa/pawn_render_nodes: how one pawn is drawn this frame, and the drawn height of each draw.
// RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER: to tell whether a map mesh draws over or under a pawn, read the
// pawn's own draws beside the mesh's (jawa/cell_draw_census probeY). Generic: any pawn, any mod.
//
// ENGINE (decompiled 1.6, read 2026-11-27): PawnRenderer keeps `private PreRenderResults results` (valid, draw, useCached, bodyPos,
// ...), set each frame by ParallelPreRenderPawnAt. useCached (a humanlike pawn with CameraDriver.ZoomRootSize > 18 and no
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
                "last ones built and are not drawn. framesSinceDraw (0..2 = drawn now) dates the reading. With probeY >= 0 (a " +
                "mesh's bounds centre from jawa/cell_draw_census) each draw says vsProbe: above, below or level. Calls no " +
                "DrawPos and dirties nothing.",
            ResultDescription =
                "success, ticksGame, pawn{thingId, x, z}, framesSinceDraw (-1 = never drawn), cameraRootSize, drawPath, " +
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
                FieldInfo resultsField = AccessTools.Field(typeof(PawnRenderer), "results");
                FieldInfo requestsField = AccessTools.Field(typeof(PawnRenderTree), "drawRequests");
                FieldInfo lastFrame = AccessTools.Field(typeof(PawnTweener), "lastDrawFrame");
                if (resultsField == null || requestsField == null)
                    return Fail("Verse.PawnRenderer.results or PawnRenderTree.drawRequests not found: the read cannot see");
                object res = resultsField.GetValue(renderer);
                Type rt = resultsField.FieldType;
                bool valid = (bool)rt.GetField("valid").GetValue(res);
                bool draw = (bool)rt.GetField("draw").GetValue(res);
                bool useCached = (bool)rt.GetField("useCached").GetValue(res);
                Vector3 bodyPos = (Vector3)rt.GetField("bodyPos").GetValue(res);
                string path = JawaBenchDrawOrderCore.DrawPath(valid, draw, useCached);
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
                        ys.Add(mx.m13);
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
                int f = lastFrame != null && pawn.Drawer?.tweener != null ? (int)lastFrame.GetValue(pawn.Drawer.tweener) : -1;
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
    }
}
