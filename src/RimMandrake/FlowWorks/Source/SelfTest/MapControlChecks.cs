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

            // ── FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: the six further controls ──────────────────────
            Case("MapControl_level_holder_need", () =>
            {
                Assert(RM_MapControlMath.LevelHolderNeed(0, 0, 0.5f) == 0, "no room still asks for liquid");
                Assert(RM_MapControlMath.LevelHolderNeed(0, 10, 0.5f) == 5, "empty 10 at 50% does not ask for 5");
                Assert(RM_MapControlMath.LevelHolderNeed(10, 10, 0.5f) == -5, "full 10 at 50% does not give 5");
                Assert(RM_MapControlMath.LevelHolderNeed(5, 10, 0.5f) == 0, "at setpoint still moves");
                Assert(RM_MapControlMath.LevelHolderNeed(0, 5, 0.5f) == 3, "2.5 does not round up to 3");
                Assert(RM_MapControlMath.LevelHolderNeed(3, 8, float.NaN) == -3, "NaN setpoint not read as 0");
                Assert(RM_MapControlMath.LevelHolderNeed(3, 8, 7f) == 5, "setpoint above 1 not clamped");
            });
            Case("MapControl_level_holder_conserves_through_the_kernel", () =>
            {
                // A 10-square channel dug to 4, a level holder at square 0 with reach {0,1} holding 50% at 1/pulse, and a
                // 0.25/pulse sink at square 9. The holder must keep its reach at 4 of 8 levels in steady state, the kernel
                // ledger must balance every pulse, and the channel must hold exactly poured - taken - drained.
                const int W = 10;
                var world = new ArrayWorld(W, 1);
                var k = world.k;
                k.flowPerPulse = 1;
                k.levelBySurfaceEnabled = true;
                k.creepWaterEnabled = true;
                k.externalInput = c => c == 0 || c == 1;
                for (int i = 0; i < W; i++) k.depth[i] = 4;
                var seeds = Enumerable.Range(0, W).ToList();
                float hc = 0f, sc = 0f;
                int poured = 0, taken = 0, drained = 0;
                int[] reach = { 0, 1 };
                for (int p = 1; p <= 600; p++)
                {
                    int due = RM_MapControlMath.Due(ref hc, 1f);
                    for (int n = 0; n < due; n++)
                    {
                        int held = k.fill[0] + k.fill[1];
                        int need = RM_MapControlMath.LevelHolderNeed(held, k.depth[0] + k.depth[1], 0.5f);
                        if (need == 0) break;
                        if (need > 0)
                        {
                            var cand = reach.Where(c => k.fill[c] < k.depth[c]).ToList();
                            int pick = RM_MapControlMath.PickPourTarget(cand.Select(c => k.fill[c] - k.depth[c]).ToList());
                            if (pick < 0) break;
                            if (k.fill[cand[pick]] == 0) world.cellFluid[cand[pick]] = ArrayWorld.Water;
                            k.fill[cand[pick]]++;
                            poured++;
                        }
                        else
                        {
                            int pick = RM_MapControlMath.PickDrainTarget(reach.Select(c => (int)k.fill[c]).ToList());
                            if (pick < 0) break;
                            k.fill[reach[pick]]--;
                            taken++;
                        }
                    }
                    if (p > 300)
                    {
                        for (int n = RM_MapControlMath.Due(ref sc, 0.25f); n > 0; n--)
                        {
                            if (k.fill[9] > 0) { k.fill[9]--; drained++; }
                        }
                    }
                    world.Pulse(seeds);
                    Assert(k.worstImbalance < 0.001f, "pulse " + p + ": the kernel ledger did not balance: " + string.Join("; ", k.imbalanceReports));
                    int total = 0;
                    for (int i = 0; i < W; i++) total += k.fill[i];
                    Assert(total == poured - taken - drained, "pulse " + p + ": channel holds " + total + ", poured " + poured + " - taken " + taken + " - drained " + drained);
                    if (p == 300)
                    {
                        // No drain yet: the whole channel levels at about half full (the holder fills to 50% of its reach,
                        // the channel spreads it, the holder tops up), never over.
                        Assert(total >= 2 * W - 2 && total <= 2 * W + 2, "channel not held near half full: " + total + "\n" + world.Grid());
                    }
                }
                int reachHeld = k.fill[0] + k.fill[1];
                Assert(reachHeld >= 3 && reachHeld <= 5, "the holder's reach is not near 4 of 8 with a sink running: " + reachHeld + "\n" + world.Grid());
                Assert(drained > 0, "the sink never drained");
            });
            Case("MapControl_timer_schedule", () =>
            {
                int H = RM_MapControlMath.TimerByHours, P = RM_MapControlMath.TimerByPeriod;
                Assert(RM_MapControlMath.TimerOn(H, 6f, 6, 18, 0, 0, 0, false), "6:00 not on for 6-18");
                Assert(!RM_MapControlMath.TimerOn(H, 18f, 6, 18, 0, 0, 0, false), "18:00 still on for 6-18 (end is exclusive)");
                Assert(RM_MapControlMath.TimerOn(H, 23.5f, 18, 6, 0, 0, 0, false) && RM_MapControlMath.TimerOn(H, 2f, 18, 6, 0, 0, 0, false), "18-6 does not wrap midnight");
                Assert(!RM_MapControlMath.TimerOn(H, 12f, 18, 6, 0, 0, 0, false), "noon on for 18-6");
                Assert(RM_MapControlMath.TimerOn(H, 12f, 3, 3, 0, 0, 0, false), "start == end is not all day");
                Assert(!RM_MapControlMath.TimerOn(H, 12f, 6, 18, 0, 0, 0, true), "invert does not flip");
                Assert(RM_MapControlMath.TimerOn(P, 0f, 0, 0, 0, 24f, 6f, false), "period start not on");
                Assert(!RM_MapControlMath.TimerOn(P, 0f, 0, 0, 2500L * 7, 24f, 6f, false), "hour 7 of a 6-on/24 period is on");
                Assert(RM_MapControlMath.TimerOn(P, 0f, 0, 0, 2500L * 25, 24f, 6f, false), "the period does not repeat");
                RM_MapControlMath.TimerOn(P, 0f, 0, 0, 2500L * 5, 0f, 1f, false);   // a zero period must not throw (the answer is not asserted)
                int onCount = 0;
                for (long t = 0; t < 2500L * 24 * 10; t += 250) if (RM_MapControlMath.TimerOn(P, 0f, 0, 0, t, 12.4f, 1f, false)) onCount++;
                double frac = onCount / (2500.0 * 24 * 10 / 250);
                Assert(Math.Abs(frac - 1.0 / 12.4) < 0.01, "a 1-in-12.4 h tide is on " + frac + " of the time");
            });
            Case("MapControl_edge_rules", () =>
            {
                int A = RM_MapControlMath.EdgeAuto, S = RM_MapControlMath.EdgeSealed, D = RM_MapControlMath.EdgeDrain;
                Assert(!RM_MapControlMath.EdgeSink(null, false, false, false, false, true), "an inland square is a sink");
                Assert(RM_MapControlMath.EdgeSink(null, true, false, false, false, true), "no setter: the automatic rule is not kept");
                Assert(!RM_MapControlMath.EdgeSink(null, true, false, false, false, false), "no setter: sinks with the automatic rule off");
                int[] m = { S, D, A, A };
                Assert(!RM_MapControlMath.EdgeSink(m, true, false, false, false, true), "a sealed north edge drains");
                Assert(RM_MapControlMath.EdgeSink(m, false, true, false, false, false), "a drain east edge does not drain with the automatic rule off");
                Assert(RM_MapControlMath.EdgeSink(m, true, true, false, false, false), "the NE corner (sealed + drain) does not drain");
                Assert(RM_MapControlMath.EdgeSink(m, false, false, true, false, true) && !RM_MapControlMath.EdgeSink(m, false, false, true, false, false), "an automatic south edge does not follow the automatic rule");
                Assert(RM_MapControlMath.EdgeSink(m, true, false, false, true, true), "the NW corner (sealed + automatic) ignores the automatic edge");
                RM_MapControlMath.BodyEdges(m, true, false, false, false, out bool open, out bool drain);
                Assert(!open && !drain, "a body on the sealed edge only counts as edge-touching");
                RM_MapControlMath.BodyEdges(m, true, true, false, false, out open, out drain);
                Assert(open && drain, "a body on the drain edge is not limitless");
                RM_MapControlMath.BodyEdges(m, false, false, true, false, out open, out drain);
                Assert(open && !drain, "a body on an automatic edge lost its edge contact");
                RM_MapControlMath.BodyEdges(m, false, false, false, false, out open, out drain);
                Assert(!open && !drain, "an inland body touches an edge");
            });
            Case("MapControl_thermostat_energy", () =>
            {
                Assert(RM_MapControlMath.ThermostatEnergy(0, 10f, 20, 30f, 1f) == 0f, "no liquid moved heat");
                Assert(RM_MapControlMath.ThermostatEnergy(4, 21f, 20, 21f, 1f) == 0f, "at the setting moved heat");
                Assert(RM_MapControlMath.ThermostatEnergy(4, 10f, 20, 30f, 0f) == 0f, "strength 0 moved heat");
                float warm = RM_MapControlMath.ThermostatEnergy(4, 10f, 20, 30f, 1f);
                Assert(Math.Abs(warm - 3f * 4 * (250 / 60f)) < 1e-3, "warming is not 3 per level per second: " + warm);
                float chill = RM_MapControlMath.ThermostatEnergy(4, 30f, 20, 10f, 1f);
                Assert(Math.Abs(chill + 2f * 4 * (250 / 60f)) < 1e-3, "chilling is not 2 per level per second: " + chill);
                Assert(RM_MapControlMath.ThermostatEnergy(1000, -50f, 1000, 100f, 1f) <= 8f * 21f * (250 / 60f) + 1e-3, "the per-room cap does not hold");
                // Never past the setting: a 1-cell room 0.5 below the target takes at most 0.5.
                Assert(RM_MapControlMath.ThermostatEnergy(50, 20.5f, 1, 21f, 1f) <= 0.5001f, "pushed past the setting");
                Assert(RM_MapControlMath.ThermostatEnergy(50, 21.5f, 1, 21f, 1f) >= -0.5001f, "chilled past the setting");
                // A room settles: iterate Room.Temperature += e / cells.
                float temp = -10f;
                for (int i = 0; i < 2000; i++) temp += RM_MapControlMath.ThermostatEnergy(6, temp, 30, 40f, 1f) / 30f;
                Assert(Math.Abs(temp - 40f) < 0.01f, "a room does not settle at the setting: " + temp);
                Assert(Math.Abs(RM_MapControlMath.PerDay(5f, 30000) - 10f) < 1e-4 && RM_MapControlMath.PerDay(5f, 0) == 0f, "PerDay is wrong");
            });
            Case("MapControl_six_wiring", () =>
            {
                string root = ModRoot();
                string src = Path.Combine(root, "Source");
                string ex = File.ReadAllText(Path.Combine(src, "RM_MapComponent_Excavation.cs"));
                string sink = Between(ex, "public bool IsSinkCell(IntVec3 c)", "public float SinkTransferredTotal");
                Assert(sink.Contains("RM_MapControls.EdgeModes(map) != null") && sink.Contains("RM_MapControls.EdgeSinkAt(map, c, RimMandrakeFlowWorksSettings.edgeSinksEnabled)"), "IsSinkCell does not read the map-edge setter");
                Assert(ex.Contains("flowKernel.edgeSinksEnabled = RimMandrakeFlowWorksSettings.edgeSinksEnabled || MapControls.RM_MapControls.AnyDrainEdge(map);"), "the kernel's edge-sink gate does not open for a drain edge");
                Assert(ex.Contains("if (flowKernel.edgeSinksEnabled)\n") || ex.Contains("if (flowKernel.edgeSinksEnabled)\r\n"), "drain-edge transfers are not added to the sink total");
                string stock = File.ReadAllText(Path.Combine(src, "RM_LiquidStock.cs"));
                Assert(stock.Contains("RM_MapControls.BodyEdgeContact(map, edgeModes, fillFound, out touchesEdge, out drainEdge)") && stock.Contains("body.limitless = drainEdge ||"), "body classification ignores the map-edge setter");
                string heat = File.ReadAllText(Path.Combine(src, "RM_LiquidHeat.cs"));
                int push = heat.IndexOf("Push(map, ex, RimMandrakeFlowWorksSettings.liquidHeatStrength);", StringComparison.Ordinal);
                int therm = heat.IndexOf("MapControls.RM_MapControls.HeatAll(map, ex, RimMandrakeFlowWorksSettings.liquidHeatStrength);", StringComparison.Ordinal);
                int gate = heat.IndexOf("if (!RimMandrakeFlowWorksSettings.liquidHeatPushEnabled)", StringComparison.Ordinal);
                Assert(push > 0 && therm > push && gate > 0 && gate < therm, "the thermostat is not run after the liquid-heat push, behind its switch");
                string cur = File.ReadAllText(Path.Combine(src, "Rivers", "RM_MapComponent_RiverCurrent.cs"));
                Assert(cur.Contains("if (Painted(c, out int pi))") && cur.Contains("Painted(c, out int pi) ? paintLane[pi]"), "the river current does not read painted squares");
                Assert(cur.Contains("if (!anyCurrent && paintedCount == 0)"), "a map with only painted current never ticks it");
                string mc = File.ReadAllText(Path.Combine(src, "MapControls", "RM_MapControls.cs"));
                foreach (string fn in new[] { "private static void RefreshEdgeCache(Map map)", "public static int PaintCurrent(", "public static void HeatAll(" })
                {
                    Assert(Between(mc, fn, "List<Thing>").Contains("RM_MapControlSettings.mapControlsEnabled"), fn + " is not behind the master switch");
                }
                string timer = File.ReadAllText(Path.Combine(src, "MapControls", "RM_TimerSwitch.cs"));
                Assert(timer.Contains("mc.TimerSwitchable") && timer.Contains("RM_FlowDoorRules.IsFlowDoor(door)"), "the timer does not switch controls and flow doors");
                string holder = File.ReadAllText(Path.Combine(src, "MapControls", "RM_LevelHolder.cs"));
                Assert(holder.Contains("ex.TryPourLevel(") && holder.Contains("ex.TryTakeLevel(") && holder.Contains("ex.NoteMapControlFlow(poured, taken)"), "the level holder does not move liquid through the engine and the ledger");
                Assert(holder.Contains("ex.Stock.TryCredit(") && holder.Contains("ex.Stock.TryDebit("), "the level holder does not hold a body through the stock");
                string xml = File.ReadAllText(Path.Combine(root, "Defs", "Canals", "ThingDefs", "FlowWorks_MapControls.xml"));
                foreach (string d in new[] { "RM_FlowMeter", "RM_LevelHolder", "RM_TimerSwitch", "RM_MapEdgeSetter", "RM_CurrentPainter", "RM_LiquidThermostat" })
                    Assert(xml.Contains("<defName>" + d + "</defName>"), d + " def missing");
                Assert(xml.Contains("<texPath>Things/Item/Chunk/ChunkStone</texPath>") && !xml.Contains("PenMarker"), "map controls are not small stones (owner 2026-10-16)");
                Assert(!xml.Contains("<designationCategory>") && !xml.Contains("<costList>"), "a map control is buildable");
                string csproj = File.ReadAllText(Path.Combine(src, "RimMandrake_FlowWorks.csproj"));
                foreach (string f in new[] { "RM_FlowMeter", "RM_LevelHolder", "RM_TimerSwitch", "RM_EdgeSetter", "RM_CurrentPainter", "RM_LiquidThermostat" })
                    Assert(csproj.Contains("MapControls\\" + f + ".cs"), f + ".cs not compiled");
            });
        }
    }
}
