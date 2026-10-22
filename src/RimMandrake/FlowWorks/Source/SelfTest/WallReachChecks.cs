// REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE (owner 2026-10-21, by card: "3: the wall-aware reach map, kept per pawn class";
// spec Transient/pile_2026-10-21/reachability_review.md §4). The arithmetic is PRODUCTION RM_WallReachMath (+ RM_PocketGridMath,
// RM_PitTrapMath); the Verse wiring (RM_WallReach, the CanReach postfix, the PatherFailed residual counter) is pinned at its
// call sites by source checks below. The four staged scenes are the proof's (northstar/reach_map_proof.py), drawn as grids.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WallReachChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const int Person = 2;
        private const byte O = RM_WallReachMath.Open, W = RM_WallReachMath.Wall, D = RM_WallReachMath.Door,
            PD = RM_WallReachMath.PlayerDoor, HD = RM_WallReachMath.HeldDoor, SG = RM_WallReachMath.ShutGate,
            F = RM_WallReachMath.Fence, DW = RM_WallReachMath.DeepWater;

        // the classes the proof's pawns fall in
        private static readonly int Colonist = RM_WallReachMath.ClassOf(true, true, false, false, false, false);
        private static readonly int Raider = RM_WallReachMath.ClassOf(true, true, false, true, false, false);
        private static readonly int RaiderBashing = RM_WallReachMath.ClassOf(true, true, true, true, false, false);
        private static readonly int WildAnimal = RM_WallReachMath.ClassOf(true, true, false, true, true, false);
        private static readonly int NonSwimmerColonist = RM_WallReachMath.ClassOf(true, true, false, false, false, true);

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        /// <summary>A scene from rows of characters, top row = highest z. '.' open, '#' wall, 'd' door, 'p' player door,
        /// 'h' held door, 'g' shut gate, 'f' fence, '~' deep water; a digit is the dug depth of an open square.</summary>
        private static (byte[] kind, byte[] depth, int w, int h) Scene(params string[] rows)
        {
            int h = rows.Length, w = rows[0].Length;
            var kind = new byte[w * h];
            var depth = new byte[w * h];
            for (int r = 0; r < h; r++)
            {
                Assert(rows[r].Length == w, "scene rows equal width");
                int z = h - 1 - r;
                for (int x = 0; x < w; x++)
                {
                    char c = rows[r][x];
                    int i = z * w + x;
                    switch (c)
                    {
                        case '#': kind[i] = W; break;
                        case 'd': kind[i] = D; break;
                        case 'p': kind[i] = PD; break;
                        case 'h': kind[i] = HD; break;
                        case 'g': kind[i] = SG; break;
                        case 'f': kind[i] = F; break;
                        case '~': kind[i] = DW; break;
                        default:
                            kind[i] = O;
                            if (c >= '0' && c <= '9') depth[i] = (byte)(c - '0');
                            break;
                    }
                }
            }
            return (kind, depth, w, h);
        }

        private static bool Veto((byte[] kind, byte[] depth, int w, int h) s, int cls, int sx, int sz, int dx, int dz,
            bool useDepth = true, List<(int, int)> ladderCells = null)
        {
            RM_WallReachMath.Labels l = RM_WallReachMath.Label(s.kind, useDepth ? s.depth : null, s.w, s.h, Person, cls);
            var edges = new List<(int a, int b)>();
            if (ladderCells != null)
            {
                foreach ((int a, int b) in ladderCells)
                {
                    (int a, int b)? e = RM_WallReachMath.LadderEdge(l, a, b, true);
                    if (e.HasValue) edges.Add(e.Value);
                }
            }
            return RM_WallReachMath.Vetoed(l.At(sx, sz), new[] { l.At(dx, dz) }, edges);
        }

        /// <summary>The pocket grid's (depth-only) answer: the half that said yes about a different route.</summary>
        private static bool SameDepthComponent((byte[] kind, byte[] depth, int w, int h) s, int sx, int sz, int dx, int dz)
        {
            RM_PocketGridMath.Labels l = RM_PocketGridMath.Label(s.depth, s.w, s.h, Person);
            return l.label[sz * s.w + sx] == l.label[dz * s.w + dx];
        }

        /// <summary>Vanilla's (walls, no depth) answer for a class: the same labels with depth ignored.</summary>
        private static bool SameWallComponent((byte[] kind, byte[] depth, int w, int h) s, int cls, int sx, int sz, int dx, int dz)
            => !Veto(s, cls, sx, sz, dx, dz, useDepth: false);

        public static void Run(Action<string, Action> Case)
        {
            Case("WallReach_passable_table_by_kind_and_class", () =>
            {
                Assert(RM_WallReachMath.Passable(O, ~0) && RM_WallReachMath.Passable(HD, ~0), "open and held-open squares pass every class");
                Assert(!RM_WallReachMath.Passable(W, 0), "a wall passes nobody (sappers never reach this map)");
                Assert(RM_WallReachMath.Passable(D, Colonist) && !RM_WallReachMath.Passable(D, RM_WallReachMath.NonOpener), "a door shuts only non-openers");
                Assert(RM_WallReachMath.Passable(PD, Colonist) && !RM_WallReachMath.Passable(PD, Raider) && !RM_WallReachMath.Passable(PD, WildAnimal),
                    "the player's door shuts raiders and wild animals, not colonists");
                Assert(RM_WallReachMath.Passable(PD, RaiderBashing), "a door-basher passes the player's door (vanilla: canBashDoors)");
                Assert(!RM_WallReachMath.Passable(SG, Colonist) && RM_WallReachMath.Passable(SG, RaiderBashing),
                    "a locked, un-held gate shuts everyone but a basher");
                Assert(!RM_WallReachMath.Passable(F, WildAnimal) && RM_WallReachMath.Passable(F, Colonist), "a fence shuts roamers only");
                Assert(!RM_WallReachMath.Passable(DW, NonSwimmerColonist) && RM_WallReachMath.Passable(DW, Colonist), "deep water shuts non-swimmers only");
                Assert(RM_WallReachMath.Passable(99, ~0), "an unknown kind is never a reason to say no");
            });

            Case("WallReach_class_door_bits_only_on_a_ByPawn_walk_without_bashing", () =>
            {
                Assert(RM_WallReachMath.ClassOf(false, false, false, true, false, false) == 0,
                    "PassDoors/NoPassClosedDoors: every door open here (PassDoors prices a shut door at 150; NoPass is vanilla's)");
                int bash = RM_WallReachMath.ClassOf(true, false, true, true, false, false);
                Assert((bash & (RM_WallReachMath.NonOpener | RM_WallReachMath.GateShut | RM_WallReachMath.PlayerDoorsShut)) == 0,
                    "a basher gets no door bit");
                int animal = RM_WallReachMath.ClassOf(true, false, false, false, false, false);
                Assert((animal & RM_WallReachMath.NonOpener) != 0 && (animal & RM_WallReachMath.PlayerDoorsShut) != 0
                    && (animal & RM_WallReachMath.GateShut) != 0, "a non-opener is shut out of every door and the gate");
                Assert((RM_WallReachMath.ClassOf(false, true, false, false, true, true) & (RM_WallReachMath.FenceBlocked | RM_WallReachMath.NonSwimmer))
                    == (RM_WallReachMath.FenceBlocked | RM_WallReachMath.NonSwimmer), "fence and swim bits are mode-independent");
                Assert(RM_WallReachMath.ClassOf(true, false, false, true, true, true) < RM_WallReachMath.ClassCount, "class fits ClassCount");
            });

            // Scene A of drawbridge_proof (LOWER_ONLY_FROM_WINCH), the measured failure: trench x=1..4 at z=0 (4 m = 8 notches),
            // granite walls z=±1 x=-2..9 capped at x=-3/x=10. Plotted at +4 so x=-4 is column 0. Far pawn x=7, winch side x=-2.
            Case("WallReach_winch_site_walls_and_trench_cut_it_only_together", () =>
            {
                var s = Scene(
                    "...............",
                    ".############..",
                    "#...8888.....#.",
                    ".############..",
                    "...............");
                // row index 2 from top = z 2; far pawn at column 11 (x=7), winch-side lip (x=-2) at column 2
                Assert(SameWallComponent(s, Colonist, 11, 2, 2, 2), "vanilla half: the trench floor joins the banks (walls only)");
                Assert(SameDepthComponent(s, 11, 2, 2, 2), "depth half: the banks join round the trench ends over the wall squares");
                Assert(Veto(s, Colonist, 11, 2, 2, 2), "the joint graph: no route (each half said yes about a different one)");
                Assert(!Veto(s, Colonist, 2, 2, 3, 2), "the winch bank to its own lip: reachable");
                var open = Scene(
                    "...............",
                    ".############..",
                    "#...0000.....#.",
                    ".############..",
                    "...............");
                Assert(!Veto(open, Colonist, 11, 2, 2, 2), "the leaf lowered (trench read as ground): reachable");
            });

            Case("WallReach_ladders_rekeyed_down_across_and_up", () =>
            {
                var s = Scene(
                    "...............",
                    ".############..",
                    "#...8888.....#.",
                    ".############..",
                    "...............");
                int w = s.w;
                int I(int x, int z) => z * w + x;
                var oneWall = new List<(int, int)> { (I(4, 2), I(3, 2)) };      // a ladder on the winch-side wall only
                Assert(Veto(s, Colonist, 11, 2, 2, 2, ladderCells: oneWall), "one ladder: the far bank still cannot climb down its 4 m");
                var both = new List<(int, int)> { (I(4, 2), I(3, 2)), (I(7, 2), I(8, 2)) };
                Assert(!Veto(s, Colonist, 11, 2, 2, 2, ladderCells: both), "a ladder on each wall: down, across, up is one route");
                Assert(RM_WallReachMath.LadderEdge(RM_WallReachMath.Label(s.kind, s.depth, s.w, s.h, Person, Colonist), I(4, 2), I(3, 2), false) == null,
                    "a ladder that is no way for this query adds no edge");
            });

            // Locked drawbridge gate with a second gap behind the moat (V3, the case option 2 missed): the gate is the only gap in
            // the wall line z=3; behind it, a wall-gap at x=10 opens onto a moat (z=1, 4 m) the colonist cannot climb.
            Case("WallReach_locked_gate_and_second_gap_behind_the_moat", () =>
            {
                // the moat (z=1, 4 m) is bridged only below the gate (x=5: the lowered leaf reads as ground)
                var s = Scene(
                    "..............",
                    "#####g#####.##",
                    "88888088888888",
                    "..............");
                // inside (above the wall, z=3) at x=2; outside beyond the moat at z=0, x=2; the moat hugs the wall line
                Assert(SameWallComponent(s, Colonist, 2, 3, 2, 0), "vanilla half: out by the second gap and over the moat floor");
                Assert(SameDepthComponent(s, 2, 3, 2, 0), "depth half: through the gate square and over the leaf");
                Assert(Veto(s, Colonist, 2, 3, 2, 0), "the colonist: gate shut to everyone, the second gap ends at a 4 m moat: no route");
                Assert(!Veto(s, RaiderBashing, 2, 3, 2, 0), "a door-basher goes through the gate");
                var held = Scene(
                    "..............",
                    "#####h#####.##",
                    "88888088888888",
                    "..............");
                Assert(!Veto(held, Colonist, 2, 3, 2, 0), "the gate held open: reachable over the leaf");
            });

            // Animal at a door + trench: a wild animal outside a player door; the other way round is a 4 m trench.
            Case("WallReach_wild_animal_at_a_player_door_and_a_trench", () =>
            {
                var s = Scene(
                    "...........",
                    "####p######",
                    "...........",
                    ".......8888",
                    "...........");
                // the wall line z=3 runs edge to edge except the door; a trench cuts nothing here, so open the right edge
                var withGap = Scene(
                    "...........",
                    "####p#####.",
                    "..........8",
                    "..........8",
                    "..........8");
                Assert(!Veto(withGap, Colonist, 2, 0, 2, 4), "a colonist walks through the door");
                Assert(SameWallComponent(withGap, WildAnimal, 2, 0, 2, 4), "walls half: round the end by the gap over the trench floor");
                Assert(SameDepthComponent(withGap, 2, 0, 2, 4), "depth half: through the door square");
                Assert(Veto(withGap, WildAnimal, 2, 0, 2, 4), "the wild animal: door shut, the gap round the end is a 4 m trench: no route");
                var noTrench = Scene(
                    "...........",
                    "####p#####.",
                    "...........",
                    "...........",
                    "...........");
                Assert(!Veto(noTrench, WildAnimal, 2, 0, 2, 4), "with no trench it walks round by the gap");
                Assert(Veto(s, WildAnimal, 2, 0, 2, 4), "sealed wall line: shut out (vanilla agrees; the veto only repeats a no)");
            });

            // Non-swimmer at a water moat: no dug square at all, so only the swim half runs (depth null).
            Case("WallReach_non_swimmer_at_a_water_moat", () =>
            {
                var s = Scene(
                    ".......",
                    ".~~~~~.",
                    ".~...~.",
                    ".~~~~~.",
                    ".......");
                Assert(Veto(s, NonSwimmerColonist, 0, 0, 3, 2, useDepth: false), "a non-swimmer cannot cross the moat to the island");
                Assert(!Veto(s, Colonist, 0, 0, 3, 2, useDepth: false), "a swimmer can");
                Assert(SameWallComponent(s, Colonist, 0, 0, 3, 2), "vanilla's regions see the water as walkable (the lie)");
            });

            Case("WallReach_vetoed_never_on_an_unknown", () =>
            {
                Assert(!RM_WallReachMath.Vetoed(-1, new[] { 3 }, null), "start on a square its class cannot stand on: vanilla decides");
                Assert(!RM_WallReachMath.Vetoed(2, new[] { -1, -1 }, null), "no passable goal square: never a no");
                Assert(!RM_WallReachMath.Vetoed(2, new[] { -1, 2 }, null), "any goal square in the start's component clears it");
                Assert(RM_WallReachMath.Vetoed(2, new[] { 5, -1 }, null), "goals all in another component: vetoed");
                Assert(!RM_WallReachMath.Vetoed(2, new[] { 5 }, new List<(int, int)> { (2, 7), (7, 5) }), "ladder hops clear it");
                Assert(RM_WallReachMath.Vetoed(2, new[] { 5 }, new List<(int, int)> { (2, 7) }), "a ladder elsewhere does not");
            });

            Case("WallReach_ramp_joins_any_band", () =>
            {
                var s = Scene(
                    ".....",
                    "..8..",
                    ".....");
                int w = s.w;
                RM_WallReachMath.Labels l0 = RM_WallReachMath.Label(s.kind, s.depth, s.w, s.h, Person, Colonist);
                Assert(l0.At(2, 1) != l0.At(1, 1), "a 4 m hole is its own component");
                RM_WallReachMath.Labels l1 = RM_WallReachMath.Label(s.kind, s.depth, s.w, s.h, Person, Colonist,
                    (a, b) => a == 1 * w + 2 && b == 1 * w + 1);
                Assert(l1.At(2, 1) == l1.At(1, 1), "a ramp joins its pair whatever the step");
            });

            Case("WallReach_bounded_log_and_rebuild_throttle", () =>
            {
                int logged = 0;
                for (int n = 1; n <= 10000; n++) if (RM_WallReachMath.ShouldLog(n, 10)) logged++;
                Assert(logged == 10 + 9, "10000 residuals log 19 lines (10 one by one, then 20,40,…,5120): got " + logged);
                Assert(!RM_WallReachMath.ShouldLog(0, 10) && RM_WallReachMath.ShouldLog(10, 10) && !RM_WallReachMath.ShouldLog(11, 10)
                    && RM_WallReachMath.ShouldLog(20, 10) && !RM_WallReachMath.ShouldLog(30, 10) && RM_WallReachMath.ShouldLog(40, 10), "the schedule");
                Assert(!RM_WallReachMath.RebuildDue(false, true, true, 100, 0, 60), "fresh labels are never rebuilt");
                Assert(!RM_WallReachMath.RebuildDue(true, false, false, 59, 0, 60) && RM_WallReachMath.RebuildDue(true, false, false, 60, 0, 60),
                    "stale: at most once per 60 ticks");
                Assert(RM_WallReachMath.RebuildDue(true, true, false, 1, 0, 60) && RM_WallReachMath.RebuildDue(true, false, true, 1, 0, 60),
                    "forced (breach, toggle, gate) or paused: now");
                Assert(RM_WallReachMath.Classify(false, true) == RM_WallReachMath.FailKind.OutOfScope
                    && RM_WallReachMath.Classify(true, true) == RM_WallReachMath.FailKind.Stale
                    && RM_WallReachMath.Classify(true, false) == RM_WallReachMath.FailKind.Residual, "residual classification");
            });

            // The 4-neighbour claim (RM_WallReachMath.Label's doc): on random maps the labels equal an 8-way BFS with the
            // pathfinder's corner rules (no diagonal past an impassable square, RM_PitTrapMath.DiagonalAllowed for depth).
            // And the labels REFINE both halves: same wall-aware component => same depth component and same walls-only one.
            Case("WallReach_fuzz_four_way_equals_eight_way_and_refines_both_halves", () =>
            {
                var rng = new Random(20261021);
                for (int t = 0; t < 400; t++)
                {
                    int w = 6 + rng.Next(10), h = 6 + rng.Next(10), n = w * h;
                    var kind = new byte[n];
                    var depth = new byte[n];
                    for (int i = 0; i < n; i++)
                    {
                        int r = rng.Next(100);
                        kind[i] = r < 18 ? W : r < 22 ? PD : r < 25 ? DW : r < 27 ? F : O;
                        depth[i] = (byte)(rng.Next(100) < 30 ? rng.Next(0, 9) : 0);
                    }
                    int cls = rng.Next(RM_WallReachMath.ClassCount);
                    int k = 1 + rng.Next(4);
                    RM_WallReachMath.Labels l = RM_WallReachMath.Label(kind, depth, w, h, k, cls);
                    RM_PocketGridMath.Labels pg = RM_PocketGridMath.Label(depth, w, h, k);
                    RM_WallReachMath.Labels wallsOnly = RM_WallReachMath.Label(kind, null, w, h, k, cls);
                    // 8-way BFS from every square
                    var seen = new int[n];
                    for (int i = 0; i < n; i++) seen[i] = -1;
                    int comp = 0;
                    var q = new Queue<int>();
                    bool P(int i) => RM_WallReachMath.Passable(kind[i], cls);
                    for (int s0 = 0; s0 < n; s0++)
                    {
                        if (!P(s0) || seen[s0] >= 0) continue;
                        seen[s0] = comp;
                        q.Enqueue(s0);
                        while (q.Count > 0)
                        {
                            int c = q.Dequeue(), x = c % w, z = c / w;
                            for (int dx = -1; dx <= 1; dx++)
                                for (int dz = -1; dz <= 1; dz++)
                                {
                                    if (dx == 0 && dz == 0) continue;
                                    int nx = x + dx, nz = z + dz;
                                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                                    int ni = nz * w + nx;
                                    if (!P(ni) || seen[ni] >= 0) continue;
                                    bool ok;
                                    if (dx != 0 && dz != 0)
                                    {
                                        int a = z * w + nx, b = nz * w + x;
                                        ok = P(a) && P(b) && RM_PitTrapMath.DiagonalAllowed(depth[c], depth[ni], depth[a], depth[b], k);
                                    }
                                    else
                                    {
                                        ok = RM_PitTrapMath.StepAllowed(depth[c], depth[ni], k);
                                    }
                                    if (!ok) continue;
                                    seen[ni] = comp;
                                    q.Enqueue(ni);
                                }
                        }
                        comp++;
                    }
                    for (int i = 0; i < n; i++)
                    {
                        Assert((l.label[i] < 0) == (seen[i] < 0), "passability agrees, map " + t);
                    }
                    for (int i = 0; i < n; i++)
                        for (int j = i + 1; j < n; j++)
                        {
                            if (l.label[i] < 0 || l.label[j] < 0) continue;
                            bool same = l.label[i] == l.label[j];
                            Assert(same == (seen[i] == seen[j]), "4-way labels == 8-way BFS with corner rules, map " + t + " cells " + i + "," + j);
                            if (same)
                            {
                                Assert(pg.label[i] == pg.label[j], "refines the depth-only labels, map " + t);
                                Assert(wallsOnly.label[i] == wallsOnly.label[j], "refines the walls-only labels, map " + t);
                            }
                        }
                }
            });

            // De-risk step 1, offline: the cost of one labelling on a 250x250 map with holes (the in-game read is ProofPocketTiming).
            Case("WallReach_offline_rebuild_ms_250_square", () =>
            {
                int w = 250, h = 250, n = w * h;
                var rng = new Random(7);
                var kind = new byte[n];
                var depth = new byte[n];
                for (int i = 0; i < n; i++) kind[i] = rng.Next(100) < 12 ? W : O;
                for (int p = 0; p < 40; p++)
                {
                    int cx = rng.Next(w), cz = rng.Next(h), r = 3 + rng.Next(8), d = 1 + rng.Next(8);
                    for (int x = Math.Max(0, cx - r); x < Math.Min(w, cx + r); x++)
                        for (int z = Math.Max(0, cz - r); z < Math.Min(h, cz + r); z++)
                            depth[z * w + x] = (byte)d;
                }
                RM_WallReachMath.Label(kind, depth, w, h, Person, Colonist);   // JIT warm-up
                RM_PocketGridMath.Label(depth, w, h, Person);
                var sw = Stopwatch.StartNew();
                const int reps = 6;
                for (int b = 1; b <= reps; b++) RM_WallReachMath.Label(kind, depth, w, h, b, Colonist);
                double wallMs = sw.Elapsed.TotalMilliseconds / reps;
                sw.Restart();
                for (int b = 1; b <= reps; b++) RM_PocketGridMath.Label(depth, w, h, b);
                double pocketMs = sw.Elapsed.TotalMilliseconds / reps;
                Console.WriteLine("        offline 250x250: wall-aware label " + wallMs.ToString("0.00") + " ms/band, depth-only pocket label "
                    + pocketMs.ToString("0.00") + " ms/band (net8 JIT, not Unity Mono: an order-of-magnitude read only)");
                Assert(wallMs < 200, "one band labels in under 200 ms offline (got " + wallMs.ToString("0.0") + ")");
            });

            Case("WallReach_wiring_source_pins", () =>
            {
                string wr = Src("Superdeep", "RM_WallReach.cs");
                RiverSwitchFlipChecks.Has(wr, @"\[HarmonyPostfix\] \[HarmonyPriority\(Priority\.Low\)\] public static void Postfix\(IntVec3 start, LocalTargetInfo dest, PathEndMode peMode, TraverseParms traverseParams, ref bool __result, Map ___map\) \{ if \(!__result \|\| !RM_WallReach\.On\) \{ return; \}",
                    "the veto runs after vanilla and the depth veto, only on a yes");
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(wr, @"__result = true"), "the veto never turns a no into a yes");
                RiverSwitchFlipChecks.Has(wr, @"tp\.mode == TraverseMode\.PassAllDestroyableThings \|\| tp\.mode == TraverseMode\.PassAllDestroyablePlayerOwnedThings \|\| tp\.mode == TraverseMode\.PassAllDestroyableThingsNotWater\) \{ return false; \}",
                    "sappers skip the wall half (V12)");
                RiverSwitchFlipChecks.Has(wr, @"TouchPathEndModeUtility\.IsAdjacentCornerAndNotAllowed\(c, bl, tl, tr, br, pc, dest\.Thing\)", "the touch corner rule (V10)");
                RiverSwitchFlipChecks.Has(wr, @"\[HarmonyPatch\(typeof\(Pawn_PathFollower\), ""PatherFailed""\)\]", "the residual counter hooks PatherFailed");
                RiverSwitchFlipChecks.Has(wr, @"req == null \|\| req\.Found != false", "it counts only a path request that came back not found");
                RiverSwitchFlipChecks.Has(wr, @"RM_WallReachMath\.ShouldLog\(Residual, LogFirst\)", "the residual log is bounded");
                RiverSwitchFlipChecks.Has(wr, @"\[HarmonyPatch\(typeof\(ConnectivitySource\), nameof\(ConnectivitySource\.UpdateIncrementally\)\)\]", "the walkability generation");
                string pg = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(pg, @"RebuildIfStale\(map, eng, false\); RM_WallReach\.Tick\(map, false\);", "rebuilt from the map tick");
                RiverSwitchFlipChecks.Has(pg, @"RM_WallReach\.Force\(map\);.{0,160}RM_WallReach\.Tick\(map, true\);", "a drawbridge toggle forces it");
                RiverSwitchFlipChecks.Has(pg, @"lastBandMs\[k\] = band\.Elapsed\.TotalMilliseconds;", "per-band rebuild timing");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                RiverSwitchFlipChecks.Has(db, @"map\.reachability\?\.ClearCache\(\); // phase 6: drawbridge gates open for nobody while locked \(R4, R7\) RM_WallReach\.Bump\(map\);",
                    "a gate lock flip bumps it at once");
                string gate = Src("Pits", "Drawbridge", "RM_DrawbridgeControl.cs");
                RiverSwitchFlipChecks.Has(gate, @"public bool ShutToEveryone => .*!RM_DrawbridgeMath\.GateOpensFor\(RM_Drawbridges\.Locked\(Map\), l\.progress > 0, HoldOpen\);",
                    "the gate's shut state is PawnCanOpen's own rule");
                string s = Src("RimMandrakeFlowWorksMod.cs");
                Assert(s.Contains("public static bool reachSeesWallsAndCliffs = true;") && s.Contains("Scribe_Values.Look(ref reachSeesWallsAndCliffs, \"reachSeesWallsAndCliffs\", true);")
                    && s.Contains("\"reachSeesWallsAndCliffs\"") && s.Contains("\"Reachability sees walls and cliffs together\""),
                    "the Mod Setting: default on, saved, listed, labelled");
            });
        }
    }
}
