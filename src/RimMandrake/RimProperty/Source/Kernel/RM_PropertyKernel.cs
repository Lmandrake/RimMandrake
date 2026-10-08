// RimProperty kernel: the Verse-free rules of the claim fabric - decay, claim ordering, authorization, the event spine's writes,
// suspicion, the foreign-claim wipe, recognizability, every silver fee and price, and how silver comes out of a pawn's stacks.
// The mod calls these with the same expressions it used inline; src/RimMandrake/Utils/selftest_property_fuzz.py compiles THIS file
// (no RimWorld/Unity) and fuzzes it. A `using Verse;` here breaks that build on purpose.
using System;

namespace RimMandrake.Property
{
    public static class RM_PropertyKernel
    {
        // ClaimantKind and TakingAct values, restated so this file needs no other source (the lint pins them to the enums).
        public const byte KindNone = 0, KindPawn = 1, KindCommons = 2;
        public const int ActTake = 0, ActUse = 1, ActStrip = 2, ActSabotage = 3, ActBuy = 4, ActClaim = 5;
        public const int VirtualNone = 0, VirtualSituational = 1, VirtualTerritorial = 2;

        public static float Clamp01(float v) { return v < 0f ? 0f : v > 1f ? 1f : v; }
        public static float Lerp(float a, float b, float t) { return a + (b - a) * Clamp01(t); }

        // ───────────── decay ─────────────
        public static float LifetimeTicks(float recognizability, float minDays, float maxDays, float multiplier, int ticksPerDay)
        {
            recognizability = Clamp01(recognizability);
            float days = Lerp(minDays, maxDays, recognizability);
            days *= multiplier;
            return days * ticksPerDay;
        }

        /// <summary>Linear from the initial strength to zero over the lifetime; a claim not yet born is untouched.</summary>
        public static float EffectiveStrength(float initialStrength, int ageTicks, float lifetime)
        {
            if (ageTicks <= 0) return initialStrength;
            if (ageTicks >= lifetime) return 0f;
            return initialStrength * (1f - ageTicks / lifetime);
        }

        // ───────────── claim resolution ─────────────
        /// <summary>A Pawn claimant outranks a Commons one at equal strength.</summary>
        public static int Specificity(byte kind)
        {
            switch (kind)
            {
                case KindPawn: return 2;
                case KindCommons: return 1;
                default: return 0;
            }
        }

        /// <summary>A recorded claimant whose pawn / faction reference went null after a load would otherwise win every contest unopposed.</summary>
        public static bool IsGhost(byte kind, bool pawnMissing, bool factionMissing)
        {
            return (kind == KindPawn && pawnMissing) || (kind == KindCommons && factionMissing);
        }

        /// <summary>List.Sort comparator: strongest first, then the more specific claimant, then the more recent. Negative = a sorts first.</summary>
        public static int Order(float aStrength, int aSpecificity, int aTimestamp, float bStrength, int bSpecificity, int bTimestamp)
        {
            int byStrength = bStrength.CompareTo(aStrength);
            if (byStrength != 0) return byStrength;
            int bySpecificity = bSpecificity.CompareTo(aSpecificity);
            if (bySpecificity != 0) return bySpecificity;
            return bTimestamp.CompareTo(aTimestamp);
        }

        /// <summary>The virtual claim: whoever possesses the thing (Situational), else the faction that owns it (Territorial).</summary>
        public static int VirtualBasis(bool hasPossessor, bool hasFaction)
        {
            if (hasPossessor) return VirtualSituational;
            if (hasFaction) return VirtualTerritorial;
            return VirtualNone;
        }

        // ───────────── authorization and the spine ─────────────
        /// <summary>The claimant is the actor, or a Commons whose faction the acting pawn belongs to.</summary>
        public static bool ClaimantMayUse(bool claimantEqualsActor, byte claimantKind, byte actorKind, bool sameFaction)
        {
            if (claimantEqualsActor) return true;
            return claimantKind == KindCommons && actorKind == KindPawn && sameFaction;
        }

        /// <summary>Unclaimed is free to take.</summary>
        public static bool IsAuthorized(bool hasPriorClaim, bool claimantMayUse)
        {
            if (!hasPriorClaim) return true;
            return claimantMayUse;
        }

        /// <summary>A completed sale or a paid claim is legitimate by definition.</summary>
        public static bool AuthorizedAfter(int act, bool authorized)
        {
            return act == ActBuy || act == ActClaim ? true : authorized;
        }

        public const int WriteNone = 0, WritePurchased = 1, WriteClaimFeePaid = 2, WriteStolenFromPrior = 3;

        /// <summary>What the spine writes into the ledger. A Take or Strip nobody authorized keeps the PRIOR owner's claim at full strength.</summary>
        public static int SpineWrite(int act, bool authorized, bool hasPriorClaim)
        {
            switch (act)
            {
                case ActBuy: return WritePurchased;
                case ActClaim: return WriteClaimFeePaid;
                case ActTake:
                case ActStrip:
                    return !authorized && hasPriorClaim ? WriteStolenFromPrior : WriteNone;
                default: return WriteNone;
            }
        }

        public static bool RollsPerception(bool authorizedAfter, bool perceptionEnabled)
        {
            return !authorizedAfter && perceptionEnabled;
        }

        /// <summary>Battle loot keeps the defeated owner's origin claim beside the looter's: only when there was an owner.</summary>
        public static bool LootKeepsOrigin(bool originalOwnerUnclaimed) { return !originalOwnerUnclaimed; }

