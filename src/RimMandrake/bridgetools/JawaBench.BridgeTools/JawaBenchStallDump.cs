// JawaBenchStallDump.cs - when the main thread has been silent for a minute, write down WHAT IT WAS DOING
// (BRIDGE_STALL_DIAGNOSTIC_1).
//
// Trigger case: 2026-10-08 19:23-19:43, Grey Sea floor map 4: a bridge save timed out at 300 s, Player.log was
// silent for 20 minutes and the game recovered alone - and nothing on disk said where the main thread had been.
// A bridge call blocks exactly when the main thread stops servicing the bridge queue, which is exactly when the
// watchdog's heartbeat goes quiet; so the watchdog thread writes the dump, and rimbridge_client names the dumps on
// the evidence row of any call that blocked past StallDumpSeconds.
//
// One file per dump, stall_<session>_<NN>.json beside hb_<session>.json in the record dir: the first after
// DumpSeconds of silence, another every RepeatSeconds while the same silence lasts (so a dump series shows whether
// the phase, the tick bucket or the main thread's CPU moved), at most MaxPerSession per session. Each holds:
//   * phaseStack  - the main thread's whole nested phase stack (outermost first), not only its top;
//   * the watchdog's context fields (phase, phaseS, ticksGame, speed, save, longEvent, heap, gc, writer health);
//   * probe       - what the companion's Verse side can say off-thread: the tick-list bucket being ticked (count,
//                   top defs, its pawns and their jobs) - see JawaBenchStallProbe.cs; a failure is data;
//   * mainStack   - an attempt at the main thread's managed stack. MEASURED 2026-11-03 (ilspycmd on the game's
//                   mscorlib.dll): Unity's Mono throws NotImplementedException from StackTrace(Thread, bool) for any
//                   thread but the caller, so this records that error, honestly, until a runtime can do it;
//   * threads     - top native threads by CPU with the main thread flagged, and mainCpuDeltaS since the previous
//                   dump: a main thread that burned ~RepeatSeconds of CPU was SPINNING; ~0 means it was WAITING.
// ⛔ Like the watchdog: no Verse, no UnityEngine (compiled into the offline harness). Never throws.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchStallDump
    {
        /// <summary>The item's "a bridge call blocks past ~60 s". rimbridge_client.py STALL_DUMP_SECONDS must equal it.</summary>
        internal const double DumpSeconds = 60.0;
        internal const double RepeatSeconds = 300.0;
        internal const int MaxPerSession = 24;
        internal const int TopThreads = 6;

        /// <summary>Set by the companion's Verse side: returns one JSON OBJECT (braces included). Called on the
        /// watchdog thread; it must read fields only. Null = no probe installed (reported as such).</summary>
        internal static Func<string> Probe;

        internal static Thread MainThread;
        internal static int MainNativeTid = -1;
        internal static int Written;
        internal static string LastPath, LastError;

        private static double _episodeBeat = double.NaN, _lastDumpAt, _lastFailAt = double.NegativeInfinity;
        /// <summary>A failed write is retried this soon, without spending the episode's dump or its repeat delay.</summary>
        internal const double RetrySeconds = 10.0;
        private static int _episodeDumps;
        private static double _prevMainCpu = double.NaN;

        [DllImport("kernel32.dll")]
        private static extern uint GetCurrentThreadId();

        /// <summary>Main thread, once (watchdog Start).</summary>
        internal static void CaptureMainThread()
        {
            MainThread = Thread.CurrentThread;
            try { MainNativeTid = (int)GetCurrentThreadId(); } catch { MainNativeTid = -1; }
        }

        /// <summary>Pure: should the watchdog write a dump now? quiet = seconds since the last beat; episodeDumps = dumps
        /// already written for THIS silence; sinceLast = seconds since the last of them.</summary>
        internal static bool ShouldDump(double quiet, int episodeDumps, double sinceLast, int written)
        {
            if (written >= MaxPerSession || !(quiet >= DumpSeconds)) return false;
            return episodeDumps == 0 || sinceLast >= RepeatSeconds;
        }

        /// <summary>Watchdog thread, every loop: beat = the monotonic second of the last heartbeat (an episode's id).</summary>
        internal static void Tick(double now, double quiet, double beat)
        {
            try
            {
                if (beat != _episodeBeat) { _episodeBeat = beat; _episodeDumps = 0; _prevMainCpu = double.NaN; }
                if (!ShouldDump(quiet, _episodeDumps, now - _lastDumpAt, Written) || now - _lastFailAt < RetrySeconds) return;
                if (Write(quiet, _episodeDumps + 1, Dir(), false) != null) { _episodeDumps++; _lastDumpAt = now; }
                else _lastFailAt = now;          // counters move only on a file that exists
            }
            catch (Exception e) { LastError = e.GetType().Name + ": " + e.Message; }
        }

        /// <summary>Main thread, at watchdog Start: run the whole dump path once so Mono JIT-compiles it HERE (PrepareMethod
        /// is a no-op on Unity's Mono). Writes one file into a scratch sub-dir and deletes it. Never throws.</summary>
        internal static void Warm(string recordDir)
        {
            try
            {
                Tick(0, 0, 0);                                     // returns at ShouldDump: compiles Tick + ShouldDump
                string d = Path.Combine(recordDir, ".stallwarm");
                Directory.CreateDirectory(d);
                string p = Write(0, 0, d, true);
                if (p != null) File.Delete(p);
                try { Directory.Delete(d); } catch { }
            }
            catch (Exception e) { LastError = "warm: " + e.GetType().Name + ": " + e.Message; }
            finally { var err = LastError; Reset(); LastError = err; }
        }

        internal static void Reset() { _episodeBeat = double.NaN; _episodeDumps = 0; _lastDumpAt = 0; _lastFailAt = double.NegativeInfinity; Written = 0; _prevMainCpu = double.NaN; LastPath = LastError = null; }

        private static string Dir() => Path.GetDirectoryName(WD.HeartbeatPath ?? "") is string d && d.Length > 0 ? d : W.Dir;

        internal static string Write(double quiet, int episodeDump) => Write(quiet, episodeDump, Dir(), false);

        /// <summary>warm = the main thread's start-up rehearsal: same code path, no record row, counters untouched.</summary>
        internal static string Write(double quiet, int episodeDump, string dir, bool warm)
        {
            if (string.IsNullOrEmpty(dir)) { LastError = "no record dir"; return null; }
            int n = Written + 1;
            string name = "stall_" + (W.Session ?? "nosession") + "_" + n.ToString("00", System.Globalization.CultureInfo.InvariantCulture) + ".json";
            string path = Path.Combine(dir, name), tmp = path + ".tmp";
            string body = Compose(quiet, n, episodeDump);
            try
            {
                File.WriteAllText(tmp, body);
                if (File.Exists(path)) File.Delete(path);
                File.Move(tmp, path);
                if (warm) return path;
                Written = n;
                LastPath = path;
                W.Enqueue("stall_dump", "\"file\":" + M.Json(name) + ",\"silentS\":" + M.F(quiet, 1) + ",\"phase\":" + M.Json(WD.PhaseName));
                return path;
            }
            catch (Exception e)
            {
                LastError = e.GetType().Name + ": " + e.Message;
                try { if (File.Exists(tmp)) File.Delete(tmp); } catch { }
                return null;
            }
        }

        /// <summary>The dump's whole text. Called once at watchdog Start ON THE MAIN THREAD so every method it reaches is
        /// JIT-compiled there: RuntimeHelpers.PrepareMethod is a no-op on Unity's Mono, and a watchdog JIT-compiling while
        /// the stuck main thread holds a runtime lock could wait forever.</summary>
        internal static string Compose(double quiet, int n, int episodeDump)
        {
            var sb = new StringBuilder(4096);
            sb.Append("{\"kind\":\"stall\",\"item\":\"BRIDGE_STALL_DIAGNOSTIC_1\"")
              .Append(",\"utc\":").Append(M.Json(DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", System.Globalization.CultureInfo.InvariantCulture)))
              .Append(",\"pid\":").Append(W.Pid)
              .Append(",\"session\":").Append(M.Json(W.Session))
              .Append(",\"seq\":").Append(n)
              .Append(",\"episodeDump\":").Append(episodeDump)
              .Append(",\"silentS\":").Append(M.F(quiet, 1))
              .Append(",\"phaseStack\":").Append(WD.PhaseStackJson())
              .Append(',').Append(WD.ContextFields())
              .Append(",\"probe\":").Append(ProbeJson())
              .Append(",\"mainStack\":").Append(MainStackJson())
              .Append(',').Append(ThreadsFields())
              .Append('}');
            return sb.ToString();
        }

        private static string ProbeJson()
        {
            var p = Probe;
            if (p == null) return "{\"error\":\"no probe installed\"}";
            try
            {
                string s = p();
                return string.IsNullOrEmpty(s) ? "{\"error\":\"probe returned nothing\"}" : s;
            }
            catch (Exception e) { return "{\"error\":" + M.Json(e.GetType().Name + ": " + e.Message) + "}"; }
        }

        /// <summary>The main thread's managed stack, or the reason there is none. Reflection, so the net8 harness (where
        /// the ctor does not exist) compiles the same file.</summary>
        internal static string MainStackJson()
        {
            var t = MainThread;
            if (t == null) return "{\"error\":\"main thread not captured\"}";
            try
            {
                var ctor = typeof(StackTrace).GetConstructor(new[] { typeof(Thread), typeof(bool) });
                if (ctor == null) return "{\"error\":\"UNAVAILABLE: this runtime has no StackTrace(Thread, bool)\"}";
                var st = ctor.Invoke(new object[] { t, false });
                return "{\"text\":" + M.Json(st.ToString()) + "}";
            }
            catch (Exception e)
            {
                var ie = e is System.Reflection.TargetInvocationException && e.InnerException != null ? e.InnerException : e;
                return "{\"error\":" + M.Json(ie.GetType().Name + ": " + ie.Message) + "}";
            }
        }

        internal static string ThreadsFields()
        {
            try
            {
                var rows = new List<KeyValuePair<double, string>>();
                double mainCpu = double.NaN;
                foreach (ProcessThread pt in Process.GetCurrentProcess().Threads)
                {
                    try
                    {
                        double cpu = pt.TotalProcessorTime.TotalSeconds;
                        bool main = pt.Id == MainNativeTid;
                        if (main) mainCpu = cpu;
                        string wait = "";
                        try { if (pt.ThreadState == System.Diagnostics.ThreadState.Wait) wait = pt.WaitReason.ToString(); } catch { }
                        rows.Add(new KeyValuePair<double, string>(main ? double.MaxValue : cpu,
                            "{\"id\":" + pt.Id + ",\"cpuS\":" + M.F(cpu, 2) + ",\"state\":" + M.Json(pt.ThreadState.ToString()) +
                            ",\"waitReason\":" + M.Json(wait) + ",\"main\":" + (main ? "true" : "false") + "}"));
                    }
                    catch { }
                    finally { pt.Dispose(); }
                }
                double delta = double.IsNaN(mainCpu) || double.IsNaN(_prevMainCpu) ? double.NaN : mainCpu - _prevMainCpu;
                if (!double.IsNaN(mainCpu)) _prevMainCpu = mainCpu;
                var top = rows.OrderByDescending(r => r.Key).Take(TopThreads).Select(r => r.Value);
                return "\"mainNativeTid\":" + MainNativeTid + ",\"mainCpuS\":" + (double.IsNaN(mainCpu) ? "null" : M.F(mainCpu, 2)) +
                       ",\"mainCpuDeltaS\":" + (double.IsNaN(delta) ? "null" : M.F(delta, 2)) +
                       ",\"threadCount\":" + rows.Count + ",\"threads\":[" + string.Join(",", top) + "]";
            }
            catch (Exception e) { return "\"threadsError\":" + M.Json(e.GetType().Name + ": " + e.Message); }
        }
    }
}
