using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F3 build pass (forge_kit_spec.md "F3. The vapor-column
    // flight layer"). The pasture-binding half of the sky-fauna mechanic — a
    // per-map field of "this cell counts as a vapor column" cells, built from
    // real emitter positions rather than any bespoke Forge content, so it is
    // reusable by any future biome that ships vents/geysers/melt.
    //
    // What counts as a column source (generic, not Forge-hardcoded):
    //   - any spawned RimWorld.Building_SteamGeyser (native steam geysers,
    //     and this repo's own SCALD_MECHANICS_1 clone RUT_ScaldVent, which
    //     shares that thingClass verbatim per its own header) — a real vent;
    //   - any spawned Thing carrying CompActiveGasEmitter — the ruled
    //     kit's harmless-gas emitter reuse the F3 spec's own text names
    //     ("The vent props themselves are the ruled RM_CompActiveGasEmitter
    //     reuse ... zero new emitter C#"); no Forge vent content uses this
    //     comp yet (checked this pass — RUT_ScaldVent's own header explicitly
    //     says it does NOT, that was a stale brief-vs-spec correction on a
    //     different item), so this is forward-looking, not dead code;
    //   - any terrain cell flagged dangerous+avoidWander — the exact two
    //     fields FORGE_MECHANICS_1's own spike pass confirmed on vanilla
    //     LavaShallow (open, walkable melt: "dangerous=true, avoidWander=true"),
    //     read generically rather than by defName/"Lava" substring so any
    //     biome's own hazardous-open-melt terrain qualifies without this
    //     class needing to know its name.
    //
    // "at map init + on-change" (the spec's own line): implemented as a full
    // rebuild on FinalizeInit plus a periodic rescan (every in-game hour,
    // the same 2500-ticks/hour conversion RM_GameCondition_WeatherPulse and
    // RM_CompScriptedDieOff already use) rather than push notifications from
    // every possible emitter/terrain-change source. Emitters are near-static
    // once placed (vents, geysers, melt terrain do not move or get built over
    // in the middle of ordinary play) so an hourly rescan is a fair proxy for
    // "on-change" at a fraction of the coupling cost of wiring spawn/despawn
    // callbacks into CompActiveGasEmitter and a terrain-changed hook — both
    // of which are cross-kit surfaces this task's own scope note says not to
    // fork/extend for F3's sake. RebuildNow() is public so a quicktest (or a
    // future GenStep that places a vent) can force an immediate rebuild
    // instead of waiting out the hour.
    //
    // Not Scribe-saved: the field is entirely derived from map content
    // (things + terrain), so FinalizeInit's own rebuild reconstructs it
    // identically on load — same reasoning RM_MapComponent_GradientAxis's
    // own header gives for deferring a per-cell save format until one is
    // actually needed.
    public class RM_MapComponent_VaporColumns : MapComponent
    {
        // INVENTED (F3 spec: "builds a column field from emitter positions").
        // No figure for the column's own radius is given in the spec beyond
        // "at" those positions — 6 cells is a starting value: bigger than a
        // single geyser's (2,2) footprint, small enough that widely spaced
        // vents don't merge into one continuous pasture by default.
        public const float DefaultColumnRadius = 6f;

        private const int RescanIntervalTicks = 2500; // 1 in-game hour

        private bool[] columnField;
        private int ticksUntilRescan = 1;
        private bool everBuilt;

        public RM_MapComponent_VaporColumns(Map map)
            : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            RebuildNow();
            ticksUntilRescan = RescanIntervalTicks; // avoid an immediate redundant rebuild next tick
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (--ticksUntilRescan > 0)
            {
                return;
            }

            ticksUntilRescan = RescanIntervalTicks;
            RebuildNow();
        }

        public bool InColumn(IntVec3 cell)
        {
            if (!everBuilt)
            {
                RebuildNow();
            }

            if (columnField == null || !cell.InBounds(map))
            {
                return false;
            }

            return columnField[map.cellIndices.CellToIndex(cell)];
        }

        // Nearest column cell to `from`, searching outward to `maxDist` cells.
        // Used by RM_JobGiver_ColumnWander as the wander-root override target;
        // returns IntVec3.Invalid if nothing is in range (caller falls back
        // to the pawn's own position, same fallback shape
        // RM_JobGiver_AnchorWander uses).
        public IntVec3 NearestColumnCell(IntVec3 from, float maxDist)
        {
            if (!everBuilt)
            {
                RebuildNow();
            }

            if (columnField == null || maxDist <= 0f)
            {
                return IntVec3.Invalid;
            }

            int maxRadius = Mathf.CeilToInt(maxDist);
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(from, maxRadius, useCenter: true))
            {
                if (cell.InBounds(map) && InColumn(cell))
                {
                    return cell;
                }
            }

            return IntVec3.Invalid;
        }

        public void RebuildNow()
        {
            everBuilt = true;

            int n = map.cellIndices.NumGridCells;
            if (columnField == null || columnField.Length != n)
            {
                columnField = new bool[n];
            }
            else
            {
                Array.Clear(columnField, 0, n);
            }

            List<Thing> allThings = map.listerThings.AllThings;
            for (int i = 0; i < allThings.Count; i++)
            {
                Thing t = allThings[i];
                if (IsEmitter(t))
                {
                    PaintAround(t.Position, DefaultColumnRadius);
                }
            }

            foreach (IntVec3 cell in map.AllCells)
            {
                TerrainDef terrain = cell.GetTerrain(map);
                if (terrain != null && terrain.dangerous && terrain.avoidWander)
                {
                    PaintAround(cell, DefaultColumnRadius);
                }
            }
        }

        private void PaintAround(IntVec3 center, float radius)
        {
            foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, radius, useCenter: true))
            {
                if (cell.InBounds(map))
                {
                    columnField[map.cellIndices.CellToIndex(cell)] = true;
                }
            }
        }

        private static bool IsEmitter(Thing t)
        {
            if (t is Building_SteamGeyser)
            {
                return true;
            }

            return t.TryGetComp<CompActiveGasEmitter>() != null;
        }
    }
}
