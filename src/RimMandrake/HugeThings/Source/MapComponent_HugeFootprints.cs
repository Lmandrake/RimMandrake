using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// Every huge plant's footprint on one map (GPT review 2026-10-07: #1 #2 #5 #6 #8 #9 #14).
    ///
    ///  * Claims: each plant claims its desired cells in a map-wide ClaimLedger; a cell is blocked while ANY plant claims it,
    ///    by exactly one RM_HugeTrunkBlocker, whatever order plants registered or refreshed in (#8).
    ///  * Realizing: a newly claimed cell closes only when Planner allows it: never over a pawn or an item (nothing is
    ///    moved aside or destroyed, #2), never over a protected cell (buildings, blueprints, frames, their interaction
    ///    cells, door approaches, trees, other giants, #6), never if it would cut a cell off from open ground (trapped
    ///    pawns, new pockets) or cut a giant's root off from access (#1). A refused cell stays claimed and is retried.
    ///  * Freeing: a cell no plant claims any more opens at once.
    ///  * Reconciling: after load, every blocker on the map is indexed (not just those near a plant) and any blocker on an
    ///    unclaimed cell, any duplicate, and any blocker on the wrong map is removed (#5).
    ///  * Cost: only plants whose signature changed are refreshed, a few per tick, and pending cells are retried on a slow
    ///    cadence (#9). Settings changes mark every plant dirty instead of flushing synchronously.
    /// </summary>
    public class MapComponent_HugeFootprints : MapComponent
    {
        public const int PendingRetryInterval = 250;
        public const int RefreshesPerTick = 8;

        private readonly Dictionary<int, CompHugeFootprint> comps = new Dictionary<int, CompHugeFootprint>();
        private readonly SortedSet<int> dirty = new SortedSet<int>();
        private readonly ClaimLedger ledger = new ClaimLedger();
        private readonly Dictionary<long, Building_TrunkBlocker> realized = new Dictionary<long, Building_TrunkBlocker>();
        private readonly SortedSet<long> pending = new SortedSet<long>();
        private bool initialized;
        private bool mutating;

        public MapComponent_HugeFootprints(Map map) : base(map) { }

        public int Count => comps.Count;

        public int BlockerCount => realized.Count;

        public int PendingCount => pending.Count;

        public bool IsClaimed(IntVec3 c) => ledger.IsClaimed(Key(c));

        public bool Owns(Building_TrunkBlocker b) => realized.TryGetValue(Key(b.Position), out Building_TrunkBlocker r) && r == b;

        private static long Key(IntVec3 c) => RM_HugeFootprintKernel.Key(c.x, c.z);

        private static IntVec3 Cell(long k) => new IntVec3(RM_HugeFootprintKernel.KeyX(k), 0, RM_HugeFootprintKernel.KeyZ(k));

        public void Register(CompHugeFootprint c)
        {
            comps[c.OwnerId] = c;
            dirty.Add(c.OwnerId);
        }

        /// <summary>A plant left the map (cut, died, minified, destroyed): its claims go now, and every cell nobody else
        /// claims opens at once.</summary>
        public void Deregister(CompHugeFootprint c)
        {
            comps.Remove(c.OwnerId);
            dirty.Remove(c.OwnerId);
            List<long> freed = new List<long>();
            ledger.Remove(c.OwnerId, freed);
            Open(freed);
            RelabelOwners();
        }

        public void MarkDirty(CompHugeFootprint c)
        {
            if (comps.ContainsKey(c.OwnerId)) dirty.Add(c.OwnerId);
        }

        public void MarkAllDirty()
        {
            foreach (int id in comps.Keys) dirty.Add(id);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            Reconcile();
        }

        /// <summary>Index every blocker on the map, then rebuild claims from the plants and drop what nobody claims.</summary>
        public void Reconcile()
        {
            realized.Clear();
            pending.Clear();
            List<Thing> all = map.listerThings.ThingsOfDef(HugeThingsDefOf.RM_HugeTrunkBlocker);
            List<Building_TrunkBlocker> extra = new List<Building_TrunkBlocker>();
            for (int i = 0; i < all.Count; i++)
            {
                if (!(all[i] is Building_TrunkBlocker b) || !b.Spawned) continue;
                long k = Key(b.Position);
                if (realized.ContainsKey(k)) extra.Add(b);
                else realized[k] = b;
            }
            foreach (Building_TrunkBlocker b in extra) Despawn(b);
            List<int> ids = new List<int>(comps.Keys);
            ids.Sort();
            foreach (int id in ids) Take(comps[id]);
            dirty.Clear();
            List<long> stray = new List<long>();
            foreach (long k in realized.Keys) if (!ledger.IsClaimed(k)) stray.Add(k);
            Open(stray);
            foreach (long k in ledger.Claimed) if (!realized.ContainsKey(k)) pending.Add(k);
            initialized = true;
            RealizePending();
            RelabelOwners();
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (!initialized) return;
            int n = 0;
            while (dirty.Count > 0 && n < RefreshesPerTick)
            {
                int id = dirty.Min;
                dirty.Remove(id);
                if (comps.TryGetValue(id, out CompHugeFootprint c))
                {
                    try
                    {
                        Take(c);
                    }
                    catch (System.Exception e)
                    {
                        Log.ErrorOnce("[RimMandrake.HugeThings] footprint refresh failed for " + c.parent + ": " + e, id ^ 0x4875);
                    }
                }
                n++;
            }
            if (n > 0 || (pending.Count > 0 && (Find.TickManager.TicksGame + map.uniqueID) % PendingRetryInterval == 0))
            {
                RealizePending();
                RelabelOwners();
            }
        }

        /// <summary>Take a plant's current desired cells into the ledger; free what it no longer wants.</summary>
        private void Take(CompHugeFootprint c)
        {
            List<long> claimed = new List<long>(), freed = new List<long>();
            List<long> want = c.DesiredKeys();
            List<long> keep = new List<long>(want.Count);
            foreach (long k in want) if (Cell(k).InBounds(map)) keep.Add(k);
            ledger.Set(c.OwnerId, keep, claimed, freed);
            Open(freed);
            foreach (long k in claimed) if (!realized.ContainsKey(k)) pending.Add(k);
            c.MarkTaken();
        }

        private void Open(List<long> cells)
        {
            foreach (long k in cells)
            {
                pending.Remove(k);
                if (realized.TryGetValue(k, out Building_TrunkBlocker b))
                {
                    realized.Remove(k);
                    Despawn(b);
                }
            }
        }

        private void Despawn(Building_TrunkBlocker b)
        {
            if (b == null || b.Destroyed) return;
            mutating = true;
            try
            {
                b.Destroy(DestroyMode.Vanish);
            }
            finally
            {
                mutating = false;
            }
        }

        /// <summary>Plan and spawn pending cells, plant by plant (lowest id first), each against its fixed window.</summary>
        private void RealizePending()
        {
            if (pending.Count == 0) return;
            List<long> roots = new List<long>();
            foreach (CompHugeFootprint c in comps.Values) roots.Add(Key(c.parent.Position));
            List<int> ids = new List<int>(comps.Keys);
            ids.Sort();
            foreach (int id in ids)
            {
                CompHugeFootprint c = comps[id];
                List<long> mine = new List<long>();
                foreach (long k in ledger.CellsOf(id)) if (pending.Contains(k)) mine.Add(k);
                if (mine.Count == 0) continue;
                CellBox window = Planner.Window(c.MaxKeys(), Key(c.parent.Position));
                Dictionary<long, CellFlags> flags = Flags(window);
                List<long> ok = Planner.Plan(mine, roots, k => flags.TryGetValue(k, out CellFlags f) ? f : CellFlags.Passable, window);
                foreach (long k in ok)
                {
                    if (Spawn(k)) flags[k] = CellFlags.None;
                }
            }
        }

        private bool Spawn(long k)
        {
            IntVec3 c = Cell(k);
            if (!c.InBounds(map) || realized.ContainsKey(k)) return false;
            Building_TrunkBlocker b = (Building_TrunkBlocker)ThingMaker.MakeThing(HugeThingsDefOf.RM_HugeTrunkBlocker);
            mutating = true;
            try
            {
                // Planner refused every cell holding an item or pawn, so Vanish wipes only small plants and filth.
                GenSpawn.Spawn(b, c, map, WipeMode.Vanish);
            }
            catch (System.Exception e)
            {
                Log.ErrorOnce("[RimMandrake.HugeThings] blocker spawn failed at " + c + ": " + e, c.GetHashCode() ^ 0x5157);
            }
            finally
            {
                mutating = false;
            }
            if (b.Spawned)
            {
                realized[k] = b;   // recorded even after an exception mid-spawn, so it can never become a ghost
                pending.Remove(k);
                return true;
            }
            return false;
        }

        /// <summary>Planner input for every cell of a window.</summary>
        private Dictionary<long, CellFlags> Flags(CellBox w)
        {
            Dictionary<long, CellFlags> f = new Dictionary<long, CellFlags>();
            HashSet<IntVec3> protectedCells = new HashSet<IntVec3>();
            CellRect scan = CellRect.FromLimits(w.MinX - 3, w.MinZ - 3, w.MaxX + 3, w.MaxZ + 3).ClipInsideMap(map);
            foreach (IntVec3 c in scan)
            {
                List<Thing> list = c.GetThingList(map);
                for (int i = 0; i < list.Count; i++)
                {
                    Thing t = list[i];
                    if (t is Building_TrunkBlocker) continue;
                    bool building = t.def.category == ThingCategory.Building || t.def.IsBlueprint || t.def.IsFrame;
                    if (building && t.def.hasInteractionCell) protectedCells.Add(t.InteractionCell);
                    if (t is Building_Door)
                    {
                        foreach (IntVec3 d in GenAdj.CardinalDirections) protectedCells.Add(c + d);
                    }
                }
            }
            for (int z = w.MinZ; z <= w.MaxZ; z++)
            {
                for (int x = w.MinX; x <= w.MaxX; x++)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    long k = Key(c);
                    if (!c.InBounds(map))
                    {
                        f[k] = CellFlags.None;
                        continue;
                    }
                    CellFlags fl = c.Walkable(map) ? CellFlags.Passable : CellFlags.None;
                    if (protectedCells.Contains(c)) fl |= CellFlags.Protected;
                    List<Thing> list = c.GetThingList(map);
                    for (int i = 0; i < list.Count; i++)
                    {
                        Thing t = list[i];
                        if (t is Pawn) fl |= CellFlags.Pawn;
                        else if (t.def.category == ThingCategory.Item) fl |= CellFlags.Item;
                        else if (t.def.category == ThingCategory.Building || t.def.IsBlueprint || t.def.IsFrame || !t.def.destroyable)
                            fl |= CellFlags.Protected;
                        else if (t is Plant pl && (pl.def.plant.IsTree || pl.def.HasModExtension<RM_HugePlantExtension>()))
                            fl |= CellFlags.Protected;
                    }
                    f[k] = fl;
                }
            }
            return f;
        }

        /// <summary>Each blocker answers to its cell's primary owner (lowest thing id among its claimants).</summary>
        private void RelabelOwners()
        {
            foreach (KeyValuePair<long, Building_TrunkBlocker> kv in realized)
            {
                int id = ledger.PrimaryOwner(kv.Key);
                kv.Value.owner = id >= 0 && comps.TryGetValue(id, out CompHugeFootprint c) ? c.Plant : null;
            }
        }

        /// <summary>A blocker vanished by something other than this component (gravship clearing, roof collapse, dev mode):
        /// forget it; its cell stays claimed and is re-planned.</summary>
        public void Notify_BlockerGone(Building_TrunkBlocker b)
        {
            if (mutating) return;
            long k = Key(b.Position);
            if (realized.TryGetValue(k, out Building_TrunkBlocker r) && r == b)
            {
                realized.Remove(k);
                if (ledger.IsClaimed(k)) pending.Add(k);
            }
        }

        /// <summary>The plants whose blockers or roots stand on any of these cells (gravship landing policy).</summary>
        public List<Plant> OwnersAt(IEnumerable<IntVec3> cells)
        {
            HashSet<Plant> outPlants = new HashSet<Plant>();
            HashSet<long> ks = new HashSet<long>();
            foreach (IntVec3 c in cells) ks.Add(Key(c));
            foreach (CompHugeFootprint c in comps.Values)
            {
                if (ks.Contains(Key(c.parent.Position))) { outPlants.Add(c.Plant); continue; }
                foreach (long k in ledger.CellsOf(c.OwnerId))
                {
                    if (ks.Contains(k) && realized.ContainsKey(k)) { outPlants.Add(c.Plant); break; }
                }
            }
            List<Plant> list = new List<Plant>(outPlants);
            list.Sort((a, b) => a.thingIDNumber.CompareTo(b.thingIDNumber));
            return list;
        }

        /// <summary>Called when Mod Settings change: every plant re-takes its footprint over the next ticks.</summary>
        public static void RefreshAllMaps()
        {
            if (Current.Game == null) return;
            foreach (Map m in Find.Maps)
            {
                m.GetComponent<MapComponent_HugeFootprints>()?.MarkAllDirty();
            }
        }
    }
}
