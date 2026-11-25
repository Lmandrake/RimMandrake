// JawaBenchSceneRunnerTools.cs - jawa/run_scenes, the shared in-game scene runner (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE).
//
// WHY: live_test_speed_assessment_2026-11-12.md section 4 step 5 (owner pick 14, 2026-11-12: "14 (prioritize this)"). About
// 110 proof C# files had no common shape, and each python driver paid one bridge round trip per Stage, per clock step and per
// Verdict. ONE call here runs a whole suite: each scene on its own plot, staged, ticked in process (DoSingleTick inside a
// per-frame wall budget, one slice per Unity frame, so the game keeps drawing) and judged, and every scene answers the same
// row table.
//
// FRAMES: an awaited MainThread.InvokeAsync is NOT a frame boundary (RimBridge may run queued work inline and drains its
// queue in one pump; Codex review 2026-11-18). Each tick slice therefore reads Time.frameCount and steps only on a frame no
// earlier slice used; between slices the call waits off the main thread. `frames` counts distinct frames that stepped.
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
        private const int SceneFrameStallMs = 15000;       // no new Unity frame this long: the game is not drawing (minimised?)

        private sealed class SceneRunState
        {
            public Type suite;
            public List<SR.Spec> specs;
            public List<int[]> origins;
            public Game game;
            public Map map;
            public MethodInfo begin, end;
            public string beginText;
            public int lastFrame = -1;
            public string until;                 // the condition that ends each scene's ticks, or null
        }

        private const string SceneRunnerTool = "jawa/run_scenes";

        /// <summary>One main-thread slice's answer: ticks stepped (also when a tick then threw), whether it ran on a new
        /// frame, and why it stopped early (null = it did not).</summary>
        private sealed class SceneSlice
        {
            public int ticks;
            public bool newFrame;
            public string stop;
            public bool ended;                   // the condition run ended on the last tick stepped
        }

        [Tool(
            "jawa/run_scenes",
            Description =
                "Shared in-game scene runner: ONE call runs a suite of [RMTest] scenes from a mod's PROOF build, each on its own " +
                "plot of the current map (the suite's Origins hook, else a 15-cell grid): stage, step its ticks in process " +
                "(paused, DoSingleTick inside frameBudgetMs, one slice per Unity frame), read the scene's Outside counts with " +
                "vanilla calls, judge. Every scene answers rows of scene/check/status/measured/expected/source/cause, status PASS, " +
                "FAIL or UNMEASURED (UNMEASURED always names its cause). MODIFIES THE MAP (scenes clear and build their plots): " +
                "scratch maps only, and the caller saves before and reloads after (src/RimMandrake/Utils/scene_runner.py does). " +
                "Refused before any scene: an unknown type or scene, a suite with problems, more than 30000 ticks a scene or " +
                "120000 a run.",
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
            int timeoutMs = 600000,
            [ToolParameter(Description = "A condition (JSON node, the grammar of jawa/cond_eval), tested at the end of every tick of each scene: the scene's ticks end ON the tick where it turns true. Empty = each scene plays all its ticks.", DefaultValue = "")]
            string until = "")
        {
            string stopWhen = until ?? "";
            string typeName = (type ?? "").Trim(), csv = scenes ?? "";
            int tickOverride = ticks;
            double budget = Math.Max(5, Math.Min(200, frameBudgetMs));
            var wall = Stopwatch.StartNew();
            CancellationToken ct = cancellationToken;
            string Halt() => ct.IsCancellationRequested ? "the call was cancelled"
                : wall.ElapsedMilliseconds > timeoutMs ? "the run passed timeoutMs " + timeoutMs : null;
            var problems = new List<string>();
            SceneRunState st = null;

            object refused = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Halt() != null) return Fail("Not started: " + Halt() + ".");
                if (Current.Game == null || Find.CurrentMap == null) return Fail("No game/map loaded.");
                if (typeName.Length == 0) return Fail("Give type = the suite's full type name.");
                Type t = GenTypes.GetTypeInAnyAssembly(typeName);
                if (t == null) return Fail("Type not found: " + typeName + " (mod inactive, a RELEASE build without RM_PROOFS, or the name is wrong).");
                var specs = SR.Discover(t, problems);
                MethodInfo om = SRL.Hook(t, "Origins", problems), bm = SRL.Hook(t, "SuiteBegin", problems), em = SRL.Hook(t, "SuiteEnd", problems);
                if (problems.Count > 0) return Fail("The suite " + typeName + " has problems; nothing was staged.", new { problems });
                var unknown = new List<string>();
                var chosen = SR.Select(specs, csv, unknown);
                if (unknown.Count > 0) return Fail("Unknown scene(s): " + string.Join(", ", unknown), new { known = SRL.Names(specs) });
                if (chosen.Count == 0) return Fail("The suite " + typeName + " declares no [RMTest] scene.");
                long total = SRL.TotalTicks(chosen, tickOverride);
                var tooLong = SRL.TooLong(chosen, tickOverride);
                if (tooLong.Count > 0) return Fail("More than " + SR.MaxSceneTicks + " ticks for: " + string.Join(", ", tooLong));
                if (total > SR.MaxRunTicks) return Fail("The run asks " + total + " ticks; the cap is " + SR.MaxRunTicks + ". Split it.");
                Map map = Find.CurrentMap;
                List<int[]> origins;
                if (om != null)
                {
                    string answer;
                    try { answer = om.Invoke(null, new object[] { chosen.Count.ToString() }) as string; }
                    catch (Exception e) { return Fail("The suite's Origins hook threw " + SceneInner(e) + "; nothing was staged."); }
                    origins = SR.ParseOrigins(answer);
                    if (origins == null) return Fail("The suite's Origins answer is unreadable (want x,z;x,z;...): " + SR.Clip(answer, 200));
                }
                else origins = SR.Grid(map.Size.x, map.Size.z, SR.DefaultPitch, chosen.Count);
                if (origins.Count < chosen.Count) return Fail("Only " + origins.Count + " plots on this map for " + chosen.Count + " scenes.");
                if (stopWhen.Trim().Length > 0)
                {
                    JawaBenchSceneTick.MakeStep(SceneRunnerTool, stopWhen, null, SR.MaxSceneTicks, 0, map, out string whyNot, out var condRefused);
                    if (whyNot != null || condRefused != null) return condRefused ?? Fail(whyNot);
                }
                string held = JawaBenchSceneTick.StepOwner;
                if (held != null) return Fail(held + " is running");
                JawaBenchSceneTick.StepOwner = SceneRunnerTool;
                st = new SceneRunState { until = stopWhen.Trim().Length > 0 ? stopWhen : null, suite = t, specs = chosen, origins = origins, game = Current.Game, map = map, begin = bm, end = em };
                return null;
            });
            if (refused != null) return refused;

            var rows = new List<SR.Row>();
            var sceneInfo = new List<object>();
            SceneRunState run = st;
            bool armed = false;
            try
            {
                // cleanup is armed BEFORE SuiteBegin runs: a hook that changes some settings and then throws is still undone
                armed = true;
                object begun = await SceneDispatch(ctx, () =>
                {
                    if (Halt() != null) return "not begun: " + Halt();
                    if (!SceneSameGame(run)) return "not begun: the game or map changed";
                    Find.TickManager.CurTimeSpeed = TimeSpeed.Paused;
                    if (run.begin == null) { run.beginText = "none"; return null; }
                    try { run.beginText = "ran: " + SR.Clip(run.begin.Invoke(null, new object[] { "" }) as string); return null; }
                    catch (Exception e) { return "SuiteBegin threw " + SceneInner(e); }
                }, timeoutMs - wall.ElapsedMilliseconds);
                string beginError = begun is SceneStop bs ? "not begun: " + bs.why : begun as string;
                if (beginError != null)
                {
                    foreach (SR.Spec s in run.specs) rows.Add(SR.Unmeasured_(s.name, "SUITE_BEGIN", beginError));
                }
                else
                {
                    for (int i = 0; i < run.specs.Count; i++)
                        await RunOneScene(ctx, run, run.specs[i], run.origins[i][0], run.origins[i][1], SR.TicksFor(run.specs[i], tickOverride),
                            budget, Halt, () => timeoutMs - wall.ElapsedMilliseconds, rows, sceneInfo);
                }
            }
            finally
            {
                JawaBenchSceneTick.StepOwner = null;
                if (armed)
                {
                    // never the request's token: the suite's own state goes back even when the call was cancelled
                    string endError = await ctx.MainThread.InvokeAsync<object>(() =>
                    {
                        if (run.end == null) return null;
                        try { run.end.Invoke(null, new object[] { "" }); return null; }
                        catch (Exception ex) { return "SuiteEnd threw " + SceneInner(ex); }
                    }) as string;
                    if (endError != null) rows.Add(SR.Unmeasured_("(suite)", "SUITE_END", endError + ": the suite's own state (settings, journal) may not be put back"));
                }
            }
            return SceneResult(true, rows, sceneInfo, run.beginText, problems, wall);
        }

        /// <summary>A main-thread dispatch bounded by the run's deadline: when the main thread does not answer in msLeft, a
        /// SceneStop comes back at once. Every callback passed here checks halt() FIRST, so one that runs late (after its
        /// answer was given up) changes nothing.</summary>
        private static async Task<object> SceneDispatch(IRimBridgeContext ctx, Func<object> f, long msLeft)
        {
            Task<object> t = ctx.MainThread.InvokeAsync<object>(f);
            int wait = (int)Math.Max(1, Math.Min(int.MaxValue, msLeft));
            if (await Task.WhenAny(t, Task.Delay(wait)).ConfigureAwait(false) != t)
                return new SceneStop("the main thread did not answer before timeoutMs");
            return await t.ConfigureAwait(false);
        }

        private static async Task RunOneScene(IRimBridgeContext ctx, SceneRunState run, SR.Spec spec, int ox, int oz, int want, double budget,
            Func<string> halt, Func<long> msLeft, List<SR.Row> rows, List<object> sceneInfo)
        {
            const string Changed = "the game or map changed under the run";
            var sw = Stopwatch.StartNew();
            object staged = await SceneDispatch(ctx, () =>
            {
                string h = halt();
                if (h != null) return new SceneStop("not run: " + h);
                if (!SceneSameGame(run)) return new SceneStop(Changed);
                object r;
                try { r = spec.method.Invoke(null, new object[] { spec.name, ox, oz }); }
                catch (Exception e) { return new SceneStop("staging threw " + SceneInner(e)); }
                return SceneSameGame(run) ? r : new SceneStop("staging changed the game or map");
            }, msLeft());
            long stageMs = sw.ElapsedMilliseconds;
            SR.Row refusal = null;
            Delegate judge = null;
            if (staged is SceneStop ss) refusal = SR.Unmeasured_(spec.name, ss.why.StartsWith("not run") ? "NOT_RUN" : "STAGE", ss.why);
            else judge = SR.StageResult(spec.name, staged, out refusal);
            if (refusal != null)
            {
                rows.Add(refusal);
                sceneInfo.Add(new { scene = spec.name, origin = ox + "," + oz, ticksWanted = want, ticksStepped = 0, frames = 0, stageMs, tickMs = 0L, judgeMs = 0L });
                return;
            }
            JawaBenchSceneTickCore.SceneRun cond = null;
            if (run.until != null && want > 0)
            {
                object armedRun = await SceneDispatch(ctx, () =>
                {
                    string h = halt();
                    if (h != null) return new SceneStop(h);
                    if (!SceneSameGame(run)) return new SceneStop(Changed);
                    var c = JawaBenchSceneTick.MakeStep(SceneRunnerTool, run.until, null, want, 0, run.map, out string whyNot, out var condRefused);
                    if (c == null) return new SceneStop("the condition: " + (whyNot ?? condRefused["refused"] + " at " + condRefused["at"] + ": " + condRefused["detail"]));
                    JawaBenchSceneTick.ArmStep(c, run.map);
                    return c;
                }, msLeft());
                cond = armedRun as JawaBenchSceneTickCore.SceneRun;
                if (cond == null)
                {
                    rows.Add(SR.Unmeasured_(spec.name, "UNTIL", armedRun is SceneStop us ? us.why : "the condition run was not armed"));
                    sceneInfo.Add(new { scene = spec.name, origin = ox + "," + oz, ticksWanted = want, ticksStepped = 0, frames = 0, stageMs, tickMs = 0L, judgeMs = 0L });
                    return;
                }
            }
            // the ticks: one main-thread slice per NEW Unity frame, each stepping until the frame budget or the target
            sw.Restart();
            int stepped = 0, frames = 0;
            string shortWhy = null;
            var sinceFrame = Stopwatch.StartNew();
            while (stepped < want && (cond == null || cond.Running))
            {
                int left = want - stepped;
                object got = await SceneDispatch(ctx, () =>
                {
                    var o = new SceneSlice();
                    string h = halt();
                    if (h != null) { o.stop = h; return o; }
                    if (!SceneSameGame(run)) { o.stop = Changed; return o; }
                    int f = UnityEngine.Time.frameCount;
                    if (f == run.lastFrame) return o;           // same frame as the last slice: step nothing, wait for the next
                    run.lastFrame = f;
                    o.newFrame = true;
                    var tm = Find.TickManager;
                    tm.CurTimeSpeed = TimeSpeed.Paused;
                    var fw = Stopwatch.StartNew();
                    try
                    {
                        while (o.ticks < left && fw.Elapsed.TotalMilliseconds < budget)
                        {
                            tm.DoSingleTick();
                            o.ticks++;
                            if (cond != null && !cond.Running) { o.ended = true; break; }      // ON the tick of the condition
                            if (!SceneSameGame(run)) { o.stop = "a tick changed the game or map"; break; }
                            string hh = halt();
                            if (hh != null) { o.stop = hh; break; }
                        }
                    }
                    catch (Exception e) { o.stop = "a tick threw " + SceneInner(e) + " after " + o.ticks + " ticks this frame"; }
                    return o;
                }, msLeft());
                if (got is SceneStop gs) { shortWhy = gs.why; break; }
                SceneSlice sl = got as SceneSlice;
                if (sl == null) { shortWhy = "a tick slice answered nothing"; break; }
                stepped += sl.ticks;                             // counted before the stop: ticks that ran stay in the evidence
                if (sl.newFrame) { frames++; sinceFrame.Restart(); }
                if (sl.stop != null) { shortWhy = sl.stop; break; }
                if (sl.ended) break;
                if (sl.newFrame && sl.ticks == 0) { shortWhy = "a frame stepped no tick"; break; }
                if (stepped < want)
                {
                    if (sinceFrame.ElapsedMilliseconds > SceneFrameStallMs) { shortWhy = "no new frame in " + SceneFrameStallMs + " ms (the game is not drawing)"; break; }
                    await Task.Delay(sl.newFrame ? 1 : 4).ConfigureAwait(false);
                }
            }
            long tickMs = sw.ElapsedMilliseconds;
            if (cond != null)
            {
                string why = shortWhy;
                // never the run's deadline: a run left armed would lock the game
                await ctx.MainThread.InvokeAsync<object>(() => { if (cond.Running) cond.Force("aborted", "the scene's ticks ended: " + (why ?? "all were stepped"), TicksGameSafe()); return null; });
                // danger: a game that stopped drawing closes nothing, and this call would never answer; the bound is the writer's drain
                // limit and the frame stall above. A run that is still open then closes by itself when frames come back.
                var settle = Stopwatch.StartNew();
                while (cond.Stage != "closed" && settle.ElapsedMilliseconds < JawaBenchSceneTickCore.DrainMs + SceneFrameStallMs) await Task.Delay(20).ConfigureAwait(false);
                if (cond.Stage != "closed" && shortWhy == null) shortWhy = "run " + cond.Id + " did not close (the game is not drawing, or its writer is stuck)";
                if (cond.State == "hit" || cond.State == "done") want = stepped;                 // the condition ended the scene: no tick is owed
                else if (shortWhy == null) shortWhy = "the condition run ended as " + cond.State + (cond.Why == null ? "" : ": " + cond.Why);
            }
            sw.Restart();
            object judgedAnswer = await SceneDispatch(ctx, () =>
            {
                var o = new List<SR.Row>();
                string h = halt();
                if (h != null) { o.Add(SR.Unmeasured_(spec.name, "VERDICT", "not judged: " + h)); return o; }
                bool same = SceneSameGame(run);
                if (!string.IsNullOrWhiteSpace(spec.outside))
                    foreach (SR.OutsideCheck c in SR.ParseOutside(spec.outside, out _))
                        o.Add(same ? SceneOutsideRow(run.map, spec.name, c, ox, oz) : SR.OutsideRow(spec.name, c, -1, Changed));
                if (!same) { o.Add(SR.Unmeasured_(spec.name, "VERDICT", Changed)); return o; }
                List<SR.Row> judged;
                try { judged = SR.Normalize(spec.name, judge.DynamicInvoke()); }
                catch (Exception e) { judged = new List<SR.Row> { SR.Unmeasured_(spec.name, "VERDICT", "the judge threw " + SceneInner(e)) }; }
                if (!SceneSameGame(run)) judged = new List<SR.Row> { SR.Unmeasured_(spec.name, "VERDICT", "the judge changed the game or map; its answer is not kept") };
                o.AddRange(judged);
                return o;
            }, Math.Max(msLeft(), 1000));                        // the judge of a scene that ticked gets at least a second
            var sceneRows = judgedAnswer is SceneStop js
                ? new List<SR.Row> { SR.Unmeasured_(spec.name, "VERDICT", "not judged: " + js.why) }
                : judgedAnswer as List<SR.Row>;
            long judgeMs = sw.ElapsedMilliseconds;
            int wanted = want;
            rows.AddRange(SR.ShortAdvance(sceneRows ?? new List<SR.Row> { SR.Unmeasured_(spec.name, "VERDICT", "no rows came back") }, stepped, want, shortWhy));
            sceneInfo.Add(new { scene = spec.name, origin = ox + "," + oz, ticksWanted = wanted, ticksStepped = stepped, frames, stageMs, tickMs, judgeMs,
                untilRun = cond?.Id, untilState = cond?.State, untilHitTick = cond?.HitTick });
        }

        private sealed class SceneStop
        {
            public readonly string why;
            public SceneStop(string why) { this.why = why; }
        }

        private static bool SceneSameGame(SceneRunState r) =>
            Current.Game == r.game && Find.CurrentMap == r.map && Find.Maps.Contains(r.map);

        private static string SceneInner(Exception e)
        {
            Exception x = e is TargetInvocationException && e.InnerException != null ? e.InnerException : e;
            return x.GetType().Name + ": " + SR.Clip(x.Message, 300);
        }

        /// <summary>A vanilla count over the WHOLE rect at origin + (dx, dz): never the mod's own state, never a clipped rect
        /// (an off-map rect, or a throw, is UNMEASURED with its cause).</summary>
        private static SR.Row SceneOutsideRow(Map map, string scene, SR.OutsideCheck c, int ox, int oz)
        {
            int[] r = SR.RectOnMap(c, ox, oz, map.Size.x, map.Size.z);
            if (r == null) return SR.OutsideRow(scene, c, -1, "the rect at origin " + ox + "," + oz + " is not wholly on the " + map.Size.x + "x" + map.Size.z + " map");
            try
            {
                int n = 0;
                foreach (IntVec3 cell in new CellRect(r[0], r[1], r[2], r[3]))
                    foreach (Thing t in cell.GetThingList(map))
                    {
                        if (c.kind == "haulables" ? t.def.EverHaulable : c.kind == "pawns" ? t is Pawn : t is Pawn p && p.IsColonist) n++;
                    }
                return SR.OutsideRow(scene, c, n);
            }
            catch (Exception e)
            {
                return SR.OutsideRow(scene, c, -1, "the read threw " + SceneInner(e));
            }
        }

        private static object SceneResult(bool completed, List<SR.Row> rows, List<object> scenes, string begin, List<string> problems, Stopwatch wall) =>
            new
            {
                success = completed, overall = SR.Overall(rows), rows = SRL.Dicts(rows), scenes,
                suiteBegin = begin, problems, wallS = Math.Round(wall.Elapsed.TotalSeconds, 2), ticksGame = TicksGameSafe(),
            };
    }

    /// <summary>The run's LINQ, kept OUT of the partial JawaBenchTerrainTools: a non-capturing lambda there lands in the
    /// partial class's shared closure class, which fails to load when an optional mod's types (GSS) are absent.</summary>
    internal static class SRL
    {
        internal static List<string> Names(List<SR.Spec> specs) => specs.Select(s => s.name).ToList();

        internal static long TotalTicks(List<SR.Spec> specs, int tickOverride) => specs.Sum(s => (long)SR.TicksFor(s, tickOverride));

        internal static List<string> TooLong(List<SR.Spec> specs, int tickOverride) =>
            specs.Where(s => SR.TicksFor(s, tickOverride) > SR.MaxSceneTicks).Select(s => s.name).ToList();

        internal static List<Dictionary<string, object>> Dicts(List<SR.Row> rows) => rows.Select(r => r.ToDict()).ToList();

        private static string Inner(Exception e)
        {
            Exception x = e is TargetInvocationException && e.InnerException != null ? e.InnerException : e;
            return x.GetType().Name + ": " + SR.Clip(x.Message, 300);
        }

        /// <summary>The optional public static string Name(string) hook; null when absent. A hook of that name with another
        /// shape, or overloads that cannot be told apart, is a problem (the run is refused), never silently skipped.</summary>
        internal static MethodInfo Hook(Type t, string name, List<string> problems)
        {
            try
            {
                var all = t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance | BindingFlags.DeclaredOnly)
                    .Where(m => m.Name == name).ToList();
                if (all.Count == 0) return null;
                MethodInfo ok = all.FirstOrDefault(m => m.IsPublic && m.IsStatic && m.ReturnType == typeof(string)
                    && m.GetParameters().Length == 1 && m.GetParameters()[0].ParameterType == typeof(string));
                if (ok == null || all.Count > 1) problems.Add(name + ": a suite hook must be the one public static string " + name + "(string)");
                return ok;
            }
            catch (Exception e)
            {
                problems.Add(name + ": hook lookup threw " + Inner(e));
                return null;
            }
        }
    }
}
