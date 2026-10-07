using System;

namespace RimMandrake.EnvironmentalHazards
{
    // Verse-free arithmetic of the fresh->brine salinity axis (RM_MapComponent_GradientAxis) and the surge that drives
    // it (RM_GameCondition_GradientSurge). Pulled out so the offline fuzz in SelfTest/ can run the PRODUCTION
    // expressions with no game: every method is the exact expression the component used to carry inline (same float
    // operation order, same types). No `using Verse;` / UnityEngine here - the selftest project compiles this file
    // alone, so one landing in it breaks that build, which is the guard rail.
    public static class RM_AxisKernel
    {
        public const float ShortScale = 65535f;

        // Mathf.Clamp01 semantics, NaN included (NaN passes through).
        public static float Clamp01(float value)
        {
            if (value < 0f) return 0f;
            if (value > 1f) return 1f;
            return value;
        }

        // ShiftAxis: a shift is never shorter than one tick.
        public static int ClampDuration(int durationTicks)
        {
            return durationTicks < 1 ? 1 : durationTicks;
        }

        // TickShift step 1: how many ticks of the remaining shift this throttled update consumes.
        public static int StepTicks(int updateInterval, int ticksRemaining)
        {
            return Math.Min(updateInterval, ticksRemaining);
        }

        // TickShift step 2: this update's proportional slice of the remaining delta (telescopes to the total).
        public static float StepDelta(float deltaRemaining, int step, int ticksRemaining)
        {
            return ticksRemaining > 0
                ? deltaRemaining * step / ticksRemaining
                : deltaRemaining;
        }

        public static bool ShiftFinished(int ticksRemaining)
        {
            return ticksRemaining <= 0;
        }

        // ApplyDeltaToAllCells: one cell.
        public static float Apply(float salinity, float delta)
        {
            return Clamp01(salinity + delta);
        }

        // The salt-line fleck band test (strict).
        public static bool InFleckBand(float salinity, float band)
        {
            return Math.Abs(salinity - 0.5f) < band;
        }

        // SaltLineCells membership (strict on both sides).
        public static bool InSaltLine(float salinity, float band)
        {
            return salinity > 0.5f - band && salinity < 0.5f + band;
        }

        // Scribe: the grid is saved as ushort and read back through SetSalinityAt's clamp.
        public static ushort Quantize(float salinity)
        {
            return (ushort)(int)Math.Round(salinity * ShortScale);
        }

        public static float Dequantize(ushort stored)
        {
            return stored / ShortScale;
        }

        // GradientSurge.Init: the forward shove, as a fraction of the half-extent the front crawls.
        public static float TotalDelta(int frontCells, int sizeX, int sizeZ)
        {
            float halfExtent = Math.Max(sizeX, sizeZ) * 0.5f;
            return halfExtent > 0f ? frontCells / (2f * halfExtent) : 0f;
        }

        // GradientSurge.End: the recede reverses most, never all, of the forward delta.
        public static float RecedeDelta(float totalDelta, float residualFraction)
        {
            return -totalDelta * (1f - residualFraction);
        }
    }
}
