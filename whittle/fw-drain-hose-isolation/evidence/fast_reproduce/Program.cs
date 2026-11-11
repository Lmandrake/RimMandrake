using System;
namespace RimMandrake.FlowWorks.SelfTest {
internal static class Program {
    private static int failures;
    public static void Check(bool ok, string message) {
        Console.WriteLine((ok ? "PASS " : "FAIL ") + message);
        if (!ok) failures++;
    }
    public static int Main() {
        var g = new HoseNetChecks.G();
            HoseNetChecks.G.Add(g.PipeOf, "P1", "a1");
            HoseNetChecks.G.Add(g.PT, "a1", "T");
            HoseNetChecks.G.Add(g.PT, "b1", "T");
            HoseNetChecks.G.Add(g.PT, "b1", "TV");
            var tanks = HoseNetChecks.Walk(g, "P1").Tanks;
            Console.WriteLine("MEASURED roles a1=" + g.RoleOf("a1") + " b1=" + g.RoleOf("b1") + " tanks=[" + string.Join(",", tanks) + "]");
            Check(!tanks.Contains("TV"), "OLD exclusion passes with no recognized pipes");
            Check(tanks.Contains("T") && !tanks.Contains("TV"), "REPAIRED reach-T-and-exclude-TV assertion on OLD fixture");
        Console.WriteLine("FAILED checks: " + failures);
        return failures == 0 ? 0 : 1;
    }
}}
