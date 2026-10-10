// Heartbeat file (MUST 10): main-thread progress and watchdog progress are separate facts, published atomically.
using System.IO;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_HeartbeatSeparatesMainAndWatchdog()
        {
            string d = TempDir();
            WD.HeartbeatPath = Path.Combine(d, "hb_abcdef.json");
            WD.LastTicksGame = 4242;
            WD.SetBeatForTest(30.0);                         // the main thread last beat 30 s ago
            WD.WriteHeartbeatForTest();
            string text = File.ReadAllText(WD.HeartbeatPath);
            Emit("heartbeat", text);
            Check(Directory.GetFiles(d).Length == 1, "no temp file left beside the heartbeat: " + Directory.GetFiles(d).Length + " files");
        }
    }
}
