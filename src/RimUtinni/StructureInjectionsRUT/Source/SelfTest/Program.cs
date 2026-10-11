using System;
using System.Collections.Generic;
using RimMandrake.Utinni.StructureInjectionsRUT;

namespace StructureInjectionsRUT.SelfTest
{
    // RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT: asserts the counting rule the
    // live GameComponent_WokenAncients polls with. Exit 0 = all pass.
    internal static class Program
    {
        private static int failures;
        private static int checks;

        private static void Check(bool ok, string what)
        {
            checks++;
            if (!ok)
            {
                failures++;
            }
            Console.WriteLine((ok ? "PASS  " : "FAIL  ") + what);
        }

        private static CasketObservation C(int id, int sleepers, bool destroyed = false)
        {
            return new CasketObservation(id, sleepers, destroyed);
        }

        private static int Main()
        {
            var snap = new Dictionary<int, int>();

            // First sight only seeds: a vault map generating with 4 sleepers wakes no one.
            int w = WokenAncientsKernel.Observe(snap, new[] { C(1, 1), C(2, 1), C(3, 1), C(4, 1) });
            Check(w == 0, "first poll seeds the snapshot and counts nothing (got " + w + ")");

            // Nothing changes: nothing counted.
            w = WokenAncientsKernel.Observe(snap, new[] { C(1, 1), C(2, 1), C(3, 1), C(4, 1) });
            Check(w == 0, "unchanged caskets count nothing (got " + w + ")");

            // Casket 1 ejected (Open job), casket 2 ejected too (vanilla group eject).
            w = WokenAncientsKernel.Observe(snap, new[] { C(1, 0), C(2, 0), C(3, 1), C(4, 1) });
            Check(w == 2, "two caskets emptied while standing = 2 woken (got " + w + ")");

            // Re-polling the already-empty caskets does not count them again.
            w = WokenAncientsKernel.Observe(snap, new[] { C(1, 0), C(2, 0), C(3, 1), C(4, 1) });
            Check(w == 0, "an emptied casket is counted once (got " + w + ")");

            // Casket 3 destroyed with its sleeper inside = LOOT, wakes nobody.
            w = WokenAncientsKernel.Observe(snap, new[] { C(1, 0), C(2, 0), C(3, 1, destroyed: true), C(4, 1) });
            Check(w == 0, "a casket destroyed with sleepers wakes nobody (got " + w + ")");
            Check(!snap.ContainsKey(3), "a destroyed casket leaves the snapshot");

            // A multi-sleeper casket counts every sleeper in it.
            var snap2 = new Dictionary<int, int>();
            WokenAncientsKernel.Observe(snap2, new[] { C(10, 3) });
            w = WokenAncientsKernel.Observe(snap2, new[] { C(10, 0) });
            Check(w == 3, "a casket of three emptied = 3 woken (got " + w + ")");

            // A casket that was empty when first seen and stays empty counts nothing.
            var snap3 = new Dictionary<int, int>();
            WokenAncientsKernel.Observe(snap3, new[] { C(20, 0) });
            w = WokenAncientsKernel.Observe(snap3, new[] { C(20, 0) });
            Check(w == 0, "an always-empty casket counts nothing (got " + w + ")");

            // Threshold: N fires, N-1 does not (the item's quicktest criterion, offline).
            const int n = 10;
            Check(!WokenAncientsKernel.ShouldFire(true, false, n - 1, n), "N-1 woken does not fire");
            Check(WokenAncientsKernel.ShouldFire(true, false, n, n), "N woken fires");
            Check(WokenAncientsKernel.ShouldFire(true, false, n + 5, n), "more than N woken fires");
            Check(!WokenAncientsKernel.ShouldFire(true, true, n, n), "fires only once");
            Check(!WokenAncientsKernel.ShouldFire(false, false, n, n), "settings toggle off never fires");
            Check(WokenAncientsKernel.ShouldFire(true, false, 1, 0), "a threshold below 1 is treated as 1");
            Check(!WokenAncientsKernel.ShouldFire(true, false, 0, 0), "zero woken never fires");

            Console.WriteLine($"{checks - failures}/{checks} checks passed");
            return failures == 0 ? 0 : 1;
        }
    }
}
