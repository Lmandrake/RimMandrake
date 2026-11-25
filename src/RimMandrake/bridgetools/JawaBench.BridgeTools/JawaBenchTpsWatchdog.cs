// JawaBenchTpsWatchdog.cs - main-thread heartbeat, last phase, and a thread that writes down SILENCE
// (BRIDGE_TPS_CAPTURE_FIXES_1, item 2).
//
// The main thread stamps a heartbeat every frame (Root.Update postfix, menu and play alike) and keeps a
// small stack of coarse PHASES (update, long event, save, tick update, tick-list category, world, map
// pre/post, components, frame-rest = the rest of the frame: non-tick play update, GUI, rendering). A background thread wakes every second:
//   * main thread silent > SilenceSeconds -> a `silence` line (silentS, the phase it was in and since
//     when, ticks, speed, heap, GC count, writer health), repeated every SilenceRepeatSeconds while it
//     lasts - so a permanent hang leaves a record that ENDS at the last heartbeat and says where;
//   * silence ends -> a `resumed` line;
//   * every 5 s -> hb_<session>.json (overwritten): pid, session, now, last heartbeat, phase, writer
//     health. belt_watchdog reads it from WSL as the EXTERNAL observer: if hb_ stops changing, this thread
//     is not running either (process dead, or a stop-the-world GC / native hang that suspends managed
//     threads), which only something outside the process can see.
// Silence means "no observed main-thread progress", never proven deadlock.
//
// ⛔ The watchdog thread touches no Verse/Unity API: everything it reports was cached by the main thread.

