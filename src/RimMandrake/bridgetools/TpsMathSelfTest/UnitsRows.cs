// Production-composed record lines (MUST 1): the envelope from JawaBenchTpsWriter.Envelope plus the body
// from JawaBenchTpsMath / JawaBenchTpsWatchdog, exactly as the companion composes them. Python parses each
// J line strictly (duplicate keys and NaN refused) and asserts on the fields.
using M = JawaBench.BridgeTools.JawaBenchTpsMath;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;
using WD = JawaBench.BridgeTools.JawaBenchTpsWatchdog;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_IncidentRowComposition()
        {
            // the cached (pre-gap) state the watchdog holds when the main thread writes the incident
            WD.LastMult = "1";
            WD.LastSpeed = "Normal";
            WD.LastTicksGame = 1234;
            var g = new M.Gap { Start = 10, Seconds = 40, Explained = 0, Paused = false, Mult = 6, Ambiguous = true };
            string body = M.IncidentFields(g, "tl:Normal@39.0s", 0.012, 3, 0, "", WD.ContextFields());
            Emit("incident", W.Envelope(7, "2026-10-10T15:00:00.000Z", 123.4, "0123abcd", "incident", body));
            Emit("silence", W.Envelope(8, "2026-10-10T15:00:01.000Z", 124.4, "0123abcd", "silence",
                                       "\"silentS\":12.0," + WD.ContextFields()));
        }
    }
}
