// PIT_DEPTH_ONE_DRAWING (pass 8, 2026-11-08): one depth drawing for pits. The occupant's sink, the far face and the near lip
// are drawn from one curve (RM_PitDrawMath.SinkFor) and one opening room (SoftCap), so the face's foot is the occupant's
// floor line and a deeper hole always draws him lower, never past 4 m. The bars: pawn_height_ladder_legible,
// pawn_lowers_on_deeper_cell, pawn_rises_on_shallower_cell, pit_occupant_below_floor, pit_trapped_reads_as_trapped,
// pit_depth_ladder_legible. Every threshold is scaled by k / 0.3 where the claim is about the curve; the sprite-size checks
// (feet 0.75 below the centre, crown 0.5 above) are at the default k only, as the brief says (no retune for the humanlike).
using System;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitDepthDrawingChecks
    {
        private const float MinFloor = RM_PitLookMath.ObliqueMinFloor;
        private const float K0 = RM_PitDrawMath.DefaultSinkPerLevel;

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
            Assert(j >= 0, "end marker present after " + start + ": " + end);
            return src.Substring(i, j - i);
        }

        // A rectangular pit of `rows` rows (z O..O+rows-1), x O..O+2, all dug to d; ground all round; -1 off a 30 x 30 map.
        private const int O = 5;
        private static Func<int, int, int> Box(int rows, int d) => (x, z) =>
            x < 0 || z < 0 || x >= 30 || z >= 30 ? -1 : (x >= O && x <= O + 2 && z >= O && z < O + rows ? d : 0);

        // The per-cell draw chain of RM_Patch_PitDepthDrawOffset.Clamped with the clamp on: the sink eased into the column's
        // opening, then held on (or holdAbove over) the riser-aware near lip.
        private static float Resting(int x, int z, int d, float run, float k, Func<int, int, int> seen, float hold = 0f)
        {
            float sink = RM_PitDrawMath.OccupantSink(d, k, run, MinFloor);
            float lip = RM_PitDrawMath.LipZBelow(x, z, d, seen, RM_PitDrawMath.SinkCapLevels * 2, k);
            return RM_PitDrawMath.ClampSinkToLip(sink, z + 0.5f, lip, hold);
        }

        // The live graded trench (ralph/live/walk7.py): east-west, rows 10..12, column x dug x notches (x 0..8), ground round
        // it. The pawn walks the middle row, z 11. Every column's opening is the 3 rows (rim 13, near 10).
        private static int Trench(int x, int z)
        {
            if (x < -5 || z < 0 || x >= 30 || z >= 30) return -1;
            return x >= 0 && x <= 8 && z >= 10 && z <= 12 ? x : 0;
        }

        // A north-south staircase in column 0: row z dug z notches (z 1..7), rows 8..10 at 8 (4 m), ground at 0 and from 11.
        private static int Stair(int x, int z)
        {
            if (x < -5 || z < 0 || x >= 30 || z >= 30) return -1;
            if (x != 0) return 0;
            return z >= 1 && z <= 7 ? z : (z >= 8 && z <= 10 ? 8 : 0);
        }

        private static float StairRun(int z) => z >= 8 ? 3f : 11f - z;   // rim 11, near: the row itself (8 for the 4 m rows)

        public static void Run(Action<string, Action> Case)
        {
            float[] scales = { 0.15f, 0.3f, 0.45f };

            Case("PitDepth_sink_monotonic_then_flat", () =>
            {
                foreach (float k in scales)
                {
                    float prev = RM_PitDrawMath.SinkFor(0, k);
                    Assert(prev == 0f, "k " + k + ": undug draws no sink");
                    for (int d = 1; d <= RM_PitDrawMath.SinkCapLevels; d++)
                    {
                        float s = RM_PitDrawMath.SinkFor(d, k);
                        Assert(s > prev, "k " + k + ": D" + d + " sink " + s + " not below D" + (d - 1) + " " + prev);
                        prev = s;
                    }
                    for (int d = RM_PitDrawMath.SinkCapLevels + 1; d <= 40; d++)
                    {
                        Assert(RM_PitDrawMath.SinkFor(d, k) == prev, "k " + k + ": no lower past 4 m (D" + d + ")");
                    }
                    // the curve is the scale times one shape
                    for (int d = 1; d <= 16; d++)
                    {
                        float want = RM_PitDrawMath.SinkFor(d, K0) * (k / K0);
                        Assert(Math.Abs(RM_PitDrawMath.SinkFor(d, k) - want) < 1e-4f, "k " + k + ": D" + d + " scales with k");
                    }
                }
                Assert(RM_PitDrawMath.SinkFor(4, 0f) == 0f && RM_PitDrawMath.SinkFor(4, float.NaN) == 0f, "k 0 (or NaN) is off");
                Assert(Math.Abs(RM_PitDrawMath.SinkFor(4, K0) - 4f * K0) < 1e-5f && Math.Abs(RM_PitDrawMath.SinkFor(8, K0) - 5f * K0) < 1e-5f,
                    "knee 4k at 2 m, 5k from 4 m");
            });

            Case("PitDepth_height_ladder_steps", () =>
            {
                int[] ladder = { 0, 1, 2, 3, 4, 8 };   // undug, 0.5, 1, 1.5, 2, 4 m
                foreach (float k in scales)
                {
                    float r = k / K0;
                    Assert(RM_PitDrawMath.SinkFor(1, k) >= 0.35f * r, "k " + k + ": 0.5 m reads (" + RM_PitDrawMath.SinkFor(1, k) + ")");
                    for (int i = 1; i < ladder.Length; i++)
                    {
                        float step = RM_PitDrawMath.SinkFor(ladder[i], k) - RM_PitDrawMath.SinkFor(ladder[i - 1], k);
                        Assert(step >= 0.2f * r, "k " + k + ": step D" + ladder[i - 1] + " -> D" + ladder[i] + " only " + step);
                    }
                    // and the same ladder in a wide pit, through the whole chain (cap and lip), on its north row
                    float prev = -1f;
                    foreach (int d in ladder)
                    {
                        float s = d == 0 ? 0f : Resting(O + 1, O + 4, d, 5f, k, Box(5, d));
                        Assert(s > prev + (d == 0 ? 0f : 0.2f * r), "k " + k + ": drawn sink at D" + d + " " + s + " vs " + prev);
                        prev = s;
                    }
                }
            });

            Case("PitDepth_trapped_wall_a_fifth_over_head", () =>
            {
                float ratio = RM_PitDrawMath.WallOverHeadRatio(4, K0, RM_PitDrawMath.HumanlikeFeetToHeadTop);
                Assert(Math.Abs(ratio - 1.2f) < 1e-4f, "2 m: the wall is 1.2 of the humanlike (" + ratio + ")");
            });

            Case("PitDepth_face_foot_is_the_floor_line", () =>
            {
                foreach (float k in scales)
                {
                    foreach (int rows in new[] { 3, 5 })
                    {
                        foreach (int d in new[] { 4, 8 })
                        {
                            int zn = O + rows - 1;
                            float rim = O + rows, near = O;
                            float face = RM_PitLookMath.ObliqueFace(d, rim - near, k, MinFloor);
                            float floorLine = zn + 1f - Resting(O + 1, zn, d, rim - near, k, Box(rows, d));
                            Assert(Math.Abs((rim - face) - floorLine) < 1e-4f,
                                "k " + k + ", " + rows + "-row D" + d + ": face foot " + (rim - face) + " vs his floor line " + floorLine);
                        }
                    }
                }
            });

            Case("PitDepth_8m_face_below_4m_face", () =>
            {
                foreach (float k in scales)
                {
                    float f4 = RM_PitLookMath.ObliqueFace(8, 3f, k, MinFloor), f8 = RM_PitLookMath.ObliqueFace(16, 3f, k, MinFloor);
                    Assert(f8 > f4, "k " + k + ", 3-row pit: the 8 m face " + f8 + " hangs lower than the 4 m face " + f4);
                    Assert(RM_PitDrawMath.OccupantSink(16, k, 3f, MinFloor) == RM_PitDrawMath.OccupantSink(8, k, 3f, MinFloor),
                        "k " + k + ": the occupant is drawn no lower at 8 m");
                }
                Assert(RM_PitLookMath.DeepFaceExtra(8, K0) == 0f && RM_PitLookMath.DeepFaceExtra(40, K0) < 0.35f, "the extra starts past 4 m and stays under 0.35");
            });

            Case("PitDepth_softcap_shape", () =>
            {
                foreach (float room in new[] { 0.85f, 1.85f, 2.85f })
                {
                    float knee = 0.75f * room, span = room - knee, prev = 0f, prevSlope = 1f;
                    for (int i = 1; i * 0.01f < knee + 3f * span; i++)   // past ~3 spans the ease is below float resolution
                    {
                        float t = i * 0.01f;
                        float v = RM_PitDrawMath.SoftCap(t, room);
                        Assert(v < room || t <= knee, "room " + room + ": " + t + " -> " + v + " reaches the room");
                        Assert(v > prev, "room " + room + ": strictly increasing at " + t);
                        if (t <= knee) Assert(Math.Abs(v - t) < 1e-5f, "room " + room + ": identity under the knee at " + t);
                        float slope = (v - prev) / 0.01f;
                        Assert(slope <= prevSlope + 1e-2f, "room " + room + ": slope never rises (" + slope + " at " + t + ")");
                        prev = v;
                        prevSlope = slope;
                    }
                    // continuous in value and slope at the knee
                    float a = RM_PitDrawMath.SoftCap(knee - 1e-3f, room), b = RM_PitDrawMath.SoftCap(knee + 1e-3f, room);
                    Assert(Math.Abs((b - a) / 2e-3f - 1f) < 0.01f, "room " + room + ": slope 1 through the knee");
                }
                Assert(Math.Abs(RM_PitDrawMath.OpeningRoom(0.16f, MinFloor) - 0.04f) < 1e-6f, "room never below a quarter of the run");
                Assert(Math.Abs(RM_PitDrawMath.OpeningRoom(3f, MinFloor) - 2.85f) < 1e-6f, "room: the run less the kept floor");
                Assert(float.IsNaN(RM_PitDrawMath.OpeningRoom(0f, MinFloor)), "no opening: no room (NaN)");
                Assert(RM_PitDrawMath.SoftCap(1.3f, float.NaN) == 1.3f, "NaN room leaves the sink");
            });

            Case("PitDepth_graded_trench_walk", () =>
            {
                foreach (float k in new[] { 0.15f, K0 })
                {
                    Func<int, int, int> seen = Trench;
                    float[] rest = new float[9];
                    for (int x = 0; x <= 8; x++)
                    {
                        float raw = RM_PitDrawMath.SinkFor(x, k);
                        rest[x] = x == 0 ? 0f : Resting(x, 11, x, 3f, k, seen);
                        Assert(Math.Abs(rest[x] - raw) < 1e-6f, "k " + k + ": column D" + x + " clamped (" + rest[x] + " vs " + raw + ")");
                        if (x > 0) Assert(rest[x] > rest[x - 1], "k " + k + ": D" + x + " not lower than D" + (x - 1));
                    }
                    // the tween, both ways: SinkOf interpolates the two resting sinks, then holds the DRAWN centre over the
                    // shallower square's lip (min depth)
                    foreach (int dir in new[] { 1, -1 })
                    {
                        float prev = dir > 0 ? -1f : 99f;
                        int x0 = dir > 0 ? 0 : 8;
                        for (int step = 0; step < 8; step++)
                        {
                            int xa = x0 + dir * step, xb = xa + dir;
                            for (int i = (step == 0 ? 0 : 1); i <= 20; i++)
                            {
                                float t = i / 20f;
                                float raw = rest[xa] + (rest[xb] - rest[xa]) * t;
                                float drawX = xa + 0.5f + dir * t;
                                float held = RM_PitDrawMath.HoldToDrawnLip(raw, drawX, 11.5f, Math.Min(xa, xb), seen, k, 0f);
                                Assert(Math.Abs(held - raw) < 1e-6f, "k " + k + ": held mid-step " + xa + "->" + xb + " t " + t);
                                Assert(dir > 0 ? held > prev : held < prev, "k " + k + ": " + (dir > 0 ? "deeper" : "back") + " " + xa + "->" + xb + " t " + t + ": " + held + " vs " + prev);
                                prev = held;
                            }
                        }
                    }
                }
            });

            Case("PitDepth_staircase_riser_lip_no_clamp", () =>
            {
                float k = K0;
                Func<int, int, int> seen = Stair;
                float prev = 0f;
                bool oldLipClamps = false;
                for (int z = 1; z <= 10; z++)
                {
                    int d = Stair(0, z);
                    float raw = RM_PitDrawMath.OccupantSink(d, k, StairRun(z), MinFloor);
                    Assert(Math.Abs(raw - RM_PitDrawMath.SinkFor(d, k)) < 1e-6f, "row " + z + ": the opening never squeezes the stair");
                    float drawnOnly = Resting(0, z, d, StairRun(z), k, seen);
                    Assert(Math.Abs(drawnOnly - raw) < 1e-6f, "row " + z + " (D" + d + "): the riser-aware lip does not clamp (" + drawnOnly + ")");
                    // walking north into the row: the tween from z-1
                    int da = Stair(0, z - 1);
                    float sa = da == 0 ? 0f : RM_PitDrawMath.SinkFor(da, k);
                    for (int i = 1; i <= 20; i++)
                    {
                        float t = i / 20f;
                        float s = sa + (raw - sa) * t;
                        float held = RM_PitDrawMath.HoldToDrawnLip(s, 0.5f, z - 0.5f + t, Math.Min(da, d), seen, k, 0f);
                        Assert(Math.Abs(held - s) < 1e-6f, "row " + (z - 1) + "->" + z + " t " + t + ": held " + held + " vs " + s);
                        Assert(held >= prev - 1e-6f, "the walk north never rises: " + held + " after " + prev);
                        prev = held;
                        if (RM_PitDrawMath.HoldToDrawnLip(s, 0.5f, z - 0.5f + t, Math.Min(da, d), seen, 0f, 0f) < s - 1e-4f)
                        {
                            oldLipClamps = true;
                        }
                    }
                }
                Assert(oldLipClamps, "can-fail: the old square-edge lip (k 0 in LipZBelow) clamps the staircase");
            });

            Case("PitDepth_3x3_8m_occupant_inside_opening", () =>
            {
                Func<int, int, int> pit = Box(3, 8);
                float north = O + 2.5f - Resting(O + 1, O + 2, 8, 3f, K0, pit);
                float feet = north - RM_PitDrawMath.HumanlikeBodyHalf, crown = north + 0.5f;
                Assert(feet >= O - 1e-4f && crown <= O + 3f + 1e-4f, "north row drawn feet " + feet + " crown " + crown + " inside the opening " + O + ".." + (O + 3));
                float south = O + 0.5f - Resting(O + 1, O, 8, 3f, K0, pit);
                Assert(Math.Abs(south - O) < 1e-4f, "south row centre on the lip at hold 0: " + south);
                float held = O + 0.5f - Resting(O + 1, O, 8, 3f, K0, pit, 0.4f);
                Assert(Math.Abs(held - (O + 0.4f)) < 1e-4f && held > south, "hold 0.4 draws the south row 0.4 above the lip: " + held);
                Assert(RM_PitDrawMath.ClampSinkToLip(1f, 0.5f, 0f, -1f) == 0.5f, "a negative hold reads as 0");
                Assert(RM_PitDrawMath.HoldToDrawnLip(1.5f, O + 1.5f, O + 0.5f, 8, pit, K0, 0.4f) < RM_PitDrawMath.HoldToDrawnLip(1.5f, O + 1.5f, O + 0.5f, 8, pit, K0, 0f),
                    "the tween hold takes the same setting");
            });

            Case("PitDepth_cover_lip_part_way_down_a_square", () =>
            {
                // a riser-aware lip at 21.6 (a shallower hole's square 21 below it) with a wall in that square: no cover at all
                Func<int, int, bool> wallAt21 = (x, z) => z == 21;
                Assert(RM_PitDrawMath.CoverStopZ(0, 21.6f, 19.8f, wallAt21) == 21.6f, "the lip's own square is tested: empty band");
                Assert(RM_PitDrawMath.CoverStopZ(0, 21.6f, 19.8f, (x, z) => z == 20) == 21f, "a wall a square lower stops the cover at its north edge");
                Assert((int)Math.Floor(21.6f) - 1 == 20, "can-fail: the old floor start skipped square 21");
            });

            Case("PitDepth_source_wiring", () =>
            {
                string draw = Src("Superdeep", "RM_PitDepthDraw.cs");
                string clamped = Between(draw, "private static float Clamped(", "private static RM_MapComponent_Excavation ExcavationOf(");
                Assert(clamped.Contains("RM_PitDrawMath.SoftCap(sink, RM_PitDrawMath.OpeningRoom(OpeningRun(ex, map, c), RM_PitLookMath.ObliqueMinFloor))"),
                    "the occupant is eased into the same opening as the face");
                Assert(clamped.Contains("LipZBelow(c.x, c.z, d, SeenDepth, RM_PitDrawMath.SinkCapLevels * 2, perLevel)")
                    && clamped.Contains("ClampSinkToLip(sink, c.z + 0.5f, lipZ, RimMandrakeFlowWorksSettings.pitSinkHoldAbove)"),
                    "the per-cell clamp is riser-aware and takes the hold");
                Assert(clamped.Contains("[ThreadStatic] private static int[] runKeys;") && clamped.Contains("SectionLayer_RMExcavationWalls.OpeningRunAt("),
                    "the run is memoised per thread (DrawPos runs in parallel pre-draw)");
                string api = Between(draw, "public static class RM_PitDepthDraw", "internal static string FormatState(");
                Assert(api.Contains("public static string DepthDrawState(int thingIdNumber)") && api.Contains("public static void SetSinkPerLevel(float k)")
                    && api.Contains("public static void SetSinkHoldAbove(float cells)"), "the bridge reads and setters are public statics");
                Assert(draw.Contains("\"cell=\"") && draw.Contains("\" hold=\"") && draw.Contains("\" k=\""), "the state line names its fields");
                string lip = Src("Superdeep", "RM_PitLipOcclusion.cs");
                Assert(lip.Contains("float lipZ = lipCell.z + 1f - RM_PitDrawMath.SinkFor(lipSeen, RimMandrakeFlowWorksSettings.pitSinkPerLevel);"),
                    "the cover band starts at the riser-aware lip");
                string face = Src("Superdeep", "RM_ExcavationWalls.cs");
                Assert(face.Contains("return RM_PitLookMath.ObliqueFace(drop, rim - near, RimMandrakeFlowWorksSettings.pitSinkPerLevel, RM_PitLookMath.ObliqueMinFloor);"),
                    "the face reads the same floor kept at the near lip");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("Scribe_Values.Look(ref pitSinkHoldAbove, \"pitSinkHoldAbove\", 0f);") && mod.Contains(".Declare(\"pitSinkClampEnabled\", \"pitSinkHoldAbove\")")
                    && mod.Contains("using (Dependent(list, \"pitSinkHoldAbove\"))"), "the hold is saved, declared under the clamp and has a slider");
            });
        }
    }
}
