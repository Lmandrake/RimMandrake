using System;

// ABYSS_LIGHTFALL_BROOD_WRECK_1 — the pure rules of the brood lair (System only, no Verse),
// so the offline selftest (Source/BroodSelfTest) compiles THIS file and drives it.
//
// ONE wake meter for both halves (owner, typed 2026-10-01: "get too greedy to steal from the
// crashed ship, and you wake an essentially unkillable thing"). Salvage cuts, the egg and light
// near the sleeper all feed it. Every number here is PROVISIONAL (FOUNDRY's call, item §open).
//
//   threshold   rolled once per lair in [0.85, 1.15] x the "sleep depth" setting and SAVED, so the
//               line is fixed per save and may be learned by save/load (owner: "It's ok to require
//               load/save to learn the boundry").
//   stirring    at 45% of threshold: a message and a low sound.  READABLE SIGN 1
//   rumbling    at 70%: a letter, camera shake.                   READABLE SIGN 2
//   awake       at 100%: she wakes and is essentially unkillable. Never decays back.
//
// The wreck holds 7 parts at 0.12 each (0.84) and the egg is 0.35: a modest haul is safe, the whole
// wreck plus the egg (1.19) is past every possible roll. Pressure decays 0.05/day but never below
// half the peak it reached, so waiting softens greed and never erases it.
namespace RimMandrake.Abyss
{
    public enum BroodStage { Asleep = 0, Stirring = 1, Rumbling = 2, Awake = 3 }

    public class BroodWakeLogic
    {
        public const float StirFraction = 0.45f;
        public const float RumbleFraction = 0.70f;
        public const float ThresholdMin = 0.85f;
        public const float ThresholdMax = 1.15f;
        public const float DecayPerDay = 0.05f;
        public const float DecayFloorOfPeak = 0.5f;
        public const float RearmBelow = 0.8f;   // a stage re-announces only after falling below 80% of its line

        public const float PartWeightDefault = 0.12f;
        public const float EggWeight = 0.35f;
        public const float EggReturnRefund = 0.8f;   // returning the egg takes back 80% of what stealing it cost
        public const float LightPerSourcePerRare = 0.004f;

        public float pressure;
        public float peak;
        public float threshold = 1f;
        public bool stirAnnounced;
        public bool rumbleAnnounced;
        public bool awake;

        /// <summary>Roll the hidden line. <paramref name="unit01"/> is a uniform 0..1 draw.</summary>
        public static float RollThreshold(float unit01, float sleepDepth)
        {
            if (unit01 < 0f) unit01 = 0f;
            if (unit01 > 1f) unit01 = 1f;
            if (sleepDepth < 0.1f) sleepDepth = 0.1f;
            return (ThresholdMin + (ThresholdMax - ThresholdMin) * unit01) * sleepDepth;
        }

        public BroodStage Stage
        {
            get
            {
                if (awake) return BroodStage.Awake;
                if (pressure >= threshold * RumbleFraction) return BroodStage.Rumbling;
                if (pressure >= threshold * StirFraction) return BroodStage.Stirring;
                return BroodStage.Asleep;
            }
        }

        /// <summary>Add (or, negative, remove) pressure. Returns the NEW sign to announce, or Asleep for none.
        /// Awake is returned exactly once, on the crossing.</summary>
        public BroodStage Add(float amount)
        {
            if (awake) return BroodStage.Asleep;
            pressure += amount;
            if (pressure < 0f) pressure = 0f;
            if (pressure > peak) peak = pressure;
            return Evaluate();
        }

        /// <summary>Quiet time passing. Never below half the peak; nothing decays once awake.</summary>
        /// <summary>Returns a sign to announce like Add (a held-back crossing can still complete here).</summary>
        public BroodStage Decay(float days)
        {
            if (awake || days <= 0f) return BroodStage.Asleep;
            float floor = peak * DecayFloorOfPeak;
            pressure -= DecayPerDay * days;
            if (pressure < floor) pressure = floor;
            return Evaluate();
        }

        /// <summary>Called every lair interval: a crossing that was held back for its warning completes here.</summary>
        public BroodStage Recheck()
        {
            return awake ? BroodStage.Asleep : Evaluate();
        }

        private BroodStage Evaluate()
        {
            if (pressure >= threshold)
            {
                // a sign ALWAYS precedes the wake (item criterion 1): one step that jumps from below the rumble
                // straight past the line (the egg is 0.35, the rumble-to-wake gap is as small as 0.255) announces
                // the rumble now and wakes her at the next Recheck, a few seconds later.
                if (!rumbleAnnounced)
                {
                    rumbleAnnounced = true;
                    stirAnnounced = true;
                    return BroodStage.Rumbling;
                }
                awake = true;
                return BroodStage.Awake;
            }
            if (stirAnnounced && pressure < threshold * StirFraction * RearmBelow) stirAnnounced = false;
            if (rumbleAnnounced && pressure < threshold * RumbleFraction * RearmBelow) rumbleAnnounced = false;
            if (!rumbleAnnounced && pressure >= threshold * RumbleFraction)
            {
                rumbleAnnounced = true;
                stirAnnounced = true;   // a rumble subsumes the stir; never announce the lesser sign after the greater
                return BroodStage.Rumbling;
            }
            if (!stirAnnounced && pressure >= threshold * StirFraction)
            {
                stirAnnounced = true;
                return BroodStage.Stirring;
            }
            return BroodStage.Asleep;
        }

