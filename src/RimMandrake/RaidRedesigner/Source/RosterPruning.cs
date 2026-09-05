using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.RaidRedesigner
{
    // Extracted pure logic (no Verse/live-game dependency) so the cap/prune
    // rule can be selftested offline, same discipline as
    // RimMandrake.Property.SelfTest extracting ClaimEngine's winner-picking
    // order. GameComponent_OldFriends.AddOrUpdate calls this; nothing else
    // should reimplement the ordering.
    public static class RosterPruning
    {
        // design/Jawa/proposals/plot_mechanisms_wave.md §1.4: "Roster cap 24
        // living; prune lowest notability; dead entries collapse to one line
        // and stay." Only entries with Dead == false count against the cap —
        // a dead entry's one-line summary is deliberately kept forever
        // (§1.4's "a dead friend's brother is the LLM's best material").
        //
        // Returns the LIVING entries to remove so `living.Count - result.Count
        // == cap`. Ties (equal notability) break on LOWER LastSeenTick first
        // (the stalest of the tied entries goes) so the rule is deterministic
        // and never depends on List ordering/insertion order.
        public static List<OldFriendEntry> SelectPruneVictims(List<OldFriendEntry> entries, int cap)
        {
            var living = entries.Where(e => e != null && !e.Dead).ToList();
            int overflow = living.Count - cap;
            if (overflow <= 0) return new List<OldFriendEntry>();

            return living
                .OrderBy(e => e.Notability)
                .ThenBy(e => e.LastSeenTick)
                .Take(overflow)
                .ToList();
        }
    }
}
