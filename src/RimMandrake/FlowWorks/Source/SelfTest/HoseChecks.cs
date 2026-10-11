// Hose port step 2 (design FINAL §3.7, G2.4): the runner adapter for the hose suites moved from Gimme Some Slack's SelfTest.
// GSS's suites assert through Program.Check(bool, string) and count ASSERTIONS; FlowWorks' own suite counts Case()s. This shim
// gives the moved files the same Program.Check they called, records every assertion under the suite running it, prints one
// "<suite>: n/n" line each, and the total "hose: n/n assertions passed (moved from Gimme Some Slack)". The step-2 gate compares
// that total with what GSS lost (python3 src/RimMandrake/Utils/selftest_flowworks_stock.py prints it).
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static partial class Program
    {
        private static string hoseSuite = "?";
        /// <summary>Suites written for the port (not moved from GSS): excluded from the "moved" count.</summary>
        private static readonly HashSet<string> NewSuites = new() { "HoseLegacyChecks", "HoseNetChecks" };
        private static readonly List<(string suite, int n, int fails)> hoseCounts = new();
        private static int hoseN, hoseFails;

        /// <summary>The GSS-shaped assertion every moved hose suite calls.</summary>
        internal static void Check(bool ok, string msg)
        {
            hoseN++;
            if (!ok) { hoseFails++; Console.WriteLine("FAIL " + msg); }
        }

        private static void HoseSuite(string name, Action run)
        {
            int n0 = hoseN, f0 = hoseFails;
            hoseSuite = name;
            try { run(); }
            catch (Exception ex) { hoseN++; hoseFails++; Console.WriteLine("FAIL " + name + " threw: " + ex); }
            hoseCounts.Add((name, hoseN - n0, hoseFails - f0));
            Console.WriteLine($"  {name}: {hoseN - n0 - (hoseFails - f0)}/{hoseN - n0}");
        }

        internal static int RunHoseSuites(string[] args)
        {
            Console.WriteLine("\nhose suites (moved from Gimme Some Slack's SelfTest):");
            HoseSuite("HoseSelfTest", () => HoseSelfTest.Run(Check));
            HoseSuite("HoseReview6", HoseReview6.Run);
            HoseSuite("HoseReview7", HoseReview7.Run);
            HoseSuite("HosePileLook", HosePileLook.Run);
            HoseSuite("HoseCarryChecks", HoseCarryChecks.Run);
            HoseSuite("HoseLiveChecks", HoseLiveChecks.Run);
            HoseSuite("StyleStage3Checks", StyleStage3Checks.Run);
            HoseSuite("HoseGptFix", HoseGptFix.Run);
            HoseSuite("HoseLegacyChecks", HoseLegacyChecks.Run);
            HoseSuite("HoseNetChecks", HoseNetChecks.Run);
            HoseSuite("HoseFuzz", () => HoseFuzz.Run(args));
            Console.WriteLine($"hose: {hoseN - hoseFails}/{hoseN} assertions passed (moved from Gimme Some Slack: {hoseCounts.Where(c => !NewSuites.Contains(c.suite)).Sum(c => c.n)}; new: {hoseCounts.Where(c => NewSuites.Contains(c.suite)).Sum(c => c.n)})");
            return hoseFails;
        }
    }
}
