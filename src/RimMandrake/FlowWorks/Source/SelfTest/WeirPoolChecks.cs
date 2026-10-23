// WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE: the weir's slack pool walked upstream by a rule that wanted a neighbour whose
// QUANTISED 8-way flow direction stepped exactly onto the cell (else the cell straight behind it). The weir's wet end
// is a bank-edge cell by construction, and vanilla's flow there runs ALONG the river (TileMutatorWorker_River averages
// the centreline tangents), so on a river not aligned to the 8 compass directions the exact step lands beside the
// cell and the cell behind is bank: pool = 0 (live, tile 825, 2026-10-12: "POOL cells=0 ... at=(108, 0, 12)").
// These cases drive the PRODUCTION walk (RM_RiverMath.UpstreamWalk, which RM_Building_BankWeir.AddPoolCells calls)
// on synthetic rasterised rivers, with the pre-fix rule beside it as the can-fail.
// NOT proven here: that tile 825's own grid has this shape (ProofWeirPool now prints the neighbourhood for that).
using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks.Rivers;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WeirPoolChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const int N = 48;

        /// <summary>A straight river band at `deg` degrees through the grid, half-width `hw` cells; every water cell
        /// carries the along-river flow, quantised (optionally jittered +-`jitter` degrees by a fixed hash, the way
        /// vanilla's averaged tangents wander), -1 for bank and out of bounds.</summary>
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

        /// <summary>The pre-fix RM_Building_BankWeir.Upstream + AddPoolCells spine, kept verbatim in shape.</summary>
        private static int OldWalk(int x0, int z0, int length, Func<int, int, int> dirAt)
        {
            int x = x0, z = z0, k = 0;
            for (; k < length; k++)
            {
                int curDir = dirAt(x, z);
                int bx = int.MinValue, bz = 0;
                bool found = false;
                for (int i = 0; i < 8 && !found; i++)
                {
                    int nx = x + RM_RiverMath.StepX[i], nz = z + RM_RiverMath.StepZ[i];
                    int d = dirAt(nx, nz);
                    if (d < 0 || nx + RM_RiverMath.StepX[d] != x || nz + RM_RiverMath.StepZ[d] != z) continue;
                    if (d == curDir) { bx = nx; bz = nz; found = true; }
                    else if (bx == int.MinValue) { bx = nx; bz = nz; }
                }
                if (bx == int.MinValue && curDir >= 0)
                {
                    int ax = x - RM_RiverMath.StepX[curDir], az = z - RM_RiverMath.StepZ[curDir];
                    if (dirAt(ax, az) >= 0) { bx = ax; bz = az; }
                }
                if (bx == int.MinValue) break;
                x = bx; z = bz;
            }
            return k;
        }

        /// <summary>Wet bank-edge cells (water with a 4-neighbour of bank) far enough from the grid edge that a
        /// full pool fits upstream - what FindWeirSite's margin guarantees in game.</summary>
        private static List<int[]> EdgeCells(Func<int, int, int> dirAt, int margin)
        {
            List<int[]> list = new List<int[]>();
            for (int x = margin; x < N - margin; x++)
                for (int z = margin; z < N - margin; z++)
                {
                    if (dirAt(x, z) < 0) continue;
                    if (dirAt(x + 1, z) < 0 || dirAt(x - 1, z) < 0 || dirAt(x, z + 1) < 0 || dirAt(x, z - 1) < 0)
                        list.Add(new[] { x, z });
                }
            return list;
        }

        private static int NewWalk(int x0, int z0, int length, Func<int, int, int> dirAt, List<int[]> spine = null)
        {
            return RM_RiverMath.UpstreamWalk(x0, z0, length, dirAt, (x, z) => spine?.Add(new[] { x, z }));
        }

        public static void Run(Action<string, Action> Case)
        {
            const int L = 8;   // RM_RiversSettings.weirPoolLength default
            const int M = L + 4;

            Case("WeirPool_edge_lane_minimal_scene_old_zero_new_pools", () =>
            {
                // the 3x3 shape of the inferred tile-825 site: wet cell flows NE, bank to its S/SW/SE, the water to
                // its W/NW also NE, N/NE flow E. No neighbour's quantised step lands on it; the cell behind is bank.
                Dictionary<(int, int), int> m = new Dictionary<(int, int), int>
                {
                    [(0, 0)] = 1, [(-1, 0)] = 1, [(-1, 1)] = 1, [(0, 1)] = 0, [(1, 1)] = 0, [(1, 0)] = 1,
                    [(-2, 0)] = 1, [(-2, 1)] = 1, [(-3, 0)] = 0, [(-3, 1)] = 0, [(-2, 2)] = 1, [(-1, 2)] = 1,
                };
                Func<int, int, int> d = (x, z) => m.TryGetValue((x, z), out int v) ? v : -1;
                int oldK = OldWalk(0, 0, L, d);
                int newK = NewWalk(0, 0, L, d);
                Console.WriteLine("      old spine=" + oldK + " new spine=" + newK);
                Assert(oldK == 0, "can-fail: the pre-fix rule must reproduce pool=0 on this scene, got " + oldK);
                Assert(newK >= 1, "the new rule must find the W neighbour upstream, got " + newK);
                Assert(RM_RiverMath.UpstreamStep(0, 0, d) == 4, "first step must be W (index 4), got " + RM_RiverMath.UpstreamStep(0, 0, d));
            });

            Case("WeirPool_off_axis_rivers_every_bank_edge_pools", () =>
            {
                // rivers at angles the 8-way quantisation does not hit exactly, with and without wander
                int oldZero = 0, newShort = 0, sites = 0;
                foreach (double deg in new[] { 0.0, 15, 22, 30, 37, 60, 105, 200, 290 })
                    foreach (double jit in new[] { 0.0, 12 })
                    {
                        Func<int, int, int> d = River(deg, 2.6, jit);
                        foreach (int[] c in EdgeCells(d, M))
                        {
                            sites++;
                            if (OldWalk(c[0], c[1], L, d) == 0) oldZero++;
                            if (NewWalk(c[0], c[1], L, d) < L) newShort++;
                        }
                    }
                Console.WriteLine("      sites=" + sites + " oldPool0=" + oldZero + " newShortOfFull=" + newShort);
                Assert(sites > 200, "sanity: the scenes must hold bank-edge sites, got " + sites);
                Assert(oldZero > 0, "can-fail: the pre-fix rule must pool 0 at some off-axis bank edge, got 0");
                Assert(newShort == 0, "every bank-edge site must get a full " + L + "-cell spine, " + newShort + " fell short");
            });

            Case("WeirPool_straight_river_unchanged_from_old_rule", () =>
            {
                // an axis-aligned river: the old exact step and the new best-aligned step are the same cell
                Func<int, int, int> d = River(0, 3.2, 0);
                foreach (int[] c in EdgeCells(d, M))
                {
                    List<int[]> sp = new List<int[]>();
                    Assert(NewWalk(c[0], c[1], L, d, sp) == L && OldWalk(c[0], c[1], L, d) == L, "full pool both ways");
                    for (int k = 0; k < sp.Count; k++)
                        Assert(sp[k][0] == c[0] - (k + 1) && sp[k][1] == c[1], "straight back along the flow at step " + k);
                }
            });

            Case("WeirPool_walk_never_goes_downstream_or_across", () =>
            {
                foreach (double deg in new[] { 0.0, 30, 60, 135, 250 })
                {
                    Func<int, int, int> d = River(deg, 2.6, 12);
                    double r = deg * Math.PI / 180.0, ux = Math.Cos(r), uz = Math.Sin(r);
                    foreach (int[] c in EdgeCells(d, M))
                    {
                        List<int[]> sp = new List<int[]>();
                        NewWalk(c[0], c[1], L, d, sp);
                        double prev = 0;
                        for (int k = 0; k < sp.Count; k++)
                        {
                            double along = (sp[k][0] - c[0]) * ux + (sp[k][1] - c[1]) * uz;
                            Assert(along < prev, "step " + k + " at deg " + deg + " did not move upstream (along " + along + ")");
                            prev = along;
                            Assert(d(sp[k][0], sp[k][1]) >= 0, "spine left the water");
                        }
                    }
                }
                // a lone cell whose only wet neighbours are lateral (flow E, wet N and S only) has no upstream
                Func<int, int, int> lat = (x, z) => x == 0 && z >= -1 && z <= 1 ? 0 : -1;
                Assert(RM_RiverMath.UpstreamStep(0, 0, lat) == -1, "a lateral neighbour is not upstream");
                // a neighbour flowing straight at the cell against its own flow gives no local flow to follow
                Func<int, int, int> opp = (x, z) => z != 0 ? -1 : (x == 0 ? 0 : (x == -1 ? 4 : -1));
                Assert(RM_RiverMath.UpstreamStep(0, 0, opp) == -1, "opposed flows: no upstream");
            });

            Case("WeirPool_length_honoured_and_no_revisit", () =>
            {
                Func<int, int, int> d = River(30, 4, 12);
                int[] c = EdgeCells(d, M)[0];
                foreach (int len in new[] { 0, 1, 3, 8 })
                {
                    List<int[]> sp = new List<int[]>();
                    int k = NewWalk(c[0], c[1], len, d, sp);
                    Assert(k == sp.Count && k <= len, "steps " + k + " for length " + len);
                    HashSet<(int, int)> seen = new HashSet<(int, int)> { (c[0], c[1]) };
                    foreach (int[] s in sp) Assert(seen.Add((s[0], s[1])), "revisited a cell");
                }
            });

            // RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS (owner 2026-10-16, by card: "Weirs join into one continuous wall")
            Case("WeirJoin_placement_straddle_or_continue", () =>
            {
                Assert(RM_RiverMath.WeirPlacementOk(1, 1, false), "a bank straddler stands alone");
                Assert(!RM_RiverMath.WeirPlacementOk(2, 0, false), "can-fail: an all-water section alone has no anchor");
                Assert(RM_RiverMath.WeirPlacementOk(2, 0, true), "an all-water section continuing a run is allowed");
                Assert(!RM_RiverMath.WeirPlacementOk(0, 2, true), "an all-dry section is never a weir");
                Assert(!RM_RiverMath.WeirPlacementOk(1, 0, true), "a half-unbuildable section is refused");
            });

            Case("WeirJoin_run_head_and_gap", () =>
            {
                // a chain 0-1-2-3 bank to bank (0 and 3 anchored), 4 is a separate weir
                Dictionary<int, int[]> links = new Dictionary<int, int[]>
                {
                    [0] = new[] { 1 }, [1] = new[] { 0, 2 }, [2] = new[] { 1, 3 }, [3] = new[] { 2 }, [4] = new int[0],
                };
                List<int> run = RM_RiverMath.WeirRun(2, i => links[i], 64);
                Assert(run.Count == 4 && run[0] == 2, "run from the middle reaches all four, start first: " + string.Join(",", run));
                Assert(RM_RiverMath.WeirRun(4, i => links[i], 64).Count == 1, "a lone weir is a run of one");
                Assert(RM_RiverMath.WeirRun(0, i => links[i], 2).Count == 2, "the cap holds");
                Func<int, bool> anchored = i => i == 0 || i == 3;
                Assert(RM_RiverMath.WeirRunHead(run, anchored, i => 100 - i) == 3, "head = lowest id among anchored (ids 100-i)");
                Assert(RM_RiverMath.WeirRunHead(new List<int> { 1, 2 }, anchored, i => i) == 1, "no anchor: lowest id");
                Assert(RM_RiverMath.WeirRunHolds(new List<bool> { true, true, true }), "sound run holds");
                Assert(!RM_RiverMath.WeirRunHolds(new List<bool> { true, false, true }), "one gap drains the run's pool");
                Assert(!RM_RiverMath.WeirRunHolds(new List<bool>()), "an empty run holds nothing");
            });

            Case("WeirArt_facing_follows_the_current", () =>
            {
                // horizontal wall (placed East=1 or West=3): current south (dir 6) -> East art (spill face to camera)
                Assert(RM_RiverMath.WeirArtRot(3, 6) == 1, "E-W wall, flow S -> East art");
                Assert(RM_RiverMath.WeirArtRot(1, 2) == 3, "E-W wall, flow N -> West art");
                Assert(RM_RiverMath.WeirArtRot(1, 5) == 1, "E-W wall, flow SW -> East art");
                Assert(RM_RiverMath.WeirArtRot(1, 0) == 1 && RM_RiverMath.WeirArtRot(3, 4) == 3, "flow along the wall keeps the placed facing");
                // vertical wall (placed North=0 or South=2): flow east (0) -> North art, west (4) -> South art
                Assert(RM_RiverMath.WeirArtRot(2, 0) == 0 && RM_RiverMath.WeirArtRot(0, 4) == 2, "N-S wall follows the flow's x");
                Assert(RM_RiverMath.WeirArtRot(0, -1) == 0 && RM_RiverMath.WeirArtRot(2, 9) == 2, "no current keeps the placed facing");
                for (int r = 0; r < 4; r++)
                    for (int d = -1; d < 8; d++)
                        Assert((RM_RiverMath.WeirArtRot(r, d) & 1) == (r & 1), "the art never changes the wall's axis");
            });
                    // ── WEIR_CATCH_FIX_NO_FREE_FISH + WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID (weir review 2026-10-23) ──
            // Owner: "they should just capture anything floating downstream. No auto fish capture." The intake is exactly
            // where the carry (RM_MapComponent_RiverCurrent.StepOne) stops a thing: an in-current cell whose flow step lands
            // on the wall (a weir cell is not standable).
            Case("WeirCatch_intake_is_where_the_carry_stops", () =>
            {
                // straight river flowing east (dir 0), z in 0..5; a N-S wall at x=10 spanning z 0..5 (three joined sections)
                Func<int, int, int> east = (x, z) => (z >= 0 && z <= 5 && x >= 0 && x < 30) ? 0 : -1;
                var wall = new List<int[]>();
                for (int z = 0; z <= 5; z++) wall.Add(new[] { 10, z });
                List<int[]> intake = RM_RiverMath.WeirIntakeCells(wall, east);
                Assert(intake.Count == 6, "one intake cell per wet wall cell on a straight river, got " + intake.Count);
                foreach (int[] c in intake)
                    Assert(c[0] == 9 && c[1] >= 0 && c[1] <= 5, "intake lies just upstream (x=9), got (" + c[0] + "," + c[1] + ")");
                // can-fail: downstream cells and the wall itself are never intake
                Assert(!intake.Exists(c => c[0] >= 10), "nothing at or below the wall is intake");
                // diagonal flow (NE, dir 1): the cells SW of the wall cells feed it too
                Func<int, int, int> ne = (x, z) => (x >= 0 && x < 30 && z >= -5 && z < 30) ? 1 : -1;
                List<int[]> diag = RM_RiverMath.WeirIntakeCells(wall, ne);
                Assert(diag.Exists(c => c[0] == 9 && c[1] == -1), "a NE flow feeds the wall's low end from (9,-1)");
                Assert(!diag.Exists(c => c[0] == 9 && c[1] == 5), "(9,5) flows NE to (10,6), beside the wall: not intake");
                // no current: no intake
                Assert(RM_RiverMath.WeirIntakeCells(wall, (x, z) => -1).Count == 0, "still water feeds nothing");
                // no duplicates when two wall cells share a feeder
                var seen = new HashSet<long>();
                foreach (int[] c in diag) Assert(seen.Add(((long)c[0] << 32) ^ (uint)c[1]), "intake cells are distinct");
            });

            Case("WeirCatch_budget_never_exceeds_the_cap", () =>
            {
                Assert(RM_RiverMath.WeirCaptureBudget(0, 30, 75) == 30, "an empty weir takes up to the cap");
                Assert(RM_RiverMath.WeirCaptureBudget(25, 30, 10) == 5, "a near-full weir takes only the room left");
                Assert(RM_RiverMath.WeirCaptureBudget(30, 30, 10) == 0 && RM_RiverMath.WeirCaptureBudget(40, 30, 10) == 0, "a full weir takes nothing");
                Assert(RM_RiverMath.WeirCaptureBudget(0, 30, 0) == 0, "nothing offered, nothing taken");
            });

            Case("WeirCatch_no_free_fish_or_drift_in_source", () =>
            {
                string w = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_Weir.cs"));
                Assert(!w.Contains("Notify_Fished") && !w.Contains("CommonFish") && !w.Contains("UncommonFish"), "the weir never touches the fish stock");
                Assert(!w.Contains("RM_RiverDriftDef.RollFor"), "the weir never rolls biome drift out of nothing");
                Assert(!w.Contains("ThingMaker.MakeThing"), "the weir creates nothing: it only moves what floated in");
                RiverSwitchFlipChecks.Has(w, @"RM_RiverMath\.WeirIntakeCells\(", "the capture reads the intake rule");
                RiverSwitchFlipChecks.Has(w, @"if \(!RM_RiversSettings\.weirCapturesFloating\)", "capture obeys its setting");
                string set = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_RiversSettings.cs"));
                Assert(!set.Contains("weirCatchesFish") && !set.Contains("weirCatchesDrift") && !set.Contains("weirDriftChance"),
                    "the fish/drift settings are gone, not left as dead switches");
                Assert(set.Contains("\"weirCapturesFloating\"") && set.Contains("\"weirWhiteWater\""), "the new settings are in the WORKS reset list");
            });

            Case("WeirFoam_only_where_the_current_crosses_the_wall", () =>
            {
                // horizontal (E-W) wall, placed rot 1 or 3: a current with a south component falls south
                Assert(RM_RiverMath.WeirFoamStep(1, 6, out int dx, out int dz) && dx == 0 && dz == -1, "E-W wall, flow S -> foam south");
                Assert(RM_RiverMath.WeirFoamStep(3, 1, out dx, out dz) && dx == 0 && dz == 1, "E-W wall, flow NE -> foam north");
                Assert(!RM_RiverMath.WeirFoamStep(1, 0, out _, out _) && !RM_RiverMath.WeirFoamStep(3, 4, out _, out _), "flow along an E-W wall: no foam (screenshot 2)");
                Assert(RM_RiverMath.WeirFoamStep(0, 0, out dx, out dz) && dx == 1 && dz == 0, "N-S wall, flow E -> foam east");
                Assert(RM_RiverMath.WeirFoamStep(2, 3, out dx, out dz) && dx == -1 && dz == 0, "N-S wall, flow NW -> foam west");
                Assert(!RM_RiverMath.WeirFoamStep(0, 2, out _, out _) && !RM_RiverMath.WeirFoamStep(2, -1, out _, out _), "along a N-S wall, or no current: none");
                // the foam side always agrees with the art's spill face (WeirArtRot)
                for (int r = 0; r < 4; r++)
                    for (int d = 0; d < 8; d++)
                        if (RM_RiverMath.WeirFoamStep(r, d, out dx, out dz))
                        {
                            int art = RM_RiverMath.WeirArtRot(r, d);
                            int ex = art == 0 ? 1 : art == 2 ? -1 : 0, ez = art == 1 ? -1 : art == 3 ? 1 : 0;
                            Assert(dx == ex && dz == ez, "foam side matches the spill face for rot " + r + " dir " + d);
                        }
            });

            Case("WeirFoam_image_left_side_in_the_world", () =>
            {
                // the frames are drawn crest-up falling south; the draw turns them, so "image-left" (the _a end) moves
                RM_RiverMath.WeirFoamLeft(0, -1, out int lx, out int lz); Assert(lx == -1 && lz == 0, "falling S: left is W");
                RM_RiverMath.WeirFoamLeft(1, 0, out lx, out lz); Assert(lx == 0 && lz == -1, "falling E: left is S");
                RM_RiverMath.WeirFoamLeft(-1, 0, out lx, out lz); Assert(lx == 0 && lz == 1, "falling W: left is N");
                RM_RiverMath.WeirFoamLeft(0, 1, out lx, out lz); Assert(lx == 1 && lz == 0, "falling N: left is E");
                foreach (var f in new[] { new[] { 0, -1 }, new[] { 1, 0 }, new[] { -1, 0 }, new[] { 0, 1 } })
                {
                    RM_RiverMath.WeirFoamLeft(f[0], f[1], out lx, out lz);
                    Assert(lx * f[0] + lz * f[1] == 0, "the end side runs along the wall, never along the fall");
                }
                Assert(RM_RiverMath.WeirFoamSuffix(true, true) == "" && RM_RiverMath.WeirFoamSuffix(false, true) == "_a"
                    && RM_RiverMath.WeirFoamSuffix(true, false) == "_b" && RM_RiverMath.WeirFoamSuffix(false, false) == "_ab",
                    "a side with no foam beside it ends in broken foam");
            });

            Case("WeirFoam_scales_with_flow", () =>
            {
                RM_RiverMath.WeirFoamLook none = RM_RiverMath.WeirFoam(RM_RiverMath.LaneNone, false);
                RM_RiverMath.WeirFoamLook m = RM_RiverMath.WeirFoam(RM_RiverMath.LaneMargin, false);
                RM_RiverMath.WeirFoamLook c = RM_RiverMath.WeirFoam(RM_RiverMath.LaneCentre, false);
                RM_RiverMath.WeirFoamLook s = RM_RiverMath.WeirFoam(RM_RiverMath.LaneCentre, true);
                Assert(none.alpha == 0f, "no lane, no foam");
                Assert(m.alpha > 0f && m.alpha < c.alpha && c.alpha <= s.alpha && s.alpha <= 1f, "margin < centre <= flood in strength");
                Assert(m.fps < c.fps && c.fps < s.fps, "faster water tumbles faster");
                Assert(m.length <= c.length && c.length < s.length && s.length <= 2f, "a flood throws the foam further");
                Assert(RM_RiverMath.WeirFoam(RM_RiverMath.LaneMargin, true).alpha >= c.alpha, "a flood margin runs like the centre");
            });

            Case("WeirFoam_frame_loops_and_desyncs", () =>
            {
                for (int i = 0; i < 200; i++)
                {
                    int f = RM_RiverMath.WeirFoamFrame(i * 0.037f, 10f, 12, 5);
                    Assert(f >= 0 && f < 12, "frame in range");
                }
                Assert(RM_RiverMath.WeirFoamFrame(0f, 10f, 12, 0) == 0 && RM_RiverMath.WeirFoamFrame(0.1f, 10f, 12, 0) == 1, "10 fps steps one frame per 0.1 s");
                Assert(RM_RiverMath.WeirFoamFrame(1.2f, 10f, 12, 0) == 0, "12 frames at 10 fps loop every 1.2 s");
                Assert(RM_RiverMath.WeirFoamFrame(0f, 10f, 12, 7) != RM_RiverMath.WeirFoamFrame(0f, 10f, 12, 8), "neighbouring weirs are out of step");
                Assert(RM_RiverMath.WeirFoamFrame(-3f, 10f, 12, -5) >= 0, "negative inputs never index out of range");
            });

            // ── owner by card 2026-10-23 07:19 (WEIR_CATCH_FIX_NO_FREE_FISH): "Flotsam? -> Yes, occasional flotsam" and
            // "Weir placed along the current? -> Auto-rotate to cross the current" ──
            Case("Flotsam_enters_only_where_the_river_comes_in", () =>
            {
                // 30x30 map, river z 10..14 flowing east: it enters on the west edge, leaves on the east edge
                Func<int, int, int> east = (x, z) => (x >= 0 && x < 30 && z >= 10 && z <= 14) ? 0 : -1;
                List<int[]> entry = RM_RiverMath.RiverEntryCells(30, 30, east);
                Assert(entry.Count == 5, "five entry cells on the west edge, got " + entry.Count);
                Assert(entry.TrueForAll(c => c[0] == 0 && c[1] >= 10 && c[1] <= 14), "all on x=0 within the river");
                // can-fail: the downstream (east) edge is never an entry
                Func<int, int, int> west = (x, z) => (x >= 0 && x < 30 && z >= 10 && z <= 14) ? 4 : -1;
                Assert(RM_RiverMath.RiverEntryCells(30, 30, west).TrueForAll(c => c[0] == 29), "a west-flowing river enters on the east edge");
                // diagonal NE river: entries lie on the west or south edge only
                Func<int, int, int> ne = (x, z) => (x >= 0 && x < 30 && z >= 0 && z < 30 && Math.Abs(x - z) <= 2) ? 1 : -1;
                List<int[]> d = RM_RiverMath.RiverEntryCells(30, 30, ne);
                Assert(d.Count > 0 && d.TrueForAll(c => c[0] == 0 || c[1] == 0), "NE river enters on the W/S edges only");
                Assert(RM_RiverMath.RiverEntryCells(30, 30, (x, z) => -1).Count == 0, "no river, no entry");
            });

            Case("Flotsam_rate_and_switch", () =>
            {
                Assert(RM_RiverMath.FlotsamRollChance(false, 2f, 2500) < 0f, "off never rolls");
                float c = RM_RiverMath.FlotsamRollChance(true, 1f, 2500);
                Assert(Math.Abs(c - 2500f / 60000f) < 1e-6f, "one a day, rolled hourly = 1/24 an hour, got " + c);
                Assert(RM_RiverMath.FlotsamRollChance(true, 0f, 2500) == 0f, "zero a day never spawns");
                Assert(RM_RiverMath.FlotsamRollChance(true, 1e6f, 2500) == 1f, "clamped to certain");
                Assert(RM_RiverMath.FlotsamLeavesAtEdge(false, true) && !RM_RiverMath.FlotsamLeavesAtEdge(false, false) && !RM_RiverMath.FlotsamLeavesAtEdge(true, true),
                    "flotsam leaves the map at the downstream edge; a colony's own stack and any pawn do not (pawns keep washOffMapEdge)");
            });

            Case("FerryRope_strip_spans_post_to_post", () =>
            {
                // RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fix 9: the 256x64 RM_FerryRope strip was never drawn; it now runs
                // centre to centre. PrintPlane turns the plane's +x axis to (cos(-rot), sin(-rot)) in (x, z).
                foreach (var ab in new[] { new[] { 0f, 0f, 6f, 0f }, new[] { 2f, 1f, 2f, 9f }, new[] { 0f, 0f, -3f, -4f }, new[] { 5f, 5f, 1f, 8f } })
                {
                    RM_RiverMath.RopePlane(ab[0], ab[1], ab[2], ab[3], out float cx, out float cz, out float len, out float rot);
                    float dx = ab[2] - ab[0], dz = ab[3] - ab[1];
                    Assert(Math.Abs(cx - (ab[0] + ab[2]) / 2f) < 1e-4f && Math.Abs(cz - (ab[1] + ab[3]) / 2f) < 1e-4f, "centred between the posts");
                    Assert(Math.Abs(len - (float)Math.Sqrt(dx * dx + dz * dz)) < 1e-4f, "as long as the span");
                    double r = -rot * Math.PI / 180.0;
                    Assert(Math.Abs(Math.Cos(r) * len - dx) < 1e-3 && Math.Abs(Math.Sin(r) * len - dz) < 1e-3,
                        "the strip's long axis points post to post, rot=" + rot);
                }
                string fp = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_FerryAndLevee.cs"));
                RiverSwitchFlipChecks.Has(fp, @"RM_RiverMath\.RopePlane\(", "the post prints the rope from the shared math");
                RiverSwitchFlipChecks.Has(fp, @"RM_FerryRope", "the rope strip texture is the one drawn");
                RiverSwitchFlipChecks.Has(fp, @"MapMeshDirty\(", "pairing and unpairing re-print the rope");
            });

            Case("Flotsam_wired_in_source", () =>
            {
                string cur = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_MapComponent_RiverCurrent.cs"));
                RiverSwitchFlipChecks.Has(cur, @"RM_RiverMath\.FlotsamLeavesAtEdge\(t is Pawn, IsFlotsam\(t\)\)", "the edge rule reads the flotsam book");
                RiverSwitchFlipChecks.Has(cur, @"RM_RiverDriftDef\.RollFor\(map\.Biome\)", "flotsam comes from the biome's drift list");
                RiverSwitchFlipChecks.Has(cur, @"RM_RiverMath\.RiverEntryCells\(", "flotsam enters at the upstream edge");
                string w = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_Weir.cs"));
                RiverSwitchFlipChecks.Has(w, @"ForgetFlotsam\(t\)", "a caught piece is the weir's catch, no longer flotsam");
                string set = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_RiversSettings.cs"));
                Assert(set.Contains("\"flotsamEnabled\"") && set.Contains("\"flotsamPerDay\""), "flotsam settings are in a reset list");
            });

            Case("WeirAutoRotate_crosses_the_current", () =>
            {
                // flow east (0): the wall must run N-S (rot 0/2); placed E-W it is turned
                List<int> c1 = RM_RiverMath.WeirCrossCandidates(1, 0);
                Assert(c1.Count == 2 && c1.TrueForAll(r => (r & 1) == 0), "E-W wall in an east flow -> try the two N-S rotations");
                Assert(RM_RiverMath.WeirCrossCandidates(0, 0).Count == 1 && RM_RiverMath.WeirCrossCandidates(0, 0)[0] == 0, "already crossing: keep it");
                // flow north (2): the wall must run E-W
                Assert(RM_RiverMath.WeirCrossCandidates(2, 2).TrueForAll(r => (r & 1) == 1), "N-S wall in a north flow -> E-W rotations");
                // diagonal flow crosses either axis; no flow decides nothing
                Assert(RM_RiverMath.WeirCrossCandidates(1, 1)[0] == 1 && RM_RiverMath.WeirCrossCandidates(3, -1)[0] == 3, "diagonal or no current keeps the placed rotation");
                for (int r = 0; r < 4; r++)
                    for (int d = 0; d < 8; d++)
                        foreach (int cand in RM_RiverMath.WeirCrossCandidates(r, d))
                            Assert(RM_RiverMath.WeirFoamStep(cand, d, out _, out _), "every candidate crosses the current (rot " + r + " dir " + d + ")");
                string w = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_Weir.cs"));
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(Designator_Place\), nameof\(Designator_Place\.SelectedUpdate\)\)\]", "the ghost shows the snapped rotation");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(Designator_Build\), nameof\(Designator_Build\.DesignateSingleCell\)\)\]", "the placed blueprint takes the snapped rotation");
            });

            Case("WeirLook_no_flat_tint_and_animated_foam_in_source", () =>
            {
                string w = RiverSwitchFlipChecks.Src(Path.Combine("Rivers", "RM_Weir.cs"));
                Assert(!w.Contains("WaterRoot"), "the flat pool-tint/static-foam strip is gone from the weir's draw");
                RiverSwitchFlipChecks.Has(w, @"protected override void DrawAt\(Vector3 drawLoc, bool flip = false\)", "the foam is drawn in real time");
                RiverSwitchFlipChecks.Has(w, @"RM_RiverMath\.WeirFoamStep\(", "the foam is drawn only where the current crosses the wall");
                RiverSwitchFlipChecks.Has(w, @"RM_RiverMath\.WeirFoamFrame\(Time\.realtimeSinceStartup", "the foam frame comes from real time");
                string xml = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_Volume.cs")), "..", "Defs", "Rivers", "RM_BankWorks.xml"));
                Assert(Regex.IsMatch(xml, @"<defName>RM_BankWeir</defName>[\s\S]*?<drawerType>MapMeshAndRealTime</drawerType>[\s\S]*?</ThingDef>"),
                    "RM_BankWeir is drawn MapMeshAndRealTime (the wall in the mesh, the foam per frame)");
                Assert(!Regex.IsMatch(xml, @"<defName>RM_BankWeir</defName>[\s\S]*?catches fish[\s\S]*?</ThingDef>"), "the description no longer promises fish");
            });
        }
    }
}
