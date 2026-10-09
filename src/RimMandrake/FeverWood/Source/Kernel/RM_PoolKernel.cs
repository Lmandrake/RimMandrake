// Verse-free kernel of the pool's ambient clock (RM_MapComponent_TentacleWatch) and the uranium suppression job
// (RM_JobDriver_FoulPool): the gate the ambient roll passes, the shared blocked-until clock every respite and fouling
// writes to, encounter pressure, the sentinel counter that hushes the chorus. SelfTest/FeverWoodFuzz.cs compiles this
// file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.FeverWood
{
    public enum AmbientKind { None = 0, Ordinary = 1, Great = 2 }

    public static class RM_PoolKernel
    {
        public const float TicksPerDay = 60000f;

        // MapComponentTick, after the hourly gate: off, permanently killed, or still inside a respite = nothing happens.
        public static bool AmbientOpen(bool bestiaryOn, bool permanentlyKilled, int now, int blockedUntil)
        {
            if (!bestiaryOn || permanentlyKilled) return false;
            return !(now < blockedUntil);
        }

        // "Large pool + many limbs" composed threshold.
        public static bool GreatEligible(int poolCells, int poolSizeThreshold, int pressure, int pressureThreshold)
        {
            return poolCells >= Math.Max(1, poolSizeThreshold) && pressure >= Math.Max(0, pressureThreshold);
        }

        public static float GreatChance(float setting) { return setting < 0f ? 0f : setting > 1f ? 1f : setting; }

        // The kind of emergence, given that the hourly MTB roll hit and (when the Great Emergence is allowed and
        // eligible) whether its own chance roll hit.
        public static AmbientKind Escalate(bool greatEnabled, bool eligible, bool greatRollHit)
        {
            return greatEnabled && eligible && greatRollHit ? AmbientKind.Great : AmbientKind.Ordinary;
        }

        public static int PressureAfter(int pressure, AmbientKind kind)
        {
            return kind == AmbientKind.Great ? 0 : pressure + 1;
        }

        // ForceEmergenceNear: one ordinary encounter (+1) and one extra deposit (+1).
        public static int PressureAfterForced(int pressure) { return pressure + 2; }

        // ---- the blocked-until clock ------------------------------------------------------------------
        // now + ticks saturating at int.MaxValue (a wrapped sum would be negative and silently shorten the respite).
        public static int Until(int now, int ticks)
        {
            long u = (long)now + ticks;
            return u > int.MaxValue ? int.MaxValue : u < int.MinValue ? int.MinValue : (int)u;
        }

        // Only ever extends: a shorter respite never cuts a longer one short.
        public static int Extend(int blockedUntil, int until) { return until > blockedUntil ? until : blockedUntil; }

        public static int SuppressionTicks(float days)
        {
            double t = Math.Round(Math.Max(0.1f, days) * TicksPerDay);
            return t >= int.MaxValue ? int.MaxValue : (int)t;
        }

        // ---- the foul-pool job ------------------------------------------------------------------------
        public static int ChargesPerUse(int setting) { return Math.Max(1, setting); }
        public static int ChargesTaken(int stackCount, int setting) { return Math.Min(stackCount, ChargesPerUse(setting)); }
        public static bool TakesAll(int stackCount, int taken) { return taken >= stackCount; }

        // The designator and work giver both gate on the same toggle; the job must not spend charges when it is off.
        public static bool FoulingAllowed(bool suppressionOn) { return suppressionOn; }

        // ---- the pool breathes (DESIGN_PASS FV-1) -------------------------------------------------------
        // A limb that has stood up for its linger time, and is not already withdrawing from damage, sinks back.
        // lingerTicks <= 0 or the toggle off = limbs stay until driven off (the pre-FV-1 behaviour).
        public static bool LingerExpired(bool lingerOn, int spawnTick, int now, int lingerTicks, bool withdrawing)
        {
            if (!lingerOn || lingerTicks <= 0 || withdrawing || spawnTick < 0) return false;
            return (long)now - spawnTick >= lingerTicks;
        }

        // How many of `wanted` new ordinary limbs may rise with `live` already up. cap <= 0 = no cap.
        public static int SpawnBudget(int live, int cap, int wanted)
        {
            if (wanted <= 0) return 0;
            if (cap <= 0) return wanted;
            return Math.Max(0, Math.Min(wanted, cap - Math.Max(0, live)));
        }

        public static int LingerTicks(float hours) { return hours <= 0f ? 0 : (int)Math.Min(int.MaxValue, Math.Round(hours * 2500.0)); }

        // ---- sentinel counter -------------------------------------------------------------------------
        public static int SentinelUp(int count, out bool hush)
        {
            count++;
            hush = count == 1;
            return count;
        }

        public static int SentinelDown(int count, out bool restore)
        {
            int previous = count;
            count = Math.Max(0, count - 1);
            restore = previous > 0 && count == 0;
            return count;
        }
    }
}
