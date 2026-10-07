// Verse-free kernel of Explosive Growth: the soak / suppression / charge ledger of one map, the 250-tick pass over it,
// the charge clock, the tell ladder, the visual curves and the soak-source slice maths. The map component and the soak
// sources call these with the same expressions; SelfTest/ExplosiveGrowthFuzz.cs compiles this file alone. Keep it free
// of Verse/RimWorld/UnityEngine (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>The section 2 tell ladder in its ruled order: ground, swell, hue, tremble, creak, silence.</summary>
    public enum RM_TellStage : byte { None = 0, Ground = 1, Swell = 2, Hue = 3, Tremble = 4, Creak = 5, Silence = 6 }

    /// <summary>One charging plant. Valid only while the plant standing on the cell is still plantId. The Scribe half
    /// (IExposable) lives in the map component's file.</summary>
    public partial class RM_ChargeRecord
    {
        public int plantId;
        public float charge;
        public RM_TellStage stage;
        public float clockFactor = 1f;
    }

    /// <summary>The plant on a cell, as the ledger needs it.</summary>
    public interface IEgSink<K>
    {
        /// <summary>false when no live plant stands on the cell.</summary>
        bool TryGetPlant(K c, out int plantId, out float growth, out bool soaks);
        /// <summary>vanilla Plant.GrowthRate (asked lazily: it is not free).</summary>
        float GrowthRate(K c);
        float NewClockFactor(K c);
        void OnDirty(K c);
        void OnArmed(K c);
        void OnCreak(K c);
        void OnTellPuff(K c);
        void OnFire(K c);
    }

    public static class RM_ExplosiveGrowthKernel
    {
        public const int PassInterval = 250;
        public const int TicksPerHour = 2500;
        public const float SwellAt = 0.15f;
        public const float HueAt = 0.45f;
        public const float TrembleAt = 0.70f;
        public const float CreakAt = 0.85f;
        public const float SilenceAt = 0.95f;
        public const float MatureGrowth = 0.999f;
        public const float ArmedCharge = 0.0001f;
        public const int SliceCount = 8;
        public const float SurgeFreshMin = 0.25f;
        public const float SurgeFreshMax = 0.48f;

        public static RM_TellStage StageFor(float charge)
        {
            return charge >= SilenceAt ? RM_TellStage.Silence
                : charge >= CreakAt ? RM_TellStage.Creak
                : charge >= TrembleAt ? RM_TellStage.Tremble
                : charge >= HueAt ? RM_TellStage.Hue
                : charge >= SwellAt ? RM_TellStage.Swell
                : RM_TellStage.Ground;
        }

        // wet + growing advances; wet + dormant HOLDS; dry decays twice as fast as it charged.
        public static float StepCharge(float charge, bool wet, bool growing, int dt, float chargeTicks, float clockFactor)
        {
            if (wet && growing) return charge + dt / (chargeTicks * clockFactor);
            if (wet) return charge;
            return charge - dt / (chargeTicks * 0.5f);
        }

        public static float ChargeTicks(float chargeHours) { return Math.Max(250f, chargeHours * TicksPerHour); }
        public static int PassDelta(int now, int lastPassTick)
        {
            return lastPassTick < 0 ? PassInterval : Math.Min(Math.Max(now - lastPassTick, 1), PassInterval * 8);
        }

        public static float InverseLerp(float a, float b, float v)
        {
            if (a == b) return 0f;
            float t = (v - a) / (b - a);
            return t < 0f ? 0f : t > 1f ? 1f : t;
        }

        public static float VisualScale(float charge, float maxOvergrowthScale, bool wobbleParity)
        {
            if (charge <= SwellAt) return 1f;
            float s = 1f + (maxOvergrowthScale - 1f) * InverseLerp(SwellAt, 1f, charge);
            if (charge >= TrembleAt && charge < SilenceAt) s *= wobbleParity ? 1.035f : 0.965f;
            return s;
        }

        // 0 = natural, 1 = fully wrong, quantised to quarters.
        public static float Hue(float charge)
        {
            if (charge <= HueAt) return 0f;
            float h = InverseLerp(HueAt, 1f, charge);
            return (float)Math.Ceiling(h * 4f) / 4f;
        }

        public static float SoakFactor(float soakMultiplier) { return Math.Max(1f, soakMultiplier); }

        // The effective top after the per-top settings: a disabled variant falls back to Churn; a disabled Churn is None.
        // Tops: 0 Churn 1 Burst 2 Slime 3 Tinder 4 Rupture 5 Flush 6 None.
        public static byte EffectiveTop(byte top, bool burst, bool tinder, bool slime, bool rupture, bool flush, bool churn)
        {
            byte fallback = churn ? (byte)0 : (byte)6;
            switch (top)
            {
                case 1: return burst ? top : fallback;
                case 3: return tinder ? top : fallback;
                case 2: return slime ? top : fallback;
                case 4: return rupture ? top : fallback;
                case 5: return flush ? top : fallback;
                case 0: return fallback;
                default: return top;
            }
        }

        // The irrigation / surge grid sweep takes SliceCount passes; slice k covers [start, end).
        public static void SliceRange(int n, int cursor, out int start, out int end)
        {
            int slice = (n + SliceCount - 1) / SliceCount;
            start = (cursor % SliceCount) * slice;
            end = Math.Min(n, start + slice);
        }
        public static int NextCursor(int cursor) { return (cursor + 1) % SliceCount; }
        public static bool InSurgeBand(float salinity) { return !(salinity < SurgeFreshMin || salinity > SurgeFreshMax); }
    }

    /// <summary>One map's soak grid, suppression grid and charge records, and the pass over them.</summary>
    public sealed class RM_EgLedger<K>
    {
        public Dictionary<K, int> soakUntil = new Dictionary<K, int>();
        public Dictionary<K, int> suppressedUntil = new Dictionary<K, int>();
        public Dictionary<K, RM_ChargeRecord> charges = new Dictionary<K, RM_ChargeRecord>();
        private readonly List<K> tmp = new List<K>();

        public bool IsSuppressed(K c, int now)
        {
            int until;
            return suppressedUntil.Count != 0 && suppressedUntil.TryGetValue(c, out until) && now < until;
        }

        public bool IsSoaked(K c, int now)
        {
            int until;
            return soakUntil.Count != 0 && soakUntil.TryGetValue(c, out until) && now < until;
        }

        /// <summary>allowed = setting on, in bounds, biome not a carve-out. Extends, never shortens, an existing soak;
        /// refused on suppressed ground.</summary>
        public bool TrySoak(K c, int now, int ticks, bool allowed)
        {
            if (!allowed) return false;
            if (IsSuppressed(c, now)) return false;
            int until = now + Math.Max(1, ticks);
            int prior;
            if (!soakUntil.TryGetValue(c, out prior) || prior < until) soakUntil[c] = until;
            return true;
        }

        public void Suppress(IEnumerable<K> cells, int now, int ticks)
        {
            int until = now + Math.Max(1, ticks);
            foreach (K c in cells)
            {
                int prior;
                if (!suppressedUntil.TryGetValue(c, out prior) || prior < until) suppressedUntil[c] = until;
                soakUntil.Remove(c);
            }
        }

        public float GrowthFactor(K c, int now, bool plantSoaks, float soakMultiplier)
        {
            if (soakUntil.Count == 0) return 1f;
            int until;
            if (!soakUntil.TryGetValue(c, out until) || now >= until) return 1f;
            if (!plantSoaks) return 1f;
            return RM_ExplosiveGrowthKernel.SoakFactor(soakMultiplier);
        }

        public bool TryGetCharge(K c, int plantId, out RM_ChargeRecord rec)
        {
            rec = null;
            if (charges.Count == 0) return false;
            if (!charges.TryGetValue(c, out rec)) return false;
            if (rec.plantId != plantId) { rec = null; return false; }
            return true;
        }

        public float TakeCharge(K c, int plantId)
        {
            RM_ChargeRecord rec;
            if (!TryGetCharge(c, plantId, out rec)) return 0f;
            charges.Remove(c);
            return rec.charge;
        }

        public void DebugSetCharge(K c, int plantId, float value)
        {
            if (value <= 0f) { charges.Remove(c); return; }
            charges[c] = new RM_ChargeRecord { plantId = plantId, charge = value, stage = RM_ExplosiveGrowthKernel.StageFor(value), clockFactor = 1f };
        }

        public int DebugForceCharge(float value)
        {
            int n = 0;
            foreach (RM_ChargeRecord rec in charges.Values) if (rec.charge < value) { rec.charge = value; n++; }
            return n;
        }

        public void PruneExpired(int now)
        {
            PruneDict(soakUntil, now);
            PruneDict(suppressedUntil, now);
        }

        private void PruneDict(Dictionary<K, int> d, int now)
        {
            if (d.Count == 0) return;
            tmp.Clear();
            foreach (KeyValuePair<K, int> kv in d) if (kv.Value <= now) tmp.Add(kv.Key);
            for (int i = 0; i < tmp.Count; i++) d.Remove(tmp[i]);
        }

        /// <summary>Step 1 (arm what is soaked and mature) and step 2 (the charge) of the map pass.</summary>
        public void Pass<S>(S sink, int now, int dt, bool reprint, float chargeTicks, bool tellSounds) where S : IEgSink<K>
        {
            if (soakUntil.Count > 0)
            {
                tmp.Clear();
                tmp.AddRange(soakUntil.Keys);
                for (int i = 0; i < tmp.Count; i++)
                {
                    K c = tmp[i];
                    int id; float growth; bool soaks;
                    if (!sink.TryGetPlant(c, out id, out growth, out soaks) || !soaks) continue;
                    if (growth < RM_ExplosiveGrowthKernel.MatureGrowth)
                    {
                        if (reprint) sink.OnDirty(c);
                        continue;
                    }
                    if (!charges.ContainsKey(c) && sink.GrowthRate(c) > 0f)
                    {
                        charges[c] = new RM_ChargeRecord { plantId = id, charge = RM_ExplosiveGrowthKernel.ArmedCharge, stage = RM_TellStage.Ground, clockFactor = sink.NewClockFactor(c) };
                        sink.OnArmed(c);
                    }
                }
            }

            if (charges.Count > 0)
            {
                tmp.Clear();
                tmp.AddRange(charges.Keys);
                for (int i = 0; i < tmp.Count; i++)
                {
                    K c = tmp[i];
                    RM_ChargeRecord rec = charges[c];
                    int id; float growth; bool soaks;
                    if (!sink.TryGetPlant(c, out id, out growth, out soaks) || id != rec.plantId)
                    {
                        charges.Remove(c);
                        continue;
                    }
                    if (!soaks)
                    {
                        charges.Remove(c);
                        sink.OnDirty(c);
                        continue;
                    }

                    int until;
                    bool wet = soakUntil.TryGetValue(c, out until) && now < until && !IsSuppressed(c, now);
                    rec.charge = RM_ExplosiveGrowthKernel.StepCharge(rec.charge, wet, sink.GrowthRate(c) > 0f, dt, chargeTicks, rec.clockFactor);

                    if (rec.charge <= 0f)
                    {
                        charges.Remove(c);
                        sink.OnDirty(c);
                        continue;
                    }

                    RM_TellStage want = RM_ExplosiveGrowthKernel.StageFor(rec.charge);
                    if (want > rec.stage)
                    {
                        if (want >= RM_TellStage.Creak && rec.stage < RM_TellStage.Creak && tellSounds) sink.OnCreak(c);
                        rec.stage = want;
                        sink.OnDirty(c);
                    }
                    if (rec.stage == RM_TellStage.Tremble || rec.stage == RM_TellStage.Creak) sink.OnTellPuff(c);

                    if (rec.charge >= 1f)
                    {
                        charges.Remove(c);
                        sink.OnFire(c);
                        continue;
                    }

                    if (reprint) sink.OnDirty(c);
                }
            }
        }
    }
}
