// Verse-free kernel of the titanoslime (RM_CompEngulfer): the mass ladder with hysteresis, the growth / reversibility
// gates, decay, the engulf gate and capacity, digestion time, struggle and burst-out, shedding, the starting-mass roll.
// SelfTest/GelatinousSlimeFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.GelatinousSlime
{
    public static class RM_TitanKernel
    {
        public static float Clamp(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

        // Highest reachable stage index: the declared ladder, lowered (never raised) by the settings slider (1..declared+1).
        public static int MaxStageIndex(int declaredThresholds, int settingMaxStage)
        {
            int fromSettings = (int)Clamp(settingMaxStage, 1, declaredThresholds + 1) - 1;
            return Math.Min(declaredThresholds, fromSettings);
        }

        // Stage for a mass, starting from the current stage so the hysteresis band has something to hold onto.
        public static int StageFor(float mass, int current, IList<float> up, float hysteresis, int maxIndex)
        {
            int stage = (int)Clamp(current, 0, up.Count);
            while (stage < maxIndex && mass >= up[stage]) stage++;
            while (stage > 0 && mass < up[stage - 1] - hysteresis) stage--;
            return Math.Min(stage, maxIndex);
        }

        // Every mass change goes through here. A growth toggle off freezes everything; a loss needs reversibility.
        public static bool TryAddMass(ref float mass, float delta, bool grows, bool reversible, float cap)
        {
            if (!grows) return false;
            if (delta < 0f && !reversible) return false;
            mass = Clamp(mass + delta, 0f, cap);
            return true;
        }

        // Announce a stage only when it is higher than any announced and above the first; a drop re-arms the latch.
        public static bool Announce(int target, ref int highestAnnounced, bool spawned, bool wanted)
        {
            bool say = wanted && target > highestAnnounced && target > 0 && spawned;
            if (say) highestAnnounced = target;
            if (target < highestAnnounced) highestAnnounced = target;
            return say;
        }

        public static int Capacity(float bodySize, float bodySizePerHeldThing) { return Math.Max(1, (int)Math.Floor(bodySize / bodySizePerHeldThing)); }

        public static bool CanEngulf(bool engulfsOn, bool selfSpawned, bool selfDead, bool selfDowned, bool preySpawned, bool preyDead, bool preyFlesh,
            bool samePawn, float preyBody, float selfBody, float preyFraction, int held, int capacity, bool preyAlreadyHeld, bool sameDef)
        {
            if (!engulfsOn) return false;
            if (samePawn || !selfSpawned || selfDead || selfDowned) return false;
            if (!preySpawned || preyDead) return false;
            if (!preyFlesh) return false;
            if (preyBody > selfBody * preyFraction) return false;
            if (held >= capacity) return false;
            if (preyAlreadyHeld) return false;
            if (sameDef && preyBody >= selfBody) return false;
            return true;
        }

        public static int DigestTicks(float seconds) { return Math.Max(60, (int)Math.Ceiling(seconds * 60f)); }

        // One decay interval: the off-slime clock resets on slime and grows off it; mass loss from starving, and from a
        // full day away from slime. Returns the loss (applied through TryAddMass, so it is dropped unless reversible).
        public static float DecayLoss(ref int ticksOffSlime, bool onSlime, int interval, bool starving, float lostPerDayStarving, float lostPerDayDry)
        {
            if (onSlime) ticksOffSlime = 0; else ticksOffSlime += interval;
            float per = interval / 60000f, loss = 0f;
            if (starving) loss += lostPerDayStarving * per;
            if (ticksOffSlime >= 60000) loss += lostPerDayDry * per;
            return loss;
        }

        public static float StruggleDamage(bool humanlike, int meleeLevel, float heldBody) { return humanlike ? 2f + meleeLevel / 4f : 2f * heldBody; }

        // Per-round chance that a struggling held pawn bursts out: scales with its size against the slime's, capped at 10%.
        public static float BurstChance(float heldBody, float selfBody) { return Clamp((heldBody / Math.Max(0.01f, selfBody) - 0.15f) * 0.25f, 0f, 0.10f); }

        // Damage-driven shedding: true when a gelatid should be shed (and damageSinceShed is reset).
        public static bool ShedStep(ref float damageSinceShed, float damage, float baseHealthScale, float shedFraction, int heldCount, float healthPercent, int stage, bool sheds)
        {
            if (!sheds || damage <= 0f) return false;
            if (stage < 1) return false;
            float hpPool = baseHealthScale * 40f;
            damageSinceShed += damage;
            float perShed = Math.Max(1f, hpPool * shedFraction);
            if (damageSinceShed < perShed) return false;
            damageSinceShed = 0f;
            if (heldCount > 0 && healthPercent < 0.25f) return false;
            return true;
        }

        // Starting mass by weighted table; `roll` in [0,1].
        public static float RollMass(IList<float> weights, IList<float> values, float roll)
        {
            if (weights == null || values == null || weights.Count == 0 || weights.Count != values.Count) return 0f;
            float total = 0f;
            for (int i = 0; i < weights.Count; i++) total += weights[i];
            if (total <= 0f) return 0f;
            float r = roll * total;
            int last = -1;
            for (int i = 0; i < weights.Count; i++)
            {
                if (weights[i] <= 0f) continue;
                last = i;
                r -= weights[i];
                if (r <= 0f) return values[i];
            }
            return values[last];
        }
    }
}
