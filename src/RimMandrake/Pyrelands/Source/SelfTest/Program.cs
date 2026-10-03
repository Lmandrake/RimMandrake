// Selftest for PYRELANDS_FURNACE_WARMTH_AMBIENT_1: the furnace-beast's local felt-temperature offset.
// REAL, compiled from production source: FurnaceWarmthMath. NOT covered (needs a live Map): the Harmony
// postfix on Thing.AmbientTemperature and the per-map registry; those are the quicktest criteria.
using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands.SelfTest
{
    internal static class Program
    {
        private static readonly List<string> Pass = new List<string>();
        private static readonly List<string> Fail = new List<string>();

        private static void Case(string name, Action fn)
        {
            try { fn(); Pass.Add(name); } catch (Exception ex) { Fail.Add(name + ": " + ex.Message); }
        }

        private static void Assert(bool c, string m) { if (!c) throw new Exception(m); }

        private static int Main()
        {
            Case("a pawn beside the beast feels the full offset, a pawn at the radius feels none", () =>
            {
                Assert(Math.Abs(FurnaceWarmthMath.Offset(0f, 4.9f, 14f, 1f) - 14f) < 1e-4f, "not full at the beast");
                Assert(FurnaceWarmthMath.Offset(4.9f * 4.9f, 4.9f, 14f, 1f) == 0f, "not zero at the radius");
                Assert(FurnaceWarmthMath.Offset(100f, 4.9f, 14f, 1f) == 0f, "not zero outside the radius");
            });
            Case("the offset falls off monotonically with distance", () =>
            {
                float prev = float.MaxValue;
                for (float d = 0f; d < 4.9f; d += 0.5f)
                {
                    float o = FurnaceWarmthMath.Offset(d * d, 4.9f, 14f, 1f);
                    Assert(o < prev || o == prev && d == 0f, "offset did not fall at d=" + d);
                    prev = o;
                }
            });
            Case("the strength dial scales it, 0 switches it off", () =>
            {
                float one = FurnaceWarmthMath.Offset(1f, 4.9f, 14f, 1f);
                Assert(Math.Abs(FurnaceWarmthMath.Offset(1f, 4.9f, 14f, 2f) - 2f * one) < 1e-4f, "2x did not double");
                Assert(FurnaceWarmthMath.Offset(1f, 4.9f, 14f, 0f) == 0f, "0x still warm");
            });
            Case("radius follows the thermal charge: run-down is small, fresh is full, no charge comp is full", () =>
            {
                Assert(Math.Abs(FurnaceWarmthMath.Radius(4.9f, 0.35f, true, 0f) - 4.9f * 0.35f) < 1e-4f, "empty charge radius");
                Assert(Math.Abs(FurnaceWarmthMath.Radius(4.9f, 0.35f, true, 1f) - 4.9f) < 1e-4f, "full charge radius");
                Assert(FurnaceWarmthMath.Radius(4.9f, 0.35f, false, 0f) == 4.9f, "no charge comp");
                Assert(FurnaceWarmthMath.Radius(4.9f, 0.35f, true, 7f) == 4.9f, "charge not clamped");
            });
            Case("two beasts are not twice as warm: the warmest counts", () =>
            {
                Assert(FurnaceWarmthMath.Combine(5f, 9f) == 9f && FurnaceWarmthMath.Combine(9f, 5f) == 9f, "combine");
            });
            foreach (string f in Fail) Console.WriteLine("FAIL " + f);
            foreach (string p in Pass) Console.WriteLine("PASS " + p);
            Console.WriteLine(Pass.Count + "/" + (Pass.Count + Fail.Count) + " passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
