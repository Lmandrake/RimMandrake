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
        /// <summary>The printed swell step (unsaved; 0 after a load re-meshes once).</summary>
        public byte sizeStep;
    }

    /// <summary>The plant on a cell, as the ledger needs it.</summary>
    public interface IEgSink<K>
    {
        /// <summary>false when no live plant stands on the cell. cycles: the plant runs the cycle here (archetype, scope,
        /// not sealed, its top not switched off).</summary>
        bool TryGetPlant(K c, out int plantId, out float growth, out bool cycles);
        /// <summary>The cycle's water is on the cell for THIS plant (any live source it accepts; RM_Kernel.CycleWet).
        /// Presence, read now: there is no settle state and no re-arm timer (ruling W3).</summary>
        bool CycleWet(K c);
        /// <summary>vanilla Plant.GrowthRate (asked lazily: it is not free). 0 = dark, cold, dormant: never arms, holds.</summary>
        float GrowthRate(K c);
        float NewClockFactor(K c);
        int Hash(K c);
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
            // Quantised to SizeStep's eight steps (the re-mesh brake, spec §7): the size a print shows only changes when
            // the step does, so re-meshing on a step change is exact.
            float s = 1f + (maxOvergrowthScale - 1f) * (SizeStep(charge) / 8f);
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

        // EffectiveTop: a disabled variant falls back to Churn; a disabled Churn is None (the plant never charges).
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

        // ══════════════ THE RULED RATES (design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md §2.5) ══════════════
        // ONE factor r per plant, multiplying vanilla's composite GrowthRate (which already holds light: a dark cell stays
        // 0, r never lifts a zero). r REPLACES every band of the old engine, never stacks.

        /// <summary>The §2.5 moisture factor r. inScope: the plant's map is in the engine's scope for this plant (our
        /// biome, or setting B for a native). stalled: the map's biome is a stunted (terminator) biome. sealed: the plant
        /// stands in a basin/pot/hydroponics (H1: vanilla speed). wet: an accepted water source is on the cell.
        /// waterNearby: an accepted clean source within nearbyRadius (vanilla plants, setting A).</summary>
        public static float MoistureFactor(RM_Archetype a, bool inScope, bool stalled, bool sealedGrower, bool wet, bool ashFresh,
                                           bool woody, bool waterNearby, RM_RateSettings s)
        {
            if (!inScope || sealedGrower || a == RM_Archetype.Exempt) return 1f;
            if (a == RM_Archetype.Vanilla) return !s.vanillaNeedsWater || waterNearby ? 1f : s.vanillaDry;
            if (stalled) return s.stunted;
            float tree = woody ? s.treeRatio : 1f;
            switch (a)
            {
                case RM_Archetype.WetNative: return s.wetNative * tree;
                case RM_Archetype.FireAdapted: return (wet || ashFresh ? s.dryWet : s.dryDry) * tree;
                default: return (wet ? s.dryWet : s.dryDry) * tree;
            }
        }

        /// <summary>Does this archetype run the cycle (charge, tells, outcome) at maturity? Only natives, in scope, unsealed,
        /// outside a stalled biome.</summary>
        public static bool Cycles(RM_Archetype a, bool inScope, bool stalled, bool sealedGrower)
        {
            if (!inScope || stalled || sealedGrower) return false;
            return a == RM_Archetype.DryNative || a == RM_Archetype.WetNative || a == RM_Archetype.FireAdapted;
        }

        /// <summary>Is the cycle's water there? Dry natives need a source (fire-adapted also take fresh ash); wet natives
        /// cycle at home whatever the ground (C1 "x4, always"; spec §7 "every wet native cycles forever").</summary>
        public static bool CycleWet(RM_Archetype a, bool wet, bool ashFresh)
        {
            if (a == RM_Archetype.WetNative) return true;
            if (a == RM_Archetype.FireAdapted) return wet || ashFresh;
            return wet;
        }

        /// <summary>The outcome at the top of a charge (§4.1, §4.2, §4.4; OQ-5, OQ-6, OQ-14, OQ-15). top is the EFFECTIVE top
        /// (after the per-top switches). ruptureChance &lt; 0 = the default for the archetype (dry: defaultChance; wet: 0).
        /// roll in [0,1). A Burst switched off never bursts: the plant fruits instead.</summary>
        public static RM_Outcome ResolveOutcome(RM_Archetype a, byte top, float ruptureChance, float defaultChance, float roll,
                                                bool nativeCrop, bool cropSelfFruit, bool burstEnabled)
        {
            if (top == 6) return RM_Outcome.None;
            if (nativeCrop && cropSelfFruit) return RM_Outcome.SelfFruit;
            if (top == 2 || top == 3 || top == 4 || top == 5) return RM_Outcome.OwnTop;   // Slime, Tinder, Rupture, Flush: own odds
            float chance = ruptureChance >= 0f ? ruptureChance : a == RM_Archetype.WetNative ? 0f : defaultChance;
            if (burstEnabled && roll < chance) return RM_Outcome.Burst;
            return a == RM_Archetype.WetNative ? RM_Outcome.Wither : RM_Outcome.Fruit;
        }

        /// <summary>Dormancy (WP2, §5.2): ticks to take off the coming 2000-tick age step so the plant ages at r. Applied in a
        /// PREFIX, before vanilla adds 2000 and checks Dying. rand01 rounds the fraction. 0 when r &gt;= 1.</summary>
        public static int AgeRemoval(float r, float rand01)
        {
            if (!(r < 1f)) return 0;
            if (r < 0f) r = 0f;
            float t = (1f - r) * 2000f;
            int whole = (int)Math.Floor(t);
            return whole + (t - whole > rand01 ? 1 : 0);
        }

        /// <summary>§7 fallback (3), OFF by default: a cell may arm only in its own hour of the day, the hour a deterministic
        /// hash of the cell picks, so a wave rolls across the map over a day and a reload replays it.</summary>
        public static bool StaggerOpen(int cellHash, int now)
        {
            unchecked
            {
                uint h = (uint)cellHash * 2654435761u;
                int delay = (int)(h % 60000u);
                return ((now + delay) % 60000) < TicksPerHour;
            }
        }

        /// <summary>Rain (OQ-9): an unroofed cell is wet while a water rain runs, and until lingerUntil after it stops,
        /// unless a fruiting plant used that water after the rain stopped (consumedAt &gt;= stoppedAt).</summary>
        public static bool RainWet(bool rainingNow, int now, int stoppedAt, int lingerUntil, int consumedAt)
        {
            if (rainingNow) return true;
            if (now >= lingerUntil) return false;
            return consumedAt < stoppedAt;
        }

        /// <summary>The re-mesh brake (§7): the printed swell moves in eight steps, so a charging plant is re-meshed only when
        /// its step or tell stage changes (plus the tremble wobble on a reprint).</summary>
        public static byte SizeStep(float charge)
        {
            if (charge <= SwellAt) return 0;
            int k = 1 + (int)(InverseLerp(SwellAt, 1f, charge) * 7.999f);
            return (byte)(k > 8 ? 8 : k);
        }
    }

    /// <summary>The ruled archetypes (§4). Vanilla = a plant our tiers do not ship (setting A governs it).</summary>
    public enum RM_Archetype : byte { DryNative = 0, WetNative = 1, FireAdapted = 2, Exempt = 3, Vanilla = 4 }

    /// <summary>What a fully charged plant does (§4).</summary>
    public enum RM_Outcome : byte { None = 0, Fruit = 1, Burst = 2, Wither = 3, SelfFruit = 4, OwnTop = 5 }

    /// <summary>The rate sliders, defaults = the ruled numbers.</summary>
    public struct RM_RateSettings
    {
        public float dryWet, dryDry, wetNative, treeRatio, stunted, vanillaDry;
        public bool vanillaNeedsWater;
        public static RM_RateSettings Ruled => new RM_RateSettings
        {
            dryWet = 10f, dryDry = 0.1f, wetNative = 4f, treeRatio = 0.625f, stunted = 0.4f, vanillaDry = 0.1f, vanillaNeedsWater = true,
        };
    }

    /// <summary>One map's TIMED sources (flood / surge / API pushes, which carry their own length), the suppression grid,
    /// the ash-fresh restarts and the charge records, and the pass over them. Every other water source is read on demand
    /// through the sink (presence model, spec §2): this ledger never decides wetness by itself.</summary>
    public sealed class RM_EgLedger<K>
    {
        public Dictionary<K, int> soakUntil = new Dictionary<K, int>();
        public Dictionary<K, int> suppressedUntil = new Dictionary<K, int>();
        public Dictionary<K, int> ashUntil = new Dictionary<K, int>();
        public Dictionary<K, RM_ChargeRecord> charges = new Dictionary<K, RM_ChargeRecord>();
        private readonly List<K> tmp = new List<K>();

        public bool IsSuppressed(K c, int now)
        {
            int until;
            return suppressedUntil.Count != 0 && suppressedUntil.TryGetValue(c, out until) && now < until;
        }

        /// <summary>A live timed source (flood, surge, API push) on the cell.</summary>
        public bool IsSoaked(K c, int now)
        {
            int until;
            return soakUntil.Count != 0 && soakUntil.TryGetValue(c, out until) && now < until && !IsSuppressed(c, now);
        }

        /// <summary>EGROWTH_SOAK_FIX_DURATION_INT_WRAP: now + ticks clamped to int.MaxValue.</summary>
        public static int Deadline(int now, int ticks)
        {
            return (int)Math.Min((long)now + Math.Max(1, ticks), int.MaxValue);
        }

        /// <summary>A timed source (a running flood re-pushes each pulse). Extends, never shortens; refused on suppressed
        /// ground or when not allowed.</summary>
        public bool TrySoak(K c, int now, int ticks, bool allowed)
        {
            if (!allowed) return false;
            if (IsSuppressed(c, now)) return false;
            int until = Deadline(now, ticks);
            int prior;
            if (!soakUntil.TryGetValue(c, out prior) || prior < until) soakUntil[c] = until;
            return true;
        }

        public void Suppress(IEnumerable<K> cells, int now, int ticks)
        {
            int until = Deadline(now, ticks);
            foreach (K c in cells)
            {
                int prior;
                if (!suppressedUntil.TryGetValue(c, out prior) || prior < until) suppressedUntil[c] = until;
                soakUntil.Remove(c);
            }
        }

        /// <summary>OQ-11: ash-fresh restarts when a seedling appears on fresh ash.</summary>
        public void RestartAsh(K c, int now, int windowTicks)
        {
            int until = Deadline(now, windowTicks), prior;
            if (!ashUntil.TryGetValue(c, out prior) || prior < until) ashUntil[c] = until;
        }

        public bool AshRestarted(K c, int now)
        {
            int until;
            return ashUntil.Count != 0 && ashUntil.TryGetValue(c, out until) && now < until;
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
            PruneDict(ashUntil, now);
        }

        private void PruneDict(Dictionary<K, int> d, int now)
        {
            if (d.Count == 0) return;
            tmp.Clear();
            foreach (KeyValuePair<K, int> kv in d) if (kv.Value <= now) tmp.Add(kv.Key);
            for (int i = 0; i < tmp.Count; i++) d.Remove(tmp[i]);
        }

        /// <summary>Step 1: arm every candidate that cycles, is mature, has its water, is lit and growing (and, with the
        /// stagger on, is in its hour). The full-map wave (PF1 option 2): candidates are a slice of every plant on the map.
        /// Step 2: the charge. Re-mesh only on a tell-stage or size-step change, plus the tremble wobble on a reprint.</summary>
        public void Pass<S>(S sink, IList<K> candidates, int now, int dt, bool reprint, float chargeTicks, bool tellSounds,
                            bool stagger) where S : IEgSink<K>
        {
            if (candidates != null)
            {
                for (int i = 0; i < candidates.Count; i++)
                {
                    K c = candidates[i];
                    if (charges.ContainsKey(c)) continue;
                    int id; float growth; bool cycles;
                    if (!sink.TryGetPlant(c, out id, out growth, out cycles) || !cycles) continue;
                    if (growth < RM_ExplosiveGrowthKernel.MatureGrowth) continue;
                    if (IsSuppressed(c, now) || !sink.CycleWet(c)) continue;
                    if (stagger && !RM_ExplosiveGrowthKernel.StaggerOpen(sink.Hash(c), now)) continue;
                    if (!(sink.GrowthRate(c) > 0f)) continue;
                    charges[c] = new RM_ChargeRecord { plantId = id, charge = RM_ExplosiveGrowthKernel.ArmedCharge, stage = RM_TellStage.Ground, clockFactor = sink.NewClockFactor(c) };
                    sink.OnArmed(c);
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
                    int id; float growth; bool cycles;
                    if (!sink.TryGetPlant(c, out id, out growth, out cycles) || id != rec.plantId)
                    {
                        charges.Remove(c);
                        continue;
                    }
                    if (!cycles)
                    {
                        charges.Remove(c);
                        sink.OnDirty(c);
                        continue;
                    }

                    bool wet = !IsSuppressed(c, now) && sink.CycleWet(c);
                    rec.charge = RM_ExplosiveGrowthKernel.StepCharge(rec.charge, wet, sink.GrowthRate(c) > 0f, dt, chargeTicks, rec.clockFactor);

                    if (rec.charge <= 0f)
                    {
                        charges.Remove(c);
                        sink.OnDirty(c);
                        continue;
                    }

                    bool dirty = false;
                    RM_TellStage want = RM_ExplosiveGrowthKernel.StageFor(rec.charge);
                    if (want > rec.stage)
                    {
                        if (want >= RM_TellStage.Creak && rec.stage < RM_TellStage.Creak && tellSounds) sink.OnCreak(c);
                        rec.stage = want;
                        dirty = true;
                    }
                    byte step = RM_ExplosiveGrowthKernel.SizeStep(rec.charge);
                    if (step != rec.sizeStep) { rec.sizeStep = step; dirty = true; }
                    bool trembling = rec.stage == RM_TellStage.Tremble || rec.stage == RM_TellStage.Creak;
                    if (trembling) sink.OnTellPuff(c);

                    if (rec.charge >= 1f)
                    {
                        charges.Remove(c);
                        sink.OnFire(c);
                        continue;
                    }

                    if (dirty || (reprint && trembling)) sink.OnDirty(c);
                }
            }
        }
    }
}
