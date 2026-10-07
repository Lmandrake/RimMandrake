// JawaBenchFlowWorksPlaytest.cs - FlowWorks in-game scenario runner, "Approach A" pilot (2026-10-06).
//
// WHY: design/RimMandrake/flowworks_playtest_automation_2026-10-06.md - move the playtest INTO the running
// game. One bridge call starts a run; C# owns execution; Python stops building experiments out of
// hundreds of RPCs. Design note: design/RimMandrake/flowworks_playtest_runner_A.md.
//
// SHAPE: a static controller (nothing is a MapComponent/GameComponent, nothing reaches a save) plus a
// hidden MonoBehaviour whose Update() advances the current scenario once per Unity frame. A scenario is
// a C# iterator that yields waits ("N ticks", "until predicate or timeout"), so no bridge call ever
// blocks. Each scenario result is appended to a JSONL journal the moment it completes; the journal's
// last line is run_end. No run_end, or run_end completed=false, reads INCOMPLETE - never green.
//
// TICKS: tickMode "speed" = game unpaused at TimeSpeed.Ultrafast (vanilla ticks); "batch" = game paused
// and the driver calls TickManager.DoSingleTick() (the dev step-one-tick entry point) inside a per-frame
// wall budget, checking the wait predicate after every tick. Both report achieved ticks/sec.
//
// EVIDENCE vs SETUP: terrain writes, Deepen() for the pit, direct pawn/ladder spawns build FIXTURES
// only. Evidence routes are production paths: RM_LiquidStock.BodyAt (the classifier), the player's
// designators + an undrafted colonist's own think tree (no forced job, no instant dig), and the trap's
// own Harmony seams acting on ordinary Goto jobs.
//
// COUPLING: FlowWorks strictly by reflection (the companion must load without FlowWorks). Every
// resolve failure becomes an INVALID scenario naming what was missing.
//
// THREAD AFFINITY: the tools hop to the main thread; the driver runs in Update(), which is the main thread.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    /// <summary>Per-frame pump for the playtest runner. Top-level so Unity's AddComponent sees a plain type.</summary>
    internal sealed class JawaBenchPlaytestDriver : MonoBehaviour
    {
        private void Update()
        {
            JawaBenchTerrainTools.PlaytestFrame();
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        // ════════════════════════════════════════════════════════════════
        // the three tools
        // ════════════════════════════════════════════════════════════════

        [Tool(
            "jawa/playtest_start",
            Description =
                "FlowWorks in-game scenario runner (Approach A). Starts a run on the CURRENT map and " +
                "returns its run id AT ONCE; the run then advances across ordinary game frames (never inside " +
                "this call). recipe = comma list of scenes: fluids, dig, pit, depth_fill, fire, pump, river, sluice, " +
                "pit_ladder_release, pit_fall_forced, pit_ladder_toggle, pit_ladder_haul, pit_ladder_raised_hold, " +
                "save_reload (arms: SAVES the game, record PENDING), save_reload_b (needs resume=<runId>, after loading " +
                "that save); pilot = fluids,dig,pit; full = every scene, save_reload last. inject appends a " +
                "scenario that throws, proving the INCOMPLETE path. tickMode batch (default) PAUSES the game " +
                "and steps ticks itself within frameBudgetMs per frame; speed unpauses at Ultrafast. The run " +
                "MODIFIES THE MAP (water/tar strips, a dug cell, a SUPERDEEP pit, a ladder, two spawned and " +
                "removed pawns): scratch maps only. Refuses while another run is active unless force=true. " +
                "Poll with playtest_status, then playtest_collect.",
            ResultDescription = "success, runId, journalPath, scenarios[], tickMode, frameBudgetMs, driver, ticksGame.")]
        public static async Task<object> PlaytestStart(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma list of scenes (see description); pilot = fluids,dig,pit; full = all.", DefaultValue = "pilot")]
            string recipe = "pilot",
            [ToolParameter(Description = "Seed for pawn generation and fixture-search jitter.", DefaultValue = 1)]
            int seed = 1,
            [ToolParameter(Description = "batch (pause + DoSingleTick in a per-frame budget) or speed (Ultrafast).", DefaultValue = "batch")]
            string tickMode = "batch",
            [ToolParameter(Description = "batch mode: wall milliseconds of ticking per Unity frame (5-500).", DefaultValue = 50)]
            int frameBudgetMs = 50,
            [ToolParameter(Description = "Abort an active run and start anyway.", DefaultValue = false)]
            bool force = false,
            [ToolParameter(Description = "save_reload_b only: the runId of the save_reload run whose checkpoint (and save) this run continues.")]
            string resume = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (ResolveExcavationComponent(map, out Type _, out string err) == null) return Fail(err);
                if (pRun != null && pRun.state == "running")
                {
                    if (!force) return Fail("A playtest run is active: " + pRun.id + ". Pass force=true to abort it.");
                    pRun.Abort("aborted by a new playtest_start force=true");
                }
                string mode = (tickMode ?? "batch").Trim().ToLowerInvariant();
                if (mode != "batch" && mode != "speed") return Fail("tickMode must be batch or speed.");
                List<string> names = PlaytestParseRecipe(recipe, out string bad);
                if (bad != null) return Fail("Unknown scenario '" + bad + "'. Known: " + string.Join(", ", PlaytestKnown) + "; recipes pilot, full.");
                if (names.Contains("save_reload_b") && string.IsNullOrEmpty(resume)) return Fail("save_reload_b needs resume=<runId of the save_reload run>.");
                if (names.Count == 0) return Fail("Empty recipe.");

                string driver = PlaytestEnsureDriver(out string driverErr);
                if (driver == null) return Fail("Could not install the per-frame driver: " + driverErr);

                var run = new PlayRun(map, names, seed, mode, Mathf.Clamp(frameBudgetMs, 5, 500), recipe);
                run.driver = driver;
                run.resume = resume;
                pRun = run;
                pRuns[run.id] = run;
                run.Begin();
                return (object)new
                {
                    success = true,
                    runId = run.id,
                    journalPath = run.journalPath,
                    scenarios = names,
                    tickMode = mode,
                    frameBudgetMs = run.frameBudgetMs,
                    driver,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/playtest_status",
            Description = "State of a playtest run (running/completed/aborted), current scenario and phase, ticks and " +
                          "wall so far, and the records written so far. Empty runId = the latest run.",
            ResultDescription = "success, runId, state, scenarioIndex, scenarioCount, current, phase, wallSec, ticks, " +
                                "frames, records[{name,status,reason,wallSec,ticks}], error, ticksGame.")]
        public static async Task<object> PlaytestStatus(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Run id from playtest_start; empty = latest.")] string runId = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                PlayRun run = PlaytestFind(runId);
                if (run == null) return Fail("No such playtest run: " + (runId ?? "(latest)"));
                return (object)run.StatusObject();
            });
        }

        [Tool(
            "jawa/playtest_collect",
            Description = "Report for a playtest run: the JSONL journal path and a verdict RE-DERIVED FROM THE FILE " +
                          "(INCOMPLETE unless its last line is run_end with completed=true and no scenario is PENDING; then FAIL if any scenario " +
                          "FAILed not marked expectedFailUntil, INVALID if any fixture was invalid, XFAIL if only expected FAILs, else PASS). Works on a still-running run (reads " +
                          "INCOMPLETE).",
            ResultDescription = "success, runId, reportPath, verdict, scenarioLines, hasRunEnd, state, summary, ticksGame.")]
        public static async Task<object> PlaytestCollect(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Run id from playtest_start; empty = latest.")] string runId = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                PlayRun run = PlaytestFind(runId);
                if (run == null) return Fail("No such playtest run: " + (runId ?? "(latest)"));
                string[] lines = File.Exists(run.journalPath) ? File.ReadAllLines(run.journalPath) : new string[0];
                int scen = lines.Count(l => l.Contains("\"type\":\"scenario\""));
                string last = lines.LastOrDefault(l => l.Trim().Length > 0) ?? "";
                bool hasEnd = last.Contains("\"type\":\"run_end\"");
                string verdict = PlaytestVerdict(lines);
                return (object)new
                {
                    success = true,
                    runId = run.id,
                    reportPath = run.journalPath,
                    verdict,
                    scenarioLines = scen,
                    hasRunEnd = hasEnd,
                    state = run.state,
                    summary = run.StatusObject(),
                    ticksGame = TicksGameSafe()
                };
            });
        }

        // ════════════════════════════════════════════════════════════════
        // controller
        // ════════════════════════════════════════════════════════════════

        private static PlayRun pRun;
        private static readonly Dictionary<string, PlayRun> pRuns = new Dictionary<string, PlayRun>();
        private static GameObject pDriverGo;
        private static bool pHarmonyDriver;

        private static PlayRun PlaytestFind(string runId)
        {
            if (string.IsNullOrEmpty(runId)) return pRun;
            return pRuns.TryGetValue(runId, out PlayRun r) ? r : null;
        }

        /// <summary>The fixed catalogue. "full" runs every scene except the resume half and inject; save_reload goes
        /// last because it saves the game and the launcher then loads that save for save_reload_b.</summary>
        private static readonly string[] PlaytestKnown =
            { "fluids", "dig", "pit", "depth_fill", "fire", "pump", "river", "sluice", "pit_ladder_release", "pit_fall_forced",
              "pit_ladder_toggle", "pit_ladder_haul", "pit_ladder_raised_hold", "save_reload", "save_reload_b", "inject" };
        private static readonly string[] PlaytestFull =
            { "fluids", "dig", "pit", "depth_fill", "fire", "pump", "river", "sluice", "pit_ladder_release", "pit_fall_forced",
              "pit_ladder_toggle", "pit_ladder_haul", "pit_ladder_raised_hold", "save_reload" };

        private static List<string> PlaytestParseRecipe(string recipe, out string bad)
        {
            bad = null;
            var outList = new List<string>();
            foreach (string raw in (recipe ?? "pilot").Split(','))
            {
                string s = raw.Trim().ToLowerInvariant();
                if (s.Length == 0) continue;
                if (s == "pilot") { outList.AddRange(new[] { "fluids", "dig", "pit" }); continue; }
                if (s == "full") { outList.AddRange(PlaytestFull); continue; }
                if (!PlaytestKnown.Contains(s)) { bad = s; return outList; }
                outList.Add(s);
            }
            return outList;
        }

        /// <summary>Verdict re-derived from the journal lines (playtest_runner.py's verdict() is the same rule):
        /// INCOMPLETE without run_end completed=true or with any status other than PASS/FAIL/INVALID (PENDING = a
        /// save_reload awaiting its resume half); FAIL if any FAIL not marked expectedFailUntil; INVALID if any
        /// INVALID; XFAIL if the only FAILs are expected ones; else PASS.</summary>
        internal static string PlaytestVerdict(string[] lines)
        {
            string last = lines.LastOrDefault(l => l.Trim().Length > 0) ?? "";
            if (!(last.Contains("\"type\":\"run_end\"") && last.Contains("\"completed\":true"))) return "INCOMPLETE";
            var scen = lines.Where(l => l.Contains("\"type\":\"scenario\"")).ToList();
            bool St(string l, string s) => l.Contains("\"status\":\"" + s + "\"");
            if (scen.Any(l => !St(l, "PASS") && !St(l, "FAIL") && !St(l, "INVALID"))) return "INCOMPLETE";
            bool expected(string l) => !l.Contains("\"expectedFailUntil\":null");
            if (scen.Any(l => St(l, "FAIL") && !expected(l))) return "FAIL";
            if (scen.Any(l => St(l, "INVALID"))) return "INVALID";
            if (scen.Any(l => St(l, "FAIL"))) return "XFAIL";
            return "PASS";
        }

        /// <summary>A hidden GameObject with JawaBenchPlaytestDriver; Harmony postfix on Root_Play.Update if Unity refuses.</summary>
        private static string PlaytestEnsureDriver(out string error)
        {
            error = null;
            if (pHarmonyDriver) return "harmony:Root_Play.Update";
            if (pDriverGo != null && pDriverGo.GetComponent<JawaBenchPlaytestDriver>() != null) return "monobehaviour";
            try
            {
                pDriverGo = new GameObject("JawaBench.PlaytestDriver");
                UnityEngine.Object.DontDestroyOnLoad(pDriverGo);
                if (pDriverGo.AddComponent<JawaBenchPlaytestDriver>() != null) return "monobehaviour";
                error = "AddComponent returned null";
            }
            catch (Exception e) { error = "AddComponent threw " + e.GetType().Name + ": " + e.Message; }
            try
            {
                var h = new HarmonyLib.Harmony("jawabench.playtest.driver");
                MethodInfo target = AccessTools2.Method(typeof(Root_Play), "Update");
                if (target == null) { error += "; Root_Play.Update not found"; return null; }
                h.Patch(target, postfix: new HarmonyLib.HarmonyMethod(typeof(JawaBenchTerrainTools), nameof(PlaytestRootPostfix)));
                pHarmonyDriver = true;
                return "harmony:Root_Play.Update";
            }
            catch (Exception e) { error += "; Harmony fallback threw " + e.Message; return null; }
        }

        private static class AccessTools2
        {
            public static MethodInfo Method(Type t, string name) =>
                t.GetMethod(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
        }

        private static void PlaytestRootPostfix() => PlaytestFrame();

        private static int pLastFrame = -1;

        /// <summary>Called once per Unity frame by the driver.</summary>
        internal static void PlaytestFrame()
        {
            if (Time.frameCount == pLastFrame) return; // both drivers installed: step once
            pLastFrame = Time.frameCount;
            PlayRun run = pRun;
            if (run == null || run.state != "running") return;
            try { run.Frame(); }
            catch (Exception e) { run.Abort("runner exception: " + e); }
        }

        // ════════════════════════════════════════════════════════════════
        // timing
        // ════════════════════════════════════════════════════════════════

        internal sealed class PhaseAcc
        {
            public double wall; public int ticks; public int frames;
            public void Add(double w, int t, int f) { wall += w; ticks += t; frames += f; }
            public Dictionary<string, object> ToDict() => PD("wallSec", Math.Round(wall, 3), "ticks", ticks, "frames", frames);
        }

        /// <summary>Wall/tick/frame accounting by named phase; switching phase books the elapsed span to the old one.</summary>
        internal sealed class PhaseClock
        {
            private readonly Stopwatch sw = Stopwatch.StartNew();
            private double markWall; private int markTick; private int markFrame;
            public string phase;
            public readonly Dictionary<string, PhaseAcc> acc = new Dictionary<string, PhaseAcc>();
            public PhaseClock(string first) { phase = first; Mark(); }
            private void Mark() { markWall = sw.Elapsed.TotalSeconds; markTick = TicksGameSafe(); markFrame = Time.frameCount; }
            public void Book()
            {
                if (!acc.TryGetValue(phase, out PhaseAcc a)) acc[phase] = a = new PhaseAcc();
                a.Add(sw.Elapsed.TotalSeconds - markWall, TicksGameSafe() - markTick, Time.frameCount - markFrame);
                Mark();
            }
            public void Switch(string next) { Book(); phase = next; }
            public double Wall => sw.Elapsed.TotalSeconds;
            public Dictionary<string, object> Phases()
            {
                var d = new Dictionary<string, object>();
                foreach (var kv in acc) d[kv.Key] = kv.Value.ToDict();
                return d;
            }
        }

        // ════════════════════════════════════════════════════════════════
        // waits
        // ════════════════════════════════════════════════════════════════

        internal sealed class PWait
        {
            public int ticks;               // fixed wait, or timeout when until != null
            public Func<bool> until;        // null = fixed tick wait
            public Action perTick;          // observer, called after each tick (batch) / frame (speed)
            public int startTick;
            public bool timedOut;
            public bool satisfied;
            public int Elapsed => TicksGameSafe() - startTick;
            public bool Done()
            {
                if (until != null && until()) { satisfied = true; return true; }
                if (Elapsed >= ticks) { timedOut = until != null; satisfied = until == null; return true; }
                return false;
            }
        }

        private static PWait PTicks(int n, Action perTick = null) => new PWait { ticks = n, perTick = perTick };
        private static PWait PUntil(Func<bool> pred, int timeout, Action perTick = null) =>
            new PWait { ticks = timeout, until = pred, perTick = perTick };

        // ════════════════════════════════════════════════════════════════
        // one scenario's context
        // ════════════════════════════════════════════════════════════════

        internal sealed class PCtx
        {
            public PlayRun run;
            public string name;
            public Map map;
            public Type excType;
            public object exc;
            public PhaseClock clock = new PhaseClock("setup");
            public string status;          // PASS / FAIL / INVALID / ERROR / PENDING (save_reload awaiting its resume)
            public string expectedFailUntil; // item id whose build is expected to turn a FAIL green; null = none
            public string reason;
            public readonly Dictionary<string, object> ev = new Dictionary<string, object>();
            public double waitWall; public int waitTicks; public int waitFrames;
            public void Phase(string p) => clock.Switch(p);
            public void Pass(string why = null) { status = "PASS"; reason = why; }
            public void Defect(string why) { status = "FAIL"; reason = why; }
            public void Invalid(string why) { status = "INVALID"; reason = why; }

            // reflection onto the excavation component
            public object Call(string method, params object[] args)
            {
                MethodInfo m = excType.GetMethod(method, args.Select(a => a.GetType()).ToArray());
                if (m == null) throw new MissingMethodException(excType.Name, method);
                return m.Invoke(exc, args);
            }
            public int Depth(IntVec3 c) => (byte)Call("DepthAt", c);
            public bool IsSource(IntVec3 c) => (bool)Call("IsSourceCell", c);
            public bool IsExcavated(IntVec3 c) => (bool)Call("IsExcavated", c);
            public bool IsSuperdeep(IntVec3 c) => (bool)Call("IsSuperdeepExcavation", c);
        }

        // ════════════════════════════════════════════════════════════════
        // the run
        // ════════════════════════════════════════════════════════════════

        internal sealed class PlayRun
        {
            public readonly string id;
            public readonly Map map;
            public readonly List<string> names;
            public readonly int seed;
            public readonly string tickMode;
            public readonly int frameBudgetMs;
            public readonly string recipe;
            public readonly string journalPath;
            public string driver;
            public string resume;
            public string state = "running";
            public string error;
            public int index = -1;
            public PCtx cur;
            private IEnumerator<PWait> it;
            private PWait wait;
            private PhaseClock runClock;
            private TimeSpeed prevSpeed;
            private int startTick, startFrame;
            private int lastSpeedTick;
            private double waitWallStart; private int waitTickStart; private int waitFrameStart;
            public readonly List<Dictionary<string, object>> records = new List<Dictionary<string, object>>();
            private const double MaxRunWallSec = 1200;

            public PlayRun(Map map, List<string> names, int seed, string tickMode, int frameBudgetMs, string recipe)
            {
                this.map = map; this.names = names; this.seed = seed; this.tickMode = tickMode;
                this.frameBudgetMs = frameBudgetMs; this.recipe = recipe;
                id = "fwpt_" + DateTime.UtcNow.ToString("yyyyMMddTHHmmss", CultureInfo.InvariantCulture) + "_s" + seed;
                string dir = Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench", "playtest");
                Directory.CreateDirectory(dir);
                journalPath = Path.Combine(dir, id + ".jsonl");
            }

            public void Begin()
            {
                runClock = new PhaseClock("runner");
                startTick = TicksGameSafe(); startFrame = Time.frameCount;
                prevSpeed = Find.TickManager.CurTimeSpeed;
                Find.TickManager.CurTimeSpeed = tickMode == "speed" ? TimeSpeed.Ultrafast : TimeSpeed.Paused;
                lastSpeedTick = TicksGameSafe();
                Type excT = GenTypes.GetTypeInAnyAssembly(ExcavationTypeName);
                Write(PD("type", "run_start", "runId", id, "recipe", recipe, "scenarios", names, "seed", seed,
                    "tickMode", tickMode, "frameBudgetMs", frameBudgetMs, "driver", driver, "resume", resume,
                    "mapId", map.uniqueID, "mapSize", map.Size.x + "x" + map.Size.z, "ticksGame", startTick,
                    "utc", DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture),
                    "flowWorks", excT != null ? (object)AssemblyIdentity(excT.Assembly) : null,
                    "companion", AssemblyIdentity(typeof(JawaBenchTerrainTools).Assembly),
                    "settings", SettingsSnapshot()));
            }

            private static Dictionary<string, object> SettingsSnapshot()
            {
                var d = new Dictionary<string, object>();
                Type s = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings");
                if (s == null) return d;
                foreach (string f in new[] { "superdeepCaptureEnabled", "superdeepCapturesOwnFaction", "ladderRequiredToExitEnabled",
                                             "ladderPrisonDoorEnabled", "digToDepthEnabled", "fillInEnabled", "sourceBudgetEnabled" })
                    d[f] = s.GetField(f, BindingFlags.Static | BindingFlags.Public)?.GetValue(null);
                return d;
            }

            private int settledFrames;

            private static bool GameSettled()
            {
                return Current.ProgramState == ProgramState.Playing && Current.Game != null && Find.TickManager != null
                    && Find.CurrentMap != null && !LongEventHandler.AnyEventNowOrWaiting;
            }

            public void Frame()
            {
                if (Current.Game == null || Find.CurrentMap != map || !Find.Maps.Contains(map)) { Abort("map changed or game ended mid-run"); return; }
                // A just-loaded game is not tickable until the long event that loaded it has finished and a few frames
                // have run (live 2026-10-07: DoSingleTick right after load_game_ready threw NRE in TickList.BucketOf).
                if (!GameSettled()) { settledFrames = 0; return; }
                if (settledFrames < 3) { settledFrames++; return; }
                if (runClock.Wall > MaxRunWallSec) { Abort("run exceeded " + MaxRunWallSec + " s wall"); return; }
                if (tickMode == "speed" && Find.TickManager.CurTimeSpeed != TimeSpeed.Ultrafast) Find.TickManager.CurTimeSpeed = TimeSpeed.Ultrafast;
                if (tickMode == "batch" && Find.TickManager.CurTimeSpeed != TimeSpeed.Paused) Find.TickManager.CurTimeSpeed = TimeSpeed.Paused;
                var budget = Stopwatch.StartNew();
                while (state == "running")
                {
                    if (cur == null)
                    {
                        if (!StartNext()) { Finish(); return; }
                    }
                    if (wait != null)
                    {
                        if (tickMode == "batch")
                        {
                            while (!wait.Done())
                            {
                                if (budget.ElapsedMilliseconds >= frameBudgetMs) return;
                                Find.TickManager.DoSingleTick();
                                wait.perTick?.Invoke();
                            }
                        }
                        else
                        {
                            if (TicksGameSafe() != lastSpeedTick) { lastSpeedTick = TicksGameSafe(); wait.perTick?.Invoke(); }
                            if (!wait.Done()) return;
                        }
                        cur.waitWall += cur.clock.Wall - waitWallStart;
                        cur.waitTicks += TicksGameSafe() - waitTickStart;
                        cur.waitFrames += Time.frameCount - waitFrameStart;
                        wait = null;
                    }
                    bool more;
                    try { more = it.MoveNext(); }
                    catch (Exception e)
                    {
                        cur.status = "ERROR";
                        cur.reason = (e is TargetInvocationException tie && tie.InnerException != null ? tie.InnerException : e).ToString();
                        EndScenario();
                        Abort("scenario '" + names[index] + "' threw; run stopped");
                        return;
                    }
                    if (!more) { EndScenario(); if (budget.ElapsedMilliseconds >= frameBudgetMs) return; continue; }
                    wait = it.Current;
                    if (wait == null) return; // yield null = next frame
                    wait.startTick = TicksGameSafe();
                    waitWallStart = cur.clock.Wall; waitTickStart = TicksGameSafe(); waitFrameStart = Time.frameCount;
                }
            }

            private bool StartNext()
            {
                index++;
                if (index >= names.Count) return false;
                runClock.Switch("scenarios");
                cur = new PCtx { run = this, name = names[index], map = map };
                cur.exc = ResolveExcavationComponent(map, out cur.excType, out string err);
                if (cur.exc == null) { cur.Invalid(err); it = Enumerable.Empty<PWait>().GetEnumerator(); return true; }
                it = ScenarioFor(names[index], cur).GetEnumerator();
                return true;
            }

            private void EndScenario()
            {
                cur.clock.Book();
                if (cur.status == null) cur.Invalid("scenario ended without a verdict");
                double wall = cur.clock.acc.Values.Sum(a => a.wall);
                int ticks = cur.clock.acc.Values.Sum(a => a.ticks);
                int frames = cur.clock.acc.Values.Sum(a => a.frames);
                var rec = PD("type", "scenario", "runId", id, "index", index, "name", cur.name, "status", cur.status,
                    "reason", cur.reason, "expectedFailUntil", cur.expectedFailUntil, "evidence", cur.ev,
                    "timing", PD("wallSec", Math.Round(wall, 3), "ticks", ticks, "frames", frames,
                        "phases", cur.clock.Phases(),
                        "waitWallSec", Math.Round(cur.waitWall, 3), "waitTicks", cur.waitTicks, "waitFrames", cur.waitFrames,
                        "ticksPerSecDuringWaits", cur.waitWall > 0 ? Math.Round(cur.waitTicks / cur.waitWall, 1) : 0.0),
                    "ticksGame", TicksGameSafe());
                records.Add(rec);
                Write(rec);
                cur = null; it = null; wait = null;
            }

            private void Finish()
            {
                state = "completed";
                WriteEnd(true);
            }

            public void Abort(string why)
            {
                if (state != "running") return;
                error = why;
                state = "aborted";
                try { WriteEnd(false); } catch (Exception e) { Log.Warning("[JawaBench.playtest] could not write run_end: " + e.Message); }
            }

            private void WriteEnd(bool completed)
            {
                runClock.Book();
                try { if (Current.Game != null) Find.TickManager.CurTimeSpeed = prevSpeed; } catch { /* restoring speed is best effort; reported below */ }
                // run-level phase split: sum each scenario's setup/exec/observe; runner = everything outside scenarios
                var split = new Dictionary<string, PhaseAcc>();
                foreach (var r in records)
                {
                    if (!(r["timing"] is Dictionary<string, object> t) || !(t["phases"] is Dictionary<string, object> ph)) continue;
                    foreach (var kv in ph)
                    {
                        var pd = (Dictionary<string, object>)kv.Value;
                        if (!split.TryGetValue(kv.Key, out PhaseAcc a)) split[kv.Key] = a = new PhaseAcc();
                        a.Add(Convert.ToDouble(pd["wallSec"]), Convert.ToInt32(pd["ticks"]), Convert.ToInt32(pd["frames"]));
                    }
                }
                double total = runClock.Wall;
                double inScen = records.Sum(r => Convert.ToDouble(((Dictionary<string, object>)r["timing"])["wallSec"]));
                double wW = records.Sum(r => Convert.ToDouble(((Dictionary<string, object>)r["timing"])["waitWallSec"]));
                int wT = records.Sum(r => Convert.ToInt32(((Dictionary<string, object>)r["timing"])["waitTicks"]));
                var phases = new Dictionary<string, object>();
                foreach (var kv in split) phases[kv.Key] = kv.Value.ToDict();
                phases["runner"] = PD("wallSec", Math.Round(Math.Max(0, total - inScen), 3));
                Write(PD("type", "run_end", "runId", id, "completed", completed, "state", state, "error", error,
                    "scenariosPlanned", names.Count, "scenariosRecorded", records.Count,
                    "statuses", records.Select(r => r["name"] + ":" + r["status"]).ToList(),
                    "timing", PD("wallSec", Math.Round(total, 3), "ticks", TicksGameSafe() - startTick,
                        "frames", Time.frameCount - startFrame, "phases", phases,
                        "waitWallSec", Math.Round(wW, 3), "waitTicks", wT,
                        "ticksPerSecDuringWaits", wW > 0 ? Math.Round(wT / wW, 1) : 0.0,
                        "tickMode", tickMode, "frameBudgetMs", frameBudgetMs,
                        "timeSpeedDuringRun", tickMode == "speed" ? "Ultrafast" : "Paused+DoSingleTick",
                        "tickRateMultiplierUltrafast", UltrafastMultiplier(),
                        "speedRestoredTo", prevSpeed.ToString()),
                    "ticksGame", TicksGameSafe()));
            }

            private static object UltrafastMultiplier()
            {
                try
                {
                    TickManager tm = Find.TickManager;
                    TimeSpeed was = tm.CurTimeSpeed;
                    tm.CurTimeSpeed = TimeSpeed.Ultrafast;
                    float m = tm.TickRateMultiplier;
                    tm.CurTimeSpeed = was;
                    return m;
                }
                catch (Exception e) { return "unreadable: " + e.Message; }
            }

            private void Write(Dictionary<string, object> rec)
            {
                var sb = new StringBuilder();
                PJson(sb, rec);
                sb.Append('\n');
                File.AppendAllText(journalPath, sb.ToString());
            }

            public Dictionary<string, object> StatusObject() => PD(
                "success", true, "runId", id, "state", state, "error", error, "journalPath", journalPath,
                "scenarioIndex", index, "scenarioCount", names.Count,
                "current", cur?.name, "phase", cur?.clock.phase,
                "wallSec", runClock != null ? Math.Round(runClock.Wall, 2) : 0.0,
                "ticks", TicksGameSafe() - startTick, "frames", Time.frameCount - startFrame,
                "tickMode", tickMode, "driver", driver,
                "records", records.Select(r => (object)PD("name", r["name"], "status", r["status"], "reason", r["reason"],
                    "expectedFailUntil", r["expectedFailUntil"],
                    "wallSec", ((Dictionary<string, object>)r["timing"])["wallSec"],
                    "ticks", ((Dictionary<string, object>)r["timing"])["ticks"])).ToList(),
                "ticksGame", TicksGameSafe());
        }

        private static IEnumerable<PWait> ScenarioFor(string name, PCtx c)
        {
            switch (name)
            {
                case "fluids": return ScnFluids(c);
                case "dig": return ScnDigFill(c);
                case "pit": return ScnPit(c);
                case "inject": return ScnInject(c);
                case "depth_fill": return ScnDepthFill(c);
                case "fire": return ScnFire(c);
                case "pump": return ScnPump(c);
                case "river": return ScnRiver(c);
                case "sluice": return ScnSluice(c);
                case "pit_ladder_release": return ScnPitLadderRelease(c);
                case "pit_fall_forced": return ScnPitFallForced(c);
                case "pit_ladder_toggle": return ScnPitLadderToggle(c);
                case "pit_ladder_haul": return ScnPitLadderHaul(c);
                case "pit_ladder_raised_hold": return ScnPitLadderRaisedHold(c);
                case "save_reload": return ScnSaveReloadA(c);
                case "save_reload_b": return ScnSaveReloadB(c);
                default: throw new ArgumentException("unknown scenario " + name);
            }
        }

        // ════════════════════════════════════════════════════════════════
        // fixtures
        // ════════════════════════════════════════════════════════════════

        /// <summary>Clean ground: in bounds, ≥10 from the edge, unfogged, no edifice/pawn/designation, dry
        /// natural terrain never excavated, standable.</summary>
        private static bool PCellClean(PCtx c, IntVec3 x, bool needSoil)
        {
            Map m = c.map;
            if (!x.InBounds(m) || x.x < 10 || x.z < 10 || x.x >= m.Size.x - 10 || x.z >= m.Size.z - 10) return false;
            if (x.Fogged(m) || x.GetEdifice(m) != null || x.GetFirstPawn(m) != null) return false;
            TerrainDef top = m.terrainGrid.TopTerrainAt(x);
            TerrainDef bas = m.terrainGrid.BaseTerrainAt(x);
            if (top == null || top.IsWater || (bas != null && bas.IsWater)) return false;
            if (m.terrainGrid.FoundationAt(x) != null) return false;
            if (needSoil && !top.IsSoil) return false;
            if (c.IsExcavated(x)) return false;
            if (m.designationManager.AllDesignationsAt(x).Count > 0) return false;
            if (x.GetThingList(m).Any(t => !(t is Plant) && t.def.category != ThingCategory.Filth)) return false;
            return x.Standable(m);
        }

        /// <summary>Margin ring: no water, no excavation (so nothing else can join the fixture).</summary>
        private static bool PCellQuiet(PCtx c, IntVec3 x)
        {
            Map m = c.map;
            if (!x.InBounds(m)) return false;
            TerrainDef bas = m.terrainGrid.BaseTerrainAt(x);
            if (bas != null && bas.IsWater) return false;
            TerrainDef top = m.terrainGrid.TopTerrainAt(x);
            if (top != null && top.IsWater) return false;
            return !c.IsExcavated(x);
        }

        /// <summary>First w×h rect (plus margin) of clean cells, origins scanned by distance from 'near'
        /// with a seed jitter. 'extra' may demand more of the rect.</summary>
        private static bool PFindRect(PCtx c, IntVec3 near, int w, int h, int margin, bool needSoil,
            out CellRect rect, Func<CellRect, bool> extra = null)
        {
            Map m = c.map;
            var rng = new System.Random(c.run.seed * 7919 + w * 31 + h);
            var origins = new List<IntVec3>();
            for (int x = 10; x < m.Size.x - 10 - w; x += 2)
                for (int z = 10; z < m.Size.z - 10 - h; z += 2)
                    origins.Add(new IntVec3(x, 0, z));
            var keyed = origins.Select(o => new { o, k = (o - near).LengthHorizontalSquared + rng.Next(0, 64) }).OrderBy(a => a.k);
            foreach (var a in keyed)
            {
                var r = new CellRect(a.o.x, a.o.z, w, h);
                bool ok = true;
                foreach (IntVec3 x in r.Cells) { if (!PCellClean(c, x, needSoil)) { ok = false; break; } }
                if (!ok) continue;
                foreach (IntVec3 x in r.ExpandedBy(margin)) { if (!PCellQuiet(c, x)) { ok = false; break; } }
                if (!ok) continue;
                if (extra != null && !extra(r)) continue;
                rect = r;
                return true;
            }
            rect = default(CellRect);
            return false;
        }

        private static void PClearPlants(Map m, IEnumerable<IntVec3> cells)
        {
            foreach (IntVec3 x in cells)
                foreach (Thing t in x.GetThingList(m).ToList())
                    if (t is Plant || t.def.category == ThingCategory.Filth || t.def.category == ThingCategory.Item)
                        t.Destroy(DestroyMode.Vanish);
        }

        private static object PCell(IntVec3 x) => PD("x", x.x, "z", x.z);

        // ════════════════════════════════════════════════════════════════
        // scenario 1: touching natural water and tar (source finding RM_LiquidStock.cs:157,168)
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnFluids(PCtx c)
        {
            c.ev["route"] = "RM_LiquidStock.BodyAt (production classifier, first contact) on a fixture of water beside tar";
            TerrainDef water = TerrainDefOf.WaterShallow;
            TerrainDef tar = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_TarShallow");
            Type ident = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.RM_FluidIdentity");
            MethodInfo fluidOf = ident?.GetMethod("FluidOfTerrain", BindingFlags.Static | BindingFlags.Public);
            object stock = c.excType.GetProperty("Stock")?.GetValue(c.exc);
            MethodInfo bodyAt = stock?.GetType().GetMethod("BodyAt");
            if (tar == null || fluidOf == null || stock == null || bodyAt == null)
            {
                c.Invalid("missing: " + (tar == null ? "RM_TarShallow " : "") + (fluidOf == null ? "RM_FluidIdentity.FluidOfTerrain " : "")
                          + (stock == null ? "Excavation.Stock " : "") + (bodyAt == null ? "RM_LiquidStock.BodyAt" : ""));
                yield break;
            }
            string fW = (fluidOf.Invoke(null, new object[] { water }) as Def)?.defName;
            string fT = (fluidOf.Invoke(null, new object[] { tar }) as Def)?.defName;
            c.ev["fluidOfWaterTerrain"] = fW;
            c.ev["fluidOfTarTerrain"] = fT;
            if (fW == null || fT == null || fW == fT) { c.Invalid("fixture fluids are not distinct: " + fW + " / " + fT); yield break; }

            // two independent fixtures: water seeded first, then tar seeded first (the body takes the SEED's fluid)
            var cases = new List<Dictionary<string, object>>();
            bool allSeparate = true;
            IntVec3 near = c.map.Center;
            foreach (bool waterFirst in new[] { true, false })
            {
                c.Phase("setup");
                if (!PFindRect(c, near, 2, 3, 3, false, out CellRect r))
                {
                    c.Invalid("no clean 2x3 fixture with a 3-cell dry margin on this map");
                    yield break;
                }
                PClearPlants(c.map, r.Cells);
                var wCells = new List<IntVec3>(); var tCells = new List<IntVec3>();
                foreach (IntVec3 x in r.Cells)
                {
                    bool isW = x.x == r.minX;
                    c.map.terrainGrid.SetTerrain(x, isW ? water : tar);
                    (isW ? wCells : tCells).Add(x);
                }
                bool srcOk = wCells.All(c.IsSource) && tCells.All(c.IsSource);
                if (!srcOk) { c.Invalid("fixture cells did not read as IsSourceCell after the terrain write"); yield break; }
                near = r.CenterCell + new IntVec3(12, 0, 0);
                // No tick between fixture and classifier: a pulse could classify first and the seed order
                // (which decides the merged body's fluid) would no longer be ours.

                c.Phase("exec");
                IntVec3 seed = waterFirst ? wCells[1] : tCells[1];
                IntVec3 other = waterFirst ? tCells[1] : wCells[1];
                object bSeed = bodyAt.Invoke(stock, new object[] { c.map, seed, c.exc });
                object bOther = bodyAt.Invoke(stock, new object[] { c.map, other, c.exc });

                c.Phase("observe");
                int Id(object b) => b == null ? -1 : (int)b.GetType().GetField("id").GetValue(b);
                string Fl(object b) => (b?.GetType().GetField("fluid")?.GetValue(b) as Def)?.defName;
                List<IntVec3> Cells(object b) => b?.GetType().GetField("cells")?.GetValue(b) as List<IntVec3> ?? new List<IntVec3>();
                bool separate = bSeed != null && bOther != null && Id(bSeed) != Id(bOther);
                bool seedFluidOk = Fl(bSeed) == (waterFirst ? fW : fT);
                bool otherFluidOk = Fl(bOther) == (waterFirst ? fT : fW);
                var seedCells = Cells(bSeed);
                int foreignInSeed = seedCells.Count(x => (waterFirst ? tCells : wCells).Contains(x));
                allSeparate &= separate && seedFluidOk && otherFluidOk;
                cases.Add(PD("seeded", waterFirst ? "water" : "tar", "rect", PD("x", r.minX, "z", r.minZ, "w", 2, "h", 3),
                    "seedBodyId", Id(bSeed), "otherBodyId", Id(bOther),
                    "seedBodyFluid", Fl(bSeed), "otherBodyFluid", Fl(bOther),
                    "seedBodyCells", seedCells.Count, "foreignCellsInSeedBody", foreignInSeed,
                    "separateBodies", separate, "fluidsCorrect", seedFluidOk && otherFluidOk));
            }
            c.ev["cases"] = cases;
            if (allSeparate) c.Pass("water and tar classified as separate bodies with their own fluids, both seed orders");
            else c.Defect("touching water and tar merged into one body carrying one fluid (expected two bodies, own fluids) - see cases");
        }

        // ════════════════════════════════════════════════════════════════
        // scenario 2: designate DigCanal -> undrafted colonist digs -> fill in restores terrain
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnDigFill(PCtx c)
        {
            c.ev["route"] = "Designator_DigCanal/Designator_FillInCanal (CanDesignateCell + DesignateSingleCell) -> colonist think tree -> JobDriver";
            Map m = c.map;
            Type tDig = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.Designator_DigCanal");
            Type tFill = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.Designator_FillInCanal");
            JobDef digJob = DefDatabase<JobDef>.GetNamedSilentFail("RM_DigCanalJob");
            JobDef fillJob = DefDatabase<JobDef>.GetNamedSilentFail("RM_FillInCanalJob");
            DesignationDef digDes = DefDatabase<DesignationDef>.GetNamedSilentFail("RM_DigCanal");
            DesignationDef fillDes = DefDatabase<DesignationDef>.GetNamedSilentFail("RM_FillInCanal");
            if (tDig == null || tFill == null || digJob == null || fillJob == null || digDes == null || fillDes == null)
            {
                c.Invalid("FlowWorks dig/fill designator, job or designation def not resolvable");
                yield break;
            }
            WorkTypeDef mining = WorkTypeDefOf.Mining;
            Pawn worker = m.mapPawns.FreeColonistsSpawned
                .Where(p => !p.Downed && !p.Drafted && !p.WorkTypeIsDisabled(mining) && p.workSettings != null
                            && p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) && !p.InMentalState)
                .OrderBy(p => p.thingIDNumber).FirstOrDefault();
            if (worker == null) { c.Invalid("no free, undrafted, mining-capable colonist on the map"); yield break; }

            int prevPriority = worker.workSettings.GetPriority(mining);
            try
            {
                worker.workSettings.SetPriority(mining, 1);
                c.ev["worker"] = PD("id", worker.ThingID, "name", worker.LabelShort, "miningPriorityBefore", prevPriority, "miningPriorityNow", 1);

                Designator dig = (Designator)Activator.CreateInstance(tDig);
                Designator fill = (Designator)Activator.CreateInstance(tFill);
                if (!PFindRect(c, worker.Position, 1, 1, 3, true, out CellRect r,
                        rr => m.reachability.CanReach(worker.Position, rr.CenterCell, PathEndMode.Touch, TraverseParms.For(worker))
                              && dig.CanDesignateCell(rr.CenterCell).Accepted))
                {
                    c.Invalid("no reachable, designatable soil cell with a dry margin near " + worker.LabelShort);
                    yield break;
                }
                IntVec3 cell = r.CenterCell;
                PClearPlants(m, new[] { cell });
                TerrainDef top0 = m.terrainGrid.TopTerrainAt(cell), fnd0 = m.terrainGrid.FoundationAt(cell), und0 = m.terrainGrid.UnderTerrainAt(cell);
                int d0 = c.Depth(cell);
                c.ev["cell"] = PCell(cell);
                c.ev["before"] = PD("top", top0?.defName, "foundation", fnd0?.defName, "under", und0?.defName, "depth", d0);

                // ── dig ──
                c.Phase("exec");
                AcceptanceReport ar = dig.CanDesignateCell(cell);
                if (!ar.Accepted) { c.Defect("Designator_DigCanal refused a clean soil cell: " + ar.Reason); yield break; }
                dig.DesignateSingleCell(cell);
                bool desPlaced = m.designationManager.DesignationAt(cell, digDes) != null;
                var digSeen = new JobWatch(m, digJob, cell);
                int t0 = TicksGameSafe();
                PWait w1 = PUntil(() => c.Depth(cell) > d0 && m.designationManager.DesignationAt(cell, digDes) == null, 30000, digSeen.Look);
                yield return w1;

                c.Phase("observe");
                int d1 = c.Depth(cell);
                c.ev["dig"] = PD("designationPlaced", desPlaced, "depthAfter", d1, "ticksToComplete", TicksGameSafe() - t0,
                    "timedOut", w1.timedOut, "job", digSeen.ToDict(),
                    "topAfterDig", m.terrainGrid.TopTerrainAt(cell)?.defName);
                if (w1.timedOut || d1 <= d0)
                {
                    c.Defect(digSeen.taker == null
                        ? "no colonist took the dig job within 30000 ticks (designation " + (desPlaced ? "placed" : "MISSING") + ")"
                        : "a colonist took the dig job but depth did not rise within 30000 ticks");
                    yield break;
                }
                if (digSeen.playerForced) { c.Defect("dig job was playerForced - not the autonomous route"); yield break; }

                // ── fill in ──
                c.Phase("exec");
                // the digger may still be standing on the cell ("Someone is down there"): let it walk off
                yield return PUntil(() => fill.CanDesignateCell(cell).Accepted, 600);
                AcceptanceReport fr = fill.CanDesignateCell(cell);
                if (!fr.Accepted) { c.Defect("Designator_FillInCanal refused the freshly dug cell: " + fr.Reason); yield break; }
                fill.DesignateSingleCell(cell);
                var fillSeen = new JobWatch(m, fillJob, cell);
                int t1 = TicksGameSafe();
                PWait w2 = PUntil(() => c.Depth(cell) == d0 && m.designationManager.DesignationAt(cell, fillDes) == null, 30000, fillSeen.Look);
                yield return w2;

                c.Phase("observe");
                TerrainDef top2 = m.terrainGrid.TopTerrainAt(cell), fnd2 = m.terrainGrid.FoundationAt(cell), und2 = m.terrainGrid.UnderTerrainAt(cell);
                bool restored = top2 == top0 && fnd2 == fnd0 && und2 == und0;
                c.ev["fill"] = PD("depthAfter", c.Depth(cell), "ticksToComplete", TicksGameSafe() - t1, "timedOut", w2.timedOut,
                    "job", fillSeen.ToDict(),
                    "after", PD("top", top2?.defName, "foundation", fnd2?.defName, "under", und2?.defName),
                    "terrainRestored", restored);
                if (w2.timedOut) c.Defect(fillSeen.taker == null ? "no colonist took the fill-in job within 30000 ticks" : "fill-in job taken but depth not restored within 30000 ticks");
                else if (fillSeen.playerForced) c.Defect("fill-in job was playerForced - not the autonomous route");
                else if (!restored) c.Defect("fill-in returned depth to " + d0 + " but terrain differs from the pre-dig snapshot");
                else c.Pass("designated dig taken and completed by " + digSeen.taker + ", fill-in by " + fillSeen.taker + "; original terrain restored");
            }
            finally
            {
                if (worker.workSettings != null) worker.workSettings.SetPriority(mining, prevPriority);
            }
        }

        /// <summary>Who first took a job of this def on this cell, observed tick by tick.</summary>
        internal sealed class JobWatch
        {
            private readonly Map map; private readonly JobDef def; private readonly IntVec3 cell;
            public string taker; public int tick = -1; public bool playerForced; public bool drafted; public int colonistsSeenWithJob;
            public JobWatch(Map map, JobDef def, IntVec3 cell) { this.map = map; this.def = def; this.cell = cell; }
            public void Look()
            {
                if (taker != null) return;
                foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
                {
                    Job j = p.CurJob;
                    if (j == null || j.def != def || j.targetA.Cell != cell) continue;
                    taker = p.LabelShort + " (" + p.ThingID + ")"; tick = TicksGameSafe(); playerForced = j.playerForced; drafted = p.Drafted;
                    colonistsSeenWithJob++;
                    return;
                }
            }
            public Dictionary<string, object> ToDict() => PD("taker", taker, "tickTaken", tick, "playerForced", playerForced, "takerDrafted", drafted);
        }

        // ════════════════════════════════════════════════════════════════
        // scenario 3: pit escape - hostile held with and without a ladder; friendly released by the ladder
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnPit(PCtx c)
        {
            c.ev["route"] = "Goto jobs through the real pather; trap = RM_SuperdeepTrap Harmony seams (path-follower floor + reachability veto); ladder = RM_LadderRules";
            Map m = c.map;
            Type trap = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.RM_SuperdeepTrap");
            MethodInfo isHeld = trap?.GetMethod("IsHeld", BindingFlags.Static | BindingFlags.Public);
            MethodInfo reqW = trap?.GetMethod("RequiredWidth", BindingFlags.Static | BindingFlags.Public);
            bool ruleOn = (bool?)trap?.GetProperty("RuleOn", BindingFlags.Static | BindingFlags.Public)?.GetValue(null) ?? false;
            ThingDef ladderDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Ladder");
            if (trap == null || isHeld == null || reqW == null || ladderDef == null) { c.Invalid("RM_SuperdeepTrap API or RM_Ladder def not resolvable"); yield break; }
            c.ev["ruleOn"] = ruleOn;
            if (!ruleOn) { c.Invalid("capture/ladder rule is switched off in mod settings"); yield break; }

            Faction enemy = Find.FactionManager.RandomEnemyFaction(allowHidden: false, allowDefeated: false, allowNonHumanlike: false);
            Faction friend = Find.FactionManager.RandomNonHostileFaction(allowHidden: false, allowDefeated: false, allowNonHumanlike: false);
            if (enemy == null || friend == null) { c.Invalid("world lacks a humanlike " + (enemy == null ? "enemy" : "non-hostile") + " faction"); yield break; }

            Pawn Gen(Faction f)
            {
                Rand.PushState(c.run.seed * 104729 + f.loadID);
                try
                {
                    Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(f.def.basicMemberKind ?? PawnKindDefOf.Villager, f, forceGenerateNewPawn: true));
                    p.equipment?.DestroyAllEquipment();
                    p.inventory?.DestroyAll();
                    return p;
                }
                finally { Rand.PopState(); }
            }

            Pawn hostile = Gen(enemy);
            int w = (int)reqW.Invoke(null, new object[] { hostile });
            int side = Math.Max(3, w + 1);
            if (!PFindRect(c, m.Center + new IntVec3(-25, 0, 20), side, side, 4, true, out CellRect pit,
                    rr => rr.ExpandedBy(4).Cells.Where(x => !rr.Contains(x)).All(x => x.Standable(m))))
            {
                hostile.Destroy(DestroyMode.Vanish);
                c.Invalid("no clean " + side + "x" + side + " pit site with a standable 4-cell ring");
                yield break;
            }
            PClearPlants(m, pit.Cells);
            foreach (IntVec3 x in pit.Cells)
                for (int i = 0; i < 6 && !c.IsSuperdeep(x); i++) c.Call("Deepen", x);
            if (!pit.Cells.All(c.IsSuperdeep)) { hostile.Destroy(DestroyMode.Vanish); c.Invalid("Deepen() did not bring every pit cell to SUPERDEEP"); yield break; }
            IntVec3 corner = new IntVec3(pit.minX, 0, pit.minZ);
            IntVec3 ladderCell = new IntVec3(pit.CenterCell.x, 0, pit.maxZ);
            IntVec3 dest = new IntVec3(pit.CenterCell.x, 0, pit.maxZ + 3);
            c.ev["pit"] = PD("x", pit.minX, "z", pit.minZ, "side", side, "requiredWidth", w);
            c.ev["dest"] = PCell(dest);
            c.ev["ladderCell"] = PCell(ladderCell);
            var phases = new List<Dictionary<string, object>>();
            c.ev["attempts"] = phases;

            // one escape attempt: ordinary Goto, re-issued if the pawn's own AI drops it; ends on exit or timeout
            bool heldAtStart = false;
            Pawn subject = null; bool left = false; int exitTick = -1; var visited = new HashSet<IntVec3>(); int reissues = 0;
            int lastOrder = 0;
            void Order()
            {
                lastOrder = TicksGameSafe();
                Job j = JobMaker.MakeJob(JobDefOf.Goto, dest);
                j.locomotionUrgency = LocomotionUrgency.Jog;
                subject.jobs.StartJob(j, JobCondition.InterruptForced);
            }
            void Watch()
            {
                if (subject == null || !subject.Spawned) return;
                visited.Add(subject.Position);
                if (!pit.Contains(subject.Position) && !left) { left = true; exitTick = TicksGameSafe(); }
                if (!left && TicksGameSafe() - lastOrder >= 120 && subject.CurJobDef != JobDefOf.Goto && !subject.Downed) { reissues++; Order(); }
            }
            Dictionary<string, object> Attempt(string label, bool ladder, int t0)
            {
                bool reach = m.reachability.CanReach(subject.Position, dest, PathEndMode.OnCell, TraverseParms.For(subject));
                return PD("attempt", label, "faction", subject.Faction?.Name, "hostile", subject.HostileTo(Faction.OfPlayer), "ladder", ladder,
                    "heldAtStart", heldAtStart, "canReachDestAfter", reach, "leftPit", left, "ticksToExit", left ? exitTick - t0 : -1,
                    "ticksObserved", TicksGameSafe() - t0, "cellsVisited", visited.Count,
                    "visitedOutsidePit", visited.Count(x => !pit.Contains(x)), "orderReissues", reissues,
                    "endPos", PCell(subject.Position), "downed", subject.Downed, "dead", subject.Dead, "job", subject.CurJobDef?.defName);
            }
            IEnumerable<PWait> Run(Pawn p, IntVec3 at, string label, bool ladder, int timeout, bool expectOut)
            {
                c.Phase("setup");
                subject = p; left = false; exitTick = -1; visited.Clear(); reissues = 0;
                if (!p.Spawned) GenSpawn.Spawn(p, at, m);
                heldAtStart = (bool)isHeld.Invoke(null, new object[] { p });
                c.Phase("exec");
                int t0 = TicksGameSafe();
                Order();
                if (expectOut) yield return PUntil(() => left, timeout, Watch);
                else yield return PTicks(timeout, Watch);
                c.Phase("observe");
                phases.Add(Attempt(label, ladder, t0));
            }

            Thing ladderThing = null;
            Pawn friendly = null;
            try
            {
                foreach (PWait x in Run(hostile, corner, "hostile_no_ladder", false, 600, false)) yield return x;
                hostile.Destroy(DestroyMode.Vanish);

                friendly = Gen(friend);
                foreach (PWait x in Run(friendly, corner, "friendly_no_ladder", false, 600, false)) yield return x;

                c.Phase("setup");
                ladderThing = ThingMaker.MakeThing(ladderDef, ladderDef.MadeFromStuff ? GenStuff.DefaultStuffFor(ladderDef) : null);
                ladderThing.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(ladderThing, ladderCell, m);
                foreach (PWait x in Run(friendly, friendly.Position, "friendly_with_ladder", true, 1500, true)) yield return x;
                if (friendly.Spawned) friendly.Destroy(DestroyMode.Vanish);

                Pawn hostile2 = Gen(enemy);
                foreach (PWait x in Run(hostile2, corner, "hostile_with_ladder", true, 600, false)) yield return x;
                if (hostile2.Spawned) hostile2.Destroy(DestroyMode.Vanish);
            }
            finally
            {
                if (friendly != null && friendly.Spawned) friendly.Destroy(DestroyMode.Vanish);
                if (subject != null && subject.Spawned) subject.Destroy(DestroyMode.Vanish);
            }

            bool Left(string label) => phases.Any(p => (string)p["attempt"] == label && (bool)p["leftPit"]);
            bool Ran(string label) => phases.Any(p => (string)p["attempt"] == label);
            bool Void(string label) => phases.Any(p => (string)p["attempt"] == label && ((bool)p["downed"] || (bool)p["dead"]));
            bool HeldAtStart(string label) => phases.Any(p => (string)p["attempt"] == label && (bool)p["heldAtStart"]);
            var voids = new[] { "hostile_no_ladder", "friendly_no_ladder", "hostile_with_ladder" }.Where(Void).ToList();
            if (voids.Count > 0) { c.Invalid("subject downed/dead during a must-stay attempt (turret? fight?): " + string.Join(", ", voids)); yield break; }
            var fails = new List<string>();
            if (!HeldAtStart("hostile_no_ladder")) fails.Add("trap predicate IsHeld=false for a hostile in a ladderless D4 pit");
            if (!Ran("hostile_with_ladder")) fails.Add("not all four attempts ran");
            if (Left("hostile_no_ladder")) fails.Add("hostile escaped a ladderless pit");
            if (Left("friendly_no_ladder")) fails.Add("friendly escaped a ladderless pit");
            if (!Left("friendly_with_ladder")) fails.Add("friendly did NOT get out by the lowered ladder within 1500 ticks");
            if (Left("hostile_with_ladder")) fails.Add("hostile climbed the lowered ladder");
            if (fails.Count == 0) c.Pass("held without a ladder (hostile and friendly); ladder released the friendly and not the hostile");
            else c.Defect(string.Join("; ", fails));
        }

        // ════════════════════════════════════════════════════════════════
        // scenario: inject - proves an exception leaves earlier records and reads INCOMPLETE
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnInject(PCtx c)
        {
            c.ev["route"] = "deliberate exception after one tick";
            yield return PTicks(1);
            throw new InvalidOperationException("injected failure (recipe token 'inject')");
        }

        // ════════════════════════════════════════════════════════════════
        // tiny JSON (the companion ships no serializer of its own)
        // ════════════════════════════════════════════════════════════════

        private static Dictionary<string, object> PD(params object[] kv)
        {
            var d = new Dictionary<string, object>();
            for (int i = 0; i + 1 < kv.Length; i += 2) d[(string)kv[i]] = kv[i + 1];
            return d;
        }

        private static void PJson(StringBuilder sb, object v)
        {
            switch (v)
            {
                case null: sb.Append("null"); return;
                case string s: PJsonStr(sb, s); return;
                case bool b: sb.Append(b ? "true" : "false"); return;
                case float f: sb.Append(float.IsNaN(f) || float.IsInfinity(f) ? "null" : f.ToString("R", CultureInfo.InvariantCulture)); return;
                case double d: sb.Append(double.IsNaN(d) || double.IsInfinity(d) ? "null" : d.ToString("R", CultureInfo.InvariantCulture)); return;
                case int _: case long _: case short _: case byte _: case uint _: case ulong _: case ushort _: case sbyte _: case decimal _:
                    sb.Append(Convert.ToString(v, CultureInfo.InvariantCulture)); return;
                case IDictionary dict:
                    sb.Append('{'); bool first = true;
                    foreach (DictionaryEntry e in dict)
                    {
                        if (!first) sb.Append(',');
                        first = false;
                        PJsonStr(sb, Convert.ToString(e.Key, CultureInfo.InvariantCulture)); sb.Append(':'); PJson(sb, e.Value);
                    }
                    sb.Append('}'); return;
                case IEnumerable seq:
                    sb.Append('['); bool f1 = true;
                    foreach (object o in seq) { if (!f1) sb.Append(','); f1 = false; PJson(sb, o); }
                    sb.Append(']'); return;
                default: PJsonStr(sb, v.ToString()); return;
            }
        }

        private static void PJsonStr(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char ch in s)
            {
                switch (ch)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (ch < 0x20) sb.Append("\\u").Append(((int)ch).ToString("x4"));
                        else sb.Append(ch);
                        break;
                }
            }
            sb.Append('"');
        }
    }
}
