using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>One charging plant. Keyed by cell in the component, but only
    /// valid while the plant standing there is still <see cref="plantId"/>.</summary>
    public class RM_ChargeRecord : IExposable
    {
        public int plantId;
        public float charge;
        public RM_TellStage stage;
        // Per-plant ±10% on the charge clock so a soaked field goes up in
        // waves, "like popcorn over an afternoon" (§3), not one frame.
        public float clockFactor = 1f;

        public void ExposeData()
        {
            Scribe_Values.Look(ref plantId, "plantId", 0);
            Scribe_Values.Look(ref charge, "charge", 0f);
            Scribe_Values.Look(ref stage, "stage", RM_TellStage.None);
            Scribe_Values.Look(ref clockFactor, "clockFactor", 1f);
        }
    }

    /// <summary>The §2 tell ladder, in its ruled fixed order: ground before
    /// sky — ground darkens and sprouts, the plant swells, its hue shifts
    /// wrong, it trembles, it creaks, and the last moment is silent.</summary>
    public enum RM_TellStage : byte
    {
        None = 0,
        Ground = 1,
        Swell = 2,
        Hue = 3,
        Tremble = 4,
        Creak = 5,
        Silence = 6,
    }

    /// <summary>An active rupture cloud: pawns inside without a full vacuum
    /// seal roll for mutations until it expires.</summary>
    public class RM_RuptureZone : IExposable
    {
        public IntVec3 center;
        public float radius;
        public int untilTick;

        public void ExposeData()
        {
            Scribe_Values.Look(ref center, "center");
            Scribe_Values.Look(ref radius, "radius", 3.9f);
            Scribe_Values.Look(ref untilTick, "untilTick", 0);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // THE SOAK, THE CHARGE AND THE SUPPRESSION GRID — one component per map.
    //
    // Auto-attached by vanilla Map.FillComponents (any non-abstract
    // MapComponent with a (Map) constructor), same as every sibling mod's.
    //
    // Sparse cell dictionaries, not full-map arrays: soak is an EVENT (a
    // flood footprint, an irrigated field, a bloom), so on a normal map the
    // dictionaries are empty and every hot-path read is a Count==0 check.
    // The shape is RM_MapComponent_CanyonFlood's soakUntilTick generalised —
    // that stub was the model, and this component replaces it.
    //
    // Nothing runs per tick but one integer compare: the whole pass runs on
    // vanilla's rare-tick cadence (250).
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ExplosiveGrowth : MapComponent
    {
        public const int PassInterval = GenTicks.TickRareInterval;

        // Tell thresholds on charge 0..1. 🄸 INVENTED spacing; order is ruled.
        public const float SwellAt = 0.15f;
        public const float HueAt = 0.45f;
        public const float TrembleAt = 0.70f;
        public const float CreakAt = 0.85f;
        public const float SilenceAt = 0.95f;

        public const float MatureGrowth = 0.999f;

        private Dictionary<IntVec3, int> soakUntil = new Dictionary<IntVec3, int>();
        private Dictionary<IntVec3, int> suppressedUntil = new Dictionary<IntVec3, int>();
        private Dictionary<IntVec3, RM_ChargeRecord> charges = new Dictionary<IntVec3, RM_ChargeRecord>();
        private List<RM_RuptureZone> ruptures = new List<RM_RuptureZone>();

        private int nextPassTick = -1;
        private int lastPassTick = -1;
        private int nextReprintTick = -1;
        private bool wobbleParity;

        // Irrigation / surge slice cursors (see RM_SoakSources).
        public int irrigationCursor;
        public int surgeCursor;

        private readonly List<IntVec3> tmpCells = new List<IntVec3>();
        private List<IntVec3> tmpKeys;
        private List<int> tmpInts;
        private List<RM_ChargeRecord> tmpRecs;

        private static Map cachedMap;
        private static RM_MapComponent_ExplosiveGrowth cachedComp;

        public RM_MapComponent_ExplosiveGrowth(Map map) : base(map)
        {
        }

        public static RM_MapComponent_ExplosiveGrowth For(Map map)
        {
            if (map == null) return null;
            if (map == cachedMap && cachedComp != null) return cachedComp;
            cachedComp = map.GetComponent<RM_MapComponent_ExplosiveGrowth>();
            cachedMap = map;
            return cachedComp;
        }

        public int SoakedCount => soakUntil.Count;
        public int ChargingCount => charges.Count;
        public int SuppressedCount => suppressedUntil.Count;
        public IEnumerable<IntVec3> SoakedCells => soakUntil.Keys;
        public bool AnyCharging => charges.Count > 0;

        // ── the soak ─────────────────────────────────────────────────────

        /// <summary>Soak one cell for <paramref name="ticks"/>. Extends, never
        /// shortens, an existing soak. Refused on suppressed ground and in a
        /// carve-out biome (terminator, deep desert — design doc §3).</summary>
        public bool TrySoak(IntVec3 c, int ticks)
        {
            if (!ExplosiveGrowthSettings.enabled || !c.InBounds(map)) return false;
            if (RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome)) return false;
            int now = Find.TickManager.TicksGame;
            if (IsSuppressed(c, now)) return false;
            int until = now + Mathf.Max(1, ticks);
            if (!soakUntil.TryGetValue(c, out int prior) || prior < until)
            {
                soakUntil[c] = until;
            }
            return true;
        }

        public bool IsSoaked(IntVec3 c)
        {
            return soakUntil.Count != 0 && soakUntil.TryGetValue(c, out int until)
                && Find.TickManager.TicksGame < until;
        }

        /// <summary>The soak multiplier for a plant, or 1. Called from the
        /// GrowthRate postfix; never allocates.</summary>
        public float GrowthFactorFor(Plant plant)
        {
            if (soakUntil.Count == 0) return 1f;
            if (!soakUntil.TryGetValue(plant.Position, out int until) || Find.TickManager.TicksGame >= until) return 1f;
            RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(plant.def);
            if (prof == null || !prof.Soaks) return 1f;
            return Mathf.Max(1f, ExplosiveGrowthSettings.soakMultiplier);
        }

        // ── suppression (Greentide kit M10 grazing, M2 dry-air blower) ────

        /// <summary>Encroachment pressure is SOAK: suppression refuses new soak,
        /// dries what is there, and makes a charging plant relax. It also keeps
        /// sown rings off the cell. That is the grid the Greentide kit's M2/M10
        /// hooks were waiting for.</summary>
        public void Suppress(IntVec3 center, int radius, int ticks)
        {
            if (!ExplosiveGrowthSettings.suppressionEnabled) return;
            int until = Find.TickManager.TicksGame + Mathf.Max(1, ticks);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, Mathf.Max(0, radius) + 0.5f, true))
            {
                if (!c.InBounds(map)) continue;
                if (!suppressedUntil.TryGetValue(c, out int prior) || prior < until) suppressedUntil[c] = until;
                soakUntil.Remove(c);
            }
        }

        public bool IsSuppressed(IntVec3 c, int now)
        {
            return suppressedUntil.Count != 0 && suppressedUntil.TryGetValue(c, out int until) && now < until;
        }

        // ── the charge, read by the visuals ──────────────────────────────

        public bool TryGetCharge(Plant plant, out RM_ChargeRecord rec)
        {
            rec = null;
            if (charges.Count == 0 || plant == null || !plant.Spawned) return false;
            if (!charges.TryGetValue(plant.Position, out rec)) return false;
            if (rec.plantId != plant.thingIDNumber) { rec = null; return false; }
            return true;
        }

        public float VisualScaleFor(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec) || rec.charge <= SwellAt) return 1f;
            float s = 1f + (ExplosiveGrowthSettings.maxOvergrowthScale - 1f) * Mathf.InverseLerp(SwellAt, 1f, rec.charge);
            // The tremble, staged: alternate ±3.5% per re-print while trembling,
            // stopped for the silent last moment.
            if (rec.charge >= TrembleAt && rec.charge < SilenceAt)
            {
                s *= wobbleParity ? 1.035f : 0.965f;
            }
            return s;
        }

        /// <summary>0 = natural colour, 1 = fully wrong. Quantised to quarters
        /// so the tinted-graphic cache stays tiny.</summary>
        public float HueFor(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec) || rec.charge <= HueAt) return 0f;
            float h = Mathf.InverseLerp(HueAt, 1f, rec.charge);
            return Mathf.Ceil(h * 4f) / 4f;
        }

        /// <summary>Removes the charge and returns it, for the harvest/cut
        /// hooks. 0 if the plant was not charging.</summary>
        public float TakeCharge(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec)) return 0f;
            charges.Remove(plant.Position);
            return rec.charge;
        }

        public float ChargeOf(Plant plant) => TryGetCharge(plant, out RM_ChargeRecord rec) ? rec.charge : 0f;

        /// <summary>The tell ladder for a charge (pure; UpdateTells and the proof both read it).</summary>
        public static RM_TellStage StageFor(float charge)
        {
            return charge >= SilenceAt ? RM_TellStage.Silence
                : charge >= CreakAt ? RM_TellStage.Creak
                : charge >= TrembleAt ? RM_TellStage.Tremble
                : charge >= HueAt ? RM_TellStage.Hue
                : charge >= SwellAt ? RM_TellStage.Swell
                : RM_TellStage.Ground;
        }

        /// <summary>EXPLOSIVE_GROWTH_PROBE_TOOL_1: put one plant at an exact charge (stage follows, no side effects).
        /// 0 removes its record.</summary>
        public void DebugSetCharge(Plant plant, float value)
        {
            if (plant == null || !plant.Spawned) return;
            if (value <= 0f)
            {
                charges.Remove(plant.Position);
                return;
            }
            charges[plant.Position] = new RM_ChargeRecord
            {
                plantId = plant.thingIDNumber,
                charge = value,
                stage = StageFor(value),
                clockFactor = 1f,
            };
        }

        public void AddRupture(IntVec3 center, float radius, int ticks)
        {
            ruptures.Add(new RM_RuptureZone { center = center, radius = radius, untilTick = Find.TickManager.TicksGame + ticks });
        }

        /// <summary>Debug / BloomBurst: jump every charging or soaked mature
        /// plant's charge to at least <paramref name="value"/>.</summary>
        public int DebugForceCharge(float value)
        {
            int n = 0;
            foreach (RM_ChargeRecord rec in charges.Values)
            {
                if (rec.charge < value) { rec.charge = value; n++; }
            }
            return n;
        }

        // ── the pass ─────────────────────────────────────────────────────

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now < nextPassTick) return;
            nextPassTick = now + PassInterval;
            if (!ExplosiveGrowthSettings.enabled || !RM_ExplosiveGrowthRegistry.Ready)
            {
                lastPassTick = now;
                return;
            }
            int dt = lastPassTick < 0 ? PassInterval : Mathf.Clamp(now - lastPassTick, 1, PassInterval * 8);
            lastPassTick = now;
            Pass(now, dt);
        }

        private void Pass(int now, int dt)
        {
            PruneExpired(now);
            RM_SoakSources.Pulse(this, now);

            bool reprint = now >= nextReprintTick;
            if (reprint)
            {
                nextReprintTick = now + Mathf.Max(60, ExplosiveGrowthSettings.reprintIntervalTicks);
                wobbleParity = !wobbleParity;
            }

            // 1. Soaked ground: grow visibly, and arm what is fully grown.
            if (soakUntil.Count > 0)
            {
                tmpCells.Clear();
                tmpCells.AddRange(soakUntil.Keys);
                for (int i = 0; i < tmpCells.Count; i++)
                {
                    IntVec3 c = tmpCells[i];
                    Plant plant = c.GetPlant(map);
                    if (plant == null || plant.Destroyed) continue;
                    RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(plant.def);
                    if (prof == null || !prof.Soaks) continue;

                    if (plant.Growth < MatureGrowth)
                    {
                        // Vanilla only re-prints a WILD plant's mesh when it
                        // matures (Plant.TickLong dirties only cultivated
                        // plants per growth step) — that, not the growth rate,
                        // is the steppiness the item warned about. Staged
                        // re-print is design doc §5 option 1.
                        if (reprint) Dirty(c);
                        continue;
                    }
                    // Only a plant that can grow RIGHT NOW arms. A dormant one
                    // (frozen, out of season, no fertility, blighted: vanilla
                    // GrowthRate == 0) waits, soaked, until it can — and does
                    // not re-fire the ground tell every pass while it waits.
                    if (!charges.ContainsKey(c) && plant.GrowthRate > 0f) StartCharge(c, plant, prof);
                }
            }

            // 2. The charge.
            if (charges.Count > 0)
            {
                float chargeTicks = Mathf.Max(250f, ExplosiveGrowthSettings.chargeHours * GenDate.TicksPerHour);
                tmpCells.Clear();
                tmpCells.AddRange(charges.Keys);
                for (int i = 0; i < tmpCells.Count; i++)
                {
                    IntVec3 c = tmpCells[i];
                    RM_ChargeRecord rec = charges[c];
                    Plant plant = c.GetPlant(map);
                    if (plant == null || plant.Destroyed || plant.thingIDNumber != rec.plantId)
                    {
                        charges.Remove(c);
                        continue;
                    }
                    RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(plant.def);
                    if (prof == null || !prof.Soaks)
                    {
                        charges.Remove(c);
                        Dirty(c);
                        continue;
                    }

                    bool wet = soakUntil.TryGetValue(c, out int until) && now < until && !IsSuppressed(c, now);
                    rec.charge = StepCharge(rec.charge, wet, plant.GrowthRate > 0f, dt, chargeTicks, rec.clockFactor);

                    if (rec.charge <= 0f)
                    {
                        charges.Remove(c);
                        Dirty(c);
                        continue;
                    }

                    UpdateTells(c, plant, rec);

                    if (rec.charge >= 1f)
                    {
                        charges.Remove(c);
                        RM_TopResolver.Fire(plant, prof, this);
                        continue;
                    }

                    if (reprint) Dirty(c);
                }
            }

            // 3. Rupture clouds.
            if (ruptures.Count > 0) TickRuptures(now);
        }

        /// <summary>
        /// One pass of the charge clock, pure so it can be self-tested
        /// (RM_ChargeSelfTest runs at startup).
        ///   wet + growing   advances: 1.0 after chargeTicks*clockFactor ticks.
        ///   wet + dormant   HOLDS. A soaked plant that cannot grow this moment
        ///                   (cold, night-dormant season, no fertility) keeps its
        ///                   charge; it is still loaded, just paused.
        ///   dry             decays — drying out defuses (SURVIVE: "keep ground
        ///                   dry"). 🄸 INVENTED: twice as fast as it charged.
        /// 2026-09-26 live-found defect: dormant used to fall into the decay
        /// branch, so on a cold map a freshly started charge (0.0001) lost
        /// 250/7500 = 0.033 in the SAME pass that created it and was removed —
        /// every pass, forever: charging read 0 on a soaked, mature plant.
        /// </summary>
        public static float StepCharge(float charge, bool wet, bool growing, int dt, float chargeTicks, float clockFactor)
        {
            if (wet && growing) return charge + dt / (chargeTicks * clockFactor);
            if (wet) return charge;
            return charge - dt / (chargeTicks * 0.5f);
        }

        private void StartCharge(IntVec3 c, Plant plant, RM_PlantProfile prof)
        {
            var rec = new RM_ChargeRecord
            {
                plantId = plant.thingIDNumber,
                charge = 0.0001f,
                stage = RM_TellStage.Ground,
                clockFactor = Rand.Range(0.9f, 1.1f),
            };
            charges[c] = rec;

            // Tell 1 — the ground darkens and sprouts (§2, "ground before sky").
            if (ExplosiveGrowthSettings.groundTellEnabled)
            {
                FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_Water);
                if (prof.top == RM_GrowthTop.Churn || prof.top == RM_GrowthTop.Burst || prof.top == RM_GrowthTop.Tinder)
                {
                    RM_SproutRing.Sow(map, c, plant.def, 1.5f, 1, respectBuiltGround: true, this, growth: 0.05f);
                }
            }
        }

        private void UpdateTells(IntVec3 c, Plant plant, RM_ChargeRecord rec)
        {
            RM_TellStage want = StageFor(rec.charge);

            if (want > rec.stage)
            {
                if (want >= RM_TellStage.Creak && rec.stage < RM_TellStage.Creak && ExplosiveGrowthSettings.tellSoundsEnabled)
                {
                    RM_ExplosiveGrowthDefOf.RM_EG_Creak?.PlayOneShot(new TargetInfo(c, map));
                }
                rec.stage = want;
                Dirty(c);
            }

            // The tremble's visible half, every pass while it lasts; the last
            // moment before the top is silent and still.
            if (rec.stage == RM_TellStage.Tremble || rec.stage == RM_TellStage.Creak)
            {
                if (Rand.Chance(0.5f)) FleckMaker.ThrowDustPuff(c, map, 0.6f);
            }
        }

        private void TickRuptures(int now)
        {
            for (int i = ruptures.Count - 1; i >= 0; i--)
            {
                RM_RuptureZone z = ruptures[i];
                if (now >= z.untilTick)
                {
                    ruptures.RemoveAt(i);
                    continue;
                }
                RM_TopResolver.RuptureExposurePulse(map, z);
            }
        }

        private void PruneExpired(int now)
        {
            PruneDict(soakUntil, now);
            PruneDict(suppressedUntil, now);
        }

        private void PruneDict(Dictionary<IntVec3, int> d, int now)
        {
            if (d.Count == 0) return;
            tmpCells.Clear();
            foreach (KeyValuePair<IntVec3, int> kv in d)
            {
                if (kv.Value <= now) tmpCells.Add(kv.Key);
            }
            for (int i = 0; i < tmpCells.Count; i++) d.Remove(tmpCells[i]);
        }

        public void Dirty(IntVec3 c)
        {
            map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Things);
        }

        public string DebugReport()
        {
            // Why a soaked plant is NOT charging, counted live — the question the
            // 2026-09-26 verify could not answer from "charging=0" alone.
            int immature = 0, dormant = 0, noSoakTop = 0, armed = 0;
            foreach (IntVec3 c in soakUntil.Keys)
            {
                Plant p = c.GetPlant(map);
                if (p == null) continue;
                RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(p.def);
                if (prof == null || !prof.Soaks) noSoakTop++;
                else if (p.Growth < MatureGrowth) immature++;
                else if (charges.ContainsKey(c)) armed++;
                else if (p.GrowthRate <= 0f) dormant++;
            }
            string why = string.Format(" | soaked plants: immature={0} matureDormant(GrowthRate 0)={1} charging={2} topNone/exempt={3}",
                immature, dormant, armed, noSoakTop);
            return Report() + why;
        }

        private string Report()
        {
            return string.Format("soaked={0} charging={1} suppressed={2} ruptures={3} biomeRefusesSoak={4} registry: soaking={5} none={6} rosterRows resolved={7} missing={8}",
                soakUntil.Count, charges.Count, suppressedUntil.Count, ruptures.Count,
                RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome),
                RM_ExplosiveGrowthRegistry.CountSoaking, RM_ExplosiveGrowthRegistry.CountNone,
                RM_ExplosiveGrowthRegistry.RosterResolved, RM_ExplosiveGrowthRegistry.RosterMissing);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref soakUntil, "soakUntil", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Collections.Look(ref suppressedUntil, "suppressedUntil", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Collections.Look(ref charges, "charges", LookMode.Value, LookMode.Deep, ref tmpKeys, ref tmpRecs);
            Scribe_Collections.Look(ref ruptures, "ruptures", LookMode.Deep);
            Scribe_Values.Look(ref irrigationCursor, "irrigationCursor", 0);
            Scribe_Values.Look(ref surgeCursor, "surgeCursor", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (soakUntil == null) soakUntil = new Dictionary<IntVec3, int>();
                if (suppressedUntil == null) suppressedUntil = new Dictionary<IntVec3, int>();
                if (charges == null) charges = new Dictionary<IntVec3, RM_ChargeRecord>();
                if (ruptures == null) ruptures = new List<RM_RuptureZone>();
                cachedMap = null;
                cachedComp = null;
            }
        }
    }
}
