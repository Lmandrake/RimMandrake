// PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP (design/RimMandrake/relative_depth_climb_design_2026-10-12.md §8.1-8.3, §8.5 step 1).
// The arithmetic is PRODUCTION RM_PitTrapMath + RM_PocketGridMath; the Verse wiring (RM_PocketGrid, the trap seams) is pinned at
// its call sites by source checks below.
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PocketGridChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const int Person = 2, Rat = 1, Muffalo = 3;

        /// <summary>A w×h map, all surface; returns the grid to paint.</summary>
        private static byte[] Map(int w, int h) => new byte[w * h];

        private static void Rect(byte[] g, int w, int x0, int z0, int rw, int rh, byte d)
        {
            for (int x = x0; x < x0 + rw; x++)
                for (int z = z0; z < z0 + rh; z++)
                    g[z * w + x] = d;
        }

        private static bool Pocket(byte[] g, int w, int h, int k, int x, int z, Func<int, int, bool> ramp = null)
            => RM_PocketGridMath.Label(g, w, h, k, ramp).IsPocketCell(x, z);

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("Climb_limit_bands_by_body_size", () =>
            {
                Assert(RM_PitTrapMath.ClimbLimit(0.2f) == 1, "rat climbs 1");
                Assert(RM_PitTrapMath.ClimbLimit(0.74f) == 1, "just under the person edge climbs 1");
                Assert(RM_PitTrapMath.ClimbLimit(0.75f) == 2 && RM_PitTrapMath.ClimbLimit(1.0f) == 2, "person climbs 2");
                Assert(RM_PitTrapMath.ClimbLimit(1.64f) == 2 && RM_PitTrapMath.ClimbLimit(1.65f) == 3, "large edge at 1.65");
                Assert(RM_PitTrapMath.ClimbLimit(2.4f) == 3, "muffalo climbs 3");
                Assert(RM_PitTrapMath.ClimbLimit(3.0f) == 4 && RM_PitTrapMath.ClimbLimit(4.0f) == 4, "thrumbo climbs 4");
                Assert(RM_PitTrapMath.ClimbLimit(0.2f, 1) == 2, "a climbing rat (+1) climbs 2");
                Assert(RM_PitTrapMath.ClimbLimit(0f) == 1 && RM_PitTrapMath.ClimbLimit(-1f) == 1, "never below 1");
                Assert(RM_PitTrapMath.ClimbLimit(1.0f, 0, 0.5f) == 1, "multiplier 0.5 halves height: a person climbs 1");
                Assert(RM_PitTrapMath.ClimbLimit(0.5f, 0, 2f) == 3, "multiplier 2 doubles height (0.5 x 4 = 2.0 effective)");
            });

            Case("Step_allowed_relative_both_ways", () =>
            {
                Assert(RM_PitTrapMath.StepAllowed(4, 2, Person) && RM_PitTrapMath.StepAllowed(2, 0, Person), "a person climbs 2");
                Assert(!RM_PitTrapMath.StepAllowed(3, 0, Person), "a person cannot climb 3");
                Assert(!RM_PitTrapMath.StepAllowed(0, 3, Person), "nor jump DOWN 3 on purpose");
                Assert(RM_PitTrapMath.StepAllowed(3, 0, Muffalo) && !RM_PitTrapMath.StepAllowed(4, 0, Muffalo), "muffalo 3, not 4");
                Assert(!RM_PitTrapMath.StepAllowed(2, 0, Rat) && RM_PitTrapMath.StepAllowed(1, 0, Rat), "rat 1");
                Assert(RM_PitTrapMath.StepAllowed(4, 0, Rat, rampJoins: true), "a ramp joins for anyone");
                Assert(RM_PitTrapMath.StepAllowed(4, 0, Rat, ladderJoinsForPawn: true), "a ladder this pawn may use joins");
                Assert(RM_PitTrapMath.StepAllowed(4, 4, Rat) && RM_PitTrapMath.StepAllowed(0, 0, Rat), "flat is always a step");
            });

            Case("Diagonal_never_cuts_a_cliff_corner", () =>
            {
                Assert(RM_PitTrapMath.DiagonalAllowed(2, 2, 2, 2, Person), "flat diagonal");
                Assert(RM_PitTrapMath.DiagonalAllowed(4, 2, 3, 3, Person), "gentle diagonal");
                // from D 4 to D 2 diagonally, but one corner is the D 0 lip: the corner pair 4..0 is a cliff
                Assert(!RM_PitTrapMath.DiagonalAllowed(4, 2, 0, 2, Person), "a corner at D 0 forbids cutting it");
                Assert(!RM_PitTrapMath.DiagonalAllowed(3, 1, 3, 0, Person), "cardinal-allowed ends, cliff corner pair: refused");
            });

            Case("Step_cost_slow_at_K_free_on_ramp", () =>
            {
                Assert(RM_PitTrapMath.StepCost(2, 2, Person, 300) == 0, "equal depth costs nothing extra");
                Assert(RM_PitTrapMath.StepCost(2, 1, Person, 300) == 300, "1 of 2: a normal climb");
                Assert(RM_PitTrapMath.StepCost(2, 0, Person, 300) == 600, "2 of 2: a slow climb, x2");
                Assert(RM_PitTrapMath.StepCost(0, 2, Person, 300) == 600, "down costs the same as up");
                Assert(RM_PitTrapMath.StepCost(1, 0, Rat, 300) == 300, "K = 1 never slow");
                Assert(RM_PitTrapMath.StepCost(4, 1, Rat, 300, viaRamp: true) == 0, "a ramp walks flat");
                Assert(RM_PitTrapMath.StepCost(4, 0, Rat, 300, viaLadder: true, ladderCostPerLevel: 50) == 200, "ladder: per level");
                Assert(RM_PitTrapMath.StepCost(2, 0, Person, 300, slowFactor: 3f) == 900, "slow factor is a setting");
            });

            Case("Falls_by_drop_over_K", () =>
            {
                Assert(RM_PitTrapMath.ArrivalDropsTooFar(0, 4, Person), "0 -> 4 is a fall for a person");
                Assert(!RM_PitTrapMath.ArrivalDropsTooFar(0, 2, Person), "0 -> 2 is not (the pond shore)");
                Assert(RM_PitTrapMath.ArrivalDropsTooFar(0, 2, Rat), "0 -> 2 is a fall for a rat");
                Assert(!RM_PitTrapMath.ArrivalDropsTooFar(4, 0, Rat), "climbing up is never a fall");
                Assert(!RM_PitTrapMath.ArrivalDropsTooFar(0, 4, 4), "a thrumbo steps down 4");
                Assert(Math.Abs(RM_RelativeRulesMath.FallScaleNotches(4) - 1f) < 1e-6, "surface to D 4 = today's flat fall");
                Assert(Math.Abs(RM_RelativeRulesMath.FallScaleNotches(3) - 0.75f) < 1e-6, "3 of 4");
                Assert(RM_RelativeRulesMath.FallScaleNotches(0) == 0f && RM_RelativeRulesMath.FallScaleNotches(-2) == 0f, "no drop, no damage scale");
            });

            Case("Pocket_dried_pond_never_traps_a_person", () =>
            {
                // owner: "Natural ponds and lakes when pumped dry would leave just such gradual terrain so no chance to fall in
                // and get stuck". Shallow ring D 2, deep core D 4 (natural_bodies ruling 3).
                int w = 20, h = 20;
                byte[] g = Map(w, h);
                Rect(g, w, 5, 5, 10, 10, 2);
                Rect(g, w, 7, 7, 6, 6, 4);
                Assert(!Pocket(g, w, h, Person, 10, 10), "the D 4 core is no pocket for a person");
                Assert(!Pocket(g, w, h, Person, 5, 5), "nor the D 2 ring");
                Assert(Pocket(g, w, h, Rat, 10, 10), "a rat is held by the 2-deep shore (owner: a 2-deep trench traps rats)");
                Assert(!Pocket(g, w, h, Muffalo, 10, 10), "a muffalo walks out");
            });

            Case("Pocket_gradual_bowl_traps_nobody", () =>
            {
                int w = 21, h = 21;
                byte[] g = Map(w, h);
                for (byte d = 1; d <= 4; d++)
                    Rect(g, w, 2 * d, 2 * d, w - 4 * d, h - 4 * d, d);
                Assert(g[10 * w + 10] == 4, "precondition: the bowl reaches D 4 at its centre");
                Assert(!Pocket(g, w, h, Rat, 10, 10), "0 -> 1 -> 2 -> 3 -> 4: not even a rat is trapped");
            });

            Case("Pocket_sheer_D3_traps_person_not_muffalo", () =>
            {
                int w = 9, h = 9;
                byte[] g = Map(w, h);
                Rect(g, w, 3, 3, 3, 3, 3);
                Assert(Pocket(g, w, h, Person, 4, 4), "a sheer 3x3 D 3 pit holds a person");
                Assert(!Pocket(g, w, h, Muffalo, 4, 4), "a muffalo climbs 3");
                var l = RM_PocketGridMath.Label(g, w, h, Person);
                Assert(l.size[l.label[4 * w + 4]] == 9, "the pocket is the 9 pit cells");
                Assert(!l.IsPocketCell(0, 0), "the surface is not a pocket");
            });

            Case("Pocket_sheer_D2_traps_rat_not_person", () =>
            {
                int w = 7, h = 7;
                byte[] g = Map(w, h);
                Rect(g, w, 3, 3, 1, 1, 2);
                Assert(Pocket(g, w, h, Rat, 3, 3), "a rat is held by a sheer D 2 cell");
                Assert(!Pocket(g, w, h, Person, 3, 3), "a person climbs out");
            });

            Case("Pocket_ramp_D4_to_D1_frees_everyone", () =>
            {
                // a sheer 3x3 D 4 pit; a D 1 cell beside its east wall; a ramp on the pit's (5,4) cell facing east to (6,4)
                int w = 10, h = 9;
                byte[] g = Map(w, h);
                Rect(g, w, 3, 3, 3, 3, 4);
                g[4 * w + 6] = 1;
                int rampCell = 4 * w + 5, top = 4 * w + 6;
                Func<int, int, bool> ramp = (a, b) => a == rampCell && b == top;
                Assert(Pocket(g, w, h, Rat, 4, 4) && Pocket(g, w, h, Person, 4, 4), "precondition: sheer, everyone held");
                Assert(!Pocket(g, w, h, Rat, 4, 4, ramp) && !Pocket(g, w, h, Person, 4, 4, ramp), "the ramp frees rat and person");
                // ...and it is still a wall everywhere else: the step over the north lip stays refused
                Assert(!RM_PitTrapMath.StepAllowed(4, 0, Person), "a ramped pit still refuses a wall step");
            });

            Case("Pocket_wall_and_width_rules", () =>
            {
                int w = 12, h = 8;
                byte[] g = Map(w, h);
                Rect(g, w, 2, 2, 3, 3, 4);  // 3x3 room
                Rect(g, w, 5, 3, 4, 1, 4);  // a 1-wide arm east
                var l = RM_PocketGridMath.Label(g, w, h, Person);
                int lab = l.label[3 * w + 3];
                Assert(l.IsPocketCell(3, 3) && l.label[3 * w + 7] == lab, "room and arm are one pocket");
                Assert(RM_PocketGridMath.WideEverywhere(l, lab, 1), "W 1 holds anywhere");
                Assert(!RM_PocketGridMath.WideEverywhere(l, lab, 2), "a 2-wide creature braces out up the 1-wide arm");
                Rect(g, w, 5, 3, 4, 1, 0);
                l = RM_PocketGridMath.Label(g, w, h, Person);
                Assert(RM_PocketGridMath.WideEverywhere(l, l.label[3 * w + 3], 2), "the 3x3 alone holds a 2-wide creature");
                Assert(!RM_PocketGridMath.WideEverywhere(l, l.label[3 * w + 3], 4), "but not a 4-wide one");
                Assert(RM_PocketGridMath.Trapped(true, false, true), "pocket, no ladder, wide: trapped");
                Assert(!RM_PocketGridMath.Trapped(true, true, true), "a usable ladder anywhere in the pocket is a way out");
                Assert(!RM_PocketGridMath.Trapped(true, false, false), "too narrow somewhere: a way out");
                Assert(!RM_PocketGridMath.Trapped(false, false, true), "not a pocket: free");
            });

            Case("Pocket_trench_splits_the_surface_and_no_cap", () =>
            {
                // a map-spanning sheer D 3 trench: both banks are surface (not pockets) but different components (GPT #1)
                int w = 30, h = 10;
                byte[] g = Map(w, h);
                Rect(g, w, 14, 0, 1, h, 3);
                var l = RM_PocketGridMath.Label(g, w, h, Person);
                Assert(!l.IsPocketCell(0, 0) && !l.IsPocketCell(29, 0), "both banks are surface");
                Assert(!l.SameComponent(0, 29), "but cut apart for a person");
                Assert(RM_PocketGridMath.Label(g, w, h, Muffalo).SameComponent(0, 29), "a muffalo crosses");
                // the retired TryGetTrapRegion stopped at 4000 cells and called the rest "escapable" (GPT #13)
                int big = 120;
                byte[] lake = Map(big, big);
                Rect(lake, big, 10, 10, 100, 100, 4);
                var ll = RM_PocketGridMath.Label(lake, big, big, Person);
                Assert(ll.IsPocketCell(60, 60) && ll.size[ll.label[60 * big + 60]] == 10000, "a 10000-cell sheer lake is one pocket");
            });

            Case("Pocket_band_and_held_gates", () =>
            {
                Assert(RM_PocketGridMath.BandFor(4, 4) == 0 && RM_PocketGridMath.BandFor(6, 4) == 0, "K at or past the band count: no grid");
                // PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: the shipped band count is sized by who climbs (6), so every real K has a grid
                Assert(RM_PocketGridMath.BandFor(4, RM_PitTrapMath.ClimbBands) == 4 && RM_PocketGridMath.BandFor(6, RM_PitTrapMath.ClimbBands) == 6,
                    "a huge K 4 and a climbing leaper K 6 each have a grid");
                Assert(RM_PocketGridMath.BandFor(2, 4) == 2 && RM_PocketGridMath.BandFor(0, 4) == 1, "bands 1..3");
                Assert(RM_PitTrapMath.HeldRelative(true, true, true, false, false, true), "all gates: held");
                Assert(!RM_PitTrapMath.HeldRelative(true, false, true, false, false, true), "no pocket: free");
                Assert(!RM_PitTrapMath.HeldRelative(true, true, false, false, false, true), "not captured: free");
                Assert(!RM_PitTrapMath.HeldRelative(true, true, true, true, false, true), "flyer: free");
                Assert(!RM_PitTrapMath.HeldRelative(true, true, true, false, true, true), "ladder cell: free");
                Assert(!RM_PitTrapMath.HeldRelative(false, true, true, false, false, true), "rule off: free");
            });

            Case("Pocket_D4_pit_traps_a_standard_pawn", () =>
            {
                // V2_PIT_ROWS_DIAGNOSE_NOBODY_STAYS_IN (live 0afba7de51: D4 pits of every width held nobody). The design holds: a
                // sheer D 4 pit deeper than a creature's climb band traps it. PRODUCTION math, the P1 width matrix shapes.
                int k = RM_PitTrapMath.ClimbLimit(1f);
                Assert(k == Person, "a standard pawn (body size 1) climbs 2 levels: " + k);
                int w = 20, h = 12;
                byte[] g = Map(w, h);
                Rect(g, w, 2, 2, 1, 1, 4);   // 1x1
                Rect(g, w, 6, 2, 4, 1, 4);   // 1-wide trench
                Rect(g, w, 12, 2, 2, 2, 4);  // 2x2
                foreach (int kk in new[] { Rat, Person, Muffalo })
                {
                    var l = RM_PocketGridMath.Label(g, w, h, kk);
                    foreach (int[] c in new[] { new[] { 2, 2 }, new[] { 7, 2 }, new[] { 12, 3 } })
                        Assert(l.IsPocketCell(c[0], c[1]), "D4 at " + c[0] + "," + c[1] + " is a pocket for band " + kk);
                }
                var lp = RM_PocketGridMath.Label(g, w, h, Person);
                int one = lp.label[2 * w + 2], sq = lp.label[2 * w + 12];
                Assert(RM_PitTrapMath.HeldRelative(true, lp.IsPocketCell(2, 2), true, false, false, true), "held where it stands");
                Assert(RM_PocketGridMath.Trapped(true, false, RM_PocketGridMath.WideEverywhere(lp, one, RM_PitTrapMath.RequiredWidth(1f, 1f))),
                    "no ladder: a person in a 1x1 D4 pit is trapped");
                Assert(RM_PocketGridMath.Trapped(true, false, RM_PocketGridMath.WideEverywhere(lp, sq, RM_PitTrapMath.RequiredWidth(4f, 1f))),
                    "a body-size-4 creature is held by the 2x2");
                Assert(!RM_PocketGridMath.Trapped(true, false, RM_PocketGridMath.WideEverywhere(lp, one, RM_PitTrapMath.RequiredWidth(4f, 1f))),
                    "can-fail: and walks out of the 1x1 (too big for it)");
                Assert(RM_PocketGridMath.BandFor(RM_PitTrapMath.ClimbLimit(1f), 4) != 0, "a person's band has a grid (K < MaxDepth)");
                // the live miss: the harness digs with the game PAUSED and the grid rebuilt only from the tick (60-tick throttle),
                // so every verdict read the ground from before the dig. Paused, the frame update rebuilds it.
                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(grid, @"public static void UpdatePaused\(Map map, RM_MapComponent_Excavation eng\) \{ if \(Find\.TickManager != null && Find\.TickManager\.Paused\) \{ RebuildIfStale\(map, eng, true\); \} \}",
                    "paused: rebuild a stale grid at once");
                RiverSwitchFlipChecks.Has(grid, @"if \(!paused && now - builtTick < RebuildMinTicks\) \{ return; \}", "the throttle applies only while time runs");
                RiverSwitchFlipChecks.Has(grid, @"if \(builtGeneration == eng\.ClimbGeneration && builtSalt == settingsSalt\) \{ return; \}", "and only a stale grid is rebuilt");
                RiverSwitchFlipChecks.Has(Src("RM_MapComponent_Excavation.cs"),
                    @"public override void MapComponentUpdate\(\) \{ base\.MapComponentUpdate\(\); // [^\n]*?RM_PocketGrid\.UpdatePaused\(map, this\); \}", "the excavation component calls it every frame");
            });

            Case("Pocket_wiring_pinned_at_call_sites", () =>
            {
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("RM_PocketGrid.ForPawn(") && trap.Contains("RM_PitTrapMath.HeldRelative("),
                    "the hold reads the pocket grid when the relative rule is on");
                Assert(trap.Contains("RM_PitTrapMath.ArrivalDropsTooFar("), "the descent detector falls by drop over K");
                Assert(trap.Contains("RM_RelativeRulesMath.FallScaleNotches("), "fall damage scales by the drop (metres fallen, P7 V3)");
                Assert(trap.Contains("RM_PitTrapMath.StepAllowed(") && trap.Contains("RM_PitTrapMath.DiagonalAllowed("),
                    "the per-move floor uses the relative step rule");
                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                Assert(grid.Contains("RM_PocketGridMath.Label("), "the runtime grid is the selftested labeller");
                Assert(grid.Contains("RebuildMinTicks = 60"), "rebuilt at most once per 60 ticks");
                string eng = Src("RM_MapComponent_Excavation.cs");
                Assert(eng.Split(new[] { "BumpClimbGeneration()" }, StringSplitOptions.None).Length >= 4,
                    "the generation moves on Deepen and FillIn (and is declared)");
                string rooms = Src("Superdeep", "RM_PitRooms.cs");
                Assert(rooms.Contains("RM_PocketGrid.IsPersonPocketCell("), "a pit room is a person-band pocket");
            });
        }
    }
}
