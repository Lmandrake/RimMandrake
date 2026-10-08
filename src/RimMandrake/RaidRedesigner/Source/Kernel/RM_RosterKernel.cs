using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.RaidRedesigner
{
    // Verse-free kernel of the OldFriends roster (design/Jawa/proposals/plot_mechanisms_wave.md 1.4). GameComponent_OldFriends and
    // OldFriendEntry call these; the seeded fuzz under Source/SelfTest compiles THIS file directly (a `using Verse;` here breaks that build).

    /// <summary>What the kernel needs from a roster entry. OldFriendEntry implements it over a Pawn; the fuzz implements it over an int.</summary>
    public interface IRosterEntry
    {
        RoleTag Role { get; set; }
        int Grudge { get; set; }
        int Notability { get; set; }
        int LastSeenTick { get; set; }
        bool Dead { get; }
        void NoteEncounter(int tick, RoleTag role, string summary);
        /// <summary>True when THIS mod added the pawn to the forcefully-kept set (and so may take it out again when the roster forgets them).</summary>
        bool PinnedByUs { get; set; }
    }

    public sealed class RecordOutcome<T> where T : class, IRosterEntry
    {
        public T Entry;
        public bool IsNew;
        /// <summary>The cap pruned the very entry this call created (its notability was strictly the lowest). The caller must not pin it.</summary>
        public bool EvictedSelf;
        public List<T> Victims = new List<T>();
    }

    public static class RM_RosterKernel
    {
        public const int GrudgeMin = -100, GrudgeMax = 100, NotabilityMin = 0, NotabilityMax = 100;

        public static int Clamp(int value, int min, int max)
        {
            if (value < min) return min;
            if (value > max) return max;
            return value;
        }

        /// <summary>A hook's delta scaled by the player's strength multiplier. Truncates toward zero (PROVISIONAL: round-to-nearest may read better).</summary>
        public static int ScaledDelta(int delta, float multiplier)
        {
            return (int)(delta * multiplier);
        }

        public static int NextGrudge(int grudge, int delta, float multiplier)
        {
            return Clamp(grudge + ScaledDelta(delta, multiplier), GrudgeMin, GrudgeMax);
        }

        public static int NextNotability(int notability, int delta, float multiplier)
        {
            return Clamp(notability + ScaledDelta(delta, multiplier), NotabilityMin, NotabilityMax);
        }

        /// <summary>The LIVING entries to drop so that at most `cap` remain. Lowest notability first, ties on the stalest LastSeenTick.
        /// Dead entries never count and are never chosen (a dead friend's one-line summary stays forever).</summary>
        public static List<T> SelectPruneVictims<T>(List<T> entries, int cap) where T : class, IRosterEntry
        {
            var living = entries.Where(e => e != null && !e.Dead).ToList();
            int overflow = living.Count - cap;
            if (overflow <= 0) return new List<T>();
            return living.OrderBy(e => e.Notability).ThenBy(e => e.LastSeenTick).Take(overflow).ToList();
        }

        /// <summary>The whole of RecordEncounter after its settings/null gates: find or create the pawn's living entry, upgrade the role
        /// to Captain only, append the encounter, apply the scaled deltas, and enforce the cap only AFTER those deltas (and only for a new entry).</summary>
        public static RecordOutcome<T> Record<T>(List<T> entries, Func<T, bool> isThePawn, Func<T> create, RoleTag role, int tick,
            string summary, int grudgeDelta, int notabilityDelta, float multiplier, int cap) where T : class, IRosterEntry
        {
            var outcome = new RecordOutcome<T>();
            T entry = entries.Find(e => !e.Dead && isThePawn(e));
            outcome.IsNew = entry == null;
            if (outcome.IsNew)
            {
                entry = create();
                entries.Add(entry);
            }
            else if (role == RoleTag.Captain)
            {
                entry.Role = RoleTag.Captain;
            }

            entry.NoteEncounter(tick, role, summary);
            entry.Grudge = NextGrudge(entry.Grudge, grudgeDelta, multiplier);
            entry.Notability = NextNotability(entry.Notability, notabilityDelta, multiplier);

            if (outcome.IsNew)
            {
                outcome.Victims = SelectPruneVictims(entries, cap);
                foreach (T victim in outcome.Victims)
                {
                    entries.Remove(victim);
                    if (ReferenceEquals(victim, entry)) outcome.EvictedSelf = true;
                }
            }
            outcome.Entry = entry;
            return outcome;
        }

        /// <summary>Whether the entry owns a pin after a pin attempt: it keeps one it already had, and takes ownership only when the pawn was NOT
        /// already force-kept by someone else (a faction pinning its leader) - a pin that was never ours is never ours to release.</summary>
        public static bool PinnedByUsAfter(bool alreadyOurs, bool keptBeforeThisCall, bool keptAfterThisCall)
        {
            return alreadyOurs || (!keptBeforeThisCall && keptAfterThisCall);
        }

        /// <summary>A forgotten (pruned) friend is unpinned only if we pinned them, and never while they lead a faction.</summary>
        public static bool ShouldUnpin(bool pinnedByUs, bool leadsAFaction)
        {
            return pinnedByUs && !leadsAFaction;
        }

        public enum SweepVerdict { Alive, Died, Lost }

        /// <summary>The hourly death poll. A living entry whose Pawn reference resolved to null (the pawn was discarded; Scribe_References gives null)
        /// can never be marked dead by the pawn and would count against the cap forever, so it collapses as Lost.</summary>
        public static SweepVerdict Sweep(bool entryDead, bool pawnIsNull, bool pawnDead)
        {
            if (entryDead) return SweepVerdict.Alive;
            if (pawnIsNull) return SweepVerdict.Lost;
            return pawnDead ? SweepVerdict.Died : SweepVerdict.Alive;
        }

        public static string DeadSummary(string name, RoleTag role, int grudge, int notability, string cause)
        {
            return name + " (" + role + ", grudge " + grudge + ", notability " + notability + ") — " + cause;
        }
    }
}
