using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.ColdStorage
{
    /// <summary>
    /// Per-map cell grid of the storage climate units standing on each cell. Rebuilt only when a unit spawns or
    /// despawns (RimFridge rebuilt a dictionary every tick); a unit's power state is read live from the comp, so a power
    /// change needs no rebuild. The getter prefix pays one array read.
    /// </summary>
    public class MapComponent_StorageClimate : MapComponent
    {
        private CompStorageClimate[] grid;
        private int count;

        public MapComponent_StorageClimate(Map map) : base(map)
        {
            StorageClimateRegistry.Add(this);
        }

        public int Count => count;

        public CompStorageClimate At(int cellIndex)
        {
            CompStorageClimate[] g = grid;
            return g == null || (uint)cellIndex >= (uint)g.Length ? null : g[cellIndex];
        }

        public void Register(CompStorageClimate unit)
        {
            if (grid == null)
            {
                grid = new CompStorageClimate[map.cellIndices.NumGridCells];
            }
            foreach (IntVec3 c in unit.parent.OccupiedRect())
            {
                if (c.InBounds(map))
                {
                    grid[map.cellIndices.CellToIndex(c)] = unit;
                }
            }
            count++;
            StorageClimateRegistry.UnitsChanged(1);
        }

        public void Deregister(CompStorageClimate unit, CellRect rect)
        {
            if (grid == null)
            {
                return;
            }
            foreach (IntVec3 c in rect)
            {
                if (c.InBounds(map))
                {
                    int i = map.cellIndices.CellToIndex(c);
                    if (grid[i] == unit)
                    {
                        grid[i] = null;
                    }
                }
            }
            count--;
            StorageClimateRegistry.UnitsChanged(-1);
        }

        public override void MapRemoved()
        {
            base.MapRemoved();
            StorageClimateRegistry.UnitsChanged(-count);
            count = 0;
            grid = null;
            StorageClimateRegistry.Remove(this);
        }
    }

    /// <summary>Clears the static registry when a new game is constructed (new or loaded), before its maps exist, and
    /// runs deferred seal transitions outside any ThingOwner tick loop.</summary>
    public class GameComponent_ColdStorage : GameComponent
    {
        public GameComponent_ColdStorage(Game game)
        {
            StorageClimateRegistry.Clear();
            CompSealed.ClearPending();
        }

        public override void GameComponentTick()
        {
            CompSealed.RunPending();
        }
    }

    public static class StorageClimateRegistry
    {
        private static readonly List<MapComponent_StorageClimate> maps = new List<MapComponent_StorageClimate>();

        /// <summary>Spawned units across every map. Zero makes every patch a single compare.</summary>
        public static int UnitCount { get; private set; }

        private static readonly System.Func<MapComponent_StorageClimate, MapComponent_StorageClimate, bool> SameMap = (a, b) => a.map == b.map;

        /// <summary>A loaded map constructs this component twice (Map.ConstructComponents, then the saved list); the
        /// newest is the one the map keeps and units register on, so it replaces the older entry for its map.</summary>
        internal static void Add(MapComponent_StorageClimate mc)
        {
            ColdStorageKernel.ReplaceOrAdd(maps, mc, SameMap);
        }

        internal static void Remove(MapComponent_StorageClimate mc)
        {
            maps.Remove(mc);
        }

        internal static void Clear()
        {
            maps.Clear();
            UnitCount = 0;
        }

        internal static void UnitsChanged(int delta)
        {
            UnitCount += delta;
            if (UnitCount < 0)
            {
                UnitCount = 0;
            }
        }

        public static MapComponent_StorageClimate For(Map map)
        {
            List<MapComponent_StorageClimate> list = maps;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i].map == map)
                {
                    return list[i];
                }
            }
            return null;
        }

        /// <summary>
        /// The unit holding <paramref name="thing"/>: the unit on its cell if it is a spawned item, or the unit whose
        /// container holds it (a casket or locker), walking up to three holders. Pawns and buildings are never held,
        /// so a colonist standing at a shelf is not chilled.
        /// </summary>
        public static CompStorageClimate UnitHolding(Thing thing)
        {
            if (UnitCount == 0 || thing.def.category != ThingCategory.Item)
            {
                return null;
            }
            if (thing.Spawned)
            {
                MapComponent_StorageClimate mc = For(thing.Map);
                return mc?.At(thing.Map.cellIndices.CellToIndex(thing.Position));
            }
            IThingHolder holder = thing.ParentHolder;
            for (int depth = 0; depth < 3 && holder != null; depth++)
            {
                ThingWithComps owner = holder as ThingWithComps ?? (holder as ThingComp)?.parent;
                if (owner != null)
                {
                    if (owner is Pawn)
                    {
                        return null;
                    }
                    CompStorageClimate unit = owner.GetComp<CompStorageClimate>();
                    if (unit != null)
                    {
                        return unit;
                    }
                }
                holder = holder.ParentHolder;
            }
            return null;
        }
    }
}
