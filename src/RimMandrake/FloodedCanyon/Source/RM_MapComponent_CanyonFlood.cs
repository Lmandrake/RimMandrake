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
    // This mod owns the biome, the phase clock, the chime and the soak. It
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
        // NON-EXCAVATED cells only: an excavated one is never written here.
        private List<IntVec3> activeFloodCells = new List<IntVec3>();

        // The excavated half of this cycle's footprint, and what each of
        // those cells held before the flood raised it. Two parallel lists
        // rather than a dictionary purely because Scribe_Collections writes
        // a List<T> of values with no working-list dance; they are always
        // the same length and are cleared together.
        private List<IntVec3> raisedFillCells = new List<IntVec3>();
        private List<int> raisedFillPrior = new List<int>();

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
                "phase={0} nextFloodTick={1} floodEndTick={2} nowTick={3} activeFloodCells={4} "
                + "raisedFillCells={5} soakedCells={6} active={7} flowWorksEngine={8}",
                phase, nextFloodTick, floodEndTick, Find.TickManager.TicksGame,
                activeFloodCells.Count, raisedFillCells.Count, soakUntilTick.Count, Active,
                Excavation != null ? "present" : "ABSENT");
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
                    soakUntilTick[c] = soakUntil;
                    continue;
                }
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
            Scribe_Collections.Look(ref raisedFillCells, "raisedFillCells", LookMode.Value);
            Scribe_Collections.Look(ref raisedFillPrior, "raisedFillPrior", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (soakUntilTick == null) soakUntilTick = new Dictionary<IntVec3, int>();
                if (activeFloodCells == null) activeFloodCells = new List<IntVec3>();
                if (raisedFillCells == null) raisedFillCells = new List<IntVec3>();
                if (raisedFillPrior == null) raisedFillPrior = new List<int>();
            }
        }
    }
}
