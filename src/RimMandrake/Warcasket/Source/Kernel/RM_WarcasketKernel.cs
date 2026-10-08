// Warcasket kernel: the Verse-free decisions of the compound-failure roll, the hazardous-terrain clock, the half-extracted core's dose,
// the cask bay's shielding gates and the sarcophagus seal / crack salvage. The mod calls these with the same expressions it used
// inline; src/RimMandrake/Utils/selftest_warcasket_fuzz.py compiles THIS file (no RimWorld/Unity) and fuzzes it.
// A `using Verse;` here breaks that build on purpose.
using System;

namespace RimMandrake.Warcasket
{
    public static class RM_WarcasketKernel
    {
        // ───────────── shared ─────────────
        public static float Clamp01(float v) { return v < 0f ? 0f : v > 1f ? 1f : v; }

        /// <summary>UnityEngine.Mathf.Lerp (t clamped to 0..1).</summary>
        public static float Lerp(float a, float b, float t) { return a + (b - a) * Clamp01(t); }

        /// <summary>Verse.Rand.Chance with the draw passed in.</summary>
        public static bool Chance(float p, float u)
        {
            if (p >= 1f) return true;
            if (p <= 0f) return false;
            return u < p;
        }

        // ───────────── compound failure ─────────────
        public const float DamagedFailureFactor = 1.6f;

        /// <summary>The mechanic runs only with the master switch and the compound-failure switch both on.</summary>
        public static bool FailureActive(bool master, bool compound) { return master && compound; }

        public static bool VacuumHazard(float roomVacuum, float threshold) { return roomVacuum > threshold; }

        public static bool TemperatureHazard(float ambient, float coldThreshold, float heatThreshold)
        {
            return ambient <= coldThreshold || ambient >= heatThreshold;
        }

        public static bool ToxinHazard(bool toxicGround, bool toxicFallout) { return toxicGround || toxicFallout; }

        public static int HazardCount(bool vacuum, bool temperature, bool toxin)
        {
            int n = 0;
            if (vacuum) n++;
            if (temperature) n++;
            if (toxin) n++;
            return n;
        }

        /// <summary>One hazard alone is exactly what the suit is built to shrug off: only a stack of two or more can fail it.</summary>
        public static bool CanFail(int hazards) { return hazards >= 2; }

        /// <summary>Chance per check once two or more hazards stack: the base for two, one extra step per hazard beyond, up to 1.6x for a
        /// wrecked suit, clamped to a probability.</summary>
        public static float FailureChance(int hazards, float baseChance, float perExtraHazard, int hitPoints, int maxHitPoints)
        {
            float chance = baseChance + perExtraHazard * (hazards - 2);
            int maxHp = maxHitPoints > 0 ? maxHitPoints : 1;
            float hpFrac = Clamp01((float)hitPoints / maxHp);
            chance *= Lerp(DamagedFailureFactor, 1f, hpFrac);
            return Clamp01(chance);
        }

        public static int FailureDamageMax(int hazards) { return hazards * 4; }

        /// <summary>A failure damages the suit but never destroys it: a wearer stranded suitless inside a compound hazard is worse.</summary>
        public static int HitPointsAfterFailure(int hitPoints, int integrityDamage, int extraRoll)
        {
            int dmg = integrityDamage + extraRoll;
            return Math.Max(1, hitPoints - dmg);
        }

        public static float BreachSeverity(float perFailure, int hazards) { return perFailure * hazards; }

        // ───────────── hazardous terrain clock ─────────────
        public const int ImmersionCheckInterval = 250;
        public const float GainPerCheckUnprotected = 0.12f;
        public const float HealPerCheckClear = -0.35f;
        public const float HealPerCheckProtected = -0.1f;
        public const float MinDriveFactor = 0.05f;

        public static bool ImmersionActive(bool master, bool immersion) { return master && immersion; }

        /// <summary>The map component's countdown: true on the check tick, then re-armed.</summary>
        public static bool CheckDue(ref int ticksUntilCheck)
        {
            if (--ticksUntilCheck > 0) return false;
            ticksUntilCheck = ImmersionCheckInterval;
            return true;
        }

