// PIT_COVER_FIX_OCCUPANT_STAYS_BELOW (owner card 2026-10-21 "Stays below, hidden"): a pawn down in a pit when a concealed
// pit's lid is laid stays below, hidden, held; it leaves only along the floor into an OPEN pit square. Offline checks on the
// production rules (RM_PitCoverBeneathMath) and on the production call sites that read them. Each case has a can-fail.
// NOT proven here: the live game (the lid laid over a colonist, her square, draw, inspect line) — validation_v2.py row
// X10_cover_occupant_stays_below, owed live.
using System;
using System.IO;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitCoverBeneathChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("Beneath_who_goes_under_a_new_lid", () =>
            {
                Assert(RM_PitCoverBeneathMath.TakesBeneath(true, false, false, false), "a living walker down in the pit goes beneath");
                Assert(!RM_PitCoverBeneathMath.TakesBeneath(false, false, false, false), "can-fail: nobody on an undug square");
                Assert(!RM_PitCoverBeneathMath.TakesBeneath(true, true, false, false), "can-fail: not the dead");
                Assert(!RM_PitCoverBeneathMath.TakesBeneath(true, false, true, false), "can-fail: not a flyer (it is above the pit)");
                Assert(!RM_PitCoverBeneathMath.TakesBeneath(true, false, false, true), "can-fail: a loaded save keeps its saved set");
            });

            Case("Beneath_leaves_only_into_an_open_pit_square", () =>
            {
                // 2 m pit (4 notches), person climb limit 2
                Assert(RM_PitCoverBeneathMath.StepAllowed(false, true, false, 4, 4, 2), "along the floor into an open pit square");
                Assert(RM_PitCoverBeneathMath.StepAllowed(false, true, false, 4, 3, 2), "a step the pawn could climb anyway");
                Assert(!RM_PitCoverBeneathMath.StepAllowed(false, false, false, 4, 0, 2), "can-fail: never up onto ground (the pop-up)");
                Assert(!RM_PitCoverBeneathMath.StepAllowed(false, true, true, 4, 4, 2), "can-fail: never under the next lid (conservative rule)");
                Assert(!RM_PitCoverBeneathMath.StepAllowed(true, true, false, 4, 4, 2), "can-fail: no diagonal step past a corner");
                Assert(!RM_PitCoverBeneathMath.StepAllowed(false, true, false, 8, 1, 2), "can-fail: a wall too high to climb");
                Assert(!RM_PitCoverBeneathMath.StepAllowed(false, true, false, 4, 0, 9), "can-fail: a 'dug' square at depth 0 is ground");
            });

            Case("Beneath_trapped_when_no_open_neighbour", () =>
            {
                Assert(RM_PitCoverBeneathMath.Trapped(false, false, false, false), "sealed: the C12 3x3 fully covered");
                Assert(!RM_PitCoverBeneathMath.Trapped(false, true, false, false), "can-fail: one open neighbour is a way");
            });

            Case("Beneath_wired_at_the_call_sites", () =>
            {
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                string cover = Src("Pits", "Building_PitCover.cs");
                string span = Src("Pits", "Building_SpanDeck.cs");
                string util = Src("Pits", "RM_PitCoverBeneath.cs");
                Assert(trap.Contains("c == p.Position && Pits.RM_PitCoverBeneath.IsBeneath(p)"), "IsHeldAt holds a beneath pawn");
                Assert(trap.Contains("return Pits.RM_PitCoverBeneath.Trapped(p);"), "IsTrapped reads the beneath rule");
                Assert(trap.Contains("Pits.RM_PitCoverBeneath.StepAllowed(pawn, eng, __instance.nextCell)"), "the step floor reads the beneath rule");
                Assert(trap.Contains("&& !InBeneathSet(p)"), "stepping out from under a lid is no fall");
                Assert(trap.Contains("\"rmBeneathCover\""), "the beneath set is saved");
                Assert(cover.Contains("RM_PitCoverBeneath.TakeUnder(this, respawningAfterLoad)"), "a new lid takes its occupants under");
                Assert(cover.Contains("!p.Flying && !RM_PitCoverBeneath.IsBeneath(p)"), "a broken lid does not drop them a second time");
                Assert(cover.Contains("t is Pawn p && !RM_PitCoverBeneath.IsBeneath(p)"), "a blast does not drop them a second time");
                Assert(cover.Contains("Below, hidden: "), "inspecting the lid names who is under it");
                Assert(span.Contains("!RM_PitCoverBeneath.IsBeneath(p)"), "a beneath pawn is not on the lid's load");
                Assert(util.Contains("nameof(Pawn.DynamicDrawPhaseAt)") && util.Contains("nameof(Pawn.DrawGUIOverlay)"), "hidden: not drawn, no label");
                // can-fail: the beneath read must require an intact lid on the pawn's own square
                Assert(util.Contains("st.InBeneathSet(p) && RM_PitCoverUtility.CoverAt(p.Map, p.Position) != null"), "beneath needs the lid there");
            });
        }
    }
}