using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsWatchdog
    {
        internal static readonly string[] PhaseNames =
        {
            "none", "update", "longEvent", "save", "load", "tickUpdate", "tick", "tl:Normal", "tl:Rare", "tl:Long",
            "world", "worldPost", "mapPre", "mapPost", "mapComp", "gameComp", "frame-rest", "menu",
        };
        internal const int PNone = 0, PUpdate = 1, PLongEvent = 2, PSave = 3, PLoad = 4, PTickUpdate = 5, PTick = 6,
            PTlNormal = 7, PTlRare = 8, PTlLong = 9, PWorld = 10, PWorldPost = 11, PMapPre = 12, PMapPost = 13,
            PMapComp = 14, PGameComp = 15, PGuiRender = 16, PMenu = 17;

        // ---- written by the main thread, read by the watchdog thread --------------------------------
        private static long _beatTicks;           // Stopwatch ticks of the last heartbeat (Interlocked)
        private static volatile int _phase;
        private static long _phaseSinceTicks;
        private static volatile int _ticksGame;
        internal static int LastTicksGame => _ticksGame;
        // SHOULD 6: the main thread caches NUMBERS every frame (no per-frame string formatting); the watchdog
        // thread formats them only when it writes a row.
        private static long _multBits = BitConverter.DoubleToInt64Bits(double.NaN);
        private static volatile int _speed = -1;
        private static readonly string[] SpeedNames = { "Paused", "Normal", "Fast", "Superfast", "Ultrafast" };   // Verse.TimeSpeed 0..4
        private static volatile string _scene = "";
        private static long _sceneSinceTicks, _lastTickChange = -1, _frameResult, _frameFaultSince;
        [ThreadStatic] private static bool _rootException;

        internal static void NoteRootException(string text)
        {
            // Verse catches this inside Root.Update (FlowWorks ee0fbaa8); the finalizer sees a normal return.
            if (text != null && text.StartsWith("Root level exception in Update():", StringComparison.Ordinal))
                _rootException = true;
        }

        internal static void SetScene(string scene)
        {
            if (_scene == scene) return;
            Interlocked.Exchange(ref _sceneSinceTicks, W.Clock.ElapsedTicks);
            _scene = scene;
        }

        internal static void FrameEnded(bool threw)
        {
            // Pack count and streak so the watchdog cannot read them from different frames.
            long previous = Interlocked.Read(ref _frameResult);
            uint frames = (uint)(previous >> 32) + 1;
            uint streak = threw || _rootException ? (uint)previous + 1 : 0;
            if (streak == 1) Interlocked.Exchange(ref _frameFaultSince, W.Clock.ElapsedTicks);
            Interlocked.Exchange(ref _frameResult, ((long)frames << 32) | streak);
        }

        internal static void SetFrameState(bool paused, double mult, int speed, int ticksGame)
        {
            LastPaused = paused;
            Interlocked.Exchange(ref _multBits, BitConverter.DoubleToInt64Bits(mult));
            _speed = speed;
            NoteTicks(ticksGame);
        }

        /// <summary>The one writer of the tick count. A second writer hid every tick: the frame's postfix wrote the count
        /// before the next prefix compared it, so lastTickMono never moved on a ticking game (live, 2026-11-24).</summary>
        internal static void NoteTicks(int ticksGame)
        {
            if (_ticksGame != ticksGame) Interlocked.Exchange(ref _lastTickChange, W.Clock.ElapsedTicks);
            _ticksGame = ticksGame;
        }

        internal static string LastSpeed { get { int sp = _speed; return sp >= 0 && sp < SpeedNames.Length ? SpeedNames[sp] : sp < 0 ? "" : sp.ToString(); } }
        internal static string LastMultJson => M.F(BitConverter.Int64BitsToDouble(Interlocked.Read(ref _multBits)), 2);
        internal static volatile bool LastPaused, LastFocused = true, LastLongEvent;
        internal static volatile string LastSave = "";
        /// <summary>The phase the watchdog saw while the main thread was quiet > 1.5 s; read+cleared by the
        /// main thread when it writes the recovered-stall incident (covers 2-10 s stalls, below SilenceSeconds).</summary>
        internal static string QuietPhase;

        private static readonly int[] Stack = new int[32];
        private static int _depth;

        private static Thread _thread;
        internal static string HeartbeatPath;
        internal static long SilenceLines;

        internal static double Now => W.Clock.Elapsed.TotalSeconds;

        /// <summary>Main thread, once per frame (start of Root.Update).</summary>
        internal static void Beat()
        {
            Interlocked.Exchange(ref _beatTicks, W.Clock.ElapsedTicks);
            _rootException = false;
            _depth = 0;                       // a phase left open by an exception never outlives its frame
            Set(PUpdate);
        }

        internal static void Set(int p)
        {
            _phase = p;
            Interlocked.Exchange(ref _phaseSinceTicks, W.Clock.ElapsedTicks);
        }

        /// <summary>Enter a nested phase (main thread). Pair with Exit in the same patch's postfix.</summary>
        internal static void Enter(int p)
        {
            if (_depth < Stack.Length) Stack[_depth] = _phase;
            _depth++;
            Set(p);
        }

        internal static void Exit()
        {
            if (_depth > 0) _depth--;
            Set(_depth < Stack.Length ? Stack[_depth] : PUpdate);
        }

        internal static string PhaseName => PhaseNames[Math.Max(0, Math.Min(PhaseNames.Length - 1, _phase))];

        private static string NameOf(int p) => PhaseNames[Math.Max(0, Math.Min(PhaseNames.Length - 1, p))];

        /// <summary>BRIDGE_STALL_DIAGNOSTIC_1: the whole nested phase stack, outermost first, the current phase last, as a
        /// JSON array. A racy read from the watchdog thread - harmless while the main thread is the one that is stuck.</summary>
        internal static string PhaseStackJson()
        {
            int d = Math.Min(_depth, Stack.Length);
            var sb = new StringBuilder(64).Append('[');
            for (int i = 0; i < d; i++) sb.Append('"').Append(NameOf(Stack[i])).Append("\",");
            return sb.Append('"').Append(PhaseName).Append("\"]").ToString();
        }

        /// <summary>Test seam: lay a phase stack as the main thread would (Beat, then nested Enters).</summary>
        internal static void SetPhasesForTest(params int[] nested)
        {
            _depth = 0;
            Set(PUpdate);
            foreach (int p in nested) Enter(p);
        }

        internal static void Start(string dir)
        {
            if (_thread != null) return;
            ProcessStartUtc();
            HeartbeatPath = Path.Combine(dir, "hb_" + W.Session + ".json");
            Interlocked.Exchange(ref _beatTicks, W.Clock.ElapsedTicks);
            JawaBenchStallDump.CaptureMainThread();
            WarmOnCaller();
            _thread = new Thread(Loop) { IsBackground = true, Name = "JawaBench.TpsWatchdog" };
            _thread.Start();
        }

        /// <summary>JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT: the watchdog starts at bridge-registration, while the
        /// installing (main) thread goes on Harmony-patching, and a background thread JIT-compiling at that moment is the
        /// 2026-10-26 archive crash's hazard class. So everything Loop runs is compiled HERE first: two real heartbeat
        /// writes (the first publishes by Move, the second by Replace), the silence row's context and the stall dump; Loop's
        /// own small body still compiles on the thread (PrepareMethod is a no-op on Unity's Mono).
        /// The watchdog is not deferred - startup is exactly when a silent main thread must be seen. Never throws.</summary>
        private static void WarmOnCaller()
        {
            try
            {
                double now = Now;
                double quiet = now - Seconds(Interlocked.Read(ref _beatTicks));
                WriteHeartbeat(now, quiet);
                WriteHeartbeat(Now, quiet);
                var unused = ContextFields() + PhaseName + M.F(quiet, 1) + PhaseStackJson();
            }
            catch { }
            // the stall dump runs on this thread only after a minute of silence: run its whole path once HERE, on the main
            // thread (RuntimeHelpers.PrepareMethod, used below for Loop, is a no-op on Unity's Mono: only running code compiles)
            JawaBenchStallDump.Warm(Path.GetDirectoryName(HeartbeatPath));
            try
            {
                var loop = typeof(JawaBenchTpsWatchdog).GetMethod(nameof(Loop), System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic);
                if (loop != null) System.Runtime.CompilerServices.RuntimeHelpers.PrepareMethod(loop.MethodHandle);
            }
            catch { }
        }

        private static double Seconds(long ticks) => (double)ticks / Stopwatch.Frequency;

        /// <summary>The incident context the watchdog can give without touching Unity (fields, no braces).</summary>
        internal static string ContextFields()
        {
            double now = Now;
            return "\"phase\":\"" + PhaseName + "\",\"phaseS\":" + M.F(now - Seconds(Interlocked.Read(ref _phaseSinceTicks)), 3) +
                   ",\"ticksGame\":" + LastTicksGame + ",\"speed\":\"" + LastSpeed + "\",\"mult\":" + LastMultJson +
                   ",\"paused\":" + (LastPaused ? "true" : "false") + ",\"focused\":" + (LastFocused ? "true" : "false") +
                   ",\"longEvent\":" + (LastLongEvent ? "true" : "false") + ",\"save\":" + W.Json(LastSave) +
                   ",\"gc\":" + GC.CollectionCount(0) + ",\"heapMB\":" + M.F(GC.GetTotalMemory(false) / 1048576.0, 1) +
                   "," + W.HealthFields();
        }

        private static void Loop()
        {
            bool silent = false;
            double lastSilenceLine = 0, lastHb = -10, silenceStart = 0;
            while (true)
            {
                try
                {
                    Thread.Sleep(1000);
                    double now = Now;
                    double beat = Seconds(Interlocked.Read(ref _beatTicks));
                    double quiet = now - beat;
                    if (quiet > 1.5) Interlocked.Exchange(ref QuietPhase, PhaseName + "@" + M.F(quiet, 1) + "s");
                    if (quiet > M.SilenceSeconds)
                    {
                        if (!silent || now - lastSilenceLine >= M.SilenceRepeatSeconds)
                        {
                            if (!silent) silenceStart = beat;
                            silent = true;
                            lastSilenceLine = now;
                            SilenceLines++;
                            W.Enqueue("silence", "\"silentS\":" + M.F(quiet, 1) + "," + ContextFields());
                        }
                        JawaBenchStallDump.Tick(now, quiet, beat);
                    }
                    else if (silent)
                    {
                        silent = false;
                        W.Enqueue("resumed", "\"silentS\":" + M.F(beat - silenceStart, 1) + ",\"phase\":\"" + PhaseName + "\"");
                    }
                    if (now - lastHb >= M.CadenceSeconds)
                    {
                        lastHb = now;
                        WriteHeartbeat(now, quiet);
                    }
                }
                catch
                {
                    // never die: the heartbeat file is the external observer's only window in
                }
            }
        }

        internal static void SetTickChangeForTest(double s) => Interlocked.Exchange(ref _lastTickChange, (long)(s * System.Diagnostics.Stopwatch.Frequency));
        internal static void SetBeatForTest(double secondsAgo) =>
            Interlocked.Exchange(ref _beatTicks, W.Clock.ElapsedTicks - (long)(secondsAgo * Stopwatch.Frequency));

        internal static void WriteHeartbeatForTest()
        {
            double now = Now;
            WriteHeartbeat(now, now - Seconds(Interlocked.Read(ref _beatTicks)));
        }

        private static long _hbSeq, _hbErrors;
        private static string _hbLastError;
        internal static string ProcStartUtc;

        private static string ProcessStartUtc()
        {
            if (ProcStartUtc != null) return ProcStartUtc;
            try { ProcStartUtc = Process.GetCurrentProcess().StartTime.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", System.Globalization.CultureInfo.InvariantCulture); }
            catch { ProcStartUtc = ""; }
            return ProcStartUtc;
        }

        /// <summary>
        /// MUST 10: the heartbeat states TWO different facts - when the MAIN thread last made progress
        /// (mainBeatMono / mainBeatUtc, from its last Root.Update beat) and when THIS watchdog thread wrote
        /// (watchdogMono / watchdogUtc) - plus a sequence number, the process start time (so an external
        /// observer can tell a reused pid), and the count/last text of heartbeat write errors. Published
        /// atomically (temp file, then replace), so a reader never sees an empty or half-written file.
        /// </summary>
        private static void WriteHeartbeat(double now, double quiet)
        {
            string tmp = HeartbeatPath + ".tmp";
            try
            {
                long seq = ++_hbSeq;
                double beatMono = Seconds(Interlocked.Read(ref _beatTicks));
                long frameResult = Interlocked.Read(ref _frameResult);
                long tickChange = Interlocked.Read(ref _lastTickChange);
                DateTime utcNow = DateTime.UtcNow;
                string iso(DateTime t) => t.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", System.Globalization.CultureInfo.InvariantCulture);
                var sb = new StringBuilder(512);
                sb.Append("{\"pid\":").Append(W.Pid)
                  .Append(",\"session\":\"").Append(W.Session).Append('"')
                  .Append(",\"procStartUtc\":").Append(M.Json(ProcessStartUtc()))
                  .Append(",\"hbSeq\":").Append(seq)
                  .Append(",\"utc\":\"").Append(iso(utcNow)).Append('"')
                  .Append(",\"mono\":").Append(M.F(now, 3))
                  .Append(",\"watchdogUtc\":\"").Append(iso(utcNow)).Append('"')
                  .Append(",\"watchdogMono\":").Append(M.F(now, 3))
                  .Append(",\"mainBeatUtc\":\"").Append(iso(utcNow.AddSeconds(-(now - beatMono)))).Append('"')
                  .Append(",\"mainBeatMono\":").Append(M.F(beatMono, 3))
                  .Append(",\"silentS\":").Append(M.F(quiet, 1))
                  .Append(",\"phase\":\"").Append(PhaseName).Append('"')
                  .Append(",\"ticksGame\":").Append(LastTicksGame)
                  .Append(",\"scene\":").Append(W.Json(_scene))
                  .Append(",\"sceneSinceMono\":").Append(M.F(Seconds(Interlocked.Read(ref _sceneSinceTicks)), 3))
                  .Append(",\"paused\":").Append(_speed < 0 ? "null" : LastPaused ? "true" : "false")
                  .Append(",\"lastTickMono\":").Append(tickChange < 0 ? "null" : M.F(Seconds(tickChange), 3))
                  .Append(",\"frames\":").Append((uint)(frameResult >> 32))
                  .Append(",\"frameFaultStreak\":").Append((uint)frameResult)
                  .Append(",\"frameFaultSinceMono\":").Append((uint)frameResult == 0 ? "null" :
                      M.F(Seconds(Interlocked.Read(ref _frameFaultSince)), 3))
                  .Append(",\"segment\":").Append(W.Json(Path.GetFileName(W.CurrentPath ?? "")))
                  .Append(",\"hbErrors\":").Append(Interlocked.Read(ref _hbErrors))
                  .Append(",\"hbLastError\":").Append(M.Json(_hbLastError))
                  .Append(',').Append(W.HealthFields())
                  .Append('}');
                File.WriteAllText(tmp, sb.ToString());
                if (File.Exists(HeartbeatPath))
                {
                    try { File.Replace(tmp, HeartbeatPath, null); }
                    catch { File.Copy(tmp, HeartbeatPath, true); File.Delete(tmp); }
                }
                else File.Move(tmp, HeartbeatPath);
            }
            catch (Exception e)
            {
                Interlocked.Increment(ref _hbErrors);
                _hbLastError = e.GetType().Name + ": " + e.Message;
                try { if (File.Exists(tmp)) File.Delete(tmp); } catch { }
            }
        }
    }
}
