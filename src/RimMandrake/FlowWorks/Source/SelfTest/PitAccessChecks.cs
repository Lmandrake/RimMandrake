// PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS (owner 2026-10-18: "Two ladders ... Also a personally carriable ladder placed into the
// pit (if not too deep) ... Climbing gear a pawn has that allows them to scale ... jump packs and other leaping abilities allow
// entrance/exit immediately, and teleportation"; rescue by card: "any colonist who can climb back out goes; if nobody can, a
// ladder job is queued first"). Offline: the pure verdicts (RM_PitAccessMath), the band contract climbing gear leans on
// (BandFor = 0 means "climbs every step"), and the production call sites and defs. Each case has a can-fail.
// NOT proven here: a colonist carrying the portable ladder and setting it in a live pit, a gear-wearer climbing a 4 m wall in
// game at the slow cost, a jump-pack landing without the fall hediff, a skip into a pit, the rescue blueprint being built and
// the downed colonist carried out. Live rows owed.
using System;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitAccessChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("PitAccess_portable_ladder_reach", () =>
            {
                Assert(RM_PitAccessMath.LadderReaches(8, 0, 0), "the fixed ladder (0) spans any depth: 4 m");
                Assert(RM_PitAccessMath.LadderReaches(6, 0, 6), "a portable 3 m ladder spans a 3 m wall");
                Assert(!RM_PitAccessMath.LadderReaches(7, 0, 6), "can-fail: not a 3.5 m wall (if not too deep)");
                Assert(RM_PitAccessMath.LadderReaches(10, 4, 6), "relative: a 3 m step between two dug floors");
                Assert(!RM_PitAccessMath.LadderReaches(4, 4, 0), "can-fail: no drop, no wall, reaches nothing");
                Assert(!RM_PitAccessMath.LadderReaches(3, 5, 6), "can-fail: the wall is deeper, not a way up");
            });
            Case("PitAccess_climbing_gear_climbs_every_step", () =>
            {
                int k = RM_PitAccessMath.ClimbLimitWithGear(2, true, true);
                Assert(k == RM_PitAccessMath.ScalesAnyWall, "gear worn and on: the any-wall limit");
                Assert(RM_PocketGridMath.BandFor(k, RM_PitTrapMath.ClimbBands) == 0,
                    "the any-wall limit has no band: every trap/mask/reach read treats it as 'climbs every step there is'");
                Assert(RM_PitTrapMath.ClimbLimit(100f, 10, 2f) < RM_PitAccessMath.ScalesAnyWall,
                    "can-fail: no creature reaches it unaided (ClimbLimit is capped at MaxClimbLimit)");
                Assert(RM_PitAccessMath.ClimbLimitWithGear(2, true, false) == 2, "can-fail: setting off, the gear does nothing");
                Assert(RM_PitAccessMath.ClimbLimitWithGear(2, false, true) == 2, "can-fail: not worn");
                Assert(RM_PitTrapMath.ArrivalDropsTooFar(0, 16, 2), "can-fail: a forced 8 m arrival still falls a person (gear is no parachute)");
                string t = Src("Superdeep", "RM_SuperdeepTrap.cs");
                RiverSwitchFlipChecks.Has(t, @"ArrivalDropsTooFar\(from, to, RM_PocketGrid\.NaturalClimbLimitOf\(p\)\)", "forced arrivals judged without the gear");
                RiverSwitchFlipChecks.Has(t, @"LadderLetsOut\(map, pos, p\) \|\| \(walked && RM_PocketGrid\.ClimbsOnGear\(p\)\)", "a walked step down on the gear is a climb, not a fall");
            });
            Case("PitAccess_gear_is_slow_only_past_the_natural_limit", () =>
            {
                Assert(RM_PitAccessMath.StepOnGear(0, 6, 2, true), "a 3 m step for a person goes on the gear");
                Assert(!RM_PitAccessMath.StepOnGear(0, 2, 2, true), "can-fail: a 1 m step it climbs anyway is not");
                Assert(!RM_PitAccessMath.StepOnGear(0, 6, 2, false), "can-fail: no gear, no gear step");
                int perLevel = 30 * 3;
                int onGear = RM_PitTrapMath.StepCost(0, 6, 2, 30, false, true, perLevel);
                Assert(onGear == 6 * 90, "priced per level at the gear's slowness (6 levels x 90)");
                Assert(onGear > RM_PitTrapMath.StepCost(0, 2, 2, 30, false, false, 0, 2f), "slower than a normal slow climb");
            });
            Case("PitAccess_jumps_and_skips_land_safely", () =>
            {
                Assert(RM_PitAccessMath.LandsSafely(true, true, false, false), "a jump-pack landing does not fall");
                Assert(!RM_PitAccessMath.LandsSafely(false, true, false, true), "can-fail: a throw (stun flyer) still falls");
                Assert(!RM_PitAccessMath.LandsSafely(true, false, false, false), "can-fail: jump setting off, a jump falls");
                Assert(RM_PitAccessMath.LandsSafely(false, false, true, true), "a skip lands safely");
                Assert(!RM_PitAccessMath.LandsSafely(false, false, true, false), "can-fail: teleport setting off");
            });
            Case("PitAccess_rescue_queues_a_ladder_only_when_nobody_can_go", () =>
            {
                Assert(RM_PitAccessMath.ChooseRescueLadder(true, true, false, 4, 6, true, true) == RM_PitAccessMath.RescueLadder.None,
                    "can-fail: someone who can climb back out goes; no ladder");
                Assert(RM_PitAccessMath.ChooseRescueLadder(true, false, true, 4, 6, true, true) == RM_PitAccessMath.RescueLadder.None,
                    "can-fail: a ladder already pending in that pit");
                Assert(RM_PitAccessMath.ChooseRescueLadder(false, false, false, 4, 6, true, true) == RM_PitAccessMath.RescueLadder.None,
                    "can-fail: nobody needs help");
                Assert(RM_PitAccessMath.ChooseRescueLadder(true, false, false, 4, 6, true, true) == RM_PitAccessMath.RescueLadder.InstallPortable,
                    "nobody can: carry the spare portable ladder there");
                Assert(RM_PitAccessMath.ChooseRescueLadder(true, false, false, 4, 6, false, true) == RM_PitAccessMath.RescueLadder.BuildPortable,
                    "no spare: build a portable one");
                Assert(RM_PitAccessMath.ChooseRescueLadder(true, false, false, 8, 6, true, true) == RM_PitAccessMath.RescueLadder.BuildFixed,
                    "too deep for a portable: the fixed wall ladder");
                Assert(RM_PitAccessMath.ChooseRescueLadder(true, false, false, 4, 6, true, false) == RM_PitAccessMath.RescueLadder.BuildFixed,
                    "portable ladders off: the fixed ladder");
            });
            Case("PitAccess_call_sites_wired", () =>
            {
                string u = Src("Superdeep", "RM_LadderUtility.cs");
                RiverSwitchFlipChecks.Has(u, @"RimMandrakeFlowWorks_DefOf\.RM_LadderPortable", "IsLadderDef names the portable ladder");
                RiverSwitchFlipChecks.Has(u, @"if \(ladder == null \|\| !RM_LadderUtility\.Reaches\(ladder\)\)", "LadderLetsOut gates on reach");
                RiverSwitchFlipChecks.Has(u, @"Props\.portable \|\| !RimMandrakeFlowWorksSettings\.ladderRaiseLowerEnabled", "no up/down button on a portable ladder");
                RiverSwitchFlipChecks.Has(u, @"RMFlow_LadderPortableTooDeep", "placement refuses a wall too deep");
                RiverSwitchFlipChecks.Has(u, @"if \(!RM_LadderUtility\.IsLadderDef\(sourceDef\)\)", "the blueprint turn covers both ladders");
                Assert(!u.Contains("def == ladderDef"), "can-fail: no single-def ladder read left in RM_LadderUtility");
                string m = Src("Superdeep", "RM_CliffMask.cs");
                RiverSwitchFlipChecks.Has(m, @"LoweredLadderAt\(Map map, IntVec3 c\) \{ // [^}]*RM_LadderUtility\.Reaches\(ladder\)", "the masks' structural join gates on reach");
                string g = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(g, @"RM_LadderUtility\.AllLadders\(map, ladderScratch\)", "the pocket grid scans both ladder defs");
                RiverSwitchFlipChecks.Has(g, @"RM_PitAccessMath\.ClimbLimitWithGear\(NaturalClimbLimitOf\(p\), WearsClimbingGear\(p\)", "ClimbLimitOf reads the gear");
                string pp = Src("Superdeep", "RM_PitPathing.cs");
                RiverSwitchFlipChecks.Has(pp, @"RM_LadderUtility\.AllLadders\(map, ladderScratch\)", "the prison-door offset closes both ladder defs");
                RiverSwitchFlipChecks.Has(pp, @"LandsSafely\(deliberate, RimMandrakeFlowWorksSettings\.pitJumpLandsSafe", "the flyer landing honours a deliberate jump");
                RiverSwitchFlipChecks.Has(pp, @"NoteHandledArrival\(p, p\.Position\); return; \} if \(RM_PocketGrid\.Relative\)", "the safe jump returns before the fall branch");
                string sc = Src("Superdeep", "RM_PitStepCost.cs");
                RiverSwitchFlipChecks.Has(sc, @"RM_PocketGrid\.ClimbsOnGear\(p\)", "a gear step is priced slowly");
                string a = Src("Superdeep", "RM_PitAccess.cs");
                RiverSwitchFlipChecks.Has(a, @"HarmonyPatch\(typeof\(CompAbilityEffect_Teleport\), nameof\(CompAbilityEffect_Teleport\.Apply\)\)", "the skip patch");
                RiverSwitchFlipChecks.Has(a, @"class RM_MapComponent_PitRescueLadder : MapComponent", "the rescue ladder job");
                RiverSwitchFlipChecks.Has(a, @"RM_PitAccessMath\.ChooseRescueLadder\(", "the rescue reads the selftested verdict");
            });
            Case("PitAccess_defs_and_settings_shipped", () =>
            {
                string d = Src("..", "Defs", "Canals", "ThingDefs", "FlowWorks_PitAccess.xml");
                Assert(d.Contains("<defName>RM_LadderPortable</defName>") && d.Contains("<portable>true</portable>"), "the portable ladder def");
                Assert(d.Contains("<minifiedDef>MinifiedThing</minifiedDef>"), "it is carried (minifiable)");
                Assert(d.Contains("Canals/RM_LadderPortable</texPath>") && d.Contains("Canals/RM_LadderPortableFlat</texPath>"),
                    "the owner's diagonal art, and the flat one when it does not reach");
                Assert(d.Contains("<defName>RM_ClimbingGear</defName>") && d.Contains("<scalesAnyWall>true</scalesAnyWall>"), "the climbing gear");
                // The three textures are not checked here: the selftest runs on a staged copy without Textures/.
                string s = Src("RimMandrakeFlowWorksMod.cs");
                foreach (string f in new[] { "portableLadderEnabled", "portableLadderMaxLevels", "climbingGearEnabled", "climbingGearSlowness",
                                             "pitJumpLandsSafe", "pitTeleportLandsSafe", "pitRescueLadderEnabled" })
                {
                    Assert(s.Contains("Scribe_Values.Look(ref " + f + ","), "scribed: " + f);
                    Assert(s.Contains("\"" + f + "\""), "in the settings section list: " + f);
                }
                string k = Src("..", "Languages", "English", "Keyed", "FlowWorks_Keys.xml");
                foreach (string key in new[] { "RMFlow_LadderPortableReach", "RMFlow_LadderPortableOff", "RMFlow_LadderPortableShort",
                                               "RMFlow_LadderPortableTooDeep", "RMFlow_ClimbsAnyWall", "RMFlow_RescueLadderQueued" })
                {
                    Assert(k.Contains("<" + key + ">"), "key: " + key);
                }
            });
        }
    }
}