        /// <summary>Water too deep to walk through: a ford or shallow margin (walkable) is ordinary ground.</summary>
        public static bool HazardousCell(bool inBounds, bool terrainKnown, bool isWater, bool affordancesKnown, bool walkable)
        {
            if (!inBounds) return false;
            if (!terrainKnown || !isWater) return false;
            return !affordancesKnown || !walkable;
        }

        /// <summary>The severity change for one check: clear ground heals fast, gear that holds the clock heals slowly, otherwise the
        /// clock gains in proportion to the drive factor (1 - protection, floored). Zero means leave the hediff alone.</summary>
        public static float ImmersionDelta(bool hazardous, bool hasHediff, float driveFactor)
        {
            if (!hazardous) return hasHediff ? HealPerCheckClear : 0f;
            if (driveFactor <= 0f) return hasHediff ? HealPerCheckProtected : 0f;
            return GainPerCheckUnprotected * driveFactor;
        }

        // ───────────── half-extracted core ─────────────
        public const int RaresPerDose = 4;

        /// <summary>The core doses on every fourth rare tick.</summary>
        public static bool DoseDue(ref int rareCount)
        {
            if (++rareCount < RaresPerDose) return false;
            rareCount = 0;
            return true;
        }

        public static bool DoseActive(bool master, bool coreDose) { return master && coreDose; }

        /// <summary>Per-dose scale that makes the rate match vanilla's per-CheckInterval figure however often the core doses.</summary>
        public static float RateScale(int tickRareInterval, int checkInterval)
        {
            return (float)(tickRareInterval * RaresPerDose) / checkInterval;
        }

        public static bool InRadius(float distance, float radius) { return !(distance > radius); }

        /// <summary>Falls linearly with distance; still positive at the radius itself and reaches zero one cell beyond it.</summary>
        public static float Falloff(float distance, float radius) { return 1f - distance / (radius + 1f); }

        public static float Dose(float toxicFactor, float falloff, float rateScale) { return toxicFactor * falloff * rateScale; }

        // ───────────── cask bay shielding ─────────────
        public static bool ShieldingActive(bool master, bool bayShielding) { return master && bayShielding; }

        /// <summary>The bay holds each stored cask's dissolve clock at zero, every rare tick, while shielding is active.</summary>
        public static bool HoldsClock(bool shieldingActive, bool spawned, bool fieldFound)
        {
            return shieldingActive && spawned && fieldFound;
        }

        /// <summary>A thing is shielded when shielding is active, it is spawned on a map, and a bay shares its cell.</summary>
        public static bool IsShielded(bool shieldingActive, bool thingKnown, bool hasMap, bool spawned, bool bayOnCell)
        {
            if (!shieldingActive || !thingKnown) return false;
            if (!hasMap || !spawned) return false;
            return bayOnCell;
        }

        // ───────────── sarcophagus ─────────────
        /// <summary>The suit locks onto its wearer at death only with both switches on, and only for a sarcophagus suit.</summary>
        public static bool SealsOnDeath(bool master, bool sarcophagi, bool isSarcophagusSuit)
        {
            return master && sarcophagi && isSarcophagusSuit;
        }

        /// <summary>The crack-open option is offered on a corpse wearing a sarcophagus suit while both switches are on.</summary>
        public static bool OffersCrack(bool master, bool sarcophagi, bool isCorpse, bool hasSuit)
        {
            return master && sarcophagi && isCorpse && hasSuit;
        }

        public static bool ExtensionApplies(bool hasExtension, bool isSealed) { return hasExtension && isSealed; }

        /// <summary>One salvage row spawns when it names a def and a positive count.</summary>
        public static bool SalvageRowWanted(bool defKnown, int count) { return defKnown && count > 0; }

        /// <summary>The next stack to place from a salvage row: never more than the def's stack limit, and never zero (a limit below one
        /// would otherwise loop forever placing nothing).</summary>
        public static int NextSalvageStack(int left, int stackLimit)
        {
            return Math.Min(left, Math.Max(1, stackLimit));
        }

        public static int CrackTicks(bool hasTicks, int ticks) { return hasTicks ? ticks : 1200; }
    }
}
