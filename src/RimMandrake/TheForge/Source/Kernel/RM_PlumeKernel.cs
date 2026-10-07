// Verse-free kernel of the white plume fronts (FORGE_WHITE_PLUME_FRONTS_1): spawn gate, front stepping, the per-cell
// expiry book the heat Harmony postfix reads, strength scaling. RM_ForgePlumeFronts.cs calls these with the same
// expressions; SelfTest/TheForgeFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;
using System.Collections.Generic;

namespace RimMandrake.TheForge
{
    public static class RM_PlumeKernel
    {
        public const int StepTicks = 15;
        public const int MaxFronts = 5;
        public const int LifeTicks = 1800;
        public const int ExpiryTicks = StepTicks * 3;
        public const float CellsPerStep = 0.75f;
        public const float BaseGas = 50f;
        public const float BaseHeatOffset = 25f;
        public const int PruneAbove = 4000;
        public const int ActiveWindowTicks = 60;

        public static float Strength(float setting) { return Math.Min(2f, Math.Max(0.25f, setting)); }
        public static int GasPerCell(float setting) { return Math.Max(1, (int)Math.Round(BaseGas * Strength(setting))); }
        public static float HeatOffset(float setting) { return BaseHeatOffset * Strength(setting); }

        // A newly crusted cell may start a front only while the feature is on and the cap is not reached (the chance roll follows).
        public static bool CanSpawn(bool enabled, int liveFronts) { return enabled && liveFronts < MaxFronts; }

        // Advances a front one step. Returns false when it is over (lifetime spent, or its centre cell left the map).
        public static bool Step(ref float x, ref float z, float dx, float dz, ref int ticksLeft, int width, int height)
        {
            x += dx * CellsPerStep;
            z += dz * CellsPerStep;
            ticksLeft -= StepTicks;
            int cx = (int)Math.Floor(x), cz = (int)Math.Floor(z);
            return !(ticksLeft <= 0 || cx < 0 || cz < 0 || cx >= width || cz >= height);
        }

        // The Harmony postfix's cheap bail-out: no front on any map for a while.
        public static bool RecentlyActive(int now, int lastActiveTick) { return !(now - lastActiveTick > ActiveWindowTicks); }

        // Vapour-adapted (or not flesh, so no heatstroke to speak of).
        public static bool Exempt(bool isFlesh, bool adaptedExemptSetting, bool hasDrifterGroundImmune)
        {
            if (!isFlesh) return true;
            if (!adaptedExemptSetting) return false;
            return hasDrifterGroundImmune;
        }

        public static bool HeatApplies(bool heatEnabled, bool cellInPlume, bool exempt) { return heatEnabled && cellInPlume && !exempt; }
    }

    /// <summary>The cell-expiry book: cell index -> last tick the cell is still inside a front.</summary>
    public sealed class RM_PlumeBook
    {
        public readonly Dictionary<int, int> Expiry = new Dictionary<int, int>();

        public void Mark(int cell, int now) { Expiry[cell] = now + RM_PlumeKernel.ExpiryTicks; }

        public bool InPlume(int liveFronts, int cell, int now)
        {
            if (liveFronts == 0) return false;
            return Expiry.TryGetValue(cell, out int exp) && exp >= now;
        }

        public void ClearAll() { Expiry.Clear(); }

        public int Prune(int now)
        {
            if (Expiry.Count <= RM_PlumeKernel.PruneAbove) return 0;
            var dead = new List<int>();
            foreach (KeyValuePair<int, int> kv in Expiry)
            {
                if (kv.Value < now) dead.Add(kv.Key);
            }
            for (int d = 0; d < dead.Count; d++) Expiry.Remove(dead[d]);
            return dead.Count;
        }
    }
}