        /// <summary>Inspect line on the sleeper. Signs only, never the number (the line is learned, not shown).</summary>
        public string Describe()
        {
            switch (Stage)
            {
                case BroodStage.Awake: return "Awake. Do not fight her. Run.";
                case BroodStage.Rumbling: return "Her breath has changed. A low rumble runs through the stone under her.";
                case BroodStage.Stirring: return "She shifts in her sleep; the throat-sacs flicker.";
                default: return "Deeply asleep.";
            }
        }
    }

    // ── the egg: will it imprint? ─────────────────────────────────────────────
    public enum ImprintResult { Bonded, WildNoBone, WildNotPlayers }

    public static class BroodImprintLogic
    {
        /// <summary>Owner, typed 2026-10-01: "you MUST have one of those great bones on your ship in order for the
        /// beast egg to bond with you. It will not imprint without it present."</summary>
        public static ImprintResult Decide(bool heldByPlayer, bool greatBoneAboardShip, bool boneRequired)
        {
            if (!heldByPlayer) return ImprintResult.WildNotPlayers;
            if (boneRequired && !greatBoneAboardShip) return ImprintResult.WildNoBone;
            return ImprintResult.Bonded;
        }

        public static string WhyNot(ImprintResult r)
        {
            switch (r)
            {
                case ImprintResult.WildNoBone:
                    return "It will not imprint: there is no great bone of its kind aboard your gravship. Without one it will hatch wild.";
                case ImprintResult.WildNotPlayers:
                    return "No one has claimed it. It will hatch wild.";
                default:
                    return "A great bone of its kind stands aboard your ship. It will imprint on you when it hatches.";
            }
        }
    }

    // ── the wreck's parts: does the ship take this one? ───────────────────────
    public enum FitResult { Fits, RefusedForeign, NothingToRestore }

    public static class ShipFitLogic
    {
        /// <summary>Owner, typed 2026-10-01: "their ship only wants certain parts. It likes what it is and doesn't
        /// want deep redesign. Just repair." A refused part says so in plain words; an accepted part with nothing
        /// worn aboard is kept, not wasted.</summary>
        public static FitResult Decide(bool partAccepted, int wornShipBuildings)
        {
            if (!partAccepted) return FitResult.RefusedForeign;
            if (wornShipBuildings <= 0) return FitResult.NothingToRestore;
            return FitResult.Fits;
        }

        public static string Reason(FitResult r)
        {
            switch (r)
            {
                case FitResult.RefusedForeign:
                    return "Your ship will not take this. It likes what it is and refuses the rescue ship's design. Sell it, or melt it down.";
                case FitResult.NothingToRestore:
                    return "Nothing aboard your ship is worn enough to need this yet. Keep it.";
                default:
                    return "Fits your ship. It will restore what has worn.";
            }
        }

        /// <summary>Spread a repair budget over worn buildings, worst-first by missing fraction.
        /// <paramref name="missing"/> is each building's missing HP; returns HP restored per building.</summary>
        public static int[] Spread(int[] missing, int budget)
        {
            int n = missing.Length;
            int[] give = new int[n];
            if (budget <= 0) return give;
            int[] order = new int[n];
            for (int i = 0; i < n; i++) order[i] = i;
            Array.Sort(order, (a, b) => missing[b].CompareTo(missing[a]));
            for (int k = 0; k < n && budget > 0; k++)
            {
                int i = order[k];
                int g = Math.Min(missing[i], budget);
                if (g < 0) g = 0;
                give[i] = g;
                budget -= g;
            }
            return give;
        }
    }

    // ── the bonded beast: bane ─────────────────────────────────────────────────
    public static class SummBaneLogic
    {
        public const float BaseHuntChancePerLong = 0.18f;   // per long tick (~33 s) while fed: semi-random killing
        public const float HungryHuntChance = 0.65f;
        public const float TameTargetShare = 0.15f;          // of victims, how often a tame animal is chosen when one is there

        /// <summary>Does it go killing this long tick? <paramref name="foodLevel"/> is 0..1.</summary>
        public static bool ShouldHunt(float foodLevel, float roll01)
        {
            float chance = foodLevel < 0.3f ? HungryHuntChance : BaseHuntChancePerLong;
            return roll01 < chance;
        }

        /// <summary>Wild first; a tame non-summ animal some of the time when one exists. -1 = none.</summary>
        public static int PickVictimKind(int wildCount, int tameCount, float roll01)
        {
            if (wildCount <= 0 && tameCount <= 0) return -1;
            if (tameCount > 0 && (wildCount == 0 || roll01 < TameTargetShare)) return 1;
            return 0;
        }

        /// <summary>Hunger slider (0.5..3) to the hunger hediff's severity; 1 = shipped.</summary>
        public static float HungerSeverity(float slider)
        {
            if (slider < 0.5f) slider = 0.5f;
            if (slider > 3f) slider = 3f;
            return slider;
        }
    }
}
