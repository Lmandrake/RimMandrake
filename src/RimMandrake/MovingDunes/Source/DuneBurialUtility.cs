using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// The burial API — MOVING_DUNES_DESIGN.md §3. <see cref="BuryThingsAt"/> is the one
    /// call the design promises other mods: WreckedMachines' wrecks and Antiquities'
    /// digs seed caches at mapgen with it, and get the wind-shift reveal for free.
    ///
    /// It is deliberately callable on a map that is NOT a dune field: a mapgen-seeded
    /// cache on an ordinary map still holds its contents and still reveals when the sand
    /// over it drops. Only the automatic burial sweep is dune-field-only.
    /// </summary>
    public static class DuneBurialUtility
    {
        /// <summary>
        /// Buries things at a cell, merging into the cache already there if one exists.
        ///
        /// </summary>
        /// <param name="cell">Where to bury. Must be in bounds.</param>
        /// <param name="map">The map. Required.</param>
        /// <param name="things">What to bury. Spawned things are despawned into the
        /// cache; already-held things are transferred. Nulls and destroyed things are
        /// skipped.</param>
        /// <param name="depth">Sand depth to force on the cell, or a negative number to
        /// leave the grid alone. A mapgen caller normally passes the material's
        /// <c>burialDepth</c> or higher so the cache does not reveal on its first tick.</param>
        /// <returns>The cache holding the things, or null if nothing could be buried.</returns>
        public static Thing_BuriedCache BuryThingsAt(IntVec3 cell, Map map,
                                                     IEnumerable<Thing> things,
                                                     float depth = -1f)
        {
            if (map == null || !cell.InBounds(map) || things == null)
            {
                return null;
            }

            // Materialise first: the caller may hand us a lazy query over the very cell
            // list we are about to mutate by despawning things out of it.
            List<Thing> toBury = new List<Thing>();
            foreach (Thing t in things)
            {
                if (t != null && !t.Destroyed && !(t is Thing_BuriedCache))
                {
                    toBury.Add(t);
                }
            }
            if (toBury.Count == 0)
            {
                return null;
            }

            Thing_BuriedCache cache = CacheAt(cell, map);
            if (cache == null)
            {
                Thing made = ThingMaker.MakeThing(MovingDunesDefOf.RM_Dunes_BuriedCache);
                cache = made as Thing_BuriedCache;
                if (cache == null)
                {
                    Log.ErrorOnce(MovingDunesMod.LogPrefix + "RM_Dunes_BuriedCache's thingClass is "
                                  + "not Thing_BuriedCache — nothing can ever be buried. Check the "
                                  + "ThingDef.", 0x5D07E4);
                    if (made != null)
                    {
                        made.Destroy();
                    }
                    return null;
                }
                cache.buriedAtTick = Find.TickManager.TicksGame;
                GenSpawn.Spawn(cache, cell, map);
            }

            int accepted = 0;
            for (int i = 0; i < toBury.Count; i++)
            {
                if (cache.Accept(toBury[i]))
                {
                    accepted++;
                }
            }

            if (accepted == 0 && cache.ContentsCount == 0)
            {
                cache.Destroy();
                return null;
            }

            if (depth >= 0f)
            {
                map.sandGrid.SetDepth(cell, depth);
            }
            return cache;
        }

        /// <summary>The cache standing on this cell, or null.</summary>
        public static Thing_BuriedCache CacheAt(IntVec3 cell, Map map)
        {
            if (map == null || !cell.InBounds(map))
            {
                return null;
            }
            List<Thing> list = map.thingGrid.ThingsListAtFast(cell);
            for (int i = 0; i < list.Count; i++)
            {
                Thing_BuriedCache cache = list[i] as Thing_BuriedCache;
                if (cache != null && !cache.Destroyed)
                {
                    return cache;
                }
            }
            return null;
        }

        /// <summary>
        /// RULED (MOVING_DUNES_DESIGN.md §3): wild and unclaimed items only. Anything in
        /// a stockpile, inside the home area, or forbidden on purpose by the player is
        /// exempt — the dune does not eat the colony's stores, it eats the desert's
        /// litter. That is the whole rule, and it is what makes the mechanic feel like
        /// weather rather than theft.
        /// </summary>
        public static bool IsBurialCandidate(Thing t, Map map, float minMarketValue)
        {
            if (t == null || t.Destroyed || !t.Spawned)
            {
                return false;
            }
            if (t is Thing_BuriedCache)
            {
                return false;
            }
            if (t.def == null || t.def.category != ThingCategory.Item || !t.def.EverHaulable)
            {
                return false;
            }
            if (t.def.destroyOnDrop)
            {
                return false;
            }
            if (map.areaManager.Home[t.Position])
            {
                return false;
            }
            if (t.IsInAnyStorage())
            {
                return false;
            }
            if (t.IsForbidden(Faction.OfPlayer))
            {
                return false;
            }
            if (map.reservationManager.IsReservedByAnyoneOf(t, Faction.OfPlayer))
            {
                return false;
            }
            if (minMarketValue > 0f && t.MarketValue * t.stackCount < minMarketValue)
            {
                return false;
            }
            return true;
        }
    }
}
