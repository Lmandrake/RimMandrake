// DRAINED_HOLE_IS_A_PRISON (owner card 2026-11-05, "Drained moat is a prison": capture from the rim works with NO bed, and the
// hole is the prison). Offline: the pure rules (RM_PitRoomMath.BedlessPrison, BedlessHeld, FoodEnoughInPocket, DropCell) and
// capture down's verdict built from them, the setting (declared, saved, listed, under capture down), the three narrow warden
// patches in RM_BedlessPitPrison.cs and their call sites, and the prison-door rule: that file never builds, sets or lowers a
// ladder, and the warden givers that would walk a prisoner out (take to bed, feed, release, execute) are left to vanilla.
// Each case has a can-fail.
// NOT proven here: a warden capturing a raider in a bare drained moat from the rim, food landing on a rim square of his
// pocket and being eaten, recruitment talk from the edge, the prisoner never escaping or showing an alert in a live game.
// Live rows owed.
using System;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class BedlessPitPrisonChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool InSectionList(string src, string name) =>
            Regex.IsMatch(src, @"Section\(list, ""[^""]*"", new\[\] \{[^}]*""" + Regex.Escape(name) + @"""");

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        /// <summary>The file's code with every // and /// comment taken out (the header names ladders to explain the rule).</summary>
        private static string Code(params string[] rel)
        {
            string raw = File.ReadAllText(RiverSwitchFlipChecks.SrcPath(Path.Combine(rel)));
            return Regex.Replace(Regex.Replace(raw, @"//[^\n]*", ""), @"\s+", " ");
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("BedlessPrison_capture_needs_no_bed_when_the_hole_traps", () =>
            {
                Assert(RM_PitRoomMath.BedlessPrison(false, true, true), "a trapping hole with the switch on is a prison, no bed");
                Assert(RM_PitRoomMath.BedlessPrison(true, false, false), "the bed prison stands as before");
                Assert(!RM_PitRoomMath.BedlessPrison(false, false, true), "can-fail: switch off, a bare hole is no prison");
                Assert(!RM_PitRoomMath.BedlessPrison(false, true, false), "can-fail: a hole he can climb out of is no prison");
                Assert(RM_PitRoomMath.BedlessHeld(false, true, true), "a trapping hole holds him whatever its depth");
                Assert(!RM_PitRoomMath.BedlessHeld(false, false, true), "can-fail: switch off, the room-depth size rule stands");
                Assert(!RM_PitRoomMath.BedlessHeld(false, true, false), "can-fail: not trapped, not held");
                bool on = true, trapped = true;
                Assert(RM_PitRoomMath.CaptureDown(true, true, false, false, RM_PitRoomMath.BedlessHeld(false, on, trapped),
                    RM_PitRoomMath.BedlessPrison(false, on, trapped)) == RM_PitRoomMath.CaptureDownVerdict.Allowed,
                    "capture down: a trapped raider in a bare hole is Allowed");
                Assert(RM_PitRoomMath.CaptureDown(true, true, false, false, RM_PitRoomMath.BedlessHeld(true, false, trapped),
                    RM_PitRoomMath.BedlessPrison(false, false, trapped)) == RM_PitRoomMath.CaptureDownVerdict.NoPrisonBed,
                    "can-fail: switch off, a held raider in a bare hole still wants the bed");
                Assert(RM_PitRoomMath.CaptureDown(true, true, true, false, RM_PitRoomMath.BedlessHeld(false, on, trapped),
                    RM_PitRoomMath.BedlessPrison(false, on, trapped)) == RM_PitRoomMath.CaptureDownVerdict.OwnSide,
                    "can-fail: one of ours in the hole is never taken prisoner");
            });
            Case("BedlessPrison_food_in_the_pocket_and_drop_cell", () =>
            {
                Assert(RM_PitRoomMath.FoodEnoughInPocket(true, 0f, 5f), "carrying something he will eat: enough");
                Assert(RM_PitRoomMath.FoodEnoughInPocket(false, 0.6f, 1.0f), "vanilla's 0.5 slack");
                Assert(!RM_PitRoomMath.FoodEnoughInPocket(false, 0.4f, 1.0f), "can-fail: too little down there, food is owed");
                Assert(!RM_PitRoomMath.FoodEnoughInPocket(false, 0f, 0.6f), "can-fail: nothing down there, one hungry prisoner");
                Assert(RM_PitRoomMath.DropCell(true, true, true, true), "a rim cell of his pocket, his room, free");
                Assert(!RM_PitRoomMath.DropCell(false, true, true, true), "can-fail: outside his pocket");
                Assert(!RM_PitRoomMath.DropCell(true, false, true, true), "can-fail: another room (food not socially proper to him)");
                Assert(!RM_PitRoomMath.DropCell(true, true, false, true), "can-fail: not standable or not empty");
                Assert(!RM_PitRoomMath.DropCell(true, true, true, false), "can-fail: the middle of the hole, no lip touches it");
            });
            Case("BedlessPrison_setting_and_call_sites", () =>
            {
                string s = Src("RimMandrakeFlowWorksMod.cs");
                Assert(s.Contains("public static bool bedlessPitPrisonEnabled = true;"), "declared, default on");
                Assert(s.Contains("Scribe_Values.Look(ref bedlessPitPrisonEnabled, \"bedlessPitPrisonEnabled\", true);"), "saved");
                Assert(InSectionList(s, "bedlessPitPrisonEnabled"), "can-fail: in the settings section list");
                Assert(s.Contains(".Declare(\"captureDownEnabled\", \"bedlessPitPrisonEnabled\")"), "under capture down");
                string proj = Src("RimMandrake_FlowWorks.csproj");
                Assert(proj.Contains(@"<Compile Include=""Superdeep\RM_BedlessPitPrison.cs"" />"), "can-fail: the file is compiled");
                string pr = Src("Superdeep", "RM_PitRooms.cs");
                RiverSwitchFlipChecks.Has(pr, @"bool trapped = bedless && humanlike && !ownSide && target\.Spawned && RM_BedlessPitPrison\.HoleHolds\(target\);",
                    "the verdict asks the hole");
                RiverSwitchFlipChecks.Has(pr, @"RM_PitRoomMath\.BedlessHeld\(.*, bedless, trapped\), RM_PitRoomMath\.BedlessPrison\(prison, bedless, trapped\)\);",
                    "the verdict's held and prison gates are the bedless rules");
                RiverSwitchFlipChecks.Has(pr, @"bedlessPitPrisonEnabled && clickedPawn\.RaceProps\.Humanlike && RM_BedlessPitPrison\.HoleHolds\(clickedPawn\)",
                    "the float menu offers a trapped person off the pit-room floor");
                RiverSwitchFlipChecks.Has(pr, @"return RM_BedlessPitPrison\.ServesJobAt\(worker, dest, cell\); \}",
                    "the lip service walks wardens to a lip-served prisoner's lip");
                string b = Src("Superdeep", "RM_BedlessPitPrison.cs");
                RiverSwitchFlipChecks.Has(b, @"return p != null && p\.Spawned && !Pits\.RM_PitCoverBeneath\.IsBeneath\(p\) && RM_SuperdeepTrap\.IsTrapped\(p\);",
                    "the hole holds: trapped, not sealed under a lid");
            });
            Case("BedlessPrison_three_narrow_patches_and_the_prison_door", () =>
            {
                string b = Code("Superdeep", "RM_BedlessPitPrison.cs");
                RiverSwitchFlipChecks.Has(b, @"\[HarmonyPatch\(typeof\(WorkGiver_Scanner\), nameof\(WorkGiver_Scanner\.AllowUnreachable\), MethodType\.Getter\)\]",
                    "patch 1: the unreachable prisoner is offered");
                RiverSwitchFlipChecks.Has(b, @"\[HarmonyPatch\(typeof\(WorkGiver_Warden\), ""ShouldTakeCareOfPrisoner""\)\]", "patch 2: reach replaced by a lip");
                RiverSwitchFlipChecks.Has(b, @"\[HarmonyPatch\(typeof\(WorkGiver_Warden_DeliverFood\), nameof\(WorkGiver_Warden_DeliverFood\.JobOnThing\)\)\]",
                    "patch 3: food lands on a rim cell");
                Assert(Regex.Matches(b, @"\[HarmonyPatch\(").Count == 3, "can-fail: exactly three patches (no IsInPrisonCell postfix)");
                Assert(!b.Contains("IsInPrisonCell\")") && !b.Contains("nameof(RoomQuery") && !b.Contains("typeof(PrisonBreakUtility)"),
                    "can-fail: no global prison-cell or escape patch");
                Assert(Regex.Matches(b, @"\[RimMandrake\.Shared\.PatchFeature\(""Wardens work from the lip"", typeof\(RimMandrake\.FlowWorks\.RimMandrakeFlowWorksSettings\), ""wardenFromLipEnabled""\)\]").Count == 3,
                    "each patch is the existing lip feature's, off with it");
                // the five givers that can work from the edge, and none that would walk a prisoner out of the hole
                foreach (string g in new[] { "WorkGiver_Warden_DeliverFood", "WorkGiver_Warden_Chat", "WorkGiver_Warden_Convert",
                                             "WorkGiver_Warden_Enslave", "WorkGiver_Warden_InterrogateIdentity" })
                {
                    Assert(b.Contains("g is " + g), "lip giver: " + g);
                }
                foreach (string g in new[] { "WorkGiver_Warden_TakeToBed", "WorkGiver_Warden_Feed", "WorkGiver_Warden_ReleasePrisoner",
                                             "WorkGiver_Warden_ExecuteGuilty", "WorkGiver_Warden_DoExecution", "WorkGiver_Warden_Release" })
                {
                    Assert(!b.Contains(g), "can-fail: left to vanilla (no reach, no job): " + g);
                }
                // THE PRISON-DOOR RULE: a lowered ladder is a held-open door (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED); a warden never brings one
                foreach (string w in new[] { "ladder", "Ladder", "PlaceBlueprint", "GenConstruct", "GenSpawn", "Blueprint", "RM_RaiderSetLadder" })
                {
                    Assert(!b.Contains(w), "can-fail: the warden code never builds or lowers anything: " + w);
                }
            });
        }
    }
}
