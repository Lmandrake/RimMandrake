// JawaBenchGssPlaytest.cs - Gimme Some Slack in-game scenario runner (Approach A for GSS, 2026-10-06).
//
// WHY: owner 2026-10-06 (design/RimMandrake/flowworks_playtest_campaign_2026-10-06.md): every mod in the campaign gets
// an in-game runner, and "very critical we test out the interface buttons and the like too". Same shape as the
// FlowWorks runner (JawaBenchFlowWorksPlaytest.cs): one bridge call starts a run, C# iterators advance across Unity
// frames, each scene's verdict is appended to a JSONL journal the moment it ends, run_end last.
// Launcher: src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py.
//
// SCENES: cords (connect / disconnect / reconnect, incremental == fresh), hose_bend (the outlet-bend hypothesis for
// the 9 live MX_H FAILs, laid with and without the outlet on the live map), hose_carry (a real colonist's work-giver
// deploy / move / retract, and a draft mid-carry), soak (wind + explosions over cords, spans and a hose, counting
// red errors), ui (every reel and anchor gizmo through ProcessInput and the Targeter's own callback, the hose float
// menu through FloatMenuMakerMap.GetOptions, the build-designator style menus, every settings toggle, the settings
// window drawn on every tab), save_reload (+ save_reload_b after loading: cords, hoses incl. a mid-carry trail and
// spans compared line by line).
//
// EVIDENCE vs SETUP: spawning conduits/devices/reels/masts and DevLayInstant build FIXTURES. Evidence routes are the
// mod's own: the cord component's rebuild (frames), RM_MapComponent_Hoses.EnsureLay, the explosion Harmony seam,
// gizmo/menu/targeter callbacks, the work giver and job drivers.
//
// COUPLING: this file compiles against RimMandrakeGimmeSomeSlack.dll (csproj GssModDir, Private=false, the same
// "call straight into the already-loaded mod" route as Droidworks/Inhabited). No member SIGNATURE in this file names
// a GSS type (helpers take Thing/Map), so a companion loaded without GSS only fails if a GSS tool is CALLED, and the
// start tool refuses first when the mod is absent.

using System;
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
using GSS = RimMandrake.GimmeSomeSlack;
using GCore = RimMandrake.GimmeSomeSlack.Core;
using GHose = RimMandrake.GimmeSomeSlack.Hose;
using GAer = RimMandrake.GimmeSomeSlack.Aerial;

