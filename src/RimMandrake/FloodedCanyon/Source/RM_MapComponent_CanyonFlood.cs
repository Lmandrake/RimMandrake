using System.Collections.Generic;
using RimMandrake.FlowWorks;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.FloodedCanyon
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
    // flood leaves is owned by mandrake.rm.explosivegrowth (see StartFlood);
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

        // Herald is appended LAST so a save written before it (bytes 0-2)
        // still reads back as the same phase.
        private enum Phase : byte { Dry, Warned, Flooding, Herald }

        private Phase phase = Phase.Dry;

        // -1 == not yet scheduled (set on first FinalizeInit/tick).
        private int nextFloodTick = -1;
        private int floodEndTick = -1;

        // Peakstorm Light coupling (MaybeFollowPeakstorm).
        private int lastRecedeTick = -1;
        private bool peakstormPulledThisCycle;

        // Next chime stage to ring while Warned (RingChime staging).
        private int chimeStage;

        // CRACKEDLANDS_GPT_ENRICHMENT_1 §2 — five beats before water. Beats
        // 1-3 (slot wind, ticking pans, tarruq hush) ring in the Herald
        // window before the chimes; heraldBeat is the next one due.
        private int heraldBeat;

        // Where this cycle's water will arrive, chosen when the warning
        // starts so the chimes can toll from the far canyon toward it and the
        // roar can sit on it. Invalid = choose at StartFlood (debug path).
        private IntVec3 pendingSeed = IntVec3.Invalid;
        private IntVec3 roarCell = IntVec3.Invalid;
        private Sustainer roar;

        // Cells this cycle's flood is currently standing on, to convert
        // back to soil at recede time (only if still ours — see header).
        // NON-EXCAVATED cells only: an excavated one is never written here.
        private List<IntVec3> activeFloodCells = new List<IntVec3>();

        // The excavated half of this cycle's footprint, and what each of
        // those cells held before the flood raised it. Two parallel lists
        // rather than a dictionary purely because Scribe_Collections writes
        // a List<T> of values with no working-list dance; they are always
        // the same length and are cleared together.
        private List<IntVec3> raisedFillCells = new List<IntVec3>();
        private List<int> raisedFillPrior = new List<int>();

        public RM_MapComponent_CanyonFlood(Map map) : base(map)
        {
        }

        // Read by RM_CompPanSleeper: a muttavaq never digs in while the
        // wall is standing.
        public bool IsFlooding => phase == Phase.Flooding;

        // Read by RM_TarruqHushPatch: from beat 3 until the water recedes,
        // the tarruq do not call.
        public bool TarruqSilenced =>
            Active && RM_FloodedCanyonSettings.fiveBeatsEnabled
            && ((phase == Phase.Herald && heraldBeat > 3) || phase == Phase.Warned || phase == Phase.Flooding);

        private bool Active =>
            RM_FloodedCanyonSettings.floodCycleEnabled
            && (map.Biome == RM_FloodedCanyonDefOf.RM_FloodedCanyon || RM_FloodedCanyonSettings.featureInOtherBiomes);

        // Test surface for RM_FloodedCanyonDebugActions — schedules the
        // chime to ring on the very next tick, so the full sequence (chime
        // -> wait chimeLeadTimeHours -> wall -> floodDurationHours -> soil)
        // plays out in real time without waiting on floodPeriodDays.
        public void DebugArmFloodSoon()
        {
            phase = Phase.Dry;
            nextFloodTick = Find.TickManager.TicksGame + 1;
        }

        // Test surface: skip straight past the chime to the wall itself.
        public void DebugStartFloodNow()
        {
            phase = Phase.Flooding;
            StartFlood(Find.TickManager.TicksGame);
        }

        // Test surface: end a standing flood on the next tick, so the recede
        // (soil conversion + CRACKEDLANDS_MECHANICS_BUILD_1's fresh fossil
        // seams) can be read without waiting out floodDurationHours.
        public void DebugRecedeSoon()
        {
            if (phase == Phase.Flooding)
            {
                floodEndTick = Find.TickManager.TicksGame;
            }
        }

        public string DebugStateReport()
        {
            return string.Format(
                "phase={0} nextFloodTick={1} floodEndTick={2} nowTick={3} activeFloodCells={4} "
                + "raisedFillCells={5} active={6} flowWorksEngine={7} explosiveGrowth={8} "
                + "chimeStage={9} lastRecedeTick={10} peakstormConsidered={11} weather={12} "
                + "heraldBeat={13} pendingSeed={14} roar={15} tarruqSilenced={16}",
                phase, nextFloodTick, floodEndTick, Find.TickManager.TicksGame,
                activeFloodCells.Count, raisedFillCells.Count, Active,
                Excavation != null ? "present" : "ABSENT",
                RM_ExplosiveGrowthBridge.Available ? "present" : "ABSENT (flood soaks nothing)",
                chimeStage, lastRecedeTick, peakstormPulledThisCycle,
                map.weatherManager.curWeather?.defName ?? "null",
                heraldBeat, pendingSeed, roar != null && !roar.Ended ? "on" : "off", TarruqSilenced);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            if (nextFloodTick < 0)
            {
                ScheduleNextFlood();
            }
        }

        public override void MapComponentTick()
        {
            if (!Active)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;

            switch (phase)
            {
                case Phase.Dry:
                    if (nextFloodTick < 0)
                    {
                        ScheduleNextFlood();
                        return;
                    }
                    if (now % 2500 == 0)
                    {
                        MaybeFollowPeakstorm(now);
                    }
                    if (RM_FloodedCanyonSettings.fiveBeatsEnabled
                        && now >= nextFloodTick - HoursToTicks(RM_FloodedCanyonSettings.chimeLeadTimeHours) - HoursToTicks(RM_FloodedCanyonSettings.heraldLeadHours))
                    {
                        ChooseSeed();
                        heraldBeat = 1;
                        phase = Phase.Herald;
                        break;
                    }
                    if (now >= nextFloodTick - HoursToTicks(RM_FloodedCanyonSettings.chimeLeadTimeHours))
                    {
                        EnterWarned();
                    }
                    break;

                case Phase.Herald:
                    // Beats 1-3 at the start, two thirds and one third of the
                    // way through the herald window (TUNED: evenly spaced, so
                    // each beat has room to be heard before the next). A loop,
                    // so a compressed window (debug arm, a late peakstorm
                    // pull) still plays every beat, in order, before the chime.
                    while (heraldBeat <= 3)
                    {
                        int heraldTicks = HoursToTicks(RM_FloodedCanyonSettings.heraldLeadHours);
                        int chimeAt = nextFloodTick - HoursToTicks(RM_FloodedCanyonSettings.chimeLeadTimeHours);
                        float frac = 1f - (heraldBeat - 1) / 3f;
                        if (now < chimeAt - (int)(heraldTicks * frac))
                        {
                            break;
                        }
                        PlayHeraldBeat(heraldBeat);
                        heraldBeat++;
                    }
                    if (now >= nextFloodTick - HoursToTicks(RM_FloodedCanyonSettings.chimeLeadTimeHours))
                    {
                        EnterWarned();
                    }
                    break;

                case Phase.Warned:
                    // CRACKEDLANDS_MECHANICS_BUILD_1 §5: the chimes are staged
                    // by distance-to-flood — later rings as the water nears.
                    if (RM_FloodedCanyonSettings.chimeStagingEnabled && chimeStage < ChimeStageFractions.Length
                        && now >= nextFloodTick - (int)(HoursToTicks(RM_FloodedCanyonSettings.chimeLeadTimeHours) * ChimeStageFractions[chimeStage]))
                    {
                        RingChime(chimeStage);
                        chimeStage++;
                    }
                    if (now >= nextFloodTick)
                    {
                        StartFlood(now);
                        phase = Phase.Flooding;
                    }
                    break;

                case Phase.Flooding:
                    MaintainRoar();
                    if (now >= floodEndTick)
                    {
                        RecedeFlood();
                        lastRecedeTick = now;
                        phase = Phase.Dry;
                        ScheduleNextFlood();
                    }
                    break;
            }
        }

        private static int HoursToTicks(float hours)
        {
            return UnityEngine.Mathf.Max(250, UnityEngine.Mathf.RoundToInt(hours * 2500f));
        }

        private static int DaysToTicks(float days)
        {
            return UnityEngine.Mathf.Max(2500, UnityEngine.Mathf.RoundToInt(days * 60000f));
        }

        // CRACKEDLANDS_MECHANICS_BUILD_1 §5: "the flood clock biases its chime
        // window to follow" Peakstorm Light. Checked hourly while dry. Once
        // per storm (peakstormPulledThisCycle), and only when at least half a
        // period has passed since the last recede, a standing Peakstorm Light
        // pulls a flood that is still more than a day away forward to
        // 0.5–1.5 days out. The chime still rings chimeLeadTimeHours before
        // it — the storm on the peaks never removes the warning.
        private void MaybeFollowPeakstorm(int now)
        {
            if (!RM_FloodedCanyonSettings.peakstormBiasEnabled || peakstormPulledThisCycle)
            {
                return;
            }
            if (map.weatherManager.curWeather != RM_FloodedCanyonDefOf.RM_PeakstormLight)
            {
                return;
            }
            int periodTicks = DaysToTicks(RM_FloodedCanyonSettings.floodPeriodDays);
            if (lastRecedeTick >= 0 && now - lastRecedeTick < periodTicks / 2)
            {
                return;
            }
            if (nextFloodTick - now <= 60000)
            {
                return;
            }
            // CRACKEDLANDS_GPT_ENRICHMENT_1 §3: the storm "raises flood odds
            // without being a perfect timer". One roll per cycle, win or lose
            // (peakstormPulledThisCycle now means "this cycle's storm has been
            // considered"), so a storm that stands for hours cannot re-roll
            // its way to certainty. TUNED: 0.6 — more often than not, never
            // reliably. The window widens to 0.5-2 days for the same reason.
            peakstormPulledThisCycle = true;
            if (!Rand.Chance(PeakstormPullChance))
            {
                return;
            }
            int pulled = now + Rand.RangeInclusive(30000, 120000);
            int minTicks = HoursToTicks(RM_FloodedCanyonSettings.chimeLeadTimeHours)
                + (RM_FloodedCanyonSettings.fiveBeatsEnabled ? HoursToTicks(RM_FloodedCanyonSettings.heraldLeadHours) : 0)
                + 2500;
            pulled = System.Math.Max(pulled, now + minTicks);
            if (pulled < nextFloodTick)
            {
                nextFloodTick = pulled;
            }
        }

        private const float PeakstormPullChance = 0.6f;

        private void ScheduleNextFlood()
        {
            peakstormPulledThisCycle = false;
            int periodTicks = DaysToTicks(RM_FloodedCanyonSettings.floodPeriodDays);
            int jitter = Rand.RangeInclusive(-periodTicks / 3, periodTicks / 3);
            nextFloodTick = Find.TickManager.TicksGame + System.Math.Max(2500, periodTicks + jitter);
        }

        // Fraction of the chime lead time still left when each stage rings:
        // stage 0 at the full lead (the first chime, unchanged), then as the
        // water comes down the lines — half the lead, then the last moments.
        private static readonly float[] ChimeStageFractions = { 1f, 0.5f, 0.15f };

        private static readonly string[] ChimeStageMessages =
        {
            "The water chimes are ringing — a flood is coming down the canyon.",
            "The chimes are ringing lower down the lines — the flood is closer.",
            "The nearest chimes are ringing — the water is almost here. Get off the canyon floor.",
        };

        private void EnterWarned()
        {
            if (!pendingSeed.IsValid)
            {
                ChooseSeed();
            }
            RingChime(0);
            chimeStage = 1;
            phase = Phase.Warned;
        }

        private void ChooseSeed()
        {
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
                    RM_FloodedCanyonDefOf.RM_CanyonBeat_SlotWind?.PlayOneShotOnCamera(map);
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
                            RM_FloodedCanyonDefOf.RM_CanyonBeat_PanTick?.PlayOneShot(SoundInfo.InMap(new TargetInfo(p.Position, map)));
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
        // that arrival point: far, then nearer, then nearest. Until the map
        // carries physical chime-line anchors (CRACKEDLANDS_LEDGES_OF_MERCY_1)
        // these are positions, not things.
        private static readonly float[] ChimeLinePositions = { 0f, 0.5f, 0.85f };

        private IntVec3 ChimeCell(int stage)
        {
            if (!pendingSeed.IsValid)
            {
                return map.Center;
            }
            IntVec3 far = FarCornerFrom(pendingSeed);
            float f = ChimeLinePositions[UnityEngine.Mathf.Clamp(stage, 0, ChimeLinePositions.Length - 1)];
            IntVec3 c = new IntVec3(
                UnityEngine.Mathf.RoundToInt(UnityEngine.Mathf.Lerp(far.x, pendingSeed.x, f)), 0,
                UnityEngine.Mathf.RoundToInt(UnityEngine.Mathf.Lerp(far.z, pendingSeed.z, f)));
            return c.ClampInsideMap(map);
        }

        private IntVec3 FarCornerFrom(IntVec3 seed)
        {
            int maxX = map.Size.x - 1;
            int maxZ = map.Size.z - 1;
            IntVec3[] corners = { new IntVec3(0, 0, 0), new IntVec3(maxX, 0, 0), new IntVec3(0, 0, maxZ), new IntVec3(maxX, 0, maxZ) };
            IntVec3 best = corners[0];
            for (int i = 1; i < corners.Length; i++)
            {
                if ((corners[i] - seed).LengthHorizontalSquared > (best - seed).LengthHorizontalSquared)
                {
                    best = corners[i];
                }
            }
            return best;
        }

        private static SoundDef ChimeSound(int stage)
        {
            switch (stage)
            {
                case 0: return RM_FloodedCanyonDefOf.RM_CanyonChime_Far;
                case 1: return RM_FloodedCanyonDefOf.RM_CanyonChime_Mid;
                default: return RM_FloodedCanyonDefOf.RM_CanyonChime_Near;
            }
        }

        // Beat 5: the flood is a continuous roar, sited where the water came in.
        private void MaintainRoar()
        {
            if (!RM_FloodedCanyonSettings.fiveBeatsEnabled || !roarCell.IsValid || RM_FloodedCanyonDefOf.RM_CanyonFlood_Roar == null)
            {
                return;
            }
            if (roar == null || roar.Ended)
            {
                roar = RM_FloodedCanyonDefOf.RM_CanyonFlood_Roar.TrySpawnSustainer(
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
            IntVec3 at = RM_FloodedCanyonSettings.fiveBeatsEnabled ? ChimeCell(stage) : map.Center;
            Messages.Message(
                ChimeStageMessages[stage],
                new TargetInfo(at, map),
                MessageTypeDefOf.ThreatBig);
            SoundDef chime = RM_FloodedCanyonSettings.fiveBeatsEnabled ? ChimeSound(stage) : null;
            if (chime != null)
            {
                chime.PlayOneShot(SoundInfo.InMap(new TargetInfo(at, map)));
            }
            else
            {
                SoundDefOf.TinyBell.PlayOneShotOnCamera(map);
            }
        }

        private void StartFlood(int now)
        {
            int target = UnityEngine.Mathf.Clamp(map.Area / 20, 40, 400);
            List<IntVec3> cells = ComputeFloodCells(target, pendingSeed);
            roarCell = cells.Count > 0 ? cells[0] : IntVec3.Invalid;
            pendingSeed = IntVec3.Invalid;
            heraldBeat = 0;

            int durationTicks = HoursToTicks(RM_FloodedCanyonSettings.floodDurationHours);
            floodEndTick = now + durationTicks;
            // crack_flood — "the canonical soak" (explosive_plant_growth_design.md
            // §1). The flood no longer keeps a soak map of its own: it hands
            // every cell it wets to mandrake.rm.explosivegrowth, which owns the
            // SOAKED state, the growth multiplier and everything after. Soaked
            // for the flood's duration plus the decay days.
            int soakTicks = (floodEndTick - now) + DaysToTicks(RM_FloodedCanyonSettings.soakDecayDays);

            TerrainDef floodTerrain = TerrainDefOf.WaterMovingShallow;
            RM_MapComponent_Excavation excavation = Excavation;

            activeFloodCells.Clear();
            raisedFillCells.Clear();
            raisedFillPrior.Clear();
            for (int i = 0; i < cells.Count; i++)
            {
                IntVec3 c = cells[i];
                // CANYON_FLOOD_ERASES_CANALS_1. An excavated cell belongs to
                // FlowWorks: the flood raises its FILL and never its terrain,
                // so a channel, a pit or a SUPERDEEP hole is filled by the
                // water rather than erased by it. Prior F is recorded here,
                // not in the engine, because only this driver knows what its
                // own recede means.
                if (excavation != null && excavation.IsExcavated(c))
                {
                    int prior = excavation.FillAt(c);
                    if (excavation.TryFloodDriverCell(c))
                    {
                        raisedFillCells.Add(c);
                        raisedFillPrior.Add(prior);
                    }
                    // Continue EITHER WAY. The engine owning the cell is the
                    // invariant, not the raise succeeding: falling through to
                    // SetTerrain here would put the flood's terrain back on an
                    // excavated cell, which is the whole defect.
                    continue;
                }
                map.terrainGrid.SetTerrain(c, floodTerrain);
                activeFloodCells.Add(c);
            }

            if (RM_FloodedCanyonSettings.growthCouplingEnabled)
            {
                RM_ExplosiveGrowthBridge.SoakCells(map, cells, soakTicks);
            }

            if (RM_FloodedCanyonSettings.floodDamageEnabled)
            {
                DamagePawnsInCells(cells);
            }

            GameCondition cond = GameConditionMaker.MakeCondition(RM_FloodedCanyonDefOf.RM_CanyonFlood, durationTicks);
            map.gameConditionManager.RegisterCondition(cond);
        }

        // Two recede policies, one per cell class — ruling 8's "per-driver
        // recede policy" made concrete:
        //
        //   convert-to      the non-excavated wall. "Death, then soil":
        //                   convert it back to real fertile ground now that
        //                   it has stood its duration. A cell only converts
        //                   if it still holds the exact flood terrain this
        //                   mod placed — anything a player built, dug, or
        //                   otherwise changed mid-flood is left alone. That
        //                   check is also what covers a cell excavated
        //                   mid-flood: its terrain is no longer ours, so it
        //                   is skipped.
        //   restore-fill    the excavated half. Hand F back to what the cell
        //                   held before the water arrived, through the engine
        //                   that owns it. No terrain of ours ever touched it,
        //                   so there is nothing to launder.
        private void RecedeFlood()
        {
            TerrainDef floodTerrain = TerrainDefOf.WaterMovingShallow;
            TerrainDef soilTerrain = TerrainDefOf.SoilRich;

            // CRACKEDLANDS_MECHANICS_BUILD_1 §3: the flood re-cuts the ledger.
            // The whole wetted footprint (both halves) is the wall line the
            // water scoured; a few natural-rock cells touching it become
            // fresh fossil seams. Taken before the lists are cleared below.
            List<IntVec3> wetted = new List<IntVec3>(activeFloodCells);
            wetted.AddRange(raisedFillCells);
            if (RM_FloodedCanyonSettings.floodRecutSeamsEnabled)
            {
                RM_FossilStrata.RecutAlong(map, wetted, RM_FloodedCanyonSettings.floodRecutSeamCount);
            }

            for (int i = 0; i < activeFloodCells.Count; i++)
            {
                IntVec3 c = activeFloodCells[i];
                if (!c.InBounds(map))
                {
                    continue;
                }
                if (map.terrainGrid.TerrainAt(c) == floodTerrain)
                {
                    map.terrainGrid.SetTerrain(c, soilTerrain);
                }
            }
            activeFloodCells.Clear();

            RM_MapComponent_Excavation excavation = Excavation;
            if (excavation != null)
            {
                int n = System.Math.Min(raisedFillCells.Count, raisedFillPrior.Count);
                for (int i = 0; i < n; i++)
                {
                    IntVec3 c = raisedFillCells[i];
                    if (!c.InBounds(map))
                    {
                        continue;
                    }
                    // Returns false if the cell stopped being excavated while
                    // the flood stood (a fill-in), which is the correct
                    // outcome: there is no F left to lower and the engine has
                    // already decided what that cell is.
                    excavation.TrySetDriverFill(c, raisedFillPrior[i]);
                }
            }
            raisedFillCells.Clear();
            raisedFillPrior.Clear();

            roar?.End();
            roar = null;
            roarCell = IntVec3.Invalid;

            // CRACKEDLANDS_GPT_ENRICHMENT_1 §5/§6: the irqit carpet, the
            // migrant sky and the floodline salvage. After the soil
            // conversion, so they land on the ground the recede left.
            map.GetComponent<RM_MapComponent_RecedeAftermath>()?.OnRecede(wetted);
        }

        private List<IntVec3> ComputeFloodCells(int target, IntVec3 preferredSeed)
        {
            List<IntVec3> result = new List<IntVec3>();

            // The seed chosen when the warning began, if the ground there is
            // still floodable; otherwise a fresh one, as before.
            IntVec3 seed = preferredSeed;
            if ((!seed.IsValid || !Eligible(seed))
                && !CellFinderLoose.TryGetRandomCellWith(Eligible, map, 2000, out seed))
            {
                return result;
            }

            HashSet<IntVec3> visited = new HashSet<IntVec3> { seed };
            Queue<IntVec3> frontier = new Queue<IntVec3>();
            frontier.Enqueue(seed);

            while (frontier.Count > 0 && result.Count < target)
            {
                IntVec3 c = frontier.Dequeue();
                if (!Eligible(c))
                {
                    continue;
                }
                result.Add(c);

                for (int i = 0; i < GenAdj.CardinalDirections.Length; i++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[i];
                    if (n.InBounds(map) && !visited.Contains(n))
                    {
                        visited.Add(n);
                        // Ragged edge rather than a perfect diamond.
                        if (Rand.Value < 0.88f)
                        {
                            frontier.Enqueue(n);
                        }
                    }
                }
            }

            return result;
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
            Scribe_Values.Look(ref phase, "phase", Phase.Dry);
            Scribe_Values.Look(ref nextFloodTick, "nextFloodTick", -1);
            Scribe_Values.Look(ref floodEndTick, "floodEndTick", -1);
            Scribe_Values.Look(ref lastRecedeTick, "lastRecedeTick", -1);
            Scribe_Values.Look(ref chimeStage, "chimeStage", 0);
            Scribe_Values.Look(ref peakstormPulledThisCycle, "peakstormPulledThisCycle", false);
            Scribe_Values.Look(ref heraldBeat, "heraldBeat", 0);
            Scribe_Values.Look(ref pendingSeed, "pendingSeed", IntVec3.Invalid);
            Scribe_Values.Look(ref roarCell, "roarCell", IntVec3.Invalid);
            Scribe_Collections.Look(ref activeFloodCells, "activeFloodCells", LookMode.Value);
            Scribe_Collections.Look(ref raisedFillCells, "raisedFillCells", LookMode.Value);
            Scribe_Collections.Look(ref raisedFillPrior, "raisedFillPrior", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (activeFloodCells == null) activeFloodCells = new List<IntVec3>();
                if (raisedFillCells == null) raisedFillCells = new List<IntVec3>();
                if (raisedFillPrior == null) raisedFillPrior = new List<int>();
            }
        }
    }
}
