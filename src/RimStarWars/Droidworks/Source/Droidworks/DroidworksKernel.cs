// Droidworks pure kernel: every rule below used to be an inline expression in a comp, recipe, need or Harmony
// postfix, tangled with Verse/Unity calls. They live here so an offline fuzz (Source/SelfTest) can drive the SAME
// code the game runs. NO `using Verse;` / `using UnityEngine;` may ever land in this file: the SelfTest project
// compiles it on plain net8.0 and the build breaks - the guard rail working.
//
// Behaviour is preserved except where a comment marks a fix. Unity's Mathf.RoundToInt/Round are Math.Round
// (banker's rounding), so Math.Round is used for them here.
using System;
using System.Collections.Generic;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_FORMAT_TIERS_1 (packet B1). The four format tiers; the integer values ARE the severity ladder minus one
    /// (severity 1/2/3/4 -> blank/mindless/programmable/sapient; the RSW_DW_FormatTier HediffDef stages cut at 0/1.5/2.5/3.5).
    /// Full rationale: DroidFormatTier.cs (DroidFormatTierUtility).
    /// </summary>
    public enum DroidFormatTier
    {
        Blank = 0,
        Mindless = 1,
        Programmable = 2,
        Sapient = 3
    }

    /// <summary>
    /// The eight chassis families. The integer values ARE DroidworksExtension.chassisClass's documented mapping
    /// ("0 labour 1 protocol 2 astromech 3 battle 4 heavy 5 probe 6 power 7 primitive"). See DroidServiceRecord.cs.
    /// </summary>
    public enum DroidChassis
    {
        Labour = 0,
        Protocol = 1,
        Astromech = 2,
        Battle = 3,
        Heavy = 4,
        Probe = 5,
        Power = 6,
        Primitive = 7
    }

    /// <summary>The six salvage part slots a destroyed droid can shed. Declaration order IS the drop order.</summary>
    [Flags]
    public enum DroidPartSlot
    {
        None = 0,
        Leg = 1,
        Manipulator = 2,
        Sensor = 4,
        Motivator = 8,
        Servo = 16,
        PowerCell = 32
    }

    public enum DriftVerdict
    {
        SettingOff,
        TierTooLow,
        AtCap,
        NotDue,
        Due
    }

    public static class DroidworksKernel
    {
        // ================================================================= format tier ladder

        public const DroidFormatTier DefaultTier = DroidFormatTier.Programmable;

        public static float SeverityFor(DroidFormatTier tier) { return (int)tier + 1f; }

        /// <summary>
        /// Severity -> tier. Clamped in the float domain BEFORE the int conversion: casting a huge or NaN float to int is
        /// undefined (int.MinValue on x86), which used to wrap a very large severity round to Blank. NaN reads as the default.
        /// Halves round AWAY from zero, matching the RSW_DW_FormatTier stage cuts (1.5 / 2.5 / 3.5 are the first severities of
        /// the next stage); Unity's Mathf.RoundToInt rounds to even, which put exactly 2.5 in Mindless although the hediff stage
        /// there is Programmable.
        /// </summary>
        public static DroidFormatTier TierForSeverity(float severity)
        {
            if (float.IsNaN(severity)) return DefaultTier;
            double r = Math.Round((double)severity, MidpointRounding.AwayFromZero);
            if (r < 1.0) r = 1.0;
            if (r > 4.0) r = 4.0;
            return (DroidFormatTier)((int)r - 1);
        }

        /// <summary>Recipe_DWFormatStandard: only ever an upgrade (a sapient is never offered it).</summary>
        public static bool StandardFormatApplicable(DroidFormatTier current) { return current < DroidFormatTier.Programmable; }

        /// <summary>Recipe_DWRestrictiveFormat.</summary>
        public static bool RestrictiveFormatApplicable(DroidFormatTier current) { return current > DroidFormatTier.Mindless; }

        /// <summary>Recipe_DWDeformat.</summary>
        public static bool DeformatApplicable(DroidFormatTier current) { return current > DroidFormatTier.Blank; }

        /// <summary>"Deformat sapient = murder thought": a droid that WAS sapient taken below the programmable rung.</summary>
        public static bool MindDestroyed(DroidFormatTier before, DroidFormatTier target)
        {
            return before == DroidFormatTier.Sapient && target < DroidFormatTier.Programmable;
        }

        /// <summary>
        /// A deformat to Blank is a wipe of the whole programming: the accreted idiosyncrasies go and the drift clock restarts
        /// (DroidServiceRecordUtility's own contract: "any route that wipes or reformats a droid must call NotifyWiped"). Before this
        /// existed a deformatted droid kept its earned personality and its clock and resumed drifting the moment it was reformatted.
        /// </summary>
        public static bool FormatClearsServiceRecord(DroidFormatTier target) { return target == DroidFormatTier.Blank; }

        /// <summary>
        /// Ruling 4: "MINDLESS and BLANK have no needs" - the power bar excepted. A stage's disablesNeeds can only name needs
        /// we know of; on the full list a dozen third-party needs (hygiene, tea, romance, prison labour...) reached mindless and
        /// blank droids (bridge5 2026-10-09). So the rule is "power only", decided per need in Patch_ShouldHaveNeed_Power.
        /// </summary>
        public static bool TierAllowsNeed(DroidFormatTier tier, bool isPowerNeed)
        {
            return isPowerNeed || tier > DroidFormatTier.Mindless;
        }

        /// <summary>A BLANK droid has no programming, so it stands where it is rather than idling about (JobGiver_DWBlankStandby).</summary>
        public static bool TierStandsIdle(DroidFormatTier tier) { return tier == DroidFormatTier.Blank; }

        // ================================================================= service record drift

        /// <summary>Ticks since the last reset; "never set" (negative) and a clock that ran backwards both read 0.</summary>
        public static int TicksSince(int now, int lastResetTick)
        {
            if (lastResetTick < 0) return 0;
            int elapsed = now - lastResetTick;
            return elapsed < 0 ? 0 : elapsed;
        }

        /// <summary>Unwiped ticks needed before the (accreted+1)th idiosyncrasy arrives: first, then one interval each, scaled by the setting.</summary>
        public static long DriftDue(int firstDriftTicks, int driftIntervalTicks, int accreted, float timeScale)
        {
            double d = (firstDriftTicks + (double)accreted * driftIntervalTicks) * (double)timeScale;
            if (double.IsNaN(d) || d <= 0.0) return 0;
            if (d >= 9.0e18) return long.MaxValue;
            return (long)d;
        }

        public static DriftVerdict DriftCheck(bool enabled, DroidFormatTier tier, int accreted, int maxAccreted, long ticksSinceReset, long due)
        {
            if (!enabled) return DriftVerdict.SettingOff;
            if (tier < DroidFormatTier.Programmable) return DriftVerdict.TierTooLow;
            if (accreted >= maxAccreted) return DriftVerdict.AtCap;
            if (ticksSinceReset < due) return DriftVerdict.NotDue;
            return DriftVerdict.Due;
        }

        /// <summary>The first drift also wakes a Programmable droid into a Sapient one (if the race allows it).</summary>
        public static bool PromotesToSapient(int accretedBefore, bool promoteToSapient, DroidFormatTier tier)
        {
            return accretedBefore == 0 && promoteToSapient && tier == DroidFormatTier.Programmable;
        }

        public static float ClampWeight(float w) { return w < 0f ? 0f : w; }

        /// <summary>First entry naming the chassis wins; otherwise the default.</summary>
        public static float ChassisWeight(float defaultWeight, IList<DroidChassis> chassisList, IList<float> weights, DroidChassis chassis)
        {
            if (chassisList != null && weights != null)
            {
                int n = Math.Min(chassisList.Count, weights.Count);
                for (int i = 0; i < n; i++)
                    if (chassisList[i] == chassis) return weights[i];
            }
            return defaultWeight;
        }

        /// <summary>
        /// Weighted pick of an index: roll01 in [0,1). Entries at weight &lt;= 0 (or NaN) are never chosen; -1 when none can be.
        /// Float rounding at the very top of the range falls back to the last positive entry instead of running off the end.
        /// </summary>
        public static int WeightedPick(IList<float> weights, float roll01)
        {
            if (weights == null) return -1;
            double total = 0.0;
            int lastPositive = -1;
            for (int i = 0; i < weights.Count; i++)
            {
                float w = weights[i];
                if (float.IsNaN(w) || w <= 0f) continue;
                total += w;
                lastPositive = i;
            }
            if (lastPositive < 0) return -1;
            double roll = roll01;
            if (double.IsNaN(roll) || roll < 0.0) roll = 0.0;
            double target = roll * total;
            double acc = 0.0;
            for (int i = 0; i < weights.Count; i++)
            {
                float w = weights[i];
                if (float.IsNaN(w) || w <= 0f) continue;
                acc += w;
                if (target < acc) return i;
            }
            return lastPositive;
        }

        // ================================================================= power, charge, resentment

        public const float PoweredDownAt = 0.02f;

        /// <summary>Need_Power.NeedInterval is every 150 ticks: 60000 / 150 = 400 intervals per day.</summary>
        public const float NeedIntervalsPerDay = 400f;

        public static float PowerFallPerInterval(float fallPerDay, float drainRate)
        {
            return fallPerDay * drainRate / NeedIntervalsPerDay;
        }

        public static float PowerAfterFall(float level, float fall) { return Math.Max(0f, level - fall); }

        public static bool ShouldPowerDown(bool powerDownWhenEmpty, float level, bool alreadyPoweredDown)
        {
            return powerDownWhenEmpty && level <= PoweredDownAt && !alreadyPoweredDown;
        }

        /// <summary>CompDWCharger nimbus: fraction of the bar gained per scan (the scan runs every scanIntervalTicks).</summary>
        public static float NimbusGainPerScan(float percentPerHour, float chargeRate, int scanIntervalTicks, int ticksPerHour)
        {
            return percentPerHour * chargeRate / 100f * scanIntervalTicks / ticksPerHour;
        }

        /// <summary>JobDriver_DWRecharge: fraction of the bar gained per tick while docked.</summary>
        public static float DockGainPerTick(float percentPerHour, float chargeRate, int ticksPerHour)
        {
            return percentPerHour * chargeRate / 100f / ticksPerHour;
        }

        /// <summary>The Need setter clamps to its bar; the kernel states the same clamp so a model can follow it.</summary>
        public static float ClampBar(float level) { return level < 0f ? 0f : (level > 1f ? 1f : level); }

        /// <summary>HediffComp_DWBoltResentment: pinned accumulator, capped at the hediff's maxSeverity.</summary>
        public static float ResentmentAfter(float severity, float perDay, float rate, int scanIntervalTicks, int ticksPerDay, float maxSeverity)
        {
            float gain = perDay * rate / ticksPerDay * scanIntervalTicks;
            return Math.Min(maxSeverity, severity + gain);
        }

        // ================================================================= detonation

        /// <summary>A drained wreck never explodes: charge at or under this is "no power".</summary>
        public const float WreckCharge = 0.05f;

        /// <summary>A deliberate deny-your-parts module raises the effective density to at least 1 (never a bypass of the charge guard).</summary>
        public static float EffectiveDensity(float density, bool hasExtension, bool deliberateDenyModule)
        {
            return hasExtension && deliberateDenyModule ? Math.Max(density, 1f) : density;
        }

        /// <summary>The blast scale, or 0 when the droid does not detonate.</summary>
        public static float DetonationScale(float charge, float density, float sizeSetting)
        {
            if (density <= 0f) return 0f;
            if (charge <= WreckCharge) return 0f;
            return charge * density * sizeSetting;
        }

        public static float DetonationRadius(float baseRadius, float scale) { return baseRadius * (float)Math.Sqrt(scale); }

        public const int MaxDetonationDamage = 100000;

        /// <summary>50 damage per unit of scale. Saturates: a float beyond int range used to cast to int.MinValue (a negative blast).</summary>
        public static int DetonationDamage(float scale)
        {
            double d = Math.Round(50.0 * scale);
            if (double.IsNaN(d)) return 0;
            if (d > MaxDetonationDamage) return MaxDetonationDamage;
            if (d < 0.0) return 0;
            return (int)d;
        }

        // ================================================================= data spike

        public static float SpikeSkillFactor(int intellectualLevel) { return 0.5f + 0.05f * intellectualLevel; }

        public static float ResistanceAfterSpike(float resistance, float resistancePerUse, int intellectualLevel)
        {
            return Math.Max(0f, resistance - resistancePerUse * SpikeSkillFactor(intellectualLevel));
        }

        /// <summary>CompDWDataSpike.MatchesFaction over plain values. targetFactionDefName is null when the target has no faction/def.</summary>
        public static bool SpikeMatchesFaction(bool targetNull, bool factionless, bool targetHasFaction, string targetFactionDefName, string spikeFaction)
        {
            if (targetNull) return false;
            if (factionless) return !targetHasFaction;
            if (targetFactionDefName == null || string.IsNullOrEmpty(spikeFaction)) return false;
            return targetFactionDefName == spikeFaction;
        }

        public static bool SpikeValidTarget(bool targetNull, bool dead, bool downed, bool prisoner, bool requiresPrisoner, bool matchesFaction)
        {
            if (targetNull || dead) return false;
            if (!(downed || prisoner)) return false;
            if (requiresPrisoner && !prisoner) return false;
            return matchesFaction;
        }

        // ================================================================= protocol droid trade

        /// <summary>
        /// Net price shift for the player. Player party: +1 with a protocol droid, -1 without. Trader party (only when it can be
        /// inspected): -1 with one, +1 without. Both-or-neither cancels exactly.
        /// </summary>
        public static float TradeAdvantage(bool playerHas, bool traderKnown, bool traderHas, float perSide)
        {
            int net = playerHas ? 1 : -1;
            if (traderKnown) net += traderHas ? -1 : 1;
            return net * perSide;
        }

        public static float BuyPrice(float vanilla, float adv, float minimumBuyPrice)
        {
            if (adv == 0f) return vanilla;
            float r = Math.Max(vanilla * (1f - adv), minimumBuyPrice);
            if (r > 99.5f) r = (float)Math.Round(r);
            return r;
        }

        public static float SellPrice(float vanilla, float adv, float minimumSellPrice)
        {
            if (adv == 0f) return vanilla;
            float r = Math.Max(vanilla * (1f + adv), minimumSellPrice);
            if (r > 99.5f) r = (float)Math.Round(r);
            return r;
        }

        // ================================================================= salvage tables

        /// <summary>
        /// Which part slots a chassis sheds, in drop order. Astromech and probe are small hoverers (no legs or arms), the power
        /// (gonk) hauler has no arms or sensor; unknown classes shed the full set.
        /// </summary>
        public static DroidPartSlot LegalParts(int chassisClass)
        {
            const DroidPartSlot All = DroidPartSlot.Leg | DroidPartSlot.Manipulator | DroidPartSlot.Sensor
                | DroidPartSlot.Motivator | DroidPartSlot.Servo | DroidPartSlot.PowerCell;
            switch (chassisClass)
            {
                case 0: return All & ~DroidPartSlot.Sensor;
                case 1: return All;
                case 2: return DroidPartSlot.Sensor | DroidPartSlot.Motivator | DroidPartSlot.Servo | DroidPartSlot.PowerCell;
                case 3: return All;
                case 4: return All;
                case 5: return DroidPartSlot.Sensor | DroidPartSlot.Motivator | DroidPartSlot.Servo | DroidPartSlot.PowerCell;
                case 6: return DroidPartSlot.Leg | DroidPartSlot.Motivator | DroidPartSlot.Servo | DroidPartSlot.PowerCell;
                case 7: return All;
                default: return All;
            }
        }

        /// <summary>Primitive (7) sheds its own tier of junk, never the fine parts.</summary>
        public static bool UsesPrimitiveParts(int chassisClass) { return chassisClass == 7; }

        /// <summary>Which family's head a chassis class drops; an unknown class drops the labour head.</summary>
        public static DroidChassis HeadChassis(int chassisClass)
        {
            return chassisClass >= 0 && chassisClass <= 7 ? (DroidChassis)chassisClass : DroidChassis.Labour;
        }

        /// <summary>DroidAssembly.BucketedHediff over the QualityCategory ints: 0 inferior (Awful, Poor), 1 standard, 2 superior (Excellent and up).</summary>
        public static int QualityBucket(int qualityCategory)
        {
            if (qualityCategory <= 1) return 0;
            if (qualityCategory >= 4) return 2;
            return 1;
        }
    }
}
