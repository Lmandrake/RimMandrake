using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.Inhabited
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
    /// The displaced pool's per-person metadata, keyed by thingIDNumber (plain value dictionaries so a load cannot
    /// half-resolve them behind a pawn that did). No Verse type: DisplacedPool owns the ThingOwner and Scribes these
    /// fields under their own names; the offline fuzz compiles THIS file.
    /// </summary>
    public sealed class DisplacementBook
    {
        public Dictionary<int, DisplacedReason> reasons = new Dictionary<int, DisplacedReason>();
        public Dictionary<int, string> origins = new Dictionary<int, string>();
        /// <summary>Displacement order, so a draw can take the longest-waiting first.</summary>
        public Dictionary<int, int> displacedAt = new Dictionary<int, int>();
        public int nextOrder;

        public void EnsureNotNull()
        {
            if (reasons == null) reasons = new Dictionary<int, DisplacedReason>();
            if (origins == null) origins = new Dictionary<int, string>();
            if (displacedAt == null) displacedAt = new Dictionary<int, int>();
        }

        public void Record(int id, DisplacedReason reason, string origin)
        {
            reasons[id] = reason;
            origins[id] = origin;
            displacedAt[id] = nextOrder++;
        }

        public void Forget(int id)
        {
            reasons.Remove(id);
            origins.Remove(id);
            displacedAt.Remove(id);
        }

        public int OrderKey(int id)
        {
            return displacedAt.TryGetValue(id, out int o) ? o : int.MaxValue;
        }

        public DisplacedReason ReasonFor(int id)
        {
            return reasons.TryGetValue(id, out DisplacedReason r) ? r : DisplacedReason.Fled;
        }

        public string OriginFor(int id)
        {
            return origins.TryGetValue(id, out string o) ? o : null;
        }
    }

    /// <summary>
    /// Who is held by what, and the rule that nobody is ever held by NOTHING. Every movement of a person between the
    /// displaced pool, a place's roster and the map goes through one of these, with the engine's container calls passed
    /// in as delegates (T is Pawn in the game, an int in the fuzz). A person leaves one holder only when another has
    /// taken them, and a refusal puts them back where they were; the single way to lose somebody is a holder that
    /// refuses to take back its own member, reported through <c>onLost</c>.
    /// </summary>
    public static class InhabitedCustody
    {
        /// <summary>
        /// Take somebody into the pool. THE DEAD NEVER ENTER. <paramref name="prepare"/> is the engine side (despawn, leave
        /// WorldPawns, change faction) and runs only for a usable pawn; metadata is recorded only once the add succeeded.
        /// </summary>
        public static bool Absorb(DisplacementBook book, int id, bool deadOrDestroyed, Action prepare,
            Func<bool> tryAdd, DisplacedReason reason, string origin)
        {
            if (deadOrDestroyed)
            {
                return false;
            }
            prepare?.Invoke();
            if (!tryAdd())
            {
                return false;
            }
            book.Record(id, reason, origin);
            return true;
        }

        /// <summary>Eligible people, longest-waiting first (stable for ties). The filter differs between draw routes; the ordering never does.</summary>
        public static List<T> Order<T>(DisplacementBook book, IEnumerable<T> eligible, Func<T, int> idOf)
        {
            return eligible.OrderBy(p => book.OrderKey(idOf(p))).ToList();
        }

        /// <summary>
        /// Hand one person to a destination and forget them here ONLY once the destination has taken them. On refusal or
        /// exception they go back with their reason and place in the queue intact.
        /// </summary>
        public static bool HandOver<T>(DisplacementBook book, T p, int id, Func<T, bool> removeFromPool,
            Func<T, bool> putBack, Func<T, bool> destination, Action<T> onLost)
        {
            if (p == null || !removeFromPool(p))
            {
                return false;
            }
            bool taken;
            try
            {
                taken = destination(p);
            }
            catch
            {
                Restore(book, p, id, putBack, onLost);
                throw;
            }
            if (!taken)
            {
                Restore(book, p, id, putBack, onLost);
                return false;
            }
            book.Forget(id);
            return true;
        }

        /// <summary>
        /// Put a refused person back. If even that fails they are held by nothing (reported through onLost), and their
        /// metadata is dropped with them -- it described a pool member they no longer are.
        /// </summary>
        private static void Restore<T>(DisplacementBook book, T p, int id, Func<T, bool> putBack, Action<T> onLost)
        {
            if (!putBack(p))
            {
                book.Forget(id);
                onLost?.Invoke(p);
            }
        }

        /// <summary>Move up to <paramref name="count"/> of the ordered candidates into a destination; returns how many arrived.</summary>
        public static int DrawInto<T>(DisplacementBook book, List<T> orderedCandidates, int count, Func<T, int> idOf,
            Func<T, bool> removeFromPool, Func<T, bool> putBack, Func<T, bool> destination, Action<T> onLost,
            List<T> arrived)
        {
            if (count <= 0 || destination == null)
            {
                return 0;
            }
            int moved = 0;
            for (int i = 0; i < orderedCandidates.Count && moved < count; i++)
            {
                if (!HandOver(book, orderedCandidates[i], idOf(orderedCandidates[i]), removeFromPool, putBack, destination, onLost))
                {
                    continue;
                }
                arrived?.Add(orderedCandidates[i]);
                moved++;
            }
            return moved;
        }

        /// <summary>The first ordered candidate a caller accepts, or default if nobody was waiting or all were refused.</summary>
        public static T DrawAny<T>(DisplacementBook book, List<T> orderedCandidates, Func<T, int> idOf,
            Func<T, bool> removeFromPool, Func<T, bool> putBack, Func<T, bool> destination, Action<T> onLost)
        {
            if (destination == null)
            {
                return default(T);
            }
            for (int i = 0; i < orderedCandidates.Count; i++)
            {
                if (HandOver(book, orderedCandidates[i], idOf(orderedCandidates[i]), removeFromPool, putBack, destination, onLost))
                {
                    return orderedCandidates[i];
                }
            }
            return default(T);
        }

        /// <summary>
        /// Everybody on a roster goes to the pool (a place emptied by fate or destruction). A person the pool refuses goes
        /// back on the roster; only if the roster refuses too are they lost. Returns how many reached the pool.
        /// </summary>
        public static int MoveRosterToPool<T>(IList<T> snapshot, Func<T, bool> skip, Func<T, bool> removeFromRoster,
            Func<T, bool> absorb, Func<T, bool> returnToRoster, Action<T> onLost)
        {
            int moved = 0;
            for (int i = 0; i < snapshot.Count; i++)
            {
                T p = snapshot[i];
                if (p == null || skip(p) || !removeFromRoster(p))
                {
                    continue;
                }
                if (absorb(p))
                {
                    moved++;
                }
                else if (!returnToRoster(p))
                {
                    onLost?.Invoke(p);
                }
            }
            return moved;
        }

        public enum RecallOutcome { Roster, Placeless, LeftToWorld }

        /// <summary>A resident recalled at map teardown: roster first, else the pool, else (never silently) the world.</summary>
        public static RecallOutcome Recall<T>(T p, Func<T, bool> returnToRoster, Func<T, bool> absorb)
        {
            if (returnToRoster(p))
            {
                return RecallOutcome.Roster;
            }
            return absorb(p) ? RecallOutcome.Placeless : RecallOutcome.LeftToWorld;
        }

        /// <summary>
        /// The kinds a cast wants, in authored order (leaders and traders first), each role repeated by its rolled count,
        /// trimmed from the BACK to <paramref name="size"/> so the front of the list keeps its authored roles. A null
        /// kind (default for reference types) is skipped.
        /// </summary>
        public static List<T> BuildWanted<T>(IList<T> kinds, IList<int> rolledCounts, int size) where T : class
        {
            List<T> wanted = new List<T>();
            for (int i = 0; i < kinds.Count; i++)
            {
                if (kinds[i] == null) continue;
                for (int j = 0; j < rolledCounts[i]; j++)
                {
                    wanted.Add(kinds[i]);
                }
            }
            if (size > 0 && wanted.Count > size)
            {
                wanted.RemoveRange(size, wanted.Count - size);
            }
            return wanted;
        }

        /// <summary>Slots left to GENERATE: the pool fills the TAIL of the wanted list, the head must still be generated.</summary>
        public static int GenerateCount(int wantedCount, int fromPool)
        {
            return Math.Max(0, wantedCount - fromPool);
        }

        /// <summary>Index of the authored character the next generated pawn receives, or -1 when the authored cast is used up.</summary>
        public static int UpcomingCharacter(int nextCharacter, int characterCount)
        {
            return nextCharacter >= 0 && nextCharacter < characterCount ? nextCharacter : -1;
        }
    }
}
