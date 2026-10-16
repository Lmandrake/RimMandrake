// FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS (owner 2026-10-16): the dev-placed flow source and flow sink. The rate math on
// the PRODUCTION RM_MapControlMath (compiled in by the .csproj), a source and a sink driven through the PRODUCTION flow
// kernel (RM_FlowKernel via ArrayWorld) with the ledger read every pulse, and the game wiring read from source.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.MapControls;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class MapControlChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string ModRoot()
        {
            string d = AppContext.BaseDirectory;
            for (int i = 0; i < 10 && d != null; i++, d = Path.GetDirectoryName(d))
            {
                if (Directory.Exists(Path.Combine(d, "Defs", "Canals")) && Directory.Exists(Path.Combine(d, "Source", "MapControls")))
                    return d;
            }
            throw new Exception("FlowWorks mod root not found above " + AppContext.BaseDirectory);
        }

        private static string Between(string s, string from, string to)
        {
            int a = s.IndexOf(from, StringComparison.Ordinal);
            Assert(a >= 0, "marker missing: " + from);
            int b = s.IndexOf(to, a + from.Length, StringComparison.Ordinal);
            Assert(b >= 0, "marker missing: " + to);
            return s.Substring(a, b - a);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("MapControl_rate_to_levels", () =>
            {
                foreach (float r in RM_MapControlMath.RatePresets.Concat(new[] { 0.3f, 1.7f, 3.33f }))
                {
                    float carry = 0f;
                    int total = 0;
                    for (int p = 1; p <= 200; p++)
                    {
                        total += RM_MapControlMath.Due(ref carry, r);
                        Assert(carry >= 0f && carry < 1f, "carry left [0,1) at rate " + r + ": " + carry);
                        int want = (int)Math.Floor(p * (double)r + 1e-3);
                        Assert(Math.Abs(total - want) <= 0, "rate " + r + " after " + p + " pulses gave " + total + ", want " + want);
                    }
                }
                float c = 0f;
                int ten = 0;
                for (int p = 0; p < 10; p++) ten += RM_MapControlMath.Due(ref c, 0.1f);
                Assert(ten == 1, "ten pulses at 0.1 gave " + ten + " levels, want 1");
            });
            Case("MapControl_rate_clamps", () =>
            {
                Assert(RM_MapControlMath.ClampRate(float.NaN) == 0f, "NaN rate not 0");
                Assert(RM_MapControlMath.ClampRate(-3f) == 0f, "negative rate not 0");
                Assert(RM_MapControlMath.ClampRate(1000f) == RM_MapControlMath.MaxRatePerPulse, "huge rate not capped");
                float bad = float.NaN;
                Assert(RM_MapControlMath.Due(ref bad, 1f) == 1 && bad == 0f, "a NaN carry is not reset");
                float zero = 0f;
                for (int p = 0; p < 50; p++) Assert(RM_MapControlMath.Due(ref zero, 0f) == 0, "rate 0 poured");
                Assert(Math.Abs(RM_MapControlMath.PerHour(1f, 250) - 10f) < 1e-4, "1 level a 250-tick pulse is not 10 per hour");
            });
            Case("MapControl_blocked_source_never_banks", () =>
            {
                // Whatever falls due is taken off the carry whether delivered or not: after a long block the first open
                // pulse delivers one pulse's worth, never the backlog.
                float carry = 0f;
                for (int p = 0; p < 100; p++) RM_MapControlMath.Due(ref carry, 0.75f);
                Assert(carry < 1f, "carry banked past one level: " + carry);
                Assert(RM_MapControlMath.Due(ref carry, 0.75f) <= 1, "a blocked 0.75 source burst when it cleared");
            });
            Case("MapControl_pick_targets", () =>
            {
                Assert(RM_MapControlMath.PickPourTarget(new List<int>()) == -1, "pour into nothing");
                Assert(RM_MapControlMath.PickPourTarget(new List<int> { -1, -3, -3, 0 }) == 1, "pour not into the lowest surface, first wins");
                Assert(RM_MapControlMath.PickDrainTarget(new List<int> { 0, 0 }) == -1, "drained a dry reach");
                Assert(RM_MapControlMath.PickDrainTarget(new List<int> { 1, 3, 3, 2 }) == 1, "drain not from the fullest, first wins");
            });
            Case("MapControl_source_and_sink_conserve_through_the_kernel", () =>
            {
                // A 12-square channel dug to 2: a 0.5/pulse source at square 0, a 0.25/pulse sink at square 11. The taps
                // act before the kernel, as RM_MapComponent_Excavation.DoPulse runs them, so the kernel's own ledger must
                // balance every pulse, and the channel must hold exactly poured - drained.
                const int W = 12;
                var world = new ArrayWorld(W, 1);
                var k = world.k;
                k.flowPerPulse = 1;
                k.levelBySurfaceEnabled = true;
                k.creepWaterEnabled = true;
                // In game the source pours through TrySetDriverFill, which marks its squares as driver inputs that seed the
                // flow order (FLOW_ORDER_EXTERNAL_INPUT_1); the same here, or a flat channel never spreads away from it.
                k.externalInput = c => c == 0 || c == 1;
                for (int i = 0; i < W; i++) k.depth[i] = 2;
                var seeds = Enumerable.Range(0, W).ToList();
                float sc = 0f, kc = 0f;
                int poured = 0, drained = 0, sinkSawWater = -1;
                for (int p = 1; p <= 400; p++)
                {
                    int due = RM_MapControlMath.Due(ref sc, 0.5f);
                    for (int n = 0; n < due; n++)
                    {
                        var reach = new List<int> { 0, 1 }.Where(c => k.fill[c] < k.depth[c]).ToList();
                        int pick = RM_MapControlMath.PickPourTarget(reach.Select(c => k.fill[c] - k.depth[c]).ToList());
                        if (pick < 0) break;
                        int cell = reach[pick];
                        if (k.fill[cell] == 0) world.cellFluid[cell] = ArrayWorld.Water;
                        k.fill[cell]++;
                        poured++;
                    }
                    int dueOut = RM_MapControlMath.Due(ref kc, 0.25f);
                    for (int n = 0; n < dueOut; n++)
                    {
                        var reach = new List<int> { 11, 10 };
                        int pick = RM_MapControlMath.PickDrainTarget(reach.Select(c => (int)k.fill[c]).ToList());
                        if (pick < 0) break;
                        k.fill[reach[pick]]--;
                        drained++;
                        if (sinkSawWater < 0) sinkSawWater = p;
                    }
                    world.Pulse(seeds);
                    Assert(k.worstImbalance < 0.001f, "pulse " + p + ": the kernel ledger did not balance: " + string.Join("; ", k.imbalanceReports));
                    int held = 0;
                    for (int i = 0; i < W; i++) held += k.fill[i];
                    Assert(held == poured - drained, "pulse " + p + ": channel holds " + held + ", poured " + poured + " - drained " + drained);
                }
                // A 0.5 source out-pours a 0.25 sink, so the channel fills and the source backs up (it never banks).
                Assert(poured <= 200, "a 0.5 source over 400 pulses poured " + poured + ", more than its rate");
                Assert(poured - drained >= 2 * W - 4 && poured - drained <= 2 * W, "the channel did not fill: holds " + (poured - drained) + "\n" + world.Grid());
                Assert(sinkSawWater > 0, "the water never reached the sink 11 squares away:\n" + world.Grid());
                Assert(drained > 0 && drained <= 100, "a 0.25 sink took " + drained + " over 400 pulses");
            });
            Case("MapControl_wiring_and_master_switch", () =>
            {
                string root = ModRoot();
                string ex = File.ReadAllText(Path.Combine(root, "Source", "RM_MapComponent_Excavation.cs"));
                string pulse = Between(ex, "private void DoPulse()", "flowKernel.Pulse(pulseSeeds, pulseCount);");
                int rain = pulse.IndexOf("ApplyRain();", StringComparison.Ordinal);
                int taps = pulse.IndexOf("MapControls.RM_MapControls.PulseAll(map, this);", StringComparison.Ordinal);
                Assert(rain >= 0 && taps > rain, "DoPulse does not run the map controls after rain and before the kernel");
                Assert(ex.Contains("flowSources=") && ex.Contains("flowSinks="), "the L0 ledger report does not disclose the map controls");
                string mc = File.ReadAllText(Path.Combine(root, "Source", "MapControls", "RM_MapControls.cs"));
                string pa = Between(mc, "public static void PulseAll(", "private static IEnumerable<Building_RM_MapControl> All(");
                Assert(pa.Contains("if (!RM_MapControlSettings.mapControlsEnabled"), "the master switch does not gate PulseAll");
                Assert(pa.Contains("mc.active"), "a switched-off control still pulses");
                string taps2 = File.ReadAllText(Path.Combine(root, "Source", "MapControls", "RM_FlowTaps.cs"));
                Assert(taps2.Contains("ex.TryPourLevel(") && taps2.Contains("ex.CanPourLevel("), "the source does not pour through the engine's driver write");
                Assert(taps2.Contains("ex.TryTakeLevel("), "the sink does not take through the engine");
                Assert(taps2.Contains("ex.NoteMapControlFlow(done, 0)") && taps2.Contains("ex.NoteMapControlFlow(0, done)"), "a tap does not record its flow");
                string xml = File.ReadAllText(Path.Combine(root, "Defs", "Canals", "ThingDefs", "FlowWorks_MapControls.xml"));
                Assert(!xml.Contains("<designationCategory>"), "a map control is buildable (designationCategory)");
                Assert(!xml.Contains("<costList>"), "a map control has a build cost");
                Assert(xml.Contains("<defName>RM_FlowSource</defName>") && xml.Contains("<defName>RM_FlowSink</defName>"), "a map control def is missing");
            });
        }
    }
}
