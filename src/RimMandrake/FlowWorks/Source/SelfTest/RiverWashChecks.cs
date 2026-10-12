// WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST (FlowWorks P10, GPT G4.3): a breach wash despawned each held stack and then
// tried to place it near the strand cell; when placement failed the stack was left unspawned (orphaned, lost). The
// per-stack rule now lives Verse-free in RM_RiverMath.WashHeld and RM_Building_BankWeir.WashCatch calls it. These
// cases drive the drop-failed path with fake things: the stack must come back at its old cell, a partial merge must
// still count, a fully merged (destroyed) stack must not be respawned. The can-fail runs the pre-fix rule beside it.
// WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME (the WeirBreach_* cases): where the washed catch strands, see below.
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

        private const float Held = 2.5f;   // RM_Building_BankWeir.HeldCatchRadius
        private const int N = 48;

        /// <summary>A straight river band (WeirPoolChecks.River's shape): along-river flow, quantised, optionally
        /// jittered by a fixed hash; -1 for bank and out of bounds.</summary>
        private static Func<int, int, int> River(double deg, double hw, double jitter)
        {
            double r = deg * Math.PI / 180.0;
            double ux = Math.Cos(r), uz = Math.Sin(r);
            int[,] g = new int[N, N];
            for (int x = 0; x < N; x++)
                for (int z = 0; z < N; z++)
                {
                    double px = x - N / 2.0, pz = z - N / 2.0;
                    double perp = -px * uz + pz * ux;
                    if (Math.Abs(perp) > hw) { g[x, z] = -1; continue; }
                    double j = jitter * (((x * 73856093 ^ z * 19349663) & 1023) / 511.5 - 1.0);
                    double a = r + j * Math.PI / 180.0;
                    g[x, z] = RM_RiverMath.Quantise((float)Math.Cos(a), (float)Math.Sin(a));
                }
            return (x, z) => x < 0 || z < 0 || x >= N || z >= N ? -1 : g[x, z];
        }

        /// <summary>The pre-fix WashCatch strand, kept in shape: step along the cell's quantised direction until a cell
        /// has none, then the nearest standable no-flow cell within 8 of that end (GenRadial order: by distance).
        /// False when nothing in reach qualifies.</summary>
        private static bool OldStrand(int x0, int z0, int steps, Func<int, int, int> dirAt, Func<int, int, bool> standable,
            out int sx, out int sz)
        {
            int x = x0, z = z0;
            for (int i = 0; i < steps; i++)
            {
                int dir = dirAt(x, z);
                if (dir < 0) break;
                x += RM_RiverMath.StepX[dir];
                z += RM_RiverMath.StepZ[dir];
            }
            sx = sz = 0;
            int best = int.MaxValue;
            for (int dx = -8; dx <= 8; dx++)
                for (int dz = -8; dz <= 8; dz++)
                {
                    int r2 = dx * dx + dz * dz;
                    if (r2 > 64 || r2 >= best) continue;
                    if (standable(x + dx, z + dz) && dirAt(x + dx, z + dz) < 0) { best = r2; sx = x + dx; sz = z + dz; }
                }
            return best != int.MaxValue;
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

            // WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME: live 2026-10-12c (tile 60145, weir at (112,52)) the breach left
            // heldBefore=3 heldAfter=3. The wet cell flows S into a no-flow cell; only N, NW and W carry flow (all S).
            // The pre-fix walk followed the quantised direction blindly, stopped one cell out, and stranded on the
            // nearest no-flow cell - inside the weir's own 2.5-cell held disc. These drive the PRODUCTION strand
            // (RM_RiverMath.WashStrand, which WashCatch calls) with the pre-fix rule beside it as the can-fail.
            Case("WeirBreach_live_scene_old_strands_home_new_leaves_disc", () =>
            {
                // the measured 3x3 (wetCell=112,52 wetDir=6 nbr=1,0:-1|1,1:-1|0,1:6|-1,1:6|-1,0:6|-1,-1:-1|0,-1:-1|1,-1:-1),
                // the river extended north from it; everything else is standable bank
                Func<int, int, int> d = (x, z) => (x == 0 || x == -1) && z >= 0 && z <= 20 ? 6 : -1;
                Func<int, int, bool> st = (x, z) => d(x, z) < 0;
                Assert(OldStrand(0, 0, 4, d, st, out int ox, out int oz), "the pre-fix rule finds a strand");
                Console.WriteLine("      old strand=(" + ox + "," + oz + ")");
                Assert(ox * ox + oz * oz <= Held * Held, "can-fail: the pre-fix rule must strand inside the held disc, got (" + ox + "," + oz + ")");
                Assert(RM_RiverMath.WashStrand(0, 0, 0, 0, 4, Held, d, st, out int sx, out int sz), "a strand exists");
                Console.WriteLine("      new strand=(" + sx + "," + sz + ")");
                double m = Held + RM_RiverMath.WashStrandMargin;
                Assert(sx * sx + sz * sz > m * m, "strand must lie beyond held radius + margin, got (" + sx + "," + sz + ")");
                Assert(-sz >= 1 && -sz >= Math.Abs(sx), "strand must lie downstream (S, within 45 degrees) of the weir, got (" + sx + "," + sz + ")");
                Assert(d(sx, sz) < 0 && st(sx, sz), "strand is standable bank");
            });

            Case("WeirBreach_off_axis_rivers_every_site_washes_downstream_out_of_reach", () =>
            {
                int sites = 0, oldHome = 0, offCone = 0;
                foreach (double deg in new[] { 0.0, 15, 22, 30, 37, 60, 105, 200, 290 })
                    foreach (double jit in new[] { 0.0, 12 })
                    {
                        Func<int, int, int> d = River(deg, 3.2, jit);
                        Func<int, int, bool> st = (x, z) => x >= 0 && z >= 0 && x < N && z < N && d(x, z) < 0;
                        double r = deg * Math.PI / 180.0, ux = Math.Cos(r), uz = Math.Sin(r);
                        for (int x = 14; x < N - 14; x++)
                            for (int z = 14; z < N - 14; z++)
                            {
                                if (d(x, z) < 0) continue;
                                // a weir needs its other cell on dry bank: try each 4-neighbour bank as the weir's Position
                                foreach (int[] b in new[] { new[] { 1, 0 }, new[] { -1, 0 }, new[] { 0, 1 }, new[] { 0, -1 } })
                                {
                                    int bx = x + b[0], bz = z + b[1];
                                    if (d(bx, bz) >= 0) continue;
                                    foreach (int[] w in new[] { new[] { x, z }, new[] { bx, bz } })
                                    {
                                        sites++;
                                        if (OldStrand(x, z, 4, d, st, out int ox, out int oz) && (ox - w[0]) * (ox - w[0]) + (oz - w[1]) * (oz - w[1]) <= Held * Held) oldHome++;
                                        Assert(RM_RiverMath.WashStrand(x, z, w[0], w[1], 4, Held, d, st, out int sx, out int sz),
                                            "no strand at deg " + deg + " (" + x + "," + z + ")");
                                        double m = Held + RM_RiverMath.WashStrandMargin;
                                        int dx = sx - w[0], dz = sz - w[1];
                                        Assert(dx * dx + dz * dz > m * m, "strand inside reach at deg " + deg + " (" + x + "," + z + ")");
                                        double along = dx * ux + dz * uz;
                                        double across = Math.Abs(-dx * uz + dz * ux);
                                        Assert(along >= 1.0, "strand not downstream at deg " + deg + " (" + x + "," + z + "): along " + along.ToString("0.00"));
                                        if (along < across) offCone++;
                                    }
                                }
                            }
                    }
                Console.WriteLine("      sites=" + sites + " oldStrandedHome=" + oldHome + " outside45degCone=" + offCone);
                Assert(sites > 200, "sanity: the scenes must hold bank-edge weir sites, got " + sites);
                Assert(oldHome > 0, "can-fail: the pre-fix rule must strand some catch at home, got 0");
                Assert(offCone == 0, offCone + " strands fell outside the 45-degree downstream cone");
            });

            Case("WeirBreach_downstream_walk_follows_flow_never_back", () =>
            {
                foreach (double deg in new[] { 0.0, 30, 60, 135, 250 })
                {
                    Func<int, int, int> d = River(deg, 2.6, 12);
                    double r = deg * Math.PI / 180.0, ux = Math.Cos(r), uz = Math.Sin(r);
                    int x0 = N / 2, z0 = N / 2;
                    List<int[]> sp = new List<int[]>();
                    int k = RM_RiverMath.DownstreamWalk(x0, z0, 8, d, out int ex, out int ez, (x, z) => sp.Add(new[] { x, z }));
                    Assert(k == 8 && sp.Count == 8, "a mid-river walk takes all 8 steps at deg " + deg + ", took " + k);
                    double prev = 0;
                    foreach (int[] c in sp)
                    {
                        double along = (c[0] - x0) * ux + (c[1] - z0) * uz;
                        Assert(along > prev, "walk did not move downstream at deg " + deg);
                        prev = along;
                    }
                    Assert(ex == sp[7][0] && ez == sp[7][1], "end is the last visited cell");
                }
                // lateral-only wet neighbours (flow E, water N and S) give no downstream step
                Func<int, int, int> lat = (x, z) => x == 0 && z >= -1 && z <= 1 ? 0 : -1;
                Assert(RM_RiverMath.DownstreamStep(0, 0, lat) == -1, "a lateral neighbour is not downstream");
                // UpstreamStep unchanged by the shared helper: a straight E river steps W upstream, E downstream
                Func<int, int, int> e = (x, z) => z == 0 ? 0 : -1;
                Assert(RM_RiverMath.UpstreamStep(0, 0, e) == 4 && RM_RiverMath.DownstreamStep(0, 0, e) == 0, "straight river: W up, E down");
            });

            Case("WeirBreach_WashCatch_routes_through_WashStrand", () =>
            {
                string weir = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_Weir.cs"));
                int i = weir.IndexOf("private int WashCatch()", StringComparison.Ordinal);
                int j = weir.IndexOf("private void TickBreach()", Math.Max(i, 0), StringComparison.Ordinal);
                Assert(i >= 0 && j > i, "found WashCatch body");
                string body = weir.Substring(i, j - i);
                RiverSwitchFlipChecks.Has(body, @"RM_RiverMath\.WashStrand\(wet\.x, wet\.z, Position\.x, Position\.z, RM_RiversSettings\.breachWashCells,\s*HeldCatchRadius,",
                    "WashCatch strands via WashStrand, outside HeldCatchRadius of Position");
                Assert(!body.Contains("GenRadial.RadialCellsAround(end"), "no blind nearest-no-flow search left in WashCatch");
            });
        }
    }
}
