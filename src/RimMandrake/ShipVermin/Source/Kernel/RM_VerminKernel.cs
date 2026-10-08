using System;
using System.Collections.Generic;

namespace RimMandrake.ShipVermin
{
    // Verse-free decisions of mandrake.rm.shipvermin: the wreck nest's schedule, burst and refusal order, which species a nest may pick, the
    // fethrik's one-time ability grant and the chemfuel spray cone. RM_CompVerminNest, ShipVerminSettings, RM_CompInnateAbility and
    // RM_CompAbilityEffect_FuelSpew call these; the seeded fuzz under Source/SelfTest compiles THIS file directly (no `using Verse;` here).
    public static class RM_VerminKernel
    {
        public const int TicksPerDay = 60000;
        public const float MinRateMultiplier = 0.01f;

        /// <summary>Ticks to the next nest attempt for a sampled interval in days. Never below 1, so a huge rate cannot spin the timer every tick.</summary>
        public static int NestIntervalTicks(float days, float rateMultiplier)
        {
            float mult = Math.Max(MinRateMultiplier, rateMultiplier);
            return Math.Max(1, (int)Math.Round(days * TicksPerDay / mult, MidpointRounding.ToEven));
        }

        /// <summary>A fresh nest (not a reload, burst not done, none scheduled) with a burst configured schedules one.</summary>
        public static bool BurstShouldSchedule(bool respawningAfterLoad, bool burstDone, int burstTick, int burstMax)
        {
            return !respawningAfterLoad && !burstDone && burstTick < 0 && burstMax > 0;
        }

        public struct NestStep { public bool Burst, Attempt; }

        /// <summary>What one CompTick of a nest does. The burst fires once, when due; the periodic attempt is independent of it.</summary>
        public static NestStep Step(bool spawned, bool wreckSpawningEnabled, bool burstDone, int burstTick, int nextSpawnTick, int now)
        {
            var step = new NestStep();
            if (!spawned || !wreckSpawningEnabled) return step;
            step.Burst = !burstDone && burstTick >= 0 && now >= burstTick;
            step.Attempt = now >= nextSpawnTick;
            return step;
        }

        public enum Refusal { None, NoMap, PopulationCap, NoSpecies, NoCell, GenerationFailed }

        /// <summary>The first reason a spawn attempt is refused, in the order the attempt checks them. A missing population component does NOT cap.</summary>
        public static Refusal SpawnRefusal(bool hasMap, bool hasPopulationComponent, int currentPopulation, int hardCap, bool hasSpecies, bool hasCell, bool generated)
        {
            if (!hasMap) return Refusal.NoMap;
            if (hasPopulationComponent && currentPopulation >= hardCap) return Refusal.PopulationCap;
            if (!hasSpecies) return Refusal.NoSpecies;
            if (!hasCell) return Refusal.NoCell;
            if (!generated) return Refusal.GenerationFailed;
            return Refusal.None;
        }

        public struct RosterSlot
        {
            public string Kind; public bool Enabled; public Func<string> ResolvedName;
        }

        /// <summary>A name in the roster (as the free kind, or as the kind swapped into its slot) follows its slot's checkbox; a name outside the roster is allowed.</summary>
        public static bool RosterAllows(IList<RosterSlot> slots, string kind)
        {
            for (int i = 0; i < slots.Count; i++)
            {
                if (slots[i].Kind == kind || (slots[i].ResolvedName != null && slots[i].ResolvedName() == kind)) return slots[i].Enabled;
            }
            return true;
        }

        /// <summary>The weighted pool of a nest with its own weights: blank names, non-positive weights, names the roster forbids and names that do not resolve are dropped.</summary>
        public static List<KeyValuePair<T, float>> BuildPool<T>(IEnumerable<KeyValuePair<string, float>> weights, Func<string, bool> allows, Func<string, T> resolve) where T : class
        {
            var pool = new List<KeyValuePair<T, float>>();
            foreach (var vw in weights)
            {
                if (string.IsNullOrEmpty(vw.Key) || vw.Value <= 0f || !allows(vw.Key)) continue;
                T r = resolve(vw.Key);
                if (r != null) pool.Add(new KeyValuePair<T, float>(r, vw.Value));
            }
            return pool;
        }

        /// <summary>Index chosen by weight for a uniform roll in [0,1). Total function: a roll at the very top lands on the last entry.</summary>
        public static int PickByWeight(IList<float> weights, double roll01)
        {
            double total = 0;
            for (int i = 0; i < weights.Count; i++) total += weights[i];
            double x = roll01 * total;
            for (int i = 0; i < weights.Count; i++)
            {
                x -= weights[i];
                if (x < 0) return i;
            }
            return weights.Count - 1;
        }

        public enum Grant { Nothing, MarkGrantedOnly, Give }

        /// <summary>The fethrik's one-time innate ability: gated by its setting, marked granted without a tracker when the def names no ability.</summary>
        public static Grant InnateGrant(bool alreadyGranted, bool settingOn, bool abilityDefMissing, bool isPawn)
        {
            if (alreadyGranted || !settingOn) return Grant.Nothing;
            if (abilityDefMissing) return Grant.MarkGrantedOnly;
            if (!isPawn) return Grant.Nothing;
            return Grant.Give;
        }

        /// <summary>The spray's aim point: pushed out to exactly `range` along the heading, so a close click still gives a full-length cone. Null when aim is the caster's own cell.</summary>
        public static bool AimPoint(int px, int pz, int ax, int az, float range, out int outX, out int outZ)
        {
            outX = ax; outZ = az;
            if (px == ax && pz == az) return false;
            float dist = (float)Math.Sqrt((double)(ax - px) * (ax - px) + (double)(az - pz) * (az - pz));
            float dx = (ax - px) / dist;
            float dz = (az - pz) / dist;
            outX = (int)Math.Round(px + dx * range, MidpointRounding.ToEven);
            outZ = (int)Math.Round(pz + dz * range, MidpointRounding.ToEven);
            return true;
        }

        public static double HalfAngleDeg(double aimDistance, double lineWidthEnd)
        {
            double half = lineWidthEnd / 2.0;
            double hyp = Math.Sqrt(aimDistance * aimDistance + half * half);
            return Math.Asin(half / hyp) * 180.0 / Math.PI;
        }

        /// <summary>True when the cell at (cdx, cdz) from the caster lies within halfAngleDeg of the heading (adx, adz). Angles wrap through 180.</summary>
        public static bool InCone(double cdx, double cdz, double adx, double adz, double halfAngleDeg)
        {
            double cellAngle = Math.Atan2(cdz, cdx) * 180.0 / Math.PI;
            double heading = Math.Atan2(adz, adx) * 180.0 / Math.PI;
            double d = (cellAngle - heading) % 360.0;
            if (d > 180.0) d -= 360.0;
            if (d < -180.0) d += 360.0;
            return Math.Abs(d) <= halfAngleDeg;
        }
    }
}
