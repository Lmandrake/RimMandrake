// HOSES_MAP1_DIAGNOSE_TICK_STALLS: map1's hose tick stalled 100-200 ms. Every building spawn (HugeThings' growing trunk
// blockers, ~1 per 17 ticks) bumps the hose world version, so the 250-tick recheck rebuilt the whole-map snapshot, and
// 86% of a ~17 ms build was RM_HoseBands.Apply: two climb-depth reads, two thing-list scans and a GetComponent walk per cell,
// plus a List of every dug square (~1-2 MB of garbage per build on a dug-out map). Mono's collector is full on every
// collection, so that garbage drew the 100-200 ms GC pauses into the hose tick. These checks hold Apply to the fast shape
// (no per-build allocation, one depth read and one deck lookup per cell, no GetComponent) with the old body kept beside it
// as the oracle the live probe RM_HoseBands.ProofOracle compares against, and hold the deckless shortcut
// (HoseBandMath.DecklessClosed) to the classification it replaces.
using System;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseBandsApplyChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Body(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            Assert(j >= 0, "end marker present: " + end);
            return src.Substring(i, j - i);
        }

        private static int Count(string s, string what) => Regex.Matches(s, Regex.Escape(what)).Count;

        private static string Fast() => Body(RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_HoseBands.cs")),
            "internal static void Apply(Map map, CordWorld w)", "internal static void ApplyLegacy(Map map, CordWorld w)");

        public static void Run(Action<string, Action> Case)
        {
            Case("HOSEBANDS_APPLY_NO_PER_BUILD_ALLOC", () =>
            {
                string fast = Fast();
                Match m = Regex.Match(fast, @"\bnew\s+(?!IntVec3\b|Cell\b)[A-Za-z_]");
                Assert(!m.Success, "Apply allocates per build: '" + (m.Success ? fast.Substring(m.Index, Math.Min(40, fast.Length - m.Index)) : "") + "'");
                Assert(!fast.Contains("foreach"), "Apply walks a collection (enumerator / dug list)");
                Assert(!fast.Contains("GetComponent"), "Apply walks the map components per cell (RM_LineCrossing.SurfaceAt)");
            });
            Case("HOSEBANDS_APPLY_ONE_READ_PER_CELL", () =>
            {
                string fast = Fast();
                Assert(Count(fast, "ClimbDepthAt(") == 1, "Apply reads the climb depth once per cell (StepDepthAt re-reads it)");
                Assert(!fast.Contains("StepDepthAt(") && !fast.Contains("IsCovered(") && !fast.Contains("SurfaceAt("),
                    "Apply calls a helper that re-scans the cell's things");
                Assert(Count(fast, "DeckAt(") == 1, "Apply looks the deck up once per dug cell");
                Assert(fast.Contains("HoseBandMath.DecklessClosed("), "a deckless cell's verdict comes from DecklessClosed");
            });
            Case("HOSEBANDS_APPLY_LEGACY_ORACLE_KEPT", () =>
            {
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_HoseBands.cs"));
                string legacy = Body(src, "internal static void ApplyLegacy(Map map, CordWorld w)", "public static string ProofOracle(string arg)");
                Assert(legacy.Contains("RM_LineCrossing.SurfaceAt(map, c)") && legacy.Contains("RM_SuperdeepTrap.StepDepthAt(map, eng, c)"),
                    "the oracle is the pre-fix rule (SurfaceAt + StepDepthAt per cell)");
                string probe = Body(src, "public static string ProofOracle(string arg)", "// end ProofOracle");
                Assert(probe.Contains("ApplyLegacy(") && probe.Contains("Apply(") && probe.Contains("CellSig"), "the probe compares both rules cell by cell");
            });
            Case("HOSEBANDS_DECKLESS_SHORTCUT_EQUALS_CLASSIFY", () =>
            {
                foreach (bool exc in new[] { false, true })
                    Assert(HoseBandMath.DecklessClosed(exc) == HoseBandMath.SurfaceClosed(true, RM_LineCrossingMath.Classify(exc, DeckOnSquare.None)),
                        "DecklessClosed(" + exc + ") differs from SurfaceClosed(Classify(" + exc + ", None))");
            });
        }
    }
}
