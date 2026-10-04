using System.Collections.Generic;
using System.Text;
using RimMandrake.EnvironmentalHazards;
using RimMandrake.FlowWorks;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.TheForge
{
    public enum ForgeCyclePhase
    {
        StillHeat = 0,
        GasWash = 1,
        Rain = 2,
        Freeze = 3,
        Growth = 4,
        Cracks = 5,
        Melt = 6,
    }

    // ════════════════════════════════════════════════════════════════════
    // FORGE_CYCLE_MECHANICS_1 — the Forge's fire-and-water grand cycle.
    //
    // This EXTENDS FORGE_MECHANICS_1's F1 pulse; it does not re-author it.
    // RM_GameCondition_WeatherPulse (EnvironmentalHazards) still owns the
    // burst: its weather switch, its scald damage, its flash window. This
    // subclass adds a phase clock around it:
    //
    //   1 StillHeat  base weather; the pulse's ordinary random bursts still
    //                roll (only here). Near the end, the hiss letter.
    //   2 GasWash    superheated gas bursts light flammable ground in
    //                swathes (vanilla fire via FireUtility.TryStartFireIn).
    //   3 Rain       ForceBurst for the whole phase = torrential boiling
    //                rain with the pulse's own scald damage; FlowWorks water
    //                releases flood open ground.
    //   4 Freeze     steam weather; lava cells crust over, in batches, into
    //                TEMPORARY basalt shingle / pumice on the 1.6 temp-terrain
    //                layer (TerrainGrid.SetTempTerrain, saved in tempGrid).
    //   5 Growth     floatstone gardens bloom on the crust; the flash window
    //                (RUT_Plant_FlashFlora's clock) spans the phase.
    //   6 Cracks     unharvested gardens tear free and drift off (counted,
    //                messaged); the crust turns to glowing-crack terrain.
    //     Melt       the temp layer is removed in batches, so the lava that
    //                was never touched underneath returns. Whatever stands on
    //                a melting cell is burned and destroyed (or, with the
    //                destroy toggle off, moved to safe ground) — never
    //                vanished silently; every loss is counted and messaged.
    //
    // Walkability: DoTerrainChangedEffects calls
    // PathGrid.RecalculatePerceivedPathCostAt, which re-derives walkability
    // and dirties regions (RimSage, TerrainGrid/PathGrid 1.6), so crust over
    // impassable LavaDeep becomes walkable and back without extra calls.
    //
    // State reads for a quicktest: Phase, PhaseEndTick, FrozenCellCount and
    // the Stat* counters below; RM_ForgeCycleDebugActions drives phases.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GameCondition_ForgeCycle : RM_GameCondition_WeatherPulse
    {
        private const float TicksPerHour = 2500f;
        private const int CycleInterval = 60;

        private ForgeCyclePhase phase = ForgeCyclePhase.StillHeat;
        private int phaseStartTick = -1;
        private int phaseEndTick = -1;
        private bool hissSent;
        private int gasWavesLeft;
        private int nextGasWaveTick = -1;
        private int floodsLeft;
        private int nextFloodTick = -1;
        private bool gardensSeeded;

        // FORGE_CYCLE_MECHANICS_1, the dhuvvox mass eruption ("erupt by the hundred" for the rain window, then
        // reseal). PROVISIONAL numbers (owner ruling 2026-10-03, tuned live later): SwarmSize extra dhuvvox per
        // rain, placed within SwarmSpread cells of a resident dhuvvox (else anywhere unroofed). At the end of the
        // rain every surviving swarm member burrows back: an ash scar (Filth_Ash) where it went down and ONE
        // counted message, so nothing vanishes without a sign. Toggle: dhuvvoxSwarmEnabled.
        public const int SwarmSize = 60;           // PROVISIONAL
        public const float SwarmSpread = 12f;      // PROVISIONAL
        private List<Pawn> swarm = new List<Pawn>();
        public int StatSwarmErupted;
        public int StatSwarmResealed;
        public int SwarmLive => swarm.Count;

        // Every cell currently carrying our crust (basalt, pumice or crack).
        private HashSet<IntVec3> frozenCells = new HashSet<IntVec3>();
        private List<Thing> gardens = new List<Thing>();

        // Counters for state reads (quicktest criteria).
        public int StatCycles;
        public int StatGasIgnitions;
        public int StatFloodReleases;
        public int StatCellsFrozen;
        public int StatCellsMelted;
        public int StatGardensSpawned;
        public int StatGardensDrifted;
        public int StatMeltDestroyed;
        public int StatMeltPawnsBurned;
        public int StatMeltRelocated;

        // Transient work queue for the batched phases; rebuilt on demand.
        private List<IntVec3> workQueue;
        private ForgeCyclePhase workQueuePhase = (ForgeCyclePhase)(-1);

        // Per-melt summary, flushed as one message per batch with losses.
        private readonly Dictionary<string, int> meltLosses = new Dictionary<string, int>();

        // FORGE_GPT_ENRICHMENT_1 §3: the phase sounds. Unsaved: a sustainer
        // is rebuilt from the saved phase on the first tick after load.
        private readonly RM_ForgeVoices voices = new RM_ForgeVoices();

        public ForgeCyclePhase Phase => phase;
        public int PhaseEndTick => phaseEndTick;
        public int FrozenCellCount => frozenCells.Count;
        public IEnumerable<IntVec3> FrozenCells => frozenCells;

        /// <summary>A random crusted cell, or Invalid. For the cooling-basalt
        /// voice; O(n) in the crust size but called at most every 90 ticks.</summary>
        public IntVec3 RandomFrozenCell()
        {
            if (frozenCells.Count == 0)
            {
                return IntVec3.Invalid;
            }
            int skip = Rand.Range(0, frozenCells.Count);
            foreach (IntVec3 c in frozenCells)
            {
                if (skip-- == 0)
                {
                    return c;
                }
            }
            return IntVec3.Invalid;
        }

        private RM_ForgeCycleExtension CycleExt => def != null ? def.GetModExtension<RM_ForgeCycleExtension>() : null;

        public static bool CycleActive
        {
            get { return RM_TheForgeSettings.Active(RM_TheForgeSettings.grandCycleEnabled); }
        }

        private Map MapOrNull
        {
            get
            {
                List<Map> maps = AffectedMaps;
                return maps != null && maps.Count > 0 ? maps[0] : null;
            }
        }

        // ── pulse seams ────────────────────────────────────────────────

        protected override bool AllowRandomBurstNow()
        {
            // The ordinary short bursts belong to the still heat only; with
            // the cycle off, the pulse behaves exactly as it always did.
            return !CycleActive || CycleExt == null || phase == ForgeCyclePhase.StillHeat;
        }

        protected override WeatherDef NonBurstWeatherOverride()
        {
            RM_ForgeCycleExtension ext = CycleExt;
            if (ext == null || !CycleActive)
            {
                return null;
            }
            // The freeze is the steam: rain on lava. Every other phase keeps
            // the pulse's own base weather.
            if (phase == ForgeCyclePhase.Freeze && ext.freezeWeather != null)
            {
                return ext.freezeWeather;
            }
            return null;
        }

        public override string Description
        {
            get
            {
                if (CycleExt == null || !CycleActive)
                {
                    return base.Description;
                }
                StringBuilder sb = new StringBuilder(base.Description);
                sb.AppendLine();
                sb.AppendLine();
                sb.Append("Phase: " + PhaseLabel(phase));
                if (phaseEndTick > 0)
                {
                    int left = Mathf.Max(0, phaseEndTick - Find.TickManager.TicksGame);
                    sb.Append(" (" + left.ToStringTicksToPeriod() + " left)");
                }
                if (frozenCells.Count > 0)
                {
                    sb.AppendLine();
                    sb.Append("Crusted cells: " + frozenCells.Count);
                }
                return sb.ToString();
            }
        }

        public override void End()
        {
            voices.Stop();
            base.End();
        }

        public static string PhaseLabel(ForgeCyclePhase p)
        {
            switch (p)
            {
                case ForgeCyclePhase.StillHeat: return "still heat";
                case ForgeCyclePhase.GasWash: return "gas wash";
                case ForgeCyclePhase.Rain: return "boiling rain";
                case ForgeCyclePhase.Freeze: return "the freeze";
                case ForgeCyclePhase.Growth: return "the growth";
                case ForgeCyclePhase.Cracks: return "glowing cracks";
                case ForgeCyclePhase.Melt: return "the melt";
            }
            return p.ToString();
        }

        // ── tick ───────────────────────────────────────────────────────

        public override void GameConditionTick()
        {
            base.GameConditionTick();

            Map map = MapOrNull;
            RM_ForgeCycleExtension ext = CycleExt;
            if (ext != null)
            {
                voices.Tick(this, map, hissSent);
            }
            if (map == null || ext == null || !map.IsHashIntervalTick(CycleInterval))
            {
                return;
            }

            // The cycle rides the pulse: if the pulse itself is gated off, or
            // the cycle toggle is off, no phase advances. Crust left standing
            // melts back gently (no damage) so nothing is stranded.
            if (!CycleActive || !RM_MechanicGates.Enabled(def))
            {
                if (frozenCells.Count > 0)
                {
                    MeltBatch(map, ext, gentle: true, batch: 200);
                }
                return;
            }

            int now = Find.TickManager.TicksGame;
            if (phaseEndTick < 0)
            {
                EnterPhase(map, ext, ForgeCyclePhase.StillHeat, now);
                return;
            }

            DoPhaseWork(map, ext, now);

            if (now >= phaseEndTick)
            {
                AdvancePhase(map, ext, now);
            }
        }

        private void DoPhaseWork(Map map, RM_ForgeCycleExtension ext, int now)
        {
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat:
                    if (!hissSent && phaseEndTick - now <= ext.hissLeadHours * TicksPerHour
                        && RM_TheForgeSettings.Active(RM_TheForgeSettings.gasWashEnabled))
                    {
                        hissSent = true;
                        Telegraph(map, "A hiss in the vents",
                            "The vents have begun to hiss, a note that swells by the minute. Superheated gas is building under the mountain; when it bursts, anything that can burn on open ground will. Get people and stores under a roof or onto bare rock.",
                            LetterDefOf.ThreatSmall, TargetInfo.Invalid);
                    }
                    break;

                case ForgeCyclePhase.GasWash:
                    if (gasWavesLeft > 0 && now >= nextGasWaveTick)
                    {
                        gasWavesLeft--;
                        GasWashWave(map, ext);
                        int span = Mathf.Max(1, phaseEndTick - now);
                        nextGasWaveTick = now + (gasWavesLeft > 0 ? span / (gasWavesLeft + 1) : span);
                    }
                    break;

                case ForgeCyclePhase.Rain:
                    if (floodsLeft > 0 && now >= nextFloodTick)
                    {
                        floodsLeft--;
                        if (RM_TheForgeSettings.Active(RM_TheForgeSettings.cycleFloodingEnabled))
                        {
                            TryFloodRelease(map, ext);
                        }
                        int span = Mathf.Max(1, phaseEndTick - now);
                        nextFloodTick = now + (floodsLeft > 0 ? span / (floodsLeft + 1) : span);
                    }
                    break;

                case ForgeCyclePhase.Freeze:
                    if (RM_TheForgeSettings.Active(RM_TheForgeSettings.lavaFreezeEnabled))
                    {
                        FreezeBatch(map, ext, now);
                    }
                    break;

                case ForgeCyclePhase.Growth:
                    if (!gardensSeeded)
                    {
                        gardensSeeded = true;
                        if (RM_TheForgeSettings.Active(RM_TheForgeSettings.floatstoneBloomEnabled))
                        {
                            SeedGardens(map, ext);
                        }
                    }
                    break;

                case ForgeCyclePhase.Cracks:
                    CrackBatch(map, ext, now);
                    break;

                case ForgeCyclePhase.Melt:
                    MeltBatch(map, ext, gentle: !RM_TheForgeSettings.Active(RM_TheForgeSettings.meltBackDestroys),
                        batch: BatchSize(frozenCells.Count, now, phaseEndTick, 0.8f));
                    break;
            }
        }

        private void AdvancePhase(Map map, RM_ForgeCycleExtension ext, int now)
        {
            ForgeCyclePhase next;
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat: next = ForgeCyclePhase.GasWash; break;
                case ForgeCyclePhase.GasWash: next = ForgeCyclePhase.Rain; break;
                case ForgeCyclePhase.Rain: next = ForgeCyclePhase.Freeze; break;
                case ForgeCyclePhase.Freeze:
                    // Nothing crusted (no lava on this map, or the freeze is
                    // switched off): growth, cracks and melt have nothing to
                    // stand on, so the cycle closes early.
                    next = frozenCells.Count > 0 ? ForgeCyclePhase.Growth : ForgeCyclePhase.StillHeat;
                    break;
                case ForgeCyclePhase.Growth: next = ForgeCyclePhase.Cracks; break;
                case ForgeCyclePhase.Cracks: next = ForgeCyclePhase.Melt; break;
                case ForgeCyclePhase.Melt:
                    if (frozenCells.Count > 0)
                    {
                        // Finish the melt before closing: no crust outlives
                        // its cycle.
                        MeltBatch(map, ext, gentle: !RM_TheForgeSettings.Active(RM_TheForgeSettings.meltBackDestroys), batch: frozenCells.Count);
                    }
                    next = ForgeCyclePhase.StillHeat;
                    StatCycles++;
                    break;
                default: next = ForgeCyclePhase.StillHeat; break;
            }
            EnterPhase(map, ext, next, now);
        }

        /// <summary>Public so the debug actions / a bridge tool can step the
        /// cycle deterministically.</summary>
        public void DebugAdvancePhase()
        {
            Map map = MapOrNull;
            RM_ForgeCycleExtension ext = CycleExt;
            if (map == null || ext == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (phaseEndTick < 0)
            {
                EnterPhase(map, ext, ForgeCyclePhase.StillHeat, now);
                return;
            }
            // Let the leaving phase's batched work finish first, so a forced
            // step leaves the same terrain a natural one would.
            FinishPhaseWork(map, ext, now);
            AdvancePhase(map, ext, now);
        }

        private void FinishPhaseWork(Map map, RM_ForgeCycleExtension ext, int now)
        {
            if (phase == ForgeCyclePhase.Freeze && RM_TheForgeSettings.Active(RM_TheForgeSettings.lavaFreezeEnabled))
            {
                int guard = 0;
                while (guard++ < 1000 && FreezeBatch(map, ext, phaseEndTick)) { }
            }
            else if (phase == ForgeCyclePhase.Growth && !gardensSeeded)
            {
                gardensSeeded = true;
                if (RM_TheForgeSettings.Active(RM_TheForgeSettings.floatstoneBloomEnabled))
                {
                    SeedGardens(map, ext);
                }
            }
            else if (phase == ForgeCyclePhase.Cracks)
            {
                int guard = 0;
                while (guard++ < 1000 && CrackBatch(map, ext, phaseEndTick)) { }
            }
        }

        private void EnterPhase(Map map, RM_ForgeCycleExtension ext, ForgeCyclePhase next, int now)
        {
            phase = next;
            phaseStartTick = now;
            phaseEndTick = now + Mathf.Max(CycleInterval, Mathf.RoundToInt(HoursFor(ext, next).RandomInRange * TicksPerHour));
            workQueue = null;

            switch (next)
            {
                case ForgeCyclePhase.StillHeat:
                    hissSent = false;
                    gardensSeeded = false;
                    break;

                case ForgeCyclePhase.GasWash:
                    if (RM_TheForgeSettings.Active(RM_TheForgeSettings.gasWashEnabled))
                    {
                        gasWavesLeft = Mathf.Max(1, ext.gasWashWaves.RandomInRange);
                        nextGasWaveTick = now;
                    }
                    else
                    {
                        gasWavesLeft = 0;
                    }
                    break;

                case ForgeCyclePhase.Rain:
                    // The whole phase is one long burst: the pulse's own
                    // weather, scald damage and flash window, exactly as a
                    // rolled burst gets them. The shared pulse switch still
                    // rules: with it off there is no burst to force.
                    if (RM_EnvironmentalHazardsSettings.weatherPulseEnabled)
                    {
                        ForceBurst(phaseEndTick - now);
                    }
                    floodsLeft = Mathf.Max(0, ext.floodReleases.RandomInRange);
                    nextFloodTick = now + Mathf.RoundToInt(0.5f * TicksPerHour);
                    EruptSwarm(map);
                    break;

                case ForgeCyclePhase.Freeze:
                    ResealSwarm(map);
                    if (frozenCells.Count == 0 && RM_TheForgeSettings.Active(RM_TheForgeSettings.lavaFreezeEnabled)
                        && CountFreezable(map, ext) > 0)
                    {
                        Telegraph(map, "The freeze",
                            "The rain has hit the lava and the whole mountain is steaming. Where the seams ran open, the melt is crusting over into basalt shingle and pumice rubble you can walk on. It will not last: the crust is a skin, and the fire underneath has not gone anywhere.",
                            LetterDefOf.PositiveEvent, TargetInfo.Invalid);
                    }
                    break;

                case ForgeCyclePhase.Growth:
                {
                    // The flash-flora window runs on the same clock as the
                    // growth (item spec, phase 5).
                    RM_MapComponent_FlashCycle flash = map.GetComponent<RM_MapComponent_FlashCycle>();
                    if (flash != null)
                    {
                        flash.StartWindow(now, phaseEndTick - now);
                    }
                    break;
                }

                case ForgeCyclePhase.Cracks:
                    DriftOffGardens(map);
                    if (frozenCells.Count > 0)
                    {
                        IntVec3 any = IntVec3.Invalid;
                        foreach (IntVec3 c in frozenCells) { any = c; break; }
                        Telegraph(map, "Glowing cracks",
                            "Red light is showing through the crust. The frozen seams are cracking open from below and will melt back into lava in "
                            + (phaseEndTick - now).ToStringTicksToPeriod()
                            + ". Anything standing on the crust when it goes will burn with it.",
                            LetterDefOf.ThreatBig, any.IsValid ? new TargetInfo(any, map) : TargetInfo.Invalid);
                    }
                    break;

                case ForgeCyclePhase.Melt:
                    if (frozenCells.Count > 0)
                    {
                        Telegraph(map, "The melt",
                            "The crust is going. The seams are running open again.",
                            LetterDefOf.ThreatSmall, TargetInfo.Invalid);
                    }
                    break;
            }
        }

        private static FloatRange HoursFor(RM_ForgeCycleExtension ext, ForgeCyclePhase p)
        {
            switch (p)
            {
                case ForgeCyclePhase.StillHeat: return ext.stillHours;
                case ForgeCyclePhase.GasWash: return ext.gasWashHours;
                case ForgeCyclePhase.Rain: return ext.rainHours;
                case ForgeCyclePhase.Freeze: return ext.freezeHours;
                case ForgeCyclePhase.Growth: return ext.growthHours;
                case ForgeCyclePhase.Cracks: return ext.cracksHours;
                case ForgeCyclePhase.Melt: return ext.meltHours;
            }
            return new FloatRange(1f, 1f);
        }

        private static void Telegraph(Map map, string label, string text, LetterDef letterDef, TargetInfo target)
        {
            if (!RM_TheForgeSettings.cycleTelegraphLetters)
            {
                return;
            }
            Find.LetterStack.ReceiveLetter(label, text, letterDef, target.IsValid ? new LookTargets(target) : new LookTargets(new TargetInfo(map.Center, map)));
        }

        // Spread a whole phase's work over the first `share` of its length.
        private int BatchSize(int remaining, int now, int end, float share)
        {
            int ticksLeft = Mathf.Max(CycleInterval, Mathf.RoundToInt((end - phaseStartTick) * share) - (now - phaseStartTick));
            int batchesLeft = Mathf.Max(1, ticksLeft / CycleInterval);
            return Mathf.Max(1, Mathf.CeilToInt(remaining / (float)batchesLeft));
        }

        // ── phase 2: gas wash ─────────────────────────────────────────

        private void GasWashWave(Map map, RM_ForgeCycleExtension ext)
        {
            IntVec3 center = CellFinderLoose.RandomCellWith(c => !c.Roofed(map) && HasFlammableGround(c, map), map, 400);
            if (!center.IsValid)
            {
                return;
            }
            int lit = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, ext.gasWashRadius, true))
            {
                if (!c.InBounds(map) || c.Roofed(map) || !Rand.Chance(ext.gasWashCellChance) || !HasFlammableGround(c, map))
                {
                    continue;
                }
                if (FireUtility.TryStartFireIn(c, map, ext.gasWashFireSize.RandomInRange, null))
                {
                    lit++;
                }
            }
            FleckMaker.ThrowHeatGlow(center, map, 3f);
            FleckMaker.ThrowSmoke(center.ToVector3Shifted(), map, 3f);
            if (RM_ForgeVoices.Enabled && Find.CurrentMap == map)
            {
                // §3: each wave bursts from a coughing vent.
                RM_TheForgeDefOf.RM_ForgeVoice_VentCough?.PlayOneShot(SoundInfo.InMap(new TargetInfo(center, map)));
            }
            StatGasIgnitions += lit;
            if (lit > 0)
            {
                Messages.Message("A burst of superheated gas washes across the ground and sets it alight.",
                    new TargetInfo(center, map), MessageTypeDefOf.NegativeEvent);
            }
        }

        private static bool HasFlammableGround(IntVec3 c, Map map)
        {
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Plant && things[i].FlammableNow)
                {
                    return true;
                }
            }
            return false;
        }

        // ── phase 3: flooding ─────────────────────────────────────────

        private void TryFloodRelease(Map map, RM_ForgeCycleExtension ext)
        {
            ThingDef floodDef = RimMandrakeFlowWorks_DefOf.RM_FluidCanalFlood;
            FluidDef water = RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
            if (floodDef == null || water == null)
            {
                return;
            }
            IntVec3 epicenter = CellFinderLoose.RandomCellWith(c =>
                c.Standable(map) && !c.Roofed(map) && !frozenCells.Contains(c)
                && !c.GetTerrain(map).dangerous && !c.GetTerrain(map).IsWater, map, 400);
            if (!epicenter.IsValid)
            {
                return;
            }
            float volume = Mathf.Max(1, ext.floodTilesPerRelease) * Mathf.Max(0.0001f, water.volumePerTile);
            Flood_FlowWorks flood = (Flood_FlowWorks)ThingMaker.MakeThing(floodDef);
            flood.Configure(water, volume);
            GenSpawn.Spawn(flood, epicenter, map);
            StatFloodReleases++;
            Messages.Message("The boiling rain is pooling and running across the ground.",
                new TargetInfo(epicenter, map), MessageTypeDefOf.NeutralEvent);
        }

        // ── phase 4: the freeze ───────────────────────────────────────

        private static bool IsFreezable(IntVec3 c, Map map, RM_ForgeCycleExtension ext)
        {
            if (map.terrainGrid.TempTerrainAt(c) != null || map.terrainGrid.FoundationAt(c) != null)
            {
                return false;
            }
            TerrainDef t = map.terrainGrid.TerrainAt(c);
            return t != null && ext.freezableTerrains.Contains(t);
        }

        private static int CountFreezable(Map map, RM_ForgeCycleExtension ext)
        {
            if (ext.freezableTerrains.NullOrEmpty())
            {
                return 0;
            }
            int n = 0;
            foreach (IntVec3 c in map.AllCells)
            {
                if (IsFreezable(c, map, ext))
                {
                    n++;
                }
            }
            return n;
        }

        // Returns true while work remains.
        private bool FreezeBatch(Map map, RM_ForgeCycleExtension ext, int now)
        {
            if (ext.basaltTerrain == null || ext.freezableTerrains.NullOrEmpty())
            {
                return false;
            }
            if (workQueue == null || workQueuePhase != ForgeCyclePhase.Freeze)
            {
                workQueue = new List<IntVec3>();
                foreach (IntVec3 c in map.AllCells)
                {
                    if (IsFreezable(c, map, ext))
                    {
                        workQueue.Add(c);
                    }
                }
                workQueue.Shuffle();
                int room = Mathf.Max(0, ext.maxFrozenCells - frozenCells.Count);
                if (workQueue.Count > room)
                {
                    workQueue.RemoveRange(room, workQueue.Count - room);
                }
                workQueuePhase = ForgeCyclePhase.Freeze;
            }
            if (workQueue.Count == 0)
            {
                return false;
            }
            int n = Mathf.Min(workQueue.Count, BatchSize(workQueue.Count, now, phaseEndTick, 0.6f));
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = workQueue[workQueue.Count - 1];
                workQueue.RemoveAt(workQueue.Count - 1);
                if (!IsFreezable(c, map, ext))
                {
                    continue;
                }
                TerrainDef crust = ext.pumiceTerrain != null && Rand.Chance(ext.pumiceChance) ? ext.pumiceTerrain : ext.basaltTerrain;
                map.terrainGrid.SetTempTerrain(c, crust);
                frozenCells.Add(c);
                StatCellsFrozen++;
                RM_MapComponent_PlumeFronts.Of(map)?.NoteCrusted(c);   // FORGE_WHITE_PLUME_FRONTS_1
                if (Rand.Chance(0.08f))
                {
                    FleckMaker.ThrowSmoke(c.ToVector3Shifted(), map, Rand.Range(1.5f, 3.5f));
                }
            }
            return workQueue.Count > 0;
        }

        // ── phase 5: the growth ───────────────────────────────────────

        private void SeedGardens(Map map, RM_ForgeCycleExtension ext)
        {
            if (ext.gardenDef == null || frozenCells.Count == 0)
            {
                return;
            }
            List<IntVec3> candidates = new List<IntVec3>();
            foreach (IntVec3 c in frozenCells)
            {
                if (c.Standable(map) && c.GetFirstItem(map) == null && c.GetPlant(map) == null && c.GetEdifice(map) == null)
                {
                    candidates.Add(c);
                }
            }
            candidates.Shuffle();
            int want = Mathf.Min(candidates.Count, ext.gardenCount.RandomInRange);
            for (int i = 0; i < want; i++)
            {
                Plant garden = ThingMaker.MakeThing(ext.gardenDef) as Plant;
                if (garden == null)
                {
                    return;
                }
                garden.Growth = ext.gardenStartGrowth;
                GenSpawn.Spawn(garden, candidates[i], map);
                gardens.Add(garden);
                StatGardensSpawned++;
            }
        }

        private void DriftOffGardens(Map map)
        {
            int drifted = 0;
            IntVec3 last = IntVec3.Invalid;
            for (int i = gardens.Count - 1; i >= 0; i--)
            {
                Thing g = gardens[i];
                if (g != null && g.Spawned && !g.Destroyed && g.Map == map)
                {
                    last = g.Position;
                    FleckMaker.ThrowDustPuffThick(g.DrawPos, map, 2f, new Color(0.95f, 0.92f, 0.85f));
                    g.Destroy(DestroyMode.Vanish);
                    drifted++;
                }
            }
            gardens.Clear();
            StatGardensDrifted += drifted;
            if (drifted > 0)
            {
                Messages.Message(drifted + " unharvested floatstone garden" + (drifted == 1 ? " has" : "s have")
                    + " torn free of the crust and drifted away over the seams.",
                    new TargetInfo(last, map), MessageTypeDefOf.NeutralEvent);
            }
        }

        // ── phase 6: cracks and melt ──────────────────────────────────

        private bool CrackBatch(Map map, RM_ForgeCycleExtension ext, int now)
        {
            if (ext.crackTerrain == null)
            {
                return false;
            }
            if (workQueue == null || workQueuePhase != ForgeCyclePhase.Cracks)
            {
                workQueue = new List<IntVec3>(frozenCells);
                workQueue.Shuffle();
                workQueuePhase = ForgeCyclePhase.Cracks;
            }
            if (workQueue.Count == 0)
            {
                return false;
            }
            int n = Mathf.Min(workQueue.Count, BatchSize(workQueue.Count, now, phaseEndTick, 0.5f));
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = workQueue[workQueue.Count - 1];
                workQueue.RemoveAt(workQueue.Count - 1);
                if (!IsOurCrust(map.terrainGrid.TempTerrainAt(c), ext) || map.terrainGrid.TempTerrainAt(c) == ext.crackTerrain)
                {
                    continue;
                }
                map.terrainGrid.SetTempTerrain(c, ext.crackTerrain);
            }
            return workQueue.Count > 0;
        }

        private static bool IsOurCrust(TerrainDef t, RM_ForgeCycleExtension ext)
        {
            return t != null && (t == ext.basaltTerrain || t == ext.pumiceTerrain || t == ext.crackTerrain);
        }

        private void MeltBatch(Map map, RM_ForgeCycleExtension ext, bool gentle, int batch)
        {
            if (frozenCells.Count == 0)
            {
                return;
            }
            if (workQueue == null || workQueuePhase != ForgeCyclePhase.Melt)
            {
                workQueue = new List<IntVec3>(frozenCells);
                workQueue.Shuffle();
                workQueuePhase = ForgeCyclePhase.Melt;
            }
            meltLosses.Clear();
            IntVec3 lossAt = IntVec3.Invalid;
            int n = Mathf.Min(workQueue.Count, batch);
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = workQueue[workQueue.Count - 1];
                workQueue.RemoveAt(workQueue.Count - 1);
                frozenCells.Remove(c);
                if (!IsOurCrust(map.terrainGrid.TempTerrainAt(c), ext))
                {
                    // Someone else's temp terrain now sits here (a lava flow,
                    // a bridge): not ours to remove.
                    continue;
                }
                if (MeltCell(map, ext, c, gentle))
                {
                    lossAt = c;
                }
                StatCellsMelted++;
            }
            if (workQueue.Count == 0)
            {
                // Stale entries (already removed from frozenCells elsewhere)
                // leave the queue empty early; resync from the set.
                workQueue = null;
            }
            if (meltLosses.Count > 0)
            {
                StringBuilder sb = new StringBuilder("The melt has taken ");
                bool first = true;
                foreach (KeyValuePair<string, int> kv in meltLosses)
                {
                    if (!first) sb.Append(", ");
                    first = false;
                    sb.Append(kv.Value > 1 ? kv.Value + "x " + kv.Key : kv.Key);
                }
                sb.Append('.');
                Messages.Message(sb.ToString(), new TargetInfo(lossAt, map), MessageTypeDefOf.NegativeEvent);
            }
        }

        // Returns true when something on the cell was lost.
        private bool MeltCell(Map map, RM_ForgeCycleExtension ext, IntVec3 c, bool gentle)
        {
            bool lost = false;
            List<Thing> snapshot = new List<Thing>(c.GetThingList(map));

            // Burn/destroy first, while the pawn is still standing on
            // walkable crust (damage on an impassable cell is legal, but a
            // relocation there is not).
            for (int i = 0; i < snapshot.Count; i++)
            {
                Thing t = snapshot[i];
                if (t == null || t.Destroyed || !t.Spawned)
                {
                    continue;
                }
                if (t is Pawn pawn)
                {
                    if (!gentle)
                    {
                        for (int h = 0; h < ext.meltPawnBurnHits && !pawn.Dead; h++)
                        {
                            pawn.TakeDamage(new DamageInfo(DamageDefOf.Flame, ext.meltPawnBurn));
                        }
                        StatMeltPawnsBurned++;
                        if (pawn.Dead)
                        {
                            AddLoss(pawn.LabelShort);
                            lost = true;
                        }
                        else if (pawn.Spawned)
                        {
                            pawn.TryAttachFire(0.5f, null);
                        }
                    }
                    continue;
                }
                if (t.def.category == ThingCategory.Mote || t.def.category == ThingCategory.Ethereal
                    || t.def.category == ThingCategory.Filth || t.def.category == ThingCategory.Attachment
                    || t is Fire)
                {
                    continue;
                }
                // Gentle mode spares what can be moved (pawns, items) or
                // taken down (buildings, below); a plant can be neither, and
                // one left standing would root in open lava.
                if (gentle && !(t is Plant))
                {
                    continue;
                }
                string label = t.LabelNoCount;
                t.Kill(new DamageInfo(DamageDefOf.Flame, 9999f));
                AddLoss(label);
                lost = true;
            }

            map.terrainGrid.RemoveTempTerrain(c, doLeavings: false, preventDestroyEffects: true);
            if (Rand.Chance(0.15f))
            {
                FleckMaker.ThrowHeatGlow(c, map, 1.5f);
            }

            // Whatever survived (pawns, and in gentle mode everything
            // haulable) is moved off ground it can no longer stand on.
            List<Thing> after = new List<Thing>(c.GetThingList(map));
            for (int i = 0; i < after.Count; i++)
            {
                Thing t = after[i];
                if (t == null || !t.Spawned || c.Standable(map))
                {
                    continue;
                }
                if (t is Pawn pawn)
                {
                    if (TryFindSafeCell(map, c, out IntVec3 safe))
                    {
                        pawn.Position = safe;
                        pawn.Notify_Teleported();
                        StatMeltRelocated++;
                    }
                }
                else if (t.def.category == ThingCategory.Item && TryFindSafeCell(map, c, out IntVec3 safeItem))
                {
                    t.DeSpawn();
                    GenPlace.TryPlaceThing(t, safeItem, map, ThingPlaceMode.Near);
                    StatMeltRelocated++;
                }
                else if (gentle && t.def.category == ThingCategory.Building)
                {
                    // Gentle mode: a building has nowhere to go; it is
                    // deconstructed to its leavings rather than left on lava.
                    string label = t.LabelNoCount;
                    t.Destroy(DestroyMode.Deconstruct);
                    AddLoss(label + " (collapsed)");
                    lost = true;
                }
            }
            return lost;
        }

        private bool TryFindSafeCell(Map map, IntVec3 from, out IntVec3 result)
        {
            return CellFinder.TryFindRandomCellNear(from, map, 8,
                x => x.Standable(map) && !frozenCells.Contains(x) && !x.GetTerrain(map).dangerous, out result);
        }

        private void AddLoss(string label)
        {
            if (label.NullOrEmpty())
            {
                label = "something";
            }
            meltLosses.TryGetValue(label, out int n);
            meltLosses[label] = n + 1;
            StatMeltDestroyed++;
        }

        /// <summary>Spawns the rain's dhuvvox swarm. Public for the proof/dev action. Returns the number spawned.</summary>
        public int EruptSwarm(Map map)
        {
            if (map == null || !RM_TheForgeSettings.Active(RM_TheForgeSettings.dhuvvoxSwarmEnabled))
            {
                return 0;
            }
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Dhuvvox");
            if (kind == null)
            {
                return 0;
            }
            var anchors = new List<IntVec3>();
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.def == kind.race && p.Faction == null) anchors.Add(p.Position);
            }
            int n = 0;
            for (int i = 0; i < SwarmSize; i++)
            {
                IntVec3 cell;
                bool found = anchors.Count > 0
                    ? CellFinder.TryFindRandomCellNear(anchors.RandomElement(), map, Mathf.RoundToInt(SwarmSpread),
                        c => c.Standable(map) && !c.Roofed(map) && !c.Fogged(map), out cell)
                    : CellFinderLoose.TryGetRandomCellWith(c => c.Standable(map) && !c.Roofed(map) && !c.Fogged(map), map, 300, out cell);
                if (!found) continue;
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer,
                    forceGenerateNewPawn: true, canGeneratePawnRelations: false));
                GenSpawn.Spawn(p, cell, map);
                swarm.Add(p);
                n++;
            }
            StatSwarmErupted += n;
            if (n > 0)
            {
                Messages.Message("The rain has woken the dhuvvox: " + n + " erupt from the ash to strip the wet rock.",
                    new TargetInfo(swarm[swarm.Count - 1].Position, map), MessageTypeDefOf.NeutralEvent);
            }
            return n;
        }

        /// <summary>Ends the swarm: each surviving member burrows back into the ash, leaving an ash scar; one counted
        /// message. Dead or tamed members are simply released from the list. Returns the number resealed.</summary>
        public int ResealSwarm(Map map)
        {
            int n = 0;
            IntVec3 last = IntVec3.Invalid;
            ThingDef ash = DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Ash");
            foreach (Pawn p in swarm)
            {
                if (p == null || p.Dead || p.Destroyed || !p.Spawned || p.Map != map || p.Faction != null)
                {
                    continue;
                }
                last = p.Position;
                if (ash != null) FilthMaker.TryMakeFilth(p.Position, map, ash);
                p.Destroy(DestroyMode.Vanish);
                n++;
            }
            swarm.Clear();
            StatSwarmResealed += n;
            if (n > 0 && map != null)
            {
                Messages.Message("The rain is over and the dhuvvox swarm has burrowed back into the ash (" + n
                    + "). Only the scars where they went down are left.", new TargetInfo(last, map), MessageTypeDefOf.NeutralEvent);
            }
            return n;
        }

        public string DebugStateReport()
        {
            return "phase=" + phase + " endsIn=" + (phaseEndTick - Find.TickManager.TicksGame)
                + " inBurst=" + InBurst + " frozen=" + frozenCells.Count + " gardensLive=" + gardens.Count
                + " cycles=" + StatCycles + " gasIgnitions=" + StatGasIgnitions + " floods=" + StatFloodReleases
                + " cellsFrozen=" + StatCellsFrozen + " cellsMelted=" + StatCellsMelted
                + " gardensSpawned=" + StatGardensSpawned + " gardensDrifted=" + StatGardensDrifted
                + " meltDestroyed=" + StatMeltDestroyed + " meltPawnsBurned=" + StatMeltPawnsBurned
                + " meltRelocated=" + StatMeltRelocated
                + " swarmLive=" + swarm.Count + " swarmErupted=" + StatSwarmErupted + " swarmResealed=" + StatSwarmResealed;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref phase, "forgePhase", ForgeCyclePhase.StillHeat);
            Scribe_Values.Look(ref phaseStartTick, "forgePhaseStartTick", -1);
            Scribe_Values.Look(ref phaseEndTick, "forgePhaseEndTick", -1);
            Scribe_Values.Look(ref hissSent, "forgeHissSent", false);
            Scribe_Values.Look(ref gasWavesLeft, "forgeGasWavesLeft", 0);
            Scribe_Values.Look(ref nextGasWaveTick, "forgeNextGasWaveTick", -1);
            Scribe_Values.Look(ref floodsLeft, "forgeFloodsLeft", 0);
            Scribe_Values.Look(ref nextFloodTick, "forgeNextFloodTick", -1);
            Scribe_Values.Look(ref gardensSeeded, "forgeGardensSeeded", false);
            Scribe_Collections.Look(ref frozenCells, "forgeFrozenCells", LookMode.Value);
            Scribe_Collections.Look(ref gardens, "forgeGardens", LookMode.Reference);
            Scribe_Collections.Look(ref swarm, "forgeDhuvvoxSwarm", LookMode.Reference);
            Scribe_Values.Look(ref StatSwarmErupted, "statSwarmErupted", 0);
            Scribe_Values.Look(ref StatSwarmResealed, "statSwarmResealed", 0);
            Scribe_Values.Look(ref StatCycles, "statCycles", 0);
            Scribe_Values.Look(ref StatGasIgnitions, "statGasIgnitions", 0);
            Scribe_Values.Look(ref StatFloodReleases, "statFloodReleases", 0);
            Scribe_Values.Look(ref StatCellsFrozen, "statCellsFrozen", 0);
            Scribe_Values.Look(ref StatCellsMelted, "statCellsMelted", 0);
            Scribe_Values.Look(ref StatGardensSpawned, "statGardensSpawned", 0);
            Scribe_Values.Look(ref StatGardensDrifted, "statGardensDrifted", 0);
            Scribe_Values.Look(ref StatMeltDestroyed, "statMeltDestroyed", 0);
            Scribe_Values.Look(ref StatMeltPawnsBurned, "statMeltPawnsBurned", 0);
            Scribe_Values.Look(ref StatMeltRelocated, "statMeltRelocated", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (frozenCells == null) frozenCells = new HashSet<IntVec3>();
                if (gardens == null) gardens = new List<Thing>();
                if (swarm == null) swarm = new List<Pawn>();
                swarm.RemoveAll(x => x == null);
                gardens.RemoveAll(g => g == null);
            }
        }
    }

    // Lookups for comps and debug actions: the cycle condition on a map, and
    // the pulse's burst state when the cycle is not present or switched off.
    public static class RM_ForgeCycleUtility
    {
        public static RM_GameCondition_WeatherPulse PulseOn(Map map)
        {
            if (map == null || map.gameConditionManager == null)
            {
                return null;
            }
            List<GameCondition> conds = map.gameConditionManager.ActiveConditions;
            for (int i = 0; i < conds.Count; i++)
            {
                if (conds[i] is RM_GameCondition_WeatherPulse pulse)
                {
                    return pulse;
                }
            }
            return null;
        }

        public static RM_GameCondition_ForgeCycle CycleOn(Map map)
        {
            return PulseOn(map) as RM_GameCondition_ForgeCycle;
        }

        /// <summary>True while boiling rain is falling: the grand cycle's rain
        /// phase, or any pulse burst.</summary>
        public static bool RainingNow(Map map)
        {
            RM_GameCondition_WeatherPulse pulse = PulseOn(map);
            if (pulse == null)
            {
                return false;
            }
            if (pulse.InBurst)
            {
                return true;
            }
            RM_GameCondition_ForgeCycle cycle = pulse as RM_GameCondition_ForgeCycle;
            return cycle != null && RM_GameCondition_ForgeCycle.CycleActive && cycle.Phase == ForgeCyclePhase.Rain;
        }

        public static bool FlashWindowNow(Map map)
        {
            RM_MapComponent_FlashCycle flash = map != null ? map.GetComponent<RM_MapComponent_FlashCycle>() : null;
            return flash != null && flash.InFlashWindow();
        }
    }
}
