// GSS_CORD_SILENCE_PHANTOM_SPARK (owner 2026-10-16, FW station carry_tanks): a conduit run ending beside a pump that vanilla
// wired straight to the battery drew a second, free, sparking cord. Scene mirrors the station: pump (5,2), conduit (5,3..5),
// battery (6,5) 1x2. Each row carries its can-fail: the old wiring (pump linked to the battery) beside the new pick.
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class PhantomSparkChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "phantom-spark: " + msg);

        private static CordWorld Scene(out MachineInfo pump, out MachineInfo bat)
        {
            var w = new CordWorld(12, 12);
            for (int z = 3; z <= 5; z++) w.SetConduit(new Cell(5, z));
            w.SetBlocked(new Cell(5, 2), BlockKind.Device);
            w.SetBlocked(new Cell(6, 5), BlockKind.Device);
            w.SetBlocked(new Cell(6, 6), BlockKind.Device);
            bat = new MachineInfo { Id = "tbat", Kind = MachineKind.Battery, X0 = 6, Z0 = 5, W = 1, H = 2 };
            bat.Hookups.Add(new Cell(5, 5));
            w.Machines.Add(bat);
            pump = new MachineInfo { Id = "cpump", Kind = MachineKind.Consumer, X0 = 5, Z0 = 2, W = 1, H = 1 };
            return w;
        }

        private static int FreeEnds(CordWorld w) =>
            new CordBuilder().Build(w, new BuildOptions { Seed = 1 }, c => true).Sum(p => p.Ends.Count);

        public static void Run()
        {
            // old: the pump is linked to the battery only -> the conduit end at (5,3) is free and sparks
            CordWorld wOld = Scene(out MachineInfo pOld, out MachineInfo bOld);
            CordWorldLinks.LinkToMachine(wOld, pOld, bOld);
            int oldEnds = FreeEnds(wOld);
            Check(oldEnds == 1, $"can-fail: battery-linked pump leaves the conduit end beside it free ({oldEnds} free ends, want 1)");

            // new: the pick hooks the same-net end beside the pump instead
            CordWorld wNew = Scene(out MachineInfo pNew, out MachineInfo bNew);
            List<Cell> pick = HookupPick.Pick(wNew, pNew, null, c => true);
            Check(pick != null && pick.Count == 1 && pick[0].Equals(new Cell(5, 3)), "pick hooks the conduit end (5,3) beside the pump");
            pNew.Hookups.AddRange(pick ?? new List<Cell>());
            wNew.Machines.Add(pNew);
            int newEnds = FreeEnds(wNew);
            Check(newEnds == 0, $"one cord battery -> conduit -> pump, no free end ({newEnds} free ends)");

            // a parent conduit already beside the pump: unchanged wiring
            CordWorld w2 = Scene(out MachineInfo p2, out _);
            Check(HookupPick.Pick(w2, p2, new Cell(5, 3), c => true) == null, "parent conduit beside the device keeps vanilla wiring");

            // other net: a conduit end beside the device on ANOTHER net stays free (a genuine loose end keeps its spark)
            CordWorld w3 = Scene(out MachineInfo p3, out _);
            Check(HookupPick.Pick(w3, p3, null, c => false) == null, "a different net's end beside the device is not adopted");

            // mid-run conduit beside the device (degree 2) is not an end: nothing to adopt
            CordWorld w4 = Scene(out MachineInfo p4, out _);
            w4.SetConduit(new Cell(4, 3)); w4.SetConduit(new Cell(6, 3));
            Check(HookupPick.Pick(w4, p4, null, c => true) == null, "a run passing beside the device (not an end) is not adopted");

            // a far parent conduit that is itself an end stays hooked beside the adopted end (never stranded)
            CordWorld w5 = Scene(out MachineInfo p5, out _);
            w5.SetConduit(new Cell(9, 9));
            List<Cell> pk5 = HookupPick.Pick(w5, p5, new Cell(9, 9), c => true);
            Check(pk5 != null && pk5.Count == 2 && pk5.Contains(new Cell(9, 9)), "a far parent end stays hooked beside the adopted end");
        }
    }
}
