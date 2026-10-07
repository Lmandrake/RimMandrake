// Verse-free kernel of the old-line projector rings (RM_CompWarscarRing): the condition roll, liveness, the wake
// test and the evaluate / salvage / repair state transitions. RM_WarscarRings.cs and RM_WarscarSalvage.cs call these;
// SelfTest/ScarlandsFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
namespace RimMandrake.Scarlands
{
    public enum RingCondition { Dead = 0, Failing = 1, Working = 2 }

    public enum SalvageResult { Strip = 0, Uninstall = 1 }

    public static class RM_RingKernel
    {
        public const float WakeRange = 40f;
        public const float WorkingChance = 0.7f;
        public const float LiveSpawnChance = 0.4f;

        // Live def: Rand.Chance(0.7) -> Working else Failing. (Rand.Chance(c) is Value < c for 0 < c < 1.)
        public static int RollLive(float value) { return (int)(value < WorkingChance ? RingCondition.Working : RingCondition.Failing); }

        // The saved field is -1 until rolled; the property reads it clamped to Dead.
        public static RingCondition Effective(int cond) { return (RingCondition)(cond < 0 ? 0 : cond); }

        // The genstep forces the first ring of a map to be a live one and Working; later rings 40% live.
        public static bool FirstLiveForcedWorking(int index, bool isLiveDef) { return index == 0 && isLiveDef; }

        public static bool IsScreenLive(bool dead, bool baseLive, RingCondition cond, bool shipWakesLine, bool wakeCached, bool spawned)
        {
            if (!dead) return baseLive && cond == RingCondition.Working;
            return shipWakesLine && wakeCached && spawned;
        }

        public static bool EngineWakes(int engineX, int engineZ, int ringX, int ringZ)
        {
            int dx = engineX - ringX;
            int dz = engineZ - ringZ;
            return dx * dx + dz * dz <= WakeRange * WakeRange;
        }

        // ---- who may do what -------------------------------------------------------------------
        public static bool CanEvaluate(bool evaluated) { return !evaluated; }
        public static bool CanSalvage(bool evaluated, bool wild) { return evaluated && wild; }
        // The player-installed salvaged ring that is Failing; wild rings are never repaired in place.
        public static bool CanRepair(bool wild, RingCondition cond) { return !wild && cond == RingCondition.Failing; }

        // ---- transitions -----------------------------------------------------------------------
        // Dead is stripped for parts; working/failing is taken up as the salvaged ring carrying the same condition,
        // already evaluated (the player knows what they are hauling).
        public static SalvageResult Salvage(RingCondition cond) { return cond == RingCondition.Dead ? SalvageResult.Strip : SalvageResult.Uninstall; }
        public static RingCondition SalvagedCondition(RingCondition cond) { return cond; }
        public static RingCondition Repaired() { return RingCondition.Working; }
    }
}