        /// <summary>The wronged owner personally saw it: only a Pawn claimant, and only that very witness.</summary>
        public static bool OwnerWitnessed(bool priorHasPawnOwner, bool witnessIsOwner) { return priorHasPawnOwner && witnessIsOwner; }

        // ───────────── suspicion ─────────────
        public static float DaysElapsed(int nowTick, int timestamp, int ticksPerDay) { return (nowTick - timestamp) / (float)ticksPerDay; }

        public static bool FullyDecayed(float daysElapsed, float halfLifeDays) { return daysElapsed >= halfLifeDays; }

        public static float Propagated(float daysElapsed, float ratePerDay) { return Clamp01(daysElapsed * ratePerDay); }

        public static float Decay(float daysElapsed, float halfLifeDays) { return Clamp01(1f - daysElapsed / halfLifeDays); }

        /// <summary>One witness entry's weight in a faction's suspicion of the suspect: it grows as the story spreads and fades as it ages.</summary>
        public static float Contribution(float confidence, float daysElapsed, float ratePerDay, float halfLifeDays)
        {
            return confidence * Propagated(daysElapsed, ratePerDay) * Decay(daysElapsed, halfLifeDays);
        }

        public static bool KnowsEnough(float contribution, float threshold) { return contribution >= threshold; }

        /// <summary>A bought round reduces what the record already knows: confidence x (1 - fraction); a non-positive fraction changes nothing.</summary>
        public static float Dampened(float confidence, float fraction)
        {
            fraction = Clamp01(fraction);
            if (fraction <= 0f) return confidence;
            return confidence * (1f - fraction);
        }

        // ───────────── the foreign-claim wipe ─────────────
        /// <summary>The colony's own claims survive: the exact claimant, or - when the kept claimant is a faction's Commons - any pawn of that faction.</summary>
        public static bool IsKept(bool claimantEqualsKeep, bool keepIsCommonsOfFaction, byte claimantKind, bool claimantPawnKnown, bool pawnInKeepFaction)
        {
            if (claimantEqualsKeep) return true;
            return keepIsCommonsOfFaction && claimantKind == KindPawn && claimantPawnKnown && pawnInKeepFaction;
        }

        // ───────────── recognizability ─────────────
        public const float Baseline = 0.05f, QualityWeight = 0.30f, MarketValueWeight = 0.25f, NamedWeight = 0.30f, MechanoidWeight = 0.25f,
            NonStackableWeight = 0.05f, MarketValueSaturation = 2000f;
        public const int LegendaryQuality = 6;

        public static float Recognizability(bool hasThing, bool hasQuality, int quality, float marketValue, bool named, bool mechanoid, bool hasDef, int stackLimit)
        {
            if (!hasThing) return 0f;
            float score = Baseline;
            if (hasQuality) score += QualityWeight * ((float)quality / (float)LegendaryQuality);
            if (marketValue > 0f) score += MarketValueWeight * Clamp01(marketValue / MarketValueSaturation);
            if (named) score += NamedWeight;
            if (mechanoid) score += MechanoidWeight;
            if (hasDef && stackLimit <= 1) score += NonStackableWeight;
            return Clamp01(score);
        }

        // ───────────── silver ─────────────
        public static int Round(float v) { return (int)Math.Round(v); }

        public static int ConfiguredFee(float setting) { return Math.Max(1, Round(setting)); }

        public static int Price(float marketValue, int stackCount, float markup)
        {
            float unitValue = Math.Max(0f, marketValue);
            float total = unitValue * Math.Max(1, stackCount) * markup;
            return Math.Max(1, Round(total));
        }

        /// <summary>The salvage claim fee: dearer for a recognizable thing under a strong claim, never below one silver.</summary>
        public static int SalvageFee(float recognizability, bool hasPriorClaim, float priorStrength, float multiplier, int minFee, int maxFee, float unclaimedFloor)
        {
            float recog = Clamp01(recognizability);
            float claimStrength = Clamp01(hasPriorClaim ? priorStrength : 0f);
            float strengthFactor = Lerp(unclaimedFloor, 1f, claimStrength);
            float riskFactor = recog * strengthFactor;
            float fee = Lerp(minFee, maxFee, riskFactor) * multiplier;
            return Math.Max(1, Round(fee));
        }

        /// <summary>Paying needs the whole fee in hand at the moment of paying, not only when the menu was built.</summary>
        public static bool CanPay(int carried, int fee) { return carried >= fee; }

        /// <summary>How much of an amount comes out of each silver stack, in stack order: what is taken from one stack, then the next.</summary>
        public static int TakeFromStack(int remaining, int stackCount) { return Math.Min(remaining, stackCount); }

        public static float ItemValue(float marketValue, int stackCount) { return Math.Max(0f, marketValue) * Math.Max(1, stackCount); }

        /// <summary>A pocket is worth picking: the stack is worth at least the threshold.</summary>
        public static bool WorthStealing(float itemValue, float minValue) { return !(itemValue < minValue); }

        public static bool BeatsBest(float value, float bestValue) { return value > bestValue; }

        // ───────────── animals ─────────────
        public static bool TheftRollPasses(float frequencyMultiplier, float draw)
        {
            return !(frequencyMultiplier < 1f && draw >= frequencyMultiplier);
        }

        public static bool LightEnough(float mass, float maxMass) { return !(mass > maxMass); }
    }
}
