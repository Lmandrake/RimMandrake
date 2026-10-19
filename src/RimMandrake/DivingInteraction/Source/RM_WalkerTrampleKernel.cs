namespace RimMandrake.DivingInteraction
{
    /// <summary>
    /// SCALD_WALKING_PASTURE_1, trample half. Owner ruled by question card 2026-10-09: "a walker that gets too close
    /// tramples the colonist and deals damage (not push-aside). A warning to the player is owed with it."
    ///
    /// The per-pawn decision, with no Verse or UnityEngine type in it, so the offline fuzz (Source/SelfTest/DivingFuzz.cs,
    /// `python3 src/RimMandrake/Utils/selftest_divinginteraction_fuzz.py`) compiles THIS file and drives the code the game
    /// runs. RM_MapComponent_ScaldWalkerGrazing measures distances and plays what this returns. A `using Verse;` landing
    /// here breaks the selftest build.
    ///
    /// Only a MOVING walker tramples: a grazing walker stands still and the crew works beside it (the gather job already
    /// keeps 3.5 cells off). A downed pawn is stepped over, not trampled again — PROVISIONAL, live tuning owed.
    /// </summary>
    public static class RM_WalkerTrampleKernel
    {
        public const int SweepInterval = 60;              // ~1 s: a pawn walking past a moving herd is not missed
        public const float TrampleRadius = 1.5f;          // adjacent, diagonals included
        public const float WarnRadius = 5f;
        public const int TrampleCooldownTicks = 600;      // per pawn: one trample per ~10 s of contact
        public const int WarnCooldownTicks = 2500;        // per pawn: one warning per in-game hour
        public const float DefaultDamage = 8f;            // PROVISIONAL first guess (owner 2026-10-03: first guesses ship, tuned live)
        public const float MinDamage = 1f;
        public const float MaxDamage = 30f;

        public enum Outcome { None, Warn, Trample }

        /// <summary>
        /// One pawn, one sweep. <paramref name="nearestMovingWalkerDistSq"/> is the squared horizontal distance to the
        /// nearest living, moving walker (float.PositiveInfinity when none). Last-tick arguments are -1 when never.
        /// </summary>
        public static Outcome Decide(float nearestMovingWalkerDistSq, bool pawnDowned, int now,
                                     int lastTrampleTick, int lastWarnTick,
                                     bool trampleEnabled, bool warnEnabled)
        {
            if (float.IsNaN(nearestMovingWalkerDistSq) || nearestMovingWalkerDistSq < 0f)
            {
                return Outcome.None;
            }
            if (trampleEnabled && !pawnDowned && nearestMovingWalkerDistSq <= TrampleRadius * TrampleRadius
                && (lastTrampleTick < 0 || now - lastTrampleTick >= TrampleCooldownTicks))
            {
                return Outcome.Trample;
            }
            if (trampleEnabled && warnEnabled && !pawnDowned && nearestMovingWalkerDistSq <= WarnRadius * WarnRadius
                && (lastWarnTick < 0 || now - lastWarnTick >= WarnCooldownTicks))
            {
                return Outcome.Warn;
            }
            return Outcome.None;
        }

        /// <summary>The setting clamped to its slider range; NaN or infinity falls back to the shipped default.</summary>
        public static float Damage(float setting)
        {
            if (float.IsNaN(setting) || float.IsInfinity(setting))
            {
                return DefaultDamage;
            }
            return setting < MinDamage ? MinDamage : (setting > MaxDamage ? MaxDamage : setting);
        }
    }
}
