// Review S2/S3 of the hose port (Transient/hose_port_offline_review_2026-10-11.md): the owner's Q7 tank feed gets its own
// Mod Settings switch (RM_HoseSettings.tanksFeedHoses, default on), and a tank-feed transfer whose destination refuses the
// units puts them back and credits nothing. Flipped through the Verse-free RM_LiquidNetKernel gates, then the PRODUCTION
// call site is read so the flip proven here is the flip the game makes (the RiverSwitchFlipChecks pattern).
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseSwitchFlipChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HoseSwitchFlip_tanksFeedHoses", () =>
            {
                Assert(RM_LiquidNetKernel.TankFeedOn(true, true), "both on: a tank feeds a hose");
                Assert(!RM_LiquidNetKernel.TankFeedOn(true, false), "tanksFeedHoses off: no tank feed with hoses on");
                Assert(!RM_LiquidNetKernel.TankFeedOn(false, true), "the hose master off still stops the tank feed");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net,
                    @"public static void TankFeedTick\(Map map\) \{ if \(map == null \|\| !RM_LiquidNetKernel\.TankFeedOn\(RM_HoseSettings\.enabled, RM_HoseSettings\.tanksFeedHoses\)\) \{ return; \}",
                    "TankFeedTick returns first unless TankFeedOn(enabled, tanksFeedHoses)");
                string set = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_HoseSettings.cs"));
                RiverSwitchFlipChecks.Has(set, @"public static bool tanksFeedHoses = true;", "default on (the owner's ruling)");
                RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref tanksFeedHoses, ""hose_tanksFeedHoses"", true\);", "saved under hose_tanksFeedHoses");
                RiverSwitchFlipChecks.Has(set, @"list\.CheckboxLabeled\(""Tanks feed hoses[^""]*"", ref tanksFeedHoses,", "a checkbox in the settings window");
            });

            Case("HoseTankFeed_refused_add_puts_back", () =>
            {
                int src = 100, dst = 0, credited = 0;
                bool Remove(int k) { if (src < k) return false; src -= k; return true; }
                bool PutBack(int k) { src += k; return true; }
                void Credit(int k) { credited += k; }
                // the destination refuses: the units go back, nothing is credited
                int moved = RM_LiquidNetKernel.TankFeedTransfer(5, Remove, k => false, PutBack, Credit, out bool lost);
                Assert(moved == 0 && src == 100 && dst == 0 && credited == 0 && !lost,
                       "refused add: moved " + moved + ", src " + src + ", credited " + credited + " (want 0/100/0)");
                // the destination accepts: units move and the route is credited with them
                moved = RM_LiquidNetKernel.TankFeedTransfer(5, Remove, k => { dst += k; return true; }, PutBack, Credit, out lost);
                Assert(moved == 5 && src == 95 && dst == 5 && credited == 5 && !lost, "accepted add: 5 moved and credited");
                // neither will take them: reported as lost, never credited
                moved = RM_LiquidNetKernel.TankFeedTransfer(5, Remove, k => false, k => false, Credit, out lost);
                Assert(moved == 0 && lost && credited == 5, "put-back refused too: reported lost, no credit");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net,
                    @"RM_LiquidNetKernel\.TankFeedTransfer\(n, k => src\.TryRemoveLiquid\(k\), k => dst\.TryAddLiquid\(liquid, k\), k => src\.TryAddLiquid\(liquid, k\), k => CreditRoute\(",
                    "TankFeedTick moves units through TankFeedTransfer (remove, checked add, put back, credit)");
                Assert(!net.Contains("dst.TryAddLiquid(liquid, n);"), "no unchecked TryAddLiquid left in the tank feed");
            });
        }
    }
}
