// JawaBenchSceneTick.cs - the Verse half of the scene run stepped in the tick, and jawa/scene_slice (TEST profile only).
// Item RIMMANDRAKE_WIRE_COND_RUN_INTO_TICK_BUILT_NEVER_JOINED. Page: design/specs/2026-11-23-bridge-v2/boundary.md. The rules
// are JawaBenchSceneTickCore.cs. The hook is the ONE end-of-tick hook (JawaBenchVitals.TickPre/TickPost on DoSingleTick): no
// second patch on that method.
//
// ENGINE FACTS READ OUT OF DECOMPILED 1.6 VIA RimSage (2026-11-23):
//   TickManager.TickManagerUpdate breaks its loop after a DoSingleTick when Paused is true, so a pause made in the postfix
//   ends the game's own loop on that tick. The setter of CurTimeSpeed drops the write when PlayerCanControl (private) is not
//   accepted: a run is refused then, and the pause is read back.
//   Rand.StateCompressed (private static ulong) = the seed and the iteration count; reading it draws nothing.
using System;
using System.Collections.Generic;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;
using LK = JawaBench.BridgeTools.JawaBenchRunLockCore;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchSceneTick
    {
        internal static volatile T.SceneRun Cur;
        internal static Game RunGame;
        internal static Map RunMap;                 // null: the run has no map of its own
        /// <summary>The step loop that drives the tick now (jawa/run_scenes), or null. Nobody else may arm a run beside it.</summary>
        internal static volatile string StepOwner;
        internal static string LastFault;
        /// <summary>The most ticks that one frame of the run played, and the ticks of the frame it ended in.</summary>
        internal static int MaxFrameTicks, FrameTicks;
        private static int _endFrame = -1, _serial, _frame = -1;
        private static object _epochBox = 0.0;
        private static int _epochOf = int.MinValue;
        private static Func<ulong> _rand;
        private static Action<ulong> _setRand;
        private static MethodInfo _canControl;
        /// <summary>The run_until run that the scene frame steps while the game stays paused (speed Step), or null.</summary>
        internal static volatile T.SceneRun StepRun;
        // budget: not a guard; it shapes the STEP arm like jawa/safe_advance's default frame (40 ms of stepping per frame), so that
        // budget: the per-frame work runs once a slice. The run ends by its own condition or limit.
        internal const double StepFrameMs = 40;

        /// <summary>Write Rand.StateCompressed and read it back. Null when it holds, else why not. Main thread.</summary>
        internal static string WriteRand(ulong v)
        {
            if (_setRand == null)
            {
                var s = AccessTools.PropertySetter(typeof(Rand), "StateCompressed");
                if (s == null) return "the setter of Rand.StateCompressed did not resolve";
                _setRand = (Action<ulong>)Delegate.CreateDelegate(typeof(Action<ulong>), s);
            }
            if (_rand == null) return "Rand.StateCompressed has no reader yet";
            _setRand(v);
            ulong back = _rand();
            return back == v ? null : "wrote " + v + ", read back " + back;
        }

        /// <summary>The tick hook has work for a run.</summary>
        internal static bool Live { get { var r = Cur; return r != null && r.Running; } }

        /// <summary>One boxed epoch, made again only when the epoch changes: the tick path allocates nothing.</summary>
        internal static object EpochBox()
        {
            if (_epochOf != JawaBenchVitals.Epoch) { _epochOf = JawaBenchVitals.Epoch; _epochBox = (double)_epochOf; }
            return _epochBox;
        }

        internal sealed class Host : ISceneHost
        {
            public long Enqueue(string fields) { return W.Enqueue("scene", fields); }
            public bool Drained() { return W.QueueDepth == 0; }
            public bool Pause()
            {
                _endFrame = Time.frameCount;
                if (!SameGame()) return false;
                var tm = Find.TickManager;
                tm.CurTimeSpeed = TimeSpeed.Paused;
                return tm.CurTimeSpeed == TimeSpeed.Paused;
            }
            public long Tick() { return SameGame() ? Find.TickManager.TicksGame : (Cur != null ? Cur.EndTick : -1); }
            public ulong RandState() { return _rand(); }
            public double NowMs() { return W.Clock.Elapsed.TotalMilliseconds; }
            public long? AllocBytes() { return JawaBenchAllocProbe.TrustedBytes(); }
        }

        internal static bool SameGame() { return Current.Game != null && ReferenceEquals(Current.Game, RunGame); }

        /// <summary>Null when a run may start, else why not. Changes nothing.</summary>
        internal static string Refuse(string caller = null)
        {
            if (!JawaBenchVitals.GameReady()) return "no game is playing";
            var adv = JawaBenchSafeAdvance.Cur;
            string held = LK.RefuseArm(Cur?.Id, Cur?.Stage, adv != null && adv.State == "running", StepOwner, caller);
            if (held != null) return held;
            if (!W.Running) return "the disk writer is not running: no trace could be kept";
            if (_rand == null)
            {
                var g = AccessTools.PropertyGetter(typeof(Rand), "StateCompressed");
                if (g == null) return "Rand.StateCompressed did not resolve: the sample phase could not be checked";
                _rand = (Func<ulong>)Delegate.CreateDelegate(typeof(Func<ulong>), g);
            }
            if (_canControl == null) _canControl = AccessTools.PropertyGetter(typeof(TickManager), "PlayerCanControl");
            if (_canControl == null) return "TickManager.PlayerCanControl did not resolve";
            if (!((AcceptanceReport)_canControl.Invoke(Find.TickManager, null)).Accepted) return "the player has no control: the game would drop the pause";
            if (Find.TickManager.ForcePaused) return "the game is force-paused (a window, a load or a cutscene)";
            return null;
        }

        internal static string NewId() { return "s" + DateTime.UtcNow.ToString("yyyyMMddTHHmmss") + "_" + (++_serial); }

        /// <summary>The gate's question, from any thread: the live run's id and its log, or null.</summary>
        internal static T.SceneRun LockHolder() { var r = Cur; return r != null && (r.Running || r.Stage == "settling") ? r : null; }

        /// <summary>The run itself is doing an act on this thread: the lock lets its tool through.</summary>
        [ThreadStatic] internal static int InsideAct;

        /// <summary>Why the run's game or map is not the one that is there, or null.</summary>
        private static string Gone()
        {
            if (!SameGame() || Current.ProgramState != ProgramState.Playing) return "the game was replaced under the run";
            return RunMap != null && !Find.Maps.Contains(RunMap) ? "map " + RunMap.uniqueID + " left the game under the run" : null;
        }

        /// <summary>Arm a run that one of the tools made. Main thread, after Refuse said null.</summary>
        internal static void Take(T.SceneRun run, Map map)
        {
            RunGame = Current.Game;
            RunMap = map;
            LastFault = null;
            MaxFrameTicks = FrameTicks = 0;
            Cur = run;
        }

        /// <summary>A condition run for a step loop (jawa/safe_advance, jawa/run_scenes): compiled, not armed. Null, with why or the
        /// refusal, when it cannot run. Changes nothing. The loop steps the tick; the run says when to stop.</summary>
        internal static T.SceneRun MakeStep(string caller, string until, string record, int maxTicks, double tickBudgetMs, Map map,
                                            out string why, out Dictionary<string, object> refusal)
        {
            refusal = null;
            why = JawaBenchHands.Busy ? "a session is open: its driver runs jawa/run_until" : Refuse(caller);
            if (why == null) why = JawaBenchVitals.EnsureTickHook();
            if (why == null && !(tickBudgetMs >= 0)) why = "tickBudgetMs is less than 0";
            if (why != null) return null;
            try
            {
                var spec = new Dictionary<string, object> { { "until", C.ParseSpec(until) }, { "max_ticks", (double)maxTicks }, { "mapId", (double)map.uniqueID } };
                if (!string.IsNullOrWhiteSpace(record))
                {
                    var probes = C.ParseSpec(record) as Dictionary<string, object>;
                    if (probes == null) { why = "record is a JSON object name -> probe"; return null; }
                    if (probes.Count > 0) spec["sample"] = new Dictionary<string, object> { { "every", 1.0 }, { "probes", probes } };
                }
                var src = JawaBenchTerrainTools.NewProbeSource();
                var c = new C.Compiler(src, "run").CompileSpec(spec);
                return new T.SceneRun(NewId(), c, src, new List<T.Act>(), new Host(), "STEP", caller, null, tickBudgetMs);
            }
            catch (CondRefused e) { refusal = C.Refusal(e); refusal["success"] = false; return null; }
        }

        internal static void ArmStep(T.SceneRun run, Map map)
        {
            Find.TickManager.CurTimeSpeed = TimeSpeed.Paused;
            Take(run, map);
            run.Arm(Find.TickManager.TicksGame, EpochBox());
        }

        /// <summary>From JawaBenchVitals.TickFin: the game's own tick threw, so the postfix did not run and the tick is not whole.</summary>
        internal static void TickThrew(Exception e)
        {
            var r = Cur;
            if (r == null || !r.Running) return;
            string why = "the game's tick threw " + e.GetType().Name + ": " + e.Message;
            try { r.Force("threw", why, SameGame() ? Find.TickManager.TicksGame : r.EndTick); }
            catch (Exception x) { LastFault = why + " | " + x.GetType().Name + ": " + x.Message; }
        }

        /// <summary>From JawaBenchVitals.TickPost, after the tick and after the monitor's own work. `stop` is the safety trigger of
        /// this tick, or null.</summary>
        internal static void TickEnd(bool runOriginal, string stop = null)
        {
            var r = Cur;
            if (r == null || !r.Running) return;
            string gone = Gone();
            if (gone != null) { r.Force("epoch", gone, SameGame() ? Find.TickManager.TicksGame : r.EndTick); return; }
            if (Time.frameCount != _frame) { _frame = Time.frameCount; FrameTicks = 0; }
            if (++FrameTicks > MaxFrameTicks) MaxFrameTicks = FrameTicks;
            try { r.OnTickEnd(Find.TickManager.TicksGame, EpochBox(), runOriginal, stop); }
            catch (Exception e) { Abort(r, "the tick step threw " + e.GetType().Name + ": " + e.Message); }
        }

        private static void Abort(T.SceneRun r, string why)
        {
            LastFault = why;
            try { r.Force("aborted", why, SameGame() ? Find.TickManager.TicksGame : r.EndTick); } catch (Exception e) { LastFault += " | " + e.Message; }
        }

        /// <summary>One slice of a STEP run: the game stays paused; DoSingleTick until the run ends or the slice is spent. The end-of-tick
        /// hook steps the run as in PLAY, and its pause ends the slice.</summary>
        private static void StepFrame(T.SceneRun r)
        {
            var tm = Find.TickManager;
            if (tm.CurTimeSpeed != TimeSpeed.Paused) tm.CurTimeSpeed = TimeSpeed.Paused;
            if (LongEventHandler.AnyEventNowOrWaiting) return;
            var sw = System.Diagnostics.Stopwatch.StartNew();
            while (r.Running && ReferenceEquals(StepRun, r) && sw.Elapsed.TotalMilliseconds < StepFrameMs) tm.DoSingleTick();
        }

        /// <summary>Once a frame (the monitor's driver), armed or not.</summary>
        internal static void Frame()
        {
            FrameRun();
            try { JawaBenchHands.Frame(); } catch (Exception e) { LastFault = "session frame: " + e.GetType().Name + ": " + e.Message; }
        }

        private static void FrameRun()
        {
            var r = Cur;
            if (r == null || r.Stage == "closed") { StepRun = null; return; }
            try
            {
                if (r.Running)
                {
                    string gone = Gone();
                    if (gone != null) { r.Force("epoch", gone, r.EndTick); return; }
                    if (ReferenceEquals(StepRun, r)) StepFrame(r);
                    return;
                }
                if (Time.frameCount == _endFrame) return;      // the tick count is read after the ending frame is over
                r.Settle();
            }
            catch (Exception e) { LastFault = "frame: " + e.GetType().Name + ": " + e.Message; }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/scene_slice",
            Description =
                "The first scene of BRIDGE v2.0, stepped in the game's OWN loop (PLAY): it samples one pawn after every tick, does one " +
                "damage act on a named tick, tests one end condition (a jawa/cond_eval tree) after every tick and pauses the game ON the " +
                "tick where it turns true. Tracks: `field` (the field path you give), `hediffs`, `dead`, `downed`, `job`, plus `tracks` (a JSON " +
                "object of probes). The trace is written as kind `scene` lines of the JawaBench record (schema scene_trace_v1, " +
                "design/specs/2026-11-23-bridge-v2/boundary.md). It JUDGES NOTHING. action=start arms and lets the game run and returns at " +
                "once; action=status reads; action=cancel ends it. Refuses when another run is live, when the player has no control, when a " +
                "window force-pauses the game, and when a name in the condition does not resolve. HURTS THE PAWN when actAt is set: scratch " +
                "maps only. TEST profile only.",
            ResultDescription =
                "success, run, stage (running | settling | closed), state, hitTick, endTick, rows, dropped, paused, ticksGame, speed, " +
                "recordDir, session (the trace is in recordDir/tps_*_<session>_*.jsonl), result (the condition run), lastFault, maxFrameTicks, endFrameTicks (ticks played in one frame). A refused " +
                "condition: refused, at, detail.")]
        public static async Task<object> SceneTickSlice(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "start, status or cancel.")] string action = "status",
            [ToolParameter(Description = "start: the pawn (id, thing id or name).")] string pawn = null,
            [ToolParameter(Description = "start: the end condition as a JSON condition node.")] string until = null,
            [ToolParameter(Description = "start: the tick limit, 1 to 60000.")] int maxTicks = 2500,
            [ToolParameter(Description = "start: ticks after the start on which the damage act is done; 0 = no act.")] int actAt = 0,
            [ToolParameter(Description = "start: the damage amount of the act.")] float damage = 8f,
            [ToolParameter(Description = "start: a field path on the pawn, for the track `field`.")] string path = "positionInt.x",
            [ToolParameter(Description = "start: more tracks, a JSON object name -> probe.")] string tracks = null,
            [ToolParameter(Description = "start: Normal, Fast, Superfast or Ultrafast.")] string speed = "Normal")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string a = (action ?? "").Trim().ToLowerInvariant();
                if (a == "status") return SceneTickStatus();
                if (a == "cancel")
                {
                    if (JawaBenchHands.Busy) return Fail("a session is open: its driver runs jawa/run_until");
                    var r = JawaBenchSceneTick.Cur;
                    if (r == null || !r.Running) return Fail("no run is live");
                    r.Force("cancelled", "cancelled by a call", TicksGameSafe());
                    return SceneTickStatus();
                }
                if (a != "start") return Fail("action is start, status or cancel, not '" + action + "'");
                if (JawaBenchHands.Busy) return Fail("a session is open: its driver runs jawa/run_until");
                string why = JawaBenchSceneTick.Refuse();
                if (why != null) return Fail(why);
                TimeSpeed sp;
                if (!Enum.TryParse(speed, true, out sp) || sp == TimeSpeed.Paused) return Fail("speed is Normal, Fast, Superfast or Ultrafast, not '" + speed + "'");
                string err;
                var p = FindPawn(pawn, out err);
                if (p == null || !p.Spawned) return Fail(p == null ? err : "the pawn is not spawned");
                if (string.IsNullOrWhiteSpace(until)) return Fail("Give until (a JSON condition node).");
                string install = JawaBenchVitals.EnsureTickHook();
                if (install != null) return Fail("the end-of-tick hook is not on: " + install);
                var host = new JawaBenchSceneTick.Host();
                T.SceneRun run;
                try
                {
                    var pid = p.ThingID;
                    Dictionary<string, object> Probe(string name, string k, string v, string k2 = null, string v2 = null)
                    {
                        var d = new Dictionary<string, object> { { "p", name }, { k, v } };
                        if (k2 != null) d[k2] = v2;
                        return d;
                    }
                    var probes = new Dictionary<string, object>
                    {
                        { "field", Probe("thing.field", "thing", pid, "path", path) },
                        { "hediffs", Probe("thing.field", "thing", pid, "path", "health.hediffSet.hediffs._size") },
                        { "dead", Probe("pawn.state", "pawn", pid, "f", "dead") },
                        { "downed", Probe("pawn.state", "pawn", pid, "f", "downed") },
                        { "job", Probe("pawn.job", "pawn", pid, "f", "def") },
                    };
                    if (!string.IsNullOrWhiteSpace(tracks))
                    {
                        var more = C.ParseSpec(tracks) as Dictionary<string, object>;
                        if (more == null) return Fail("tracks is a JSON object name -> probe");
                        foreach (var kv in more) probes[kv.Key] = kv.Value;
                    }
                    if (maxTicks < 1 || maxTicks > 60000) return Fail("maxTicks is 1 to 60000");
                    var spec = new Dictionary<string, object>
                    {
                        { "until", C.ParseSpec(until) }, { "max_ticks", (double)maxTicks }, { "mapId", (double)p.Map.uniqueID },
                        { "sample", new Dictionary<string, object> { { "every", 1.0 }, { "probes", probes } } },
                    };
                    var acts = new List<T.Act>();
                    if (actAt > 0)
                        acts.Add(new T.Act("damage", actAt, () =>
                        {
                            if (p.Dead || p.Destroyed) throw new InvalidOperationException("the pawn is gone");
                            var res = p.TakeDamage(new DamageInfo(DamageDefOf.Cut, damage, 999f, -1f, null, p.RaceProps.body.corePart));
                            return "Cut " + damage + " asked, " + res.totalDamageDealt + " dealt to " + p.ThingID;
                        }));
                    why = T.RefuseActs(acts, maxTicks);
                    if (why != null) return Fail(why);
                    var src = NewProbeSource();
                    var c = new C.Compiler(src, "run").CompileSpec(spec);
                    run = new T.SceneRun(JawaBenchSceneTick.NewId(), c, src, acts, host, "PLAY", sp.ToString());
                }
                catch (CondRefused e) { var f = C.Refusal(e); f["success"] = false; return f; }
                var tm = Find.TickManager;
                tm.CurTimeSpeed = TimeSpeed.Paused;
                if (tm.CurTimeSpeed != TimeSpeed.Paused) return Fail("the pause did not hold");
                JawaBenchSceneTick.Take(run, p.Map);
                run.Arm(tm.TicksGame, JawaBenchSceneTick.EpochBox());
                if (run.Running) tm.CurTimeSpeed = sp;
                return SceneTickStatus();
            }, cancellationToken);
        }

        private static object SceneTickStatus()
        {
            var r = JawaBenchSceneTick.Cur;
            var tm = Current.Game != null ? Find.TickManager : null;
            return new Dictionary<string, object>
            {
                { "success", r != null }, { "run", r?.Id }, { "stage", r?.Stage ?? "none" }, { "state", r?.State }, { "why", r?.Why },
                { "hitTick", r?.HitTick }, { "endTick", r?.EndTick }, { "rows", r?.Rows }, { "dropped", r?.Dropped },
                { "paused", tm != null && tm.CurTimeSpeed == TimeSpeed.Paused }, { "speed", tm?.CurTimeSpeed.ToString() },
                { "ticksGame", TicksGameSafe() }, { "recordDir", W.Dir }, { "session", W.Session },
                { "lockReads", r?.Lock.Reads }, { "breaches", r?.Lock.Breaches() }, { "costliest", r?.Costliest() },
                { "result", r?.Result() }, { "lastFault", JawaBenchSceneTick.LastFault }, { "maxFrameTicks", JawaBenchSceneTick.MaxFrameTicks }, { "endFrameTicks", JawaBenchSceneTick.FrameTicks },
            };
        }
    }
}
