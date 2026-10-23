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

        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

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

            // PIT_LID_FIX_VICKY_PEEKS_THROUGH (owner 2026-10-22: a colonist on a covered pit "just gets a funny dark square around
            // her but otherwise is still "over" the cover"): a walker on a lid draws at ground; only a beneath pawn keeps the hole's
            // depth (and is not drawn). The lid is the near lip of an open part of its pit. Live: validation_v2 X8c / X8b.
            Case("LidWalker_drawn_at_ground_not_sunk", () =>
            {
                string susp = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                string sink = Src("Superdeep", "RM_PitDepthDraw.cs");
                string lip = Src("Superdeep", "RM_PitLipOcclusion.cs");
                string draw = Between(susp, "public static int DrawDepth(", "public static bool OnDeck(");
                int coverAt = draw.IndexOf("RM_PitCoverUtility.CoverAt(p.Map, c) != null");
                int suspDeck = draw.IndexOf("is Building_SuspensionDeck d");
                Assert(coverAt > 0 && suspDeck > coverAt, "DrawDepth reads a lid before the suspension-deck branch");
                Assert(draw.Contains("c == p.Position && RM_PitCoverBeneath.IsBeneath(p) ? hollow : RM_SpanUtility.WalkingDepth(p.Map, c, hollow)"),
                    "on a lid: the hole's depth only for a pawn beneath it, else the lid's walking height");
                Assert(!susp.Contains("Covers keep their old read"), "can-fail: the old 'covers sink' doc line is gone");
                // PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL moved the lip scan into RM_PitDrawMath.LipZBelow (s < d) over one SeenDepth lookup
                Assert(sink.Contains("Pits.RM_SuspensionUnderpass.SeenDepthAt(cachedMap, cachedComp, q)") && sink.Contains("RM_PitDrawMath.LipZBelow(c.x, c.z, d, SeenDepth,"),
                    "the sink clamp sees a lid as the lip");
                Assert(lip.Contains("int d = Pits.RM_SuspensionUnderpass.DrawDepth(p, p.Position, eng.HollowDepthAt(p.Position));"),
                    "the lip occluder covers a pawn at its DRAWN depth (a lid walker: none)");
                Assert(lip.Contains("|| Pits.RM_PitCoverBeneath.IsBeneath(p)"), "no lip cover round a hidden beneath pawn");
                Assert(lip.Contains("SeenDepthAt(map, eng, cand) < d") && lip.Contains("SeenDepthAt(map, eng, g) >= d"),
                    "a lid square is ground to the lip search");
                Assert(lip.Contains("lid != null ? lid.PrintedSurface"), "a lid square is drawn in the ground it prints");
                // can-fail: no remaining raw hollow read of the pawn's own depth in the occluder
                Assert(!lip.Contains("int d = eng.HollowDepthAt(p.Position);"), "can-fail: the occluder no longer reads the raw hole depth");
            });
        }
    }
}
