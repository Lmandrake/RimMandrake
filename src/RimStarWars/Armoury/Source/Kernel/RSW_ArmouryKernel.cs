// Pure decision kernels of Jawa Armoury (mandrake.rsw.armoury): no Verse, no RimWorld, no UnityEngine (the offline fuzz in
// Source/SelfTest compiles this file on plain net8.0; a `using Verse;` here breaks that build on purpose). The mod's
// DamageWorkers, Harmony postfixes, comps and job givers call these with the same expressions they used inline, and keep
// only the engine half (stat reads, hediff creation, defs, messages).
using System;
using System.Collections.Generic;

namespace RimMandrake.StarWars.Armoury
{
    /// <summary>Rounding and clamps shared by the settings-derived numbers (Mathf.RoundToInt is Math.Round, ties to even).</summary>
    public static class RSW_Num
    {
        public static int RoundToInt(float f) { return (int)Math.Round(f); }
    }

    /// <summary>Ion / stun damage: what a hit adds to a pawn (guy762_Ionization and guy762_IonizationABF workers).</summary>
    public static class RSW_IonKernel
    {
        public struct Plan
        {
            public bool Gate;        // the mechanic is on, the damage def carries the extension and it names a hediff
            public bool Applies;     // Gate and the victim is the kind this worker targets
            public float Severity;   // severity per hediff (<= 0: no hediff)
            public int Hediffs;      // how many hediffs get added
            public bool Stun;        // the hit also stuns
        }

        /// <summary>The hediff severity: fixed x global strength, then the resistance stat (a stat whose default is positive multiplies,
        /// otherwise it is a 0..1 fraction resisted), then divided by body size. Body size 0 or less does not divide.</summary>
        public static float Severity(float severityFixed, float strength, bool hasResistStat, float resistDefaultBase, float resistStatValue,
                                     bool variesBySize, float bodySize)
        {
            float severity = severityFixed * strength;
            if (hasResistStat)
            {
                severity = resistDefaultBase > 0f ? severity * resistStatValue : severity * (1f - resistStatValue);
            }
            if (severity > 0f && variesBySize && bodySize > 0f)
            {
                severity /= bodySize;
            }
            return severity;
        }

        /// <summary>Everything one hit does. stunWhenApplies is the worker kind: Ionization and Ionize stun an applicable victim,
        /// the plain race workers and AllDroids do not. The resistance stat is read only for an applicable victim of a mechanic that is on.</summary>
        public static Plan Decide(bool enabled, bool hasExtension, bool namesHediff, bool victimApplies, bool stunWhenApplies,
                                  float severityFixed, float strength, bool hasResistStat, float resistDefaultBase, Func<float> resistStatValue,
                                  bool variesBySize, float bodySize, bool wholeBody, int partCount)
        {
            Plan p = new Plan();
            p.Gate = enabled && hasExtension && namesHediff;
            p.Applies = p.Gate && victimApplies;
            if (!p.Applies) return p;
            p.Severity = Severity(severityFixed, strength, hasResistStat, resistDefaultBase, hasResistStat ? resistStatValue() : 0f, variesBySize, bodySize);
            if (p.Severity > 0f) p.Hediffs = wholeBody ? 1 : Math.Max(0, partCount);
            p.Stun = stunWhenApplies;
            return p;
        }

        /// <summary>DamageWorker_OrganicStun: a flesh victim is stunned while the mechanic is on.</summary>
        public static bool OrganicStun(bool enabled, bool isFlesh) { return enabled && isFlesh; }

        /// <summary>Plasma grenade: fires only with the setting on.</summary>
        public static bool PlasmaFires(bool setting, bool defFlagWantsFire) { return setting && defFlagWantsFire; }
    }

    /// <summary>Bonus mining yield (SecondaryMineableYield).</summary>
    public static class RSW_YieldKernel
    {
        /// <summary>The bonus drop fires when the roll (0..1, both ends possible) does not exceed chance x global chance; a chance of 0
        /// (the slider's low end) never fires, even on a roll of exactly 0.</summary>
        public static bool Drops(float roll, float dropChance, float chanceScale) { float p = dropChance * chanceScale; return p > 0f && roll <= p; }

        /// <summary>Weighted pick: roll01 in [0,1] scaled onto the weight sum; the entry whose cumulative weight first exceeds the scaled
        /// roll wins. Zero-weight entries never win; a roll at the very top lands on the last entry that has weight. -1 only when no
        /// entry has weight.</summary>
        public static int Pick(IList<float> weights, float roll01)
        {
            float sum = 0f;
            for (int i = 0; i < weights.Count; i++) sum += Math.Max(0f, weights[i]);
            if (!(sum > 0f)) return -1;
            float roll = Math.Min(Math.Max(roll01, 0f), 1f) * sum;
            float cum = 0f;
            int lastPositive = -1;
            for (int i = 0; i < weights.Count; i++)
            {
                float w = Math.Max(0f, weights[i]);
                if (w <= 0f) continue;
                lastPositive = i;
                cum += w;
                if (roll < cum) return i;
            }
            return lastPositive;
        }

