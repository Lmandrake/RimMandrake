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

            Case("Ramp_beats_ladder_and_both_join", () =>
            {
                // PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS (design §8.4): a ramp walks flat, a ladder costs per level, so stairs beat ladders
                int climb = 300;
                int ramp = RM_PitTrapMath.StepCost(4, 1, Person, climb, viaRamp: true);
                int ladder = RM_PitTrapMath.StepCost(4, 0, Person, climb, viaLadder: true, ladderCostPerLevel: climb * 2);
                Assert(ramp == 0, "a ramp step is a flat walk");
                Assert(ladder == 2400 && ladder > ramp, "a ladder spans 4 levels at 2 climbs a level");
                Assert(RM_PitTrapMath.StepAllowed(4, 0, Rat, ladderJoinsForPawn: true), "a ladder spans any depth");
                // a ramp D 4 -> D 1 then a 1-step: a rat (K 1) walks out; D 4 -> D 0 needs two ramps
                int w = 9, h = 7;
                byte[] g = Map(w, h);
                Rect(g, w, 2, 2, 3, 3, 4);
                g[3 * w + 5] = 1;
                Func<int, int, bool> one = (a, b) => a == 3 * w + 4 && b == 3 * w + 5 && RM_CliffMaskMath.RampJoins(g[a], g[b], 3);
                Assert(!RM_PocketGridMath.Label(g, w, h, Rat, one).IsPocketCell(3, 3), "ramp 4 -> 1, step 1 -> 0: the rat is out");
                g[3 * w + 5] = 0;
                Assert(RM_PocketGridMath.Label(g, w, h, Rat, one).IsPocketCell(3, 3), "facing D 0 (4 levels) the ramp joins nothing");
                Assert(!RM_CliffMaskMath.RampJoins(4, 2, 1), "span 1: only one level");
            });

            Case("Ramp_wiring_pinned_at_call_sites", () =>
            {
                string ramp = Src("Superdeep", "RM_PitRamp.cs");
                Assert(ramp.Contains("RM_CliffMaskMath.RampJoins(") && ramp.Contains("r.Rotation.FacingCell == high"), "a ramp joins the square it faces, uphill");
                Assert(ramp.Split(new[] { "BumpClimbGeneration()" }, StringSplitOptions.None).Length >= 3, "spawn and despawn move the climb generation");
                Assert(ramp.Contains("RM_LadderUtility.HasLadder(map, loc)") && ramp.Contains("RMFlow_RampMustFaceUphill"), "placement rules (§8.4)");
                Assert(Src("Superdeep", "RM_CliffMask.cs").Contains("return RM_PitRamp.Joins(map, a, b, aD, bD);"), "the masks and the floor see ramps");
                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                Assert(grid.Contains("RM_PitRamp.Pairs(map, depth)") && grid.Contains("RM_PocketGridMath.Label(depth, w, h, k, rampJoins)"), "the pocket grid sees ramps");
                string lad = Src("Superdeep", "RM_LadderUtility.cs");
                Assert(lad.Contains("RMFlow_LadderNeedsWall") && lad.Contains("RM_PitRamp.RampAt(map, loc)"), "a ladder stands at a wall, never on a ramp");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("\"pitRampsEnabled\", true") && mod.Contains("\"pitRampMaxSpan\", 3") && mod.Contains("\"pitLadderSlowness\", 2f"),
                    "Mod Settings: Ramps, Levels a ramp spans, Ladder slowness");
                string defs = Src("..", "Defs", "Canals", "ThingDefs", "FlowWorks_ThingDefs.xml");
                Assert(defs.Contains("<defName>RM_PitRamp</defName>") && defs.Contains("PlaceWorker_PitRamp") && defs.Contains("Excavation/RM_PitRamp</texPath>")
                    && !defs.Contains("(Placeholder art.)"),
                    "the ramp def ships, placement-checked, drawing its own four-facing art");
                string races = Src("..", "Patches", "Canals", "FlowWorks_ClimbAbility.xml");
                Assert(races.Contains("RM_ClimbAbility") && races.Contains("defName=\"Squirrel\"") && races.Contains("<leaper>true</leaper>"),
                    "climbers and leapers carry RM_ClimbAbility (§8.2 modifiers)");
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

            Case("Cliff_mask_lowered_ladder_at_wall_lets_a_person_down_and_out_of_D4", () =>
            {
                // V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT (v2 P4/P4f/P5n): a 1×1 D 4 pit, a lowered ladder in it (against a wall on
                // all four sides). The join is RM_ClimbJoins.Structural's: the ladder in the DEEPER cell, LadderJoins(deep, shallow).
                int w = 7, h = 7, pit = 3 * w + 3, lip = 3 * w + 1;
                byte[] g = Map(w, h);
                g[pit] = 4;
                Func<int, int, bool> ladder = (i, j) =>
                {
                    int deep = g[i] > g[j] ? i : j, shallow = deep == i ? j : i;
                    return deep == pit && RM_CliffMaskMath.LadderJoins(g[deep], g[shallow]);
                };
                Assert(!Flood(g, w, h, Person, 1, 3).Contains(pit), "no ladder: a person cannot walk down into D 4");
                Assert(Flood(g, w, h, Person, 3, 3).Count == 1, "no ladder: a person in D 4 is walled in");
                Assert(Flood(g, w, h, Person, 1, 3, ladder).Contains(pit), "lowered ladder: a person climbs down into D 4");
                Assert(Flood(g, w, h, Person, 3, 3, ladder).Contains(lip), "lowered ladder: a person climbs out to the lip");
                // the masks only learn of the ladder through the climb generation: a built or removed ladder must move it
                string lad = Src("Superdeep", "RM_LadderUtility.cs");
                int b = lad.IndexOf("class RM_Building_Ladder", StringComparison.Ordinal);
                int e = lad.IndexOf("class RM_LadderRules", StringComparison.Ordinal);
                string body = b < 0 || e < b ? "" : lad.Substring(b, e - b);
                Assert(body.Contains("override void SpawnSetup") && body.Contains("override void DeSpawn"),
                    "RM_Building_Ladder hooks spawn and despawn");
                Assert(body.Split(new[] { "BumpClimbGeneration()" }, StringSplitOptions.None).Length - 1 >= 2,
                    "building or removing a ladder re-derives the cliff masks (Standable, pathCost 0: vanilla sends no cell delta)");
                // the masks only re-check the generation inside vanilla's incremental update, which runs only on a cell delta (R4 live:
                // the generation bump alone left P4/P4f/P5n red), so spawn, despawn and the raise/lower toggle each push one
                Assert(lad.Split(new[] { "Notify_CellDelta(" }, StringSplitOptions.None).Length - 1 >= 3,
                    "ladder spawn, despawn and toggle each push a vanilla cell delta so the masks re-derive");
            });

            Case("Pawnless_reach_counts_a_lowered_ladder_as_the_masks_do", () =>
            {
                // V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT, the third cause (R5): with masks current (R4 live: pit 0x0F) the walk still
                // failed, because vanilla Pawn_PathFollower.StartPath (decompiled 1.6) first asks Reachability.CanReach(pawn.Position,
                // dest, peMode, TraverseParms.For(TraverseMode.PassDoors)) — NO pawn — and RM_SuperdeepTrap.RelativeVeto gave a
                // pawnless query no ladder: surface -> laddered pocket and pocket -> surface were both vetoed, PatherFailed.
                int w = 7, h = 7;
                byte[] g = Map(w, h);
                g[3 * w + 3] = 4;                       // v2 P_walk: a 1x1 D 4 pit, ladder lowered in it
                var l = RM_PocketGridMath.Label(g, w, h, Person);
                bool destPocket = l.IsPocketCell(3, 3), startPocket = l.IsPocketCell(3, 0);
                Assert(destPocket && !startPocket && !l.SameComponent(0, 3 * w + 3), "the pit is its own person-band pocket");
                bool pawnlessLowered = RM_PocketGridMath.LadderIsAWay(false, true, false);
                // the old rule (pawnless: no ladder) reproduces the live failure both ways
                Assert(RM_PocketGridMath.ReachVetoed(false, false, false, true, false), "old: pawnless walk IN vetoed (P4, P5n)");
                Assert(RM_PocketGridMath.ReachVetoed(false, true, !RM_PocketGridMath.Trapped(true, false, true), false, false),
                    "old: pawnless walk OUT vetoed (P4f)");
                // the fix
                Assert(pawnlessLowered, "a pawnless query counts a lowered ladder");
                Assert(!RM_PocketGridMath.ReachVetoed(false, startPocket, false, destPocket, pawnlessLowered), "pawnless: in by the ladder");
                Assert(!RM_PocketGridMath.ReachVetoed(false, true, !RM_PocketGridMath.Trapped(true, pawnlessLowered, true), false, false),
                    "pawnless: out by the ladder");
                // what must NOT change
                Assert(!RM_PocketGridMath.LadderIsAWay(false, false, true), "pawnless: a RAISED ladder is no way");
                Assert(!RM_PocketGridMath.LadderIsAWay(true, true, false), "a hostile's own query: the prison door holds");
                Assert(RM_PocketGridMath.LadderIsAWay(true, true, true), "a colonist's own query: its ladder");
                Assert(RM_PocketGridMath.ReachVetoed(false, false, false, true, RM_PocketGridMath.LadderIsAWay(true, true, false)),
                    "a hostile is still kept out of (and in) a laddered pocket");
                Assert(!RM_PocketGridMath.ReachVetoed(true, true, false, true, false), "same component: never vetoed");
                // pinned at the call sites
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("RM_PocketGridMath.ReachVetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn,")
                    && !trap.Contains("p != null && g.ComponentIsPocket(k, cd)"), "RelativeVeto decides by ReachVetoed, pawnless included");
                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                Assert(grid.Contains("RM_PocketGridMath.LadderIsAWay(p != null, p == null && RM_ClimbJoins.LoweredLadderAt(map, c)"),
                    "UsableLadderIn: pawnless counts a lowered ladder");
            });

            Case("Reach_veto_needs_a_way_at_both_ends", () =>
            {
                // REACH_VETO_FIX_ONE_END_ENOUGH (GPT C3-F8/C4-F2): either end having a way used to clear the veto, so a laddered
                // pocket "reached" a sealed one (and a sealed one a laddered one); A* then refused and the job looped on PatherFailed.
                Assert(RM_PocketGridMath.ReachVetoed(false, true, true, true, false), "laddered pocket -> sealed pocket: vetoed");
                Assert(RM_PocketGridMath.ReachVetoed(false, true, false, true, true), "sealed pocket -> laddered pocket: vetoed");
                Assert(!RM_PocketGridMath.ReachVetoed(false, true, true, true, true), "laddered -> laddered: allowed");
                Assert(!RM_PocketGridMath.ReachVetoed(false, true, true, false, false), "laddered pocket -> surface: allowed");
                Assert(!RM_PocketGridMath.ReachVetoed(false, false, false, true, true), "surface -> laddered pocket: allowed");
                Assert(RM_PocketGridMath.ReachVetoed(false, false, false, true, false), "surface -> sealed pocket: vetoed");
                Assert(RM_PocketGridMath.ReachVetoed(false, true, false, false, false), "sealed pocket -> surface: vetoed");
                Assert(RM_PocketGridMath.ReachVetoed(false, false, false, false, false), "two surface components stay apart");
                Assert(!RM_PocketGridMath.ReachVetoed(true, true, false, true, false), "same component: never vetoed");
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(!trap.Contains("!startWayOut && destPocket"), "RelativeVeto judges the destination's way in on its own");
            });

            Case("Map_edge_island_ringed_by_a_trench_is_cut_off", () =>
            {
                // REACH_VETO_FIX_ONE_END_ENOUGH (GPT C3-F9): the map-edge veto only knew pockets; a surface island inside a sheer
                // moat is a SURFACE component (TrappedIn false), so its pawns believed they could leave the map.
                int w = 9, h = 9;
                byte[] g = Map(w, h);
                for (int x = 1; x <= 7; x++)
                    for (int z = 1; z <= 7; z++)
                        if (x == 1 || x == 7 || z == 1 || z == 7) g[z * w + x] = 4;   // a D 4 moat ring
                var l = RM_PocketGridMath.Label(g, w, h, Person);
                int island = l.label[4 * w + 4], outer = l.label[0];
                Assert(island != outer && l.surface[island] && l.surface[outer], "island and outside are two surface components");
                Assert(!RM_PocketGridMath.TouchesEdge(l, island), "the island holds no border cell");
                Assert(RM_PocketGridMath.TouchesEdge(l, outer), "the outside does");
                Assert(!RM_PocketGridMath.TouchesEdge(l, l.label[1 * w + 1]) && !l.surface[l.label[1 * w + 1]], "the moat is a pocket");
                var big = RM_PocketGridMath.Label(g, w, h, 5);
                Assert(big.label[4 * w + 4] == big.label[0], "a climber of 5 crosses the moat: one component");
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("g.TrappedIn(k, comp, p) || (!walksOut && !g.ReachesEdge(k, comp, p))"),
                    "the map-edge postfix vetoes an island or a pit pocket with no way to the edge (unless ladders this pawn may use join it to a border component)");
                Assert(trap.Contains("n.Walkable(p.Map) && eng.IsSuperdeepExcavation(n)"), "absolute-rule trap BFS never crosses a wall (C3-F12)");
            });

            Case("Trench_laddered_on_both_walls_is_one_route", () =>
            {
                // TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP: bank A (x 0-2, D 0) | sheer D 3 trench (x 3-5) | bank B (x 6-8, D 0).
                // A ladder on the near wall (3,1) hung west toward A and one on the far wall (5,1) hung east toward B. Before the
                // fix ReachVetoed kept any two surface components apart, so this was never one hop (raiders were sent INTO the
                // trench first; a colonist crossing by two ladders was refused).
                int w = 9, h = 3;
                byte[] g = Map(w, h);
                Rect(g, w, 3, 0, 3, h, 3);
                var l = RM_PocketGridMath.Label(g, w, h, Person);
                int A = l.label[1 * w + 0], P = l.label[1 * w + 4], B = l.label[1 * w + 8];
                Assert(A != P && P != B && A != B && l.surface[A] && l.surface[B] && !l.surface[P], "A, trench, B: three components");
                const int West = 3, East = 1;
                // one ladder's edge, the way production builds it (RM_PocketGrid.LadderEdges)
                List<(int a, int b)> Edges(bool nearWay, bool farWay, int nearRot = West, int farRot = East)
                {
                    var e = new List<(int a, int b)>();
                    foreach ((int x, int rot, bool way) in new[] { (3, nearRot, nearWay), (5, farRot, farWay) })
                    {
                        int ox = x + RM_LadderWallMath.FX[rot], oz = 1 + RM_LadderWallMath.FZ[rot];
                        int a = l.label[1 * w + x], b = l.label[oz * w + ox];
                        if (RM_PocketGridMath.LadderEdge(rot, g[1 * w + x], a, g[oz * w + ox], b, way)) e.Add((a, b));
                    }
                    return e;
                }
                bool Way(bool mayClimb, bool ownLadder, bool raised = false, bool prisonDoor = true) =>
                    RM_PocketGridMath.LadderIsAWay(true, !raised, RM_PitTrapMath.LadderUsable(true, raised, prisonDoor, mayClimb || ownLadder));
                bool Vetoed(List<(int a, int b)> e) =>
                    RM_PocketGridMath.ReachVetoedWhole(false, false, false, false, false, false, () => RM_PocketGridMath.JoinedByLadders(A, B, e));

                // colonist: down the near ladder, across the floor, up the far one
                bool col = Way(true, false);
                Assert(!Vetoed(Edges(col, col)), "a colonist crosses bank to bank by two ladders: one route");
                Assert(!RM_PocketGridMath.ReachVetoedWhole(false, false, false, false, false, false, () => RM_PocketGridMath.JoinedByLadders(B, A, Edges(col, col))),
                    "and back the other way (a ladder is climbed down and up)");
                Assert(RM_PocketGridMath.ReachVetoed(false, false, false, false, false), "can-fail: the old veto alone kept the banks apart");
                Assert(Vetoed(Edges(col, false)), "can-fail: one ladder only (near wall) is no crossing");
                Assert(Vetoed(Edges(false, col)), "can-fail: one ladder only (far wall) is no crossing");
                Assert(Vetoed(Edges(col, col, nearRot: East)), "can-fail: a ladder hung toward the trench floor joins nothing");
                // raider: the raid's own scaling ladders (ClimbsOwnLadder) — prison door refuses it everything else
                Assert(!Vetoed(Edges(Way(false, true), Way(false, true))), "a raider crosses on its own faction's ladders");
                Assert(Vetoed(Edges(Way(false, true), Way(false, false))), "can-fail: one own ladder, one colony ladder: the far wall bars it");
                // hostile on ladders that are not its own: the prison-door rule
                Assert(Vetoed(Edges(Way(false, false), Way(false, false))), "a hostile on ladders not its own: refused (prison door)");
                Assert(!Vetoed(Edges(Way(false, false, prisonDoor: false), Way(false, false, prisonDoor: false))),
                    "sanity: prison-door rule off, the same hostile crosses (the refusal is the rule, not the graph)");
                // raised ladders
                Assert(Vetoed(Edges(Way(true, false, raised: true), col)), "a raised ladder blocks the crossing, even for a colonist");
                Assert(!RM_PocketGridMath.LadderIsAWay(false, false, true) && RM_PocketGridMath.LadderIsAWay(false, true, false),
                    "pawnless (vanilla StartPath): any lowered ladder joins, a raised one does not");
                // a sealed pocket stays sealed: ladders into a pit with no way on are no route to the other bank
                Assert(!RM_PocketGridMath.JoinedByLadders(A, B, new List<(int a, int b)> { (P, A) }), "can-fail: A to the floor only");
                Assert(RM_PocketGridMath.JoinedByLadders(A, P, Edges(col, false)), "A to the trench floor by the near ladder");
                Assert(!RM_PocketGridMath.JoinedByLadders(-1, B, Edges(col, col)), "can-fail: an off-map start joins nothing");

                // the pathfinder agrees: the masks restore exactly the edges the graph uses (a structural ladder join)
                int near = 1 * w + 3, nearWall = 1 * w + 2, far = 1 * w + 5, farWall = 1 * w + 6;
                Func<int, int, bool> both = (i, j) => (i == near && j == nearWall) || (i == far && j == farWall);
                Func<int, int, bool> one = (i, j) => i == near && j == nearWall;
                Assert(Flood(g, w, h, Person, 0, 1, both).Contains(1 * w + 8), "A* (cardinal mask flood): A reaches B by both ladders");
                Assert(!Flood(g, w, h, Person, 0, 1, one).Contains(1 * w + 8), "can-fail: A* with one ladder does not reach B");
                Assert(!Flood(g, w, h, Person, 0, 1).Contains(1 * w + 4), "can-fail: A* with no ladder never enters the trench");

                // an island in a sheer moat, laddered in and out, reaches the map edge
                int mw = 9, mh = 9;
                byte[] m = Map(mw, mh);
                for (int x = 1; x <= 7; x++)
                    for (int z = 1; z <= 7; z++)
                        if (x == 1 || x == 7 || z == 1 || z == 7) m[z * mw + x] = 4;
                var ml = RM_PocketGridMath.Label(m, mw, mh, Person);
                int island = ml.label[4 * mw + 4], outer = ml.label[0], moat = ml.label[4 * mw + 1];
                var me = new List<(int a, int b)>();
                // (1,4) hung east toward the island (2,4); (1,3) hung west toward the outside (0,3)
                if (RM_PocketGridMath.LadderEdge(East, 4, moat, 0, ml.label[4 * mw + 2], true)) me.Add((moat, ml.label[4 * mw + 2]));
                if (RM_PocketGridMath.LadderEdge(West, 4, ml.label[3 * mw + 1], 0, ml.label[3 * mw + 0], true)) me.Add((ml.label[3 * mw + 1], outer));
                Assert(me.Count == 2 && RM_PocketGridMath.JoinedByLadders(island, outer, me) && RM_PocketGridMath.TouchesEdge(ml, outer),
                    "a laddered island joins the border component (CanReachMapEdge agrees)");
                Assert(!RM_PocketGridMath.JoinedByLadders(island, outer, me.GetRange(0, 1)), "can-fail: laddered in only: still an island");

                // pinned at the call sites
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("RM_PocketGridMath.ReachVetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn,")
                    && trap.Contains("() => g.JoinedByLadders(k, cs, cd, p))"), "RelativeVeto lifts the veto through the ladder graph");
                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                Assert(grid.Contains("RM_PocketGridMath.LadderEdge(rot, RM_SuperdeepTrap.StepDepthAt(map, eng, c), a,")
                    && grid.Contains("p != null && RM_LadderRules.LadderLetsOut(map, c, p)"),
                    "LadderEdges: per-pawn LadderLetsOut (prison door, own ladders, raised), pawnless lowered");
                string r = Src("Superdeep", "RM_RaiderTrench.cs");
                Assert(r.Contains("Warn(p, \"RMFlow_RaidersSetLadders\")") && r.Contains("key.Translate(p.Faction.Name)")
                    && !r.Contains("\"Raiders of \""), "raider messages are Keyed strings");
            });

            Case("Trench_reach_agrees_with_the_pathfinder_every_direction", () =>
            {
                // RAIDER_TRENCH_FIX_REACH_BOUNCE: a raider on the trench floor with only the near-wall ladder was told the FAR bank
                // was reachable (a pocket with any way out cleared the veto for every surface), A* found no path, the raid looped.
                // Property: for every ladder-usability case on each wall, from each of bank A, the floor and bank B to each other,
                // RelativeVeto's decision (ReachVetoedWhole) == "the cardinal mask flood (A*) does NOT reach it".
                int w = 9, h = 3;
                byte[] g = Map(w, h);
                Rect(g, w, 3, 0, 3, h, 3);
                var l = RM_PocketGridMath.Label(g, w, h, Person);
                const int West = 3, East = 1;
                int near = 1 * w + 3, far = 1 * w + 5;
                // the usability cases, as each query sees one ladder (RM_PocketGrid.LadderEdges / UsableLadderIn)
                bool Way(bool mayClimb, bool own, bool raised) =>
                    RM_PocketGridMath.LadderIsAWay(true, !raised, RM_PitTrapMath.LadderUsable(true, raised, true, mayClimb || own));
                var cases = new (string name, bool way)[]
                {
                    ("colonist", Way(true, false, false)),
                    ("raider on its own ladder", Way(false, true, false)),
                    ("hostile refused (prison door)", Way(false, false, false)),
                    ("raised", Way(true, false, true)),
                    ("pawnless lowered", RM_PocketGridMath.LadderIsAWay(false, true, false)),
                    ("pawnless raised", RM_PocketGridMath.LadderIsAWay(false, false, false)),
                };
                Assert(cases[0].way && cases[1].way && !cases[2].way && !cases[3].way && cases[4].way && !cases[5].way,
                    "the usability cases resolve as ruled");
                var ends = new (string name, int x)[] { ("bank A", 0), ("floor", 4), ("bank B", 8) };
                int checkedPairs = 0, bounces = 0;
                foreach (int nearRot in new[] { West, East })
                    foreach (var nc in cases)
                        foreach (var fc in cases)
                        {
                            var edges = new List<(int a, int b)>();
                            var restored = new List<(int i, int j)>();
                            bool usableInFloor = false;
                            foreach ((int c, int rot, bool way) in new[] { (near, nearRot, nc.way), (far, East, fc.way) })
                            {
                                int o = c + RM_LadderWallMath.FX[rot] + RM_LadderWallMath.FZ[rot] * w;
                                int a = l.label[c], b = l.label[o];
                                if (RM_PocketGridMath.LadderEdge(rot, g[c], a, g[o], b, way))
                                {
                                    edges.Add((a, b));
                                    restored.Add((c, o));   // the masks restore exactly this edge (RM_CliffMask)
                                    usableInFloor |= !l.surface[a];
                                }
                            }
                            Func<int, int, bool> join = (i, j) => restored.Exists(e => e.i == i && e.j == j);
                            foreach (var s in ends)
                                foreach (var d in ends)
                                {
                                    int si = 1 * w + s.x, di = 1 * w + d.x;
                                    if (l.SameComponent(si, di)) continue;
                                    int cs = l.label[si], cd = l.label[di];
                                    bool sp = !l.surface[cs], dp = !l.surface[cd];
                                    bool sNarrow = sp && !RM_PocketGridMath.WideEverywhere(l, cs, 1);
                                    bool dNarrow = dp && !RM_PocketGridMath.WideEverywhere(l, cd, 1);
                                    bool sOut = sp && !RM_PocketGridMath.Trapped(true, usableInFloor, !sNarrow);
                                    bool dIn = dp && (usableInFloor || dNarrow);
                                    bool vetoed = RM_PocketGridMath.ReachVetoedWhole(sp, sNarrow, sOut, dp, dNarrow, dIn,
                                        () => RM_PocketGridMath.JoinedByLadders(cs, cd, edges));
                                    bool astar = Flood(g, w, h, Person, s.x, 1, join).Contains(di);
                                    checkedPairs++;
                                    if (!vetoed && !astar) bounces++;
                                    Assert(vetoed == !astar, "reach and A* disagree: " + s.name + " -> " + d.name + ", near ladder "
                                        + nc.name + (nearRot == East ? " (hung toward the floor)" : "") + ", far ladder " + fc.name
                                        + ": reach " + (vetoed ? "vetoed" : "allowed") + ", A* " + (astar ? "reaches" : "does not"));
                                }
                        }
                Assert(checkedPairs == 2 * 6 * 6 * 6 && bounces == 0, "every pair checked (" + checkedPairs + "), no bounce");
                // the reported bug, by name: floor, near ladder only (colonist-usable), far bank
                Assert(!Flood(g, w, h, Person, 4, 1, (i, j) => i == near && j == near - 1).Contains(1 * w + 8),
                    "can-fail: A* from the floor up the near ladder never reaches the far bank");
                // pinned at the call site
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("RM_PocketGridMath.ReachVetoedWhole(startPocket, startNarrow, startWayOut, destPocket, destNarrow, destWayIn,")
                    && trap.Contains("() => g.JoinedByLadders(k, cs, cd, p))"), "RelativeVeto decides by ReachVetoedWhole");
            });

            Case("StartPath_reach_answers_for_the_walker_not_the_person_band", () =>
            {
                // PIT_REACH_VERIFY_FLYERS_AND_GIANTS (GPT C3-F4): vanilla StartPath's reach check is pawnless, and the veto read it
                // at the person band with no flyer exemption. A muffalo (K 3) up a 3-level step: apart at the person band, one
                // component in its own band. Answering for the walker (flyers exempt, own band) is the fix.
                int w = 6, h = 3;
                byte[] g = Map(w, h);
                Rect(g, w, 3, 0, 3, 3, 3);                                     // a D 3 shelf east of the surface
                var person = RM_PocketGridMath.Label(g, w, h, Person);
                var muff = RM_PocketGridMath.Label(g, w, h, Muffalo);
                Assert(!person.SameComponent(0, 5) && person.IsPocketCell(5), "person band: the shelf is a sealed pocket");
                Assert(RM_PocketGridMath.ReachVetoed(person.SameComponent(0, 5), false, false, true, false), "person band: vetoed");
                Assert(muff.SameComponent(0, 5), "muffalo band: one walk");
                Assert(!RM_PocketGridMath.ReachVetoed(muff.SameComponent(0, 5), false, false, false, false), "its own band: allowed");
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("[HarmonyPatch(typeof(Pawn_PathFollower), nameof(Pawn_PathFollower.StartPath))]")
                    && trap.Contains("public static class RM_Patch_PathFollower_ReachWalker"), "StartPath remembers its walker");
                Assert(trap.Contains("[ThreadStatic]") && trap.Contains("[HarmonyFinalizer]"), "the walker is restored even when StartPath throws or nests");
                Assert(trap.Contains("Pawn walker = p ?? RM_Patch_PathFollower_ReachWalker.WalkerAt(___map, start);")
                    && trap.Contains("RM_SuperdeepTrap.RelativeVeto(___map, start, dest, peMode, walker)"), "the CanReach veto answers for the walker");
            });

            Case("Too_wide_pawn_is_not_walled_in_by_the_masks", () =>
            {
                // PIT_REACH_VERIFY_FLYERS_AND_GIANTS (GPT C3-F5): IsHeld honours the width rule, the masks did not: a width-2
                // pawn in a 1-cell D 4 hole read "not held" yet its band's mask and the step floor sealed it in.
                int w = 5, h = 5;
                byte[] g = Map(w, h);
                g[2 * w + 2] = 4;
                var l = RM_PocketGridMath.Label(g, w, h, Muffalo);
                int hole = l.label[2 * w + 2];
                int wide = RM_PitTrapMath.RequiredWidth(2.4f, 1f);
                Assert(wide == 2 && RM_PitTrapMath.ClimbLimit(2.4f) == Muffalo, "a muffalo: K 3, width 2");
                Assert(l.IsPocketCell(2, 2) && !RM_PocketGridMath.WideEverywhere(l, hole, wide), "the hole is a pocket too narrow for it");
                Assert(!RM_PocketGridMath.Trapped(true, false, RM_PocketGridMath.WideEverywhere(l, hole, wide)), "so it is not trapped");
                string mask = Src("Superdeep", "RM_CliffMask.cs");
                Assert(mask.Contains("RM_PocketGrid.CanFly(p) || RM_SuperdeepTrap.InOwnPocketTooNarrow(p)"), "the masks step aside for it");
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("RM_PocketGrid.CanFly(pawn) || RM_SuperdeepTrap.InOwnPocketTooNarrow(pawn)"), "the step floor lets it out");
            });

            Case("Ramp_spawn_and_despawn_reach_the_masks", () =>
            {
                // RAMP_MASKS_VERIFY_STALE_SLOPE (GPT C3-F6, PLAUSIBLE): not a bug. RM_Building_PitRamp is a Building, and vanilla
                // Building.SpawnSetup / DeSpawn (decompiled 1.6) raise map.events BuildingSpawned / BuildingDespawned, which
                // PathFinderMapData.Notify_BuildingChanged turns into Notify_CellDelta(OccupiedRect). The masks' incremental pass
                // then sees the bumped climb generation in KeyFor and re-derives in full. Pinned so a refactor cannot break it.
                string ramp = Src("Superdeep", "RM_PitRamp.cs");
                Assert(ramp.Contains("public class RM_Building_PitRamp : Building"), "the ramp is a Building (vanilla pushes its cell delta)");
                Assert(ramp.Contains("base.SpawnSetup(map, respawningAfterLoad);") && ramp.Contains("base.DeSpawn(mode);"),
                    "the ramp keeps vanilla's spawn and despawn");
                Assert(ramp.Split(new[] { "BumpClimbGeneration()" }, StringSplitOptions.None).Length - 1 >= 2, "spawn and despawn move the generation");
                string mask = Src("Superdeep", "RM_CliffMask.cs");
                Assert(mask.Contains("long k = eng == null ? 0 : eng.ClimbGeneration;") && mask.Contains("if (KeyFor(eng) != m.key)"),
                    "a moved generation (or a ramp setting) makes the next incremental pass re-derive in full");
            });
        }
    }
}
