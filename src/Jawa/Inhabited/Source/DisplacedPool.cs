using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace Inhabited
{
    /// <summary>
    /// Why someone is placeless. Drift between factions is possible but rare and
    /// must carry a reason -- it is never random.
    /// </summary>
    public enum DisplacedReason
    {
        /// <summary>The player menaced them off their own site. Stays in faction.</summary>
        Fled,
        /// <summary>The larder emptied and they went. Stays in faction.</summary>
        StarvedOut,
        /// <summary>May change faction: to the new owner.</summary>
        Enslaved,
        /// <summary>May change faction: to factionless, or whoever shelters them.</summary>
        Escaped,
        /// <summary>May change faction: absorbed by the victor.</summary>
        LostABattle,
        /// <summary>May change faction: to the buyer's cast. They stay there.</summary>
        SoldByPlayer
    }

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
        /// Why each is placeless, and where from, keyed by thingIDNumber rather
        /// than by pawn reference. Plain value dictionaries need no cross-reference
        /// resolution, so they cannot half-load behind a pawn that did.
        /// </summary>
        private Dictionary<int, DisplacedReason> reasons = new Dictionary<int, DisplacedReason>();

        private Dictionary<int, string> origins = new Dictionary<int, string>();

        /// <summary>Displacement order, so a Draw can take the longest-waiting first.</summary>
        private Dictionary<int, int> displacedAt = new Dictionary<int, int>();

        private int nextOrder;

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
            Scribe_Collections.Look(ref reasons, "reasons", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref origins, "origins", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref displacedAt, "displacedAt", LookMode.Value, LookMode.Value);
            Scribe_Values.Look(ref nextOrder, "nextOrder", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (placeless == null)
                {
                    placeless = new ThingOwner<Pawn>(this, oneStackOnly: false, LookMode.Deep);
                }
                if (reasons == null)
                {
                    reasons = new Dictionary<int, DisplacedReason>();
                }
                if (origins == null)
                {
                    origins = new Dictionary<int, string>();
                }
                if (displacedAt == null)
                {
                    displacedAt = new Dictionary<int, int>();
                }
            }
        }

        /// <summary>
        /// Take somebody in. THE DEAD NEVER ENTER THE POOL -- they are eaten and
        /// forgotten, and this method is where that is enforced.
        /// </summary>
        public bool Absorb(Pawn pawn, Faction faction, DisplacedReason reason = DisplacedReason.Fled,
            string origin = null)
        {
            if (pawn == null || pawn.Dead || pawn.Destroyed)
            {
                return false;
            }
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
            if (!placeless.TryAdd(pawn, canMergeWithExistingStacks: false))
            {
                return false;
            }
            reasons[pawn.thingIDNumber] = reason;
            origins[pawn.thingIDNumber] = origin;
            displacedAt[pawn.thingIDNumber] = nextOrder++;
            return true;
        }

        /// <summary>
        /// Remove and return up to <paramref name="count"/> of a faction's
        /// placeless, longest-waiting first. This is the ONLY way anyone leaves the
        /// pool, and it runs at cast instantiation, never on a tick.
        /// </summary>
        public List<Pawn> Draw(Faction faction, int count)
        {
            List<Pawn> drawn = new List<Pawn>();
            if (count <= 0 || placeless == null || placeless.Count == 0)
            {
                return drawn;
            }
            List<Pawn> candidates = placeless.InnerListForReading
                .Where(p => p != null && !p.Dead && p.Faction == faction)
                .OrderBy(p => displacedAt.TryGetValue(p.thingIDNumber, out int o) ? o : int.MaxValue)
                .ToList();
            for (int i = 0; i < candidates.Count && drawn.Count < count; i++)
            {
                Pawn p = candidates[i];
                if (!placeless.Remove(p))
                {
                    continue;
                }
                reasons.Remove(p.thingIDNumber);
                origins.Remove(p.thingIDNumber);
                displacedAt.Remove(p.thingIDNumber);
                drawn.Add(p);
            }
            return drawn;
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
            return reasons.TryGetValue(pawn.thingIDNumber, out DisplacedReason r) ? r : DisplacedReason.Fled;
        }

        public string OriginFor(Pawn pawn)
        {
            return origins.TryGetValue(pawn.thingIDNumber, out string o) ? o : null;
        }

        /// <summary>Everyone waiting, for debug listing only.</summary>
        public IEnumerable<Pawn> AllPlaceless =>
            placeless?.InnerListForReading ?? (IEnumerable<Pawn>)new List<Pawn>();
    }
}
