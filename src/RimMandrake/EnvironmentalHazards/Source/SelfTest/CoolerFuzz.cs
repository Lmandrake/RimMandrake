// BLOWER_ROOM_COOLER_1 + LAUNCH_HELD_COLONIST_WARNING_1: properties of ../RM_RoomCoolerKernel.cs (the production file).
// Family "cooler": the blower never heats (energy <= 0, applied change <= 0 for any input incl. NaN/inf), power draw is
// bounded by the setting and full only while cooling. Family "held": the launch warning names exactly ours-alive-unspawned-
// not-in-transporter-held-by-not-ours, checked over all 64 flag combinations against an independently written oracle.
using System;

namespace RimMandrake.EnvironmentalHazards.SelfTest
{
    internal static class CoolerFuzz
    {
        public static int Cases;

        public static bool Run(double scale, int? one, string only)
        {
            bool ok = true;
            if (only == null || only == "cooler") ok &= Cooler(scale, one);
            if (only == null || only == "held") ok &= Held();
            return ok;
        }

        private static float Wild(Random r)
        {
            switch (r.Next(8))
            {
                case 0: return float.NaN;
                case 1: return float.PositiveInfinity;
                case 2: return float.NegativeInfinity;
                case 3: return 0f;
                default: return (float)((r.NextDouble() - 0.5) * 2000.0);
            }
        }

        private static bool Cooler(double scale, int? one)
        {
            int n = (int)(5000 * scale);
            bool ok = true;
            for (int i = 0; i < n; i++)
            {
                int seed = one ?? i;
                Random r = new Random(seed);
                Cases++;
                float strength = Wild(r);
                float e = RM_RoomCoolerKernel.CoolingEnergyPerRareTick(strength);
                if (!(e <= 0f) || float.IsNaN(e) || float.IsInfinity(e))
                {
                    Console.WriteLine("FAIL cooler seed " + seed + ": energy " + e + " for strength " + strength); ok = false;
                }
                float change = Wild(r);
                float applied = RM_RoomCoolerKernel.ClampNeverHeat(change);
                if (!(applied <= 0f) || (change <= 0f && applied != change))
                {
                    Console.WriteLine("FAIL cooler seed " + seed + ": clamp " + change + " -> " + applied); ok = false;
                }
                float watts = (float)(r.NextDouble() * 1200.0 - 200.0);
                float low = (float)(r.NextDouble() * 3.0 - 1.0);
                float full = RM_RoomCoolerKernel.PowerDraw(watts, true, low);
                float idle = RM_RoomCoolerKernel.PowerDraw(watts, false, low);
                float wMax = Math.Max(0f, watts);
                if (full != wMax || idle < 0f || idle > full)
                {
                    Console.WriteLine("FAIL cooler seed " + seed + ": power full " + full + " idle " + idle + " for " + watts + "W low " + low); ok = false;
                }
                if (one.HasValue) break;
            }
            // Fixed anchor: vanilla cooler scale, 21/s -> -87.5 per rare tick.
            Cases++;
            if (Math.Abs(RM_RoomCoolerKernel.CoolingEnergyPerRareTick(21f) + 87.5f) > 0.01f)
            {
                Console.WriteLine("FAIL cooler anchor: 21 heat/s should be -87.5 per rare tick"); ok = false;
            }
            return ok;
        }

        private static bool Held()
        {
            bool ok = true;
            int named = 0;
            for (int m = 0; m < 64; m++)
            {
                Cases++;
                bool ours = (m & 1) != 0, dead = (m & 2) != 0, spawned = (m & 4) != 0;
                bool transporter = (m & 8) != 0, hasHolder = (m & 16) != 0, holderOurs = (m & 32) != 0;
                bool expect = m == (1 | 16); // the one combination: ours, held by something not ours, nothing else
                bool got = RM_RoomCoolerKernel.ShouldNameHeld(ours, dead, spawned, transporter, hasHolder, holderOurs);
                if (got) named++;
                if (got != expect)
                {
                    Console.WriteLine("FAIL held mask " + m + ": got " + got + " expected " + expect); ok = false;
                }
            }
            if (named != 1) { Console.WriteLine("FAIL held: named " + named + " combinations, expected exactly 1"); ok = false; }
            return ok;
        }
    }
}
