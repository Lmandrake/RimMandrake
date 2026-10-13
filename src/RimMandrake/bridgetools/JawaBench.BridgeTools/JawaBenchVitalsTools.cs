// JawaBenchVitalsTools.cs - the test-state monitor's tools (TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO):
// the vitals control/read tool and the safe advance stepper. Verse half: JawaBenchVitals.cs; pure rules: JawaBenchVitalsCore.cs.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using SA = JawaBench.BridgeTools.JawaBenchSafeAdvance;
using V = JawaBench.BridgeTools.JawaBenchVitalsCore;
using VT = JawaBench.BridgeTools.JawaBenchVitals;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/vitals",
            Description =
                "Test-state monitor: every spawned pawn's vitals over time (alive/downed/health/bleeding/mood vs its own break " +
                "threshold/mental state/hostility; deaths kept as tombstones that outlive the corpse), hostile structures " +
                "(turrets, spawners, dormant), a clock ledger (processed ticks vs TicksGame: a reassignment is a discontinuity, " +
                "seen while paused too), blocking windows with age, new letters incl. GameEnded (colony loss), required actors " +
                "and specimens, and a coverage heartbeat. Rows go to the TPS record as kind 'vitals'. " +
                "action=arm (ttlMin, critical=pawn ids, specimens=thing ids, row, timeException, budgetTicks) | disarm | status " +
                "(default) | events (sinceSeq) | sample (census now, returns every pawn). The first arm installs a DoSingleTick " +
                "prefix+postfix; a channel that is switched off or never ran reports UNMEASURED, never 0. ABSENCE IS NOT DEATH: " +
                "a pawn that leaves the spawned set is 'departed'; only the Kill hook writes a death.",
            ResultDescription =
                "success, armed, row, ttlLeftS, critical, specimens, latched{first, count, seq}, clock{processed, discontinuities, " +
                "declared}, rollup, threats, modalMaxAgeS, gameEnding, channels{on, calls, cost, meanUs}, hooks, driver, counters; " +
                "events: triggers[], tombs[]; sample: pawns[].")]
        public static async Task<object> Vitals(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "status | arm | disarm | events | sample", DefaultValue = "status")] string action = "status",
            [ToolParameter(Description = "arm: minutes until the monitor disarms itself (default 30, max 240)", DefaultValue = 30.0)] double ttlMin = 30,
            [ToolParameter(Description = "arm: comma list of REQUIRED actor pawn ids (ThingID like Human123 or the number). Without any, every colonist counts.", DefaultValue = null)] string critical = null,
            [ToolParameter(Description = "arm: comma list of specimen thing ids whose loss damages the test", DefaultValue = null)] string specimens = null,
            [ToolParameter(Description = "arm: the row/test name (rides on every row)", DefaultValue = null)] string row = null,
            [ToolParameter(Description = "arm: the row DECLARES a time exception (long advances, clock reassignment allowed and recorded as declared)", DefaultValue = false)] bool timeException = false,
            [ToolParameter(Description = "arm: the row's advance budget in ticks per safe_advance call on a populated map (0 = default 30000)", DefaultValue = 0L)] long budgetTicks = 0,
            [ToolParameter(Description = "arm/disarm: who and why", DefaultValue = null)] string why = null,
            [ToolParameter(Description = "events: return triggers with seq above this", DefaultValue = 0L)] long sinceSeq = 0,
            [ToolParameter(Description = "events/sample: max rows", DefaultValue = 200)] int limit = 200)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                string a = (action ?? "status").Trim().ToLowerInvariant();
                if (a == "arm")
                {
                    if (Current.Game == null || Find.TickManager == null) return Fail("No game loaded.");
                    var crit = V.ParseIds(critical, out var bad1);
                    if (bad1 != null) return Fail("critical: '" + bad1 + "' is not a pawn id");
                    var spec = V.ParseIds(specimens, out var bad2);
                    if (bad2 != null) return Fail("specimens: '" + bad2 + "' is not a thing id");
                    var missing = new List<int>();
                    var spawnedIds = new HashSet<int>();
                    foreach (var m in Find.Maps) foreach (var p in m.mapPawns.AllPawnsSpawned) spawnedIds.Add(p.thingIDNumber);
                    foreach (var c in crit) if (!spawnedIds.Contains(c)) missing.Add(c);
                    if (missing.Count > 0) return Fail("critical actor(s) not spawned on any map: " + string.Join(",", missing) + " - a required actor that is not there cannot be watched");
                    VT.Arm(ttlMin, "jawa/vitals", why, row, crit, spec, timeException, budgetTicks);
                    if (VT.SpecimensUnresolved.Count > 0)
                        return Fail("specimen id(s) not found on any map: " + string.Join(",", VT.SpecimensUnresolved) + " (the monitor IS armed; the rest are watched)", Status());
                }
                else if (a == "disarm") VT.Disarm(why ?? "jawa/vitals disarm");
                else if (a == "events")
                {
                    var trig = VT.Latch.Since(sinceSeq);
                    int skip = Math.Max(0, trig.Count - Math.Max(1, limit));
                    return new
                    {
                        success = true, armed = VT.Armed, seq = VT.Latch.Seq, overflow = VT.Latch.Overflow, first = Json(VT.Latch.First),
                        triggers = TrigList(trig, skip, trig.Count), truncated = skip,
                        tombs = new List<string>(VT.Tombs), ticksGame = TicksGameSafe(),
                    };
                }
                else if (a == "sample")
                {
                    if (!VT.Armed) return Fail("not armed: arm first (a sample outside an armed window has no history to diff against)");
                    VT.Sample("tool");
                    var ps = VT.Census();
                    return new
                    {
                        success = true, rollup = VT.LastRollup?.Fields(), count = ps.Count,
                        pawns = PawnList(ps, Math.Max(1, limit)), truncated = Math.Max(0, ps.Count - limit),
                        threats = new { structures = VT.ThreatTotal, turrets = VT.ThreatTurrets, spawners = VT.ThreatSpawners, dormant = VT.ThreatDormant },
                        ticksGame = TicksGameSafe(),
                    };
                }
                else if (a != "status") return Fail("action must be status, arm, disarm, events or sample");
                return Status();
            });
        }

        // Explicit loops: written while JawaBenchTerrainTools' shared <>c (every NON-capturing lambda of every file) held
        // GimmeSomeSlack-typed fields and failed to load without GSS (measured live 2026-10-13). Root fixed since: GSS-typed
        // lambdas live in GssLambdaHome and build.py's closure_scan refuses any that return, so static lambdas are safe here.
        private static List<object> TrigList(List<V.Trigger> ts, int from, int to)
        {
            var r = new List<object>();
            for (int i = from; i < to && i < ts.Count; i++) r.Add(Json(ts[i]));
            return r;
        }

        private static List<object> PawnList(List<V.PawnObs> ps, int n)
        {
            var r = new List<object>();
            for (int i = 0; i < n && i < ps.Count; i++) r.Add(ps[i].Json());
            return r;
        }

        private static object Json(V.Trigger t) => t == null ? null : new
        {
            seq = t.Seq, kind = t.Kind, severity = t.Severity, tick = t.Tick, map = t.Map, subjectId = t.SubjectId, subject = t.Subject,
            critical = t.Critical, declared = t.Declared, detail = t.Detail,
        };

        private static object Status()
        {
            bool game = Current.Game != null && Find.TickManager != null;
            return new
            {
                success = true, armed = VT.Armed, row = VT.Row, by = VT.By, why = VT.Why, armedUtc = VT.ArmedUtc, lastDisarm = VT.LastDisarm,
                ttlLeftS = Math.Round(VT.TtlLeft, 0), timeException = VT.TimeException, budgetTicks = VT.Budget,
                critical = VT.Critical.ToList(), specimens = VT.Specimens.Keys.ToList(), specimensUnresolved = VT.SpecimensUnresolved.ToList(),
                latched = new { first = Json(VT.Latch.First), count = VT.Latch.Count, seq = VT.Latch.Seq, overflow = VT.Latch.Overflow },
                clock = new { processed = VT.Clock.Processed, discontinuities = VT.Clock.Discontinuities, declared = VT.Clock.Declared },
                rollup = VT.LastRollup?.Fields(), lastSampleTick = VT.LastSampleTick, samples = VT.Samples,
                threats = new { structures = VT.ThreatTotal < 0 ? (int?)null : VT.ThreatTotal, turrets = VT.ThreatTurrets, spawners = VT.ThreatSpawners, dormant = VT.ThreatDormant },
                modalMaxAgeS = Math.Round(VT.Modals.MaxAge(VT.Mono), 1), gameEnding = game && Find.GameEnder != null && Find.GameEnder.gameEnding,
                populated = game && VT.Populated(), epoch = VT.Epoch,
                channels = VT.ChannelStatus(), hooks = VT.HookStatus, hookDetail = VT.HookDetail, driver = VT.DriverStatus,
                rows = new { written = VT.RowsWritten, dropped = VT.RowsDropped, writerRunning = JawaBenchTpsWriter.Running },
                faults = VT.Faults, lastFault = VT.LastFault, tickHookCalls = VT.TickHookCalls,
                advance = AdvanceJson(SA.Cur), ticksGame = TicksGameSafe(), paused = game && Find.TickManager.Paused,
            };
        }

        private static object AdvanceJson(SA.Run r) => r == null ? null : new
        {
            state = r.State, requested = r.Requested, executed = r.Executed, tickFrom = r.StartTick, tickTo = r.EndTick,
            stopBy = Json(r.StopBy), abortWhy = r.AbortWhy, timeException = r.TimeException, frames = r.Frames,
            wallS = Math.Round((r.State == "running" ? VT.Mono : r.EndMono) - r.StartMono, 2),
        };

        [Tool(
            "jawa/safe_advance",
            Description =
                "Advance ordinary simulation by N ticks, safely: game paused, DoSingleTick in chunks of <= 60 inside a per-frame " +
                "wall budget, and after EVERY chunk the monitor's latch is checked - a death, a downed/hurt/starving required actor, " +
                "a colonist turned hostile, a new hostile pawn or structure, a stuck modal, colony loss, a lost specimen or an " +
                "undeclared clock discontinuity STOPS the advance locally (stopOn narrows the list). REFUSED BEFORE ANY TICK: more " +
                "than budgetTicks (default 30000, or the armed row's budget) on a populated map without timeException=true, and " +
                "anything above 1,200,000 ticks. Arms the monitor if it is not armed. action=start (default, waits up to timeoutMs) " +
                "| cancel | status. Never reassigns the clock: for a time of day, prepare the fixture before pawns exist. A return to " +
                "the main menu, a load or new game ends the run as aborted with abortWhy 'game_changed: ...'; the start map leaving " +
                "Find.Maps ends it with 'map_gone: ...'; tickTo is then the last tick the run stepped.",
            ResultDescription =
                "success, state (done | stopped | cancelled | aborted | refused | running), requested, executed, tickFrom, tickTo, " +
                "stopBy{kind, severity, detail}, triggers[] since start, refused (reason), wallS.")]
        public static async Task<object> SafeAdvance(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "start | cancel | status", DefaultValue = "start")] string action = "start",
            [ToolParameter(Description = "ticks to advance", DefaultValue = 0L)] long ticks = 0,
            [ToolParameter(Description = "per-call budget on a populated map (0 = the armed row's budget, else 30000)", DefaultValue = 0L)] long budgetTicks = 0,
            [ToolParameter(Description = "the row declares a time exception (owner 2026-10-13: long runs only when clearly worth it)", DefaultValue = false)] bool timeException = false,
            [ToolParameter(Description = "comma list of trigger kinds that stop the advance, or 'default'", DefaultValue = "default")] string stopOn = "default",
            [ToolParameter(Description = "ticks per chunk (1..60)", DefaultValue = 60)] int chunk = 60,
            [ToolParameter(Description = "main-thread ms per frame spent stepping", DefaultValue = 40.0)] double frameBudgetMs = 40,
            [ToolParameter(Description = "start: ms to wait for completion before returning state=running", DefaultValue = 300000)] int timeoutMs = 300000)
        {
            string a = (action ?? "start").Trim().ToLowerInvariant();
            if (a == "cancel") { SA.CancelRequested = true; }
            if (a == "cancel" || a == "status")
            {
                if (a == "cancel") await Task.Delay(200, cancellationToken).ConfigureAwait(false);
                string act = a;     // captured on purpose: a NON-capturing lambda lands in the partial class's shared <>c, which fails to load when an optional mod's types (GSS) are absent
                return await ctx.MainThread.InvokeAsync<object>(() => new { success = act != null, advance = AdvanceJson(SA.Cur), ticksGame = TicksGameSafe() });
            }
            if (a != "start") return Fail("action must be start, cancel or status");
            if (timeoutMs < 0) return Fail("timeoutMs must be >= 0 (0 = start and return at once; poll action=status)");
            object err = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null || Find.TickManager == null || Find.CurrentMap == null) return Fail("No game/map loaded.");
                if (SA.Cur != null && SA.Cur.State == "running") return Fail("an advance is already running (action=status / cancel)");
                if (chunk < 1 || chunk > V.MaxChunk) return Fail("chunk must be 1.." + V.MaxChunk);
                var kinds = V.ParseKinds(stopOn, out var badK);
                if (badK != null) return Fail("stopOn: unknown kind '" + badK + "'", new { kinds = V.DefaultStopKinds });
                bool pop = VT.Populated();
                long budget = budgetTicks > 0 ? budgetTicks : (VT.Armed && VT.Budget > 0 ? VT.Budget : V.DefaultAdvanceBudget);
                bool exc = timeException || (VT.Armed && VT.TimeException);
                string refuse = V.AdvanceRefusal(ticks, budget, pop, exc);
                if (refuse != null)
                {
                    if (VT.Armed) VT.Emit(V.ChClock, "advance", "\"state\":\"refused\",\"requested\":" + ticks + ",\"budget\":" + budget + ",\"populated\":" + V.B(pop) + ",\"why\":" + V.J(refuse));
                    return new { success = false, state = "refused", refused = refuse, requested = ticks, budget, populated = pop, timeException = exc,
                                 ticksGame = TicksGameSafe() };
                }
                bool armedHere = false;
                if (!VT.Armed) { VT.Arm(60, "jawa/safe_advance", "auto-armed by safe_advance", null, new List<int>(), new List<int>(), false, 0); armedHere = true; }
                SA.CancelRequested = false;
                var tm = Find.TickManager;
                SA.Cur = new SA.Run
                {
                    Requested = ticks, Chunk = chunk, FrameBudgetMs = Math.Max(5, Math.Min(200, frameBudgetMs)), Stop = kinds,
                    StartSeq = VT.Latch.Seq, StartTick = tm.TicksGame, EndTick = tm.TicksGame, StartMono = VT.Mono, MaxWallS = Math.Max(60, timeoutMs / 1000.0 * 4),
                    TimeException = exc, PrevSpeed = tm.CurTimeSpeed,
                    Game = Current.Game, Map = Find.CurrentMap, MapId = Find.CurrentMap.uniqueID,
                };
                tm.CurTimeSpeed = TimeSpeed.Paused;
                VT.Emit(V.ChClock, "advance", "\"state\":\"start\",\"requested\":" + ticks + ",\"budget\":" + budget + ",\"populated\":" + V.B(pop) +
                                              ",\"timeException\":" + V.B(exc) + ",\"autoArmed\":" + V.B(armedHere));
                return null;
            });
            if (err != null) return err;
            var sw = System.Diagnostics.Stopwatch.StartNew();
            while (SA.Cur.State == "running" && sw.ElapsedMilliseconds < timeoutMs)
                await Task.Delay(100, cancellationToken).ConfigureAwait(false);
            int waited = timeoutMs;     // captured on purpose (see above)
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var r = SA.Cur;
                if (waited < 0) return null;
                var trig = VT.Latch.Since(r.StartSeq);
                return new
                {
                    success = r.State == "done", state = r.State, requested = r.Requested, executed = r.Executed, tickFrom = r.StartTick,
                    tickTo = r.State == "running" ? TicksGameSafe() : r.EndTick, stopBy = Json(r.StopBy), abortWhy = r.AbortWhy,
                    triggers = TrigList(trig, 0, Math.Min(40, trig.Count)), triggersTotal = trig.Count,
                    wallS = Math.Round((r.State == "running" ? VT.Mono : r.EndMono) - r.StartMono, 2), frames = r.Frames,
                    note = r.State == "running" ? "still running after timeoutMs: poll action=status or cancel" : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
