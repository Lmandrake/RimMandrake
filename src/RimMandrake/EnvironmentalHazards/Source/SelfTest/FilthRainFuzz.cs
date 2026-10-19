// SUMP_TAR_LIVING_SYSTEMS_1 (tar rain): properties of ../RM_FilthRainKernel.cs (the production file).
// Family "filthrain": a burst MTB scales inversely with frequency and a non-positive/NaN/inf input means never
// (+inf); cells per event are in [0, mapArea], 0 exactly when nothing is asked, >= 1 otherwise, and grow with area
// and intensity; the pawn chance stays in [0, 1].
using System;

namespace RimMandrake.EnvironmentalHazards.SelfTest
{
    internal static class FilthRainFuzz
    {
        public static int Cases;

        public static bool Run(double scale, int? one, string only)
        {
            if (only != null && only != "filthrain") return true;
            bool ok = true;
            int n = (int)(5000 * scale);
            for (int i = 0; i < n; i++)
            {
                int seed = one ?? i;
                Random r = new Random(seed);
                Cases++;
                float mtb = Wild(r), freq = Wild(r);
                float e = RM_FilthRainKernel.EffectiveMtbHours(mtb, freq);
                bool never = !(mtb > 0f) || float.IsInfinity(mtb) || !(freq > 0f) || float.IsInfinity(freq);
                if (never ? !float.IsPositiveInfinity(e) : !(e > 0f) || Math.Abs(e * freq - mtb) > 1e-3f * mtb)
                {
                    Console.WriteLine("FAIL filthrain seed " + seed + ": mtb " + mtb + " freq " + freq + " -> " + e); ok = false;
                }
                float cells = Wild(r), inten = Wild(r);
                int area = r.Next(5) == 0 ? r.Next(-5, 2) : r.Next(1, 400 * 400);
                int c = RM_FilthRainKernel.CellsPerEvent(cells, area, inten);
                bool none = area <= 0 || !(cells > 0f) || !(inten > 0f) || float.IsInfinity(cells) || float.IsInfinity(inten);
                if (c < 0 || (area > 0 && c > area) || (none ? c != 0 : c < 1))
                {
                    Console.WriteLine("FAIL filthrain seed " + seed + ": cells " + cells + " area " + area + " inten " + inten + " -> " + c); ok = false;
                }
                if (!none && area < int.MaxValue / 2)
                {
                    int bigger = RM_FilthRainKernel.CellsPerEvent(cells, Math.Min(area * 2, 400 * 400 * 2), inten);
                    if (bigger < c)
                    {
                        Console.WriteLine("FAIL filthrain seed " + seed + ": doubling area shrank cells " + c + " -> " + bigger); ok = false;
                    }
                }
                float p = RM_FilthRainKernel.PawnChance(Wild(r), Wild(r));
                if (!(p >= 0f && p <= 1f))
                {
                    Console.WriteLine("FAIL filthrain seed " + seed + ": pawn chance " + p); ok = false;
                }
            }
            // fixed points: the shipped Sump numbers
            Cases++;
            if (RM_FilthRainKernel.CellsPerEvent(6f, 250 * 250, 1f) != 6 || RM_FilthRainKernel.EffectiveMtbHours(96f, 2f) != 48f
                || !float.IsPositiveInfinity(RM_FilthRainKernel.EffectiveMtbHours(96f, 0f)))
            {
                Console.WriteLine("FAIL filthrain fixed points"); ok = false;
            }
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
                default: return (float)((r.NextDouble() - 0.3) * 200.0);
            }
        }
    }
}
