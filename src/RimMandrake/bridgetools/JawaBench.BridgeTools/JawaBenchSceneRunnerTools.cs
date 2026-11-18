// JawaBenchSceneRunnerTools.cs - jawa/run_scenes, the shared in-game scene runner (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE).
//
// WHY: live_test_speed_assessment_2026-11-12.md section 4 step 5 (owner pick 14, 2026-11-12: "14 (prioritize this)"). About
// 110 proof C# files had no common shape, and each python driver paid one bridge round trip per Stage, per clock step and per
// Verdict. ONE call here runs a whole suite: each scene on its own plot, staged, ticked in process (DoSingleTick inside a
// per-frame wall budget, so the game keeps drawing) and judged, and every scene answers the same row table.
//
// The contract (scene signature, RMTestAttribute, Origins/SuiteBegin/SuiteEnd hooks, the row table) and every pure rule are
// in JawaBenchSceneRunnerCore.cs, unit-tested offline. This file only touches the game.
//
// THE SAVE AROUND THE RUN is the caller's (owner 2026-11-17, "Just save the test in a file and reload"): the python driver
// src/RimMandrake/Utils/scene_runner.py wraps this call in modcheck/scene_snapshot.py. A test-only tool: CAMPAIGN refuses it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using SR = JawaBench.BridgeTools.JawaBenchSceneRunnerCore;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private sealed class SceneRunState
        {
            public Type suite;
            public List<SR.Spec> specs;
            public List<int[]> origins;
            public Game game;
            public Map map;
            public string begin;
        }

        [Tool(
            "jawa/run_scenes",
            Description =
                "Shared in-game scene runner: ONE call runs a suite of [RMTest] scenes from a mod's PROOF build, each on its own " +
                "plot of the current map (the suite's Origins hook, else a 15-cell grid): stage, step its ticks in process " +
                "(paused, DoSingleTick inside frameBudgetMs per frame), read the scene's Outside counts with vanilla calls, judge. " +
                "Every scene answers rows of scene/check/status/measured/expected/source/cause, status PASS, FAIL or UNMEASURED " +
                "(UNMEASURED always names its cause). MODIFIES THE MAP (scenes clear and build their plots): scratch maps only, " +
                "and the caller saves before and reloads after (src/RimMandrake/Utils/scene_runner.py does). Refused before any " +
                "scene: an unknown type or scene, a suite with problems, more than 30000 ticks a scene or 120000 a run.",
            ResultDescription =
                "success (the run completed; NOT the verdict), overall (PASS | FAIL | UNMEASURED | EMPTY), rows[], scenes[] " +
                "(scene, origin, ticksWanted, ticksStepped, frames, stageMs, tickMs, judgeMs), suiteBegin, problems[], wallS, ticksGame.")]
        public static async Task<object> RunScenes(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Full name of the suite type, e.g. RimMandrake.ExplosiveKnockback.RM_KnockbackScenes.")]
            string type = null,
            [ToolParameter(Description = "Comma list of scene names, in run order; empty = every scene the suite declares.", DefaultValue = "")]
            string scenes = "",
            [ToolParameter(Description = "Ticks per scene; 0 = each scene's own Ticks (default 300).", DefaultValue = 0)]
            int ticks = 0,
            [ToolParameter(Description = "Main-thread ms per frame spent stepping (5..200).", DefaultValue = 40.0)]
            double frameBudgetMs = 40,
            [ToolParameter(Description = "Wall budget for the whole run; scenes not reached are UNMEASURED.", DefaultValue = 600000)]
            int timeoutMs = 600000)
        {
            string typeName = (type ?? "").Trim(), csv = scenes ?? "";
            int tickOverride = ticks;
            double budget = Math.Max(5, Math.Min(200, frameBudgetMs));
            var wall = Stopwatch.StartNew();
            var problems = new List<string>();
            SceneRunState st = null;

            object refused = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null || Find.CurrentMap == null) return Fail("No game/map loaded.");
                if (typeName.Length == 0) return Fail("Give type = the suite's full type name.");
                Type t = GenTypes.GetTypeInAnyAssembly(typeName);
                if (t == null) return Fail("Type not found: " + typeName + " (mod inactive, a RELEASE build without RM_PROOFS, or the name is wrong).");
                var specs = SR.Discover(t, problems);
                if (problems.Count > 0) return Fail("The suite " + typeName + " has problems; nothing was staged.", new { problems });
                var unknown = new List<string>();
                var chosen = SR.Select(specs, csv, unknown);
                if (unknown.Count > 0) return Fail("Unknown scene(s): " + string.Join(", ", unknown), new { known = specs.Select(s => s.name).ToList() });
                if (chosen.Count == 0) return Fail("The suite " + typeName + " declares no [RMTest] scene.");
                long total = chosen.Sum(s => (long)SR.TicksFor(s, tickOverride));
                var tooLong = chosen.Where(s => SR.TicksFor(s, tickOverride) > SR.MaxSceneTicks).Select(s => s.name).ToList();
                if (tooLong.Count > 0) return Fail("More than " + SR.MaxSceneTicks + " ticks for: " + string.Join(", ", tooLong));
                if (total > SR.MaxRunTicks) return Fail("The run asks " + total + " ticks; the cap is " + SR.MaxRunTicks + ". Split it.");
                Map map = Find.CurrentMap;
                List<int[]> origins;
                MethodInfo om = SceneHook(t, "Origins");
                if (om != null)
                {
                    origins = SR.ParseOrigins(om.Invoke(null, new object[] { chosen.Count.ToString() }) as string);
                    if (origins == null) return Fail("The suite's Origins answer is unreadable (want x,z;x,z;...).");
                }
                else origins = SR.Grid(map.Size.x, map.Size.z, SR.DefaultPitch, chosen.Count);
                if (origins.Count < chosen.Count) return Fail("Only " + origins.Count + " plots on this map for " + chosen.Count + " scenes.");
                st = new SceneRunState { suite = t, specs = chosen, origins = origins, game = Current.Game, map = map };
                Find.TickManager.CurTimeSpeed = TimeSpeed.Paused;
                return null;
            });
            if (refused != null) return refused;

            var rows = new List<SR.Row>();
            var sceneInfo = new List<object>();
            SceneRunState run = st;
            bool begun = false;
            try
            {
                object b = await ctx.MainThread.InvokeAsync<object>(() =>
                {
                    MethodInfo bm = SceneHook(run.suite, "SuiteBegin");
                    if (bm == null) return "none";
                    try { return "ran: " + SR.Clip(bm.Invoke(null, new object[] { "" }) as string); }
                    catch (Exception e) { return new Exception("SuiteBegin threw " + SceneInner(e)); }
                });
                if (b is Exception be)
                {
                    foreach (SR.Spec s in run.specs) rows.Add(SR.Unmeasured_(s.name, "SUITE_BEGIN", be.Message));
                    return SceneResult(true, rows, sceneInfo, be.Message, problems, wall);
                }
                begun = true;
                run.begin = b as string;
                for (int i = 0; i < run.specs.Count; i++)
                {
                    SR.Spec spec = run.specs[i];
                    int ox = run.origins[i][0], oz = run.origins[i][1];
                    int want = SR.TicksFor(spec, tickOverride);
                    if (cancellationToken.IsCancellationRequested || wall.ElapsedMilliseconds > timeoutMs)
                    {
                        rows.Add(SR.Unmeasured_(spec.name, "NOT_RUN", cancellationToken.IsCancellationRequested ? "the call was cancelled" : "the run passed timeoutMs " + timeoutMs));
                        continue;
                    }
                    var sw = Stopwatch.StartNew();
                    SR.Row refusal = null;
                    Delegate judge = null;
                    object staged = await ctx.MainThread.InvokeAsync<object>(() =>
                    {
                        if (!SceneSameGame(run)) return new Exception("the game or map changed under the run");
                        try { return spec.method.Invoke(null, new object[] { spec.name, ox, oz }); }
                        catch (Exception e) { return new Exception("staging threw " + SceneInner(e)); }
                    });
                    long stageMs = sw.ElapsedMilliseconds;
                    if (staged is Exception se) refusal = SR.Unmeasured_(spec.name, "STAGE", se.Message);
                    else judge = SR.StageResult(spec.name, staged, out refusal);
                    if (refusal != null)
                    {
                        rows.Add(refusal);
                        sceneInfo.Add(new { scene = spec.name, origin = ox + "," + oz, ticksWanted = want, ticksStepped = 0, frames = 0, stageMs, tickMs = 0L, judgeMs = 0L });
                        continue;
                    }
                    // the ticks: one main-thread slice per frame, each stepping until the frame budget or the target
                    sw.Restart();
                    int stepped = 0, frames = 0;
                    string shortWhy = null;
                    while (stepped < want)
                    {
                        if (cancellationToken.IsCancellationRequested) { shortWhy = "the call was cancelled"; break; }
                        if (wall.ElapsedMilliseconds > timeoutMs) { shortWhy = "the run passed timeoutMs " + timeoutMs; break; }
                        int left = want - stepped;
                        object got = await ctx.MainThread.InvokeAsync<object>(() =>
                        {
                            if (!SceneSameGame(run)) return -1;
                            var tm = Find.TickManager;
                            tm.CurTimeSpeed = TimeSpeed.Paused;
                            var fw = Stopwatch.StartNew();
                            int n = 0;
                            try
                            {
                                while (n < left && fw.Elapsed.TotalMilliseconds < budget)
                                {
                                    tm.DoSingleTick();
                                    n++;
                                }
                            }
                            catch (Exception e) { return new Exception("a tick threw " + SceneInner(e) + " after " + n + " ticks this frame"); }
                            return n;
                        });
                        frames++;
                        if (got is Exception te) { shortWhy = te.Message; break; }
                        int moved = got is int k ? k : -1;
                        if (moved < 0) { shortWhy = "the game or map changed under the run"; break; }
                        if (moved == 0) { shortWhy = "a frame stepped no tick"; break; }
                        stepped += moved;
                    }
                    long tickMs = sw.ElapsedMilliseconds;
                    sw.Restart();
                    var sceneRows = await ctx.MainThread.InvokeAsync<object>(() =>
                    {
                        var o = new List<SR.Row>();
                        bool same = SceneSameGame(run);
                        if (!string.IsNullOrWhiteSpace(spec.outside))
                            foreach (SR.OutsideCheck c in SR.ParseOutside(spec.outside, out _))
                                o.Add(same ? SR.OutsideRow(spec.name, c, SceneCountOutside(run.map, c, ox, oz)) : SR.OutsideRow(spec.name, c, -1, "the game or map changed under the run"));
                        if (!same) { o.Add(SR.Unmeasured_(spec.name, "VERDICT", "the game or map changed under the run")); return o; }
                        try { o.AddRange(SR.Normalize(spec.name, judge.DynamicInvoke())); }
                        catch (Exception e) { o.Add(SR.Unmeasured_(spec.name, "VERDICT", "the judge threw " + SceneInner(e))); }
                        return o;
                    }) as List<SR.Row>;
                    long judgeMs = sw.ElapsedMilliseconds;
                    rows.AddRange(SR.ShortAdvance(sceneRows ?? new List<SR.Row> { SR.Unmeasured_(spec.name, "VERDICT", "no rows came back") }, stepped, want, shortWhy));
                    sceneInfo.Add(new { scene = spec.name, origin = ox + "," + oz, ticksWanted = want, ticksStepped = stepped, frames, stageMs, tickMs, judgeMs });
                }
            }
            finally
            {
                if (begun)
                {
                    object e = await ctx.MainThread.InvokeAsync<object>(() =>
                    {
                        MethodInfo em = SceneHook(run.suite, "SuiteEnd");
                        if (em == null) return null;
                        try { em.Invoke(null, new object[] { "" }); return null; }
                        catch (Exception ex) { return "SuiteEnd threw " + SceneInner(ex); }
                    });
                    if (e is string why) rows.Add(SR.Unmeasured_("(suite)", "SUITE_END", why + ": the suite's own state (settings, journal) may not be put back"));
                }
            }
            return SceneResult(true, rows, sceneInfo, run.begin, problems, wall);
        }

        private static MethodInfo SceneHook(Type t, string name)
        {
            MethodInfo m = t.GetMethod(name, BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(string) }, null);
            return m != null && m.ReturnType == typeof(string) ? m : null;
        }

        private static bool SceneSameGame(SceneRunState r) =>
            Current.Game == r.game && Find.CurrentMap == r.map && Find.Maps.Contains(r.map);

        private static string SceneInner(Exception e)
        {
            Exception x = e is TargetInvocationException && e.InnerException != null ? e.InnerException : e;
            return x.GetType().Name + ": " + SR.Clip(x.Message, 300);
        }

        /// <summary>A vanilla count over the rect at origin + (dx, dz): never the mod's own state.</summary>
        private static int SceneCountOutside(Map map, SR.OutsideCheck c, int ox, int oz)
        {
            int n = 0;
            foreach (IntVec3 cell in new CellRect(ox + c.dx, oz + c.dz, c.w, c.h).ClipInsideMap(map))
                foreach (Thing t in cell.GetThingList(map))
                {
                    if (c.kind == "haulables" ? t.def.EverHaulable : c.kind == "pawns" ? t is Pawn : t is Pawn p && p.IsColonist) n++;
                }
            return n;
        }

        private static object SceneResult(bool completed, List<SR.Row> rows, List<object> scenes, string begin, List<string> problems, Stopwatch wall) =>
            new
            {
                success = completed, overall = SR.Overall(rows), rows = rows.Select(r => r.ToDict()).ToList(), scenes,
                suiteBegin = begin, problems, wallS = Math.Round(wall.Elapsed.TotalSeconds, 2), ticksGame = TicksGameSafe(),
            };
    }
}
