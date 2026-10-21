// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 6 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P5):
// the hose's band rules, Verse-free (compiled into the SelfTest). The game adapter is RM_HoseBands (Hose/RM_HoseBands.cs).
namespace RimMandrake.FlowWorks.Hose
{
    public static class HoseBandMath
    {
        /// <summary>The band a hose route reads for a cell: its step depth (the height a pawn walks it at: a dug square's
        /// climb depth, swim water read at its surface, a deck at its walking depth). With the line-crossing rules off every
        /// cell is band 0 (the pre-ruling hose: it ignores dug squares).</summary>
        public static int Band(bool rulesOn, int stepDepth) => rulesOn ? stepDepth : 0;

        /// <summary>Review answer 7: a ladder carries a hose down its wall while it stands on the square, hangs on that wall
        /// and spans the drop. Whether it is RAISED does not matter: raising it leaves the hose hanging (still connected), and
        /// does not make the ladder climbable either.</summary>
        public static bool LadderCarriesHose(bool ladderHere, bool hangsTowardOther, bool reaches, bool raised) =>
            ladderHere && hangsTowardOther && reaches;

        /// <summary>May a hose step between two cardinal neighbours whose bands are aBand and bBand? One band, or a ramp
        /// joining them, or a ladder carrying the hose. A sheer wall otherwise refuses it.</summary>
        public static bool StepLinked(int aBand, int bBand, bool rampJoins, bool ladderCarries) =>
            aBand == bBand || rampJoins || ladderCarries;

        /// <summary>Endpoint reach by band: a hose end couples to a port (or touches water) only on its own band, so a pump on
        /// the lip does not take a hose end lying on the floor below it.</summary>
        public static bool EndReaches(int endBand, int otherBand) => endBand == otherBand;
    }
}
