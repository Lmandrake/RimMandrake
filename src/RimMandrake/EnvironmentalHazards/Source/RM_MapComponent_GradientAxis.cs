using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M1 spike + M2 build (miasma_kit_spec.md). The
    // fresh->brine axis: a per-map scalar field, 0f fresh .. 1f brine, that
    // M2's surge shoves and M3/M4/M6 read.
    //
    // M1 SPIKE SCOPE proved the storage + API shape only — SalinityAt,
    // SetSalinityAt, SaltLineCells, and ShiftAxis's entry point signature.
    // M2 (this pass) adds the part that spike explicitly deferred: the
    // actual per-tick walk (TickShift/ApplyDeltaToAllCells below) and the
    // MTB-driven surge trigger (TickSurgeRoll). Both live HERE, on the
    // MapComponent, rather than on RM_GameCondition_GradientSurge, for one
    // load-bearing reason: a MapComponent ticks for as long as the map
    // exists; a GameCondition is destroyed the moment it Ends. The recede
    // (miasma_kit_spec.md M2: "the shove back... over days") is explicitly
    // started at the condition's End() but must keep moving for 2-4
    // INVENTED days AFTER that condition object is gone — only something
    // that outlives the condition can carry it, so it has to be here.
    // Owed, not silently skipped (unchanged from the M1 spike, M2 not
    // touching either):
    //   - the "coarse grid" downsample the spec mentions (perf tuning, not
    //     an engine fact, deferred to the full build);
    //   - Scribe save/load of the grid itself (TerrainGrid.
    //     ExposeTerrainGrid's per-cell ushort-array pattern is the model
    //     to crib — Verse/TerrainGrid.cs:671 — not reproduced here since
    //     no per-cell save format decision has been made yet). M2 does NOT
    //     need this: the per-tick walk only ever ADDS a delta to whatever
    //     salinity[] already holds, so a save mid-shift loses no more than
    //     the grid itself already did before this pass — shiftInProgress/
    //     shiftDeltaRemaining/shiftTicksRemaining/shiftIsRecede are scribed,
    //     so the SHIFT resumes correctly; only the per-cell field's own
    //     absolute values (fresh vs brine at any one cell) don't survive a
    //     save, exactly as already flagged.
    public class RM_MapComponent_GradientAxis : MapComponent
    {
        private float[] salinity;

        // M2's shift-in-progress state. Scribed so a save mid-surge
        // doesn't silently forget it.
        private bool shiftInProgress;
        private float shiftDeltaRemaining;
        private int shiftTicksRemaining;

        // Distinguishes a forward shove from a recede-back shift, so
        // TickShift knows whether completion should fire the M3 handoff
        // signal below (M3 only cares about a RECEDE finishing, not a
        // forward shove — "recede is what arms M3", miasma_kit_spec.md M2).
        private bool shiftIsRecede;

        // M3's own handoff signal (this item's M2 assignment: "expose
        // whatever signal/state M3 will need to read later"). -1 = no
        // recede has ever completed on this map. M3 (a separate, later
        // build) reads this and compares against its own last-seen tick to
        // detect a NEW recede finishing, without needing an event/callback
        // that wouldn't survive a save/load.
        private int lastRecedeCompletedTick = -1;

        // Throttle for both TickShift's grid walk and TickSurgeRoll's MTB
        // check — GenTicks.TickRareInterval (250 ticks, ~4.2 real seconds),
        // the same "rare tick" cadence vanilla itself uses for exactly this
        // kind of "too expensive/unnecessary to run every tick" per-map
        // work. Jittered at construction so every Miasma map on a multi-map
        // save doesn't all land on the same global tick.
        private const int UpdateIntervalTicks = GenTicks.TickRareInterval;
        private int updateCooldown;

        // Salt-line presentation while ANY shift runs (miasma_kit_spec.md
        // M2: "the salt line drawn as a subtle ground fleck line while the
        // condition runs" — read generously as "while the terrain is
        // actually moving", which spans the recede too, since the recede
        // continues after the GameCondition itself has ended and stopped
        // drawing anything). INVENTED-BUILD tuning, not the spec's own
        // numbers: a sparse per-cell roll during the grid walk keeps this
        // cheap (no second full-map pass just to find SaltLineCells()).
        private const float SaltLineFleckBand = 0.03f;
        private const float SaltLineFleckChance = 0.01f;
        private const float SaltLineFleckScale = 1.2f;
        private static readonly Color SaltLineFleckColor = new Color(0.9f, 0.92f, 0.85f);

        public RM_MapComponent_GradientAxis(Map map)
            : base(map)
        {
            updateCooldown = Rand.RangeInclusive(1, UpdateIntervalTicks);
        }

        private void EnsureGrid()
        {
            int n = map.cellIndices.NumGridCells;
            if (salinity == null || salinity.Length != n)
            {
                salinity = new float[n];
            }
        }

        public float SalinityAt(IntVec3 c)
        {
            EnsureGrid();
            if (!c.InBounds(map))
            {
                return 0f;
            }
            return salinity[map.cellIndices.CellToIndex(c)];
        }

        public void SetSalinityAt(IntVec3 c, float value)
        {
            EnsureGrid();
            if (!c.InBounds(map))
            {
                return;
            }
            salinity[map.cellIndices.CellToIndex(c)] = Mathf.Clamp01(value);
        }

        // M2's entry point (RM_GameCondition_GradientSurge calls this on
        // the surge's ramp-in/recede). Records the requested shift; TickShift
        // (below, called from MapComponentTick) is what actually walks it
        // cell-by-cell. Kept as the original 2-arg spike signature — nothing
        // outside this pass called it yet, but changing it in place would
        // widen this pass's diff for no reason; the recede needs a third
        // parameter, added as a new overload instead.
        public void ShiftAxis(float delta, int durationTicks)
        {
            ShiftAxis(delta, durationTicks, isRecede: false);
        }

        public void ShiftAxis(float delta, int durationTicks, bool isRecede)
        {
            shiftInProgress = true;
            shiftDeltaRemaining = delta;
            shiftTicksRemaining = durationTicks < 1 ? 1 : durationTicks;
            shiftIsRecede = isRecede;
        }

        public bool ShiftInProgress => shiftInProgress;

        // M3's handoff signal (see field header above). -1 = never.
        public int LastRecedeCompletedTick => lastRecedeCompletedTick;

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (--updateCooldown > 0)
            {
                return;
            }
            updateCooldown = UpdateIntervalTicks;

            if (shiftInProgress)
            {
                TickShift();
            }
            else
            {
                TickSurgeRoll();
            }
        }

        // Advances the in-progress shift by this throttled step's share of
        // whatever delta/time remain. Each step consumes a PROPORTIONAL
        // slice of the remaining budget over the remaining time
        // (deltaThisStep = shiftDeltaRemaining * step/shiftTicksRemaining),
        // so the steps telescope to exactly the original total with no
        // rounding drift, and a shift's length only ever needs the two
        // scribed "remaining" counters — no separate start-of-shift
        // snapshot of the whole grid.
        private void TickShift()
        {
            int step = Mathf.Min(UpdateIntervalTicks, shiftTicksRemaining);
            float deltaThisStep = shiftTicksRemaining > 0
                ? shiftDeltaRemaining * step / shiftTicksRemaining
                : shiftDeltaRemaining;

            ApplyDeltaToAllCells(deltaThisStep);

            shiftDeltaRemaining -= deltaThisStep;
            shiftTicksRemaining -= step;

            if (shiftTicksRemaining <= 0)
            {
                shiftInProgress = false;
                shiftDeltaRemaining = 0f;
                if (shiftIsRecede)
                {
                    lastRecedeCompletedTick = Find.TickManager.TicksGame;
                }
            }
        }

        // The repaint (miasma_kit_spec.md M2's own "hard part") and the
        // salt-line presentation both ride this one pass over every cell,
        // rather than a second full-map scan for each — see
        // RM_GradientAxisRepaint's header for the floor-exclusion fix this
        // applies on every SetTerrain-equivalent write.
        private void ApplyDeltaToAllCells(float delta)
        {
            if (delta == 0f)
            {
                return;
            }

            EnsureGrid();
            RM_GradientAxisExtension ext = map.Biome != null ? map.Biome.GetModExtension<RM_GradientAxisExtension>() : null;

            foreach (IntVec3 c in map.AllCells)
            {
                int idx = map.cellIndices.CellToIndex(c);
                float newSalinity = Mathf.Clamp01(salinity[idx] + delta);
                salinity[idx] = newSalinity;

                if (ext != null)
                {
                    RM_GradientAxisRepaint.RepaintCell(map, c, newSalinity, ext);
                }

                if (Mathf.Abs(newSalinity - 0.5f) < SaltLineFleckBand && Rand.Chance(SaltLineFleckChance))
                {
                    FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, SaltLineFleckScale, SaltLineFleckColor);
                }
            }
        }

        // The MTB clock itself (miasma_kit_spec.md M2, ban #4: "never
        // scheduled... the def carries no period field"). Deliberately NOT
        // driven by RUT_Surge.xml's own Storyteller category — see that
        // file's header for why its category is Misc — this mechanism owns
        // its entire schedule here, in code, gated per-biome by
        // RM_GradientSurgeExtension being present at all (same "extension
        // absent = mechanism does nothing" fail-safe M1's own gate uses).
        private void TickSurgeRoll()
        {
            RM_GradientSurgeExtension ext = map.Biome != null ? map.Biome.GetModExtension<RM_GradientSurgeExtension>() : null;
            if (ext == null || ext.incidentDef == null)
            {
                return;
            }

            float mtbDays = ext.baseMtbDays;
            // "Storm weather active", resolved concretely — see
            // RM_GradientSurgeExtension's own header for why this reads
            // live wind gust strength rather than the map's current
            // WeatherDef (M4's RUT_MiasmaWeatherLock makes every OTHER
            // weather provably unreachable here, so there is no on-map
            // "storm weather" state left to check).
            if (map.windManager != null && map.windManager.WindSpeed >= ext.stormWindSpeedThreshold)
            {
                mtbDays *= ext.stormMtbMultiplier;
            }

            if (!Rand.MTBEventOccurs(mtbDays, GenDate.TicksPerDay, UpdateIntervalTicks))
            {
                return;
            }

            IncidentParms parms = StorytellerUtility.DefaultParmsNow(ext.incidentDef.category, map);
            if (ext.incidentDef.Worker.CanFireNow(parms))
            {
                ext.incidentDef.Worker.TryExecute(parms);
            }
        }

        public IEnumerable<IntVec3> SaltLineCells(float band = 0.05f)
        {
            EnsureGrid();
            foreach (IntVec3 c in map.AllCells)
            {
                float s = salinity[map.cellIndices.CellToIndex(c)];
                if (s > 0.5f - band && s < 0.5f + band)
                {
                    yield return c;
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shiftInProgress, "shiftInProgress", false);
            Scribe_Values.Look(ref shiftDeltaRemaining, "shiftDeltaRemaining", 0f);
            Scribe_Values.Look(ref shiftTicksRemaining, "shiftTicksRemaining", 0);
            Scribe_Values.Look(ref shiftIsRecede, "shiftIsRecede", false);
            Scribe_Values.Look(ref lastRecedeCompletedTick, "lastRecedeCompletedTick", -1);
            Scribe_Values.Look(ref updateCooldown, "updateCooldown", 0);
        }
    }
}
