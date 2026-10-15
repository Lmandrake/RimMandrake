// PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS (design/RimMandrake/relative_depth_climb_design_2026-10-12.md §8.5 steps 2-5).
// The arithmetic is PRODUCTION RM_CliffMaskMath + RM_PitTrapMath; the Verse wiring (RM_CliffMask's Harmony seams, the swap,
// the floor, the step cost, the retired planner) is pinned at its call sites by source checks below.
using System;
using System.Collections.Generic;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class CliffMaskChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const int Person = 2, Rat = 1, Muffalo = 3;
        private const byte N = 1, S = 2, E = 4, W = 8, NE = 0x10, SE = 0x20, SW = 0x40, NW = 0x80;

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        /// <summary>3×3 patch, rows from north (dz = +1) to south: {nw, n, ne}, {w, c, e}, {sw, s, se}.</summary>
        private static int[] P(int nw, int n, int ne, int w, int c, int e, int sw, int s, int se)
        {
            var d = new int[9];
            d[RM_CliffMaskMath.N9(-1, 1)] = nw; d[RM_CliffMaskMath.N9(0, 1)] = n; d[RM_CliffMaskMath.N9(1, 1)] = ne;
            d[RM_CliffMaskMath.N9(-1, 0)] = w; d[RM_CliffMaskMath.N9(0, 0)] = c; d[RM_CliffMaskMath.N9(1, 0)] = e;
            d[RM_CliffMaskMath.N9(-1, -1)] = sw; d[RM_CliffMaskMath.N9(0, -1)] = s; d[RM_CliffMaskMath.N9(1, -1)] = se;
            return d;
        }

        private static byte[] Map(int w, int h) => new byte[w * h];

        private static void Rect(byte[] g, int w, int x0, int z0, int rw, int rh, byte d)
        {
            for (int x = x0; x < x0 + rw; x++)
                for (int z = z0; z < z0 + rh; z++)
                    g[z * w + x] = d;
        }

        /// <summary>Flood over the mask's CARDINAL bits from (sx, sz): the cells A* could reach by cardinal steps.</summary>
        private static HashSet<int> Flood(byte[] g, int w, int h, int k, int sx, int sz, Func<int, int, bool> rampJoin = null)
        {
            var seen = new HashSet<int> { sz * w + sx };
            var q = new Queue<int>();
            q.Enqueue(sz * w + sx);
            while (q.Count > 0)
            {
                int i = q.Dequeue();
                int x = i % w, z = i / w;
                var d9 = new int[9];
                for (int dz = -1; dz <= 1; dz++)
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        int nx = x + dx, nz = z + dz;
                        d9[RM_CliffMaskMath.N9(dx, dz)] = nx < 0 || nz < 0 || nx >= w || nz >= h ? 0 : g[nz * w + nx];
                    }
                byte bits = RM_CliffMaskMath.AllowedBits(d9, k, b =>
                {
                    int nx = x + RM_CliffMaskMath.Dx[b], nz = z + RM_CliffMaskMath.Dz[b];
                    int j = nz * w + nx;
                    return rampJoin != null && nx >= 0 && nz >= 0 && nx < w && nz < h && (rampJoin(i, j) || rampJoin(j, i));
                });
                for (int b = 0; b < 4; b++)
                {
                    if ((bits & (1 << b)) == 0) continue;
                    int nx = x + RM_CliffMaskMath.Dx[b], nz = z + RM_CliffMaskMath.Dz[b];
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                    int j = nz * w + nx;
                    if (seen.Add(j)) q.Enqueue(j);
                }
            }
            return seen;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Cliff_mask_bits_follow_the_step_rule", () =>
            {
                // a person at the D 4 core of a dried pond: D 2 ring all round, gentle
                Assert(RM_CliffMaskMath.AllowedBits(P(2, 2, 2, 2, 4, 2, 2, 2, 2), Person) == 0xFF, "dried pond core: every way open");
                // a person at the bottom of a sheer D 3 pit cell, surface all round: nothing
                Assert(RM_CliffMaskMath.AllowedBits(P(0, 0, 0, 0, 3, 0, 0, 0, 0), Person) == 0, "sheer D 3: no way up for a person");
                Assert(RM_CliffMaskMath.AllowedBits(P(0, 0, 0, 0, 3, 0, 0, 0, 0), Muffalo) == 0xFF, "a muffalo climbs 3");
                Assert(RM_CliffMaskMath.AllowedBits(P(0, 0, 0, 0, 2, 0, 0, 0, 0), Rat) == 0, "a rat in D 2: held");
                // on the lip beside a D 4 hole to the east: no step down (nobody jumps a cliff on purpose), and the two
                // diagonals that would cut the hole's corner are refused too
                byte lip = RM_CliffMaskMath.AllowedBits(P(0, 0, 0, 0, 0, 4, 0, 0, 0), Person);
                Assert((lip & E) == 0, "no walked step down 4");
                Assert((lip & (NE | SE)) == 0, "no diagonal across the hole's corner");
                Assert((lip & (N | S | W | NW | SW)) == (N | S | W | NW | SW), "the rest of the lip is open");
            });

            Case("Cliff_mask_ramp_and_ladder_join_cardinals_only", () =>
            {
                int[] pit = P(0, 0, 0, 0, 4, 0, 0, 0, 0);
                byte withRampEast = RM_CliffMaskMath.AllowedBits(pit, Rat, b => b == 2 /* E */);
                Assert(withRampEast == E, "a ramp east opens east only, for anyone");
                Assert(RM_CliffMaskMath.LadderJoins(4, 0) && RM_CliffMaskMath.LadderJoins(4, 3), "a ladder joins any shallower neighbour");
                Assert(!RM_CliffMaskMath.LadderJoins(4, 4) && !RM_CliffMaskMath.LadderJoins(2, 4), "not a level or deeper one");
                Assert(RM_CliffMaskMath.RampJoins(4, 1, 3) && RM_CliffMaskMath.RampJoins(4, 3, 3), "a ramp spans 1..3 up");
                Assert(!RM_CliffMaskMath.RampJoins(4, 0, 3) && !RM_CliffMaskMath.RampJoins(4, 4, 3), "not 4, not 0");
                Assert(!RM_CliffMaskMath.RampJoins(1, 4, 3), "a ramp faces uphill");
                Assert(!RM_CliffMaskMath.RampJoins(4, 1, 2), "the span setting caps it");
                Assert(RM_CliffMaskMath.CardinalBit(1, 0) == 2 && RM_CliffMaskMath.CardinalBit(0, -1) == 1 && RM_CliffMaskMath.CardinalBit(1, 1) == -1,
                    "cardinal bits in CellConnection order");
                Assert(RM_CliffMaskMath.Derive(0x0F, 0xFF) == 0x0F && RM_CliffMaskMath.Derive(0xFF, 0x0F) == 0x0F, "vanilla AND climb");
            });

            Case("Cliff_mask_offsets_match_vanilla_CellConnection", () =>
            {
                // Verse.CellConnectionExtensions.OffsetFromBitIndex (decompiled 1.6): N, S, E, W, NE, SE, SW, NW
                int[] dx = { 0, 0, 1, -1, 1, 1, -1, -1 }, dz = { 1, -1, 0, 0, 1, -1, -1, 1 };
                for (int b = 0; b < 8; b++)
                    Assert(RM_CliffMaskMath.Dx[b] == dx[b] && RM_CliffMaskMath.Dz[b] == dz[b], "bit " + b + " offset");
            });

            Case("Cliff_mask_components_equal_the_pocket_grid", () =>
            {
                // the masks and the pocket grid must never disagree (design §5 A minus): flood the mask's cardinal bits and
                // compare with RM_PocketGridMath.Label on random terrain, per band, with and without a ramp
                var rng = new Random(20261014);
                for (int trial = 0; trial < 40; trial++)
                {
                    int w = 12, h = 10;
                    byte[] g = Map(w, h);
                    for (int i = 0; i < g.Length; i++) g[i] = (byte)(rng.Next(3) == 0 ? rng.Next(5) : 0);
                    int a = rng.Next(w * h), bx = a % w, bz = a / w;
                    int rb = bx + 1 < w ? a + 1 : a - 1;
                    Func<int, int, bool> ramp = trial % 2 == 0 ? null : (i, j) => i == a && j == rb;
                    for (int k = 1; k <= 3; k++)
                    {
                        var l = RM_PocketGridMath.Label(g, w, h, k, ramp);
                        for (int s = 0; s < g.Length; s += 7)
                        {
                            var f = Flood(g, w, h, k, s % w, s / w, ramp);
                            for (int j = 0; j < g.Length; j++)
                                Assert(f.Contains(j) == l.SameComponent(s, j),
                                    "trial " + trial + " K " + k + ": mask flood and pocket label disagree at " + s + " -> " + j);
                        }
                    }
                }
            });

            Case("Cliff_mask_walls_stay_walls_with_a_ramp", () =>
            {
                // GPT #18: one ramp must not make every wall crossable. Sheer 3x3 D 4 pit, D 1 shelf east, ramp (5,4) -> (6,4).
                int w = 10, h = 9;
                byte[] g = Map(w, h);
                Rect(g, w, 3, 3, 3, 3, 4);
                g[4 * w + 6] = 1;
                int rampCell = 4 * w + 5, top = 4 * w + 6;
                Func<int, int, bool> ramp = (x, y) => x == rampCell && y == top;
                var f = Flood(g, w, h, Person, 4, 4, ramp);
                Assert(f.Contains(0), "the pit floor reaches the surface by the ramp");
                int[] lip = P(0, 0, 0, 0, 4, 0, 0, 0, 0);
                Assert(RM_CliffMaskMath.AllowedBits(lip, Person) == 0, "the north wall cell (no ramp) is still sealed");
            });

            Case("Cliff_mask_wiring_pinned_at_call_sites", () =>
            {
                string mask = Src("Superdeep", "RM_CliffMask.cs");
                Assert(mask.Contains("typeof(ConnectivitySource), nameof(ConnectivitySource.ComputeAll)")
                    && mask.Contains("typeof(ConnectivitySource), nameof(ConnectivitySource.UpdateIncrementally)"),
                    "the bands move when vanilla's array moves (GatherData)");
                Assert(mask.Contains("typeof(PathFinder), \"ParameterizePathJob\"")
                    && mask.Contains("typeof(PathFinderMapData), nameof(PathFinderMapData.ParameterizePathJob)")
                    && mask.Contains("job.connectivity = m.band[band].AsReadOnly()"), "per-request swap of job.connectivity");
                Assert(mask.Contains("RM_CliffMaskMath.AllowedBits(") && mask.Contains("RM_PocketGrid.EffectiveDepth("),
                    "the masks use the selftested bits over the pocket grid's own depth input");
                Assert(mask.Contains("RM_PocketGrid.CanFly(p)"), "flyers keep vanilla's mask");
                Assert(!mask.Contains("vanilla[idx] =") && !mask.Contains("data[") , "vanilla's array is never written");
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("RM_ClimbJoins.ForPawn(") && trap.Contains("bool everyone = RM_CliffMask.On"),
                    "the step floor checks every pawn while the masks are on");
                Assert(trap.Contains("(!RM_CliffMask.On && !Captures(p))"), "reachability: physics for everyone with the masks on");
                string cost = Src("Superdeep", "RM_PitStepCost.cs");
                Assert(cost.Contains("RM_PitTrapMath.StepCost(") && cost.Contains("pitSlowClimbFactor"),
                    "walking speed: slow climb at s = K");
                Assert(cost.Contains("\"CostToMoveIntoCell\", new[] { typeof(Pawn), typeof(IntVec3) }"), "the step cost knows its pawn");
                string path = Src("Superdeep", "RM_PitPathing.cs");
                Assert(path.Contains("if (RM_CliffMask.On)") && path.Contains("PitLeg.ClosedLadders"),
                    "the staged planner is retired under the masks; only the ladder offset remains");
                Assert(path.Contains("RM_CliffMask.On || pawn == null"), "the entry veto is retired under the masks");
                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                Assert(grid.Contains("LadderLeadsOut("), "a ladder is an exit only where it joins a shallower neighbour");
                Assert(grid.Contains("RM_CliffMask.settingsSalt++"), "a climb setting re-derives the masks");
                string ladder = Src("Superdeep", "RM_LadderUtility.cs");
                Assert(ladder.Contains("BumpClimbGeneration()"), "raising or lowering a ladder re-derives the masks");
            });
        }
    }
}
