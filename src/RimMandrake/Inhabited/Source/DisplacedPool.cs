using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// The people who lost their place. They are not destroyed; they wait here,
    /// and any cast being instantiated draws from this pool BEFORE generating
    /// anyone new. That one ordering rule is the entire recurring-character
    /// effect, and it costs a list.
    ///
    /// NOTHING IN THIS CLASS TICKS, deliberately. Redistribution happens at cast
    /// instantiation -- when a map generates -- never on a background tick, which
    /// is what keeps "frozen until visited" true. There is no GameComponentTick
    /// here and there must not be one.
    ///
    /// THERE IS NO MORALITY SYSTEM HERE AND THERE MUST NEVER BE ONE. No karma, no
    /// reputation number, no counter of who was wronged, no popup. The consequence
    /// is delivered entirely by RimWorld's existing name, backstory and memory
    /// systems, plus the player recognising a face. The moment this acquires a
    /// guilt statistic it becomes a mechanic instead of a memory.
    ///
    /// STORAGE NOTE. The queue item specified
    /// `Dictionary&lt;Faction, ThingOwner&lt;Pawn&gt;&gt; pools`. That container cannot be
    /// scribed safely: a ThingOwner must be constructed with its IThingHolder
    /// owner, and Scribe_Collections deep-look has no way to pass one to a value
    /// it is reconstructing, so the owners come back null and every pool empties
    /// on load. One ThingOwner plus a faction QUERY gives the same API -- Absorb
    /// and Draw below take a Faction exactly as specified -- and survives a round
    /// trip. Pawn.Faction is already the key; it did not need duplicating into the
    /// container shape.
    /// </summary>
    public class DisplacedPool : GameComponent, IThingHolder
    {
        private ThingOwner<Pawn> placeless;

        /// <summary>
        /// Why each is placeless, and where from, and in what order, keyed by thingIDNumber rather
        /// than by pawn reference. Plain value dictionaries need no cross-reference
        /// resolution, so they cannot half-load behind a pawn that did. The bookkeeping
        /// lives in InhabitedCustodyKernel.cs (DisplacementBook), which the offline fuzz drives.
        /// </summary>
        private DisplacementBook book = new DisplacementBook();

        public DisplacedPool(Game game)
        {
            placeless = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
        }

        public static DisplacedPool Current => Verse.Current.Game?.GetComponent<DisplacedPool>();

        public int Count => placeless?.Count ?? 0;

        public IThingHolder ParentHolder => null;

        public ThingOwner GetDirectlyHeldThings()
        {
            return placeless;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref placeless, "placeless", this);
            Scribe_Collections.Look(ref book.reasons, "reasons", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref book.origins, "origins", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref book.displacedAt, "displacedAt", LookMode.Value, LookMode.Value);
            Scribe_Values.Look(ref book.nextOrder, "nextOrder", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (placeless == null)
                {
                    placeless = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
                }
                book.EnsureNotNull();
            }
        }

        /// <summary>
        /// Take somebody in. THE DEAD NEVER ENTER THE POOL -- they are eaten and
        /// forgotten, and this method is where that is enforced.
        /// </summary>
        public bool Absorb(Pawn pawn, Faction faction, DisplacedReason reason = DisplacedReason.Fled,
            string origin = null)
        {
            if (pawn == null)
            {
                return false;
            }
            return InhabitedCustody.Absorb(book, pawn.thingIDNumber, pawn.Dead || pawn.Destroyed,
                () =>
                {
                    if (pawn.Spawned)
                    {
                        pawn.DeSpawnOrDeselect();
                    }
                    if (pawn.IsWorldPawn())
                    {
                        // A pawn cannot be both deep-held here and owned by WorldPawns: it
                        // would be saved twice, and WorldPawnGC would still be free to
                        // discard the copy it can see.
                        Find.WorldPawns.RemovePawn(pawn);
                    }
                    if (faction != null && pawn.Faction != faction)
                    {
                        pawn.SetFaction(faction);
                    }
                },
                () => placeless.TryAdd(pawn, canMergeWithExistingStacks: false),
                reason, origin);
        }

        /// <summary>
        /// Everyone eligible for a draw, longest-waiting first. The filter differs
        /// between the two draw routes below; the ordering never does.
        /// </summary>
        private List<Pawn> Candidates(Func<Pawn, bool> filter)
        {
            if (placeless == null || placeless.Count == 0)
            {
                return new List<Pawn>();
            }
            return InhabitedCustody.Order(book,
                placeless.InnerListForReading.Where(p => p != null && !p.Dead && filter(p)),
                p => p.thingIDNumber);
        }

        /// <summary>
        /// Hand one person to a destination, and forget them here ONLY once the
        /// destination has taken them.
        ///
        /// ⛔ THIS IS WHY THERE IS NO PLAIN `Draw` RETURNING A LIST. A method that
        /// removed a pawn from the pool and handed it back left an instant in which
        /// that person belonged nowhere -- not in the pool, not in a roster, not
        /// spawned, not a world pawn -- and anything that went wrong in the caller
        /// during that instant deleted them permanently, because nothing that saves
        /// the game could see them. Every draw carries its own destination and puts
        /// the pawn back, with their reason and their place in the queue intact, on
        /// any refusal or exception.
        /// </summary>
        private bool TryHandOver(Pawn p, Func<Pawn, bool> destination)
        {
            return InhabitedCustody.HandOver(book, p, p?.thingIDNumber ?? 0,
                x => placeless != null && placeless.Remove(x), PutBack, destination, LogLost);
        }

        /// <summary>
        /// Undo a hand-over the destination refused. The metadata is cleared only
        /// on success, so this restores the reason, the origin and the place
        /// in the queue exactly as they were.
        /// </summary>
        private bool PutBack(Pawn p)
        {
            return placeless.TryAdd(p, canMergeWithExistingStacks: false);
        }

        private static void LogLost(Pawn p)
        {
            Log.Error("[RimMandrake.Inhabited] could not return " + p.ToStringSafe()
                      + " to the displaced pool; they are now held nowhere and will not be saved.");
        }

        /// <summary>
        /// Move up to <paramref name="count"/> of a faction's placeless straight
        /// into <paramref name="destination"/>, longest-waiting first, and report
        /// how many arrived. Anyone the destination refuses simply stays in the
        /// pool. Optionally appends the people who moved to
        /// <paramref name="arrived"/>, for a caller that wants to name them.
        ///
        /// This is the ONLY way anyone leaves the pool for a roster, and it runs at
        /// cast instantiation, never on a tick.
        /// </summary>
        public int DrawInto(Faction faction, int count, ThingOwner<Pawn> destination,
            List<Pawn> arrived = null)
        {
            if (count <= 0 || destination == null)
            {
                return 0;
            }
            return InhabitedCustody.DrawInto(book, Candidates(p => p.Faction == faction), count, p => p.thingIDNumber,
                x => placeless.Remove(x), PutBack, p => destination.TryAdd(p, canMergeWithExistingStacks: false),
                LogLost, arrived);
        }

        /// <summary>
        /// Hand ONE of the placeless, REGARDLESS of faction, to a caller that
        /// registers them somewhere this class cannot reach. Returns the person, or
        /// null if nobody was waiting or the caller refused them -- in which case
        /// they are still in the pool, unchanged.
        ///
        /// For the beggars at the player's own gate. Beggars do not belong to an
        /// existing faction -- the quest builds a hidden temporary one -- so the
        /// faction-scoped draw above cannot serve them, and the point of the
        /// feature is precisely that the people at the gate came from anywhere the
        /// player has been.
        /// </summary>
        public Pawn DrawAnyInto(Func<Pawn, bool> destination)
        {
            if (destination == null)
            {
                return null;
            }
            return InhabitedCustody.DrawAny(book, Candidates(p => p.RaceProps != null && p.RaceProps.Humanlike),
                p => p.thingIDNumber, x => placeless.Remove(x), PutBack, destination, LogLost);
        }

        /// <summary>How many of a faction are waiting. Used to size a draw.</summary>
        public int CountFor(Faction faction)
        {
            if (placeless == null)
            {
                return 0;
            }
            return placeless.InnerListForReading.Count(p => p != null && !p.Dead && p.Faction == faction);
        }

        public DisplacedReason ReasonFor(Pawn pawn)
        {
            return book.ReasonFor(pawn.thingIDNumber);
        }

        public string OriginFor(Pawn pawn)
        {
            return book.OriginFor(pawn.thingIDNumber);
        }

        /// <summary>Everyone waiting, for debug listing only.</summary>
        public IEnumerable<Pawn> AllPlaceless =>
            placeless?.InnerListForReading ?? (IEnumerable<Pawn>)new List<Pawn>();
    }
}
