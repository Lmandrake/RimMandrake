// Review S2/S3 of the hose port (Transient/hose_port_offline_review_2026-10-11.md), revised by liquid networks L4: the tank-jobs
// switch (RM_HoseSettings.tankModesEnabled, default on; it replaced tanksFeedHoses and reads its old key once), and a tank-to-tank
// transfer whose destination refuses the units puts them back and credits nothing. Flipped through the Verse-free RM_LiquidNetKernel gates, then the PRODUCTION
// call site is read so the flip proven here is the flip the game makes (the RiverSwitchFlipChecks pattern).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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
            // L4 (rev 2 §3.11): tanksFeedHoses became tankModesEnabled (the old key is read once on load)
            Case("HoseSwitchFlip_tankModesEnabled", () =>
            {
                var jobs = new List<RM_SettleTank> { new RM_SettleTank(1, 50, 100, "water", RM_TankMode.Empty), new RM_SettleTank(2, 0, 100, null, RM_TankMode.Store) };
                var off = jobs.Select(t => new RM_SettleTank(t.Id, t.Units, t.Cap, t.Liquid, RM_TankMode.Store)).ToList();   // EffectiveMode with the switch off
                Assert(RM_LiquidNetKernel.SettlePlan(jobs, 10, 0).Count == 1, "on: an Empty tank sends to the Store tank");
                Assert(RM_LiquidNetKernel.SettlePlan(off, 10, 0).Count == 0, "off: every tank is Store and nothing moves (never the old equalising)");
                string tank = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidTank.cs"));
                RiverSwitchFlipChecks.Has(tank, @"public Machinery\.RM_TankMode EffectiveMode => Hose\.RM_HoseSettings\.tankModesEnabled && Faction == RimWorld\.Faction\.OfPlayer \? mode : Machinery\.RM_TankMode\.Store;",
                    "the job in force is Store with the switch off");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"public static void SettleTick\(Map map\) \{ if \(map == null \|\| !RM_HoseSettings\.tankModesEnabled\) \{ return; \}", "SettleTick returns first with the switch off");
                string set = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_HoseSettings.cs"));
                RiverSwitchFlipChecks.Has(set, @"public static bool tankModesEnabled = true;", "default on");
                RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref tankModesEnabled, ""hose_tankModesEnabled"", true\);", "saved under hose_tankModesEnabled");
                RiverSwitchFlipChecks.Has(set, @"Scribe\.loader\.curXmlParent\?\[""hose_tankModesEnabled""\] == null && Scribe\.loader\.curXmlParent\?\[""hose_tanksFeedHoses""\] is System\.Xml\.XmlNode legacyFeed && bool\.TryParse\(legacyFeed\.InnerText, out bool fed\)\) \{ tankModesEnabled = fed; \}",
                    "the old hose_tanksFeedHoses value is read once when the new key was never written");
                RiverSwitchFlipChecks.Has(set, @"list\.CheckboxLabeled\(""Tank jobs[^""]*"", ref tankModesEnabled,", "a checkbox in the settings window");
                Assert(!set.Contains("tanksFeedHoses ="), "no tanksFeedHoses field is left");
            });

            // L5 (rev 2 §3.4): hose free ends take a role; off, every free end is Capped (no port)
            Case("HoseSwitchFlip_freeEndRolesEnabled", () =>
            {
                RM_NetComponent Comp(RM_FreeEndRole role)
                {
                    var g = new HoseNetChecks.G();
                    HoseNetChecks.G.Add(g.PipeOf, "P1", "c1");
                    g.Links.Add(new RM_NetLink { Id = 0, A = "c1", B = new RM_NetPort { Reel = "R1", Cell = "lake", Role = role }, Reel = "R1" });
                    return new RM_NetComponents(g).ComponentsOf("P1")[0];
                }
                Assert(Comp(RM_FreeEndRole.Intake).Ports.Count == 1 && Comp(RM_FreeEndRole.Outflow).Ports.Count == 1, "on: an Intake or Outflow end is a port of its network");
                Assert(Comp(RM_FreeEndRole.Capped).Ports.Count == 0, "off (every end Capped): no port");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"public static RM_FreeEndRole FreeEndRole\(CompHoseReel r\) => RM_HoseSettings\.freeEndRolesEnabled \? r\.freeEndRole : RM_FreeEndRole\.Capped;", "the role in force is Capped with the switch off");
                RiverSwitchFlipChecks.Has(net, @"else if \(e\.Port == null\) \{ RM_FreeEndRole role = FreeEndRole\(r\); if \(role != RM_FreeEndRole\.Capped\) \{ far = new RM_NetPort", "a role counts only while the end lies free (inert when coupled)");
                string reel = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "CompHoseReel.cs"));
                RiverSwitchFlipChecks.Has(reel, @"Scribe_Values\.Look\(ref freeEndRole, ""rmFreeEndRole"", Machinery\.RM_FreeEndRole\.Capped\);", "saved as rmFreeEndRole, default Capped (old saves: Capped)");
                RiverSwitchFlipChecks.Has(reel, @"if \(RM_HoseSettings\.freeEndRolesEnabled\) yield return new Command_Action \{ defaultLabel = ""Free end: "" \+ freeEndRole,", "the role button shows only with the switch on");
                RiverSwitchFlipChecks.Has(reel, @"freeEndRole = \(Machinery\.RM_FreeEndRole\)\(\(\(int\)freeEndRole \+ 1\) % 3\); Machinery\.RM_LiquidNet\.Bump\(parent\.Map\);", "a role change bumps the topology revision");
                string set = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_HoseSettings.cs"));
                RiverSwitchFlipChecks.Has(set, @"public static bool freeEndRolesEnabled = true;", "default on");
                RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref freeEndRolesEnabled, ""hose_freeEndRolesEnabled"", true\);", "saved under hose_freeEndRolesEnabled");
                RiverSwitchFlipChecks.Has(set, @"list\.CheckboxLabeled\(""Hose free ends[^""]*"", ref freeEndRolesEnabled,", "a checkbox in the settings window");
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
                    "SettleTick moves units through RM_LiquidTransfer.Move (remove, checked add, put back) and credits the units moved");
                Assert(!net.Contains("dst.TryAddLiquid(liquid, n);"), "no unchecked TryAddLiquid left in the tank feed");
            });
        }
    }
}
