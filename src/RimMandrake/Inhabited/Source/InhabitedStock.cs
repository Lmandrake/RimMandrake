using System.Collections.Generic;
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
    /// 🔴 THE CONTENTS NEVER REACH A MAP YET. Fill() runs once at cast
    /// instantiation and the things sit in this holder, scribed with the world
    /// object; no GenStep spawns them and no teardown collects them back. The
    /// design wants them on the ground and reachable -- Thing.IsForbidden returns
    /// false for any non-player faction, so a hungry cast would raid the colony's
    /// stockpile and the player could equally walk off with the place's food, and
    /// that theft is meant to be the audible click before a cast leaves. Building
    /// that is INHABITED_STOCK_ONTO_MAP_AND_FATE_1; until it lands, this class is
    /// a ledger.
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

        /// <summary>Fill from a def's table. Used once, when a place is created.</summary>
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
                Thing t = ThingMaker.MakeThing(entry.thingDef, GenStuff.DefaultStuffFor(entry.thingDef));
                t.stackCount = entry.count;
                if (!things.TryAdd(t))
                {
                    t.Destroy();
                }
            }
        }
    }
}
