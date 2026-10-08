// Verse-free kernel of the bark-warden roost (RM_SweetlineGuardians.cs): the disturbance meter, its stages, forgiveness, refill
// and the double-roost rule. SelfTest/LeaningScrubFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.LeaningScrub
{
    public static class RM_GuardianKernel
    {
        public const float StirringAt = 0.3f;
        public const float RestlessAt = 0.6f;
        public const int TicksPerDay = 60000;
        public const int LongTick = 2000;

        public static int StageOf(float meter)
        {
            if (meter >= 1f) return 3;
            if (meter >= RestlessAt) return 2;
            if (meter >= StirringAt) return 1;
            return 0;
        }

        // AddDisturbance. Returns false (and changes nothing) for a non-positive amount, an unspawned or switched-off roost, or one
        // with no live warden. Otherwise raises the meter (capped at 1), raises the stage and reports `announce` (the new stage, or
        // 0 when the stage did not rise) and `drop` (the meter is full: the wardens drop on the harmer).
        public static bool Add(float meter, int stage, float amount, bool spawned, bool on, int liveWardens, out float newMeter, out int newStage, out int announce, out bool drop)
        {
            newMeter = meter; newStage = stage; announce = 0; drop = false;
            if (amount <= 0f || !spawned || !on || liveWardens == 0) return false;
            newMeter = Math.Min(1f, meter + amount);
            int s = StageOf(newMeter);
            if (s > stage) { newStage = s; announce = s; }
            drop = newMeter >= 1f;
            return true;
        }

        // The long-tick drain while nobody is raging: 1 / forgivenessDays (floored at half a day) per day.
        public static void Forgive(float meter, int stage, float forgivenessDays, bool anyRaging, out float newMeter, out int newStage)
        {
            newMeter = meter; newStage = stage;
            if (anyRaging || meter <= 0f) return;
            float perDay = 1f / Math.Max(0.5f, forgivenessDays);
            newMeter = Math.Max(0f, meter - perDay * ((float)LongTick / TicksPerDay));
            newStage = Math.Min(stage, StageOf(newMeter));
        }

        public static bool ShouldReroost(bool watchful, bool anyRaging, float meter) { return watchful && !anyRaging && meter < StirringAt; }

        public static int Complement(int targetCount, int maxPerTree) { return Math.Min(targetCount, Math.Max(0, maxPerTree)); }

        public static int RefillTick(int now, float days) { return now + (int)(days * TicksPerDay); }

        // The refill tick fires: a warden spawns only into a vacancy and never beside an older roost.
        public static bool RefillSpawns(int liveCount, int complement, bool otherRoostTooClose) { return liveCount < complement && !otherRoostTooClose; }

        // Two roosts within the watch radius would double a visitor's trouble: the later tree (higher thing id) stays empty.
        public static bool YieldsToOther(int dx, int dz, float watchRadius, int otherId, int myId)
        {
            return (float)dx * dx + (float)dz * dz <= watchRadius * watchRadius && otherId < myId;
        }
    }
}
