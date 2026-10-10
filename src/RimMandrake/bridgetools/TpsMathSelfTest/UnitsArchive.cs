// Player.log archive (MUST 12): two different logs never collide or dedupe into one; the same content once.
using System.IO;
using System.Linq;
using W = JawaBench.BridgeTools.JawaBenchTpsWriter;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_ArchiveNoCollisions()
        {
            string d = PrepWriter();
            W.Start(d, "a11ce0", 7);
            string src = TempDir();
            string a = Path.Combine(src, "A.log"), b = Path.Combine(src, "B.log");
            File.WriteAllText(a, new string('a', 4096));
            File.WriteAllText(b, new string('b', 4096));               // SAME length, different content
            W.ArchiveLogNow(a, "Player-prev_20261010T150000Z.log");    // same second-resolution name
            W.ArchiveLogNow(b, "Player-prev_20261010T150000Z.log");
            W.ArchiveLogNow(a, "Player-prev_20261010T150000Z.log");    // the same content again
            var logs = Directory.GetFiles(Path.Combine(d, "logs"), "*.log").Select(Path.GetFileName).ToList();
            Check(logs.Count == 2, "two different logs -> two archives, a repeat -> none: " + string.Join(",", logs));
            var texts = Directory.GetFiles(Path.Combine(d, "logs"), "*.log").Select(File.ReadAllText).ToList();
            Check(texts.Any(t => t[0] == 'a') && texts.Any(t => t[0] == 'b'), "both contents preserved");
            W.Drain(5000);
            W.ResetForTest();
        }
    }
}
