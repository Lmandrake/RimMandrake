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
                RiverSwitchFlipChecks.Has(t, @"bool climbsDown = walked && \(RM_PocketGrid\.ClimbsOnGear\(p\) \|\|", "a walked step down on the gear is a climb, not a fall");
                RiverSwitchFlipChecks.Has(t, @"LadderLetsOut\(map, pos, p\) \|\| climbsDown,", "the fall verdict reads the climb");
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
                RiverSwitchFlipChecks.Has(u, @"d == RimMandrakeFlowWorks_DefOf\.RM_LadderSteel", "IsLadderDef names the steel wall ladder");
                RiverSwitchFlipChecks.Has(u, @"ThingsOfDef\(RimMandrakeFlowWorks_DefOf\.RM_LadderSteel\)", "AllLadders scans the steel wall ladder");
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
                // RESCUE_LADDER_DIAGNOSE_NOBODY_FETCHES_IT: a drafted (or Doctor-disabled) colonist who reaches the pit never
                // goes, so it must not stop the ladder job (live pass 2c: a drafted climbing-gear wearer did).
                RiverSwitchFlipChecks.Has(a, @"!c\.InMentalState && !c\.Drafted && !c\.WorkTypeIsDisabled\(WorkTypeDefOf\.Doctor\)", "only a rescuer who would go cancels the ladder");
            });
            // FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT (bar jump_into_pit_lands_unhurt; he typed 2026-10-20: "plus flying creatures
            // can simply fly in/out, jumping creatures jump in or out, floating creatures float in/out")
            Case("PitTravel_fly_jump_float_cross_freely_and_never_fall", () =>
            {
                Assert(RM_PitAccessMath.CrossesPitsFreely(true, false, false, false), "a flyer crosses freely, setting or not");
                Assert(RM_PitAccessMath.CrossesPitsFreely(false, true, true, false), "a jumper crosses freely");
                Assert(RM_PitAccessMath.CrossesPitsFreely(false, true, false, true), "a floater crosses freely");
                Assert(!RM_PitAccessMath.CrossesPitsFreely(false, true, false, false), "can-fail: a walker does not");
                Assert(!RM_PitAccessMath.CrossesPitsFreely(false, false, true, true), "setting off: jumpers and floaters are walkers");
                Assert(!RM_PitAccessMath.FallHurts(true, true, true), "a free traveller is never hurt arriving");
                Assert(RM_PitAccessMath.FallHurts(true, false, true), "can-fail: a walker pushed in still falls");
                Assert(RM_PitAccessMath.FallHurts(true, true, false), "setting off: the old rule (only the airborne are spared)");
                Assert(!RM_PitAccessMath.FallHurts(false, false, true), "fall damage off: nobody");
            });
            Case("PitTravel_every_trap_mask_reach_and_fall_read_asks_it", () =>
            {
                string g = Src("Superdeep", "RM_PocketGrid.cs");
                RiverSwitchFlipChecks.Has(g, @"return RM_PitAccessMath\.CrossesPitsFreely\(CanFly\(p\), RimMandrakeFlowWorksSettings\.pitFreeTravelEnabled,", "the pawn read is the selftested rule");
                RiverSwitchFlipChecks.Has(g, @"public class RM_PitTravelExtension : DefModExtension\s*\{\s*public bool jumps;\s*public bool floats;", "the race marker");
                foreach (string f in new[] { "RM_SuperdeepTrap.cs", "RM_CliffMask.cs", "RM_TrenchStride.cs", "RM_RaiderTrench.cs", "RM_FallRails.cs" })
                {
                    string t = Src("Superdeep", f);
                    Assert(t.Contains("RM_PocketGrid.FreePitTraveller("), "reads the free-traveller rule: " + f);
                    Assert(!t.Contains("RM_PocketGrid.CanFly("), "can-fail: no pit read asks CanFly alone: " + f);
                }
                string tr = Src("Superdeep", "RM_SuperdeepTrap.cs");
                RiverSwitchFlipChecks.Has(tr, @"if \(RM_PitAccessMath\.FallHurts\(RimMandrakeFlowWorksSettings\.fallDamageEnabled, RM_PocketGrid\.FreePitTraveller\(p\),",
                    "the one fall-damage site spares them");
                Assert(System.Text.RegularExpressions.Regex.Matches(tr, @"!p\.Flying && !\(RimMandrakeFlowWorksSettings\.pitFreeTravelEnabled && RM_PocketGrid\.FreePitTraveller\(p\)\)").Count
                    + System.Text.RegularExpressions.Regex.Matches(tr, @"!p\.Flying\s*&& !\(RimMandrakeFlowWorksSettings\.pitFreeTravelEnabled && RM_PocketGrid\.FreePitTraveller\(p\)\)").Count >= 2,
                    "both arrival detectors (the tick pass and ResolveArrivalNow) skip them");
                string pp = Src("Superdeep", "RM_PitPathing.cs");
                RiverSwitchFlipChecks.Has(pp, @"if \(RimMandrakeFlowWorksSettings\.pitFreeTravelEnabled && RM_PocketGrid\.FreePitTraveller\(p\)\)\s*\{\s*eng\.SuperdeepTrap\.NoteHandledArrival\(p, p\.Position\);",
                    "a flyer set down in a pit is not a fall");
                string s = Src("RimMandrakeFlowWorksMod.cs");
                Assert(s.Contains("Scribe_Values.Look(ref pitFreeTravelEnabled,") && s.Contains("\"pitFreeTravelEnabled\""), "the setting is saved and listed");
            });
            // PIT_RAMP_FIX_WALKER_TAKES_FALL (GPT review FC_pits_superdeep_2.1): a captured walker stepping down a working ramp past
            // its natural climb limit was judged a fall (only ladders and gear were exempt)
            Case("PitRamp_walked_step_down_a_ramp_is_no_fall", () =>
            {
                string tr = Src("Superdeep", "RM_SuperdeepTrap.cs");
                RiverSwitchFlipChecks.Has(tr, @"bool climbsDown = walked && \(RM_PocketGrid\.ClimbsOnGear\(p\) \|\| RM_PitRamp\.Joins\(map, prev, pos, RM_SuperdeepTrap\.StepDepthAt\(map, eng, prev\), RM_SuperdeepTrap\.StepDepthAt\(map, eng, pos\)\)\);",
                    "can-fail: a walked step a ramp joins is climbing down, like a ladder or gear");
                RiverSwitchFlipChecks.Has(tr, @"DescentFalls\(walked, RM_LadderRules\.LadderLetsOut\(map, pos, p\) \|\| climbsDown,", "the fall verdict reads it");
                Assert(!RM_PitTrapMath.DescentFalls(true, true, false, true), "a captured raider climbing down (ladder, gear, ramp) does not fall");
                Assert(RM_PitTrapMath.DescentFalls(false, true, false, true), "shoved off the ramp's top is still forced, still a fall");
            });
            // PIT_RESCUE_FIX_COUNTS_DOCTOR_OFF (GPT review FC_pits_superdeep_2.2): a colonist with Doctor unticked in the work tab
            // (capable, never sent) counted as a rescuer and held the rescue ladder back for good
            Case("PitRescue_only_a_colonist_assigned_Doctor_counts_as_a_rescuer", () =>
            {
                string a = Src("Superdeep", "RM_PitAccess.cs");
                RiverSwitchFlipChecks.Has(a, @"!c\.WorkTypeIsDisabled\(WorkTypeDefOf\.Doctor\)\s*&& c\.workSettings != null && c\.workSettings\.WorkIsActive\(WorkTypeDefOf\.Doctor\)",
                    "can-fail: the work-tab assignment is read, not only the capability");
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
            // GODMODE_LADDER_FIX_ASKS_FOR_WOOD (owner 2026-10-24): in god mode the rescue ladder is built at once and free, as
            // vanilla's god-mode Designator_Build does, never a blueprint waiting on wood; installing a spare is skipped too.
            Case("PitAccess_god_mode_rescue_ladder_is_instant_and_free", () =>
            {
                string a = Src("Superdeep", "RM_PitAccess.cs");
                int pb = a.IndexOf("private bool PlaceBuild(", StringComparison.Ordinal);
                Assert(pb > 0, "PlaceBuild found");
                string body = a.Substring(pb, a.IndexOf("PlaceBlueprintForBuild", pb, StringComparison.Ordinal) - pb);
                Assert(body.Contains("if (DebugSettings.godMode)") && body.Contains("GenSpawn.Spawn(built, cell, map, rot"),
                    "god mode spawns the finished ladder before any blueprint is placed");
                Assert(a.Contains("case RM_PitAccessMath.RescueLadder.InstallPortable when !DebugSettings.godMode:"),
                    "god mode never queues an install job either");
            });
        }
    }
}