        /// <summary>Items in the bonus stack: the entry's yield (already difficulty-scaled) x the size slider, at least 1; a wasteable
        /// yield is further scaled by the mineable's yield fraction with random rounding, still at least 1.</summary>
        public static int Count(int effectiveYield, float amountScale, bool wasteable, float yieldPct, Func<float, int> roundRandom)
        {
            int count = Math.Max(1, RSW_Num.RoundToInt(effectiveYield * amountScale));
            if (wasteable) count = Math.Max(1, roundRandom(count * yieldPct));
            return count;
        }

        /// <summary>The mining-damage postfix credits the miner only for an unabsorbed mining hit on a mineable with no yield of its own.</summary>
        public static bool CreditsMiner(bool enabled, bool absorbed, bool mineableHasOwnYield, bool damageIsMining, bool instigatorIsPawn, bool hasEntries)
        {
            return enabled && !absorbed && !mineableHasOwnYield && damageIsMining && instigatorIsPawn && hasEntries;
        }
    }

    /// <summary>Gear that buffs its wearer: the use cooldown (SelfHediffVerb) and the mental-break blocker.</summary>
    public static class RSW_GearKernel
    {
        public const int Idle = -1;

        public static bool CanUse(int remainTicks) { return remainTicks < 0; }
        public static int Tick(int remainTicks) { return remainTicks >= 0 ? remainTicks - 1 : remainTicks; }
        public static int AfterUse(int cooldownTicks, float cooldownScale) { return Math.Max(0, RSW_Num.RoundToInt(cooldownTicks * cooldownScale)); }

        /// <summary>Cause bits: 1 mood, 2 damage, 4 psycast (BlockMentalBreakCause). Blacklist (default): blocked when the break's
        /// cause intersects the listed causes; whitelist: blocked when it does NOT.</summary>
        public static bool IsBlocked(int causeBits, bool isWhitelist, bool byMood, bool byDamage, bool byPsycast)
        {
            int b = (byMood ? 1 : 0) | (byDamage ? 2 : 0) | (byPsycast ? 4 : 0);
            return (causeBits & b) > 0 ^ isWhitelist;
        }
    }

    /// <summary>Kolto tank: what it heals, how fast it fills, when it heals and when it ejects.</summary>
    public static class RSW_KoltoKernel
    {
        public const int Empty = 0, StartFilling = 1, Full = 2;
        public const int BaseTicksBetweenHealing = 2500;

        public static bool WillHeal(bool hasDef, bool everCurableByItem, bool countsAsImplant, bool chronic, bool isBloodLoss, bool isInjury, bool injuryPermanent)
        {
            if (!hasDef) return false;
            if (!everCurableByItem || countsAsImplant) return false;
            if (chronic || isBloodLoss) return true;
            return isInjury && !injuryPermanent;
        }

        /// <summary>Ticks between two heals: 2500 x the def's multiplier when that is positive, else the plain hour.</summary>
        public static int TicksBetweenHealing(float multiplier) { return multiplier > 0f ? RSW_Num.RoundToInt(BaseTicksBetweenHealing * multiplier) : BaseTicksBetweenHealing; }

        /// <summary>The heal interval at the current speed slider (never below one tick; a slider under 0.01 acts as 0.01).</summary>
        public static int HealInterval(int shippedTicks, float speed) { return Math.Max(1, RSW_Num.RoundToInt(shippedTicks / Math.Max(0.01f, speed))); }

        public static bool HealDue(bool enabled, int ticksGame, int interval, bool hasPawn) { return enabled && ticksGame % interval == 0 && hasPawn; }

        public enum Outcome { None, Eject }

        /// <summary>One occupied tick: no fuel or no power ejects; otherwise a filling tank fills by its speed and becomes full at 1.</summary>
        public static Outcome Step(ref int state, ref float fillPct, float fillSpeed, bool hasFuel, bool hasPower)
        {
            if (!hasFuel || !hasPower) return Outcome.Eject;
            if (state == StartFilling)
            {
                fillPct += fillSpeed;
                if (fillPct >= 1f) { fillPct = 1f; state = Full; }
            }
            return Outcome.None;
        }

        /// <summary>Power state from the power trader, else the plain power comp, else assumed on.</summary>
        public static bool HasPower(bool hasTrader, bool traderOn, bool hasPowerComp, bool transmitsNow)
        {
            if (hasTrader) return traderOn;
            if (hasPowerComp) return transmitsNow;
            return true;
        }

