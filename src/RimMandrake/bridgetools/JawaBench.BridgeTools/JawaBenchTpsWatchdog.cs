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
        internal static volatile int LastTicksGame;
        internal static volatile string LastSpeed = "";
        internal static volatile string LastMult = "";
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

        internal static void Start(string dir)
        {
            if (_thread != null) return;
            HeartbeatPath = Path.Combine(dir, "hb_" + W.Session + ".json");
            Interlocked.Exchange(ref _beatTicks, W.Clock.ElapsedTicks);
            _thread = new Thread(Loop) { IsBackground = true, Name = "JawaBench.TpsWatchdog" };
            _thread.Start();
        }

        private static double Seconds(long ticks) => (double)ticks / Stopwatch.Frequency;

        /// <summary>The incident context the watchdog can give without touching Unity (fields, no braces).</summary>
        internal static string ContextFields()
        {
            double now = Now;
            return "\"phase\":\"" + PhaseName + "\",\"phaseS\":" + M.F(now - Seconds(Interlocked.Read(ref _phaseSinceTicks)), 3) +
                   ",\"ticksGame\":" + LastTicksGame + ",\"speed\":\"" + LastSpeed + "\",\"mult\":" + (LastMult.Length > 0 ? LastMult : "null") +
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

        private static void WriteHeartbeat(double now, double quiet)
        {
            try
            {
                var sb = new StringBuilder(256);
                sb.Append("{\"pid\":").Append(W.Pid)
                  .Append(",\"session\":\"").Append(W.Session).Append('"')
                  .Append(",\"utc\":\"").Append(W.Utc()).Append('"')
                  .Append(",\"mono\":").Append(M.F(now, 3))
                  .Append(",\"silentS\":").Append(M.F(quiet, 1))
                  .Append(",\"phase\":\"").Append(PhaseName).Append('"')
                  .Append(",\"ticksGame\":").Append(LastTicksGame)
                  .Append(",\"segment\":").Append(W.Json(Path.GetFileName(W.CurrentPath ?? "")))
                  .Append(',').Append(W.HealthFields())
                  .Append('}');
                File.WriteAllText(HeartbeatPath, sb.ToString());
            }
            catch { }
        }
    }
}
