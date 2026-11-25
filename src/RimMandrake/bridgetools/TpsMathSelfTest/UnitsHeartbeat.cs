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
            WD.SetScene("map");
            WD.SetFrameState(true, 0, 0, 4242);
            WD.FrameEnded(true);
            WD.Beat();
            WD.NoteRootException("unrelated error");
            WD.FrameEnded(false);
            WD.FrameEnded(true);
            WD.Beat();
            WD.NoteRootException("Root level exception in Update(): System.NullReferenceException");
            WD.FrameEnded(false);
            WD.SetBeatForTest(30.0);                         // the main thread last beat 30 s ago
            WD.WriteHeartbeatForTest();
            string text = File.ReadAllText(WD.HeartbeatPath);
            Emit("heartbeat", text);
            Check(text.Contains("\"scene\":\"map\"") && text.Contains("\"paused\":true"), "watcher scene and pause fields");
            Check(text.Contains("\"frames\":4,\"frameFaultStreak\":2") &&
                  !text.Contains("\"frameFaultSinceMono\":null"), "watcher counts frames and resets the fault streak after success");
            WD.SetFrameState(false, 1, 1, 4242);             // before the tick
            WD.SetTickChangeForTest(0.5);
            WD.NoteTicks(4243);                              // after the tick, same frame
            WD.SetFrameState(false, 1, 1, 4243);             // the next frame sees no difference
            WD.WriteHeartbeatForTest();
            string ticked = File.ReadAllText(WD.HeartbeatPath);
            Check(ticked.Contains("\"ticksGame\":4243") && !ticked.Contains("\"lastTickMono\":0.5"),
                  "a tick counted at the end of the frame moves lastTickMono: " + ticked);
            Check(Directory.GetFiles(d).Length == 1, "no temp file left beside the heartbeat: " + Directory.GetFiles(d).Length + " files");
        }
    }
}