namespace JawaBench.BridgeTools
{
    internal sealed class JawaBenchGssPlaytestDriver : MonoBehaviour
    {
        private void Update() => JawaBenchTerrainTools.GssPlaytestFrame();
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/gss_playtest_start",
            Description =
                "Gimme Some Slack in-game scenario runner. Starts a run on the CURRENT map and returns its run id AT ONCE; the run " +
                "advances across game frames. recipe = comma list: cords, hose_bend, hose_carry, soak, ui, save_reload (arms: SAVES " +
                "the game, record PENDING), save_reload_b (needs resume=<runId>, after loading that save); full = all but the resume " +
                "half, save_reload last; quick = cords,hose_bend,ui. tickMode batch (default) PAUSES and steps ticks itself; speed = " +
                "Ultrafast. MODIFIES THE MAP (conduits, devices, reels, masts, explosions; settings flipped and restored): scratch maps " +
                "only. Poll gss_playtest_status, then gss_playtest_collect.",
            ResultDescription = "success, runId, journalPath, scenarios[], tickMode, frameBudgetMs, driver, ticksGame.")]
        public static async Task<object> GssPlaytestStart(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma list of scenes; quick = cords,hose_bend,ui; full = all.", DefaultValue = "quick")]
            string recipe = "quick",
            [ToolParameter(Description = "Seed for fixture-search jitter and explosion placement.", DefaultValue = 1)]
            int seed = 1,
            [ToolParameter(Description = "batch or speed.", DefaultValue = "batch")]
            string tickMode = "batch",
            [ToolParameter(Description = "batch mode: wall ms of ticking per frame (5-500).", DefaultValue = 50)]
            int frameBudgetMs = 50,
            [ToolParameter(Description = "Abort an active GSS run and start anyway.", DefaultValue = false)]
            bool force = false,
            [ToolParameter(Description = "save_reload_b only: the runId of the save_reload run it continues.")]
            string resume = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (GenTypes.GetTypeInAnyAssembly("RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph") == null)
                    return Fail("Gimme Some Slack (mandrake.rm.gimmesomeslack) is not loaded.");
                if (gRun != null && gRun.state == "running")
                {
                    if (!force) return Fail("A GSS playtest run is active: " + gRun.id + ". Pass force=true to abort it.");
                    gRun.Abort("aborted by a new gss_playtest_start force=true");
                }
                if (pRun != null && pRun.state == "running") return Fail("A FlowWorks playtest run is active: " + pRun.id + "; one runner at a time.");
                string mode = (tickMode ?? "batch").Trim().ToLowerInvariant();
                if (mode != "batch" && mode != "speed") return Fail("tickMode must be batch or speed.");
                List<string> names = GssParseRecipe(recipe, out string bad);
                if (bad != null) return Fail("Unknown scenario '" + bad + "'. Known: " + string.Join(", ", GssKnown) + "; recipes quick, full.");
                if (names.Contains("save_reload_b") && string.IsNullOrEmpty(resume)) return Fail("save_reload_b needs resume=<runId of the save_reload run>.");
                if (names.Count == 0) return Fail("Empty recipe.");
                string driver = GssEnsureDriver(out string derr);
                if (driver == null) return Fail("Could not install the per-frame driver: " + derr);
                var run = new GRun(map, names, seed, mode, Mathf.Clamp(frameBudgetMs, 5, 500), recipe) { driver = driver, resume = resume };
                gRun = run;
                gRuns[run.id] = run;
                run.Begin();
                return (object)new { success = true, runId = run.id, journalPath = run.journalPath, scenarios = names, tickMode = mode, frameBudgetMs = run.frameBudgetMs, driver, ticksGame = TicksGameSafe() };
            });
        }

        [Tool("jawa/gss_playtest_status", Description = "State of a GSS playtest run and the records so far. Empty runId = latest.",
            ResultDescription = "success, runId, state, scenarioIndex, scenarioCount, current, phase, wallSec, ticks, records[], error.")]
        public static async Task<object> GssPlaytestStatus(IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "Run id; empty = latest.")] string runId = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                GRun run = string.IsNullOrEmpty(runId) ? gRun : (gRuns.TryGetValue(runId, out GRun r) ? r : null);
                if (run == null) return Fail("No such GSS playtest run: " + (runId ?? "(latest)"));
                return (object)run.StatusObject();
            });
        }

        [Tool("jawa/gss_playtest_collect", Description = "Report for a GSS playtest run: journal path and a verdict RE-DERIVED FROM THE FILE (same rule as jawa/playtest_collect).",
            ResultDescription = "success, runId, reportPath, verdict, scenarioLines, hasRunEnd, state, summary.")]
        public static async Task<object> GssPlaytestCollect(IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "Run id; empty = latest.")] string runId = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                GRun run = string.IsNullOrEmpty(runId) ? gRun : (gRuns.TryGetValue(runId, out GRun r) ? r : null);
                if (run == null) return Fail("No such GSS playtest run: " + (runId ?? "(latest)"));
                string[] lines = File.Exists(run.journalPath) ? File.ReadAllLines(run.journalPath) : new string[0];
                string last = lines.LastOrDefault(l => l.Trim().Length > 0) ?? "";
                return (object)new
                {
                    success = true, runId = run.id, reportPath = run.journalPath, verdict = PlaytestVerdict(lines),
                    scenarioLines = lines.Count(l => l.Contains("\"type\":\"scenario\"")), hasRunEnd = last.Contains("\"type\":\"run_end\""),
                    state = run.state, summary = run.StatusObject()
                };
            });
        }

        [Tool(
            "jawa/gss_stage",
            Description =
                "Gimme Some Slack looks board: the GSS state ops a recipe needs after jawa/artboard_stage spawned its things " +
                "(src/RimMandrake/Utils/artboard/recipes.py gss_states). One op per line, key=value joined by |: " +
                "id=..|kind=gss_charge|x|z (fill the battery there); kind=gss_hose|x|z (reel cell)|tx|tz|end=open,nozzle,cap|flow=0,1|look=<style look>; " +
                "kind=gss_link|x|z|x2|z2|cut=0,1 (anchors at the two cells, optional explosion-style cut); kind=gss_ticks|n=1-2000 (single ticks, " +
                "for a hose to plump). Things touched get the player faction. REFUSES an op rather than relocating it. Ends with a cord rebuild " +
                "and the touched cells' cord mesh dirtied so the next capture shows them.",
            ResultDescription = "success (every op ok), ops[{id, kind, ok, error}].")]
        public static async Task<object> GssStage(IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "Path of an ops file (one op per line).")] string opsPath = null,
            [ToolParameter(Description = "Ops inline, separated by ';;' (when no file).")] string ops = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (GenTypes.GetTypeInAnyAssembly("RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph") == null) return Fail("Gimme Some Slack is not loaded.");
                string[] lines = !string.IsNullOrEmpty(opsPath) ? File.ReadAllLines(opsPath) : (ops ?? "").Split(new[] { ";;" }, StringSplitOptions.None);
                var rows = new List<Dictionary<string, object>>();
                foreach (string raw in lines)
                {
                    if (raw.Trim().Length == 0) continue;
                    var kv = raw.Trim().Split('|').Select(x => x.Split(new[] { '=' }, 2)).Where(x => x.Length == 2).ToDictionary(x => x[0], x => x[1]);
                    var row = PD("id", kv.TryGetValue("id", out string id) ? id : null, "kind", kv.TryGetValue("kind", out string k) ? k : null, "ok", false, "error", null);
                    rows.Add(row);
                    try { row["error"] = GssStageOp(map, kv); row["ok"] = row["error"] == null; }
                    catch (Exception e) { row["error"] = e.GetType().Name + ": " + e.Message; }
                }
                var comp = map.GetComponent<GSS.RM_MapComponent_CordGraph>();
                comp?.Rebuild();
                if (comp != null) foreach (GCore.LaidPiece pc in comp.Pieces) map.mapDrawer.MapMeshDirty(GSS.CordWorldAdapter.I(pc.Owner), GSS.GimmeSomeSlackDefOf.RM_MessyCords);
                return (object)PD("success", rows.All(r => (bool)r["ok"]), "ops", rows, "ticksGame", TicksGameSafe());
            });
        }

        private static string GssStageOp(Map map, Dictionary<string, string> kv)
        {
            int I(string key) => int.Parse(kv[key], CultureInfo.InvariantCulture);
            string kind = kv.TryGetValue("kind", out string kk) ? kk : "";
            if (kind == "gss_ticks")
            {
                int n = Mathf.Clamp(I("n"), 1, 2000);
                for (int i = 0; i < n; i++) Find.TickManager.DoSingleTick();
                return null;
            }
            var at = new IntVec3(I("x"), 0, I("z"));
            if (!at.InBounds(map)) return "cell " + at + " out of bounds";
            ThingWithComps Own(IntVec3 c, Func<ThingWithComps, bool> pred)
            {
                ThingWithComps t = c.GetThingList(map).OfType<ThingWithComps>().FirstOrDefault(pred);
                if (t != null && t.def.CanHaveFaction && t.Faction != Faction.OfPlayer) t.SetFaction(Faction.OfPlayer);
                return t;
            }
            if (kind == "gss_charge")
            {
                ThingWithComps b = Own(at, t => t.TryGetComp<CompPowerBattery>() != null);
                if (b == null) return "no battery at " + at;
                CompPowerBattery cb = b.TryGetComp<CompPowerBattery>();
                cb.AddEnergy(cb.Props.storedEnergyMax);
                return null;
            }
            if (kind == "gss_hose")
            {
                ThingWithComps reel = Own(at, t => t.TryGetComp<GHose.CompHoseReel>() != null);
                if (reel == null) return "no hose reel at " + at;
                var rc = reel.TryGetComp<GHose.CompHoseReel>();
                if (kv.TryGetValue("look", out string look) && look.Length > 0) rc.SetLook(look);
                if (kv.TryGetValue("end", out string end)) rc.end = end == "nozzle" ? GHose.HoseEnd.Nozzle : end == "cap" ? GHose.HoseEnd.EndCap : GHose.HoseEnd.Open;
                if (kv.ContainsKey("tx"))
                {
                    string why = rc.DevLayInstant(new IntVec3(I("tx"), 0, I("tz")));
                    if (why != null) return "lay refused: " + why;
                    if (map.GetComponent<GHose.RM_MapComponent_Hoses>().EnsureLay(rc) == null) return "laid but no geometry: " + rc.lastLayReason;
                }
                if (kv.TryGetValue("flow", out string fl)) rc.debugFlowing = fl == "1";
                return null;
            }
            if (kind == "gss_link")
            {
                var at2 = new IntVec3(I("x2"), 0, I("z2"));
                ThingWithComps a = Own(at, t => GAer.CompAerialAnchor.Of(t) != null), b = Own(at2, t => GAer.CompAerialAnchor.Of(t) != null);
                if (a == null || b == null) return "no anchor at " + (a == null ? at : at2);
                GAer.LinkVerdict v = GAer.CompAerialAnchor.TryLink(GAer.CompAerialAnchor.Of(a), b);
                if (v != GAer.LinkVerdict.Ok) return "link refused: " + v;
                if (kv.TryGetValue("cut", out string cut) && cut == "1" && !GAer.CompAerialAnchor.Cut(GAer.CompAerialAnchor.Of(a), GAer.CompAerialAnchor.Of(b), 0.5f, true)) return "cut refused";
                return null;
            }
            return "unknown kind '" + kind + "' (gss_charge, gss_hose, gss_link, gss_ticks)";
        }

        // ════════════════════════════════════════════════════════════════ controller

        private static GRun gRun;
        private static readonly Dictionary<string, GRun> gRuns = new Dictionary<string, GRun>();
        private static GameObject gDriverGo;
        private static int gLastFrame = -1;

        private static readonly string[] GssKnown = { "cords", "hose_bend", "hose_carry", "soak", "ui", "save_reload", "save_reload_b" };
        private static readonly string[] GssFull = { "cords", "hose_bend", "hose_carry", "soak", "ui", "save_reload" };

        private static List<string> GssParseRecipe(string recipe, out string bad)
        {
            bad = null;
            var o = new List<string>();
            foreach (string raw in (recipe ?? "quick").Split(','))
            {
                string s = raw.Trim().ToLowerInvariant();
                if (s.Length == 0) continue;
                if (s == "quick") { o.AddRange(new[] { "cords", "hose_bend", "ui" }); continue; }
                if (s == "full") { o.AddRange(GssFull); continue; }
                if (!GssKnown.Contains(s)) { bad = s; return o; }
                o.Add(s);
            }
            return o;
        }

        private static string GssEnsureDriver(out string error)
        {
            error = null;
            if (gDriverGo != null && gDriverGo.GetComponent<JawaBenchGssPlaytestDriver>() != null) return "monobehaviour";
            try
            {
                gDriverGo = new GameObject("JawaBench.GssPlaytestDriver");
                UnityEngine.Object.DontDestroyOnLoad(gDriverGo);
                if (gDriverGo.AddComponent<JawaBenchGssPlaytestDriver>() != null) return "monobehaviour";
                error = "AddComponent returned null";
            }
            catch (Exception e) { error = "AddComponent threw " + e.GetType().Name + ": " + e.Message; }
            return null;
        }

        internal static void GssPlaytestFrame()
        {
            if (Time.frameCount == gLastFrame) return;
            gLastFrame = Time.frameCount;
            GRun run = gRun;
            if (run == null || run.state != "running") return;
            try { run.Frame(); }
            catch (Exception e) { run.Abort("runner exception: " + e); }
        }

        /// <summary>One GSS scene's context: the shared PCtx fields the FlowWorks runner uses (no excavation), plus a red-error
        /// counter fed by Unity's log callback while the scene runs.</summary>
        internal sealed class GCtx
        {
            public GRun run; public string name; public Map map;
            public PhaseClock clock = new PhaseClock("setup");
            public string status, reason;
            public string expectedFailUntil = null;   // no GSS scene is expected to fail yet (G2 waits on a design call, so it FAILs)
            public readonly Dictionary<string, object> ev = new Dictionary<string, object>();
            public readonly List<Thing> fixtures = new List<Thing>();
            public int errors; public readonly List<string> errorSamples = new List<string>();
            public double waitWall; public int waitTicks;
            public void Phase(string p) => clock.Switch(p);
            public void Pass(string why = null) { status = "PASS"; reason = why; }
            public void Defect(string why) { status = "FAIL"; reason = why; }
            public void Invalid(string why) { status = "INVALID"; reason = why; }
            public void OnLog(string msg, string stack, LogType type)
            {
                if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert) return;
                errors++;
                if (errorSamples.Count < 6) errorSamples.Add(msg.Length > 300 ? msg.Substring(0, 300) : msg);
            }
            public T Keep<T>(T t) where T : Thing { fixtures.Add(t); return t; }
        }

        internal sealed class GRun
        {
            public readonly string id; public readonly Map map; public readonly List<string> names; public readonly int seed;
            public readonly string tickMode; public readonly int frameBudgetMs; public readonly string recipe; public readonly string journalPath;
            public string driver, resume, state = "running", error;
            public int index = -1;
            public GCtx cur;
            private IEnumerator<PWait> it;
            private PWait wait;
            private PhaseClock runClock;
            private TimeSpeed prevSpeed;
            private int startTick, startFrame, lastSpeedTick;
            private double waitWallStart; private int waitTickStart;
            private Application.LogCallback logCb;
            public readonly List<Dictionary<string, object>> records = new List<Dictionary<string, object>>();

            public GRun(Map map, List<string> names, int seed, string tickMode, int frameBudgetMs, string recipe)
            {
                this.map = map; this.names = names; this.seed = seed; this.tickMode = tickMode; this.frameBudgetMs = frameBudgetMs; this.recipe = recipe;
                id = "gsspt_" + DateTime.UtcNow.ToString("yyyyMMddTHHmmss", CultureInfo.InvariantCulture) + "_s" + seed;
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
                logCb = (m, s, t) => cur?.OnLog(m, s, t);
                Application.logMessageReceived += logCb;
                Write(PD("type", "run_start", "runId", id, "recipe", recipe, "scenarios", names, "seed", seed, "tickMode", tickMode,
                    "frameBudgetMs", frameBudgetMs, "driver", driver, "resume", resume, "mapId", map.uniqueID, "mapSize", map.Size.x + "x" + map.Size.z,
                    "ticksGame", startTick, "utc", DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture),
                    "gss", AssemblyIdentity(typeof(GSS.RM_MapComponent_CordGraph).Assembly),
                    "companion", AssemblyIdentity(typeof(JawaBenchTerrainTools).Assembly),
                    "settings", GssSettingsSnapshot(), "devMode", Prefs.DevMode));
            }

            public void Frame()
            {
                if (Current.Game == null || Find.CurrentMap != map || !Find.Maps.Contains(map)) { Abort("map changed or game ended mid-run"); return; }
                if (runClock.Wall > 1500) { Abort("run exceeded 1500 s wall"); return; }
                if (tickMode == "speed" && Find.TickManager.CurTimeSpeed != TimeSpeed.Ultrafast) Find.TickManager.CurTimeSpeed = TimeSpeed.Ultrafast;
                if (tickMode == "batch" && Find.TickManager.CurTimeSpeed != TimeSpeed.Paused) Find.TickManager.CurTimeSpeed = TimeSpeed.Paused;
                var budget = Stopwatch.StartNew();
                while (state == "running")
                {
                    if (cur == null && !StartNext()) { Finish(); return; }
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
                    if (wait == null) return;            // yield null = next frame (lets the cord layer rebuild)
                    wait.startTick = TicksGameSafe();
                    waitWallStart = cur.clock.Wall; waitTickStart = TicksGameSafe();
                }
            }

            private bool StartNext()
            {
                index++;
                if (index >= names.Count) return false;
                runClock.Switch("scenarios");
                cur = new GCtx { run = this, name = names[index], map = map };
                it = GssScenarioFor(names[index], cur).GetEnumerator();
                return true;
            }

            private void EndScenario()
            {
                cur.clock.Book();
                if (cur.status == null) cur.Invalid("scenario ended without a verdict");
                // a scene that passed while the game logged red errors is not a pass
                if (cur.status == "PASS" && cur.errors > 0) cur.Defect(cur.errors + " red error(s) logged during an otherwise passing scene: " + string.Join(" | ", cur.errorSamples));
                if (cur.name != "save_reload") GssCleanup(cur);
                double wall = cur.clock.acc.Values.Sum(a => a.wall);
                int ticks = cur.clock.acc.Values.Sum(a => a.ticks), frames = cur.clock.acc.Values.Sum(a => a.frames);
                var rec = PD("type", "scenario", "runId", id, "index", index, "name", cur.name, "status", cur.status, "reason", cur.reason,
                    "expectedFailUntil", cur.expectedFailUntil, "evidence", cur.ev, "redErrors", cur.errors, "redErrorSamples", cur.errorSamples,
                    "timing", PD("wallSec", Math.Round(wall, 3), "ticks", ticks, "frames", frames, "phases", cur.clock.Phases(),
                        "waitWallSec", Math.Round(cur.waitWall, 3), "waitTicks", cur.waitTicks,
                        "ticksPerSecDuringWaits", cur.waitWall > 0 ? Math.Round(cur.waitTicks / cur.waitWall, 1) : 0.0),
                    "ticksGame", TicksGameSafe());
                records.Add(rec);
                Write(rec);
                cur = null; it = null; wait = null;
            }

            private void Finish() { state = "completed"; WriteEnd(true); }

            public void Abort(string why)
            {
                if (state != "running") return;
                error = why; state = "aborted";
                try { if (cur != null) GssCleanup(cur); } catch { /* best effort */ }
                try { WriteEnd(false); } catch (Exception e) { Log.Warning("[JawaBench.gss_playtest] could not write run_end: " + e.Message); }
            }

            private void WriteEnd(bool completed)
            {
                runClock.Book();
                if (logCb != null) Application.logMessageReceived -= logCb;
                try { if (Current.Game != null) Find.TickManager.CurTimeSpeed = prevSpeed; } catch { /* best effort */ }
                double inScen = records.Sum(r => Convert.ToDouble(((Dictionary<string, object>)r["timing"])["wallSec"]));
                double wW = records.Sum(r => Convert.ToDouble(((Dictionary<string, object>)r["timing"])["waitWallSec"]));
                int wT = records.Sum(r => Convert.ToInt32(((Dictionary<string, object>)r["timing"])["waitTicks"]));
                Write(PD("type", "run_end", "runId", id, "completed", completed, "state", state, "error", error,
                    "scenariosPlanned", names.Count, "scenariosRecorded", records.Count,
                    "statuses", records.Select(r => r["name"] + ":" + r["status"]).ToList(),
                    "timing", PD("wallSec", Math.Round(runClock.Wall, 3), "ticks", TicksGameSafe() - startTick, "frames", Time.frameCount - startFrame,
                        "phases", PD("runner", PD("wallSec", Math.Round(Math.Max(0, runClock.Wall - inScen), 3))),
                        "waitWallSec", Math.Round(wW, 3), "waitTicks", wT, "ticksPerSecDuringWaits", wW > 0 ? Math.Round(wT / wW, 1) : 0.0,
                        "tickMode", tickMode, "frameBudgetMs", frameBudgetMs, "speedRestoredTo", prevSpeed.ToString()),
                    "ticksGame", TicksGameSafe()));
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
                "scenarioIndex", index, "scenarioCount", names.Count, "current", cur?.name, "phase", cur?.clock.phase,
                "wallSec", runClock != null ? Math.Round(runClock.Wall, 2) : 0.0, "ticks", TicksGameSafe() - startTick,
                "frames", Time.frameCount - startFrame, "tickMode", tickMode, "driver", driver,
                "records", records.Select(r => (object)PD("name", r["name"], "status", r["status"], "reason", r["reason"],
                    "expectedFailUntil", r["expectedFailUntil"], "wallSec", ((Dictionary<string, object>)r["timing"])["wallSec"],
                    "ticks", ((Dictionary<string, object>)r["timing"])["ticks"])).ToList(),
                "ticksGame", TicksGameSafe());
        }

        private static Dictionary<string, object> GssSettingsSnapshot()
        {
            var d = new Dictionary<string, object>();
            foreach (Type t in new[] { typeof(GSS.GimmeSomeSlackSettings), typeof(GHose.HoseSettings), typeof(GAer.AerialSettings) })
                foreach (FieldInfo f in t.GetFields(BindingFlags.Public | BindingFlags.Static))
                    if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int) || f.FieldType == typeof(string) || f.FieldType.IsEnum)
                        d[t.Name + "." + f.Name] = f.FieldType.IsEnum ? f.GetValue(null)?.ToString() : f.GetValue(null);
            return d;
        }

        private static IEnumerable<PWait> GssScenarioFor(string name, GCtx c)
        {
            switch (name)
            {
                case "cords": return GScnCords(c);
                case "hose_bend": return GScnHoseBend(c);
                case "hose_carry": return GScnHoseCarry(c);
                case "soak": return GScnSoak(c);
                case "ui": return GScnUi(c);
                case "save_reload": return GScnSaveReloadA(c);
                case "save_reload_b": return GScnSaveReloadB(c);
                default: throw new ArgumentException("unknown scenario " + name);
            }
        }

        private static void GssCleanup(GCtx c)
        {
            foreach (Thing t in c.fixtures.AsEnumerable().Reverse())
                if (t != null && !t.Destroyed && t.Spawned) { try { t.Destroy(DestroyMode.Vanish); } catch (Exception e) { Log.Warning("[JawaBench.gss_playtest] cleanup " + t + ": " + e.Message); } }
            c.fixtures.Clear();
            if (Find.Targeter.IsTargeting) Find.Targeter.StopTargeting();
            Find.DesignatorManager.Deselect();
        }

        // ════════════════════════════════════════════════════════════════ fixtures

        /// <summary>A w x h rect of clean, standable, unroofed, unfogged ground with no building/pawn/item (plants cleared),
        /// 10 cells from the edge, searched outward from near.</summary>
        private static bool GFindRect(GCtx c, IntVec3 near, int w, int h, out CellRect rect)
        {
            Map m = c.map;
            var rng = new System.Random(c.run.seed * 7919 + w * 31 + h);
            var keyed = new List<KeyValuePair<int, IntVec3>>();
            for (int x = 10; x < m.Size.x - 10 - w; x += 3)
                for (int z = 10; z < m.Size.z - 10 - h; z += 3)
                {
                    var o = new IntVec3(x, 0, z);
                    keyed.Add(new KeyValuePair<int, IntVec3>((o - near).LengthHorizontalSquared + rng.Next(0, 64), o));
                }
            foreach (var kv in keyed.OrderBy(k => k.Key))
            {
                var r = new CellRect(kv.Value.x, kv.Value.z, w, h);
                bool ok = true;
                foreach (IntVec3 x in r.Cells)
                {
                    if (x.Fogged(m) || x.Roofed(m) || x.GetEdifice(m) != null || x.GetFirstPawn(m) != null || !x.Standable(m)) { ok = false; break; }
                    TerrainDef t = m.terrainGrid.TopTerrainAt(x);
                    if (t == null || t.IsWater || !t.affordances.Contains(TerrainAffordanceDefOf.Light)) { ok = false; break; }
                    if (x.GetThingList(m).Any(th => !(th is Plant) && th.def.category != ThingCategory.Filth)) { ok = false; break; }
                }
                if (!ok) continue;
                foreach (IntVec3 x in r.Cells) foreach (Thing th in x.GetThingList(m).ToList()) if (th is Plant || th.def.category == ThingCategory.Filth) th.Destroy(DestroyMode.Vanish);
                rect = r;
                return true;
            }
            rect = default(CellRect);
            return false;
        }

        private static Thing GSpawn(GCtx c, string defName, IntVec3 at, Rot4? rot = null)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (d == null) return null;
            Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? GenStuff.DefaultStuffFor(d) : null);
            if (t.def.CanHaveFaction) t.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(t, at, c.map, rot ?? Rot4.North);
            return c.Keep(t);
        }

        private static IEnumerable<PWait> GFrames(int n) { for (int i = 0; i < n; i++) yield return null; }

        // ════════════════════════════════════════════════════════════════ cords

        /// <summary>Edges (visible cords) with one end inside the rect of thing t.</summary>
        private static int GCordsTo(Map m, Thing t)
        {
            var comp = m.GetComponent<GSS.RM_MapComponent_CordGraph>();
            GCore.CordGraph g = comp?.Graph;
            if (g == null) return -1;
            CellRect r = t.OccupiedRect();
            int n = 0;
            foreach (GCore.CordEdge e in g.CordEdges())
            {
                GCore.Cell a = g.CellOf(e.A), b = g.CellOf(e.B);
                if (r.Contains(new IntVec3(a.X, 0, a.Z)) || r.Contains(new IntVec3(b.X, 0, b.Z))) n++;
            }
            return n;
        }

        /// <summary>The live component's laid cords against a fresh builder on a fresh snapshot (GimmeSomeSlackProbe "fresh").</summary>
        private static Dictionary<string, object> GFresh(Map m)
        {
            var comp = m.GetComponent<GSS.RM_MapComponent_CordGraph>();
            GCore.CordWorld w = GSS.CordWorldAdapter.Snapshot(m);
            List<GCore.LaidPiece> fresh = new GCore.CordBuilder().Build(w, GSS.GimmeSomeSlackSettings.BuildOptions(), cc => GSS.CordWorldAdapter.IsLive(m, cc));
            var cur = comp.Pieces.Where(p => p.EndA != null).GroupBy(p => p.Key).ToDictionary(g => g.Key, g => g.First().GeometryHash());
            int same = 0, diff = 0, missing = 0;
            var diffKeys = new List<string>();
            foreach (GCore.LaidPiece p in fresh.Where(p => p.EndA != null))
            {
                if (!cur.TryGetValue(p.Key, out ulong h)) { missing++; if (diffKeys.Count < 4) diffKeys.Add("missing " + p.Key); }
                else if (h == p.GeometryHash()) same++;
                else { diff++; if (diffKeys.Count < 4) diffKeys.Add("differs " + p.Key); }
            }
            int extra = cur.Keys.Count(k => !fresh.Any(p => p.Key == k));
            return PD("edges", fresh.Count(p => p.EndA != null), "same", same, "different", diff, "missing", missing, "extraInLive", extra,
                "equal", diff == 0 && missing == 0 && extra == 0, "diffKeys", diffKeys, "builds", comp.Builds, "planned", comp.LastPlanned, "reused", comp.LastReused);
        }

        private static IEnumerable<PWait> GScnCords(GCtx c)
        {
            c.ev["route"] = "conduits + battery + lamp spawned (fixture); vanilla PowerConnectionMaker connects; the cord component rebuilds on its own over frames; checked against a fresh CordBuilder";
            Map m = c.map;
            if (!GSS.GimmeSomeSlackSettings.enabled) { c.Invalid("Gimme Some Slack cords are switched off in settings"); yield break; }
            if (!GFindRect(c, m.Center + new IntVec3(-30, 0, -30), 14, 9, out CellRect r)) { c.Invalid("no clean 14x9 site"); yield break; }
            int z = r.minZ + 4;
            var conduits = new List<Thing>();
            for (int x = r.minX + 2; x <= r.minX + 9; x++) conduits.Add(GSpawn(c, "PowerConduit", new IntVec3(x, 0, z)));
            Thing battery = GSpawn(c, "Battery", new IntVec3(r.minX + 2, 0, z + 2), Rot4.North);
            Thing lamp = GSpawn(c, "StandingLamp", new IntVec3(r.minX + 8, 0, z - 3));
            if (conduits.Any(t => t == null) || battery == null || lamp == null) { c.Invalid("PowerConduit / Battery / StandingLamp def missing"); yield break; }
            battery.TryGetComp<CompPowerBattery>()?.AddEnergy(600f);
            c.ev["site"] = PD("x", r.minX, "z", r.minZ);
            c.Phase("exec");
            yield return PTicks(5);
            foreach (PWait x in GFrames(4)) yield return x;
            c.Phase("observe");
            var steps = new List<Dictionary<string, object>>();
            c.ev["steps"] = steps;
            CompPower lp = lamp.TryGetComp<CompPower>();
            int toLamp = GCordsTo(m, lamp);
            var f1 = GFresh(m);
            steps.Add(PD("step", "connect", "lampConnectedTo", lp?.connectParent?.parent?.Position.ToString(), "cordsToLamp", toLamp, "fresh", f1));

            // disconnect: remove every conduit (the lamp loses its transmitter)
            c.Phase("exec");
            foreach (Thing t in conduits) if (t.Spawned) t.Destroy(DestroyMode.Deconstruct);
            yield return PTicks(5);
            foreach (PWait x in GFrames(4)) yield return x;
            c.Phase("observe");
            int toLamp2 = GCordsTo(m, lamp);
            var f2 = GFresh(m);
            steps.Add(PD("step", "disconnect", "lampConnectedTo", lp?.connectParent?.parent?.Position.ToString(), "cordsToLamp", toLamp2, "fresh", f2));

            // reconnect: lay the run again
            c.Phase("exec");
            conduits.Clear();
            for (int x = r.minX + 2; x <= r.minX + 9; x++) conduits.Add(GSpawn(c, "PowerConduit", new IntVec3(x, 0, z)));
            yield return PTicks(5);
            foreach (PWait x in GFrames(4)) yield return x;
            c.Phase("observe");
            int toLamp3 = GCordsTo(m, lamp);
            var f3 = GFresh(m);
            steps.Add(PD("step", "reconnect", "lampConnectedTo", lp?.connectParent?.parent?.Position.ToString(), "cordsToLamp", toLamp3, "fresh", f3));

            // a wall 4-6 cells from the run (fuzz gap C1: the per-edge cache margin is 3)
            c.Phase("exec");
            Thing wall = GSpawn(c, "Wall", new IntVec3(r.minX + 6, 0, z + 4));
            yield return PTicks(2);
            foreach (PWait x in GFrames(4)) yield return x;
            c.Phase("observe");
            var f4 = GFresh(m);
            steps.Add(PD("step", "wall_4_away", "fresh", f4));

            var fails = new List<string>();
            if (toLamp <= 0) fails.Add("no cord drawn to a connected lamp (" + toLamp + ")");
            if (!(bool)f1["equal"]) fails.Add("connect: live cords != fresh build");
            if (toLamp2 > 0) fails.Add("a cord still runs to the lamp after every conduit was removed (" + toLamp2 + ")");
            if (!(bool)f2["equal"]) fails.Add("disconnect: live cords != fresh build");
            if (toLamp3 <= 0) fails.Add("no cord after the run was rebuilt");
            if (!(bool)f3["equal"]) fails.Add("reconnect: live cords != fresh build");
            bool c1 = !(bool)f4["equal"];
            c.ev["c1Reproduced"] = c1;
            if (fails.Count == 0) c.Pass("cord drawn on connect, gone on disconnect, back on reconnect; live == fresh at every step" + (c1 ? "; C1 (wall 4 away leaves a stale cord) REPRODUCED live, recorded not failed (design call)" : "; C1 not reproduced here"));
            else c.Defect(string.Join("; ", fails));
        }

        // ════════════════════════════════════════════════════════════════ hose bend (the 9 live FAILs)
        // 2026-10-06, owner decision by question card (straight lead-out): the hose leaves the nozzle straight for
        // HoseMath.LeadOutStraight cells, then joins the laid hose by a curve never under the minimum radius; a target with no
        // room for that is REFUSED (HoseMath.LeadOutBlocked), which this scene counts as a refusal, not a bar failure.

        private static double GMinBendAt(IList<GCore.V2> X, double skip, out double sAt)
        {
            double[] s = GCore.Geo.CumLen(X);
            double L = s[s.Length - 1], best = 99; sAt = -1;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < skip || s[i] > L - skip) continue;
                double th = GCore.CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (GCore.V2.Dist(X[i - 1], X[i]) + GCore.V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9 && seg / th < best) { best = seg / th; sAt = s[i]; }
            }
            return best;
        }

        private static IEnumerable<PWait> GScnHoseBend(GCtx c)
        {
            c.ev["route"] = "reel spawned; DevLayInstant (fixture) to 12 targets round it; geometry from RM_MapComponent_Hoses.EnsureLay (production); the same ends re-laid WITHOUT the outlet on the live map snapshot for the counterfactual";
            Map m = c.map;
            if (!GHose.HoseSettings.enabled) { c.Invalid("hoses switched off in settings"); yield break; }
            if (!GFindRect(c, m.Center + new IntVec3(30, 0, -30), 34, 34, out CellRect r)) { c.Invalid("no clean 34x34 site"); yield break; }
            IntVec3 at = r.CenterCell;
            Thing reel = GSpawn(c, "RM_HoseReel", at);
            if (reel == null) { c.Invalid("RM_HoseReel def missing"); yield break; }
            var rc = reel.TryGetComp<GHose.CompHoseReel>();
            var hc = m.GetComponent<GHose.RM_MapComponent_Hoses>();
            double minR = GHose.HoseSettings.minBendRadius;
            c.ev["minBendSetting"] = minR;
            c.ev["outward"] = rc.Rect.Outward.HasValue ? rc.Rect.Outward.Value.ToString() : null;
            var rows = new List<Dictionary<string, object>>();
            c.ev["lays"] = rows;
            GHose.HoseShapeParams sp = GHose.HoseSettings.Shape();
            sp.MaxLength = rc.MaxLength;
            double st = GHose.HoseMath.LeadOutStraight(sp);
            c.Phase("exec");
            foreach (int rad in new[] { 8, 14 })
                for (int k = 0; k < (rad == 8 ? 8 : 4); k++)
                {
                    double ang = (rad == 8 ? 45.0 * k : 90.0 * k + 45) * Math.PI / 180;
                    var tgt = new IntVec3(at.x + (int)Math.Round(rad * Math.Cos(ang)), 0, at.z + (int)Math.Round(rad * Math.Sin(ang)));
                    string why = rc.DevLayInstant(tgt);
                    GHose.HoseLay lay = why == null ? hc.EnsureLay(rc) : null;
                    var row = PD("target", PCell(tgt), "bearingDeg", Math.Round(ang * 180 / Math.PI), "refused", why ?? (lay == null ? rc.lastLayReason : null));
                    if (lay != null)
                    {
                        double mb = GMinBendAt(lay.Flat, GHose.HoseMath.EndSkip, out double sAt);
                        double beyond = Math.Min(GHose.HoseMath.MinBendRadius(lay.Flat, lay.LeadOutLen + 0.5), GHose.HoseMath.MinBendRadius(lay.Plump, lay.LeadOutLen + 0.5));
                        // counterfactual: the same ends, no outlet (EnsureLay's own call minus startOutward)
                        GCore.CordWorld w = hc.World();
                        GHose.HoseLay free = GHose.HoseMath.LayAlong(w, GHose.RM_MapComponent_Hoses.Start(rc), rc.TrailCells(), new GCore.Cell(tgt.x, tgt.z).Centre, sp, rc.Seed);
                        string zone = sAt < 0 ? "none" : sAt <= st ? "straight" : sAt <= lay.LeadOutLen + 0.25 ? "blend" : "beyond";
                        row["leadOutLen"] = Math.Round(lay.LeadOutLen, 2);
                        row["outlet"] = lay.Outlet; row["minBendFlat"] = Math.Round(lay.MinBendFlat, 3); row["minBendPlump"] = Math.Round(lay.MinBendPlump, 3);
                        row["minBendAtS"] = Math.Round(sAt, 2); row["zone"] = zone; row["minBendBeyondBlend"] = Math.Round(beyond, 3);
                        row["flatLen"] = Math.Round(lay.FlatLen, 2); row["maxLength"] = rc.MaxLength; row["overLength"] = lay.FlatLen > rc.MaxLength + 1e-6;
                        row["fellBack"] = lay.FellBack;
                        row["freeMinBend"] = free.Ok ? Math.Round(Math.Min(free.MinBendFlat, free.MinBendPlump), 3) : (object)null;
                        row["barPass"] = Math.Min(lay.MinBendFlat, lay.MinBendPlump) >= 0.95 * minR;
                    }
                    rows.Add(row);
                    rc.ReelIn();
                    yield return PTicks(1);
                }
            c.Phase("observe");
            var laid = rows.Where(x => x.ContainsKey("barPass")).ToList();
            var bad = laid.Where(x => !(bool)x["barPass"]).ToList();
            int inBlend = bad.Count(x => (string)x["zone"] == "blend" || (string)x["zone"] == "straight");
            int freeOk = bad.Count(x => x["freeMinBend"] is double fb && fb >= 0.95 * minR);
            int beyondOk = bad.Count(x => (double)x["minBendBeyondBlend"] >= 0.95 * minR);
            int over = laid.Count(x => (bool)x["overLength"]);
            string hyp = bad.Count == 0 ? "no tight bend to explain"
                : inBlend == bad.Count && freeOk == bad.Count && beyondOk == bad.Count
                    ? "CONFIRMED: every tight bend sits in the outlet straight/blend, the hose beyond the blend holds the radius, and the same ends laid without the outlet bend fine"
                    : "NOT confirmed as sole cause: " + inBlend + "/" + bad.Count + " in the outlet zone, " + beyondOk + "/" + bad.Count + " fine beyond it, " + freeOk + "/" + bad.Count + " fine without the outlet";
            c.ev["hypothesisOutletBend"] = hyp;
            c.ev["laid"] = laid.Count; c.ev["underBar"] = bad.Count; c.ev["overLength"] = over;
            c.ev["refusedNoLeadOut"] = rows.Count(x => (x["refused"] as string) == GHose.HoseMath.LeadOutBlocked);
            if (laid.Count == 0) { c.Invalid("no lay succeeded"); yield break; }
            if (bad.Count == 0 && over == 0) c.Pass("all " + laid.Count + " lays hold >= 95% of the minimum bend radius and the hose length");
            else c.Defect(bad.Count + "/" + laid.Count + " lays bend under 95% of " + minR.ToString("0.00") + " (worst " +
                          (bad.Count > 0 ? bad.Min(x => (double)x["minBendFlat"]).ToString("0.00") : "-") + "), " + over + " over the hose length; outlet hypothesis " + hyp);
        }

        // ════════════════════════════════════════════════════════════════ hose carry (real colonist)

        private static Pawn GWorker(Map m)
        {
            return m.mapPawns.FreeColonistsSpawned
                .Where(p => !p.Downed && !p.Drafted && !p.InMentalState && p.workSettings != null && !p.WorkTypeIsDisabled(WorkTypeDefOf.Hauling)
                            && p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
                .OrderBy(p => p.thingIDNumber).FirstOrDefault();
        }

        private static IEnumerable<PWait> GScnHoseCarry(GCtx c)
        {
            c.ev["route"] = "OrderDeploy/OrderMove/OrderRetract (what the gizmos call) -> an undrafted colonist's think tree takes WorkGiver_HoseOrders (Hauling) -> JobDriver_CarryHoseEnd / JobDriver_RetractHose; then a draft mid-carry";
            Map m = c.map;
            Pawn p = GWorker(m);
            if (p == null) { c.Invalid("no free undrafted hauling-capable colonist"); yield break; }
            if (!GFindRect(c, p.Position, 24, 12, out CellRect r)) { c.Invalid("no clean 24x12 site"); yield break; }
            if (!m.reachability.CanReach(p.Position, r.CenterCell, PathEndMode.Touch, TraverseParms.For(p))) { c.Invalid("colonist cannot reach the site"); yield break; }
            Thing reel = GSpawn(c, "RM_HoseReel", new IntVec3(r.minX + 3, 0, r.minZ + 5));
            if (reel == null) { c.Invalid("RM_HoseReel def missing"); yield break; }
            var rc = reel.TryGetComp<GHose.CompHoseReel>();
            int prevPrio = p.workSettings.GetPriority(WorkTypeDefOf.Hauling);
            var steps = new List<Dictionary<string, object>>();
            c.ev["steps"] = steps; c.ev["worker"] = p.LabelShort;
            var fails = new List<string>();
            try
            {
                p.workSettings.SetPriority(WorkTypeDefOf.Hauling, 1);
                IntVec3 t1 = new IntVec3(r.minX + 15, 0, r.minZ + 6), t2 = new IntVec3(r.minX + 12, 0, r.minZ + 10);
                foreach (var stage in new[] { new { name = "deploy", tgt = t1 }, new { name = "move", tgt = t2 }, new { name = "retract", tgt = IntVec3.Invalid } })
                {
                    c.Phase("exec");
                    string why = stage.name == "deploy" ? rc.OrderDeploy(stage.tgt) : stage.name == "move" ? rc.OrderMove(stage.tgt) : rc.OrderRetract();
                    string taker = null; bool forced = false; int t0 = TicksGameSafe();
                    PWait w = PUntil(() => rc.pending == GHose.HosePendingOrder.None &&
                                           (stage.name == "retract" ? rc.carry == GHose.HoseCarryState.Stored : rc.carry == GHose.HoseCarryState.Laid), 6000,
                        () => { if (taker == null && rc.carrier != null) { taker = rc.carrier.LabelShort; forced = rc.carrier.CurJob?.playerForced ?? false; } });
                    if (why == null) yield return w;
                    c.Phase("observe");
                    var lay = rc.HoseOut ? m.GetComponent<GHose.RM_MapComponent_Hoses>().EnsureLay(rc) : null;
                    var row = PD("stage", stage.name, "orderRefused", why, "carry", rc.carry.ToString(), "pending", rc.pending.ToString(), "far", rc.far.ToString(),
                        "taker", taker, "playerForced", forced, "ticks", TicksGameSafe() - t0, "timedOut", why == null && w.timedOut,
                        "trailCells", rc.trail.Count, "trailLength", Math.Round(rc.TrailLength(), 2), "maxLength", rc.MaxLength,
                        "layOk", lay != null, "flatLen", lay != null ? Math.Round(lay.FlatLen, 2) : (object)null);
                    steps.Add(row);
                    if (why != null) fails.Add(stage.name + " order refused: " + why);
                    else if (w.timedOut) fails.Add(stage.name + ": not finished in 6000 ticks (carry " + rc.carry + ", pending " + rc.pending + ", taker " + (taker ?? "none") + ")");
                    else if (forced) fails.Add(stage.name + ": the job was playerForced, not the work-giver route");
                    else if (stage.name != "retract" && lay == null) fails.Add(stage.name + ": the carried hose did not lay (" + rc.lastLayReason + ")");
                    if (fails.Count > 0) break;
                }
                // a draft mid-carry drops the end; undrafting resumes it (autoResumeDroppedHose)
                if (fails.Count == 0)
                {
                    c.Phase("exec");
                    string why = rc.OrderDeploy(t1);
                    yield return PUntil(() => rc.carry == GHose.HoseCarryState.Carrying && rc.TrailLength() >= 3, 4000);
                    Pawn carrier = rc.carrier;
                    bool carrying = rc.carry == GHose.HoseCarryState.Carrying && carrier != null;
                    if (carrying) carrier.drafter.Drafted = true;
                    yield return PTicks(60);
                    string afterDraft = rc.carry.ToString();
                    if (carrier != null) carrier.drafter.Drafted = false;
                    PWait wr = PUntil(() => rc.carry == GHose.HoseCarryState.Laid && rc.pending == GHose.HosePendingOrder.None, 6000);
                    yield return wr;
                    c.Phase("observe");
                    steps.Add(PD("stage", "draft_mid_carry", "orderRefused", why, "wasCarrying", carrying, "afterDraft", afterDraft, "final", rc.carry.ToString(),
                        "resumed", !wr.timedOut, "autoResumeSetting", GHose.HoseSettings.autoResumeDroppedHose));
                    if (!carrying) fails.Add("draft_mid_carry: never saw the hose being carried");
                    else if (afterDraft != "Dropped") fails.Add("drafting the carrier left the hose " + afterDraft + " (expected Dropped)");
                    else if (GHose.HoseSettings.autoResumeDroppedHose && wr.timedOut) fails.Add("undrafted carrier never resumed the dropped hose (" + rc.carry + ")");
                    rc.ReelIn();
                }
            }
            finally { if (p.workSettings != null) p.workSettings.SetPriority(WorkTypeDefOf.Hauling, prevPrio); if (p.Drafted) p.drafter.Drafted = false; }
            if (fails.Count == 0) c.Pass("deploy, move and retract taken by the work giver and finished; a draft mid-carry dropped the end and undrafting resumed it");
            else c.Defect(string.Join("; ", fails));
        }

        // ════════════════════════════════════════════════════════════════ soak: wind, cuts, explosions

        private static List<string> GSpanInvariants(Map m)
        {
            var bad = new List<string>();
            foreach (Thing t in m.listerThings.AllThings.Where(t => GAer.CompAerialAnchor.IsAnchorDef(t.def)).ToList())
            {
                var a = GAer.CompAerialAnchor.Of(t);
                if (a == null) continue;
                foreach (GAer.SpanLink l in a.links)
                {
                    if (l.other == null) { bad.Add(t.ThingID + " links a missing anchor"); continue; }
                    GAer.SpanLink back = l.other.LinkTo(a);
                    if (back == null) bad.Add(t.ThingID + "->" + l.other.parent.ThingID + " not symmetric");
                    else if (back.state != l.state) bad.Add(t.ThingID + "<->" + l.other.parent.ThingID + " states differ " + l.state + "/" + back.state);
                }
                if (a.links.Count > a.MaxLinks) bad.Add(t.ThingID + " over MaxLinks");
            }
            return bad;
        }

        private static IEnumerable<PWait> GScnSoak(GCtx c)
        {
            c.ev["route"] = "windiest weather forced (fixture); GenExplosion.DoExplosion (Bomb) every 250 ticks across a conduit run, a mast span and a laid hose: the mod's explosion seam, cord rebuild and hose re-check react on their own";
            Map m = c.map;
            if (!GFindRect(c, m.Center + new IntVec3(0, 0, 35), 26, 14, out CellRect r)) { c.Invalid("no clean 26x14 site"); yield break; }
            int z = r.minZ + 4;
            for (int x = r.minX + 2; x <= r.minX + 20; x++) GSpawn(c, "PowerConduit", new IntVec3(x, 0, z));
            Thing bat = GSpawn(c, "Battery", new IntVec3(r.minX + 2, 0, z + 2));
            bat?.TryGetComp<CompPowerBattery>()?.AddEnergy(600f);
            for (int x = r.minX + 4; x <= r.minX + 18; x += 4) GSpawn(c, "StandingLamp", new IntVec3(x, 0, z - 2));
            Thing m1 = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 3, 0, z + 7)), m2 = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 15, 0, z + 7));
            Thing reel = GSpawn(c, "RM_HoseReel", new IntVec3(r.minX + 20, 0, z + 6));
            if (m1 == null || m2 == null || reel == null || bat == null) { c.Invalid("Battery / RM_AerialMast / RM_HoseReel def missing"); yield break; }
            var a1 = GAer.CompAerialAnchor.Of(m1); var a2 = GAer.CompAerialAnchor.Of(m2);
            GAer.LinkVerdict lv = GAer.CompAerialAnchor.TryLink(a1, m2);
            var rc = reel.TryGetComp<GHose.CompHoseReel>();
            string layWhy = rc.DevLayInstant(new IntVec3(r.minX + 8, 0, z + 10));
            WeatherDef windy = DefDatabase<WeatherDef>.AllDefsListForReading.Where(w => !w.isBad || w.windSpeedFactor > 1.5f).OrderByDescending(w => w.windSpeedFactor).FirstOrDefault();
            WeatherDef prevW = m.weatherManager.curWeather;
            if (windy != null) { m.weatherManager.curWeather = windy; m.weatherManager.lastWeather = windy; }
            c.ev["link"] = lv.ToString(); c.ev["hoseLay"] = layWhy; c.ev["weather"] = windy?.defName;
            var aer = m.GetComponent<GAer.RM_MapComponent_Aerial>();
            int cuts0 = aer?.explosionCuts ?? 0;
            var rng = new System.Random(c.run.seed * 31 + 7);
            var log = new List<Dictionary<string, object>>();
            c.ev["blasts"] = log;
            var fails = new List<string>();
            try
            {
                for (int i = 0; i < 8; i++)
                {
                    c.Phase("exec");
                    IntVec3 at = i % 3 == 0 ? new IntVec3(r.minX + 9 + rng.Next(-2, 3), 0, z + 7) : i % 3 == 1 ? new IntVec3(r.minX + 3 + rng.Next(0, 16), 0, z) : new IntVec3(r.minX + 14 + rng.Next(-2, 3), 0, z + 8);
                    GenExplosion.DoExplosion(at, m, 1.9f, DamageDefOf.Bomb, null, 10);
                    yield return PTicks(250);
                    foreach (PWait x in GFrames(3)) yield return x;
                    c.Phase("observe");
                    var fr = GFresh(m);
                    List<string> spans = GSpanInvariants(m);
                    var hl = rc.HoseOut ? m.GetComponent<GHose.RM_MapComponent_Hoses>().EnsureLay(rc) : null;
                    bool hoseClear = hl == null || GHose.HoseMath.Clear(m.GetComponent<GHose.RM_MapComponent_Hoses>().World(), hl.Flat);
                    var sl = a1.LinkTo(a2);
                    log.Add(PD("i", i, "at", PCell(at), "wind", Math.Round(m.windManager.WindSpeed, 2), "freshEqual", fr["equal"], "freshDiff", fr["diffKeys"],
                        "spanState", sl?.state.ToString(), "spanBad", spans, "hoseCarry", rc.carry.ToString(), "hoseRetractReason", rc.lastRetractReason, "hoseClear", hoseClear,
                        "redErrorsSoFar", c.errors));
                    if (!(bool)fr["equal"]) fails.Add("blast " + i + ": live cords != fresh");
                    if (spans.Count > 0) fails.Add("blast " + i + ": span invariants " + string.Join(", ", spans));
                    if (!hoseClear) fails.Add("blast " + i + ": the laid hose runs through a wall/rubble");
                    if (fails.Count > 0) break;
                }
            }
            finally { if (prevW != null) { m.weatherManager.curWeather = prevW; m.weatherManager.lastWeather = prevW; } }
            c.ev["explosionCuts"] = (aer?.explosionCuts ?? 0) - cuts0;
            if (fails.Count == 0) c.Pass("8 blasts in wind: cords == fresh, spans symmetric, hose clear after every blast; " + c.ev["explosionCuts"] + " span cut(s) by explosion");
            else c.Defect(string.Join("; ", fails.Distinct()));
        }

        // ════════════════════════════════════════════════════════════════ ui: gizmos, float menus, designators, settings

        private static readonly FieldInfo TargeterAction = typeof(Targeter).GetField("action", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
        private static readonly FieldInfo FloatMenuOptions = typeof(FloatMenu).GetField("options", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);

        /// <summary>The thing's full gizmo list as the inspector shows it (Thing.GetGizmos, our comps included).</summary>
        private static List<Command> GGizmos(Thing t) => (t as ThingWithComps)?.GetGizmos().OfType<Command>().ToList() ?? new List<Command>();

        private static string GLabel(Command g) => g?.LabelCap.ToString() ?? g?.Label;

        /// <summary>Click a gizmo through its own ProcessInput; if that began targeting, complete the targeter's own callback
        /// on 'target' (what the player's click does). Returns what happened.</summary>
        private static string GClick(Command g, LocalTargetInfo? target)
        {
            if (g == null) return "absent";
            if (g.Disabled) return "disabled: " + g.disabledReason;
            g.ProcessInput(null);
            if (Find.Targeter.IsTargeting)
            {
                var act = TargeterAction?.GetValue(Find.Targeter) as Action<LocalTargetInfo>;
                if (act == null) { Find.Targeter.StopTargeting(); return "targeting began but its callback is unreadable"; }
                if (!target.HasValue) { Find.Targeter.StopTargeting(); return "targeting began, no target given"; }
                Find.Targeter.StopTargeting();
                act(target.Value);
                return "targeted";
            }
            return "clicked";
        }

        /// <summary>The newest FloatMenu's options, the window closed.</summary>
        private static List<FloatMenuOption> GTakeFloatMenu()
        {
            FloatMenu fm = Find.WindowStack.Windows.OfType<FloatMenu>().LastOrDefault();
            if (fm == null) return null;
            var l = (FloatMenuOptions?.GetValue(fm) as List<FloatMenuOption>)?.ToList() ?? new List<FloatMenuOption>();
            fm.Close(false);
            return l;
        }

        private static IEnumerable<PWait> GScnUi(GCtx c)
        {
            c.ev["route"] = "Thing.GetGizmos -> Command.ProcessInput -> (Targeter callback / FloatMenu option action); FloatMenuMakerMap.GetOptions for a selected colonist; Designator_Build.ProcessInput (style menu patch); settings fields flipped + Apply; Dialog_ModSettings drawn by the game on every tab";
            Map m = c.map;
            var checks = new List<Dictionary<string, object>>();
            c.ev["checks"] = checks;
            void Check(string what, bool ok, object detail = null) => checks.Add(PD("check", what, "ok", ok, "detail", detail));
            if (!GFindRect(c, m.Center + new IntVec3(-30, 0, 30), 30, 16, out CellRect r)) { c.Invalid("no clean 30x16 site"); yield break; }
            bool devWas = Prefs.DevMode;
            Thing reel = GSpawn(c, "RM_HoseReel", new IntVec3(r.minX + 3, 0, r.minZ + 4));
            Thing ma = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 4, 0, r.minZ + 12));
            Thing mb = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 12, 0, r.minZ + 12));
            Thing mc = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 20, 0, r.minZ + 12));
            if (reel == null || ma == null || mb == null || mc == null) { c.Invalid("RM_HoseReel / RM_AerialMast def missing"); yield break; }
            var rc = reel.TryGetComp<GHose.CompHoseReel>();
            var aa = GAer.CompAerialAnchor.Of(ma); var ab = GAer.CompAerialAnchor.Of(mb); var ac = GAer.CompAerialAnchor.Of(mc);
            IntVec3 tgt = new IntVec3(r.minX + 14, 0, r.minZ + 4);
            Command G(Thing t, string label) => GGizmos(t).FirstOrDefault(g => GLabel(g) != null && GLabel(g).StartsWith(label, StringComparison.OrdinalIgnoreCase));
            List<string> Labels(Thing t) => GGizmos(t).Select(GLabel).ToList();
            try
            {
                c.Phase("exec");
                // ── reel, player mode
                Prefs.DevMode = false;
                Find.Selector.ClearSelection(); Find.Selector.Select(reel, false, false);
                var l0 = Labels(reel);
                Check("reel stored: Deploy shown, no DEV gizmo with dev mode off", l0.Any(s => s.StartsWith("Deploy hose")) && !l0.Any(s => s.StartsWith("DEV")), l0);
                string res = GClick(G(reel, "Deploy hose"), tgt);
                Check("Deploy hose -> targeter -> pending Deploy at the clicked cell", rc.pending == GHose.HosePendingOrder.Deploy && rc.pendingAt == tgt, res + " pending " + rc.pending + " at " + rc.pendingAt);
                res = GClick(G(reel, "Cancel hose order"), null);
                Check("Cancel hose order clears it", rc.pending == GHose.HosePendingOrder.None, res);
                var ends = new List<string>();
                for (int i = 0; i < 3; i++) { GClick(G(reel, "Free end"), null); ends.Add(rc.end.ToString()); }
                Check("Free end toggle cycles three ends and returns", ends.Distinct().Count() == 3 && ends[2] == "Open", ends);
                string look0 = GAer.StylePicker.LookOfThing(reel);
                res = GClick(G(reel, "Choose style"), null);
                List<FloatMenuOption> sopts = GTakeFloatMenu();
                FloatMenuOption other = sopts?.FirstOrDefault(o => !o.Label.Contains("(current)"));
                other?.action?.Invoke();
                Check("Choose style opens a menu of looks and a pick restyles the reel", sopts != null && sopts.Count >= 2 && other != null && GAer.StylePicker.LookOfThing(reel) != look0,
                    res + " options " + (sopts == null ? "none" : string.Join("/", sopts.Select(o => o.Label))) + " look " + look0 + "->" + GAer.StylePicker.LookOfThing(reel));
                // ── reel, dev mode
                Prefs.DevMode = true;
                var l1 = Labels(reel);
                Check("dev mode shows DEV: lay hose instantly", l1.Any(s => s.StartsWith("DEV: lay")), l1);
                res = GClick(G(reel, "DEV: lay"), tgt);
                Check("DEV lay -> targeter -> laid", rc.laid && rc.far == tgt, res + " carry " + rc.carry);
                var l2 = Labels(reel);
                Check("laid: Move hose end, Retract hose, DEV flow shown", l2.Any(s => s.StartsWith("Move hose end")) && l2.Any(s => s.StartsWith("Retract hose")) && l2.Any(s => s.StartsWith("DEV: flow")), l2);
                bool fl0 = rc.debugFlowing; GClick(G(reel, "DEV: flow"), null);
                Check("DEV flow toggle flips the debug provider", rc.debugFlowing != fl0, rc.debugFlowing);
                GClick(G(reel, "DEV: flow"), null);
                IntVec3 tgt2 = new IntVec3(r.minX + 10, 0, r.minZ + 2);
                res = GClick(G(reel, "Move hose end"), tgt2);
                Check("Move hose end -> pending Move at the clicked cell", rc.pending == GHose.HosePendingOrder.Move && rc.pendingAt == tgt2, res + " " + rc.pending + " " + rc.pendingAt);
                res = GClick(G(reel, "Retract hose"), null);
                Check("Retract hose -> pending Retract", rc.pending == GHose.HosePendingOrder.Retract, res + " " + rc.pending);
                GClick(G(reel, "Cancel hose order"), null);
                res = GClick(G(reel, "DEV: reel in"), null);
                Check("DEV reel in -> stored", rc.carry == GHose.HoseCarryState.Stored && !rc.laid, res + " " + rc.carry);
                Prefs.DevMode = false;

                // ── float menu: a selected colonist right-clicks the reel
                Pawn p = GWorker(m);
                if (p != null && p.CanReach(reel, PathEndMode.Touch, Danger.Deadly))
                {
                    Find.Selector.ClearSelection(); Find.Selector.Select(p, false, false);
                    List<FloatMenuOption> fo = FloatMenuMakerMap.GetOptions(new List<Pawn> { p }, reel.TrueCenter(), out FloatMenuContext _);
                    FloatMenuOption carry = fo.FirstOrDefault(o => o.Label.StartsWith("Carry hose out from"));
                    string act = carry == null ? "absent" : carry.Disabled ? "disabled" : "ok";
                    if (carry != null && !carry.Disabled)
                    {
                        carry.action();
                        var tact = TargeterAction?.GetValue(Find.Targeter) as Action<LocalTargetInfo>;
                        Find.Targeter.StopTargeting();
                        tact?.Invoke(new LocalTargetInfo(tgt));
                    }
                    Check("float menu 'Carry hose out from' -> targeter -> pending Deploy and the pawn's forced carry job",
                        carry != null && rc.pending == GHose.HosePendingOrder.Deploy && p.CurJobDef?.defName == "RM_CarryHoseEnd",
                        act + "; options " + string.Join(" / ", fo.Select(o => o.Label).Where(s => s.Contains("hose"))) + "; job " + p.CurJobDef?.defName);
                    rc.CancelOrder(); p.jobs.EndCurrentJob(JobCondition.InterruptForced);
                    if (rc.carry != GHose.HoseCarryState.Stored) rc.ReelIn();
                    // hoses off: no gizmo, no float menu
                    GHose.HoseSettings.enabled = false;
                    List<FloatMenuOption> fo2 = FloatMenuMakerMap.GetOptions(new List<Pawn> { p }, reel.TrueCenter(), out FloatMenuContext _);
                    var loff = Labels(reel);
                    GHose.HoseSettings.enabled = true;
                    Check("hoses disabled: no reel gizmo of ours and no hose float-menu option",
                        !loff.Any(s => s.StartsWith("Deploy hose") || s.StartsWith("Free end")) && !fo2.Any(o => o.Label.Contains("hose")), loff);
                }
                else Check("float menu (skipped: no colonist can reach the reel)", true, "skipped");

                // ── anchors
                Find.Selector.ClearSelection(); Find.Selector.Select(ma, false, false);
                res = GClick(G(ma, "Link wire"), new LocalTargetInfo(mb));
                Check("Link wire -> targeter -> linked both ways", aa.LinkTo(ab) != null && ab.LinkTo(aa) != null, res);
                res = GClick(G(ma, "Unlink wire"), null);
                List<FloatMenuOption> uo = GTakeFloatMenu();
                uo?.FirstOrDefault()?.action?.Invoke();
                Check("Unlink wire -> menu of partners -> unlinked", uo != null && uo.Count == 1 && aa.LinkTo(ab) == null, res + " options " + uo?.Count);
                GAer.CompAerialAnchor.TryLink(aa, mb);
                GClick(G(ma, "Unlink all"), null);
                Check("Unlink all takes every wire down", aa.links.Count == 0 && ab.links.Count == 0, aa.links.Count);
                GAer.CompAerialAnchor.TryLink(aa, mb);
                GAer.CompAerialAnchor.Cut(aa, ab, 0.5f, true);
                bool cutShown = G(ma, "Re-string") != null;
                res = GClick(G(ma, "Re-string"), null);
                Check("cut span: Re-string shown and restores it Up", cutShown && aa.LinkTo(ab)?.state == GAer.SpanState.Up, res + " " + aa.LinkTo(ab)?.state);
                GAer.CompAerialAnchor.Unlink(aa, ab);
                Find.Selector.ClearSelection();
                foreach (Thing t in new[] { ma, mb, mc }) Find.Selector.Select(t, false, false);
                int fired = 0;
                foreach (Thing t in new[] { ma, mb, mc }) { Command g = G(t, "Auto-link"); if (g != null) { g.ProcessInput(null); fired++; } }
                int links = aa.links.Count + ab.links.Count + ac.links.Count;
                Check("Auto-link selected (one ProcessInput per selected, same frame) lays the 2-span tree once", fired == 3 && links == 4, "fired " + fired + " link-ends " + links);
                Find.Selector.ClearSelection();

                // ── build designators' style menus
                foreach (string dn in new[] { "RM_HoseReel", "RM_AerialMast", "PowerConduit" })
                {
                    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                    if (d == null) { Check("designator " + dn + " (def missing)", false); continue; }
                    var des = new Designator_Build(d);
                    des.ProcessInput(null);
                    List<FloatMenuOption> dopts = GTakeFloatMenu();
                    FloatMenuOption pick = dopts?.FirstOrDefault(o => !o.Label.Contains("(current)"));
                    ThingStyleDef before = des.ThingStyleDefNonPreceptSource;
                    pick?.action?.Invoke();
                    ThingStyleDef after = des.ThingStyleDefNonPreceptSource;
                    Check("build " + dn + ": the button opens a look menu and a pick changes the designator's style",
                        dopts != null && dopts.Count >= 2 && pick != null && after != before,
                        (dopts == null ? "no menu" : string.Join("/", dopts.Select(o => o.Label))) + " style " + before?.defName + "->" + after?.defName);
                    Find.DesignatorManager.Deselect();
                }
            }
            finally { Prefs.DevMode = devWas; Find.Selector.ClearSelection(); if (Find.Targeter.IsTargeting) Find.Targeter.StopTargeting(); }

            // ── every settings field: flip, Apply, two frames, restore (red errors are counted by the scene)
            c.Phase("exec");
            var flips = new List<string>();
            foreach (Type st in new[] { typeof(GSS.GimmeSomeSlackSettings), typeof(GHose.HoseSettings), typeof(GAer.AerialSettings) })
            {
                MethodInfo apply = st.GetMethod("Apply", BindingFlags.Public | BindingFlags.Static);
                foreach (FieldInfo f in st.GetFields(BindingFlags.Public | BindingFlags.Static).Where(f => !f.IsLiteral && !f.IsInitOnly))
                {
                    object was = f.GetValue(null), now;
                    if (f.FieldType == typeof(bool)) now = !(bool)was;
                    else if (f.FieldType == typeof(float)) now = (float)was * 0.5f + 0.25f;
                    else if (f.FieldType == typeof(int)) now = Math.Max(1, (int)was / 2);
                    else if (f.FieldType.IsEnum) { Array vals = Enum.GetValues(f.FieldType); now = vals.GetValue((Array.IndexOf(vals, was) + 1) % vals.Length); }
                    else continue;
                    int e0 = c.errors;
                    f.SetValue(null, now);
                    try { apply?.Invoke(null, null); m.GetComponent<GSS.RM_MapComponent_CordGraph>()?.Notify_SettingsChanged(); } catch (Exception ex) { flips.Add(st.Name + "." + f.Name + " Apply threw " + ex.GetType().Name); }
                    foreach (PWait x in GFrames(2)) yield return x;
                    f.SetValue(null, was);
                    try { apply?.Invoke(null, null); m.GetComponent<GSS.RM_MapComponent_CordGraph>()?.Notify_SettingsChanged(); } catch { /* reported above */ }
                    if (c.errors > e0) flips.Add(st.Name + "." + f.Name + " -> " + now + ": " + (c.errors - e0) + " red error(s)");
                }
            }
            foreach (PWait x in GFrames(2)) yield return x;
            Check("every settings field flipped and restored without a red error", flips.Count == 0, flips);

            // ── the settings window, drawn by the game on each tab
            var mod = LoadedModManager.GetMod<GSS.GimmeSomeSlackMod>();
            FieldInfo tabF = typeof(GSS.GimmeSomeSlackMod).GetField("tab", BindingFlags.Static | BindingFlags.NonPublic);
            var tabRows = new List<string>();
            if (mod != null && tabF != null)
            {
                object tab0 = tabF.GetValue(null);
                foreach (object tv in Enum.GetValues(tabF.FieldType))
                {
                    tabF.SetValue(null, tv);
                    int e0 = c.errors;
                    var dlg = new Dialog_ModSettings(mod);
                    Find.WindowStack.Add(dlg);
                    foreach (PWait x in GFrames(4)) yield return x;
                    bool open = Find.WindowStack.IsOpen(dlg);
                    dlg.Close(false);
                    foreach (PWait x in GFrames(1)) yield return x;
                    tabRows.Add(tv + ": " + (open ? "drawn" : "NOT OPEN") + ", " + (c.errors - e0) + " error(s)");
                }
                tabF.SetValue(null, tab0);
            }
            Check("Mod Settings window drawn on every tab with no red error", mod != null && tabF != null && tabRows.All(s => s.Contains("drawn, 0 error")), tabRows);
            c.Phase("observe");
            var failed = checks.Where(x => !(bool)x["ok"]).Select(x => (string)x["check"]).ToList();
            c.ev["passed"] = checks.Count - failed.Count; c.ev["total"] = checks.Count;
            if (failed.Count == 0) c.Pass(checks.Count + "/" + checks.Count + " interface checks passed");
            else c.Defect(failed.Count + "/" + checks.Count + " interface checks failed: " + string.Join("; ", failed));
        }

        // ════════════════════════════════════════════════════════════════ save / reload

        /// <summary>One line per observable GSS fact in the rect: laid cords (key@geometry), hose reels (state, end, trail,
        /// geometry), anchors (each link's partner cell and state, fallen cords).</summary>
        private static List<string> GSnapshot(Map m, CellRect r)
        {
            var o = new List<string>();
            var comp = m.GetComponent<GSS.RM_MapComponent_CordGraph>();
            foreach (GCore.LaidPiece p in comp.Pieces.Where(p => r.Contains(new IntVec3(p.Owner.X, 0, p.Owner.Z))).OrderBy(p => p.Key, StringComparer.Ordinal))
                o.Add("cord " + p.Key + " " + p.GeometryHash().ToString("x16"));
            var hc = m.GetComponent<GHose.RM_MapComponent_Hoses>();
            foreach (Thing t in r.Cells.SelectMany(x => x.GetThingList(m)).Distinct().OrderBy(t => t.thingIDNumber))
            {
                var rc = t.TryGetComp<GHose.CompHoseReel>();
                if (rc != null && t.Position.InBounds(m))
                {
                    var lay = rc.HoseOut ? hc.EnsureLay(rc) : null;
                    o.Add("reel " + t.Position.x + "," + t.Position.z + " carry " + rc.carry + " laid " + rc.laid + " far " + rc.far + " end " + rc.end +
                          " pending " + rc.pending + " trail " + string.Join(";", rc.trail.Select(x => x.x + "," + x.z)) +
                          " geom " + GHose.RM_MapComponent_Hoses.GeometryHash(lay).ToString("x16") + " style " + GAer.StylePicker.LookOfThing(t));
                }
                var a = GAer.CompAerialAnchor.Of(t);
                if (a != null)
                    o.Add("anchor " + t.Position.x + "," + t.Position.z + " links " + string.Join(";", a.links.Select(l => (l.other != null ? l.other.Position.x + "," + l.other.Position.z : "?") + ":" + l.state).OrderBy(s => s, StringComparer.Ordinal)) +
                          " fallen " + a.fallen.Count);
            }
            return o;
        }

        private static string GCheckpointPath(string runId) => Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench", "playtest", runId + ".gss_checkpoint.txt");

        private static IEnumerable<PWait> GScnSaveReloadA(GCtx c)
        {
            c.ev["route"] = "fixture of cords, a laid hose, a hose mid-carry (real colonist), linked and cut spans, a styled reel; GameDataSaveLoader.SaveGame; snapshot written to a checkpoint";
            Map m = c.map;
            if (!GFindRect(c, m.Center + new IntVec3(0, 0, -35), 28, 16, out CellRect r)) { c.Invalid("no clean 28x16 site"); yield break; }
            int z = r.minZ + 3;
            for (int x = r.minX + 2; x <= r.minX + 12; x++) GSpawn(c, "PowerConduit", new IntVec3(x, 0, z));
            Thing bat = GSpawn(c, "Battery", new IntVec3(r.minX + 2, 0, z + 2));
            bat?.TryGetComp<CompPowerBattery>()?.AddEnergy(600f);
            GSpawn(c, "StandingLamp", new IntVec3(r.minX + 9, 0, z - 2));
            Thing reel1 = GSpawn(c, "RM_HoseReel", new IntVec3(r.minX + 16, 0, z + 1));
            Thing reel2 = GSpawn(c, "RM_HoseReel", new IntVec3(r.minX + 16, 0, z + 9));
            Thing m1 = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 3, 0, z + 9)), m2 = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 10, 0, z + 9)), m3 = GSpawn(c, "RM_AerialMast", new IntVec3(r.minX + 10, 0, z + 12));
            if (bat == null || reel1 == null || reel2 == null || m1 == null) { c.Invalid("fixture defs missing"); yield break; }
            var r1 = reel1.TryGetComp<GHose.CompHoseReel>(); var r2 = reel2.TryGetComp<GHose.CompHoseReel>();
            string lw = r1.DevLayInstant(new IntVec3(r.minX + 25, 0, z + 4));
            r1.end = GHose.HoseEnd.Nozzle;
            r1.SetLook(GAer.AerialStyles.Looks.Last());
            GAer.CompAerialAnchor.TryLink(GAer.CompAerialAnchor.Of(m1), m2);
            GAer.CompAerialAnchor.TryLink(GAer.CompAerialAnchor.Of(m2), m3);
            GAer.CompAerialAnchor.Cut(GAer.CompAerialAnchor.Of(m2), GAer.CompAerialAnchor.Of(m3), 0.5f, true);
            Pawn p = GWorker(m);
            string carryNote = "no colonist";
            if (p != null)
            {
                p.workSettings.SetPriority(WorkTypeDefOf.Hauling, 1);
                string why = r2.OrderDeploy(new IntVec3(r.minX + 26, 0, z + 12));
                c.Phase("exec");
                if (why == null) yield return PUntil(() => r2.carry == GHose.HoseCarryState.Carrying && r2.trail.Count >= 4, 5000);
                carryNote = why ?? ("carry " + r2.carry + " trail " + r2.trail.Count);
            }
            foreach (PWait x in GFrames(4)) yield return x;
            c.Phase("observe");
            var s0 = GSnapshot(m, r.ExpandedBy(2).ClipInsideMap(m));
            int ticksAtSave = TicksGameSafe();
            string save = "JBPT_" + c.run.id;
            string path = GenFilePaths.FilePathForSavedGame(save);
            DateTime before = DateTime.UtcNow.AddSeconds(-1);
            GameDataSaveLoader.SaveGame(save);
            if (!(File.Exists(path) && File.GetLastWriteTimeUtc(path) >= before)) { c.Invalid("SaveGame wrote no fresh file at " + path); yield break; }
            var cp = new List<string> { "runId " + c.run.id, "save " + save, "ticksAtSave " + ticksAtSave, "rect " + r.minX + " " + r.minZ + " " + r.Width + " " + r.Height };
            cp.AddRange(s0.Select(l => "s0 " + l));
            File.WriteAllLines(GCheckpointPath(c.run.id), cp.ToArray());
            c.ev["saveName"] = save; c.ev["savePath"] = path; c.ev["ticksAtSave"] = ticksAtSave; c.ev["checkpoint"] = GCheckpointPath(c.run.id);
            c.ev["hoseLay"] = lw; c.ev["midCarry"] = carryNote; c.ev["s0"] = s0; c.ev["resumeRecipe"] = "save_reload_b";
            c.status = "PENDING";
            c.reason = "armed: saved " + save + " at tick " + ticksAtSave + " (" + s0.Count + " lines); verdict owed by save_reload_b (resume=" + c.run.id + ") after loading that save";
        }

        private static IEnumerable<PWait> GScnSaveReloadB(GCtx c)
        {
            c.ev["route"] = "the loaded save's cords, hoses and spans re-derived by the mod after load, compared line by line with the snapshot taken before saving";
            string cpPath = GCheckpointPath(c.run.resume ?? "");
            if (!File.Exists(cpPath)) { c.Invalid("no checkpoint " + cpPath); yield break; }
            string[] cp = File.ReadAllLines(cpPath);
            string Val(string k) => cp.FirstOrDefault(l => l.StartsWith(k + " "))?.Substring(k.Length + 1);
            int ticksAtSave = int.Parse(Val("ticksAtSave"), CultureInfo.InvariantCulture);
            int offset = TicksGameSafe() - ticksAtSave;
            c.ev["loadTickOffset"] = offset;
            if (offset < 0 || offset > 2) { c.Invalid("game at tick " + TicksGameSafe() + ", not within 0-2 ticks of the checkpoint's " + ticksAtSave + " - load " + Val("save") + " first"); yield break; }
            int[] rr = Val("rect").Split(' ').Select(s => int.Parse(s, CultureInfo.InvariantCulture)).ToArray();
            var r = new CellRect(rr[0], rr[1], rr[2], rr[3]);
            foreach (PWait x in GFrames(6)) yield return x;           // let the cord layer rebuild from the loaded map
            var s0 = cp.Where(l => l.StartsWith("s0 ")).Select(l => l.Substring(3)).ToList();
            var l0 = GSnapshot(c.map, r.ExpandedBy(2).ClipInsideMap(c.map));
            var missing = s0.Except(l0).ToList();
            var extra = l0.Except(s0).ToList();
            c.ev["savedLines"] = s0.Count; c.ev["loadedLines"] = l0.Count; c.ev["missingAfterLoad"] = missing.Take(12).ToList(); c.ev["newAfterLoad"] = extra.Take(12).ToList();
            c.ev["fresh"] = GFresh(c.map);
            if (missing.Count == 0 && extra.Count == 0) c.Pass("all " + s0.Count + " cord/hose/span lines identical after the load");
            else c.Defect(missing.Count + " line(s) changed or lost and " + extra.Count + " new after the load (first: " + string.Join(" || ", missing.Take(2)) + " => " + string.Join(" || ", extra.Take(2)) + ")");
        }
    }
}
