// RIMMANDRAKE_TRACE_FLOWWORKS_HELD_RAIDER_LEFT_DRAINED_MOAT (sc_moat_raid T161018): a raider held in a drained 4 m moat shared
// square 67,63 with another and was set on the bank 67,64 by vanilla's collision recovery (Pawn_PathFollower.PatherTick l.225,
// CellFinder.TryFindBestPawnStandCell cellByCell). RM_Patch_PitRecovery filters that search.
//
// The search below is vanilla's own (decompile rw16 CellFinder.cs l.575-672: radius 10 doubled, cardinal Dijkstra, blocked
// square +15, nearest free square, its first step); the edge rule is the SHIPPED RM_PitTrapMath.RecoveryShuffleAllowed.
// Range read: pit shape (8) x floor depth (0..14 notches: dry to 7 m, and any level water lifts the climb to) x climb limit
// (every body from a rat to a thrumbo) x how many other pawns stand about (0..90 %) x seed. Left out, judged live or by their
// own checks: doors, walls (walkability, vanilla's), decks and lids (RM_SuspensionUnderpass, RM_PitCoverBeneath), rails
// (FallRailChecks), flyers and bodies too wide for the pocket (both exempt).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitRecoveryChecks
    {
        private const int W = 25;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] parts) => RiverSwitchFlipChecks.Src(Path.Combine(parts));

        private static readonly (int x, int z)[] Cardinal = { (0, 1), (1, 0), (0, -1), (-1, 0) };

        /// <summary>Vanilla's search: the first step from <paramref name="start"/> toward the nearest free square, or null.</summary>
        private static (int x, int z)? Search((int x, int z) start, Func<(int x, int z), bool> blocked, Func<(int x, int z), (int x, int z), bool> edge)
        {
            int last = -1;
            for (float radius = 10f; ; radius *= 2f)
            {
                var dist = new Dictionary<(int x, int z), float> { [start] = 0f };
                var parent = new Dictionary<(int x, int z), (int x, int z)>();
                var queue = new PriorityQueue<(int x, int z), float>();
                queue.Enqueue(start, 0f);
                while (queue.TryDequeue(out var c, out float at))
                {
                    if (at != dist[c] || Math.Abs(c.x - start.x) + Math.Abs(c.z - start.z) > radius) continue;
                    foreach (var d in Cardinal)
                    {
                        var n = (x: c.x + d.x, z: c.z + d.z);
                        if (n.x < 0 || n.z < 0 || n.x >= W || n.z >= W || !edge(c, n)) continue;
                        float next = at + 1f + (blocked(n) ? 15f : 0f);
                        if (dist.TryGetValue(n, out float old) && old <= next) continue;
                        dist[n] = next;
                        parent[n] = c;
                        queue.Enqueue(n, next);
                    }
                }
                if (dist.Count == last) return null;
                var free = dist.Where(p => !blocked(p.Key)).OrderBy(p => p.Value).ToList();
                if (free.Count > 0)
                {
                    var c = free[0].Key;
                    var step = c;
                    while (c != start)
                    {
                        step = c;
                        c = parent[c];
                    }
                    return step;
                }
                if (radius > W) return null;
                last = dist.Count;
            }
        }

        /// <summary>Shape s at floor depth d: 0 flat, 1-3 a trench 1-3 wide, 4 a 3x3 pit, 5 a 1x1 pit, 6 a moat ring 3 wide, 7 a pit
        /// whose middle is 6 notches deeper (4/7/7/4).</summary>
        private static int[,] Shape(int s, int d)
        {
            var g = new int[W, W];
            for (int x = 0; x < W; x++)
                for (int z = 0; z < W; z++)
                {
                    int rx = Math.Abs(x - 12), rz = Math.Abs(z - 12), r = Math.Max(rx, rz);
                    bool dug = s >= 1 && s <= 3 ? x >= 10 && x < 10 + s && z > 2 && z < 22
                        : s == 4 ? r <= 1 : s == 5 ? r == 0 : s == 6 ? r >= 6 && r <= 8 : s == 7 && r <= 2;
                    g[x, z] = dug ? d + (s == 7 && r <= 1 && d > 0 ? 6 : 0) : 0;
                }
            return g;
        }

        private static bool Shuffle(int[,] g, (int x, int z) a, (int x, int z) b, int k) =>
            RM_PitTrapMath.RecoveryShuffleAllowed(true, false, g[a.x, a.z], g[b.x, b.z], k);

        public static void Run(Action<string, Action> Case)
        {
            int person = RM_PitTrapMath.ClimbLimit(1f);

            Case("PitRecovery_T161018_overlap_stays_in_the_moat", () =>
            {
                // the scene's own squares: plot 64..71 undug, moat ring 61..74 dug 4 m, water 0.96 m (walls 8 notches to the climb)
                Func<(int x, int z), int> depth = c =>
                {
                    int x = c.x + 55, z = c.z + 55;
                    bool ring = x >= 61 && x <= 74 && z >= 61 && z <= 74, plot = x >= 64 && x <= 71 && z >= 64 && z <= 71;
                    return ring && !plot ? 8 : 0;
                };
                var at = (x: 67 - 55, z: 63 - 55);
                var bank = (x: 67 - 55, z: 64 - 55);
                Func<(int x, int z), bool> blocked = c => c == at;   // Human21222
                var old = Search(at, blocked, (a, b) => true);
                Assert(old.HasValue && old.Value == bank, "can-fail: vanilla's own search sets him on the bank square he was read on (67,64): " + old);
                var now = Search(at, blocked, (a, b) => RM_PitTrapMath.RecoveryShuffleAllowed(true, false, depth(a), depth(b), person));
                Assert(now.HasValue && depth(now.Value) == 8, "he is moved along the moat floor: " + now);
                // every open floor square taken but the bank: he stays, on the floor
                Func<(int x, int z), bool> full = c => depth(c) > 0;
                var stay = Search(at, full, (a, b) => RM_PitTrapMath.RecoveryShuffleAllowed(true, false, depth(a), depth(b), person));
                Assert(stay == null, "with the whole floor taken he stays put: " + stay);
            });

            Case("PitRecovery_sweep_no_edge_crossed", () =>
            {
                int cases = 0, moved = 0, stayed = 0, oldCrossed = 0, worst = 0, steps = 0;
                int[] limits = new[] { 0.2f, 0.6f, 1f, 2f, 4f }.Select(b => RM_PitTrapMath.ClimbLimit(b)).Distinct().ToArray();
                for (int s = 0; s <= 7; s++)
                    for (int d = 0; d <= 14; d++)
                        foreach (int k in limits)
                            for (int crowd = 0; crowd <= 9; crowd += 3)
                                for (int seed = 0; seed < 3; seed++)
                                {
                                    var g = Shape(s, d);
                                    var rng = new Random(s * 100003 + d * 1009 + k * 101 + crowd * 11 + seed);
                                    var spots = new List<(int x, int z)>();
                                    for (int x = 0; x < W; x++)
                                        for (int z = 0; z < W; z++)
                                            if (g[x, z] > 0 == (s > 0 && d > 0 && seed != 2)) spots.Add((x, z));   // seed 2 starts on the rim
                                    if (seed == 2 && s > 0 && d > 0)
                                    {
                                        spots = spots.Where(c => Cardinal.Any(o => c.x + o.x >= 0 && c.z + o.z >= 0 && c.x + o.x < W && c.z + o.z < W
                                            && g[c.x + o.x, c.z + o.z] > 0)).ToList();
                                    }
                                    var at = spots[rng.Next(spots.Count)];
                                    var taken = new HashSet<(int x, int z)> { at };
                                    for (int x = 0; x < W; x++)
                                        for (int z = 0; z < W; z++)
                                            if (rng.Next(10) < crowd) taken.Add((x, z));
                                    cases++;
                                    var old = Search(at, taken.Contains, (a, b) => true);
                                    if (old.HasValue && Math.Abs(g[at.x, at.z] - g[old.Value.x, old.Value.z]) > k) oldCrossed++;
                                    int n = 0;
                                    while (taken.Contains(at))
                                    {
                                        var step = Search(at, taken.Contains, (a, b) => Shuffle(g, a, b, k));
                                        if (step == null) break;
                                        worst = Math.Max(worst, Math.Abs(g[at.x, at.z] - g[step.Value.x, step.Value.z]) - k);
                                        Assert(Math.Abs(g[at.x, at.z] - g[step.Value.x, step.Value.z]) <= k,
                                            $"shape {s} depth {d} k {k} crowd {crowd} seed {seed}: {at} -> {step} crosses a pit edge");
                                        at = step.Value;
                                        Assert(++n <= W * W, $"shape {s} depth {d} k {k} crowd {crowd} seed {seed}: never settles (moved back and forth)");
                                    }
                                    steps = Math.Max(steps, n);
                                    if (taken.Contains(at)) stayed++; else moved++;
                                    if (d == 0 || s == 0)
                                    {
                                        Assert(!taken.Contains(at) || taken.Count == W * W, "flat ground: the crowded pawn always finds a free square");
                                    }
                                }
                Console.WriteLine($"      PitRecovery sweep: {cases} cases, worst step over the climb limit {worst} (limit 0), settled {moved}, stayed {stayed}, "
                    + $"longest shuffle {steps}; the unfiltered search crosses an edge in {oldCrossed}");
                Assert(oldCrossed > 100, "can-fail: the unfiltered search crosses pit edges in this range: " + oldCrossed);
                Assert(moved > stayed && stayed > 0, "both ends of the range are read");
            });

            Case("PitRecovery_absolute_rule", () =>
            {
                Assert(!RM_PitTrapMath.RecoveryShuffleAllowed(false, true, 4, 0, person), "a held pawn is not crowded out");
                Assert(!RM_PitTrapMath.RecoveryShuffleAllowed(false, true, 4, 3, person), "nor onto a shallower floor");
                Assert(RM_PitTrapMath.RecoveryShuffleAllowed(false, true, 4, 4, person), "along the floor he is");
                Assert(!RM_PitTrapMath.RecoveryShuffleAllowed(false, false, 0, 4, person), "nobody is crowded into it");
                Assert(RM_PitTrapMath.RecoveryShuffleAllowed(false, false, 4, 0, person), "a pawn it does not hold is vanilla's");
            });

            Case("PitRecovery_wired", () =>
            {
                string s = Src("Superdeep", "RM_PitRecovery.cs");
                Assert(s.Contains("[HarmonyPatch(typeof(CellFinder), nameof(CellFinder.TryFindBestPawnStandCell))]"), "the recovery's search is patched");
                Assert(s.Contains("[HarmonyPatch(typeof(CellFinder), \"GetAdjacentCardinalCellsForBestStandCell\")]"), "and its neighbours");
                Assert(s.Contains("return RM_Patch_PitRecovery.Filtering(pawn) ? Open(__result, x) : __result;"), "filtered for this pawn's search only");
                Assert(s.Contains("if (!RimMandrakeFlowWorksSettings.superdeepCaptureEnabled || !cellByCell || forPawn == null || !forPawn.Spawned)"),
                    "the hold's switch off, or the search that ends in death (cellByCell false), stays vanilla");
                Assert(s.Contains("return RM_PitTrapMath.RecoveryShuffleAllowed(relative, !relative && RM_SuperdeepTrap.IsHeldAt(pawn, from),"), "by the rule read above");
                Assert(s.Contains("if (__result && cell != from && !EdgeAllowed(from, cell))"), "and the answer is read once more");
                Assert(s.Contains("k = RM_PocketGrid.NaturalClimbLimitOf(forPawn);"), "no climbing gear");
                Assert(s.Split(new[] { "\"superdeepCaptureEnabled\"" }, StringSplitOptions.None).Length == 3, "both patches follow the hold's switch");
                Assert(Src("..", "Source", "RimMandrake_FlowWorks.csproj").Contains("Superdeep\\RM_PitRecovery.cs"), "and it is in the mod build");
            });
        }
    }
}
