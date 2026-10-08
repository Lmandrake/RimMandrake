// Verse-free kernel of the slimification ladder (HediffComp_Slimification, SlimeUtility, IngestionOutcomeDoer_SlimeDose,
// CompTargetEffect_SlimeAntidote, ChunkBombUtility.Drench, CompUseEffect gene injection): the severity rate with its
// drying-biome / slime-ground / injected-clock priority, the stage thresholds and announce latch, dissolution, the dose,
// the antidote's cure rule, the poison classification and the Slime-marked bookkeeping. The mod calls these with the same
// expressions; SelfTest/GelatinousSlimeFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.GelatinousSlime
{
    public static class RM_SlimeLadder
    {
        // Vanilla's own severity cadence: 200 ticks, scaled by 200/60000.
        public const int CheckIntervalTicks = 200;
        public const float PerDayToPerCheck = 200f / 60000f;
        public const float GrowthPerDayOnSlime = 1f / 7f;          // RULED: ~7 days to dissolution
        public const float GrowthPerDayFastClock = 1f / 3f;        // [INVENTED] the injected clock
        public const float SelfRevertPerDay = 0.5f;
        public const float SelfRevertCeiling = 0.2f;
        public const float SlickedAt = 0.2f, HalfAbsorbedAt = 0.5f, ReturningAt = 0.9f;
        public const float SeverityPerDose = 0.06f, DoseCeiling = 0.99f;
        public const float DrenchSeverity = 0.55f;
        public const float MaxSeverity = 1f;                        // HediffDef maxSeverity: reaching it dissolves

        public static int StageIndex(float severity)
        {
            if (severity >= ReturningAt) return 3;
            if (severity >= HalfAbsorbedAt) return 2;
            if (severity >= SlickedAt) return 1;
            return 0;
        }

        // Severity change per day. Priority: a drying biome leaches wherever the pawn is and on whatever clock; then the
        // body reading you (7 days scaled by the clock setting, 3 on the injected clock); then the injected clock anywhere;
        // then ordinary country (stage 0 wipes off, later stages hold). `grows` off = nothing grows, wipe-off still runs.
        public static float RatePerDay(bool dryingBiome, float decayPerDay, bool grows, float clockDays, bool beingRead, bool fastClock, float severity)
        {
            if (dryingBiome) return -Math.Abs(decayPerDay);
            float clock = 7f / Math.Max(0.5f, clockDays);
            if (beingRead)
            {
                if (!grows) return -SelfRevertPerDay;
                return (fastClock ? GrowthPerDayFastClock : GrowthPerDayOnSlime) * clock;
            }
            if (fastClock) return grows ? GrowthPerDayFastClock * clock : -SelfRevertPerDay;
            if (severity < SelfRevertCeiling) return -SelfRevertPerDay;
            return 0f;
        }

        // One 200-tick check of the comp. announceable = a player-faction humanlike (only they get the letters, and only
        // they advance the announce latch).
        public static void Check(float severity, float ratePerDay, bool announceable, ref int highestAnnounced,
            out bool endHostileState, out bool dissolve, out float adjustment, out int announceStage)
        {
            endHostileState = severity >= HalfAbsorbedAt;
            dissolve = severity >= MaxSeverity;
            adjustment = 0f;
            announceStage = -1;
            if (dissolve) return;
            adjustment = ratePerDay * PerDayToPerCheck;
            if (!announceable) return;
            int stage = StageIndex(severity);
            if (stage <= highestAnnounced) return;
            highestAnnounced = stage;
            announceStage = stage;
        }

        // Dissolution leaves raw slime by body size: clamp(round(size*25), 5, 120).
        public static int DissolveSlime(float bodySize)
        {
            int n = (int)Math.Round(bodySize * 25f, MidpointRounding.AwayFromZero);
            return n < 5 ? 5 : (n > 120 ? 120 : n);
        }

        // ---- resistance ----
        public static bool Resistant(bool noRaceProps, bool isFlesh, bool extension, bool biotechGene)
        {
            if (noRaceProps) return true;
            if (!isFlesh) return true;
            return extension || biotechGene;
        }

        // ---- eating the body ----
        // The fee: +0.06 per portion, never past 0.99 (one dose cannot dissolve you) and NEVER LOWER than you already were.
        public static float DoseSeverity(float severity, int ingestedCount)
        {
            float raised = Math.Min(DoseCeiling, severity + SeverityPerDose * Math.Max(1, ingestedCount));
            return Math.Max(severity, raised);
        }

        public static bool IsPoisonLike(bool isInjuryMissingOrAddiction, bool isBad, bool isToxicOrFoodPoisoning, string defName)
        {
            if (isInjuryMissingOrAddiction) return false;
            if (!isBad) return false;
            if (isToxicOrFoodPoisoning) return true;
            return defName.IndexOf("Toxic", StringComparison.OrdinalIgnoreCase) >= 0
                || defName.IndexOf("Poison", StringComparison.OrdinalIgnoreCase) >= 0
                || defName.IndexOf("Venom", StringComparison.OrdinalIgnoreCase) >= 0
                || defName.IndexOf("Radiation", StringComparison.OrdinalIgnoreCase) >= 0;
        }

        // ---- the antidote ----
        // Clears the hediff at any severity below the last; the toxic cost is paid by every flesh patient regardless.
        public static bool AntidoteCures(bool hasHediff, float severity) { return hasHediff && severity < MaxSeverity; }

        // ---- drench, injection, release ----
        public static float Drench(float severity) { return severity < DrenchSeverity ? DrenchSeverity : severity; }
        public static float InjectedStart(float severity, float start) { return severity < start ? start : severity; }
        public static float ReleasePenalty(float severity) { return Math.Min(1f, severity + 0.15f); }

        // ---- Slime-marked (gene injection) ----
        public static float MarkIncrement(bool reekRider, bool pheromoneCharm)
        {
            float inc = reekRider ? 2f : 1f;
            if (pheromoneCharm) inc = Math.Max(0f, inc - 1f);
            return inc;
        }
        public static int MarkStage(float severity) { return severity >= 4f ? 2 : (severity >= 2f ? 1 : 0); }
    }
}