        /// <summary>A tank fits a pawn whose body size is within its band, both ends inclusive.</summary>
        public static bool Fits(float bodySize, float min, float max) { return bodySize <= max && bodySize >= min; }
    }

    /// <summary>Hostile jumppack AI, the emergency-healing job giver, mine defusing and the settings numbers they read.</summary>
    public static class RSW_CombatKernel
    {
        public const float MeleeJumpMinDistSq = 25f, PatchMeleeJumpMinDistSq = 16f, CoverWorthFlanking = 0.3f;
        public const float DefuseManipulationFloor = 0.6f;
        public const int DefuseBaseTicks = 60;
        public const float TicksPerHour = 2500f;

        public static float ScaleSquaredDistance(float shippedSquared, float distanceFactor) { return shippedSquared * distanceFactor * distanceFactor; }
        public static int HoursToTicks(float hours, int min) { return Math.Max(min, RSW_Num.RoundToInt(hours * TicksPerHour)); }
        public static int InstantHealReuseTicks(float hours) { return HoursToTicks(hours, 0); }
        public static int InstantHealRecentHarmTicks(float hours) { return HoursToTicks(hours, 1); }
        public static int DefuseTicks(int baseTicks, float timeScale) { return Math.Max(1, RSW_Num.RoundToInt(baseTicks * timeScale)); }

        public enum Jump { None, Melee, Ranged }

        /// <summary>The melee jump gate (JobGiver_AIMeleeJumppack and the fight-enemy postfix): lazy probes, original order. The jumper must
        /// be a non-colonist humanlike, with a target it cannot already touch, farther than the scaled squared distance, and own a jump verb
        /// that can hit the target.</summary>
        public static bool MeleeJump(bool enabled, bool humanlike, bool colonist, Func<bool> hasTarget, Func<bool> meleeVerb, Func<bool> canReachNow,
                                     Func<float> distSq, float shippedSquared, float distanceFactor, Func<bool> hasJumpVerb)
        {
            if (!enabled) return false;
            if (!humanlike || colonist) return false;
            if (!hasTarget()) return false;
            if (!meleeVerb()) return false;
            if (canReachNow()) return false;
            if (distSq() < ScaleSquaredDistance(shippedSquared, distanceFactor)) return false;
            return hasJumpVerb();
        }

        /// <summary>Flank jump over cover: needs both settings, a non-colonist humanlike, and some cover worth hiding behind.</summary>
        public static bool FlankWorthIt(bool enabled, bool flankSetting, bool humanlike, bool colonist, IList<float> coverBlockChances)
        {
            if (!enabled || !flankSetting) return false;
            if (!humanlike || colonist) return false;
            if (coverBlockChances == null || coverBlockChances.Count == 0) return false;
            for (int i = 0; i < coverBlockChances.Count; i++) if (!(coverBlockChances[i] < CoverWorthFlanking)) return true;
            return false;
        }

        /// <summary>Flank landing: behind the target first, then in front; -1 none, 0 behind, 1 in front.</summary>
        public static int FlankSpot(bool behindReachable, bool frontReachable) { return behindReachable ? 0 : frontReachable ? 1 : -1; }

        /// <summary>Emergency healing (postfix of the combat-drug giver): only when the vanilla giver found nothing, the harm is recent and
        /// the last use is old enough. Ticks are compared as the engine does.</summary>
        public static bool InstantHealDue(bool enabled, bool vanillaGaveJob, bool plumbingOk, int ticksGame, int lastHarmTick, int recentHarmTicks, int lastDrugTick, int reuseTicks)
        {
            if (!enabled || vanillaGaveJob || !plumbingOk) return false;
            if (ticksGame - lastHarmTick > recentHarmTicks) return false;
            if (ticksGame - lastDrugTick < reuseTicks) return false;
            return true;
        }

        /// <summary>The prefix forces "only if in danger" for a pawn carrying instant-heal drugs (mechanic on).</summary>
        public static bool ForceOnlyInDanger(bool enabled, bool carriesInstantHealDrug, bool original) { return enabled && carriesInstantHealDrug ? true : original; }

        public struct Defuse { public bool Wick, Spawn, Destroy; }

        /// <summary>Defusing a mine: a clumsy hand (manipulation under the floor) lights the wick and leaves the mine standing; a steady
        /// hand recovers the parts and removes the mine.</summary>
        public static Defuse DefuseOutcome(float manipulation)
        {
            Defuse d = new Defuse();
            if (manipulation < DefuseManipulationFloor) d.Wick = true;
            else { d.Spawn = true; d.Destroy = true; }
            return d;
        }
    }
}
