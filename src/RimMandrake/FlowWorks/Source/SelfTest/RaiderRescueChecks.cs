// RAIDERS_FETCH_THEIR_FALLEN (owner's story: raiders fall into a covered spike pit; the others hack saplings into a ladder to
// fetch them while the defenders shoot; the raid is driven off, leaving some injured prisoners already in a tidy prison).
// Offline: the pure verdicts (RM_RaiderTrenchMath.FetchFallen, RescueDrop, ClaimLive, ClimbOutDone, HoldColonyDamageExit),
// the duty patches that put JobGiver_RM_FetchFallen before the first fight node of AssaultColony, Breaching and Sapper, the
// call sites that keep the crossing and the ladder-taking out of the fetcher's way, the rescue's own JobDef, the held
// colony-damage exit and the one keyed message for a ladder into a hole that holds colony prisoners. Each case has a can-fail.
// NOT proven here: a live raid where one raider fells a sapling, carries it, lowers it into the pit while the others shoot,
// and a fallen raider climbing it out; the single message per raid; the raid staying for the rescue and leaving after the
// cap; the fetcher giving up when the raid flees. Live rows owed.
using System;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class RaiderRescueChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static int Count(string s, string needle)
        {
            int n = 0;
            for (int i = s.IndexOf(needle, StringComparison.Ordinal); i >= 0; i = s.IndexOf(needle, i + needle.Length, StringComparison.Ordinal))
            {
                n++;
            }
            return n;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("RaidersFetch_step_order", () =>
            {
                // (master, assault, siege, freedFallen, rescuerFit, anyTrapped, claimedByOther, slot, supplyJob, canBuild)
                Assert(RM_RaiderTrenchMath.FetchFallen(true, true, false, false, true, true, false, true, false, true)
                    == RM_RaiderTrenchMath.FetchStep.SetLadder, "a fit raider, a trapped friend, a slot and a ladder in hand: set it");
                Assert(RM_RaiderTrenchMath.FetchFallen(true, true, false, false, true, true, false, true, true, true)
                    == RM_RaiderTrenchMath.FetchStep.Supply, "no ladder yet: the supply job comes first");
                Assert(RM_RaiderTrenchMath.FetchFallen(true, true, false, true, false, false, true, false, false, false)
                    == RM_RaiderTrenchMath.FetchStep.ClimbOut, "a fallen raider whose pocket has a ladder now climbs out, whatever else");
                Assert(RM_RaiderTrenchMath.FetchFallen(true, true, false, false, true, true, true, true, false, true)
                    == RM_RaiderTrenchMath.FetchStep.None, "can-fail: another raider already holds the claim");
                Assert(RM_RaiderTrenchMath.FetchFallen(true, false, false, true, true, true, false, true, false, true)
                    == RM_RaiderTrenchMath.FetchStep.None, "can-fail: no longer an assault (the raid flees): nothing, not even the climb");
                Assert(RM_RaiderTrenchMath.FetchFallen(true, true, true, false, true, true, false, true, false, true)
                    == RM_RaiderTrenchMath.FetchStep.None, "can-fail: a siege does not fetch");
                Assert(RM_RaiderTrenchMath.FetchFallen(false, true, false, true, true, true, false, true, false, true)
                    == RM_RaiderTrenchMath.FetchStep.None, "can-fail: the master switch off");
                Assert(RM_RaiderTrenchMath.FetchFallen(true, true, false, false, true, true, false, false, false, true)
                    == RM_RaiderTrenchMath.FetchStep.None, "can-fail: no slot on the rim");
                Assert(RM_RaiderTrenchMath.FetchFallen(true, true, false, false, true, true, false, true, false, false)
                    == RM_RaiderTrenchMath.FetchStep.None, "can-fail: no ladder to be had");
            });
            Case("RaidersFetch_rescue_drop_and_claim_lease", () =>
            {
                Assert(RM_RaiderTrenchMath.RescueDrop(6, 0, 6, false, true, true) == 6, "a 3 m drop inside the portable reach");
                Assert(RM_RaiderTrenchMath.RescueDrop(9, 0, 0, false, true, true) == 9, "reach 0: any depth");
                Assert(RM_RaiderTrenchMath.RescueDrop(7, 0, 6, false, true, true) == -1, "can-fail: past the portable reach");
                Assert(RM_RaiderTrenchMath.RescueDrop(4, 4, 6, false, true, true) == -1, "can-fail: no drop is no slot");
                Assert(RM_RaiderTrenchMath.RescueDrop(6, 0, 6, true, true, true) == -1, "can-fail: a ladder or ramp already there");
                Assert(RM_RaiderTrenchMath.RescueDrop(6, 0, 6, false, false, true) == -1, "can-fail: reserved by someone else");
                Assert(RM_RaiderTrenchMath.RescueDrop(6, 0, 6, false, true, false) == -1, "can-fail: out of the fetcher's touch");
                int lease = RM_RaiderTrenchMath.RescueLeaseTicks;
                Assert(lease == 2500, "the lease is a game hour");
                Assert(RM_RaiderTrenchMath.ClaimLive(true, 1000, 1000 + lease - 1, lease, true, true), "a renewed claim stands");
                Assert(!RM_RaiderTrenchMath.ClaimLive(true, 1000, 1000 + lease, lease, true, true), "can-fail: the lease ran out");
                Assert(!RM_RaiderTrenchMath.ClaimLive(true, 1000, 1001, lease, false, true), "can-fail: the holder is down or trapped");
                Assert(!RM_RaiderTrenchMath.ClaimLive(true, 1000, 1001, lease, true, false), "can-fail: nobody left down there");
                Assert(!RM_RaiderTrenchMath.ClaimLive(false, 1000, 1001, lease, true, true), "can-fail: no claim");
            });
            Case("RaidersFetch_duty_inserts_and_call_sites", () =>
            {
                string x = Src("..", "Patches", "RaiderTrench", "FlowWorks_RaiderTrenchDuties.xml");
                Assert(Count(x, "<li Class=\"RimMandrake.FlowWorks.JobGiver_RM_FetchFallen\" />") == 3, "can-fail: three duty inserts");
                RiverSwitchFlipChecks.Has(x, @"DutyDef\[defName=""AssaultColony""\]/thinkNode/subNodes/li\[@Class=""JobGiver_AIFightEnemies""\]</xpath> <order>Prepend</order> <value> <li Class=""RimMandrake\.FlowWorks\.JobGiver_RM_FetchFallen"" />",
                    "AssaultColony: before the fight");
                RiverSwitchFlipChecks.Has(x, @"DutyDef\[defName=""Breaching""\]/thinkNode/subNodes/li\[@Class=""ThinkNode_HarmedRecently""\]</xpath> <order>Prepend</order> <value> <li Class=""RimMandrake\.FlowWorks\.JobGiver_RM_FetchFallen"" />",
                    "Breaching: before the fight");
                RiverSwitchFlipChecks.Has(x, @"DutyDef\[defName=""Sapper""\]/thinkNode/subNodes/li\[@Class=""JobGiver_AIFightEnemies""\]</xpath> <order>Prepend</order> <value> <li Class=""RimMandrake\.FlowWorks\.JobGiver_RM_FetchFallen"" />",
                    "Sapper: before the fight");
                string proj = Src("RimMandrake_FlowWorks.csproj");
                Assert(proj.Contains(@"<Compile Include=""Superdeep\RM_RaiderRescue.cs"" />"), "can-fail: the file is compiled");
                string rr = Src("Superdeep", "RM_RaiderRescue.cs");
                RiverSwitchFlipChecks.Has(rr, @"class JobGiver_RM_FetchFallen : ThinkNode_JobGiver", "the job giver the duties name");
                RiverSwitchFlipChecks.Has(rr, @"RM_RaiderTrenchMath\.FetchFallen\(", "the giver asks the pure verdict");
                string tr = Src("Superdeep", "RM_RaiderTrench.cs");
                RiverSwitchFlipChecks.Has(tr, @"RM_RaiderRescue\.ClearMemos\(\);", "the claims die with the save");
                RiverSwitchFlipChecks.Has(tr, @"if \(RM_RaiderRescue\.Busy\(p\)\) \{ return null; \}", "the crossing leaves the fetcher alone");
                RiverSwitchFlipChecks.Has(tr, @"FailOn\(\(\) => RM_RaiderRescue\.GivenUp\(pawn, job\)\)", "the set-ladder job fails when the fetch is given up");
                string lp = Src("Superdeep", "RM_LadderParity.cs");
                RiverSwitchFlipChecks.Has(lp, @"if \(RM_RaiderRescue\.IsRescueLadder\(l\)\) \{ continue;", "no raider takes the rescue ladder away");
                string k = Src("..", "Languages", "English", "Keyed", "FlowWorks_Keys.xml");
                Assert(k.Contains("<RMFlow_RaidersFetchFallen>") && rr.Contains("\"RMFlow_RaidersFetchFallen\".Translate("), "the one message is keyed");
            });
            Case("RaidersFetch_climb_out_and_the_held_exit", () =>
            {
                // the climb-out ends on the wall top or once he has left the pocket he was fetched from
                Assert(!RM_RaiderTrenchMath.ClimbOutDone(true, false, true), "can-fail: still in the pocket, off the wall: climbing");
                Assert(RM_RaiderTrenchMath.ClimbOutDone(true, true, true), "on the wall top: out");
                Assert(RM_RaiderTrenchMath.ClimbOutDone(true, false, false), "in another pocket: left the one he was fetched from");
                Assert(RM_RaiderTrenchMath.ClimbOutDone(false, false, false), "on the open ground: out");
                // the colony-damage exit waits for the rescue, at most the cap after the first hold
                int cap = RM_RaiderTrenchMath.RescueHoldCapTicks;
                Assert(cap == 5000, "can-fail: the cap is about 5000 ticks");
                Assert(!RM_RaiderTrenchMath.HoldColonyDamageExit(false, -1, 100, cap), "can-fail: no rescue, the exit fires");
                Assert(RM_RaiderTrenchMath.HoldColonyDamageExit(true, -1, 100, cap), "a rescue under way, first hold: held");
                Assert(RM_RaiderTrenchMath.HoldColonyDamageExit(true, 100, 100 + cap - 1, cap), "inside the cap: held");
                Assert(!RM_RaiderTrenchMath.HoldColonyDamageExit(true, 100, 100 + cap, cap), "can-fail: at the cap the exit fires");
                Assert(!RM_RaiderTrenchMath.HoldColonyDamageExit(true, 100, 100 + 3 * cap, cap), "can-fail: past the cap the exit fires");
                Assert(RM_RaiderTrenchMath.HoldColonyDamageExit(true, 9000, 100, cap), "a first hold in the future is stale: counts as none");
                Assert(!RM_RaiderTrenchMath.HoldColonyDamageExit(true, -1, 100, 0), "can-fail: a zero cap never holds");
                string rr = Src("Superdeep", "RM_RaiderRescue.cs");
                RiverSwitchFlipChecks.Has(rr, @"\[HarmonyPatch\(typeof\(Trigger_FractionColonyDamageTaken\), nameof\(Trigger_FractionColonyDamageTaken\.ActivateOn\)\)\] \[RimMandrake\.Shared\.PatchFeature\(""[^""]+"", typeof\(RimMandrake\.FlowWorks\.RM_RaiderTrenchSettings\), ""raiderRescueHoldsRaid""\)\]",
                    "only the colony-damage exit is held, behind its setting");
                Assert(Count(rr, "[HarmonyPatch(typeof(Trigger_") == 1, "can-fail: no other exit trigger is touched");
                RiverSwitchFlipChecks.Has(rr, @"RM_RaiderTrenchMath\.HoldColonyDamageExit\(", "the hold asks the pure cap");
                RiverSwitchFlipChecks.Has(rr, @"RM_RaiderTrenchMath\.ClimbOutDone\(", "the climb-out asks the pure rule");
                string tr = Src("Superdeep", "RM_RaiderTrench.cs");
                RiverSwitchFlipChecks.Has(tr, @"public static bool raiderRescueHoldsRaid = true;", "the setting, default on");
                RiverSwitchFlipChecks.Has(tr, @"Scribe_Values\.Look\(ref raiderRescueHoldsRaid, ""raiderRescueHoldsRaid"", true\);", "the setting is saved");
                RiverSwitchFlipChecks.Has(tr, @"CheckboxLabeled\([^;]*ref raiderRescueHoldsRaid", "the setting is listed");
                RiverSwitchFlipChecks.Has(tr, @"public static JobDef RM_RaiderRescueLadder;", "the rescue's own JobDef");
                string jd = Src("..", "Defs", "Canals", "JobDefs", "FlowWorks_RaiderTrench.xml");
                Assert(jd.Contains("<defName>RM_RaiderRescueLadder</defName>"), "can-fail: the rescue JobDef exists");
                // owner ruling 2026-11-07: the ladder stays when the hole holds colony prisoners; one message per ladder
                string k = Src("..", "Languages", "English", "Keyed", "FlowWorks_Keys.xml");
                Assert(k.Contains("<RMFlow_RescueLadderIntoPrison>") && Count(rr, "\"RMFlow_RescueLadderIntoPrison\".Translate(") == 1,
                    "can-fail: the prison-hole message is keyed and sent from one place");
                string lp = Src("Superdeep", "RM_LadderParity.cs");
                RiverSwitchFlipChecks.Has(lp, @"if \(RM_RaiderRescue\.OwnRaidBelow\(p, l\)\)", "a ladder down to a standing raid-mate is left alone");
            });
        }
    }
}
