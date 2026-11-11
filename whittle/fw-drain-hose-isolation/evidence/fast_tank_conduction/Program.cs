using System;
namespace RimMandrake.FlowWorks.SelfTest {
internal static class Program {
    private static int failures;
    public static void Check(bool ok, string message) {
        Console.WriteLine((ok ? "PASS " : "FAIL ") + message);
        if (!ok) failures++;
    }
    public static int Main() {
        HoseNetChecks.Run();
        Console.WriteLine("FAILED checks: " + failures);
        return failures == 0 ? 0 : 1;
    }
}}
