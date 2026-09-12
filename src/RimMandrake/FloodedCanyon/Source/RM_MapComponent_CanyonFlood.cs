using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // THE FLOOD CYCLE ENGINE. Auto-attached to every map by vanilla's own
    // Map.FillComponents (any non-abstract MapComponent subclass with a
    // (Map) constructor gets one instance per map — confirmed against the
    // 1.6 assembly; no Harmony wiring needed, same as the sibling
    // Greentide mod's own map components).
    //
    // Deliberately does NOT subclass vanilla's Odyssey-gated `Flood` Thing
    // (RimWorld/Flood.cs, ModLister.CheckOdyssey-gated, used by the sibling
    // FluidCanals mod for a channel-fed release) and deliberately does NOT
    // use TerrainGrid.SetTempTerrain either: every terrain marked
    // `temporary="true"` in the base game (ShallowFloodwater, MarshFlood)
    // is itself [MayRequireOdyssey] — MEASURED against the 1.6 assembly's
    // own TerrainDefOf, RimSage 2026-09. This mod ships for every player,
    // DLC or not, so the wall and its recede are both plain PERMANENT
    // TerrainGrid.SetTerrain calls, driven by this component's own phase
    // clock rather than TempTerrainManager: flood on with WaterMovingShallow
    // (Core, always present), soil on with SoilRich, each cell converted
    // back to soil ONLY if it still holds the exact flood terrain this
    // mod placed — if a player built or dug there mid-flood, that change
    // is left alone.
    //
    // One GameCondition (RM_CanyonFlood, plain vanilla GameCondition class
    // — nothing to override, every effect lives here) is registered purely
    // as the player-visible signal: the letter, the end message, the
    // "canyon flood" chip in the condition bar. It carries no mechanism of
    // its own.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_CanyonFlood : MapComponent
    {
        private enum Phase : byte { Dry, Warned, Flooding }

        private Phase phase = Phase.Dry;

        // -1 == not yet scheduled (set on first FinalizeInit/tick).
        private int nextFloodTick = -1;
        private int floodEndTick = -1;

        // Cell -> tick its soak-driven growth bonus expires. Read by
        // RM_Patch_Plant_GrowthRate every plant tick; written only here.
        private Dictionary<IntVec3, int> soakUntilTick = new Dictionary<IntVec3, int>();

        // Cells this cycle's flood is currently standing on, to convert
        // back to soil at recede time (only if still ours — see header).
        private List<IntVec3> activeFloodCells = new List<IntVec3>();

        private List<IntVec3> tmpKeys = new List<IntVec3>();
        private List<int> tmpValues = new List<int>();

        public RM_MapComponent_CanyonFlood(Map map) : base(map)
        {
        }

        private bool Active =>
            RM_FloodedCanyonSettings.floodCycleEnabled
            && (map.Biome == RM_FloodedCanyonDefOf.RM_FloodedCanyon || RM_FloodedCanyonSettings.featureInOtherBiomes);

        // Public for RM_Patch_Plant_GrowthRate. Never allocates.
        public float SoakFactorAt(IntVec3 cell, int nowTick)
        {
            if (!RM_FloodedCanyonSettings.growthCouplingEnabled)
            {
                return 1f;
            }
            if (soakUntilTick.TryGetValue(cell, out int until) && nowTick < until)
            {
                return System.Math.Max(1f, RM_FloodedCanyonSettings.growthMultiplier);
            }
            return 1f;
        }

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

        public string DebugStateReport()
        {
            return string.Format(
                "phase={0} nextFloodTick={1} floodEndTick={2} nowTick={3} activeFloodCells={4} soakedCells={5} active={6}",
                phase, nextFloodTick, floodEndTick, Find.TickManager.TicksGame,
                activeFloodCells.Count, soakUntilTick.Count, Active);
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
                    if (now >= nextFloodTick - HoursToTicks(RM_FloodedCanyonSettings.chimeLeadTimeHours))
                    {
                        RingChime();
                        phase = Phase.Warned;
                    }
                    break;

                case Phase.Warned:
                    if (now >= nextFloodTick)
                    {
                        StartFlood(now);
                        phase = Phase.Flooding;
                    }
                    break;

                case Phase.Flooding:
                    if (now >= floodEndTick)
                    {
                        RecedeFlood();
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

        private void ScheduleNextFlood()
        {
            int periodTicks = DaysToTicks(RM_FloodedCanyonSettings.floodPeriodDays);
            int jitter = Rand.RangeInclusive(-periodTicks / 3, periodTicks / 3);
            nextFloodTick = Find.TickManager.TicksGame + System.Math.Max(2500, periodTicks + jitter);
        }

        private void RingChime()
        {
            // "the water chimes ring... tones rolling up through the stone
            // ahead of any sound of water" (source sheet), generalized to a
            // reused vanilla notification cue rather than commissioning new
            // audio for v1 (same call the sibling WeatherSuite mod made
            // reusing an existing texture for its instrument mast).
            Messages.Message(
                "The water chimes are ringing — a flood is coming down the canyon.",
                new TargetInfo(map.Center, map),
                MessageTypeDefOf.ThreatBig);
            SoundDefOf.TinyBell.PlayOneShotOnCamera(map);
        }

        private void StartFlood(int now)
        {
            PruneSoak(now);

            int target = UnityEngine.Mathf.Clamp(map.Area / 20, 40, 400);
            List<IntVec3> cells = ComputeFloodCells(target);

            int durationTicks = HoursToTicks(RM_FloodedCanyonSettings.floodDurationHours);
            floodEndTick = now + durationTicks;
            int soakUntil = floodEndTick + DaysToTicks(RM_FloodedCanyonSettings.soakDecayDays);

            TerrainDef floodTerrain = TerrainDefOf.WaterMovingShallow;

            activeFloodCells.Clear();
            for (int i = 0; i < cells.Count; i++)
            {
                IntVec3 c = cells[i];
                map.terrainGrid.SetTerrain(c, floodTerrain);
                activeFloodCells.Add(c);
                soakUntilTick[c] = soakUntil;
            }

            if (RM_FloodedCanyonSettings.floodDamageEnabled)
            {
                DamagePawnsInCells(cells);
            }

            GameCondition cond = GameConditionMaker.MakeCondition(RM_FloodedCanyonDefOf.RM_CanyonFlood, durationTicks);
            map.gameConditionManager.RegisterCondition(cond);
        }

        // "Death, then soil": convert the wall back to real fertile ground
        // now that it has stood its duration. A cell only converts if it
        // still holds the exact flood terrain this mod placed — anything a
        // player built, dug, or otherwise changed mid-flood is left alone.
        private void RecedeFlood()
        {
            TerrainDef floodTerrain = TerrainDefOf.WaterMovingShallow;
            TerrainDef soilTerrain = TerrainDefOf.SoilRich;

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
        }

        private List<IntVec3> ComputeFloodCells(int target)
        {
            List<IntVec3> result = new List<IntVec3>();

            if (!CellFinderLoose.TryGetRandomCellWith(Eligible, map, 2000, out IntVec3 seed))
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
                return false;
            }
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

        private void PruneSoak(int now)
        {
            if (soakUntilTick.Count == 0)
            {
                return;
            }
            List<IntVec3> stale = null;
            foreach (KeyValuePair<IntVec3, int> kv in soakUntilTick)
            {
                if (kv.Value <= now)
                {
                    (stale ?? (stale = new List<IntVec3>())).Add(kv.Key);
                }
            }
            if (stale != null)
            {
                for (int i = 0; i < stale.Count; i++)
                {
                    soakUntilTick.Remove(stale[i]);
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref phase, "phase", Phase.Dry);
            Scribe_Values.Look(ref nextFloodTick, "nextFloodTick", -1);
            Scribe_Values.Look(ref floodEndTick, "floodEndTick", -1);
            Scribe_Collections.Look(ref soakUntilTick, "soakUntilTick", LookMode.Value, LookMode.Value, ref tmpKeys, ref tmpValues);
            Scribe_Collections.Look(ref activeFloodCells, "activeFloodCells", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (soakUntilTick == null) soakUntilTick = new Dictionary<IntVec3, int>();
                if (activeFloodCells == null) activeFloodCells = new List<IntVec3>();
            }
        }
    }
}
