using System;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the furnace-beast kit: the thermal-charge step and its hysteresis (CompFurnaceThermalCharge), the
    // bed-ignition rest clock and cell count (CompFurnaceBedIgnition), the size ratio and the fire-hawk sortie cooldown. Tuning numbers are PARAMETERS (the mod
    // passes PyrelandsTuning's constants; the fuzz reads PyrelandsTuning.cs itself), so nothing here can drift from the shipped values.

    public enum RM_RestOutcome { Resting, NothingToReport, WokeTooShort, WokeRested }

    public static class RM_FurnaceKernel
    {
        /// <summary>One charge check. Above the ambient threshold it charges in proportion to how far above (capped at the span); below the
        /// bleed threshold it drains likewise; between them it holds. Standing near fire adds a fixed fast-lane step.</summary>
        public static float ChargeStep(float ambient, bool nearFire, float chargeAmbientC, float chargeSpanC, float chargePerCheckAtFullHeat,
            float bleedAmbientC, float bleedSpanC, float bleedPerCheckAtFullCold, float nearFireStep)
        {
            float step;
            if (ambient >= chargeAmbientC)
            {
                float over = Math.Min(ambient - chargeAmbientC, chargeSpanC);
                step = chargePerCheckAtFullHeat * (over / chargeSpanC);
            }
            else if (ambient <= bleedAmbientC)
            {
                float under = Math.Min(bleedAmbientC - ambient, bleedSpanC);
                step = -bleedPerCheckAtFullCold * (under / bleedSpanC);
            }
            else
            {
                step = 0f;
            }
            if (nearFire)
            {
                step += nearFireStep;
            }
            return step;
        }

        public static float ClampCharge(float charge)
        {
            return charge < 0f ? 0f : charge > 1f ? 1f : charge;
        }

        public static bool WantsHeat(float charge, float seekBelow)
        {
            return charge < seekBelow;
        }

        public static bool IsFullyCharged(float charge, float avoidAbove)
        {
            return charge >= avoidAbove;
        }

        /// <summary>The bed-ignition rest clock for one interval: asleep accumulates; on waking the accumulated rest is judged.</summary>
        public static RM_RestOutcome RestStep(ref int restingTicks, bool awake, int delta, int minRestTicks)
        {
            if (!awake)
            {
                restingTicks += delta;
                return RM_RestOutcome.Resting;
            }
            if (restingTicks <= 0)
            {
                return RM_RestOutcome.NothingToReport;
            }
            int slept = restingTicks;
            restingTicks = 0;
            return slept < minRestTicks ? RM_RestOutcome.WokeTooShort : RM_RestOutcome.WokeRested;
        }

        /// <summary>The cells a rested beast smoulders: the min..max range scaled by its size (rounded), and the scatter radius.</summary>
        public static void BedCells(float sizeRatio, int minCells, int maxCells, out int lo, out int hi, out float spread)
        {
            lo = (int)Math.Round(minCells * sizeRatio);
            hi = (int)Math.Round(maxCells * sizeRatio);
            spread = Math.Max(1.5f, 1.5f * sizeRatio);
        }

        public static float SizeRatio(float? baseBodySize, float classicBodySize)
        {
            float baseSize = baseBodySize ?? classicBodySize;
            return Math.Max(0.25f, baseSize / classicBodySize);
        }

        public static bool SortieReady(int now, int lastSortieTick, int cooldownTicks)
        {
            return now - lastSortieTick >= cooldownTicks;
        }
    }
}
