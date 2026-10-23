using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
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
    // THE CELL STATE, THE CHARGE AND THE SUPPRESSION GRID — one component per map
    // (design/RimMandrake/explosive_growth_ruled_spec_2026-10-16.md §2, §7).
    //
    // A cell is WET while a live source is on it (RM_WetSources, read on demand, never ticked per cell). This component
    // holds what the sources need from the map: the timed (flood/surge) ledger, the rain clock and its used-up marks, the
    // cached channel grids, the Pyrelands ash read, and the charge records. The pass (every 250 ticks) offers a slice of
    // EVERY plant on the map to the arming step (PF1 option 2, the full-map wave; option 3, the stagger, is a setting, off).
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ExplosiveGrowth : MapComponent
    {
        public const int PassInterval = RM_ExplosiveGrowthKernel.PassInterval;   // == GenTicks.TickRareInterval (250)

        public const float SwellAt = RM_ExplosiveGrowthKernel.SwellAt;
        public const float HueAt = RM_ExplosiveGrowthKernel.HueAt;
        public const float TrembleAt = RM_ExplosiveGrowthKernel.TrembleAt;
        public const float CreakAt = RM_ExplosiveGrowthKernel.CreakAt;
        public const float SilenceAt = RM_ExplosiveGrowthKernel.SilenceAt;
        public const float MatureGrowth = RM_ExplosiveGrowthKernel.MatureGrowth;

        private readonly RM_EgLedger<IntVec3> ledger = new RM_EgLedger<IntVec3>();
        private List<RM_RuptureZone> ruptures = new List<RM_RuptureZone>();

        private int nextPassTick = -1;
        private int lastPassTick = -1;
        private int nextReprintTick = -1;
        private bool wobbleParity;

        public int irrigationCursor;   // kept for old saves; the channel is read on demand now
        public int surgeCursor;
        private int plantCursor;

        // Rain (OQ-9): saved.
        private bool wasRaining;
        private int rainStoppedAt = -1;
        private int rainLingerUntil = -1;
        private Dictionary<IntVec3, int> rainUsed = new Dictionary<IntVec3, int>();
        // Unsaved per-pass caches.
        private bool rainingNow;
        private readonly Dictionary<HashSet<string>, RimMandrake.Shared.FlowWorksIrrigationRead.Grids> channelGrids
            = new Dictionary<HashSet<string>, RimMandrake.Shared.FlowWorksIrrigationRead.Grids>();
        private int channelGridsTick = -1;
        private MapComponent ashField;
        private bool ashResolvedForMap;

        private readonly Sink sink;
        private readonly List<IntVec3> candidates = new List<IntVec3>();
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
        /// <summary>Live timed soaks only (EGROWTH_BLOOMBURST_FIX_STALE_FOOTPRINT).</summary>
        public IEnumerable<IntVec3> SoakedCells => ledger.soakUntil.Keys.Where(IsSoaked);
        public bool AnyCharging => ledger.charges.Count > 0;
        /// <summary>A no-soak biome (deep desert, HARD BAN 4): no water counts here at all.</summary>
        public bool NoWaterHere => RM_ExplosiveGrowthRegistry.IsNoSoakBiome(map.Biome);

        // ── the timed sources (flood / surge / API) ──────────────────────

        /// <summary>A timed source for <paramref name="ticks"/> (a running flood re-pushes each pulse). Refused on
        /// suppressed ground and where no water counts.</summary>
        public bool TrySoak(IntVec3 c, int ticks)
        {
            bool allowed = ExplosiveGrowthSettings.On && c.InBounds(map)
                && !RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome);
            return ledger.TrySoak(c, Find.TickManager.TicksGame, ticks, allowed);
        }

        public bool IsTimedSoaked(IntVec3 c, int now) => ledger.IsSoaked(c, now);

        /// <summary>ExplosiveGrowthAPI.IsSoaked: the cell is wet for clean water from ANY source.</summary>
        public bool IsSoaked(IntVec3 c) => IsWetFor(c, RM_ExplosiveGrowthRegistry.CleanWaterSet);

        public bool IsWetFor(IntVec3 c, HashSet<string> accepts)
            => ExplosiveGrowthSettings.On && RM_WetSources.IsWet(this, c, accepts, Find.TickManager.TicksGame);

        // ── rain (OQ-9) ──────────────────────────────────────────────────

        public bool RainWetAt(IntVec3 c, int now)
        {
            if (!rainingNow && now >= rainLingerUntil) return false;
            if (c.Roofed(map)) return false;
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.IsWater) return false;
            int used = int.MinValue;
            if (rainUsed.Count != 0 && rainUsed.TryGetValue(c, out int u)) used = u;
            return RM_ExplosiveGrowthKernel.RainWet(rainingNow, now, rainStoppedAt, rainLingerUntil, used);
        }

        /// <summary>A fruiting plant drank the rain on its cell: dry for the rest of the after-rain hours (while it still
        /// rains, the rain refills it).</summary>
        public bool ConsumeRain(IntVec3 c, int now)
        {
            if (rainingNow) return false;
            rainUsed[c] = now;
            return true;
        }

        private void UpdateRain(int now)
        {
            WeatherManager wm = map.weatherManager;
            bool raining = false;
            if (ExplosiveGrowthSettings.rainWaterEnabled && wm?.curWeather != null && wm.lastWeather != null)
            {
                raining = wm.RainRate > 0.05f || RM_ExplosiveGrowthRegistry.SoakWeathers.Contains(wm.curWeather)
                    || (ExplosiveGrowthSettings.snowmeltEnabled && wm.SnowRate > 0.05f && RM_ExplosiveGrowthRegistry.IsSnowmeltBiome(map.Biome));
            }
            if (raining && !wasRaining) rainUsed.Clear();
            if (!raining && wasRaining)
            {
                rainStoppedAt = now;
                rainLingerUntil = now + Mathf.RoundToInt(ExplosiveGrowthSettings.rainLingerHours * GenDate.TicksPerHour);
                LeavePuddles();
            }
            if (!raining && rainLingerUntil >= 0 && now >= rainLingerUntil && rainUsed.Count > 0) rainUsed.Clear();
            wasRaining = raining;
            rainingNow = raining;
        }

        /// <summary>"Shown by puddles": the after-rain wet is the clock above; the puddles are its visible reason (GM1).</summary>
        private void LeavePuddles()
        {
            ThingDef puddle = RM_ExplosiveGrowthDefOf.RM_Filth_RainPuddle;
            if (puddle == null || !ExplosiveGrowthSettings.rainPuddlesEnabled) return;
            int n = Mathf.Clamp(map.Area / 250, 20, 400);
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.Roofed(map)) continue;
                TerrainDef t = c.GetTerrain(map);
                if (t == null || t.IsWater) continue;
                FilthMaker.TryMakeFilth(c, map, puddle);
            }
        }

        // ── the channel (D5) ─────────────────────────────────────────────

        /// <summary>The FlowWorks grids for one accepted-liquid set: a pure read of the cache RefreshChannelGrids fills once per
        /// pass (§7: GrowthRate allocates nothing). The Grids hold FlowWorks' own arrays, so their contents are live; only a
        /// reallocated grid (a map resize) waits for the next pass. null = no channel water this set accepts.</summary>
        public RimMandrake.Shared.FlowWorksIrrigationRead.Grids ChannelGrids(HashSet<string> accepts)
        {
            return channelGrids.TryGetValue(accepts, out var g) ? g : null;
        }

        private void RefreshChannelGrids(int now)
        {
            channelGrids.Clear();
            channelGridsTick = now;
            if (!ExplosiveGrowthSettings.irrigationSoakEnabled || !RimMandrake.Shared.FlowWorksIrrigationRead.Available) return;
            List<HashSet<string>> sets = RM_ExplosiveGrowthRegistry.LiquidSets;
            for (int i = 0; i < sets.Count; i++)
            {
                RimMandrake.Shared.FlowWorksIrrigationRead.TryGrids(map, sets[i], out var g);
                if (g != null) channelGrids[sets[i]] = g;
            }
        }

        // ── ash (C5, OQ-11) ──────────────────────────────────────────────

        private static System.Type ashType;
        private static System.Reflection.FieldInfo burnTickField;
        private static bool ashTypeResolved;

        /// <summary>ASH-FRESH: Pyrelands' saved last-fire tick within ashFlushDays, or restarted by a seedling since.</summary>
        public bool AshFresh(IntVec3 c, int now)
        {
            if (!ExplosiveGrowthSettings.ashFreshEnabled) return false;
            if (ledger.AshRestarted(c, now)) return true;
            int[] burn = BurnTicks();
            if (burn == null) return false;
            int i = map.cellIndices.CellToIndex(c);
            if (i < 0 || i >= burn.Length || burn[i] <= 0) return false;
            return now - burn[i] < AshWindowTicks;
        }

        public static int AshWindowTicks => Mathf.RoundToInt(ExplosiveGrowthSettings.ashFlushDays * GenDate.TicksPerDay);

        /// <summary>OQ-11: a seedling appearing on fresh ash restarts the window there.</summary>
        public void NoteSeedling(IntVec3 c)
        {
            int now = Find.TickManager.TicksGame;
            if (AshFresh(c, now)) ledger.RestartAsh(c, now, AshWindowTicks);
        }

        private int[] BurnTicks()
        {
            if (!ashTypeResolved)
            {
                ashTypeResolved = true;
                try
                {
                    ashType = AccessTools.TypeByName("RimMandrake.Pyrelands.MapComponent_PyrelandsAshField");
                    if (ashType != null) burnTickField = AccessTools.Field(ashType, "burnTick");
                }
                catch (System.Exception e)
                {
                    Log.Warning("[RM ExplosiveGrowth] Pyrelands ash read failed; ash-fresh is off: " + e.Message);
                    ashType = null;
                }
            }
            if (ashType == null || burnTickField == null) return null;
            if (!ashResolvedForMap)
            {
                ashResolvedForMap = true;
                for (int k = 0; k < map.components.Count; k++)
                    if (map.components[k] != null && ashType.IsInstanceOfType(map.components[k])) { ashField = map.components[k]; break; }
            }
            return ashField != null ? burnTickField.GetValue(ashField) as int[] : null;
        }

        // ── the rule for one plant ───────────────────────────────────────

        /// <summary>Sealed in a basin / pot / hydroponics (H1: vanilla speed, no cycle).</summary>
        public bool Sealed(Plant plant)
            => ExplosiveGrowthSettings.sealedGrowersVanilla && plant.Position.GetEdifice(map) is Building_PlantGrower;

        /// <summary>The §2.5 factor r for a spawned plant on this map. Pure: no writes, no allocation (§7).</summary>
        public float MoistureFactorFor(Plant plant, RM_PlantProfile prof)
        {
            if (prof == null || !plant.Spawned) return 1f;
            BiomeDef biome = map.Biome;
            if (!RM_ExplosiveGrowthRegistry.PlantInScope(prof, biome)) return 1f;
            if (prof.archetype == RM_Archetype.Exempt) return 1f;
            bool sealedGrower = Sealed(plant);
            if (sealedGrower) return 1f;
            var s = ExplosiveGrowthSettings.Rates;
            int now = Find.TickManager.TicksGame;
            IntVec3 c = plant.Position;
            if (prof.archetype == RM_Archetype.Vanilla)
            {
                bool near = s.vanillaNeedsWater && RM_WetSources.WaterNearby(this, c, RM_ExplosiveGrowthRegistry.CleanWaterSet, ExplosiveGrowthSettings.nearbyRadius, now);
                return RM_ExplosiveGrowthKernel.MoistureFactor(prof.archetype, true, false, false, false, false, prof.woody, near, s);
            }
            bool stalled = RM_ExplosiveGrowthRegistry.IsTerminatorBiome(biome);
            bool wet = prof.archetype != RM_Archetype.WetNative && !stalled && RM_WetSources.IsWet(this, c, prof.liquids, now);
            bool ash = prof.archetype == RM_Archetype.FireAdapted && !wet && AshFresh(c, now);
            if (prof.isTree)
                return RM_ExplosiveGrowthKernel.TreeMoistureFactor(prof.archetype, true, stalled, false, wet, ash,
                    plant.Growth >= MatureGrowth, s);
            return RM_ExplosiveGrowthKernel.MoistureFactor(prof.archetype, true, stalled, false, wet, ash, prof.woody, false, s);
        }

        /// <summary>The tree rules (tree_burst_design_2026-10-17.md §3, §4, §6a) run for this tree here: in scope, not sealed,
        /// not in a stalled biome (where our plants never cycle and water does not move them). Elsewhere a tree is vanilla.</summary>
        public bool TreeRulesHere(Plant plant, RM_PlantProfile prof)
        {
            if (prof == null || !prof.isTree || !plant.Spawned) return false;
            BiomeDef biome = map.Biome;
            return RM_ExplosiveGrowthRegistry.PlantInScope(prof, biome) && !RM_ExplosiveGrowthRegistry.IsTerminatorBiome(biome)
                && !Sealed(plant);
        }

        /// <summary>The plant runs the cycle here (archetype, scope, not sealed or stalled, its top on). A tree never does: its
        /// end of life is its event (§2 table, T4).</summary>
        public bool CyclesHere(Plant plant, RM_PlantProfile prof)
        {
            if (prof == null || prof.isTree || !prof.Soaks || RM_TopResolver.Effective(prof.top) == RM_GrowthTop.None) return false;
            BiomeDef biome = map.Biome;
            return RM_ExplosiveGrowthKernel.Cycles(prof.archetype, RM_ExplosiveGrowthRegistry.PlantInScope(prof, biome),
                RM_ExplosiveGrowthRegistry.IsTerminatorBiome(biome), Sealed(plant));
        }

        public bool CycleWetFor(Plant plant, RM_PlantProfile prof, int now)
        {
            IntVec3 c = plant.Position;
            bool wet = prof.archetype != RM_Archetype.WetNative && RM_WetSources.IsWet(this, c, prof.liquids, now);
            bool ash = prof.archetype == RM_Archetype.FireAdapted && !wet && AshFresh(c, now);
            return RM_ExplosiveGrowthKernel.CycleWet(prof.archetype, wet, ash);
        }

        // ── suppression (Greentide kit M10 grazing, M2 dry-air blower) ────

        public void Suppress(IntVec3 center, int radius, int ticks)
        {
            // EGROWTH_MASTER_FIX_SPARES_THE_BANDS (owner by card: "Master stops everything"): the master switch off lays nothing.
            if (!ExplosiveGrowthSettings.On || !ExplosiveGrowthSettings.suppressionEnabled) return;
            var cells = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, Mathf.Max(0, radius) + 0.5f, true))
            {
                if (c.InBounds(map)) cells.Add(c);
            }
            ledger.Suppress(cells, Find.TickManager.TicksGame, ticks);
        }

        public bool IsSuppressed(IntVec3 c, int now) => ledger.IsSuppressed(c, now);

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

        public float HueFor(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec)) return 0f;
            return RM_ExplosiveGrowthKernel.Hue(rec.charge);
        }

        public float TakeCharge(Plant plant)
        {
            if (!TryGetCharge(plant, out RM_ChargeRecord rec)) return 0f;
            return ledger.TakeCharge(plant.Position, plant.thingIDNumber);
        }

        public float ChargeOf(Plant plant) => TryGetCharge(plant, out RM_ChargeRecord rec) ? rec.charge : 0f;

        public static RM_TellStage StageFor(float charge) => RM_ExplosiveGrowthKernel.StageFor(charge);

        public void DebugSetCharge(Plant plant, float value)
        {
            if (plant == null || !plant.Spawned) return;
            ledger.DebugSetCharge(plant.Position, plant.thingIDNumber, value);
        }

        public void AddRupture(IntVec3 center, float radius, int ticks)
        {
            ruptures.Add(new RM_RuptureZone { center = center, radius = radius, untilTick = Find.TickManager.TicksGame + ticks });
        }

        public int DebugForceCharge(float value) => ledger.DebugForceCharge(value);

        // ── the pass ─────────────────────────────────────────────────────

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now < nextPassTick) return;
            nextPassTick = now + PassInterval;
            // EGROWTH_SUPPRESS_FIX_OFF_STILL_SUPPRESSES: switching suppression off drops grids already laid.
            // EGROWTH_MASTER_FIX_SPARES_THE_BANDS: the master switch off drops them too, so nothing laid survives a master-off spell.
            if ((!ExplosiveGrowthSettings.suppressionEnabled || !ExplosiveGrowthSettings.On) && ledger.suppressedUntil.Count != 0)
                ledger.suppressedUntil.Clear();
            if (!ExplosiveGrowthSettings.On || !RM_ExplosiveGrowthRegistry.Ready)
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
            if (!RM_ExplosiveGrowthRegistry.MapMayRun(map.Biome))
            {
                // EGROWTH_SCOPE_FIX_FROZEN_CHARGES_GAMBLE: out of scope the ledger is not stepped, so drop charges instead of freezing them (a frozen charge still paid the jackpot).
                if (ledger.charges.Count != 0) ledger.charges.Clear();
                if (ruptures.Count > 0) TickRuptures(now);
                return;
            }
            UpdateRain(now);
            RefreshChannelGrids(now);
            RM_SoakSources.Pulse(this, now);

            bool reprint = now >= nextReprintTick;
            if (reprint)
            {
                nextReprintTick = now + Mathf.Max(60, ExplosiveGrowthSettings.reprintIntervalTicks);
                wobbleParity = !wobbleParity;
            }

            if (ruptures.Count > 0) TickRuptures(now);

            // The full-map wave: one eighth of every plant on the map is offered to the arming step per pass.
            candidates.Clear();
            List<Thing> plants = map.listerThings.ThingsInGroup(ThingRequestGroup.Plant);
            RM_ExplosiveGrowthKernel.SliceRange(plants.Count, plantCursor, out int start, out int end);
            plantCursor = RM_ExplosiveGrowthKernel.NextCursor(plantCursor);
            for (int i = start; i < end; i++)
            {
                Thing t = plants[i];
                if (t is Plant p && p.Spawned && p.Growth >= MatureGrowth) candidates.Add(p.Position);
            }

            float chargeTicks = RM_ExplosiveGrowthKernel.ChargeTicks(ExplosiveGrowthSettings.chargeHours);
            ledger.Pass(sink, candidates, now, dt, reprint, chargeTicks, ExplosiveGrowthSettings.tellSoundsEnabled,
                ExplosiveGrowthSettings.waveStaggerEnabled);
        }

        private sealed class Sink : IEgSink<IntVec3>
        {
            private readonly RM_MapComponent_ExplosiveGrowth comp;
            public Sink(RM_MapComponent_ExplosiveGrowth comp) { this.comp = comp; }

            public bool TryGetPlant(IntVec3 c, out int plantId, out float growth, out bool cycles)
            {
                plantId = 0; growth = 0f; cycles = false;
                Plant plant = c.GetPlant(comp.map);
                if (plant == null || plant.Destroyed) return false;
                RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(plant.def);
                plantId = plant.thingIDNumber;
                growth = plant.Growth;
                cycles = comp.CyclesHere(plant, prof);
                return true;
            }

            public bool CycleWet(IntVec3 c)
            {
                Plant plant = c.GetPlant(comp.map);
                return plant != null && comp.CycleWetFor(plant, RM_ExplosiveGrowthRegistry.For(plant.def), Find.TickManager.TicksGame);
            }

            public float GrowthRate(IntVec3 c) { return c.GetPlant(comp.map).GrowthRate; }
            public float NewClockFactor(IntVec3 c) { return Rand.Range(0.9f, 1.1f); }
            public int Hash(IntVec3 c) { return comp.map.cellIndices.CellToIndex(c); }
            public void OnDirty(IntVec3 c) { comp.Dirty(c); }

            // Tell 1 - the ground darkens (section 2, "ground before sky"). D11: no arming sprout; sprouts belong to the
            // outcome.
            public void OnArmed(IntVec3 c)
            {
                if (!ExplosiveGrowthSettings.groundTellEnabled) return;
                FilthMaker.TryMakeFilth(c, comp.map, ThingDefOf.Filth_Water);
            }

            public void OnCreak(IntVec3 c) { RM_ExplosiveGrowthDefOf.RM_EG_Creak?.PlayOneShot(new TargetInfo(c, comp.map)); }
            public void OnTellPuff(IntVec3 c) { if (Rand.Chance(0.5f)) FleckMaker.ThrowDustPuff(c, comp.map, 0.6f); }

            public void OnFire(IntVec3 c)
            {
                Plant plant = c.GetPlant(comp.map);
                RM_TopResolver.Fire(plant, RM_ExplosiveGrowthRegistry.For(plant.def), comp);
            }
        }

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
            int immature = 0, dormant = 0, noSoakTop = 0, armed = 0;
            foreach (IntVec3 c in ledger.soakUntil.Keys)
            {
                Plant p = c.GetPlant(map);
                if (p == null) continue;
                RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(p.def);
                if (prof == null || !CyclesHere(p, prof)) noSoakTop++;
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
            return string.Format("soaked={0} charging={1} suppressed={2} ruptures={3} biomeRefusesSoak={4} registry: soaking={5} none={6} rosterRows resolved={7} missing={8}"
                + " scope: biomeInScope={9} homeBiomes={10} forcedBy={11} mechanicsOn={12} raining={13} rainLingerUntil={14} ashRestarts={15} tidallyLocked={16}",
                ledger.soakUntil.Count, ledger.charges.Count, ledger.suppressedUntil.Count, ruptures.Count,
                RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome),
                RM_ExplosiveGrowthRegistry.CountSoaking, RM_ExplosiveGrowthRegistry.CountNone,
                RM_ExplosiveGrowthRegistry.RosterResolved, RM_ExplosiveGrowthRegistry.RosterMissing,
                RM_ExplosiveGrowthRegistry.BiomeInScope(map.Biome), RM_ExplosiveGrowthRegistry.HomeBiomes.Count,
                RM_ExplosiveGrowthRegistry.ScopeForcedBy ?? "none", ExplosiveGrowthSettings.On, rainingNow, rainLingerUntil,
                ledger.ashUntil.Count, RM_ExplosiveGrowthRegistry.TidallyLocked);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref ledger.soakUntil, "soakUntil", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Collections.Look(ref ledger.suppressedUntil, "suppressedUntil", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Collections.Look(ref ledger.ashUntil, "ashUntil", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Collections.Look(ref ledger.charges, "charges", LookMode.Value, LookMode.Deep, ref tmpKeys, ref tmpRecs);
            Scribe_Collections.Look(ref ruptures, "ruptures", LookMode.Deep);
            Scribe_Collections.Look(ref rainUsed, "rainUsed", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpInts);
            Scribe_Values.Look(ref wasRaining, "wasRaining", false);
            Scribe_Values.Look(ref rainStoppedAt, "rainStoppedAt", -1);
            Scribe_Values.Look(ref rainLingerUntil, "rainLingerUntil", -1);
            Scribe_Values.Look(ref irrigationCursor, "irrigationCursor", 0);
            Scribe_Values.Look(ref surgeCursor, "surgeCursor", 0);
            Scribe_Values.Look(ref plantCursor, "plantCursor", 0);
            Scribe_Values.Look(ref nextPassTick, "nextPassTick", -1);
            Scribe_Values.Look(ref lastPassTick, "lastPassTick", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                // D21: a save from the old model loads its timed soaks and charges as they were; the new keys default.
                if (ledger.soakUntil == null) ledger.soakUntil = new Dictionary<IntVec3, int>();
                if (ledger.suppressedUntil == null) ledger.suppressedUntil = new Dictionary<IntVec3, int>();
                if (ledger.ashUntil == null) ledger.ashUntil = new Dictionary<IntVec3, int>();
                if (ledger.charges == null) ledger.charges = new Dictionary<IntVec3, RM_ChargeRecord>();
                if (ruptures == null) ruptures = new List<RM_RuptureZone>();
                if (rainUsed == null) rainUsed = new Dictionary<IntVec3, int>();
                rainingNow = wasRaining;
                channelGridsTick = -1;
                cachedMap = null;
                cachedComp = null;
            }
        }
    }
}
