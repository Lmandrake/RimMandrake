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
                // L1 (2026-10-11): the feed moves through the one transfer service, RM_LiquidTransfer.Move (TankFeedTransfer deleted);
                // the same three outcomes are asserted on Move with the feed's legs, plus can-time refusals
                int src = 100, dst = 0, credited = 0;
                bool srcBack = true;
                RM_TransferLeg Src() => RM_TransferLeg.Store(k => src >= k, k => { if (src < k) return false; src -= k; return true; }, k => { if (!srcBack) return false; src += k; return true; });
                RM_TransferLeg Dst(bool accept, bool can = true) => RM_TransferLeg.Store(k => can, k => { if (!accept) return false; dst += k; return true; }, k => { dst -= k; return true; });
                int Feed(RM_TransferLeg d, out RM_MoveOutcome o) { int m = RM_LiquidTransfer.Move(5, Src(), d, out o); if (m > 0) credited += m; return m; }
                // the destination refuses at Do: the units go back, nothing is credited
                int moved = Feed(Dst(false), out RM_MoveOutcome o1);
                Assert(moved == 0 && src == 100 && dst == 0 && credited == 0 && o1.Lost == 0 && o1.Refused == RM_MoveRefusal.DestDo,
                       "refused add: moved " + moved + ", src " + src + ", credited " + credited + " (want 0/100/0)");
                // the destination refuses at Can: nothing is even removed
                moved = Feed(Dst(true, false), out RM_MoveOutcome o2);
                Assert(moved == 0 && src == 100 && dst == 0 && credited == 0 && o2.Refused == RM_MoveRefusal.DestCan, "refused at validation: nothing moved");
                // the destination accepts: units move and the route is credited with them
                moved = Feed(Dst(true), out _);
                Assert(moved == 5 && src == 95 && dst == 5 && credited == 5, "accepted add: 5 moved and credited");
                // neither will take them: reported as lost, never credited
                srcBack = false;
                moved = Feed(Dst(false), out RM_MoveOutcome o3);
                Assert(moved == 0 && o3.Lost == 5 && credited == 5, "put-back refused too: reported lost, no credit");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net,
                    @"if \(RM_LiquidTransfer\.Move\(n, RM_TransferLeg\.Store\(k => src\.CanProvide\(k\), k => src\.TryRemoveLiquid\(k\), k => src\.TryAddLiquid\(liquid, k\)\), RM_TransferLeg\.Store\(k => dst\.CanAccept\(liquid, k\), k => dst\.TryAddLiquid\(liquid, k\), k => dst\.TryRemoveLiquid\(k\)\), out RM_MoveOutcome mv\) > 0\) \{ CreditRoute\(map, route, liquid, mv\.Moved,",
                    "TankFeedTick moves units through RM_LiquidTransfer.Move (remove, checked add, put back) and credits the units moved");
                Assert(!net.Contains("dst.TryAddLiquid(liquid, n);"), "no unchecked TryAddLiquid left in the tank feed");
            });
        }
    }
}
