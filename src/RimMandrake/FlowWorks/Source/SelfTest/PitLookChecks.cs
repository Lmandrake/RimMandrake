// PIT_LOOK_TREATMENTS (Artisan pass 3, 2026-11-07): the oblique cut's far face, the hole's light and the well's perspective.
// The bars: pit_depth_ladder_legible (every depth its own look, 4 m and 8 m apart), pawn_height_ladder_legible (no lower past
// 4 m), pit_reads_as_hole (some floor always shows at the near lip, where the occupant is drawn).
using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitLookChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            int[] ladder = { 1, 2, 3, 4, 8, 16 };   // 0.5, 1, 1.5, 2, 4, 8 m
            Case("PitLook_oblique_face_grows_every_step", () =>
            {
                for (int run = 1; run <= 6; run++)
                {
                    float prev = 0f;
                    foreach (int d in ladder)
                    {
                        float f = RM_PitLookMath.ObliqueFace(d, run, 0.3f, 0.15f);
                        // PIT_DEPTH_ONE_DRAWING: a 1-row opening has 0.85 of room and the face eases into it (0.37, 0.66, 0.80,
                        // 0.83, 0.85, 0.85), so there it only has to keep growing; from 2 rows every step shows
                        Assert(run == 1 ? f > prev : f > prev + 0.04f, "run " + run + ": face at " + d + " notches " + f + " not above " + prev);
                        Assert(f <= run - 0.15f + 1e-4f, "run " + run + ": face " + f + " leaves no floor");
                        prev = f;
                    }
                }
            });
            Case("PitLook_4m_8m_apart_in_trap_pit", () =>
            {
                // PIT_DEPTH_ONE_DRAWING: past 4 m only the face grows (DeepFaceExtra, 0.22 at 8 m, k 0.3); a 2-row opening eases
                // it into 1.85 of room, so 4 m 1.49 and 8 m 1.63 there (0.14 apart), 1.50 and 1.72 from 3 rows
                float a = RM_PitLookMath.ObliqueFace(8, 2f, 0.3f, 0.15f), b = RM_PitLookMath.ObliqueFace(16, 2f, 0.3f, 0.15f);
                Assert(b - a >= 0.12f, "2-row pit: 4 m " + a + " vs 8 m " + b);
                float a3 = RM_PitLookMath.ObliqueFace(8, 3f, 0.3f, 0.15f), b3 = RM_PitLookMath.ObliqueFace(16, 3f, 0.3f, 0.15f);
                Assert(b3 - a3 >= 0.2f, "3-row pit: 4 m " + a3 + " vs 8 m " + b3);
            });
            Case("PitLook_shallow_true_scale", () =>
            {
                float f = RM_PitLookMath.ObliqueFace(2, 5f, 0.3f, 0.15f);
                Assert(Math.Abs(f - RM_PitDrawMath.SinkFor(2, 0.3f)) < 1e-4f, "1 m in a wide pit hangs exactly the occupant's sink ("
                    + RM_PitDrawMath.SinkFor(2, 0.3f) + "): " + f);
                Assert(RM_PitLookMath.ObliqueFace(0, 2f, 0.3f, 0.15f) == 0f, "undug has no face");
                Assert(RM_PitLookMath.ObliqueFace(4, 2f, float.NaN, 0.15f) == 0f, "NaN scale draws nothing");
            });
            Case("PitLook_floor_darkens_with_depth", () =>
            {
                float prev = 0f;
                foreach (int d in ladder)
                {
                    float k = RM_PitLookMath.FloorDark(d, RM_PitLookMath.Oblique);
                    Assert(k > prev && k <= 0.82f, "floor dark at " + d + ": " + k);
                    prev = k;
                }
            });
            Case("PitLook_well_scale_stops_at_4m", () =>
            {
                Assert(RM_PitLookMath.OccupantScale(8, RM_PitLookMath.Well) == RM_PitLookMath.OccupantScale(16, RM_PitLookMath.Well), "no smaller past 4 m");
                Assert(RM_PitLookMath.OccupantScale(8, RM_PitLookMath.Oblique) == 1f, "only the well scales");
                Assert(RM_PitLookMath.OccupantShade(4, RM_PitLookMath.Bevel) == 0f, "the bevel look leaves pawns alone");
            });
        }
    }
}
