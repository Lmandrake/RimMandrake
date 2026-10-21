// PIT_LADDER_REDRAW_HUNG_ON_THE_WALL (owner 2026-10-16: "installed along a side of the pit, like a door to a room ... a
// 'slid up' version that's inaccessible to the prisoners below or a 'slid down' version that is clearly visible"). Offline
// checks on the production verdict (RM_LadderWallMath) over small depth grids, the state->climb rule, and the production
// call sites (placement, spawn turn, blueprint turn, the masks' joins, the pocket grid). Each case has a can-fail.
// NOT proven here: the art drawn against the right wall on screen, a blueprint turning in the real designator, a prisoner
// actually staying down under a slid-up ladder in a live pit. Live check owed.
using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LadderWallChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        // Grid legend: a digit is a square's dug depth (0 = the rim), '@' the ladder's square (depth given separately).
        // Rows run north (top) to south. Returns the resolved wall as N/E/S/W, or "-" for none.
        private static string Wall(int placed, int ladderD, params string[] rows)
        {
            int h = rows.Length, ax = -1, az = -1;
            for (int r = 0; r < h; r++)
            {
                int i = rows[r].IndexOf('@');
                if (i >= 0) { ax = i; az = h - 1 - r; }
            }
            Assert(ax >= 0, "can-fail: grid has no ladder");
            int[] sideD = new int[4];
            bool[] inB = new bool[4];
            for (int k = 0; k < 4; k++)
            {
                int x = ax + RM_LadderWallMath.FX[k], z = az + RM_LadderWallMath.FZ[k];
                int rr = h - 1 - z;
                inB[k] = rr >= 0 && rr < h && x >= 0 && x < rows[rr].Length;
                sideD[k] = inB[k] ? rows[rr][x] - '0' : ladderD;
            }
            int w = RM_LadderWallMath.Resolve(placed, ladderD, sideD, inB);
            return w < 0 ? "-" : "NESW"[w].ToString();
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LadderWall_placed_rotation_stands_on_a_wall", () =>
            {
                // the north-west corner square of a depth-4 pit: walls north and west
                Assert(Wall(0, 4, "000", "0@4", "044") == "N", "placed north on the north wall: north");
                Assert(Wall(3, 4, "000", "0@4", "044") == "W", "placed west on the west wall: west (a corner lets the player choose)");
                // can-fail: placed east faces the pit floor (no wall) and is overruled
                Assert(Wall(1, 4, "000", "0@4", "044") == "N", "placed east into the pit: turned to a wall (north first on a tie)");
            });
            Case("LadderWall_auto_turns_to_the_biggest_drop", () =>
            {
                // a square at depth 4 with a 2-deep step east and the rim south: the rim is the bigger drop
                Assert(Wall(0, 4, "444", "4@2", "404") == "S", "rim south (drop 4) beats the step east (drop 2)");
                Assert(Wall(0, 4, "444", "4@4", "424") == "S", "the only wall");
                Assert(Wall(0, 4, "444", "2@2", "444") == "E", "a tie between east and west: Rot4 order (east first)");
            });
            Case("LadderWall_no_wall_refused", () =>
            {
                Assert(Wall(0, 4, "444", "4@4", "444") == "-", "the middle of a flat floor: no wall, placement refused");
                Assert(Wall(0, 0, "000", "0@0", "000") == "-", "open ground: no wall");
                Assert(Wall(0, 2, "444", "4@4", "444") == "-", "deeper on every side: no wall (a ladder climbs UP only)");
                // the map edge is never a wall: a pit cut to the edge has no rim there
                Assert(Wall(0, 4, "@4", "44") == "-", "can-fail: off the map is not a wall");
                Assert(!RM_LadderWallMath.IsWall(4, 0, false) && RM_LadderWallMath.IsWall(4, 0, true), "IsWall needs the side on the map");
            });
            Case("LadderWall_joins_only_the_wall_it_hangs_on", () =>
            {
                // hung north (rot 0) on a depth-4 square: joins the rim north, NOT the rim west, east or south
                Assert(RM_LadderWallMath.Joins(0, 4, 0, 1, 0), "north wall joined");
                Assert(!RM_LadderWallMath.Joins(0, 4, -1, 0, 0), "can-fail: the old ladder joined ANY shallower side; west is not its wall");
                Assert(!RM_LadderWallMath.Joins(0, 4, 0, -1, 0), "south is not its wall");
                Assert(!RM_LadderWallMath.Joins(0, 4, 0, 1, 4), "its wall filled level with the floor: leads nowhere");
                Assert(RM_LadderWallMath.Joins(1, 4, 1, 0, 2) && RM_LadderWallMath.Joins(2, 4, 0, -1, 0) && RM_LadderWallMath.Joins(3, 4, -1, 0, 3),
                    "east, south and west hang the same way");
                Assert(!RM_LadderWallMath.Faces(-1, 0, 1) && !RM_LadderWallMath.Faces(4, 0, 1), "no rotation faces nothing");
            });
            Case("LadderWall_slid_up_holds_everyone_slid_down_is_the_prison_door", () =>
            {
                // (raiseLowerOn, raised, prisonDoorOn, mayClimb): the state drives the climb, not just the picture
                Assert(!RM_PitTrapMath.LadderUsable(true, true, true, true), "slid up: a colonist below cannot climb out");
                Assert(!RM_PitTrapMath.LadderUsable(true, true, true, false), "slid up: a prisoner below stays put");
                Assert(RM_PitTrapMath.LadderUsable(true, false, true, true), "slid down: your people climb");
                Assert(!RM_PitTrapMath.LadderUsable(true, false, true, false), "slid down: a prisoner (not breaking out) still stays");
                Assert(RM_PitTrapMath.LadderUsable(false, true, true, true), "can-fail: the setting off makes slid-up count as down");
            });
            // FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE (bar wall_ladder_rides_on_rails; he typed 2026-10-20: "It can be raised
            // from either below or above. But it can only be lowered from above.")
            Case("LadderRails_raise_either_side_lower_only_from_above", () =>
            {
                Assert(RM_LadderWallMath.MayOperate(true, true), "raise from above");
                Assert(RM_LadderWallMath.MayOperate(true, false), "raise from below");
                Assert(RM_LadderWallMath.MayOperate(false, true), "lower from above");
                Assert(!RM_LadderWallMath.MayOperate(false, false), "can-fail: lower from below is refused");
            });
            Case("LadderRails_gizmo_job_and_ai_ask_the_rule", () =>
            {
                string u = RiverSwitchFlipChecks.Src("Superdeep/RM_LadderUtility.cs");
                // gizmo: orders, never moves; a lower nobody could stand above for is refused
                RiverSwitchFlipChecks.Has(u, @"toggleAction = \(\) => Order\(!wantRaised\),", "the button orders the move");
                RiverSwitchFlipChecks.Has(u, @"if \(wantRaised && !RM_LadderWallMath\.MayOperate\(false, RM_LadderUtility\.TopStandable\(parent\)\)\)\s*\{\s*cmd\.Disable\(",
                    "the button refuses a lower with no standing room above");
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(u, @"toggleAction = \(\) => SetRaised"), "can-fail: the button no longer moves the ladder itself");
                // AI: the work giver offers only an allowed, reachable side; only designated ladders are scanned
                RiverSwitchFlipChecks.Has(u, @"if \(RM_LadderWallMath\.MayOperate\(toRaised, true\) && TopStandable\(ladder\)", "above is offered only when the rule allows it");
                RiverSwitchFlipChecks.Has(u, @"if \(RM_LadderWallMath\.MayOperate\(toRaised, false\) && pawn\.CanReach\(ladder\.Position, PathEndMode\.OnCell, danger\)",
                    "below is offered only when the rule allows it (a raise)");
                RiverSwitchFlipChecks.Has(u, @"if \(!RM_LadderUtility\.StandCellFor\(pawn, t, comp\.wantRaised\)\.IsValid\)", "no allowed side: no job");
                RiverSwitchFlipChecks.Has(u, @"foreach \(Designation des in pawn\.Map\.designationManager\.SpawnedDesignationsOfDef\(d\)\)", "only ordered ladders");
                // job: re-checks where the pawn actually stands before moving the ladder
                RiverSwitchFlipChecks.Has(u, @"bool above = pawn\.Position == RM_LadderUtility\.TopCell\(job\.targetA\.Thing\);\s*if \(comp == null \|\| !RM_LadderWallMath\.MayOperate\(comp\.wantRaised, above\)\)\s*\{\s*EndJobWith\(JobCondition\.Incompletable\);",
                    "the job refuses a lower from below");
                RiverSwitchFlipChecks.Has(u, @"comp\.SetRaised\(comp\.wantRaised\);", "the job is what moves it");
                RiverSwitchFlipChecks.Has(u, @"return ladder\.Position \+ ladder\.Rotation\.FacingCell;", "above = the wall's top square the ladder faces");
                RiverSwitchFlipChecks.Has(u, @"Scribe_Values\.Look\(ref wantRaised, ""rmLadderWantRaised"", raised\);", "the order is saved; an old save orders nothing");
            });
            Case("LadderWall_call_sites", () =>
            {
                string u = RiverSwitchFlipChecks.Src("Superdeep/RM_LadderUtility.cs");
                RiverSwitchFlipChecks.Has(u, @"return RM_LadderWallMath\.Resolve\(placed\.AsInt, d, sideD, inB\);", "the wall comes from the production verdict");
                RiverSwitchFlipChecks.Has(u, @"if \(!respawningAfterLoad \|\| comp == null \|\| !comp\.hung\)\s*\{\s*int wall = RM_LadderUtility\.WallRotAt\(map, Position, Rotation\);\s*if \(wall >= 0 && wall != Rotation\.AsInt\)\s*\{\s*Rotation = new Rot4\(wall\);\s*\}\s*\}\s*if \(comp != null\)\s*\{\s*comp\.hung = true;\s*\}\s*base\.SpawnSetup",
                    "the building turns to its wall BEFORE it spawns (so it prints turned); a reload keeps a settled turn");
                // PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS reshaped the return (the portable ladder's depth check follows it).
                RiverSwitchFlipChecks.Has(u, @"int wall = RM_LadderUtility\.WallRotAt\(map, loc, rot\); if \(wall < 0\) \{ return ""RMFlow_LadderNeedsWall""\.Translate\(\); \}",
                    "placement refused with no wall");
                RiverSwitchFlipChecks.Has(u, @"Scribe_Values\.Look\(ref hung, ""rmLadderHung"", false\);", "the settled turn is saved");
                RiverSwitchFlipChecks.Has(u, @"\[HarmonyPatch\(typeof\(GenConstruct\), nameof\(GenConstruct\.PlaceBlueprintForBuild\)\)\]", "the blueprint turns when placed");
                RiverSwitchFlipChecks.Has(u, @"public static bool LadderLetsOutToward\(Map map, IntVec3 deep, IntVec3 other, Pawn p\)\s*\{\s*return RM_LadderUtility\.HangsToward",
                    "the per-pawn edge read checks the wall first");
                string m = RiverSwitchFlipChecks.Src("Superdeep/RM_CliffMask.cs");
                RiverSwitchFlipChecks.Has(m, @"return LoweredLadderAt\(map, deep\) && RM_LadderUtility\.HangsToward\(RM_LadderUtility\.LadderAt\(map, deep\), shallow\);",
                    "the structural mask join is the hung wall only");
                RiverSwitchFlipChecks.Has(m, @"RM_LadderRules\.LadderLetsOutToward\(map, deep, aD > bD \? b : a, p\)", "the per-pawn mask join is the hung wall only");
                string g = RiverSwitchFlipChecks.Src("Superdeep/RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(g, @"LadderLeadsOut\(k, component, c, ladders\[i\]\.Rotation\.AsInt\)", "the pocket grid reads the ladder's wall");
                RiverSwitchFlipChecks.Has(g, @"RM_LadderWallMath\.Joins\(rot, d, dx, dz,", "the pocket grid's way out is the production join");
            });
        }
    }
}
