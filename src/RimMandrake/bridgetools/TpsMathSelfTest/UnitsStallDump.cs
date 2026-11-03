// Stall dump (BRIDGE_STALL_DIAGNOSTIC_1): a main-thread silence of >= 60 s writes stall_<session>_NN.json naming the
// phase stack, the context, the probe's answer, the stack attempt and the thread CPU; once per episode, then every
// RepeatSeconds; never before 60 s; capped per session.
using System.IO;
using System.Linq;
using System.Text.Json;
using SD = JawaBench.BridgeTools.JawaBenchStallDump;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_StallDumpDecision()
        {
            Check(!SD.ShouldDump(59.9, 0, 1e9, 0), "no dump before 60 s of silence");
            Check(SD.ShouldDump(60.0, 0, 0, 0), "the first dump at 60 s");
            Check(!SD.ShouldDump(200, 1, 140, 1), "no second dump within RepeatSeconds of the first");
            Check(SD.ShouldDump(400, 1, 300, 1), "a second dump RepeatSeconds later, same silence");
            Check(!SD.ShouldDump(1e6, 0, 1e9, SD.MaxPerSession), "capped per session");
            Check(SD.DumpSeconds == 60.0, "DumpSeconds is the item's ~60 s: " + SD.DumpSeconds);
        }

        private static void T_StallDumpAt60s()
        {
            string d = TempDir();
            SD.Reset();
            WD.HeartbeatPath = Path.Combine(d, "hb_abcdef.json");
            WD.LastTicksGame = 777;
            WD.SetPhasesForTest(WD.PTick, WD.PTlRare);
            SD.CaptureMainThread();                                  // this test thread plays the main thread
            SD.Probe = () => "{\"ticksGameNow\":777,\"tickList\":\"Rare\",\"pawns\":[{\"id\":\"Human12\",\"job\":\"Wait\"}]}";
            try
            {
                SD.Tick(100.0, 30.0, 70.0);
                Check(Directory.GetFiles(d, "stall_*.json").Length == 0, "30 s of silence wrote a dump");
                SD.Tick(131.0, 61.0, 70.0);
                SD.Tick(132.0, 62.0, 70.0);                          // same episode, inside RepeatSeconds: no second file
                var files = Directory.GetFiles(d, "stall_*.json");
                Check(files.Length == 1, "one dump for the first minute, got " + files.Length + " (" + SD.LastError + ")");
                Check(Directory.GetFiles(d, "*.tmp").Length == 0, "a temp file was left beside the dump");
                if (files.Length == 0) return;
                string text = File.ReadAllText(files[0]);
                Emit("stall", text);
                using (var doc = JsonDocument.Parse(text))
                {
                    var r = doc.RootElement;
                    var stack = r.GetProperty("phaseStack").EnumerateArray().Select(e => e.GetString()).ToArray();
                    Check(string.Join(">", stack) == "update>tick>tl:Rare", "phaseStack outermost-first: " + string.Join(">", stack));
                    Check(r.GetProperty("phase").GetString() == "tl:Rare", "phase field");
                    Check(r.GetProperty("ticksGame").GetInt32() == 777, "ticksGame");
                    Check(r.GetProperty("silentS").GetDouble() >= 60.0, "silentS");
                    Check(r.GetProperty("probe").GetProperty("pawns")[0].GetProperty("job").GetString() == "Wait", "probe embedded verbatim");
                    var ms = r.GetProperty("mainStack");
                    Check(ms.TryGetProperty("text", out _) || ms.TryGetProperty("error", out _), "mainStack has text or a named error");
                    Check(r.GetProperty("threadCount").GetInt32() > 0, "threads listed");
                    Check(r.GetProperty("threads").EnumerateArray().Any(t => t.GetProperty("main").GetBoolean()), "the main thread is flagged among the threads");
                }
                // a new silence (new beat) dumps again at once; the first dump of an episode carries no CPU delta, a repeat does
                SD.Tick(500.0, 61.0, 439.0);
                SD.Tick(800.0, 361.0, 439.0);
                files = Directory.GetFiles(d, "stall_*.json").OrderBy(f => f).ToArray();
                Check(files.Length == 3, "new episode + its repeat -> 3 dumps, got " + files.Length);
                if (files.Length == 3)
                {
                    using (var doc = JsonDocument.Parse(File.ReadAllText(files[2])))
                    {
                        Check(doc.RootElement.GetProperty("episodeDump").GetInt32() == 2, "third file is the episode's second dump");
                        Check(doc.RootElement.GetProperty("mainCpuDeltaS").ValueKind == JsonValueKind.Number, "a repeat dump carries mainCpuDeltaS");
                    }
                }
                // a throwing probe is data, not a lost dump
                SD.Probe = () => throw new System.InvalidOperationException("boom");
                SD.Tick(2000.0, 70.0, 1930.0);
                files = Directory.GetFiles(d, "stall_*.json").OrderBy(f => f).ToArray();
                Check(files.Length == 4 && File.ReadAllText(files[3]).Contains("InvalidOperationException: boom"), "a throwing probe is recorded in the dump");
            }
            finally { SD.Probe = null; SD.Reset(); }
        }
    }
}
