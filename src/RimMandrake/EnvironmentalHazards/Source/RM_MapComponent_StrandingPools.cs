using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M3 build (miasma_kit_spec.md M3: "stranding pools
    // and the stranded"), "armed by M2's recede" — this item's own words,
    // and concretely: this component polls RM_MapComponent_GradientAxis.
    // LastRecedeCompletedTick (the exact handoff signal the M2 build pass
    // exposed for this purpose) on the SAME throttled-tick cadence M1/M2
    // already use, never inventing its own recede-detection.
    //
    // Auto-instantiated on every map (Map.FillComponents, same as every
    // other MapComponent in this file) — harmless everywhere else: on any
    // map whose biome never carries RM_GradientSurgeExtension,
    // axis.LastRecedeCompletedTick never advances past -1, so DetectPools
    // never runs and pools never populates. No separate biome gate is
    // needed at MapComponentTick's own top level for that reason; DetectPools
    // itself still gates on RM_StrandingPoolsExtension presence (below) so a
    // map that somehow received a stray recede signal without stranding
    // config configured still does nothing, matching M1/M2's own "extension
    // absent = mechanism does nothing" fail-safe pattern.
    //
    // Detection: a full flood-fill of the map's water-band cells (4-way,
    // matching vanilla's own room/region flood-fill convention) into
    // connected components. The LARGEST component is treated as the main
    // channel network; every other component is a candidate pool. A
    // candidate that shares any cell with an already-tracked pool is that
    // SAME pool (updated in place, not re-spawned); a candidate with no
    // overlap anywhere is brand new — registered and rolled for stranding
    // spawns immediately.
    //
    // Reconciliation (every throttled tick while any pool exists, not only
    // on a recede): each tracked pool gets a bounded local flood-fill from
    // one of its own cells. If that fill either reaches the map edge or
    // exceeds a size cap without terminating, the pool's water has become
    // part of something large/open again — read as "reconnected to the main
    // network," i.e. item 5's "re-covered by M2 restarting a shift over
    // previously-pooled cells." This is a deliberate, documented heuristic
    // (a full-map recompute every throttled tick would be needlessly
    // expensive) rather than a literal "is this the same component vanilla
    // rivers/coast connect to" proof — honest about the tradeoff, not
    // guessed at silently. Reconnected pools are simply removed: their
    // occupants were always ordinary spawned wild pawns on the map, tracked
    // here only as bookkeeping, so "rejoin the wild population" (spec's own
    // words) needs no further action.
    //
    // Decay: pools not reconnected shrink cell-by-cell toward zero over
    // decayTotalTicks (INVENTED, RM_StrandingPoolsExtension.decayDaysRange),
    // removing edge cells first (cells adjacent to dry ground) for a
    // visually reasonable "drying from the shore inward" — a simplification
    // of true erosion, not a physical simulation. Each removed cell repaints
    // via RM_GradientAxisRepaint.SetTerrainFloorSafe — the SAME floor-safe
    // write M2 built (this item's own assignment: "reuse it, don't fork
    // it") — to RM_StrandingPoolsExtension.dryTerrain, so a player floor
    // sitting over a decaying pool cell is never silently destroyed, exactly
    // the bug class M2's own build pass fixed for the surge repaint.
    //
    // The stranded: RM_JobGiver_ReturnToWater (a separate file, inserted
    // globally via RM_ThinkTree_StrandingBehaviors) reads
    // TryGetPoolFor/TryFindNearestChannelCell below once a pool's live cell
    // count drops to/below RM_StrandingPoolsExtension.poolSizeThreshold —
    // the REAL return-to-water job, not a stub. The explicit, documented
    // fallback the spec's own M3 text permits ("return-to-water job may land
    // as despawn at pool death first") still exists as a safety net for the
    // one case the job cannot resolve on its own: a pool that fully dries
    // (cells.Count reaches 0) while still holding occupants the job never
    // got to a channel (no reachable cell within searchRadius, blocked
    // pathing, etc.) — those are despawned, loudly logged, not silently
    // vanished.
    public class RM_MapComponent_StrandingPools : MapComponent
    {
        private List<RM_StrandingPool> pools = new List<RM_StrandingPool>();
        private int nextPoolId = 1;

        // -1 = no recede has ever been observed by THIS component (mirrors
        // RM_MapComponent_GradientAxis's own -1 = never convention).
        private int lastSeenRecedeTick = -1;

        // Same throttle/jitter shape as M1/M2's own MapComponentTick.
        private const int UpdateIntervalTicks = GenTicks.TickRareInterval;
        private int updateCooldown;

        public RM_MapComponent_StrandingPools(Map map)
            : base(map)
        {
            updateCooldown = Rand.RangeInclusive(1, UpdateIntervalTicks);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_EnvironmentalHazardsSettings.strandingPoolsEnabled)
            {
                return;
            }

            if (--updateCooldown > 0)
            {
                return;
            }
            updateCooldown = UpdateIntervalTicks;

            RM_MapComponent_GradientAxis axis = map.GetComponent<RM_MapComponent_GradientAxis>();
            if (axis == null)
            {
                return;
            }

            if (axis.LastRecedeCompletedTick >= 0 && axis.LastRecedeCompletedTick != lastSeenRecedeTick)
            {
                lastSeenRecedeTick = axis.LastRecedeCompletedTick;
                DetectPools();
            }

            if (pools.Count > 0)
            {
                ReconcileAndDecayPools();
            }
        }

        // ---- detection -----------------------------------------------

        private bool IsWaterCell(IntVec3 c)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            TerrainDef t = map.terrainGrid.BaseTerrainAt(c);
            return t != null && t.IsWater;
        }

        private void DetectPools()
        {
            RM_StrandingPoolsExtension ext = map.Biome != null ? map.Biome.GetModExtension<RM_StrandingPoolsExtension>() : null;
            if (ext == null)
            {
                return; // no config on this biome — mechanism does nothing, same as M1/M2's own gate
            }

            int n = map.cellIndices.NumGridCells;
            bool[] visited = new bool[n];
            List<List<IntVec3>> components = new List<List<IntVec3>>();

            foreach (IntVec3 start in map.AllCells)
            {
                int startIdx = map.cellIndices.CellToIndex(start);
                if (visited[startIdx] || !IsWaterCell(start))
                {
                    continue;
                }

                List<IntVec3> comp = new List<IntVec3>();
                Queue<IntVec3> queue = new Queue<IntVec3>();
                visited[startIdx] = true;
                queue.Enqueue(start);

                while (queue.Count > 0)
                {
                    IntVec3 cur = queue.Dequeue();
                    comp.Add(cur);

                    for (int d = 0; d < GenAdj.CardinalDirections.Length; d++)
                    {
                        IntVec3 nb = cur + GenAdj.CardinalDirections[d];
                        if (!nb.InBounds(map))
                        {
                            continue;
                        }
                        int nbIdx = map.cellIndices.CellToIndex(nb);
                        if (visited[nbIdx] || !IsWaterCell(nb))
                        {
                            continue;
                        }
                        visited[nbIdx] = true;
                        queue.Enqueue(nb);
                    }
                }

                components.Add(comp);
            }

            if (components.Count < 2)
            {
                return; // nothing but (at most) the main network — no disconnected water anywhere
            }

            List<IntVec3> mainNetwork = components[0];
            for (int i = 1; i < components.Count; i++)
            {
                if (components[i].Count > mainNetwork.Count)
                {
                    mainNetwork = components[i];
                }
            }

            // Map every already-tracked pool's cells to that pool once, so
            // matching a candidate component against existing pools is a
            // single dictionary probe per cell rather than an O(pools *
            // cells^2) scan.
            Dictionary<int, RM_StrandingPool> cellToPool = new Dictionary<int, RM_StrandingPool>();
            for (int p = 0; p < pools.Count; p++)
            {
                for (int i = 0; i < pools[p].cells.Count; i++)
                {
                    cellToPool[map.cellIndices.CellToIndex(pools[p].cells[i])] = pools[p];
                }
            }

            for (int i = 0; i < components.Count; i++)
            {
                List<IntVec3> comp = components[i];
                if (comp == mainNetwork)
                {
                    continue;
                }

                RM_StrandingPool existing = null;
                for (int c = 0; c < comp.Count && existing == null; c++)
                {
                    cellToPool.TryGetValue(map.cellIndices.CellToIndex(comp[c]), out existing);
                }

                if (existing != null)
                {
                    existing.cells = comp; // shape may have shifted between recede events — keep it current
                    continue;
                }

                RM_StrandingPool pool = new RM_StrandingPool
                {
                    id = nextPoolId++,
                    cells = comp,
                    originalCellCount = comp.Count,
                    birthTick = Find.TickManager.TicksGame,
                    decayTotalTicks = Mathf.Max(1, Mathf.RoundToInt(ext.decayDaysRange.RandomInRange * GenDate.TicksPerDay)),
                };
                pools.Add(pool);
                SpawnStrandedInto(pool, ext);
            }
        }

        private void SpawnStrandedInto(RM_StrandingPool pool, RM_StrandingPoolsExtension ext)
        {
            if (ext.strandedSpawnList.NullOrEmpty() || pool.cells.Count == 0)
            {
                return; // valid config: a biome may want pools with no stranded spawns at all
            }

            float total = ext.emptyWeight + ext.smallWeight + ext.bigWeight;
            if (total <= 0f)
            {
                return;
            }

            float roll = Rand.Range(0f, total);
            int count;
            if (roll < ext.emptyWeight)
            {
                count = 0;
            }
            else if (roll < ext.emptyWeight + ext.smallWeight)
            {
                count = ext.strandedCountSmall.RandomInRange;
            }
            else
            {
                count = ext.strandedCountBig.RandomInRange;
            }

            for (int i = 0; i < count; i++)
            {
                PawnKindDef kind = ext.strandedSpawnList.RandomElement();
                if (kind == null)
                {
                    continue;
                }

                IntVec3 spawnCell = pool.cells.RandomElement();
                PawnGenerationRequest request = new PawnGenerationRequest(
                    kind, null, PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, canGeneratePawnRelations: false);
                Pawn pawn = PawnGenerator.GeneratePawn(request);
                GenSpawn.Spawn(pawn, spawnCell, map);
                pool.occupants.Add(pawn);

                // COMMISSION_LEDGER_CLEANUP_1 the_miasma sheet, slug
                // `the-stranded-transitional-orphan-forms-2-3-species`. The
                // roster's own minority "deformed, does not thrive" tier
                // (miasma_fauna_roster_2026-09-23.md §5), rolled per pawn
                // rather than per pool so a "big" (3-5) draw doesn't
                // deform all of them together.
                if (ext.strandedDeformationHediff != null && Rand.Chance(ext.strandedDeformationChance))
                {
                    pawn.health.AddHediff(ext.strandedDeformationHediff);
                }
            }
        }

        // ---- reconciliation + decay ------------------------------------

        private void ReconcileAndDecayPools()
        {
            RM_StrandingPoolsExtension ext = map.Biome != null ? map.Biome.GetModExtension<RM_StrandingPoolsExtension>() : null;

            for (int i = pools.Count - 1; i >= 0; i--)
            {
                RM_StrandingPool pool = pools[i];
                PruneOccupants(pool);

                if (IsReconnected(pool))
                {
                    // Item 5: re-covered by the next surge — deregister, no
                    // despawn. Occupants were always ordinary spawned wild
                    // pawns on this map; this list was bookkeeping only.
                    pools.RemoveAt(i);
                    continue;
                }

                DecayPool(pool, ext);

                if (pool.cells.Count == 0)
                {
                    DespawnStrandedFallback(pool);
                    pools.RemoveAt(i);
                }
            }
        }

        // Bounded local flood-fill from one of the pool's own cells. Either
        // outcome below is read as "connected to something large/open again":
        // reaching the map edge (vanilla rivers/coasts always touch the map
        // boundary), or the fill exceeding a cap without terminating (a
        // small, still-isolated pool terminates almost immediately; a body
        // reconnected to the channel network does not). See class header for
        // why this is a deliberate heuristic, not a full-map recompute.
        private bool IsReconnected(RM_StrandingPool pool)
        {
            if (pool.cells.Count == 0)
            {
                return false;
            }

            int cap = Mathf.Max(200, pool.cells.Count * 8);
            HashSet<IntVec3> visited = new HashSet<IntVec3> { pool.cells[0] };
            Queue<IntVec3> queue = new Queue<IntVec3>();
            queue.Enqueue(pool.cells[0]);

            while (queue.Count > 0)
            {
                if (visited.Count > cap)
                {
                    return true;
                }

                IntVec3 cur = queue.Dequeue();
                if (cur.x == 0 || cur.z == 0 || cur.x == map.Size.x - 1 || cur.z == map.Size.z - 1)
                {
                    return true;
                }

                for (int d = 0; d < GenAdj.CardinalDirections.Length; d++)
                {
                    IntVec3 nb = cur + GenAdj.CardinalDirections[d];
                    if (visited.Contains(nb) || !IsWaterCell(nb))
                    {
                        continue;
                    }
                    visited.Add(nb);
                    queue.Enqueue(nb);
                }
            }

            return false;
        }

        private void DecayPool(RM_StrandingPool pool, RM_StrandingPoolsExtension ext)
        {
            int elapsed = Find.TickManager.TicksGame - pool.birthTick;
            if (elapsed <= 0 || pool.decayTotalTicks <= 0 || pool.originalCellCount <= 0)
            {
                return;
            }

            float remainingFraction = Mathf.Clamp01(1f - (float)elapsed / pool.decayTotalTicks);
            int targetCount = Mathf.RoundToInt(pool.originalCellCount * remainingFraction);
            TerrainDef dry = ext?.dryTerrain;

            while (pool.cells.Count > targetCount && pool.cells.Count > 0)
            {
                IntVec3 cell = PickEdgeCellToRemove(pool);
                pool.cells.Remove(cell);

                if (dry != null)
                {
                    RM_GradientAxisRepaint.SetTerrainFloorSafe(map.terrainGrid, cell, dry);
                }
            }
        }

        // Prefers a cell adjacent to non-water (the pool's shoreline) so the
        // pool visibly shrinks from its edges inward rather than losing
        // random interior cells first — a simplification of real erosion,
        // documented as such in the class header.
        private IntVec3 PickEdgeCellToRemove(RM_StrandingPool pool)
        {
            for (int i = 0; i < pool.cells.Count; i++)
            {
                IntVec3 c = pool.cells[i];
                bool isEdge = false;
                for (int d = 0; d < GenAdj.CardinalDirections.Length; d++)
                {
                    if (!IsWaterCell(c + GenAdj.CardinalDirections[d]))
                    {
                        isEdge = true;
                        break;
                    }
                }
                if (isEdge)
                {
                    return c;
                }
            }
            return pool.cells[pool.cells.Count - 1];
        }

        private void PruneOccupants(RM_StrandingPool pool)
        {
            for (int i = pool.occupants.Count - 1; i >= 0; i--)
            {
                Pawn p = pool.occupants[i];
                if (p == null || p.Dead || p.Destroyed || !p.Spawned || p.Map != map)
                {
                    pool.occupants.RemoveAt(i);
                }
            }
        }

        // The spec's own explicitly-permitted fallback ("return-to-water job
        // may land as despawn at pool death first") — reached only when the
        // real job (RM_JobGiver_ReturnToWater) could not resolve an occupant
        // before its pool fully dried (no reachable channel cell, blocked
        // path, etc.), not the primary path. Loudly logged, never silent.
        private void DespawnStrandedFallback(RM_StrandingPool pool)
        {
            for (int i = 0; i < pool.occupants.Count; i++)
            {
                Pawn occ = pool.occupants[i];
                if (occ == null || !occ.Spawned)
                {
                    continue;
                }

                Log.Message("[RM EnvironmentalHazards] " + occ.LabelShort
                    + " despawned at stranding pool " + pool.id + "'s death (MIASMA_MECHANICS_1 M3's "
                    + "documented despawn-at-pool-death fallback — the return-to-water job did not get "
                    + "it to a reachable channel before the pool fully dried).");
                occ.DeSpawn(DestroyMode.Vanish);
            }
        }

        // ---- RM_JobGiver_ReturnToWater's own read surface --------------

        public bool TryGetPoolFor(Pawn pawn, out RM_StrandingPool pool)
        {
            for (int i = 0; i < pools.Count; i++)
            {
                if (pools[i].occupants.Contains(pawn))
                {
                    pool = pools[i];
                    return true;
                }
            }
            pool = null;
            return false;
        }

        // GenRadial.RadialCellsAround yields cells in strictly increasing
        // distance order from its center (confirmed against the live
        // decompile's own precomputed cell table), so the first match this
        // loop finds genuinely is the NEAREST reachable non-pool water cell,
        // not merely a random one within range.
        public bool TryFindNearestChannelCell(Pawn pawn, float radius, out IntVec3 result)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, radius, useCenter: false))
            {
                if (!IsWaterCell(c) || IsPartOfAnyPool(c))
                {
                    continue;
                }
                if (!map.reachability.CanReach(pawn.Position, c, PathEndMode.OnCell, TraverseParms.For(pawn)))
                {
                    continue;
                }
                result = c;
                return true;
            }
            result = IntVec3.Invalid;
            return false;
        }

        private bool IsPartOfAnyPool(IntVec3 c)
        {
            for (int i = 0; i < pools.Count; i++)
            {
                if (pools[i].cells.Contains(c))
                {
                    return true;
                }
            }
            return false;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref pools, "pools", LookMode.Deep);
            Scribe_Values.Look(ref nextPoolId, "nextPoolId", 1);
            Scribe_Values.Look(ref lastSeenRecedeTick, "lastSeenRecedeTick", -1);
            Scribe_Values.Look(ref updateCooldown, "updateCooldown", 0);

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                pools ??= new List<RM_StrandingPool>();
            }
        }
    }

    // One disconnected water region, Scribe-saved whole. A plain data class
    // (not a ThingComp/MapComponent) since it belongs to
    // RM_MapComponent_StrandingPools, never independently ticked.
    public class RM_StrandingPool : IExposable
    {
        public int id;
        public List<IntVec3> cells = new List<IntVec3>();
        public int originalCellCount;
        public int birthTick;
        public int decayTotalTicks;
        public List<Pawn> occupants = new List<Pawn>();

        public void ExposeData()
        {
            Scribe_Values.Look(ref id, "id", 0);
            Scribe_Collections.Look(ref cells, "cells", LookMode.Value);
            Scribe_Values.Look(ref originalCellCount, "originalCellCount", 0);
            Scribe_Values.Look(ref birthTick, "birthTick", 0);
            Scribe_Values.Look(ref decayTotalTicks, "decayTotalTicks", 0);
            Scribe_Collections.Look(ref occupants, "occupants", LookMode.Reference);

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                cells ??= new List<IntVec3>();
                occupants ??= new List<Pawn>();
            }
        }
    }
}
