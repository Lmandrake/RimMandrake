// JawaBenchArtboardTools.cs - the live half of the contact-board art pre-review (2026-10-06).
//
// Design: design/RimMandrake/rich_screenshot_art_prereview.md section 11. Python side:
// src/RimMandrake/Utils/artboard/live.py (stages a recipe, captures plate + board, segments, checks).
//
//   artboard_stage        stage a whole board from an ops FILE (or string) in one call. Every subject lands on
//                         the cell it names or is REFUSED with a per-op error - never nudged to a neighbour
//                         (stage_xenotype_grid.py's nearest-open-cell fallback broke the first trial's geometry).
//   artboard_capture      render a cell rect OFF-SCREEN at an exact px/cell: the main camera is pointed at the
//                         rect, rendered into a RenderTexture and put back inside one coroutine step that runs
//                         after Update and before the frame is drawn, so the user's view never moves, the window
//                         is never resized or focused, and IMGUI (labels, alerts, tabs) is not in the image.
//   thing_screen_rects    things in a cell rect with their draw rects in the pixel space of a capture mapping,
//                         so an existing review map can be cut up without a recipe.
//
// HOW THE OFF-SCREEN RENDER GETS CONTENT (read from decompiled 1.6, 2026-10-06):
//   Map.MapUpdate (Root_Play.Update -> Game.UpdatePlay) culls BOTH section meshes (MapDrawer.ViewRect) and dynamic
//   things (DynamicDrawManager.ComputeCulledThings) to CameraDriver.CurrentViewRect, then queues them with
//   Graphics.DrawMesh(camera = null), i.e. for every camera that renders this frame. So a rect outside the user's
//   view has no draws queued and no regenerated sections. A Harmony postfix on CameraDriver.CurrentViewRect
//   ENCAPSULATES the capture rect while a capture is armed: the next MapUpdate regenerates dirty sections there
//   (Section.TryUpdate) and queues their draws alongside the user's view. Nothing is drawn twice - we issue no draws
//   of our own; extra draws off the user's screen are invisible to him.
//   Water: SectionLayer_Watergen draws onto the WaterDepth subcamera's layer and the water shader samples that
//   subcamera's screen-sized RT by screen UV, so the subcamera is pointed at the same rect with the same aspect and
//   rendered first, then restored (its own automatic render re-fills the RT for the user's frame).
//
// THREAD AFFINITY: everything touching game or Unity state runs inside ctx.MainThread.InvokeAsync or inside the
// coroutine (main thread). The tool awaits a TaskCompletionSource the coroutine completes.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    internal static class JawaArtboardCapture
    {
        internal static bool Armed;
        internal static CellRect Rect;
        internal static bool Installed;
        internal static string InstallError;
        internal static int Token;
        private static bool _attempted;

        internal static void Install()
        {
            if (_attempted) return;
            _attempted = true;
            try
            {
                MethodInfo getter = AccessTools.PropertyGetter(typeof(CameraDriver), "CurrentViewRect");
                if (getter == null) { InstallError = "CameraDriver.CurrentViewRect getter not found"; return; }
                var h = new Harmony("mandrake.jawabench.artboard");
                h.Patch(getter, postfix: new HarmonyMethod(typeof(JawaArtboardCapture).GetMethod("ViewRectPostfix",
                    BindingFlags.Static | BindingFlags.NonPublic)));
                Installed = true;
            }
            catch (Exception e) { InstallError = e.GetType().Name + ": " + e.Message; }
        }

        private static void ViewRectPostfix(ref CellRect __result)
        {
            if (Armed) __result = __result.Encapsulate(Rect);
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        // pawns this tool generated, so a re-stage can clear them without touching anyone else's
        private static readonly HashSet<int> ArtboardPawnIds = new HashSet<int>();

        // ════════════════════════════════════════════════════════════════
        //  jawa/artboard_stage
        // ════════════════════════════════════════════════════════════════
        [Tool(
            "jawa/artboard_stage",
            Description =
                "Stage a whole contact board on the CURRENT map in one call. phase=ground: clear 'clearRect' (destroys " +
                "every non-player Thing and plant in it, removes roof/snow/fog, fills excavations back to the surface) and " +
                "lay 'ground' terrain - then capture the clean plate. phase=subjects: run the ops. phase=all: both. " +
                "ops (or opsPath, a file - bulk takes a file) = one op per line, key=value pairs joined by '|': " +
                "id=..|kind=pit|x=|z=|w=|h=|depth=1-4|fill=0..depth|fluid=RM_Fluid_Water ; kind=terrain|x|z|w|h|def= ; " +
                "kind=thing|x|z|def|stuff|rot ; kind=plant|x|z|def|growth=0..1 ; kind=pawn|x|z|def=<PawnKindDef>|rot|" +
                "faction=none,player. REFUSES rather than relocates: an op whose cell is out of bounds, blocked, " +
                "not standable (pawns), or already dug deeper than asked (pits - D only goes down) reports ok:false with " +
                "the reason and nothing is placed for it. Pits are dug for all ops first, then filled, then read back " +
                "through DepthAt/FillAt/FluidAt. Pauses the game (pause=true) so nothing moves before the capture; staged " +
                "pawns are given a long Wait job and their rotation is set after it. killHostiles destroys every pawn " +
                "hostile to the player on the map.",
            ResultDescription =
                "success (every op ok), phase, ground{cleared, refusedCells[]}, ops[{id, kind, ok, error, requested, " +
                "actual{x,z}, def, thingId, drawRect{x,z,w,h} world units, readBack}], refused count, ticksGame.")]
        public static async Task<object> ArtboardStage(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ground | subjects | all")] string phase = "all",
            [ToolParameter(Description = "Op lines (see description). Use opsPath for anything big.")] string ops = null,
            [ToolParameter(Description = "Absolute path of a file holding the op lines.")] string opsPath = null,
            [ToolParameter(Description = "phase ground/all: 'x,z,w,h' cell rect to clear.")] string clearRect = null,
            [ToolParameter(Description = "phase ground/all: TerrainDef laid over clearRect (e.g. Soil). Empty = leave terrain.")] string ground = null,
            [ToolParameter(Description = "Destroy every pawn hostile to the player on this map.")] bool killHostiles = true,
            [ToolParameter(Description = "Pause the game after staging.")] bool pause = true)
        {
            string text = ops;
            if (!string.IsNullOrEmpty(opsPath))
            {
                try { text = File.ReadAllText(opsPath); }
                catch (Exception e) { return Fail("Could not read opsPath '" + opsPath + "': " + e.Message); }
            }
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                string ph = (phase ?? "all").Trim().ToLowerInvariant();
                if (ph != "ground" && ph != "subjects" && ph != "all") return Fail("phase must be ground, subjects or all.");
                object exc = ResolveExcavationComponent(map, out Type excType, out string excErr);

                int hostilesKilled = 0;
                if (killHostiles)
                    foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
                        if (p.HostileTo(Faction.OfPlayer)) { p.Destroy(DestroyMode.Vanish); hostilesKilled++; }

                object groundResult = null;
                if (ph != "subjects")
                {
                    if (!TryParseRect(clearRect, out CellRect cr)) return Fail("phase " + ph + " needs clearRect 'x,z,w,h'.");
                    if (!cr.InBounds(map)) return Fail("clearRect " + clearRect + " is not inside the map (" + map.Size.x + "x" + map.Size.z + ").");
                    TerrainDef gdef = null;
                    if (!string.IsNullOrEmpty(ground))
                    {
                        gdef = DefDatabase<TerrainDef>.GetNamedSilentFail(ground);
                        if (gdef == null) return Fail("Unknown ground TerrainDef '" + ground + "'.", new { suggestions = DefSuggestions<TerrainDef>(ground) });
                    }
                    var colonists = cr.Cells.SelectMany(c => c.GetThingList(map)).OfType<Pawn>()
                        .Where(p => p.Faction == Faction.OfPlayer && !ArtboardPawnIds.Contains(p.thingIDNumber)).Distinct().ToList();
                    if (colonists.Count > 0)
                        return Fail("clearRect holds player pawns (refusing to destroy or move them): " +
                                    string.Join(", ", colonists.Select(p => p.LabelShortCap + "@" + p.Position)));
                    int destroyed = 0;
                    var refusedCells = new List<string>();
                    foreach (IntVec3 c in cr.Cells)
                    {
                        foreach (Thing t in c.GetThingList(map).ToList())
                        {
                            if (t.Destroyed) continue;
                            if (t is Pawn pp && pp.Faction == Faction.OfPlayer && !ArtboardPawnIds.Contains(pp.thingIDNumber)) continue;
                            t.Destroy(DestroyMode.Vanish); destroyed++;
                        }
                        if (exc != null)
                        {
                            try
                            {
                                if (Convert.ToInt32(QCall(exc, "DepthAt", c)) > 0)
                                {
                                    QCall(exc, "TrySetDriverFill", c, 0, null);
                                    for (int i = 0; i < 6 && Convert.ToInt32(QCall(exc, "DepthAt", c)) > 0; i++) QCall(exc, "FillIn", c);
                                    if (Convert.ToInt32(QCall(exc, "DepthAt", c)) > 0) refusedCells.Add(c.x + "," + c.z + " still excavated");
                                }
                            }
                            catch (Exception e) { refusedCells.Add(c.x + "," + c.z + " excavation reset threw " + Inner(e)); }
                        }
                        map.roofGrid.SetRoof(c, null);
                        map.snowGrid.SetDepth(c, 0f);
                        if (map.fogGrid.IsFogged(c)) map.fogGrid.Unfog(c);
                        if (gdef != null && map.terrainGrid.TerrainAt(c) != gdef)
                        {
                            if (map.terrainGrid.TempTerrainAt(c) != null) map.terrainGrid.RemoveTempTerrain(c);
                            map.terrainGrid.SetTerrain(c, gdef);
                        }
                    }
                    groundResult = new { rect = RectObj(cr), ground = gdef?.defName, destroyed, refusedCells };
                    if (refusedCells.Count > 0 && ph == "ground")
                        return Fail("ground could not be fully cleared", groundResult);
                }

                var results = new List<Dictionary<string, object>>();
                if (ph != "ground")
                {
                    if (string.IsNullOrWhiteSpace(text)) return Fail("phase " + ph + " needs ops or opsPath.");
                    var parsed = new List<Dictionary<string, string>>();
                    foreach (string raw in text.Split('\n'))
                    {
                        string line = raw.Trim('\r', ' ', '\t');
                        if (line.Length == 0 || line.StartsWith("#")) continue;
                        var kv = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                        foreach (string part in line.Split('|'))
                        {
                            int eq = part.IndexOf('=');
                            if (eq > 0) kv[part.Substring(0, eq).Trim()] = part.Substring(eq + 1).Trim();
                        }
                        parsed.Add(kv);
                    }
                    if (parsed.Count > MaxOps) return Fail("too many ops (" + parsed.Count + " > " + MaxOps + ").");
                    var pits = new List<(Dictionary<string, object> row, CellRect r, int D, int F, Def fluid)>();
                    // pass 1: terrain + pits dug (fills come after every dig, so a neighbour's dig cannot drain them)
                    foreach (var kv in parsed)
                    {
                        var row = new Dictionary<string, object>
                        {
                            ["id"] = Get(kv, "id"), ["kind"] = Get(kv, "kind"), ["ok"] = false, ["error"] = null
                        };
                        results.Add(row);
                        try { StageOne(map, exc, excErr, kv, row, pits); }
                        catch (Exception e) { row["ok"] = false; row["error"] = "threw " + Inner(e); }
                    }
                    // pass 2: fills, then read back every pit cell
                    foreach (var p in pits)
                    {
                        int bad = 0; string first = null;
                        foreach (IntVec3 c in p.r.Cells)
                        {
                            if (p.F > 0) QCall(exc, "TrySetDriverFill", c, p.F, p.fluid);
                            int d = Convert.ToInt32(QCall(exc, "DepthAt", c)), f = Convert.ToInt32(QCall(exc, "FillAt", c));
                            string fl = (QCall(exc, "FluidAt", c) as Def)?.defName;
                            bool ok = d == p.D && f == p.F && (p.F == 0 || fl == p.fluid?.defName);
                            if (!ok) { bad++; if (first == null) first = c.x + "," + c.z + " D" + d + "F" + f + " " + fl; }
                        }
                        p.row["readBack"] = new { cells = p.r.Area, badCells = bad, firstBad = first };
                        if (bad > 0) { p.row["ok"] = false; p.row["error"] = bad + "/" + p.r.Area + " cells read back wrong, e.g. " + first; }
                    }
                }

                if (pause && Find.TickManager != null) Find.TickManager.CurTimeSpeed = TimeSpeed.Paused;
                int refused = results.Count(r => !(bool)r["ok"]);
                return (object)new
                {
                    success = refused == 0,
                    phase = ph,
                    hostilesKilled,
                    ground = groundResult,
                    opsCount = results.Count,
                    refused,
                    ops = results,
                    paused = Find.TickManager?.Paused,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        private static string Get(Dictionary<string, string> kv, string k) => kv.TryGetValue(k, out string v) ? v : null;

        private static int GetInt(Dictionary<string, string> kv, string k, int dflt)
        {
            string v = Get(kv, k);
            if (string.IsNullOrEmpty(v)) return dflt;
            if (!int.TryParse(v, NumberStyles.Integer, CultureInfo.InvariantCulture, out int n))
                throw new FormatException(k + "='" + v + "' is not an integer");
            return n;
        }

        private static string Inner(Exception e)
        {
            while (e is TargetInvocationException && e.InnerException != null) e = e.InnerException;
            return e.GetType().Name + ": " + e.Message;
        }

        private static object RectObj(CellRect r) => new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height };

        private static bool TryParseRect(string s, out CellRect r)
        {
            r = CellRect.Empty;
            if (string.IsNullOrEmpty(s)) return false;
            string[] f = s.Split(',');
            if (f.Length != 4) return false;
            var n = new int[4];
            for (int i = 0; i < 4; i++)
                if (!int.TryParse(f[i].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out n[i])) return false;
            if (n[2] <= 0 || n[3] <= 0) return false;
            r = new CellRect(n[0], n[1], n[2], n[3]);
            return true;
        }

        internal sealed class ArtDrawRect
        {
            public float x, z, w, h;
            public string source;
        }

        private static ArtDrawRect DrawRectOf(Thing t)
        {
            Vector3 dp = t.DrawPos;
            Vector2 ds = Vector2.one;
            string src = "default 1x1";
            try
            {
                if (t is Pawn p)
                {
                    var gd = p.ageTracker?.CurKindLifeStage?.bodyGraphicData;
                    if (gd != null && !p.RaceProps.Humanlike) { ds = gd.drawSize; src = "lifeStage bodyGraphicData"; }
                    else if (p.RaceProps.Humanlike) { ds = new Vector2(1.5f, 1.5f); src = "humanlike body+head nominal 1.5"; }
                }
                else if (t.Graphic != null) { ds = t.Graphic.drawSize; src = "Graphic.drawSize"; }
            }
            catch { }
            if (t.Rotation.IsHorizontal && !(t is Pawn) && t.def.rotatable) ds = new Vector2(ds.y, ds.x);
            return new ArtDrawRect { x = dp.x - ds.x / 2f, z = dp.z - ds.y / 2f, w = ds.x, h = ds.y, source = src };
        }

        private static void StageOne(Map map, object exc, string excErr, Dictionary<string, string> kv,
            Dictionary<string, object> row, List<(Dictionary<string, object> row, CellRect r, int D, int F, Def fluid)> pits)
        {
            string kind = (Get(kv, "kind") ?? "").ToLowerInvariant();
            int x = GetInt(kv, "x", int.MinValue), z = GetInt(kv, "z", int.MinValue);
            if (x == int.MinValue || z == int.MinValue) { row["error"] = "needs x and z"; return; }
            int w = GetInt(kv, "w", 1), h = GetInt(kv, "h", 1);
            var rect = new CellRect(x, z, w, h);
            row["requested"] = RectObj(rect);
            if (!rect.InBounds(map)) { row["error"] = "out of bounds"; return; }
            string defName = Get(kv, "def");
            row["def"] = defName;

            if (kind == "terrain")
            {
                TerrainDef td = DefDatabase<TerrainDef>.GetNamedSilentFail(defName ?? "");
                if (td == null) { row["error"] = "unknown TerrainDef '" + defName + "'"; return; }
                foreach (IntVec3 c in rect.Cells)
                {
                    if (map.terrainGrid.TempTerrainAt(c) != null) map.terrainGrid.RemoveTempTerrain(c);
                    map.terrainGrid.SetTerrain(c, td);
                }
                int bad = rect.Cells.Count(c => map.terrainGrid.TerrainAt(c) != td);
                row["actual"] = new { x, z };
                row["readBack"] = new { cells = rect.Area, badCells = bad };
                if (bad > 0) { row["error"] = bad + " cells did not take " + td.defName; return; }
                row["ok"] = true;
                return;
            }
            if (kind == "pit")
            {
                if (exc == null) { row["error"] = excErr; return; }
                int D = GetInt(kv, "depth", -1), F = GetInt(kv, "fill", 0);
                if (D < 1 || D > 4) { row["error"] = "depth must be 1..4"; return; }
                if (F < 0 || F > D) { row["error"] = "fill must be 0..depth (" + D + ")"; return; }
                Def fluid = null;
                if (F > 0)
                {
                    fluid = QFluid(Get(kv, "fluid") ?? "RM_Fluid_Water");
                    if (fluid == null) { row["error"] = "unknown FluidDef '" + Get(kv, "fluid") + "'"; return; }
                }
                var deeper = rect.Cells.Where(c => Convert.ToInt32(QCall(exc, "DepthAt", c)) > D).ToList();
                if (deeper.Count > 0) { row["error"] = deeper.Count + " cells already deeper than D" + D + " (D only goes down; clear the ground first)"; return; }
                var blocked = rect.Cells.Where(c => c.GetEdifice(map) != null).ToList();
                if (blocked.Count > 0) { row["error"] = "edifice on " + blocked[0]; return; }
                foreach (IntVec3 c in rect.Cells)
                {
                    foreach (Thing t in c.GetThingList(map).Where(t => t.def.category == ThingCategory.Plant).ToList()) t.Destroy(DestroyMode.Vanish);
                    for (int i = 0; i < 6 && Convert.ToInt32(QCall(exc, "DepthAt", c)) < D; i++) QCall(exc, "Deepen", c);
                }
                row["actual"] = new { x, z };
                row["fluid"] = fluid?.defName;
                row["ok"] = true;          // pass 2 fills and reads back, and may turn this false
                pits.Add((row, rect, D, F, fluid));
                return;
            }

            IntVec3 cell = new IntVec3(x, 0, z);
            if (!TryRot(Get(kv, "rot"), out Rot4 rot)) { row["error"] = "bad rot '" + Get(kv, "rot") + "'"; return; }
            if (kind == "thing" || kind == "plant")
            {
                ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(defName ?? "");
                if (td == null) { row["error"] = "unknown ThingDef '" + defName + "'"; return; }
                if (kind == "plant" && td.category != ThingCategory.Plant) { row["error"] = defName + " is not a plant"; return; }
                ThingDef stuff = null;
                if (td.MadeFromStuff)
                {
                    string sn = Get(kv, "stuff");
                    stuff = string.IsNullOrEmpty(sn) ? GenStuff.DefaultStuffFor(td) : DefDatabase<ThingDef>.GetNamedSilentFail(sn);
                    if (stuff == null) { row["error"] = "unknown stuff '" + sn + "'"; return; }
                }
                CellRect occ = GenAdj.OccupiedRect(cell, rot, td.size);
                if (!occ.InBounds(map)) { row["error"] = "footprint " + occ + " leaves the map"; return; }
                foreach (IntVec3 c in occ)
                {
                    var blockers = c.GetThingList(map).Where(t => t.def.passability == Traversability.Impassable || t is Building ||
                                                                 (td.category == ThingCategory.Plant && t.def.category == ThingCategory.Plant)).ToList();
                    if (blockers.Count > 0) { row["error"] = "cell " + c + " blocked by " + blockers[0].def.defName; return; }
                }
                Thing thing = ThingMaker.MakeThing(td, stuff);
                if (thing is Plant pl)
                {
                    string g = Get(kv, "growth");
                    if (!string.IsNullOrEmpty(g))
                    {
                        if (!float.TryParse(g, NumberStyles.Float, CultureInfo.InvariantCulture, out float gv) || gv < 0f || gv > 1f)
                        { row["error"] = "growth must be 0..1"; return; }
                        pl.Growth = gv;
                    }
                }
                Thing spawned = GenSpawn.Spawn(thing, cell, map, rot, WipeMode.FullRefund, respawningAfterLoad: false);
                return_placed(row, spawned, cell);
                if (spawned is Plant sp) row["readBack"] = new { growth = sp.Growth };
                return;
            }
            if (kind == "pawn")
            {
                PawnKindDef pk = DefDatabase<PawnKindDef>.GetNamedSilentFail(defName ?? "");
                if (pk == null) { row["error"] = "unknown PawnKindDef '" + defName + "'"; return; }
                if (!cell.Standable(map)) { row["error"] = "cell " + cell + " is not standable"; return; }
                if (cell.GetFirstPawn(map) != null) { row["error"] = "cell " + cell + " already holds " + cell.GetFirstPawn(map).LabelShortCap; return; }
                string fac = (Get(kv, "faction") ?? "none").ToLowerInvariant();
                Faction faction = fac == "player" ? Faction.OfPlayer : null;
                if (fac != "player" && fac != "none") { row["error"] = "faction must be none or player"; return; }
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(pk, faction, forceGenerateNewPawn: true));
                p.equipment?.DestroyAllEquipment();
                Pawn sp = (Pawn)GenSpawn.Spawn(p, cell, map, rot, WipeMode.Vanish, respawningAfterLoad: false);
                ArtboardPawnIds.Add(sp.thingIDNumber);
                if (sp.jobs != null)
                {
                    Job j = JobMaker.MakeJob(JobDefOf.Wait, 60000);
                    sp.jobs.StartJob(j, JobCondition.InterruptForced);
                }
                sp.Rotation = rot;
                return_placed(row, sp, cell);
                row["readBack"] = new { rotation = sp.Rotation.ToStringHuman(), position = new { x = sp.Position.x, z = sp.Position.z } };
                return;
            }
            row["error"] = "unknown kind '" + kind + "' (pit, terrain, thing, plant, pawn)";
        }

        private static void return_placed(Dictionary<string, object> row, Thing t, IntVec3 want)
        {
            if (t == null || !t.Spawned) { row["error"] = "spawn returned nothing"; return; }
            row["thingId"] = t.ThingID;
            row["actual"] = new { x = t.Position.x, z = t.Position.z };
            ArtDrawRect d = DrawRectOf(t);
            row["drawRect"] = new { d.x, d.z, d.w, d.h, d.source };
            if (t.Position != want)
            {
                // the engine moved it: refuse rather than keep a subject on the wrong cell
                row["error"] = "engine placed it at " + t.Position + " not " + want + " - destroyed";
                t.Destroy(DestroyMode.Vanish);
                return;
            }
            row["ok"] = true;
        }

        // ════════════════════════════════════════════════════════════════
        //  jawa/artboard_capture
        // ════════════════════════════════════════════════════════════════
        private static bool artboardBusy;

        [Tool(
            "jawa/artboard_capture",
            Description =
                "Render the cell rect x,z,w,h of the CURRENT map OFF-SCREEN to a PNG at exactly ppc pixels per cell " +
                "(frame = w*ppc x h*ppc). The main camera is pointed at the rect, rendered into a RenderTexture and put " +
                "back inside one coroutine step after Update - the user's view does not move, the window is never " +
                "resized or focused, and no IMGUI (labels, alerts, tabs, review_label boxes) is in the image. Arms a " +
                "view-rect override first and waits 'frames' frames so section meshes in the rect are regenerated and " +
                "its things are queued by the game's own MapUpdate. Returns the exact cell->pixel mapping: u = ax*X + bx, " +
                "v = az*Z + bz (X,Z world cell coordinates, v down), and origin_px = pixel of world corner (0,0) in the " +
                "artboard board-JSON 'camera' convention. Needs frames to advance: if the game window is minimised with " +
                "Run-in-background off this times out and says so. Selection brackets are cleared first (clearSelection).",
            ResultDescription =
                "success, path, ppc, rect{x,z,w,h}, frame[W,H], origin_px[u0,v0], mapping{ax,bx,az,bz}, frameArmed, " +
                "frameRendered, ticksGame, skyGlow, foggedCells, roofedCells, cameraRestored, fileSizeBytes.")]
        public static async Task<object> ArtboardCapture(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect min cell x.")] int x = 0,
            [ToolParameter(Description = "Rect min cell z.")] int z = 0,
            [ToolParameter(Description = "Rect width in cells.")] int w = 0,
            [ToolParameter(Description = "Rect height in cells.")] int h = 0,
            [ToolParameter(Description = "Pixels per cell (integer, 8..256). Default 48.")] int ppc = 48,
            [ToolParameter(Description = "Absolute output PNG path (Windows).")] string path = null,
            [ToolParameter(Description = "Frames to run with the rect armed before rendering (>=2). Default 2.")] int frames = 2,
            [ToolParameter(Description = "Clear the selection first so no selection brackets are drawn.")] bool clearSelection = true,
            [ToolParameter(Description = "Give up after this many ms of real time.")] int timeoutMs = 15000)
        {
            if (string.IsNullOrWhiteSpace(path)) return Fail("Give an absolute output PNG path in 'path'.");
            if (w <= 0 || h <= 0) return Fail("w and h must be positive.");
            if (ppc < 8 || ppc > 256) return Fail("ppc must be 8..256.");
            int W = w * ppc, H = h * ppc;
            if (W > 8192 || H > 8192) return Fail("frame " + W + "x" + H + " exceeds 8192 px; split the board into tiles.");
            frames = Math.Max(2, frames);
            var tcs = new TaskCompletionSource<object>();
            object armErr = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (Current.ProgramState != ProgramState.Playing) return Fail("ProgramState is " + Current.ProgramState + ", need Playing.");
                if (!WorldRendererUtility.DrawingMap) return Fail("The world view is open; the map is not being drawn.");
                var rect = new CellRect(x, z, w, h);
                if (!rect.InBounds(map)) return Fail("rect is not inside the map (" + map.Size.x + "x" + map.Size.z + ").");
                if (artboardBusy) return Fail("another artboard_capture is in progress.");
                JawaArtboardCapture.Install();
                if (!JawaArtboardCapture.Installed) return Fail("view-rect patch not installed: " + JawaArtboardCapture.InstallError);
                try { Directory.CreateDirectory(Path.GetDirectoryName(path)); }
                catch (Exception e) { return Fail("Cannot create the output folder: " + e.Message); }
                if (clearSelection) Find.Selector?.ClearSelection();
                artboardBusy = true;
                int token = ++JawaArtboardCapture.Token;
                JawaArtboardCapture.Rect = rect;
                JawaArtboardCapture.Armed = true;
                Find.CameraDriver.StartCoroutine(ArtboardRenderCo(token, map, rect, W, H, ppc, path, frames, tcs));
                return null;
            }).ConfigureAwait(false);
            if (armErr != null) return armErr;
            Task done = await Task.WhenAny(tcs.Task, Task.Delay(timeoutMs, cancellationToken)).ConfigureAwait(false);
            if (done != tcs.Task)
            {
                await ctx.MainThread.InvokeAsync<object>(() =>
                {
                    JawaArtboardCapture.Token++;          // the coroutine, if it ever resumes, sees a stale token and quits
                    JawaArtboardCapture.Armed = false;
                    artboardBusy = false;
                    return null;
                }).ConfigureAwait(false);
                return Fail("Timed out after " + timeoutMs + " ms waiting for " + frames + " rendered frames - is the game " +
                            "window minimised with Run in background off, or the game loading? Nothing was written.");
            }
            return tcs.Task.Result;
        }

        private static IEnumerator ArtboardRenderCo(int token, Map map, CellRect rect, int W, int H, int ppc, string path,
            int frames, TaskCompletionSource<object> tcs)
        {
            int armed = Time.frameCount;
            // yield null resumes after every Update of the next frame, i.e. after Root_Play.Update -> MapUpdate queued
            // this frame's draws with the armed (encapsulated) view rect, and before anything is rendered.
            while (Time.frameCount < armed + frames)
            {
                yield return null;
                if (token != JawaArtboardCapture.Token) yield break;
            }
            object result;
            try { result = ArtboardRenderNow(map, rect, W, H, ppc, path, armed); }
            catch (Exception e) { result = Fail("render threw " + Inner(e)); }
            finally
            {
                JawaArtboardCapture.Armed = false;
                artboardBusy = false;
            }
            tcs.TrySetResult(result);
        }

        private static object ArtboardRenderNow(Map map, CellRect rect, int W, int H, int ppc, string path, int armedFrame)
        {
            if (Find.CurrentMap != map) return Fail("the current map changed during the capture.");
            Camera cam = Find.Camera;
            if (cam == null) return Fail("Find.Camera is null.");
            Camera water = null;
            try { water = Current.SubcameraDriver?.GetSubcamera(SubcameraDefOf.WaterDepth); } catch { }

            Vector3 camPos = cam.transform.position;
            float camSize = cam.orthographicSize;
            RenderTexture camTarget = cam.targetTexture;
            Vector3 wPos = water != null ? water.transform.position : Vector3.zero;
            float wSize = water != null ? water.orthographicSize : 0f;

            float cx = rect.minX + rect.Width / 2f, cz = rect.minZ + rect.Height / 2f;
            var rt = new RenderTexture(W, H, 24, RenderTextureFormat.ARGB32) { antiAliasing = 1 };
            rt.Create();
            Texture2D tex = null;
            RenderTexture prevActive = RenderTexture.active;
            bool restored;
            try
            {
                if (water != null)
                {
                    water.transform.position = new Vector3(cx, wPos.y, cz);
                    water.orthographicSize = rect.Height / 2f;
                    water.aspect = (float)W / H;
                    water.Render();
                }
                cam.transform.position = new Vector3(cx, camPos.y, cz);
                cam.orthographicSize = rect.Height / 2f;
                cam.targetTexture = rt;
                cam.Render();
                tex = new Texture2D(W, H, TextureFormat.RGB24, false);
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, W, H), 0, 0);
                tex.Apply(false);
            }
            finally
            {
                RenderTexture.active = prevActive;
                cam.targetTexture = camTarget;
                cam.transform.position = camPos;
                cam.orthographicSize = camSize;
                cam.ResetAspect();
                if (water != null)
                {
                    water.transform.position = wPos;
                    water.orthographicSize = wSize;
                    water.ResetAspect();
                }
                restored = cam.transform.position == camPos && cam.orthographicSize == camSize && cam.targetTexture == camTarget;
                rt.Release();
                UnityEngine.Object.Destroy(rt);
            }
            byte[] png = tex.EncodeToPNG();
            UnityEngine.Object.Destroy(tex);
            File.WriteAllBytes(path, png);
            if (!File.Exists(path)) return Fail("PNG write returned but no file exists at '" + path + "'.");
            long size = new FileInfo(path).Length;
            int fogged = rect.Cells.Count(c => map.fogGrid.IsFogged(c));
            int roofed = rect.Cells.Count(c => map.roofGrid.Roofed(c));
            float ax = ppc, bx = -rect.minX * (float)ppc, az = -ppc, bz = (rect.maxZ + 1) * (float)ppc;
            return new
            {
                success = true,
                message = "rendered " + rect + " at " + ppc + " px/cell to " + path + " (" + size + " bytes)" +
                          (fogged > 0 ? "; WARNING " + fogged + " fogged cells" : ""),
                path,
                ppc,
                rect = RectObj(rect),
                frame = new[] { W, H },
                origin_px = new[] { bx, bz },
                mapping = new { ax, bx, az, bz },
                method = "offscreen: main camera + WaterDepth subcamera rendered to a RenderTexture after Update",
                waterSubcamera = water != null,
                frameArmed = armedFrame,
                frameRendered = Time.frameCount,
                ticksGame = TicksGameSafe(),
                paused = Find.TickManager?.Paused,
                skyGlow = map.skyManager.CurSkyGlow,
                foggedCells = fogged,
                roofedCells = roofed,
                cameraRestored = restored,
                fileSizeBytes = size
            };
        }

        // ════════════════════════════════════════════════════════════════
        //  jawa/thing_screen_rects
        // ════════════════════════════════════════════════════════════════
        [Tool(
            "jawa/thing_screen_rects",
            Description =
                "List the spawned things whose cell lies in the rect x,z,w,h of the CURRENT map with their world draw " +
                "rects and the same rects in PIXELS of an artboard_capture of that rect at ppc (v down), so an existing " +
                "review map can be cut into per-thing crops without a recipe. Pawns use their life-stage drawSize " +
                "(humanlike: a nominal 1.5); other things Graphic.drawSize. Filth, motes and blueprints are skipped unless " +
                "includeMinor. Capped at 'limit' rows and says when it truncated.",
            ResultDescription = "success, count, truncated, things[{thingId, def, kind, cell{x,z}, rot, drawRect, px{l,t,r,b}}].")]
        public static async Task<object> ThingScreenRects(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect min cell x (same rect as the capture).")] int x = 0,
            [ToolParameter(Description = "Rect min cell z.")] int z = 0,
            [ToolParameter(Description = "Rect width in cells.")] int w = 0,
            [ToolParameter(Description = "Rect height in cells.")] int h = 0,
            [ToolParameter(Description = "Pixels per cell of that capture.")] int ppc = 48,
            [ToolParameter(Description = "Include filth, motes, blueprints and frames.")] bool includeMinor = false,
            [ToolParameter(Description = "Maximum rows. Default 2000.")] int limit = 2000)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (w <= 0 || h <= 0) return Fail("w and h must be positive.");
                var rect = new CellRect(x, z, w, h).ClipInsideMap(map);
                var rows = new List<object>();
                var seen = new HashSet<int>();
                bool truncated = false;
                foreach (IntVec3 c in rect.Cells)
                {
                    foreach (Thing t in c.GetThingList(map))
                    {
                        if (!seen.Add(t.thingIDNumber) || t.Position != c) continue;
                        if (!includeMinor && (t is Filth || t is Mote || t is Blueprint || t is Frame)) continue;
                        if (rows.Count >= limit) { truncated = true; break; }
                        ArtDrawRect dr = DrawRectOf(t);
                        float l = (dr.x - x) * ppc, r = (dr.x + dr.w - x) * ppc;
                        float top = (z + h - (dr.z + dr.h)) * ppc, bot = (z + h - dr.z) * ppc;
                        rows.Add(new
                        {
                            thingId = t.ThingID, def = t.def.defName, kind = t.def.category.ToString(),
                            cell = new { x = c.x, z = c.z }, rot = t.Rotation.ToStringHuman(),
                            drawRect = new { dr.x, dr.z, dr.w, dr.h, dr.source },
                            px = new { l, t = top, r, b = bot }
                        });
                    }
                    if (truncated) break;
                }
                return (object)new { success = true, rect = RectObj(rect), ppc, count = rows.Count, truncated, things = rows, ticksGame = TicksGameSafe() };
            });
        }
    }
}
