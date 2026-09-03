using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// The larder and the trade goods, held by a place.
    ///
    /// A separate holder rather than a second ThingOwner on the world object,
    /// because IThingHolder.GetDirectlyHeldThings returns exactly one owner. This
    /// is the shape Caravan uses for its own sub-trackers (pather, needs, beds,
    /// trader): a small IExposable+IThingHolder that takes the parent and is
    /// deep-scribed by it.
    ///
    /// THE HOLDER IS THE OFF-MAP HALF OF ONE CYCLE. <see cref="Fill"/> stocks it
    /// once at cast instantiation; <see cref="DumpOnto"/> puts every held thing on
    /// the ground when a map generates, and <see cref="CollectFrom"/> takes back
    /// whatever survived the visit just before the map is torn down. What the
    /// player ate, burned or carried away simply is not there to collect, so the
    /// holder's contents ARE the place's remaining goods with no bookkeeping of
    /// losses anywhere -- the same "the container is the record" rule the roster
    /// follows.
    ///
    /// ⚠️ WHAT COUNTS AS OURS ON THE WAY BACK IS DELIBERATELY GENEROUS. See
    /// <see cref="IsPlaceGoods"/>: an item is the place's if it is one of the
    /// stacks we dropped OR it is simply lying in the place's stock area. A
    /// player who leaves goods at the granary has given them away, and since the
    /// map is destroyed on departure regardless, absorbing them loses nothing
    /// that would otherwise survive.
    /// </summary>
    public class InhabitedStock : IExposable, IThingHolder
    {
        private ThingOwner<Thing> things;
        private IThingHolder parent;

        public InhabitedStock()
        {
            things = new ThingOwner<Thing>(this, oneStackOnly: false, LookMode.Deep);
        }

        public InhabitedStock(IThingHolder parent)
            : this()
        {
            this.parent = parent;
        }

        public IThingHolder ParentHolder => parent;

        public int Count => things?.Count ?? 0;

        /// <summary>Total stackCount held, which is what "half the granary is
        /// gone" has to be measured against -- three stacks of one are not the
        /// same larder as three stacks of two hundred.</summary>
        public int TotalStackCount
        {
            get
            {
                if (things == null)
                {
                    return 0;
                }
                int n = 0;
                List<Thing> held = things.InnerListForReading;
                for (int i = 0; i < held.Count; i++)
                {
                    if (held[i] != null)
                    {
                        n += held[i].stackCount;
                    }
                }
                return n;
            }
        }

        public ThingOwner GetDirectlyHeldThings()
        {
            return things;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public void ExposeData()
        {
            Scribe_Deep.Look(ref things, "things", this);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && things == null)
            {
                things = new ThingOwner<Thing>(this, oneStackOnly: false, LookMode.Deep);
            }
        }

        /// <summary>
        /// Fill from a def's table. Used once, when a place is created.
        ///
        /// ⚠️ SPLIT AT THE STACK LIMIT, not written as one oversized Thing. This
        /// used to set stackCount straight from the authored count, which was
        /// invisible while the holder was a ledger and stops being invisible the
        /// moment DumpOnto puts it on a map: a 200-deep stack of steel is four
        /// times the def's own limit of 75, and everything downstream -- the drop,
        /// the hauling, the stack merge on the way back -- assumes the limit
        /// holds. An author asking for 200 steel gets three stacks and a
        /// remainder, which is what a granary looks like anyway.
        /// </summary>
        public void Fill(List<ThingDefCountClass> table)
        {
            if (table.NullOrEmpty())
            {
                return;
            }
            for (int i = 0; i < table.Count; i++)
            {
                ThingDefCountClass entry = table[i];
                if (entry?.thingDef == null || entry.count <= 0)
                {
                    continue;
                }
                int limit = System.Math.Max(1, entry.thingDef.stackLimit);
                int remaining = entry.count;
                while (remaining > 0)
                {
                    Thing t = ThingMaker.MakeThing(entry.thingDef, GenStuff.DefaultStuffFor(entry.thingDef));
                    t.stackCount = System.Math.Min(limit, remaining);
                    remaining -= t.stackCount;
                    if (!things.TryAdd(t))
                    {
                        t.Destroy();
                        break;
                    }
                }
            }
        }

        // ------------------------------------------------------------------
        // On the ground, and back off it. INHABITED_STOCK_ONTO_MAP_AND_FATE_1.
        // ------------------------------------------------------------------

        /// <summary>
        /// Put every held thing on the map around <paramref name="anchor"/> and
        /// empty the holder. Returns the total stackCount that reached the ground.
        ///
        /// ⭐ THE LEDGER IS THE RESULTING STACK, NOT THE ONE WE HANDED OVER.
        /// GenDrop.TryDropSpawn merges into an existing stack where it can, which
        /// destroys the thing we passed in and returns the survivor -- recording
        /// the input's thingIDNumber would therefore have written down an ID that
        /// no longer exists on any map, and the recall would find nothing.
        ///
        /// ⚠️ The ledger is a FLOOR on what is ours, never a census. A stack the
        /// player splits, or the cast eats half of, gets a new thingIDNumber that
        /// was never written here; that is what the stock AREA in
        /// <see cref="IsPlaceGoods"/> is for.
        /// </summary>
        public int DumpOnto(Map map, IntVec3 anchor, List<int> ledger)
        {
            if (map == null || things == null || things.Count == 0 || !anchor.IsValid)
            {
                return 0;
            }

            int placed = 0;
            // Copy first: TryDrop removes from the owner we are reading.
            List<Thing> held = things.InnerListForReading.ToList();
            for (int i = 0; i < held.Count; i++)
            {
                Thing t = held[i];
                if (t == null)
                {
                    continue;
                }
                int wanted = t.stackCount;
                if (!things.TryDrop(t, anchor, map, ThingPlaceMode.Near, out Thing landed))
                {
                    Log.Warning("[RimMandrake.Inhabited] could not place " + t.LabelCap
                                + " on the map; it stays in the holder.");
                    continue;
                }
                placed += wanted;
                if (landed != null && ledger != null && !ledger.Contains(landed.thingIDNumber))
                {
                    ledger.Add(landed.thingIDNumber);
                }
            }
            return placed;
        }

        /// <summary>
        /// Take back everything of ours still on the map. Returns the total
        /// stackCount recovered. Must run while the map still exists -- see
        /// Patch_MapRemoval for the exact instant and why it is that one.
        /// </summary>
        public int CollectFrom(Map map, CellRect area, List<int> ledger)
        {
            if (map == null || things == null)
            {
                return 0;
            }

            List<Thing> ours = new List<Thing>();
            List<Thing> all = map.listerThings.AllThings;
            for (int i = 0; i < all.Count; i++)
            {
                if (IsPlaceGoods(all[i], area, ledger))
                {
                    ours.Add(all[i]);
                }
            }

            int taken = 0;
            for (int i = 0; i < ours.Count; i++)
            {
                Thing t = ours[i];
                int n = t.stackCount;
                t.DeSpawn();
                if (things.TryAdd(t, canMergeWithExistingStacks: true))
                {
                    taken += n;
                    continue;
                }
                Log.Warning("[RimMandrake.Inhabited] the stock holder refused " + t.LabelCap
                            + " at teardown; it is lost with the map.");
            }
            ledger?.Clear();
            return taken;
        }

        /// <summary>Total stackCount of the place's goods lying on the map right
        /// now. The same predicate the recall uses, so "how much is left" and
        /// "what comes back" can never disagree.</summary>
        public static int CountOnMap(Map map, CellRect area, List<int> ledger)
        {
            if (map == null)
            {
                return 0;
            }
            int n = 0;
            List<Thing> all = map.listerThings.AllThings;
            for (int i = 0; i < all.Count; i++)
            {
                if (IsPlaceGoods(all[i], area, ledger))
                {
                    n += all[i].stackCount;
                }
            }
            return n;
        }

        /// <summary>
        /// Is this spawned thing the place's to take back?
        ///
        /// ⛔ CORPSES ARE EXCLUDED AND THAT IS LOAD-BEARING, not squeamishness. A
        /// Corpse is ThingCategory.Item and would pass every other test here, and
        /// it HOLDS ITS PAWN -- absorbing one would deep-scribe a dead resident
        /// into the world object forever, which is precisely the record
        /// WorldObject_Inhabited's "the absence is the memory" rule says must not
        /// exist.
        ///
        /// Player-faction items are excluded too: a minified building or an
        /// unfinished thing the colony owns is not larder.
        /// </summary>
        public static bool IsPlaceGoods(Thing t, CellRect area, List<int> ledger)
        {
            if (t == null || !t.Spawned || t.Destroyed)
            {
                return false;
            }
            if (t.def?.category != ThingCategory.Item)
            {
                return false;
            }
            if (t is Corpse)
            {
                return false;
            }
            if (t.Faction != null && t.Faction == Faction.OfPlayer)
            {
                return false;
            }
            if (ledger != null && ledger.Contains(t.thingIDNumber))
            {
                return true;
            }
            return area.Area > 0 && area.Contains(t.Position);
        }
    }
}
