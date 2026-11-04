// Stall dump WIRING (BRIDGE_STALL_DIAGNOSTIC_1, gen 7): the real watchdog thread, started by the production
// JawaBenchTpsWatchdog.Start, must itself write stall_<session>_NN.json once the main thread has been silent >= 60 s.
// The T_StallDump* units call JawaBenchStallDump.Tick directly, so they stay green if Loop stops calling it; this one
// does not. Loop never ends, so it is NOT a T_ unit (it would keep writing into every later unit): Program runs it from
// the `L` line, after `U`, and the process exits with it. It prints a `U` line, so CS_UNITS lists it like the rest.
using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading;
using SD = JawaBench.BridgeTools.JawaBenchStallDump;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static string[] WaitFor(string dir, string mask, double seconds)
        {
            var until = DateTime.UtcNow.AddSeconds(seconds);
            string[] f;
            while ((f = Directory.GetFiles(dir, mask)).Length == 0 && DateTime.UtcNow < until) Thread.Sleep(100);
            return f;
        }

        [DllImport("kernel32.dll")]
        private static extern uint GetCurrentThreadId();

        internal static void RunWatchdogLoop()
        {
            _cur = "StallDumpWatchdogLoop";
            Fails.Clear();
            try
            {
                string d = TempDir();
                SD.Reset();
                SD.Probe = null;
                // a FRESH thread plays the main thread and calls Start, so the dump's "main" flag can only come from Start's
                // own CaptureMainThread (the T_ units captured the harness thread earlier); it stays alive until the end
                int mainTid = -1;
                var started = new ManualResetEventSlim(false);
                var done = new ManualResetEventSlim(false);
                var main = new Thread(() =>
                {
                    mainTid = (int)GetCurrentThreadId();
                    WD.Start(d);                                      // Loop runs on its own thread from here
                    WD.SetPhasesForTest(WD.PTick, WD.PTlRare);
                    started.Set();
                    done.Wait(30000);
                }) { IsBackground = true, Name = "fake-main" };
                main.Start();
                Check(started.Wait(10000), "Start did not return on the fake main thread");
                // alive first, so "no dump yet" below is not a dead thread's silence: Loop writes the heartbeat each cadence
                var hb = WaitFor(d, "hb_*.json", 3.0);
                Check(hb.Length == 1, "the watchdog thread never wrote its heartbeat (" + hb.Length + " files)");
                Thread.Sleep(2500);                                   // ~2.5 s of quiet: well under 60 s
                Check(Directory.GetFiles(d, "stall_*.json").Length == 0, "Loop dumped after only seconds of silence");
                WD.SetBeatForTest(120.0);                             // the main thread has now been silent two minutes
                var files = WaitFor(d, "stall_*.json", 6.0);
                Check(files.Length == 1, "Loop wrote " + files.Length + " stall dumps within 6 s of a 120 s silence, want 1 (" + SD.LastError + ")");
                if (files.Length == 1)
                {
                    string text = File.ReadAllText(files[0]);
                    using (var doc = JsonDocument.Parse(text))
                    {
                        var r = doc.RootElement;
                        Check(r.GetProperty("silentS").GetDouble() >= 60.0, "silentS from the watchdog's own clock");
                        var stack = r.GetProperty("phaseStack").EnumerateArray().Select(e => e.GetString()).ToArray();
                        Check(string.Join(">", stack) == "update>tick>tl:Rare", "phaseStack: " + string.Join(">", stack));
                        var flagged = r.GetProperty("threads").EnumerateArray().Where(t => t.GetProperty("main").GetBoolean())
                                       .Select(t => t.GetProperty("id").GetInt32()).ToArray();
                        Check(flagged.Length == 1 && flagged[0] == mainTid,
                              "the thread that called Start (" + mainTid + ") is the one flagged main: [" + string.Join(",", flagged) + "]");
                    }
                }
                WD.SetBeatForTest(0.0);                               // quiet again before the process exits
                done.Set();
            }
            catch (Exception e) { Fails.Add("threw " + e.GetType().Name + ": " + e.Message); }
            Console.WriteLine("U " + _cur + (Fails.Count == 0 ? " ok" : " FAIL " + string.Join(" | ", Fails).Replace("\n", " ")));
        }
    }
}
