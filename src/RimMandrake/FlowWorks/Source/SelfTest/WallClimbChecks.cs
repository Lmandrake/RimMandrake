// WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS (owner 2026-10-18: climbing gear "should allow pawns to scale walls (unroofed on both
// sides) just as easily as canal sides, albeit slowly"; by card: built walls too, colonists AND raiders, both ways, slowly).
// Offline: the pure verdicts (RM_WallClimbMath: which walls, who may, the roof rule on both sides and the wall, the slow cost),
// and the production wiring (the seams, the settings, the defs). Each case has a can-fail.
// NOT proven here: a colonist ordered over a wall in game, a sapper/breacher/raider choosing the climb live, the landing
// past a pit edge, the settings window drawing. Live rows owed.
using System;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WallClimbChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("WallClimb_which_things_are_walls", () =>
            {
                Assert(RM_WallClimbMath.IsClimbableWallKind(true, false, false, false, true, false), "a built impassable wall");
                Assert(RM_WallClimbMath.IsClimbableWallKind(true, false, false, false, false, true), "an impassable fence");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(false, false, false, false, false, true), "can-fail: a fence people walk through is no wall");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, true, false, false, true, false), "can-fail: a door opens");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, false, true, false, true, false), "can-fail: mineable rock is a cliff");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, false, false, true, false, false), "can-fail: natural rock");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, false, false, false, false, false), "can-fail: an impassable machine is not scaled");
            });
            Case("WallClimb_gear_required_raiders_by_setting", () =>
            {
                Assert(RM_WallClimbMath.MayClimb(true, true, true, true, false), "a colonist in gear");
                Assert(RM_WallClimbMath.MayClimb(true, true, true, false, true), "a raider in gear, raiders may climb (the default)");
                Assert(!RM_WallClimbMath.MayClimb(false, true, true, true, true), "can-fail: no gear, no climb");
                Assert(!RM_WallClimbMath.MayClimb(true, false, true, true, true), "can-fail: climbing gear switched off");
                Assert(!RM_WallClimbMath.MayClimb(true, true, false, true, true), "can-fail: wall climbing switched off");
                Assert(!RM_WallClimbMath.MayClimb(true, true, true, false, false), "can-fail: raiders barred by the setting");
            });
            Case("WallClimb_unroofed_on_both_sides_and_the_wall", () =>
            {
                Assert(RM_WallClimbMath.CrossingOpen(1, false, false, false, true, true), "open sky over the wall and both sides");
                Assert(RM_WallClimbMath.CrossingOpen(2, false, false, false, true, true), "a double wall");
                Assert(!RM_WallClimbMath.CrossingOpen(1, false, true, false, true, true), "can-fail: the near side roofed");
                Assert(!RM_WallClimbMath.CrossingOpen(1, false, false, true, true, true), "can-fail: the far side roofed");
                Assert(!RM_WallClimbMath.CrossingOpen(1, true, false, false, true, true), "can-fail: the wall square roofed");
                Assert(!RM_WallClimbMath.CrossingOpen(1, false, false, false, true, false), "can-fail: nowhere to land");
                Assert(!RM_WallClimbMath.CrossingOpen(RM_WallClimbMath.MaxWallSquares + 1, false, false, false, true, true), "can-fail: too thick");
                Assert(!RM_WallClimbMath.CrossingOpen(0, false, false, false, true, true), "can-fail: no wall to climb");
            });
            Case("WallClimb_is_slow", () =>
            {
                int one = RM_WallClimbMath.ClimbTicks(1, 1f, RM_WallClimbMath.NormalMoveSpeed);
                Assert(one == RM_WallClimbMath.BaseTicksPerSquare, "a person, speed 1: the base ticks per square");
                Assert(one >= 10 * 60 / RM_WallClimbMath.NormalMoveSpeed, "slower than walking ten squares");
                Assert(RM_WallClimbMath.ClimbTicks(2, 1f, RM_WallClimbMath.NormalMoveSpeed) == 2 * one, "a double wall takes twice as long");
                Assert(RM_WallClimbMath.ClimbTicks(1, 2f, RM_WallClimbMath.NormalMoveSpeed) == one / 2, "the speed slider halves it");
                Assert(RM_WallClimbMath.ClimbTicks(1, 1f, 2.3f) == 2 * one, "a slow walker climbs slower");
                Assert(RM_WallClimbMath.ClimbTicks(1, 1f, 100f) == one / 2, "can-fail: a fast walker is capped at double");
                Assert(RM_WallClimbMath.ClimbTicks(1, 100f, 100f) >= 60, "can-fail: never under a second");
            });
            Case("WallClimb_wiring", () =>
            {
                string w = Src("Superdeep", "RM_WallClimb.cs");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.IsClimbableWallKind\(d\.passability == Traversability\.Impassable,\s*d\.IsDoor, d\.mineable, d\.building\.isNaturalRock, d\.IsWall, d\.IsFence\)", "walls read from def flags");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.CrossingOpen\(squares, anyRoof, fromRoofed, toRoofed, from\.Standable\(map\), c\.Standable\(map\)\)", "the roof rule on the wall and both sides");
                RiverSwitchFlipChecks.Has(w, @"RM_PocketGrid\.WearsClimbingGear\(p\)", "gear read from worn apparel");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(DigUtility\), nameof\(DigUtility\.PassBlockerJob\)\)\]", "sappers climb");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(JobGiver_AIBreaching\), ""TryGiveJob""\)\]", "breachers climb");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(Pawn_PathFollower\), ""TryEnterNextPathCell""\)\]", "a blocked path climbs instead of bashing");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(JobGiver_AIGotoNearestHostile\), ""TryGiveJob""\)\]", "raiders with no way in climb");
                RiverSwitchFlipChecks.Has(w, @"class FloatMenuOptionProvider_RM_ClimbOverWall : FloatMenuOptionProvider", "colonists ordered over");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.ClimbTicks\(squares, RM_WallClimbSettings\.wallClimbSpeed", "the climb lasts ClimbTicks at the speed setting");
                string s = Src("Superdeep", "RM_WallClimbSettings.cs");
                foreach (string f in new[] { "wallClimbEnabled", "wallClimbSpeed", "raidersMayClimbWalls" })
                {
                    Assert(s.Contains("ref " + f + ", \"" + f + "\""), "scribed setting " + f);
                }
                Assert(s.Contains("public static bool raidersMayClimbWalls = true;"), "raiders climb by default (owner by card)");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("RM_WallClimbSettings.ExposeData();") && mod.Contains("RM_WallClimbSettings.DoSettingsSection(list);"), "settings scribed and drawn");
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                foreach (string f in new[] { "RM_WallClimbMath.cs", "RM_WallClimbSettings.cs", "RM_WallClimb.cs" })
                {
                    Assert(csproj.Contains("Superdeep\\" + f), "compiled: " + f);
                }
                string jobs = Src("..", "Defs", "Canals", "JobDefs", "FlowWorks_WallClimb.xml");
                Assert(jobs.Contains("<defName>RM_ClimbOverWall</defName>") && jobs.Contains("JobDriver_RM_ClimbOverWall"), "the climb job def");
            });
        }
    }
}
