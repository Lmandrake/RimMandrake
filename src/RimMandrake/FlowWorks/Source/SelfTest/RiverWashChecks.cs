// WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST (FlowWorks P10, GPT G4.3): a breach wash despawned each held stack and then
// tried to place it near the strand cell; when placement failed the stack was left unspawned (orphaned, lost). The
// per-stack rule now lives Verse-free in RM_RiverMath.WashHeld and RM_Building_BankWeir.WashCatch calls it. These
// cases drive the drop-failed path with fake things: the stack must come back at its old cell, a partial merge must
// still count, a fully merged (destroyed) stack must not be respawned. The can-fail runs the pre-fix rule beside it.
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks.Rivers;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class RiverWashChecks
    {
        private sealed class FakeThing
        {
            public int pos;            // cell id
            public int stack;
            public bool spawned = true;
            public bool destroyed;
            public int placeTakes;     // how much of the stack a failing placement merges away first
            public bool placeOk;
        }

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static int Wash(List<FakeThing> held, bool restore)
        {
            Func<FakeThing, bool> tryPlace = t =>
            {
                t.stack -= Math.Min(t.placeTakes, t.stack);
                if (t.stack == 0) { t.destroyed = true; return false; }   // merged away entirely
                if (t.placeOk) { t.spawned = true; t.pos = 999; return true; }
                return false;
            };
            if (restore)
                return RM_RiverMath.WashHeld(held, t => !t.destroyed && t.spawned, t => t.pos, t => t.stack,
                    t => t.spawned = false, tryPlace, t => t.destroyed, (t, from) => { t.spawned = true; t.pos = from; });
            // the pre-fix body: despawn, try to place, nothing on failure
            int moved = 0;
            foreach (FakeThing t in held)
            {
                if (t.destroyed || !t.spawned) continue;
                t.spawned = false;
                if (tryPlace(t)) moved++;
            }
            return moved;
        }

        private static List<FakeThing> Scene() => new List<FakeThing>
        {
            new FakeThing { pos = 1, stack = 10, placeOk = true },                 // placed fine
            new FakeThing { pos = 2, stack = 10, placeOk = false },                // placement fails outright
            new FakeThing { pos = 3, stack = 10, placeOk = false, placeTakes = 4 },// partial merge, then fails
            new FakeThing { pos = 4, stack = 5, placeOk = false, placeTakes = 5 }, // fully merged away
            new FakeThing { pos = 5, stack = 7, spawned = false },                 // not live: untouched
        };

        public static void Run(Action<string, Action> Case)
        {
            Case("P10_wash_failed_placement_respawns_at_old_cell", () =>
            {
                var h = Scene();
                int moved = Wash(h, true);
                Assert(h[0].spawned && h[0].pos == 999, "placed stack sits at the strand");
                Assert(h[1].spawned && h[1].pos == 2 && h[1].stack == 10, "failed stack respawned whole at its old cell");
                Assert(h[2].spawned && h[2].pos == 3 && h[2].stack == 6, "partly merged stack: remainder respawned at its old cell");
                Assert(h[3].destroyed && !h[3].spawned, "fully merged stack is not respawned");
                Assert(!h[4].spawned && h[4].pos == 5, "a non-live stack is left alone");
                Assert(moved == 2, "moved counts the placed and the partly merged stack, got " + moved);
                foreach (var t in h)
                    Assert(t.destroyed || t.spawned || t == h[4], "no live stack orphaned unspawned (cell " + t.pos + ")");
                // can-fail: the pre-fix rule orphans the failed stacks
                var o = Scene();
                Wash(o, false);
                Assert(!o[1].spawned && !o[1].destroyed, "can-fail: old rule must orphan the failed stack");
                Assert(!o[2].spawned && !o[2].destroyed, "can-fail: old rule must orphan the partly merged remainder");
            });

            Case("P10_WashCatch_routes_through_WashHeld", () =>
            {
                string weir = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_Weir.cs"));
                int i = weir.IndexOf("private int WashCatch()", StringComparison.Ordinal);
                int j = weir.IndexOf("private void TickBreach()", Math.Max(i, 0), StringComparison.Ordinal);
                Assert(i >= 0 && j > i, "found WashCatch body");
                string body = weir.Substring(i, j - i);
                RiverSwitchFlipChecks.Has(body, @"return RM_RiverMath\.WashHeld\(HeldCatch\(\),", "WashCatch returns WashHeld over HeldCatch()");
                RiverSwitchFlipChecks.Has(body, @"\(t, from\) => GenSpawn\.Spawn\(t, from, Map\)", "respawn puts the stack back at its old cell");
                RiverSwitchFlipChecks.Has(body, @"t => t\.Position,", "position captured before despawn");
                Assert(!body.Contains("t.DeSpawn(); if"), "no inline despawn-then-place loop left in WashCatch");
            });
        }
    }
}
