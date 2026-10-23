// PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL (bridge run 1, save e C3 boar pit 38-39,22-23, D8): the wild boar, logically on 39,23,
// was DRAWN at about (38.5, 21.0), on the room's south wall, with lip-cover soil squares either side of it.
// Mechanism: the sink clamp (PIT_LIP_OCCLUDES_OUTSIDE_1) measured the room above the near lip from the LOGICAL cell's
// centre (Position), but the sink is subtracted from the TWEENED draw position. Vanilla's PawnTweener lags the logical
// position (spring 0.09/frame, ~0.85 cell behind a walking boar at any speed) and freezes entirely while paused, so after
// the boar stepped 38,22 -> 39,23 its tween still sat on 38,22: room 1.5 (from 23.5) taken off 22.5 put it 1.0 below the lip.
// The fix holds the drawn centre itself above the near lip in the DRAWN column (RM_PitDrawMath.HoldToDrawnLip).
// Each case has a can-fail. NOT proven here: the live frame (re-capture C3 on save e).
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitDrawHoldChecks
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

        // save e's boar pit: 38-39 x 22-23 dug to 8, ground (0) all round; -1 = off the map
        private static int BoarPit(int x, int z)
        {
            if (x < 0 || z < 0 || x >= 250 || z >= 250) return -1;
            return x >= 38 && x <= 39 && z >= 22 && z <= 23 ? 8 : 0;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PitDrawHold_lip_found_in_the_drawn_column", () =>
            {
                Assert(RM_PitDrawMath.LipZBelow(39, 23, 8, BoarPit, 16) == 22f, "north row: the lip is the ground row's north edge, 22");
                Assert(RM_PitDrawMath.LipZBelow(38, 22, 8, BoarPit, 16) == 22f, "south row: the same lip, right under the cell");
                Assert(float.IsNaN(RM_PitDrawMath.LipZBelow(38, 23, 9, (x, z) => z < 0 ? -1 : 9, 16)), "can-fail: no shallower cell -> NaN");
                Assert(float.IsNaN(RM_PitDrawMath.LipZBelow(38, 2, 8, (x, z) => z < 0 ? -1 : 8, 16)), "can-fail: the map edge stops the search");
            });

            Case("PitDrawHold_boar_with_a_lagging_tween_stays_in_the_pit", () =>
            {
                // the per-cell clamp for Position 39,23 lets 1.5 through (centre 23.5, lip 22)
                float perCell = RM_PitDrawMath.ClampSinkToLip(RM_PitDrawMath.SinkFor(8, 0.3f), 23.5f, 22f);
                Assert(Math.Abs(perCell - 1.5f) < 1e-4f, "per-cell clamp on 39,23 is 1.5, got " + perCell);
                // the tween still on 38,22 (frozen while paused / lagging while walking)
                float held = RM_PitDrawMath.HoldToDrawnLip(perCell, 38.5f, 22.5f, 8, BoarPit);
                float drawnZ = 22.5f - held;
                Assert(drawnZ >= 22f - 1e-4f, "drawn centre held on/above the near lip (22), got " + drawnZ);
                Assert(Math.Abs(held - 0.5f) < 1e-4f, "held sink 0.5, got " + held);
                Assert(22.5f - perCell < 22f - 0.5f, "can-fail: the per-cell clamp alone draws the boar a cell below the lip (21.0)");
            });

            Case("PitDrawHold_tween_on_the_cell_changes_nothing", () =>
            {
                float s = RM_PitDrawMath.SinkFor(8, 0.3f);
                float atCell = RM_PitDrawMath.ClampSinkToLip(s, 23.5f, 22f);
                Assert(Math.Abs(RM_PitDrawMath.HoldToDrawnLip(atCell, 39.5f, 23.5f, 8, BoarPit) - atCell) < 1e-4f, "at rest the hold equals the per-cell clamp");
                Assert(Math.Abs(RM_PitDrawMath.HoldToDrawnLip(s, 38.5f, 30.5f, 8, (x, z) => z < 0 ? -1 : 8) - s) < 1e-4f, "a long trench with no lip within reach: full sink");
                Assert(RM_PitDrawMath.HoldToDrawnLip(s, 38.5f, 22.9f, 8, BoarPit) < s, "can-fail: drawn on the south row the hold does bite");
                Assert(RM_PitDrawMath.HoldToDrawnLip(s, 38.5f, 22.5f, 0, BoarPit) == s, "d <= 0: nothing to hold (no sink came from a hole)");
                Assert(RM_PitDrawMath.HoldToDrawnLip(0f, 38.5f, 22.5f, 8, BoarPit) == 0f, "no sink stays none");
            });

            Case("PitDrawHold_SinkOf_holds_the_drawn_position", () =>
            {
                string src = Src("Superdeep", "RM_PitDepthDraw.cs");
                string sinkOf = Between(src, "public static float SinkOf(", "private static float Clamped(");
                Assert(sinkOf.Contains("return Held(Clamped(ex, pawn.Map, from, dFrom, perLevel), drawPos, dFrom);"), "at rest SinkOf holds the drawn position");
                Assert(sinkOf.Contains("return Held(sa + (sb - sa) * t, drawPos,"), "moving, SinkOf holds the drawn position");
                string held = Between(src, "private static float Held(", "private static readonly Func<int, int, int> SeenDepth");
                Assert(held.Contains("HoldToDrawnLip(sink, drawPos.x, drawPos.z, d, SeenDepth)"), "the hold reads the TWEENED draw position, not Position");
                Assert(held.Contains("pitSinkClampEnabled"), "the hold sits under the clamp switch (X rows run with it off)");
                string clamped = Between(Src("Superdeep", "RM_PitDepthDraw.cs"), "private static float Clamped(", "private static RM_MapComponent_Excavation ExcavationOf(");
                Assert(clamped.Contains("LipZBelow("), "the per-cell clamp uses the same lip finder");
            });
        }
    }
}
