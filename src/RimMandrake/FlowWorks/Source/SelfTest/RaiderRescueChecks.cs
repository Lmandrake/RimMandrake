// RAIDERS_FETCH_THEIR_FALLEN (owner's story: raiders fall into a covered spike pit; the others hack saplings into a ladder to
// fetch them while the defenders shoot; the raid is driven off, leaving some injured prisoners already in a tidy prison).
// Offline: the pure verdicts (RM_RaiderTrenchMath.FetchFallen, RescueDrop, ClaimLive), the duty patches that put
// JobGiver_RM_FetchFallen before the first fight node of AssaultColony, Breaching and Sapper, and the call sites that keep the
// crossing and the ladder-taking out of the fetcher's way. Each case has a can-fail.
// NOT proven here: a live raid where one raider fells a sapling, carries it, lowers it into the pit while the others shoot,
// and a fallen raider climbing it out; the single message per raid; the fetcher giving up when the raid flees. Live rows owed.
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
        }
    }
}
