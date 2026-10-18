using System.Collections.Generic;
using RimMandrake.FlowWorks;
using RimMandrake.CrackedLands.MapControls;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.CrackedLands
{
    // ════════════════════════════════════════════════════════════════════
    // THE FLOOD CYCLE CLOCK, AND A FLOWWORKS DRIVER CLIENT.
    //
    // Auto-attached to every map by vanilla's own Map.FillComponents (any
    // non-abstract MapComponent subclass with a (Map) constructor gets one
    // instance per map — confirmed against the 1.6 assembly; no Harmony
    // wiring needed, same as the sibling Greentide mod's own map
    // components).
    //
    // This mod owns the biome, the phase clock and the chime. The SOAK the
    // flood leaves is owned by the Explosive Growth engine (see StartFlood;
    // a direct ExplosiveGrowthAPI call, both composed in Baroque Biomes);
    // this mod only reports which cells the water reached. It
    // does NOT own what an excavated cell looks like — FlowWorks does
    // (flowworks_mod_definition.md §15 ruling 8: one engine, per-driver
    // recede policy, and this mod is the flood driver). Two owners for one
    // cell is the disease; CANYON_FLOOD_ERASES_CANALS_1 was the symptom.
    //
    // So a flood cell takes one of two paths:
    //
    //   EXCAVATED (FlowWorks' depth grid says D > 0) — the flood raises
    //     that cell's FILL through the engine (TryFloodDriverCell) and
    //     recede lowers it back to what it held before. No terrain write of
    //     ours ever lands on it, so a channel, a pit or a SUPERDEEP
    //     excavation cannot be engulfed, and cannot be laundered into
    //     SoilRich when the water leaves. The engine draws the liquid and
    //     the engine takes it away.
    //
    //   EVERYTHING ELSE — unchanged: a plain PERMANENT TerrainGrid.SetTerrain
    //     wall of WaterMovingShallow (Core, always present) driven by this
    //     component's own phase clock, converted to SoilRich at recede and
    //     ONLY if the cell still holds the exact flood terrain this mod
    //     placed. If a player built or dug there mid-flood, that change is
    //     left alone.
    //
    // One GameCondition (RM_CanyonFlood, plain vanilla GameCondition class
    // — nothing to override, every effect lives here) is registered purely
    // as the player-visible signal: the letter, the end message, the
    // "canyon flood" chip in the condition bar. It carries no mechanism of
    // its own.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_CanyonFlood : MapComponent
    {
        // The engine. Looked up lazily because MapComponent construction
        // order between two mods is not something either mod may assume.
        private RM_MapComponent_Excavation excavationInt;

        private RM_MapComponent_Excavation Excavation =>
            excavationInt ?? (excavationInt = map.GetComponent<RM_MapComponent_Excavation>());

        // CRACKEDLANDS_LEDGES_OF_MERCY_1: refuge ledges and chime-line anchors.
        // Same-mod component, so it is always present; looked up lazily all
        // the same (construction order).
        private RM_MapComponent_LedgeRefuge refugeInt;

        private RM_MapComponent_LedgeRefuge Refuge =>
            refugeInt ?? (refugeInt = map.GetComponent<RM_MapComponent_LedgeRefuge>());

        // Herald is appended LAST so a save written before it (bytes 0-2)
        // still reads back as the same phase.

        // The cycle's clocks and counters live in the Verse-free kernel's state.
        private readonly FloodState st = new FloodState();

        private IntVec3 pendingSeed = IntVec3.Invalid;

        // FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: the cell of the flood trigger this cycle's flood enters at, from
        // the moment a trigger is chosen (clock) or pressed (button) until the water recedes. Invalid = an ordinary
        // canyon flood from a random seed. While it is valid the flood runs on ANY biome (the trigger is the map
        // maker's explicit choice), so a standing aimed flood is never torn down next tick by the biome gate.
        private IntVec3 aimedAt = IntVec3.Invalid;

        // Last tick's Active (not saved: a load is not a switch-on). Off the canyon the clock idles while no trigger
        // lifts the gate, so its next flood ages into the past; on the switch-on edge it gets a fresh period instead of
        // playing the whole warning and the wall within a few ticks.
        private bool wasActive = true;
        private IntVec3 roarCell = IntVec3.Invalid;
        private Sustainer roar;

        // Cells this cycle's flood is currently standing on, to convert
        // back to soil at recede time (only if still ours — see header).
        // NON-EXCAVATED cells only: an excavated one is never written here.
        private readonly RM_FloodKernel.Ledger ledger = new RM_FloodKernel.Ledger();
        private List<IntVec3> activeFloodCells, raisedFillCells;
        private List<int> raisedFillPrior;

        // The excavated half of this cycle's footprint, and what each of
        // those cells held before the flood raised it. Two parallel lists
        // rather than a dictionary purely because Scribe_Collections writes
        // a List<T> of values with no working-list dance; they are always
        // the same length and are cleared together.

        public RM_MapComponent_CanyonFlood(Map map) : base(map)
        {
        }

        // Read by RM_CompPanSleeper: a muttavaq never digs in while the
        // wall is standing.
        public bool IsFlooding => st.Phase == FloodPhase.Flooding;

        // Read by RM_TarruqHushPatch: from beat 3 until the water recedes,
        // the tarruq do not call.
        public bool TarruqSilenced =>
            Active && RM_CrackedLandsSettings.fiveBeatsEnabled
            && ((st.Phase == FloodPhase.Herald && st.HeraldBeat > 3) || st.Phase == FloodPhase.Warned || st.Phase == FloodPhase.Flooding);

        // The canyon's own gate: this biome, or the cross-biome option.
        private bool CanyonGate =>
            map.Biome == RM_CrackedLandsDefOf.RM_FloodedCanyon || RM_CrackedLandsSettings.featureInOtherBiomes;

        // FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: a flood trigger lifts the biome gate for ITS flood only -- while
        // one stands on the clock, or while a flood it started is pending or standing.
        private bool Active =>
            RM_CrackedLandsSettings.floodCycleEnabled
            && (CanyonGate || (RM_BiomeMapControls.FloodTriggersOn && (aimedAt.IsValid || RM_BiomeMapControls.AnyClockTrigger(map))));

        public FloodPhase Phase => st.Phase;
        public IntVec3 AimedAt => aimedAt;

        // Test surface for RM_CrackedLandsDebugActions — schedules the
        // chime to ring on the very next tick, so the full sequence (chime
        // -> wait chimeLeadTimeHours -> wall -> floodDurationHours -> soil)
        // plays out in real time without waiting on floodPeriodDays.
        public void DebugArmFloodSoon()
        {
            st.Phase = FloodPhase.Dry;
            st.NextFloodTick = Find.TickManager.TicksGame + 1;
        }

        // Test surface: skip straight past the chime to the wall itself.
        public void DebugStartFloodNow()
        {
            if (!pendingSeed.IsValid)
            {
                ChooseSeed();   // a clock flood trigger on the map aims it (FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS)
            }
            st.Phase = FloodPhase.Flooding;
            StartFlood(Find.TickManager.TicksGame);
        }

        // FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: a flood trigger's button. warn=false: the wall now, at the trigger.
        // warn=true: the whole warning (beats, staged chimes) from the next tick, then the wall at the trigger.
        public string FireTrigger(IntVec3 at, bool warn)
        {
            if (!RM_CrackedLandsSettings.floodCycleEnabled)
            {
                return "REFUSED: the flood cycle is off in Mod Settings (Cracked Lands > Flood cycle)";
            }
            if (!RM_BiomeMapControls.FloodTriggersOn)
            {
                return "REFUSED: flood triggers are off in Mod Settings (Cracked Lands > Map controls, or FlowWorks' map controls switch)";
            }
            if (st.Phase == FloodPhase.Flooding)
            {
                return "REFUSED: a flood is already standing on this map (it recedes at tick " + st.FloodEndTick + ")";
            }
            int n = AimedCells(at).Count;
            if (n == 0)
            {
                return "REFUSED: no dug channel at or beside " + at + " for the water to run into";
            }
            aimedAt = at;
            pendingSeed = at;
            int now = Find.TickManager.TicksGame;
            if (warn)
            {
                st.Phase = FloodPhase.Dry;
                st.NextFloodTick = now + 1;
                return "OK armed: warning from the next tick, then " + n + " cells from " + at;
            }
            st.Phase = FloodPhase.Flooding;
            int flooded = StartFlood(now);
            return "OK flooding " + flooded + " cells from " + at + " until tick " + st.FloodEndTick;
        }


        // Test surface: end a standing flood on the next tick, so the recede
        // (soil conversion + CRACKEDLANDS_MECHANICS_BUILD_1's fresh fossil
        // seams) can be read without waiting out floodDurationHours.
        public void DebugRecedeSoon()
        {
            if (st.Phase == FloodPhase.Flooding)
            {
                st.FloodEndTick = Find.TickManager.TicksGame;
            }
        }

        public string DebugStateReport()
        {
            return string.Format(
                "phase={0} nextFloodTick={1} floodEndTick={2} nowTick={3} activeFloodCells={4} "
                + "raisedFillCells={5} active={6} flowWorksEngine={7} explosiveGrowth={8} "
                + "chimeStage={9} lastRecedeTick={10} peakstormConsidered={11} weather={12} "
                + "heraldBeat={13} pendingSeed={14} roar={15} tarruqSilenced={16} refugeFlooded={17} aimedAt={18}",
                st.Phase, st.NextFloodTick, st.FloodEndTick, Find.TickManager.TicksGame,
                ledger.Active.Count, ledger.RaisedCells.Count, Active,
                Excavation != null ? "present" : "ABSENT",
                RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings.On ? "present" : "OFF(engine-switched-off;flood-soaks-nothing)",
                st.ChimeStage, st.LastRecedeTick, st.PeakstormPulled,
                map.weatherManager.curWeather?.defName ?? "null",
                st.HeraldBeat, pendingSeed, roar != null && !roar.Ended ? "on" : "off", TarruqSilenced,
                RefugeFloodedCount(), aimedAt.IsValid ? aimedAt.x + "," + aimedAt.z : "none");
        }

        // Ledges of Mercy verify: footprint cells that are refuge cells. Must
        // read 0 — Eligible excludes them.
        private static IntVec3 Cell(long key)
        {
            return new IntVec3(RM_FloodKernel.KeyX(key), 0, RM_FloodKernel.KeyZ(key));
        }

        private static long KeyOf(IntVec3 c)
        {
            return RM_FloodKernel.Key(c.x, c.z);
        }

        private int RefugeFloodedCount()
        {
            RM_MapComponent_LedgeRefuge r = Refuge;
            if (r == null)
            {
                return -1;
            }
            int n = 0;
            for (int i = 0; i < ledger.Active.Count; i++)
            {
                if (r.IsRefugeCell(Cell(ledger.Active[i]))) n++;
            }
            for (int i = 0; i < ledger.RaisedCells.Count; i++)
            {
                if (r.IsRefugeCell(Cell(ledger.RaisedCells[i]))) n++;
            }
            return n;
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            if (st.NextFloodTick < 0)
            {
                ScheduleNextFlood();
            }
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            bool active = Active;
            if (active && !wasActive && !CanyonGate && st.Phase == FloodPhase.Dry && st.NextFloodTick <= now)
            {
                ScheduleNextFlood();
            }
            wasActive = active;
            FloodCfg cfg = new FloodCfg
            {
                Active = active,
                FiveBeats = RM_CrackedLandsSettings.fiveBeatsEnabled,
                ChimeStaging = RM_CrackedLandsSettings.chimeStagingEnabled,
                PeakstormBias = RM_CrackedLandsSettings.peakstormBiasEnabled,
                ChimeLeadHours = RM_CrackedLandsSettings.chimeLeadTimeHours,
                HeraldLeadHours = RM_CrackedLandsSettings.heraldLeadHours,
                FloodPeriodDays = RM_CrackedLandsSettings.floodPeriodDays,
            };
            bool wasFlooding = st.Phase == FloodPhase.Flooding;
            FloodStep step = RM_FloodKernel.Tick(st, cfg, now, pendingSeed.IsValid,
                st.Phase == FloodPhase.Dry && map.weatherManager.curWeather == RM_CrackedLandsDefOf.RM_PeakstormLight,
                Rand.Value, (lo, hi) => Rand.RangeInclusive(lo, hi), (lo, hi) => Rand.RangeInclusive(lo, hi));

            if (step.SweepRefuge)
            {
                Refuge?.Sweep();
            }
            if (step.ChooseSeed)
            {
                ChooseSeed();
            }
            for (int i = 0; i < step.HeraldBeats.Count; i++)
            {
                PlayHeraldBeat(step.HeraldBeats[i]);
            }
            if (step.RingChime >= 0)
            {
                RingChime(step.RingChime);
            }
            if (step.StartFlood)
            {
                StartFlood(now);
            }
            if (wasFlooding)
            {
                MaintainRoar();
            }
            if (step.Recede)
            {
                RecedeFlood();
            }
        }

        private static int HoursToTicks(float hours)
        {
            return RM_FloodKernel.HoursToTicks(hours);
        }

        private static int DaysToTicks(float days)
        {
            return RM_FloodKernel.DaysToTicks(days);
        }

        // CRACKEDLANDS_MECHANICS_BUILD_1 §5: "the flood clock biases its chime
        // window to follow" Peakstorm Light. Checked hourly while dry. Once
        // per storm (peakstormPulledThisCycle), and only when at least half a
        // period has passed since the last recede, a standing Peakstorm Light
        // pulls a flood that is still more than a day away forward to
        // 0.5–1.5 days out. The chime still rings chimeLeadTimeHours before
        // it — the storm on the peaks never removes the warning.
        private void ScheduleNextFlood()
        {
            RM_FloodKernel.ScheduleNext(st, new FloodCfg { FloodPeriodDays = RM_CrackedLandsSettings.floodPeriodDays }, Find.TickManager.TicksGame,
                (lo, hi) => Rand.RangeInclusive(lo, hi));
        }


        private static readonly string[] ChimeStageMessages =
        {
            "The water chimes are ringing — a flood is coming down the canyon.",
            "The chimes are ringing lower down the lines — the flood is closer.",
            "The nearest chimes are ringing — the water is almost here. Get off the canyon floor.",
        };

        private void ChooseSeed()
        {
            Refuge?.RefreshCells();
            // FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: a flood trigger on the clock is where the water enters.
            if (!aimedAt.IsValid && RM_BiomeMapControls.FloodTriggersOn)
            {
                Thing t = RM_BiomeMapControls.PickClockTrigger(map);
                if (t != null)
                {
                    aimedAt = t.Position;
                }
            }
            if (aimedAt.IsValid)
            {
                pendingSeed = aimedAt;
                return;
            }
            pendingSeed = CellFinderLoose.TryGetRandomCellWith(Eligible, map, 2000, out IntVec3 seed) ? seed : IntVec3.Invalid;
        }

        // Beats 1-3. Vanilla clips retinted in Defs/SoundDefs/RM_CanyonBeats.xml
        // stand in until the bespoke audio lands (CRACKEDLANDS_FIVE_BEATS_AUDIO_1).
        private void PlayHeraldBeat(int beat)
        {
            switch (beat)
            {
                case 1:
                    Messages.Message("Wind is threading the slot canyons, cool and smelling of wet clay.",
                        new TargetInfo(map.Center, map), MessageTypeDefOf.NeutralEvent);
                    RM_CrackedLandsDefOf.RM_CanyonBeat_SlotWind?.PlayOneShotOnCamera(map);
                    break;
                case 2:
                    int ticked = 0;
                    IntVec3 first = IntVec3.Invalid;
                    IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                    for (int i = 0; i < pawns.Count && ticked < MaxTickingSleepers; i++)
                    {
                        Pawn p = pawns[i];
                        CompCanBeDormant d = p.RaceProps.Animal ? p.TryGetComp<CompCanBeDormant>() : null;
                        if (d != null && !d.Awake)
                        {
                            RM_CrackedLandsDefOf.RM_CanyonBeat_PanTick?.PlayOneShot(SoundInfo.InMap(new TargetInfo(p.Position, map)));
                            if (!first.IsValid) first = p.Position;
                            ticked++;
                        }
                    }
                    Messages.Message(ticked > 0
                            ? "The sleeper pans have started ticking."
                            : "The dry flats have started ticking.",
                        new TargetInfo(first.IsValid ? first : map.Center, map), MessageTypeDefOf.NeutralEvent);
                    break;
                case 3:
                    Messages.Message("The tarruq have gone silent in the cracks.",
                        new TargetInfo(map.Center, map), MessageTypeDefOf.NeutralEvent);
                    break;
            }
        }

        // TUNED: at most this many pans tick audibly — a chorus, not a
        // per-pawn sound spike on a sleeper-dense map.
        private const int MaxTickingSleepers = 8;

        // The chime for stage k tolls from a point on the line running from
        // the map corner farthest from where the water will arrive toward
        // that arrival point: far, then nearer, then nearest. Where the map
        // carries chime-line anchor things (RM_ChimeAnchorExtension,
        // CRACKEDLANDS_LEDGES_OF_MERCY_1) the chime tolls from the anchor
        // nearest that position; with none, from the position itself.

        private IntVec3 ChimeCell(int stage)
        {
            if (!pendingSeed.IsValid)
            {
                return map.Center;
            }
            RM_FloodKernel.ChimePoint(stage, pendingSeed.x, pendingSeed.z, map.Size.x - 1, map.Size.z - 1, out int x, out int z);
            IntVec3 c = new IntVec3(x, 0, z).ClampInsideMap(map);
            return Refuge != null ? Refuge.NearestAnchorTo(c) : c;
        }

        private static SoundDef ChimeSound(int stage)
        {
            switch (stage)
            {
                case 0: return RM_CrackedLandsDefOf.RM_CanyonChime_Far;
                case 1: return RM_CrackedLandsDefOf.RM_CanyonChime_Mid;
                default: return RM_CrackedLandsDefOf.RM_CanyonChime_Near;
            }
        }

        // Beat 5: the flood is a continuous roar, sited where the water came in.
        private void MaintainRoar()
        {
            if (!RM_CrackedLandsSettings.fiveBeatsEnabled || !roarCell.IsValid || RM_CrackedLandsDefOf.RM_CanyonFlood_Roar == null)
            {
                return;
            }
            if (roar == null || roar.Ended)
            {
                roar = RM_CrackedLandsDefOf.RM_CanyonFlood_Roar.TrySpawnSustainer(
                    SoundInfo.InMap(new TargetInfo(roarCell, map), MaintenanceType.PerTick));
            }
            roar?.Maintain();
        }

        private void RingChime(int stage)
        {
            // "the water chimes ring... tones rolling up through the stone
            // ahead of any sound of water" (source sheet). STAGED by
            // distance-to-flood (CRACKEDLANDS_MECHANICS_BUILD_1 §5). The
            // bespoke 3–4 chime tones are owed audio; until they exist every
            // stage reuses the vanilla TinyBell cue — the staging, messages
            // and timing are the mechanism, the tone per stage is the art.
            stage = UnityEngine.Mathf.Clamp(stage, 0, ChimeStageMessages.Length - 1);
            IntVec3 at = RM_CrackedLandsSettings.fiveBeatsEnabled ? ChimeCell(stage) : map.Center;
            Messages.Message(
                ChimeStageMessages[stage],
                new TargetInfo(at, map),
                MessageTypeDefOf.ThreatBig);
            SoundDef chime = RM_CrackedLandsSettings.fiveBeatsEnabled ? ChimeSound(stage) : null;
            if (chime != null)
            {
                chime.PlayOneShot(SoundInfo.InMap(new TargetInfo(at, map)));
            }
            else
            {
                SoundDefOf.TinyBell.PlayOneShotOnCamera(map);
            }
        }

        private int StartFlood(int now)
        {
            int target = RM_FloodKernel.TargetCells(map.Area);
            Refuge?.RefreshCells();
            List<IntVec3> cells = aimedAt.IsValid ? AimedCells(aimedAt) : ComputeFloodCells(target, pendingSeed);
            if (aimedAt.IsValid && cells.Count == 0)
            {
                Messages.Message("The flood came down to the flood trigger at " + aimedAt + ", but no dug channel beside it took the water.",
                    new TargetInfo(aimedAt, map), MessageTypeDefOf.NeutralEvent);
            }
            roarCell = cells.Count > 0 ? cells[0] : IntVec3.Invalid;
            pendingSeed = IntVec3.Invalid;

            RM_FloodKernel.Begin(st, now, RM_CrackedLandsSettings.floodDurationHours, RM_CrackedLandsSettings.soakDecayDays,
                out int durationTicks, out int soakTicks);

            TerrainDef floodTerrain = TerrainDefOf.WaterMovingShallow;
            RM_MapComponent_Excavation excavation = Excavation;

            ledger.Begin(cells.ConvertAll(KeyOf),
                k => excavation != null && excavation.IsExcavated(Cell(k)),
                k => excavation.FillAt(Cell(k)),
                k => excavation.TryFloodDriverCell(Cell(k)));
            for (int i = 0; i < ledger.Active.Count; i++)
            {
                map.terrainGrid.SetTerrain(Cell(ledger.Active[i]), floodTerrain);
            }

            if (RM_CrackedLandsSettings.growthCouplingEnabled)
            {
                RimMandrake.ExplosiveGrowth.ExplosiveGrowthAPI.SoakCells(map, cells, soakTicks);
            }

            if (RM_CrackedLandsSettings.floodDamageEnabled)
            {
                DamagePawnsInCells(cells);
            }

            GameCondition cond = GameConditionMaker.MakeCondition(RM_CrackedLandsDefOf.RM_CanyonFlood, durationTicks);
            map.gameConditionManager.RegisterCondition(cond);
            return cells.Count;
        }

        // FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: the footprint of a flood entering at a trigger. Canal only (the
        // default): the dug channel joined to the trigger, no terrain write anywhere. Spill: an ordinary canyon flood
        // seeded at the trigger (or the first open cell beside it). Size: the trigger's cap, else the map's flood size.
        public List<IntVec3> AimedCells(IntVec3 at)
        {
            Building_RM_FloodTrigger trig = RM_BiomeMapControls.TriggerAt(map, at);
            int cap = trig != null && trig.maxCells > 0 ? trig.maxCells : RM_FloodKernel.TargetCells(map.Area);
            if (!at.InBounds(map))
            {
                return new List<IntVec3>();
            }
            if (trig != null && trig.spill)
            {
                IntVec3 seed = Eligible(at) ? at : IntVec3.Invalid;
                for (int i = 0; i < 4 && !seed.IsValid; i++)
                {
                    IntVec3 n = at + GenAdj.CardinalDirections[i];
                    if (Eligible(n)) seed = n;
                }
                if (!seed.IsValid)
                {
                    return new List<IntVec3>();
                }
                return RM_FloodKernel.FloodCells(cap, seed.x, seed.z, true, (x, z) => new IntVec3(x, 0, z).InBounds(map),
                    (x, z) => Eligible(new IntVec3(x, 0, z)), () => Rand.Value).ConvertAll(Cell);
            }
            RM_MapComponent_Excavation ex = Excavation;
            if (ex == null)
            {
                return new List<IntVec3>();
            }
            return RM_FloodKernel.FloodCellsAimed(cap, at.x, at.z, (x, z) => new IntVec3(x, 0, z).InBounds(map),
                (x, z) => Channel(ex, new IntVec3(x, 0, z))).ConvertAll(Cell);
        }

        // A dug cell the water may run along: not behind a shut sluice, not a refuge ledge. Roofed or already wet
        // is fine -- the engine raises a channel cell to its brim, whatever it held.
        private bool Channel(RM_MapComponent_Excavation ex, IntVec3 c)
        {
            return ex.IsExcavated(c) && !RM_FlowDoorRules.SealsLiquid(map.edificeGrid[c])
                && (Refuge == null || !Refuge.IsRefugeCell(c));
        }

        private void RecedeFlood()
        {
            TerrainDef floodTerrain = TerrainDefOf.WaterMovingShallow;
            TerrainDef soilTerrain = TerrainDefOf.SoilRich;

            List<IntVec3> wetted = ledger.Wetted().ConvertAll(Cell);
            // FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: a trigger's flood outside the canyon brings the water and its
            // soak only; the canyon's ecology (fresh fossil seams, the feast, migrants, floodline salvage) stays canyon.
            bool ecology = !aimedAt.IsValid || CanyonGate;
            aimedAt = IntVec3.Invalid;
            if (ecology && RM_CrackedLandsSettings.floodRecutSeamsEnabled)
            {
                RM_FossilStrata.RecutAlong(map, wetted, RM_CrackedLandsSettings.floodRecutSeamCount);
            }

            RM_MapComponent_Excavation excavation = Excavation;
            // FLOOD_DRIVER_OWNERSHIP_CONTRACT_1: restore through the outcome contract. NotOwned and Refused are both
            // hands-off here -- a raised cell is never given a fallback terrain write.
            ledger.Recede(k => Cell(k).InBounds(map),
                k => map.terrainGrid.TerrainAt(Cell(k)) == floodTerrain,
                k => map.terrainGrid.SetTerrain(Cell(k), soilTerrain),
                (k, prior) => excavation?.TrySetDriverFillOutcome(Cell(k), prior));

            roar?.End();
            roar = null;
            roarCell = IntVec3.Invalid;

            if (ecology)
            {
                map.GetComponent<RM_MapComponent_RecedeAftermath>()?.OnRecede(wetted);
            }
        }

        private List<IntVec3> ComputeFloodCells(int target, IntVec3 preferredSeed)
        {
            IntVec3 seed = preferredSeed;
            if ((!seed.IsValid || !Eligible(seed))
                && !CellFinderLoose.TryGetRandomCellWith(Eligible, map, 2000, out seed))
            {
                return new List<IntVec3>();
            }
            return RM_FloodKernel.FloodCells(target, seed.x, seed.z, true, (x, z) => new IntVec3(x, 0, z).InBounds(map),
                (x, z) => Eligible(new IntVec3(x, 0, z)), () => Rand.Value).ConvertAll(Cell);
        }

        private bool Eligible(IntVec3 c)
        {
            if (!c.InBounds(map) || c.Fogged(map) || c.Roofed(map))
            {
                return false;
            }
            TerrainDef t = map.terrainGrid.TerrainAt(c);
            if (t == null || t.IsWater)
            {
                // Covers an excavated cell that is ALREADY full: FlowWorks
                // renders fill as water terrain, so a brimming channel reads
                // as water and there is nothing for a flood to add.
                return false;
            }
            // An excavated cell is deliberately NOT excluded any more. It is
            // eligible, and StartFlood routes it to the engine instead of
            // writing terrain on it (CANYON_FLOOD_ERASES_CANALS_1).
            if (c.GetEdifice(map) != null)
            {
                return false;
            }
            // A refuge ledge is never flooded, whatever its physical form.
            if (Refuge != null && Refuge.IsRefugeCell(c))
            {
                return false;
            }
            return true;
        }

        private void DamagePawnsInCells(List<IntVec3> cells)
        {
            HashSet<IntVec3> cellSet = new HashSet<IntVec3>(cells);
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || p.Downed)
                {
                    continue;
                }
                if (cellSet.Contains(p.Position))
                {
                    // One light, non-fatal hit — the startle of the wall
                    // arriving, never a steady damage-over-time hazard.
                    p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, Rand.Range(3f, 8f)));
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            FloodPhase phase = st.Phase;
            int nextFloodTick = st.NextFloodTick, floodEndTick = st.FloodEndTick, lastRecedeTick = st.LastRecedeTick, chimeStage = st.ChimeStage, heraldBeat = st.HeraldBeat;
            bool peakstormPulledThisCycle = st.PeakstormPulled;
            Scribe_Values.Look(ref phase, "phase", FloodPhase.Dry);
            Scribe_Values.Look(ref nextFloodTick, "nextFloodTick", -1);
            Scribe_Values.Look(ref floodEndTick, "floodEndTick", -1);
            Scribe_Values.Look(ref lastRecedeTick, "lastRecedeTick", -1);
            Scribe_Values.Look(ref chimeStage, "chimeStage", 0);
            Scribe_Values.Look(ref peakstormPulledThisCycle, "peakstormPulledThisCycle", false);
            Scribe_Values.Look(ref heraldBeat, "heraldBeat", 0);
            st.Phase = phase; st.NextFloodTick = nextFloodTick; st.FloodEndTick = floodEndTick; st.LastRecedeTick = lastRecedeTick;
            st.ChimeStage = chimeStage; st.HeraldBeat = heraldBeat; st.PeakstormPulled = peakstormPulledThisCycle;
            Scribe_Values.Look(ref pendingSeed, "pendingSeed", IntVec3.Invalid);
            Scribe_Values.Look(ref roarCell, "roarCell", IntVec3.Invalid);
            Scribe_Values.Look(ref aimedAt, "aimedAt", IntVec3.Invalid);
            // ExposeData runs once per load phase (LoadingVars, ResolveCrossRefs, PostLoadInit); the loaded lists must live in FIELDS so
            // the LoadingVars read survives to PostLoadInit. Same labels as before the kernel extraction, so old saves load.
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                activeFloodCells = ledger.Active.ConvertAll(Cell);
                raisedFillCells = ledger.RaisedCells.ConvertAll(Cell);
                raisedFillPrior = new List<int>(ledger.RaisedPrior);
            }
            Scribe_Collections.Look(ref activeFloodCells, "activeFloodCells", LookMode.Value);
            Scribe_Collections.Look(ref raisedFillCells, "raisedFillCells", LookMode.Value);
            Scribe_Collections.Look(ref raisedFillPrior, "raisedFillPrior", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                ledger.Restore(activeFloodCells?.ConvertAll(KeyOf), raisedFillCells?.ConvertAll(KeyOf), raisedFillPrior);
                activeFloodCells = null; raisedFillCells = null; raisedFillPrior = null;
            }
        }
    }
}
