using System;
using RimMandrake.FlowWorks.Hose;
namespace RimMandrake.FlowWorks.SelfTest {
internal static class Program {
    private static int failures;
    public static void Check(bool ok, string message) {
        Console.WriteLine((ok ? "PASS " : "FAIL ") + message);
        if (!ok) failures++;
    }
    public static int Main(string[] args) {
        if (Array.IndexOf(args, "g2off") >= 0) HoseMath.G2On = false;
        if (Array.IndexOf(args, "g2") >= 0) HoseMath.G2On = true;
        if (Array.IndexOf(args, "--inspect") >= 0) {
            for (long seed = 1; seed <= 40; seed++) {
                foreach (bool outlet in new[] { true, false }) {
                    long steps = 0;
                    var c = HoseFuzz.MakeHose(seed);
                    string msg = HoseFuzz.RunHose(seed, null, ref steps, out int laid, out int fallback, outlet);
                    Console.WriteLine($"INSPECT seed={seed} outlet={outlet} reel={c.Reel.W} laid={laid} fallback={fallback} steps={steps} install={HoseMath.CheckInstall(c.W, c.Reel, c.Target, c.MaxLen) ?? "ok"} msg={msg ?? "ok"}");
                }
            }
        } else HoseFuzz.Run(args);
        Console.WriteLine("FAILED checks: " + failures);
        return failures == 0 ? 0 : 1;
    }
}}
