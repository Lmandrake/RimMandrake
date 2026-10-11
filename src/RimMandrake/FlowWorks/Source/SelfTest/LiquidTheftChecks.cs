// Liquid networks build step L9 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.4, §6 L9; owner card
// Q4: a hose into another faction's tank is allowed, as theft, priced like power theft; ruling #7: 2 goodwill a day, 12-cell
// notice). The PRODUCTION rule (RM_LiquidTheftMath, a copy of Gimme Some Slack's AerialMath theft rule) with GSS's own cases
// (src/RimMandrake/GimmeSomeSlack/Source/SelfTest/TheftChecks.cs), the touched test, then the production tick read from source.
using System;
using System.IO;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LiquidTheftChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Theft_spotting_matches_power_theft", () =>
            {
                Assert(RM_LiquidTheftMath.TheftSpotted(5, 12, true, true, false), "an awake member 5 cells away with sight catches it");
                Assert(!RM_LiquidTheftMath.TheftSpotted(13, 12, true, true, false), "13 cells is out of a 12-cell sight range");
                Assert(!RM_LiquidTheftMath.TheftSpotted(5, 12, false, true, false), "a wall between them hides it");
                Assert(!RM_LiquidTheftMath.TheftSpotted(5, 12, true, false, false), "a sleeping or downed member sees nothing");
                Assert(!RM_LiquidTheftMath.TheftSpotted(5, 12, true, true, true), "our own prisoner is no witness");
                Assert(!RM_LiquidTheftMath.TheftSpotted(double.NaN, 12, true, true, false) && !RM_LiquidTheftMath.TheftSpotted(1, 0, true, true, false), "NaN or a zero range sees nothing");
            });

            Case("Theft_accrues_per_day_of_taking_and_idle_accrues_nothing", () =>
            {
                const int day = 60000, step = 250;
                int acc = 0, total = 0;
                for (int t = 0; t < day * 3; t += step) total += RM_LiquidTheftMath.TheftGoodwillAccrue(ref acc, step, true, 2, day);
                Assert(total == -6, "three days of caught taking at 2/day costs 6 goodwill (got " + total + ")");
                acc = 0; total = 0;
                for (int t = 0; t < day * 5; t += step) total += RM_LiquidTheftMath.TheftGoodwillAccrue(ref acc, step, false, 2, day);
                Assert(total == 0 && acc == 0, "an idle tank (nothing taken) accrues nothing over five days");
                acc = 0;
                Assert(RM_LiquidTheftMath.TheftGoodwillAccrue(ref acc, day * 2, true, 0, day) == 0, "a 0/day setting charges nothing");
                Assert(RM_LiquidTheftMath.TheftGoodwillAccrue(ref acc, day, true, 5, day) == -5, "the per-day setting is the charge");
                Assert(RM_LiquidTheftMath.Touched(40, "water", 35, "water") && RM_LiquidTheftMath.Touched(0, null, 5, "tar") && !RM_LiquidTheftMath.Touched(40, "water", 40, "water"),
                    "touched = its stock or liquid changed since the last look; a put-back nets to untouched");
            });

            Case("Theft_production_tick_join_and_switch", () =>
            {
                string th = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidTheft.cs"));
                RiverSwitchFlipChecks.Has(th, @"public static void TheftTick\(Map map\) \{ if \(map == null \|\| !RM_MachinerySettings\.liquidTheftEnabled\) \{ return; \}", "off: no theft tick");
                RiverSwitchFlipChecks.Has(th, @"bool touched = t\.theftSeenUnits >= 0 && RM_LiquidTheftMath\.Touched\(t\.theftSeenUnits, t\.theftSeenLiquid, t\.storedUnits, t\.storedLiquid\);", "touched = the stock changed");
                RiverSwitchFlipChecks.Has(th, @"int change = RM_LiquidTheftMath\.TheftGoodwillAccrue\(ref t\.theftTicks, RM_PumpMath\.CycleTicks, true, RM_MachinerySettings\.liquidTheftGoodwillPerDay, GenDate\.TicksPerDay\);",
                    "a caught tank accrues only in cycles it is touched");
                RiverSwitchFlipChecks.Has(th, @"if \(change >= 0 \|\| victim\.PlayerGoodwill <= -100 \|\| victim\.def\.permanentEnemy\) \{ continue; \}", "a faction at -100 or permanently hostile is skipped");
                RiverSwitchFlipChecks.Has(th, @"RM_LiquidTheftDefOf\.RM_LiquidTheftCaught", "the goodwill reason is FlowWorks' own history event");
                Assert(!th.Contains("GimmeSomeSlack"), "FlowWorks never references Gimme Some Slack");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"if \(\(role == RM_NetRole\.Tank \|\| role == RM_NetRole\.Machine\) && !RM_MachinerySettings\.liquidTheftEnabled && IsForeign\(t\)\) \{ return RM_NetRole\.None; \}",
                    "off: another faction's tank or machine never joins");
                RiverSwitchFlipChecks.Has(net, @"RevisionKey\(s\.revision, RM_MachinerySettings\.universalPipesEnabled, RM_HoseSettings\.enabled, RM_MachinerySettings\.liquidTheftEnabled\)", "switching it is a new revision");
                Assert(RM_LiquidNetKernel.RevisionKey(3, true, true, true) != RM_LiquidNetKernel.RevisionKey(3, true, true, false), "the key separates it");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"Machinery\.RM_LiquidNet\.SettleTick\(map\); Machinery\.RM_LiquidTheft\.TheftTick\(map\);", "the theft tick runs once per pump cycle");
            });
        }
    }
}
