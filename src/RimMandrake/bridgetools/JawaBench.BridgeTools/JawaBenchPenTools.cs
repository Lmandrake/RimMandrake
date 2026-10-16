// JawaBenchPenTools.cs - release review-pen animals from their pinning Wait job, and pin them again.
//
// WHY THIS FILE EXISTS
// =====================
// REVIEW_SAVE_RELEASE_PENS. Review maps (Pyrelands human_review.py, via the artboard
// stager's pawn ops) place each pen specimen with a 60000-tick JobDefOf.Wait job so it
// holds its planned facing. A save made then keeps every animal frozen for a day of game
// time, and the owner cannot watch them move. jawa/order_pawn refuses wild animals
// (0/64 accepted, lesson 20261016T035329Z), so nothing on the bridge could let them go.
//
// API, read from 1.6 source (also cited in JawaBenchJobTools.cs's header):
//   Verse.AI.Pawn_JobTracker.EndCurrentJob(JobCondition, bool startNewJob, bool canReturnToPool)
//       - startNewJob=true asks the think tree for the next job at once, so the job the
//         animal takes next is readable in the same main-thread step.
//   Verse.AI.Pawn_JobTracker.StartJob(Job, JobCondition, ...) + JobMaker.MakeJob(JobDefOf.Wait, ticks)
//       - exactly how the artboard pins a pawn, so pen_pin is the same pin.
//   Verse.Pawn.Notify_Teleported(bool endCurrentJob, bool resetTweenedPos)
//
// Design rules kept: every selected pawn is reported (changed / skipped with a reason);
// the job each pawn holds AFTER is read back from CurJobDef, never assumed; a release
// that leaves the pawn in Wait is counted as NOT changed.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private sealed class PenStash { public IntVec3 cell; public Rot4 rot; public int releasedTick; }

        // Where each released animal stood and faced when it was let go, so pen_pin can put it back.
        // Weak keys: a destroyed or garbage-collected pawn drops out by itself. Not saved with the game.
        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Pawn, PenStash> PenStashes =
            new System.Runtime.CompilerServices.ConditionalWeakTable<Pawn, PenStash>();

        private static bool TryParsePenRects(string rects, out List<CellRect> outRects, out string err)
        {
            outRects = new List<CellRect>();
            err = null;
            if (string.IsNullOrWhiteSpace(rects)) return true;
            foreach (string part in rects.Split(new[] { ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string[] f = part.Split(',');
                if (f.Length != 4) { err = "rect '" + part.Trim() + "' is not x,z,w,h"; return false; }
                int[] v = new int[4];
                for (int i = 0; i < 4; i++)
                    if (!int.TryParse(f[i].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out v[i]))
                    { err = "rect '" + part.Trim() + "' has a non-integer field"; return false; }
                if (v[2] <= 0 || v[3] <= 0) { err = "rect '" + part.Trim() + "' has w or h <= 0"; return false; }
                outRects.Add(new CellRect(v[0], v[1], v[2], v[3]));
            }
            return true;
        }

        // The selection shared by both tools. Returns null and sets err on a bad argument.
        // scope "map" means: release -> every animal currently in a Wait job; pin -> every animal pen_release let go.
        private static List<Pawn> SelectPenPawns(Map map, string rects, string pawns, bool mapScope, bool forPin,
                                                 bool includeHumanlike, List<object> skipped, out string err)
        {
            err = null;
            int given = (string.IsNullOrWhiteSpace(rects) ? 0 : 1) + (string.IsNullOrWhiteSpace(pawns) ? 0 : 1) + (mapScope ? 1 : 0);
            if (given != 1) { err = "Give exactly one of rects, pawns, or allMap=true (got " + given + ")."; return null; }
            var picked = new List<Pawn>();
            if (!string.IsNullOrWhiteSpace(pawns))
            {
                foreach (string id in pawns.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    Pawn p = FindPawn(id.Trim(), out string e);
                    if (p == null) { skipped.Add(new { pawn = id.Trim(), reason = "not found: " + e }); continue; }
                    if (!p.Spawned || p.Map != map) { skipped.Add(new { pawn = p.ThingID, reason = "not spawned on the current map" }); continue; }
                    picked.Add(p);
                }
            }
            else
            {
                if (!TryParsePenRects(rects, out List<CellRect> rs, out err)) return null;
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
                {
                    if (mapScope)
                    {
                        if (forPin ? !PenStashes.TryGetValue(p, out PenStash _) : p.CurJobDef != JobDefOf.Wait) continue;
                    }
                    else if (!rs.Any(r => r.Contains(p.Position))) continue;
                    picked.Add(p);
                }
            }
            var kept = new List<Pawn>();
            foreach (Pawn p in picked.Distinct())
            {
                if (p.RaceProps == null) { skipped.Add(new { pawn = p.ThingID, reason = "no race" }); continue; }
                if (p.RaceProps.Humanlike && !includeHumanlike) { skipped.Add(new { pawn = p.ThingID, reason = "humanlike (pass includeHumanlike=true)" }); continue; }
                if (!p.RaceProps.Humanlike && !p.RaceProps.Animal) { skipped.Add(new { pawn = p.ThingID, reason = "not an animal (mech/other)" }); continue; }
                if (p.Dead || p.Downed) { skipped.Add(new { pawn = p.ThingID, reason = p.Dead ? "dead" : "downed" }); continue; }
                if (p.jobs == null) { skipped.Add(new { pawn = p.ThingID, reason = "no job tracker" }); continue; }
                kept.Add(p);
            }
            return kept;
        }

        private static Dictionary<string, int> JobHistogram(IEnumerable<Pawn> ps)
        {
            var h = new Dictionary<string, int>();
            foreach (Pawn p in ps)
            {
                string k = p.CurJobDef?.defName ?? "(none)";
                h[k] = h.TryGetValue(k, out int n) ? n + 1 : 1;
            }
            return h;
        }

        [Tool(
            "jawa/pen_release",
            Description =
                "End the long Wait job that pins review-pen animals (the artboard stager and review-map builders give each " +
                "pen specimen a 60000-tick Wait so it holds its facing), so they take their own next job and wander inside " +
                "their walled pen. Select with exactly ONE of: rects ('x,z,w,h;x,z,w,h' - every animal standing in any), " +
                "pawns (comma ids), or allMap=true (every animal on the current map whose current job is Wait). Only a pawn " +
                "whose CURRENT job is Wait is touched; others are reported in skipped with their job. Humanlikes are skipped " +
                "unless includeHumanlike=true. Each released pawn's cell and rotation are remembered (in memory only, not in " +
                "the save) so the pin tool (pen_pin) can put it back. NOTHING MOVES WHILE PAUSED: unpause to watch. A save " +
                "made after this keeps them released. The pen must be closed (walls, a door wild animals cannot open) or they leave.",
            ResultDescription =
                "success, selected, released, notReleased (still Wait after ending it), skipped[{pawn,reason}], " +
                "jobsBefore{def:n}, jobsAfter{def:n}, pawns[{pawn,kind,x,z,jobAfter}], ticksGame.")]
        public static async Task<object> PenRelease(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell rects 'x,z,w,h' separated by ';'. Every animal standing in any of them is selected.")] string rects = null,
            [ToolParameter(Description = "Comma-separated pawn ids (thingIDNumber, ThingID, or name).")] string pawns = null,
            [ToolParameter(Description = "true: every animal on the current map whose current job is Wait.")] bool allMap = false,
            [ToolParameter(Description = "Also release humanlike pawns in the selection (default false).")] bool includeHumanlike = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                var skipped = new List<object>();
                List<Pawn> sel = SelectPenPawns(map, rects, pawns, allMap, false, includeHumanlike, skipped, out string err);
                if (sel == null) return Fail(err);
                var before = JobHistogram(sel);
                var rows = new List<object>();
                int released = 0, stuck = 0;
                foreach (Pawn p in sel)
                {
                    if (p.CurJobDef != JobDefOf.Wait)
                    {
                        skipped.Add(new { pawn = p.ThingID, reason = "not in a Wait job (" + (p.CurJobDef?.defName ?? "none") + ")" });
                        continue;
                    }
                    IntVec3 cell = p.Position;
                    Rot4 rot = p.Rotation;
                    p.jobs.ClearQueuedJobs();
                    p.jobs.EndCurrentJob(JobCondition.InterruptForced, true, true);
                    string after = p.CurJobDef?.defName ?? "(none)";
                    if (p.CurJobDef == JobDefOf.Wait) stuck++;
                    else
                    {
                        released++;
                        PenStashes.Remove(p);
                        PenStashes.Add(p, new PenStash { cell = cell, rot = rot, releasedTick = TicksGameSafe() });
                    }
                    rows.Add(new { pawn = p.ThingID, kind = p.kindDef?.defName, x = cell.x, z = cell.z, jobAfter = after });
                }
                return (object)new
                {
                    success = sel.Count > 0 && stuck == 0 && released > 0,
                    message = sel.Count == 0 ? "selection matched no eligible pawn" :
                              released == 0 ? "no pawn left its Wait job" : null,
                    selected = sel.Count,
                    released,
                    notReleased = stuck,
                    skipped,
                    jobsBefore = before,
                    jobsAfter = JobHistogram(sel),
                    paused = Find.TickManager?.Paused,
                    pawns = rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        [Tool(
            "jawa/pen_pin",
            Description =
                "Pin animals again with a Wait job of 'ticks' (default 60000, one day), the same pin the artboard stager " +
                "gives pen specimens. Select with exactly ONE of: rects ('x,z,w,h;...'), pawns (comma ids), or allMap=true " +
                "(every animal the release tool (pen_release) let go this game session). restore=true first puts each " +
                "pawn back on the cell it was released from and turns it to that facing - only for pawns released this " +
                "session (the memory is not in the save); the cell must be standable and hold no other pawn, otherwise the " +
                "pawn is pinned where it stands and the reason is reported. Rotation is read back after the pin.",
            ResultDescription =
                "success, selected, pinned, returnedHome, homeRefused[{pawn,reason}], skipped[{pawn,reason}], " +
                "pawns[{pawn,x,z,rotation,job}], ticksGame.")]
        public static async Task<object> PenPin(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell rects 'x,z,w,h' separated by ';'.")] string rects = null,
            [ToolParameter(Description = "Comma-separated pawn ids.")] string pawns = null,
            [ToolParameter(Description = "true: every animal released by the release tool this session.")] bool allMap = false,
            [ToolParameter(Description = "Return each pawn to its release cell and facing first (default true).")] bool restore = true,
            [ToolParameter(Description = "Wait length in ticks, 1-600000 (default 60000).")] int ticks = 60000,
            [ToolParameter(Description = "Also pin humanlike pawns in the selection (default false).")] bool includeHumanlike = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (ticks < 1 || ticks > 600000) return Fail("ticks must be 1-600000, got " + ticks + ".");
                var skipped = new List<object>();
                List<Pawn> sel = SelectPenPawns(map, rects, pawns, allMap, true, includeHumanlike, skipped, out string err);
                if (sel == null) return Fail(err);
                var homeRefused = new List<object>();
                var rows = new List<object>();
                int pinned = 0, home = 0;
                foreach (Pawn p in sel)
                {
                    Rot4? want = null;
                    if (restore && PenStashes.TryGetValue(p, out PenStash st))
                    {
                        want = st.rot;
                        if (p.Position != st.cell)
                        {
                            Pawn other = st.cell.GetFirstPawn(map);
                            if (!st.cell.InBounds(map) || !st.cell.Standable(map)) homeRefused.Add(new { pawn = p.ThingID, reason = "release cell " + st.cell + " not standable" });
                            else if (other != null && other != p) homeRefused.Add(new { pawn = p.ThingID, reason = "release cell " + st.cell + " holds " + other.ThingID });
                            else { p.Position = st.cell; p.Notify_Teleported(true, true); home++; }
                        }
                        else home++;
                    }
                    else if (restore) homeRefused.Add(new { pawn = p.ThingID, reason = "not released this session: pinned where it stands" });
                    p.jobs.ClearQueuedJobs();
                    p.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Wait, ticks), JobCondition.InterruptForced);
                    if (want.HasValue) p.Rotation = want.Value;
                    if (p.CurJobDef == JobDefOf.Wait) { pinned++; PenStashes.Remove(p); }
                    rows.Add(new { pawn = p.ThingID, x = p.Position.x, z = p.Position.z, rotation = p.Rotation.ToStringHuman(),
                                   job = p.CurJobDef?.defName ?? "(none)" });
                }
                return (object)new
                {
                    success = sel.Count > 0 && pinned == sel.Count,
                    message = sel.Count == 0 ? "selection matched no eligible pawn" : null,
                    selected = sel.Count,
                    pinned,
                    returnedHome = home,
                    homeRefused,
                    skipped,
                    pawns = rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
