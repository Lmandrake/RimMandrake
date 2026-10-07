using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>The Scribe half of the charge record; the fields and the tell ladder enum live in
    /// Kernel/RM_ExplosiveGrowthKernel.cs.</summary>
    public partial class RM_ChargeRecord : IExposable
    {
        public void ExposeData()
        {
            Scribe_Values.Look(ref plantId, "plantId", 0);
            Scribe_Values.Look(ref charge, "charge", 0f);
            Scribe_Values.Look(ref stage, "stage", RM_TellStage.None);
            Scribe_Values.Look(ref clockFactor, "clockFactor", 1f);
        }
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
        public const int PassInterval = RM_ExplosiveGrowthKernel.PassInterval;   // == GenTicks.TickRareInterval (250)

        // Tell thresholds on charge 0..1. 🄸 INVENTED spacing; order is ruled.
        public const float SwellAt = RM_ExplosiveGrowthKernel.SwellAt;
        public const float HueAt = RM_ExplosiveGrowthKernel.HueAt;
        public const float TrembleAt = RM_ExplosiveGrowthKernel.TrembleAt;
        public const float CreakAt = RM_ExplosiveGrowthKernel.CreakAt;
        public const float SilenceAt = RM_ExplosiveGrowthKernel.SilenceAt;

        public const float MatureGrowth = RM_ExplosiveGrowthKernel.MatureGrowth;

        // The soak / suppression / charge ledger and its pass live in the Verse-free kernel (fuzzed offline).
        private readonly RM_EgLedger<IntVec3> ledger = new RM_EgLedger<IntVec3>();
        private List<RM_RuptureZone> ruptures = new List<RM_RuptureZone>();

        private int nextPassTick = -1;
        private int lastPassTick = -1;
        private int nextReprintTick = -1;
        private bool wobbleParity;

        // Irrigation / surge slice cursors (see RM_SoakSources).
        public int irrigationCursor;
        public int surgeCursor;

        private readonly Sink sink;
        private List<IntVec3> tmpKeys;
        private List<int> tmpInts;
        private List<RM_ChargeRecord> tmpRecs;

        private static Map cachedMap;
        private static RM_MapComponent_ExplosiveGrowth cachedComp;

        public RM_MapComponent_ExplosiveGrowth(Map map) : base(map)
        {
            sink = new Sink(this);
        }

        public static RM_MapComponent_ExplosiveGrowth For(Map map)
        {
            if (map == null) return null;
            if (map == cachedMap && cachedComp != null) return cachedComp;
            cachedComp = map.GetComponent<RM_MapComponent_ExplosiveGrowth>();
            cachedMap = map;
            return cachedComp;
        }

        public int SoakedCount => ledger.soakUntil.Count;
        public int ChargingCount => ledger.charges.Count;
        public int SuppressedCount => ledger.suppressedUntil.Count;
        public IEnumerable<IntVec3> SoakedCells => ledger.soakUntil.Keys;
        public bool AnyCharging => ledger.charges.Count > 0;

        // ── the soak ─────────────────────────────────────────────────────

        /// <summary>Soak one cell for <paramref name="ticks"/>. Extends, never
        /// shortens, an existing soak. Refused on suppressed ground and in a
        /// carve-out biome (terminator, deep desert — design doc §3).</summary>
        public bool TrySoak(IntVec3 c, int ticks)
        {
            bool allowed = ExplosiveGrowthSettings.enabled && c.InBounds(map)
                && !RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome);
            return ledger.TrySoak(c, Find.TickManager.TicksGame, ticks, allowed);
        }

        public bool IsSoaked(IntVec3 c)
        {
            return ledger.IsSoaked(c, Find.TickManager.TicksGame);
        }

        /// <summary>The soak multiplier for a plant, or 1. Called from the
        /// GrowthRate postfix; never allocates.</summary>
        public float GrowthFactorFor(Plant plant)
        {
            if (ledger.soakUntil.Count == 0) return 1f;
            RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(plant.def);
            return ledger.GrowthFactor(plant.Position, Find.TickManager.TicksGame, prof != null && prof.Soaks, ExplosiveGrowthSettings.soakMultiplier);
        }

        // ── suppression (Greentide kit M10 grazing, M2 dry-air blower) ────

        /// <summary>Encroachment pressure is SOAK: suppression refuses new soak,
        /// dries what is there, and makes a charging plant relax. It also keeps
        /// sown rings off the cell. That is the grid the Greentide kit's M2/M10
        /// hooks were waiting for.</summary>
        public void Suppress(IntVec3 center, int radius, int ticks)
        {
            if (!ExplosiveGrowthSettings.suppressionEnabled) return;
            var cells = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, Mathf.Max(0, radius) + 0.5f, true))
            {
                if (c.InBounds(map)) cells.Add(c);
            }
            ledger.Suppress(cells, Find.TickManager.TicksGame, ticks);
        }

        public bool IsSuppressed(IntVec3 c, int now)
        {
            return ledger.IsSuppressed(c, now);
        }

        // ── the charge, read by the visuals ──────────────────────────────

        public bool TryGetCharge(Plant plant, out RM_ChargeRecord rec)
        {
            rec = null;
            if (ledger.charges.Count == 0 || plant == null || !plant.Spawned) return false;
            return ledger.TryGetCharge(plant.Position, plant.thingIDNumber, out rec);
        }

        public float VisualScaleFor(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec)) return 1f;
            return RM_ExplosiveGrowthKernel.VisualScale(rec.charge, ExplosiveGrowthSettings.maxOvergrowthScale, wobbleParity);
        }

        /// <summary>0 = natural colour, 1 = fully wrong. Quantised to quarters
        /// so the tinted-graphic cache stays tiny.</summary>
        public float HueFor(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec)) return 0f;
            return RM_ExplosiveGrowthKernel.Hue(rec.charge);
        }

        /// <summary>Removes the charge and returns it, for the harvest/cut
        /// hooks. 0 if the plant was not charging.</summary>
        public float TakeCharge(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec)) return 0f;
            return ledger.TakeCharge(plant.Position, plant.thingIDNumber);
        }

        public float ChargeOf(Plant plant) => TryGetCharge(plant, out RM_ChargeRecord rec) ? rec.charge : 0f;

        /// <summary>The tell ladder for a charge (pure; UpdateTells and the proof both read it).</summary>
        public static RM_TellStage StageFor(float charge) => RM_ExplosiveGrowthKernel.StageFor(charge);

        /// <summary>EXPLOSIVE_GROWTH_PROBE_TOOL_1: put one plant at an exact charge (stage follows, no side effects).
        /// 0 removes its record.</summary>
        public void DebugSetCharge(Plant plant, float value)
        {
            if (plant == null || !plant.Spawned) return;
            ledger.DebugSetCharge(plant.Position, plant.thingIDNumber, value);
        }

        public void AddRupture(IntVec3 center, float radius, int ticks)
        {
            ruptures.Add(new RM_RuptureZone { center = center, radius = radius, untilTick = Find.TickManager.TicksGame + ticks });
        }

        /// <summary>Debug / BloomBurst: jump every charging or soaked mature
        /// plant's charge to at least <paramref name="value"/>.</summary>
        public int DebugForceCharge(float value) => ledger.DebugForceCharge(value);

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
            int dt = RM_ExplosiveGrowthKernel.PassDelta(now, lastPassTick);
            lastPassTick = now;
            Pass(now, dt);
        }

        private void Pass(int now, int dt)
        {
            ledger.PruneExpired(now);
            RM_SoakSources.Pulse(this, now);

            bool reprint = now >= nextReprintTick;
            if (reprint)
            {
                nextReprintTick = now + Mathf.Max(60, ExplosiveGrowthSettings.reprintIntervalTicks);
                wobbleParity = !wobbleParity;
            }

            // Arm what is soaked and mature, then run the charge (kernel; this component answers through Sink).
            float chargeTicks = RM_ExplosiveGrowthKernel.ChargeTicks(ExplosiveGrowthSettings.chargeHours);
            ledger.Pass(sink, now, dt, reprint, chargeTicks, ExplosiveGrowthSettings.tellSoundsEnabled);

            // 3. Rupture clouds.
            if (ruptures.Count > 0) TickRuptures(now);
        }

        /// <summary>What the kernel pass needs from the live map, and what it asks the game to do.</summary>
        private sealed class Sink : IEgSink<IntVec3>
        {
            private readonly RM_MapComponent_ExplosiveGrowth comp;
            public Sink(RM_MapComponent_ExplosiveGrowth comp) { this.comp = comp; }

            public bool TryGetPlant(IntVec3 c, out int plantId, out float growth, out bool soaks)
            {
                plantId = 0; growth = 0f; soaks = false;
                Plant plant = c.GetPlant(comp.map);
                if (plant == null || plant.Destroyed) return false;
                RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(plant.def);
                plantId = plant.thingIDNumber;
                growth = plant.Growth;
                // A top the settings have switched off (a disabled Churn is None) must not charge: the plant relaxes back to
                // normal size instead of arming, swelling and "firing" nothing, over and over.
                soaks = prof != null && prof.Soaks && RM_TopResolver.Effective(prof.top) != RM_GrowthTop.None;
                return true;
            }

            public float GrowthRate(IntVec3 c) { return c.GetPlant(comp.map).GrowthRate; }
            public float NewClockFactor(IntVec3 c) { return Rand.Range(0.9f, 1.1f); }
            public void OnDirty(IntVec3 c) { comp.Dirty(c); }

            // Tell 1 - the ground darkens and sprouts (section 2, "ground before sky").
            public void OnArmed(IntVec3 c)
            {
                Plant plant = c.GetPlant(comp.map);
                RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(plant.def);
                if (!ExplosiveGrowthSettings.groundTellEnabled) return;
                FilthMaker.TryMakeFilth(c, comp.map, ThingDefOf.Filth_Water);
                if (prof.top == RM_GrowthTop.Churn || prof.top == RM_GrowthTop.Burst || prof.top == RM_GrowthTop.Tinder)
                {
                    RM_SproutRing.Sow(comp.map, c, plant.def, 1.5f, 1, respectBuiltGround: true, comp, growth: 0.05f);
                }
            }

            public void OnCreak(IntVec3 c) { RM_ExplosiveGrowthDefOf.RM_EG_Creak?.PlayOneShot(new TargetInfo(c, comp.map)); }
            public void OnTellPuff(IntVec3 c) { if (Rand.Chance(0.5f)) FleckMaker.ThrowDustPuff(c, comp.map, 0.6f); }

            public void OnFire(IntVec3 c)
            {
                Plant plant = c.GetPlant(comp.map);
                RM_TopResolver.Fire(plant, RM_ExplosiveGrowthRegistry.For(plant.def), comp);
            }
        }

        /// <summary>The pure charge clock (kernel; RM_ChargeSelfTest runs it at startup). See
        /// RM_ExplosiveGrowthKernel.StepCharge. 2026-09-26 live-found defect: dormant used to fall into the decay
        /// branch, so a freshly started charge was removed in the pass that created it.</summary>
        public static float StepCharge(float charge, bool wet, bool growing, int dt, float chargeTicks, float clockFactor)
            => RM_ExplosiveGrowthKernel.StepCharge(charge, wet, growing, dt, chargeTicks, clockFactor);

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

        public void Dirty(IntVec3 c)
        {
            map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Things);
        }

        public string DebugReport()
        {
            // Why a soaked plant is NOT charging, counted live — the question the
            // 2026-09-26 verify could not answer from "charging=0" alone.
            int immature = 0, dormant = 0, noSoakTop = 0, armed = 0;
            foreach (IntVec3 c in ledger.soakUntil.Keys)
            {
                Plant p = c.GetPlant(map);
                if (p == null) continue;
                RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(p.def);
                if (prof == null || !prof.Soaks) noSoakTop++;
                else if (p.Growth < MatureGrowth) immature++;
                else if (ledger.charges.ContainsKey(c)) armed++;
                else if (p.GrowthRate <= 0f) dormant++;
            }
            string why = string.Format(" | soaked plants: immature={0} matureDormant(GrowthRate 0)={1} charging={2} topNone/exempt={3}",
                immature, dormant, armed, noSoakTop);
            return Report() + why;
        }

        private string Report()
        {
            return string.Format("soaked={0} charging={1} suppressed={2} ruptures={3} biomeRefusesSoak={4} registry: soaking={5} none={6} rosterRows resolved={7} missing={8}",
                ledger.soakUntil.Count, ledger.charges.Count, ledger.suppressedUntil.Count, ruptures.Count,
                RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome),
                RM_ExplosiveGrowthRegistry.CountSoaking, RM_ExplosiveGrowthRegistry.CountNone,
                RM_ExplosiveGrowthRegistry.RosterResolved, RM_ExplosiveGrowthRegistry.RosterMissing);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref ledger.soakUntil, "soakUntil", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Collections.Look(ref ledger.suppressedUntil, "suppressedUntil", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Collections.Look(ref ledger.charges, "charges", LookMode.Value, LookMode.Deep, ref tmpKeys, ref tmpRecs);
            Scribe_Collections.Look(ref ruptures, "ruptures", LookMode.Deep);
            Scribe_Values.Look(ref irrigationCursor, "irrigationCursor", 0);
            Scribe_Values.Look(ref surgeCursor, "surgeCursor", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (ledger.soakUntil == null) ledger.soakUntil = new Dictionary<IntVec3, int>();
                if (ledger.suppressedUntil == null) ledger.suppressedUntil = new Dictionary<IntVec3, int>();
                if (ledger.charges == null) ledger.charges = new Dictionary<IntVec3, RM_ChargeRecord>();
                if (ruptures == null) ruptures = new List<RM_RuptureZone>();
                cachedMap = null;
                cachedComp = null;
            }
        }
    }
}
