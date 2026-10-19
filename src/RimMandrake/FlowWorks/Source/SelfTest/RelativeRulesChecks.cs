// PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE (plan P7 of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG). Owner R7 (2026-10-17, by card):
// "The four rules keyed to 2 m deep (drowning, fall damage, spikes, shooting) → relative to the height difference", plus
// pit rooms by person-band pocket without the 2 m clause. Forms: the plan's veto-able defaults V2-V6. Arithmetic is the
// PRODUCTION Verse-free code (RM_RelativeRulesMath, RM_PocketGridMath, RM_PitTrapMath); the Verse-bound wiring is read from
// production source. Scenes: the 4/7/7/4 square, an 8 m drop, a ledge 3 m inside a 7 m core, water over a ledge.
using System;
using System.Diagnostics;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class RelativeRulesChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A w×h depth grid (notches); out of bounds answers -1 (TallestWallOver skips it) or 0 (shot rule).</summary>
        private sealed class Grid
        {
            public readonly int w, h;
            public readonly byte[] d;

            public Grid(int w, int h)
            {
                this.w = w;
                this.h = h;
                d = new byte[w * h];
            }

            public void Fill(int x0, int z0, int x1, int z1, int depth)
            {
                for (int z = z0; z <= z1; z++)
                    for (int x = x0; x <= x1; x++)
                        d[z * w + x] = (byte)depth;
            }

            public int At(int x, int z) => x < 0 || z < 0 || x >= w || z >= h ? -1 : d[z * w + x];

            public int Shot(int x, int z) => x < 0 || z < 0 || x >= w || z >= h ? 0 : d[z * w + x];

            public bool Blocked(int sx, int sz, int tx, int tz, int cliff = 4) => RM_RelativeRulesMath.ShotBlocked(Shot, sx, sz, tx, tz, cliff);
        }

        /// <summary>The 4/7/7/4 square at (x0, z0): ring 12 squares at 4 m (8 notches), core 2×2 at 7 m (14).</summary>
        private static void Square4774(Grid g, int x0, int z0)
        {
            g.Fill(x0, z0, x0 + 3, z0 + 3, 8);
            g.Fill(x0 + 1, z0 + 1, x0 + 2, z0 + 2, 14);
        }

        public static void Run(Action<string, Action> Case)
        {
            const int Person = 2;

            Case("PitRoom_depth_three_metres_scaled_by_body_height", () =>
            {
                // PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER (owner card 2026-10-18): 3.0 m for a person, scaled by height
                Assert(RM_PitRoomMath.DefaultRoomDepthMetres == 3.0f && RM_PitRoomMath.ReferenceHeightMetres == RM_RelativeRulesMath.HeightMetres(2),
                    "the person figure is 3.0 m for the 1.75 m person band");
                Assert(Math.Abs(RM_PitRoomMath.RoomDepthMetresFor(3f, 1.75f) - 3f) < 1e-4f, "a person: 3.0 m");
                Assert(Math.Abs(RM_PitRoomMath.RoomDepthMetresFor(3f, 3.5f) - 6f) < 1e-4f, "twice the height, twice the depth");
                Assert(RM_PitRoomMath.RoomDepthMetresFor(3f, 0.5f) < 1f, "a small creature needs under a metre");
                Assert(RM_PitRoomMath.RoomDepthMetresFor(0f, 3.5f) == 0f && RM_PitRoomMath.DeepEnoughFor(0f, 0f, 3.5f), "0 = any depth");
                Assert(RM_PitRoomMath.DeepEnoughFor(3f, 3f, 1.75f) && !RM_PitRoomMath.DeepEnoughFor(2.5f, 3f, 1.75f), "a person: 3 m holds, 2.5 m does not");
                Assert(!RM_PitRoomMath.DeepEnoughFor(5f, 3f, 3.5f) && RM_PitRoomMath.DeepEnoughFor(6f, 3f, 3.5f), "a huge creature: 6 m, not 5");
                Assert(RM_PitRoomMath.RoomDepthMetresFor(3f, float.NaN) == 3f, "a NaN height reads as a person");
                int six = RM_RelativeRulesMath.Notches(RM_PitRoomMath.DefaultRoomDepthMetres, 0);
                Assert(six == 6 && !RM_RelativeRulesMath.PitRoomCell(true, 5, six) && RM_RelativeRulesMath.PitRoomCell(true, 6, six),
                    "the room cell test at the shipped 3.0 m: a 2.5 m pocket is no room, 3.0 m is");
                string rooms = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitRooms.cs"));
                Assert(rooms.Contains("RM_SuperdeepTrap.IsHeld(target) && HoldsBySize(target)"), "capture-down asks the size-scaled depth");
                Assert(rooms.Contains("RM_PitRoomMath.DeepEnoughFor(floorMetres, RimMandrakeFlowWorksSettings.pitRoomMinDepthMetres, RM_Drowning.HeightOf(p))"),
                    "HoldsBySize reads the setting and the pawn's height");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                Assert(set.Contains("Scribe_Values.Look(ref pitRoomMinDepthMetres, \"pitRoomMinDepthMetres\", 3f);"), "saved with the 3 m default");
            });
            Case("PitStuck_alert_only_for_a_held_colonist_cut_off_from_food_or_bed", () =>
            {
                // PIT_ALERT_BUILD_RED_MEANS_HELP (owner card Q12, 2026-10-18)
                Assert(RM_PitRoomMath.StuckAlert(true, true, true, true, false, true, true), "held, no food: alert");
                Assert(RM_PitRoomMath.StuckAlert(true, true, true, true, true, true, false), "held, no bed: alert");
                Assert(!RM_PitRoomMath.StuckAlert(true, true, true, true, true, true, true), "held but fed and bedded in the pit: no alert");
                Assert(!RM_PitRoomMath.StuckAlert(true, true, false, true, false, true, false), "not held: no alert");
                Assert(!RM_PitRoomMath.StuckAlert(true, false, true, true, false, true, false), "not a free colonist: no alert");
                Assert(!RM_PitRoomMath.StuckAlert(false, true, true, true, false, true, false), "setting off: no alert");
                Assert(!RM_PitRoomMath.StuckAlert(true, true, true, false, false, false, false), "no needs (a mech): nothing to be cut off from");
                string a = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitStuckAlert.cs"));
                Assert(a.Contains("class Alert_ColonistStuckInPit : Alert_Critical") && a.Contains("RM_SuperdeepTrap.IsHeld(p)")
                    && a.Contains("RM_PitRoomMath.StuckAlert("), "the alert is the standard red one and asks the kernel");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                Assert(set.Contains("public static bool pitStuckAlertEnabled = true;") && set.Contains("Scribe_Values.Look(ref pitStuckAlertEnabled, \"pitStuckAlertEnabled\", true);")
                    && set.Contains("ref pitStuckAlertEnabled,"), "setting: on by default, saved, on the screen");
            });
            Case("Fall_deep_drops_can_kill_by_metres", () =>
            {
                // FALL_DAMAGE_BUILD_DEEP_DROPS_KILL (owner V3 card 2026-10-18, PROVISIONAL 6 m / 25 m)
                Func<float, float> ch = m => RM_RelativeRulesMath.FallDeathChance(m);
                Assert(ch(2f) == 0f && ch(6f) == 0f && ch(0f) == 0f && ch(-3f) == 0f && ch(float.NaN) == 0f, "no death at or under 6 m");
                Assert(ch(8f) > 0f && ch(8f) < ch(12f) && ch(12f) < ch(20f) && ch(20f) < 1f, "rises with the metres fallen");
                Assert(ch(25f) == 1f && ch(125f) == 1f, "certain at 25 m and past");
                Assert(Math.Abs(ch(15.5f) - 0.5f) < 1e-5f, "linear: halfway at 15.5 m");
                Assert(RM_RelativeRulesMath.FallDeathChance(10f, 8f, 8f) == 1f && RM_RelativeRulesMath.FallDeathChance(8f, 8f, 8f) == 0f,
                    "certain at or under the start: a step");
                string trap = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_SuperdeepTrap.cs"));
                Assert(trap.Contains("MaybeKillByFall(p, d);") && trap.Contains("RM_RelativeRulesMath.FallDeathChance(dropNotches * RM_RelativeRulesMath.MetresPerNotch,")
                    && trap.Contains("Rand.ChanceSeeded(chance,"), "the descent rolls the seeded death chance after the blunt damage");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                foreach (string f in new[] { "public static bool fallDeathEnabled = true;", "public static float fallDeathFromMetres = 6f;", "public static float fallDeathCertainMetres = 25f;" })
                    Assert(set.Contains(f), "setting: " + f);
                Assert(RM_RelativeRulesMath.DefaultFallDeathFromMetres == 6f && RM_RelativeRulesMath.DefaultFallDeathCertainMetres == 25f, "kernel defaults = settings");
            });
            Case("Relative_spikes_on_a_sheer_drop_at_any_depth", () =>
            {
                var g = new Grid(20, 12);
                g.Fill(1, 1, 1, 1, 4);                       // a 1-wide 2 m pit
                for (int i = 0; i < 4; i++) g.Fill(4 + i, 1, 4 + i, 1, i + 1);   // a gentle 0.5 m staircase down to 2 m
                g.Fill(10, 1, 10, 1, 3);                     // a sheer 1.5 m pocket
                Square4774(g, 12, 4);                        // ledge 4 m, core 7 m
                Assert(RM_RelativeRulesMath.SheerDropAt(g.At, 1, 1, 4), "the floor of a 2 m pit takes spikes");
                Assert(RM_RelativeRulesMath.TallestWallOver(g.At, 7, 1) == 4, "a 1-wide staircase's 2 m end square: the surface beside it is a 2 m wall, so it qualifies by THAT wall");
                Assert(!RM_RelativeRulesMath.SheerDropAt(g.At, 10, 1, 4), "a sheer 1.5 m pocket is short of the 2 m drop");
                Assert(RM_RelativeRulesMath.SheerDropAt(g.At, 10, 1, 3), "and takes spikes when the setting says 1.5 m");
                Assert(RM_RelativeRulesMath.TallestWallOver(g.At, 13, 5) == 6 && RM_RelativeRulesMath.SheerDropAt(g.At, 13, 5, 4),
                    "the 7 m core under its 4 m ledge: a 3 m wall, spikes allowed (the old rule needed only D >= 4)");
                Assert(RM_RelativeRulesMath.TallestWallOver(g.At, 12, 4) == 8, "a ledge square under the surface: a 4 m wall");
                Assert(RM_RelativeRulesMath.TallestWallOver(g.At, 0, 0) == 0, "undug ground has no wall over it");
                // a gentle staircase square whose higher neighbours are all within a step: no spikes at any depth
                var s = new Grid(9, 3);
                for (int x = 0; x < 9; x++) s.Fill(x, 0, x, 2, x * 1);
                Assert(!RM_RelativeRulesMath.SheerDropAt(s.At, 8, 1, 4) && RM_RelativeRulesMath.TallestWallOver(s.At, 8, 1) == 1,
                    "the bottom of a 4 m staircase (0.5 m steps all the way) takes no spikes: no sheer drop");
            });

            Case("Relative_falls_by_metres_fallen_8m_and_capped", () =>
            {
                Assert(Math.Abs(RM_RelativeRulesMath.FallScale(0.5f) - 0.25f) < 1e-6 && RM_RelativeRulesMath.FallScale(2f) == 1f,
                    "today's fall up to 2 m (linear, 2 m = the full fall)");
                Assert(Math.Abs(RM_RelativeRulesMath.FallScale(3f) - 1.5f) < 1e-6 && Math.Abs(RM_RelativeRulesMath.FallScale(7f) - 3.5f) < 1e-6,
                    "+50% of the 2 m fall a metre past 2 m");
                Assert(RM_RelativeRulesMath.FallScaleNotches(16) == 4f, "an 8 m drop is 4 times the 2 m fall");
                Assert(RM_RelativeRulesMath.FallScaleNotches(40) == 4f && RM_RelativeRulesMath.FallScale(125f) == 4f, "capped at 4x: a 20 m fall is an 8 m fall");
                Assert(RM_RelativeRulesMath.FallScale(0f) == 0f && RM_RelativeRulesMath.FallScale(-1f) == 0f && RM_RelativeRulesMath.FallScale(float.NaN) == 0f,
                    "no drop, no damage");
                Assert(RM_RelativeRulesMath.FallScale(8f, 0f, 4f) == 1f && RM_RelativeRulesMath.FallScale(8f, 1f, 10f) == 7f
                    && RM_RelativeRulesMath.FallScale(8f, 0.5f, 0.2f) == 1f, "settings: 0 a metre = flat past 2 m; the cap never below the 2 m fall");
                // the 4/7/7/4 square: the ledge from the surface is a 4 m fall, the core from its ledge a 3 m fall, the core
                // from the surface (a push across the ledge in one go) a 7 m fall
                Assert(RM_RelativeRulesMath.FallScaleNotches(8) == 2f && RM_RelativeRulesMath.FallScaleNotches(6) == 1.5f
                    && RM_RelativeRulesMath.FallScaleNotches(14) == 3.5f, "4/7 square falls by the drop, not the depth");
                // can-fail: the dig cap never enters (dividing by an 8 m cap made a 2 m fall a quarter fall)
                Assert(RM_RelativeRulesMath.FallScaleNotches(4) == 1f, "a 2 m fall stays the full fall at every dig cap");
            });

            Case("Relative_drowning_head_under_not_hole_depth", () =>
            {
                float person = RM_RelativeRulesMath.HeightMetres(Person);
                Assert(person == 1.75f && RM_RelativeRulesMath.HeightMetres(1) == 0.5f && RM_RelativeRulesMath.HeightMetres(4) == 3.5f
                    && RM_RelativeRulesMath.HeightMetres(9) == 3.5f && RM_RelativeRulesMath.HeightMetres(0) == 0.5f, "heights by size band");
                Assert(Math.Abs(RM_RelativeRulesMath.HeadUnderMetres(person, false) - 1.575f) < 1e-5 && Math.Abs(RM_RelativeRulesMath.HeadUnderMetres(person, true) - 0.35f) < 1e-5,
                    "a person's head goes under over 1.575 m standing, 0.35 m lying");
                Assert(!RM_RelativeRulesMath.HeadUnder(0.0005f, person, false), "one litre in a 7 m pit cannot drown its occupant");
                Assert(!RM_RelativeRulesMath.HeadUnder(1.5f, person, false), "a brimming 1.5 m pocket is at a person's chest");
                Assert(RM_RelativeRulesMath.HeadUnder(1.5f, person, true), "but drowns one lying in it");
                Assert(RM_RelativeRulesMath.HeadUnder(2f, person, false), "2 m of water is over a person's head");
                Assert(RM_RelativeRulesMath.HeadUnder(0.5f, RM_RelativeRulesMath.HeightMetres(1), false), "for a rat 0.5 m is over its head");
                Assert(!RM_RelativeRulesMath.HeadUnder(2f, RM_RelativeRulesMath.HeightMetres(4), false), "a thrumbo stands in 2 m");
                Assert(!RM_RelativeRulesMath.HeadUnder(1.7f, person, false, 1.0f) && RM_RelativeRulesMath.HeadUnder(1.7f, person, false, 0.9f),
                    "the head-fraction setting moves the line");
                // water over a ledge: the 4/7/7/4 square holding 56,000 L settles ring 1 m / core 4 m (P5's measured case)
                Assert(!RM_RelativeRulesMath.HeadUnder(1f, person, false), "on the ledge in 1 m: wading, not drowning");
                Assert(RM_RelativeRulesMath.HeadUnder(4f, person, false), "in the core under 4 m: head under");
                bool coreExit = RM_RelativeRulesMath.ExitInReach(14, 8, Person, false, 1f, person);
                Assert(!coreExit, "from the 7 m core the 4 m ledge is a 3 m wall: no exit for a person (drowns)");
                Assert(RM_RelativeRulesMath.ExitInReach(14, 8, Person, true, 1f, person), "a lowered ladder to the ledge is a way out");
                Assert(RM_RelativeRulesMath.ExitInReach(8, 9, Person, false, 0.5f, person), "a step it can climb into shallow water is an exit");
                Assert(!RM_RelativeRulesMath.ExitInReach(8, 9, Person, false, 2f, person), "a step into water over its head is no exit");
                float rate = RM_RelativeRulesMath.DrowningPerCheck(true, false, false, false, coreExit, 1f);
                Assert(rate > 0f, "the core pawn drowns");
                Assert(RM_RelativeRulesMath.DrowningPerCheck(true, false, false, false, coreExit, 2f) == 2f * rate, "the speed setting multiplies");
                // brim-full (152,000 L): 4 m over the ledge too; out over the lip is a 4 m wall; a swimmer keeps its head up
                Assert(RM_RelativeRulesMath.HeadUnder(4f, person, false) && !RM_RelativeRulesMath.ExitInReach(8, 0, Person, false, 0f, person),
                    "brim-full, the ledge pawn is under with no climbable exit");
                Assert(RM_RelativeRulesMath.DrowningPerCheck(true, false, true, false, false, 1f) == 0f, "the P12 hook (keeps its head up) stops it");
                // can-fail: the old rule (fill / depth at D >= 4) drowned in a 4.5 cm sheet and never in a 1.5 m pocket
                Assert(!RM_RelativeRulesMath.HeadUnder(0.045f, person, true), "a 4.5 cm sheet drowns nobody, even lying down");
            });

            Case("Relative_shooting_across_a_cliff_edge_only", () =>
            {
                // (a) the P5 finding: two pawns on one wide 2 m pit floor, 3 apart, fight normally
                var g = new Grid(30, 30);
                g.Fill(5, 5, 11, 11, 4);
                Assert(!g.Blocked(6, 8, 9, 8) && !g.Blocked(6, 6, 10, 10), "two pawns on one wide pit floor can shoot each other");
                // (b) ruling 23: from the pit only those at the edge above; into the pit only from the edge
                Assert(!g.Blocked(8, 8, 12, 8), "the pit centre shoots a pawn standing right at the edge above");
                Assert(g.Blocked(8, 8, 14, 8) && g.Blocked(14, 8, 8, 8), "but not one standing back from it, either way");
                Assert(!g.Blocked(11, 8, 12, 8), "adjacent always");
                // (c) on the surface, across a pit: no cliff stands between them (the pit is lower)
                Assert(!g.Blocked(3, 8, 14, 8), "surface to surface across a pit");
                // (d) a 1-wide pit: only its 8 neighbours, as before
                var n = new Grid(20, 20);
                n.Fill(10, 10, 10, 10, 4);
                Assert(!n.Blocked(10, 10, 11, 11) && n.Blocked(10, 10, 12, 10) && n.Blocked(10, 10, 15, 13), "a 1-wide pit: neighbours only");
                // (e) a ledge 3 m inside a 7 m core (an 8×8 square: ledge 2 wide at 4 m, core 4×4 at 7 m)
                var l = new Grid(20, 20);
                l.Fill(4, 4, 11, 11, 8);
                l.Fill(6, 6, 9, 9, 14);
                Assert(!l.Blocked(7, 7, 9, 9), "two in the core");
                Assert(!l.Blocked(7, 7, 5, 7), "the core shoots a pawn at the edge of the ledge above");
                Assert(l.Blocked(7, 7, 4, 7), "but not one at the back of the ledge (3 m wall between)");
                Assert(!l.Blocked(7, 7, 4, 7, 7), "unless the cliff setting is over 3 m");
                Assert(!l.Blocked(5, 5, 10, 10), "ledge to ledge across the core");
                Assert(l.Blocked(7, 7, 2, 7), "the core never shoots the surface (4 m and 7 m walls)");
                Assert(l.Blocked(5, 7, 2, 7) && !l.Blocked(4, 7, 3, 7), "the ledge shoots the surface only at its edge");
                // (f) the 4/7/7/4 square: ring 1 wide, so every ledge square touches the core: the core shoots the whole ledge
                var q = new Grid(10, 10);
                Square4774(q, 3, 3);
                Assert(!q.Blocked(4, 4, 6, 6) && !q.Blocked(4, 4, 3, 6) && !q.Blocked(4, 4, 6, 3), "4/7/7/4: the core and its ledge");
                Assert(q.Blocked(4, 4, 7, 4) && q.Blocked(4, 4, 8, 4) && !q.Blocked(4, 4, 6, 4), "the core shoots the ledge, never the surface past it");
                // (g) shallow digs never block: a 1 m canal, a 1.5 m pocket
                var c = new Grid(20, 5);
                c.Fill(2, 2, 17, 2, 3);
                Assert(!c.Blocked(5, 2, 15, 2) && !c.Blocked(5, 2, 10, 0), "a 1.5 m cut never blocks a shot");
            });

            Case("Relative_shooting_line_walk_cost_measured", () =>
            {
                // A busy 250×250 map: 60 pits of 7×7 at 2-7 m and every pair of 400 pawns asked once (79,800 asks), as
                // CastPositionFinder and AttackTargetFinder would. The cost is MEASURED, not asserted tight: printed for the
                // build log; the assert only catches a blow-up (> 5 µs an ask on this machine class).
                var g = new Grid(250, 250);
                var rnd = new Random(17);
                for (int i = 0; i < 60; i++)
                {
                    int x = rnd.Next(5, 238), z = rnd.Next(5, 238);
                    g.Fill(x, z, x + 6, z + 6, rnd.Next(4, 15));
                }
                var px = new int[400];
                var pz = new int[400];
                for (int i = 0; i < 400; i++)
                {
                    px[i] = rnd.Next(0, 250);
                    pz[i] = rnd.Next(0, 250);
                }
                int asks = 0, blocked = 0;
                var sw = Stopwatch.StartNew();
                for (int i = 0; i < 400; i++)
                    for (int j = i + 1; j < 400; j++)
                    {
                        asks++;
                        if (g.Blocked(px[i], pz[i], px[j], pz[j])) blocked++;
                    }
                sw.Stop();
                double us = sw.Elapsed.TotalMilliseconds * 1000.0 / asks;
                Console.WriteLine("      shot rule: " + asks + " asks, " + blocked + " blocked, " + us.ToString("0.000") + " us/ask");
                Assert(us < 5.0, "the line walk costs " + us + " us an ask");
            });

            Case("Relative_pit_rooms_person_pocket_any_depth", () =>
            {
                // a sheer 1.5 m pocket (D 3) is a person-band pocket (a pit room only with the setting at 0); a 1 m pocket is not
                var g = new Grid(12, 7);
                g.Fill(2, 2, 4, 4, 3);
                g.Fill(7, 2, 9, 4, 2);
                var lab = RM_PocketGridMath.Label(g.d, g.w, g.h, Person);
                Assert(lab.IsPocketCell(3, 3) && !lab.IsPocketCell(8, 3), "1.5 m sheer pocket holds a person; 1 m does not");
                Assert(RM_RelativeRulesMath.PitRoomCell(lab.IsPocketCell(3, 3), 3, 0), "setting 0: the 1.5 m pocket is a pit room");
                Assert(!RM_RelativeRulesMath.PitRoomCell(lab.IsPocketCell(3, 3), 3, 4), "with a 2 m setting it is not (3 m shipped)");
                Assert(RM_RelativeRulesMath.PitRoomCell(true, 14, 4) && !RM_RelativeRulesMath.PitRoomCell(false, 14, 0)
                    && !RM_RelativeRulesMath.PitRoomCell(true, 0, 0), "a deep pocket always; a walkable bowl never; undug never");
                Assert(RM_RelativeRulesMath.Notches(0f, 0) == 0 && RM_RelativeRulesMath.Notches(2f, 0) == 4 && RM_RelativeRulesMath.Notches(1.5f) == 3
                    && RM_RelativeRulesMath.Notches(0.2f) == 1, "settings in metres read back as notches");
            });

            Case("Relative_free_fall_step_is_the_drop", () =>
            {
                Assert(RM_PitTrapMath.DryStepBaseCost(0, 4, 300) == 0 && RM_PitTrapMath.DryStepBaseCost(8, 14, 300) == 0, "a 2 m or 3 m sheer drop is a fall");
                Assert(RM_PitTrapMath.DryStepBaseCost(4, 5, 300) == 300 && RM_PitTrapMath.DryStepBaseCost(3, 4, 300) == 300,
                    "a half-metre step down past 2 m is a climb (the absolute rule priced it as a free fall)");
                Assert(RM_PitTrapMath.DryStepBaseCost(14, 8, 300) == 300, "up is a climb");
            });

            Case("Relative_rules_wired_at_call_sites", () =>
            {
                string sp = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_Spikes.cs"));
                RiverSwitchFlipChecks.Has(sp, @"int wall = TallestWallOver\(engine, c\); return wall >= need \? null", "spikes: a sheer drop of the setting's metres (V4)");
                Assert(!sp.Contains("depth >= 4"), "spikes no longer read an absolute depth");
                string sh = RiverSwitchFlipChecks.Src("RM_Patch_SuperdeepShooting.cs");
                RiverSwitchFlipChecks.Has(sh, @"return !RM_RelativeRulesMath\.ShotBlocked\(", "shooting: across a cliff edge (V5)");
                Assert(!sh.Contains("IsSuperdeepExcavation") && !sh.Contains("dx <= 1 && dz <= 1"), "no 8-way adjacency key");
                RiverSwitchFlipChecks.Has(sh, @"int d = engine\.ClimbDepthAt\(c\);", "never DepthAt (lakes would block every shot)");
                string fe = RiverSwitchFlipChecks.Src("RM_PitFillEffects.cs");
                RiverSwitchFlipChecks.Has(fe, @"public static System\.Func<Pawn, IntVec3, float, bool> keepsHeadUp", "the P12 swim hook");
                RiverSwitchFlipChecks.Has(fe, @"return RM_RelativeRulesMath\.DrowningPerCheck\(true, lying, headUp, false, exit,", "drowning: one relative rule (V2)");
                Assert(!fe.Contains("IsSuperdeepExcavation"), "drowning never asks 'dug 2 m'");
                string trap = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_SuperdeepTrap.cs"));
                RiverSwitchFlipChecks.Has(trap, @"RM_RelativeRulesMath\.FallScaleNotches\(dropNotches, RimMandrakeFlowWorksSettings\.fallDamagePerMetrePast2, RimMandrakeFlowWorksSettings\.fallDamageCap\)",
                    "falls: by metres fallen under the settings (V3)");
                RiverSwitchFlipChecks.Has(trap, @"if \(RM_PocketGrid\.Relative\) \{ int fromD = RM_TrenchStride\.StepDepthFor\(p, p\.Map, eng, from\);", "the jump gizmo: a drop over the climb limit");
                string rooms = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitRooms.cs"));
                RiverSwitchFlipChecks.Has(rooms, @"return RM_RelativeRulesMath\.PitRoomCell\(RM_PocketGrid\.IsPersonPocketCell\(map, c\), eng\.ExcavatedDepthRaw\(c\), MinRoomNotches\);",
                    "rooms: a person-band pocket at the setting's depth (V6)");
                Assert(!rooms.Contains("IsSuperdeepExcavation(cell)") && !rooms.Contains("IsSuperdeepExcavation(lip)")
                    && !rooms.Contains("IsSuperdeepExcavation(pawn.Position)") && !rooms.Contains("IsSuperdeepExcavation(clickedPawn.Position)"),
                    "lip service and capture-down read the room test (IsPitFloor), never D 4");
                string ex = RiverSwitchFlipChecks.Src("RM_PitExposure.cs");
                Assert(!ex.Contains("IsSuperdeepExcavation") && ex.Contains("RM_PitRooms.IsPitFloor(map, eng, c)"), "exposure and pit-room temperature: the room test");
                string fire = RiverSwitchFlipChecks.Src("RM_LiquidFire.cs");
                Assert(!fire.Contains("IsSuperdeepExcavation") && fire.Contains("bool heldInPit = RM_PitRooms.IsPitFloor(map, ex, c);")
                    && fire.Contains("!RM_PitRooms.IsPitFloor(map, ex, p.Position)"), "liquid fire's trapped occupant and the knock-back exemption: the room test");
                string cover = RiverSwitchFlipChecks.Src(Path.Combine("Pits", "Building_PitCover.cs"));
                RiverSwitchFlipChecks.Has(cover, @"RM_SpikeUtility\.TallestWallOver\(engine, loc\) < RM_PitTrapMath\.Superdeep", "a cover goes over a 2 m sheer drop");
                string step = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitStepCost.cs"));
                Assert(!step.Contains("IsSuperdeepRaw(c)") && step.Contains("RM_ExcavationDepth.DryTerrainFor((byte)System.Math.Min(255, depth))"),
                    "a wet dug square costs its own dry hole, not 'a 2 m pit or nothing'");
                string lab = RiverSwitchFlipChecks.Src("RM_ExcavationDepth.cs");
                Assert(!lab.Contains("\"pit \" + m"), "no 'pit' label from 2 m");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                // review day 3: "on the screen" reads the drawn window only (the Scribe key string matched it before)
                int s0 = set.IndexOf("public void DoWindowContents(", StringComparison.Ordinal);
                int s1 = s0 < 0 ? -1 : set.IndexOf("private static void ApplyChangedSettings()", s0, StringComparison.Ordinal);
                Assert(s0 >= 0 && s1 > s0, "found the settings window");
                string screen = set.Substring(s0, s1 - s0);
                foreach (string f in new[] { "public static float shootingCliffMetres = 2f;", "public static float pitRoomMinDepthMetres = 3f;",
                    "public static float fallDamagePerMetrePast2 = 0.5f;", "public static float fallDamageCap = 4f;",
                    "public static float pitDrowningHeadFraction = 0.9f;", "public static float pitDrowningLyingFraction = 0.2f;",
                    "public static float spikeMinDropMetres = 2f;" })
                {
                    Assert(set.Contains(f), "setting: " + f);
                    string name = f.Split(' ')[3];
                    Assert(set.Contains("Scribe_Values.Look(ref " + name + ", \"" + name + "\""), "scribed: " + name);
                    Assert(System.Text.RegularExpressions.Regex.IsMatch(screen, name + @" = [^;]*list\.Slider\(" + name + ","), "on the screen: " + name);
                }
                Assert(RM_RelativeRulesMath.DefaultFallPerMetrePast == 0.5f && RM_RelativeRulesMath.DefaultFallCap == 4f
                    && RM_RelativeRulesMath.DefaultHeadFraction == 0.9f && RM_RelativeRulesMath.DefaultLyingFraction == 0.2f,
                    "the settings' literals are the math's defaults");
                Assert(RM_RelativeRulesMath.DrowningCheckTicks == RM_FillEffectMath.IntervalTicks, "the drowning rate is per the fill-effects pass");
            });

            Case("Relative_head_fraction_live_with_drowning_off", () =>
            {
                // review day 3: swimming reads the standing head fraction (who is swimming, where footing is) with drowning off,
                // so it is not greyed under the drowning switch; the lying fraction and the rate are drowning's alone.
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                string swim = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                Assert(swim.Contains("RimMandrakeFlowWorksSettings.pitDrowningHeadFraction"), "swimming reads the head fraction");
                RiverSwitchFlipChecks.Has(set, @"\.Declare\(""pitDrowningEnabled"", ""pitDrowningRateMultiplier"", ""pitDrowningLyingFraction""\)", "drowning greys rate and lying fraction only");
                RiverSwitchFlipChecks.Has(set, @"\.Independent\([^)]*""pitDrowningHeadFraction""\)", "the head fraction is declared independent");
                Assert(!set.Contains("Dependent(list, \"pitDrowningRateMultiplier\", \"pitDrowningHeadFraction\""), "its slider is outside the greyed scope");
            });
        }
    }
}
