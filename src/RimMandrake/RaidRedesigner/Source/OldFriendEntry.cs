using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.RaidRedesigner
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §1.4, verbatim shape:
    // "OldFriendEntry { Pawn pawn (Scribe_References), Faction factionAtEntry,
    // RoleTag role, List<Encounter> encounters, int grudge, int notability,
    // int lastSeenTick, bool dead }".
    public class OldFriendEntry : IExposable, IRosterEntry
    {
        public Pawn Pawn;
        public Faction FactionAtEntry;
        public RoleTag Role;
        public List<Encounter> Encounters = new List<Encounter>();
        public int Grudge;
        public int Notability;
        public int LastSeenTick;
        public bool Dead;

        // True when this mod put the pawn in WorldPawns.ForcefullyKeptPawns (not someone else, e.g. a faction pinning its leader), so the pin
        // is released when the roster forgets them. A pin nobody released kept every fled raider ever seen alive forever.
        public bool PinnedByUs;

        // Only meaningful once Dead — §1.4 "a dead friend's brother is the
        // LLM's best material": the roster keeps the thread alive by naming
        // who inherits it. Never set by this mod (no LLM here); a later
        // consumer (Part 1, out of scope) is the one writer.
        public string KinOf;

        // Collapsed one-line text, written once at the moment Dead flips true
        // (MarkDead below) so a dead entry's footprint never grows again —
        // §1.4 "dead entries collapse to one line and stay".
        public string DeadSummary;

        public OldFriendEntry()
        {
        }

        public OldFriendEntry(Pawn pawn, Faction factionAtEntry, RoleTag role, int tick)
        {
            Pawn = pawn;
            FactionAtEntry = factionAtEntry;
            Role = role;
            LastSeenTick = tick;
        }

        public void AddEncounter(Encounter e)
        {
            Encounters.Add(e);
            LastSeenTick = e.Tick;
        }

        // RM_RosterKernel's view of this entry (the kernel is Verse-free, so it cannot name Pawn or Encounter's Scribe).
        RoleTag IRosterEntry.Role { get { return Role; } set { Role = value; } }
        int IRosterEntry.Grudge { get { return Grudge; } set { Grudge = value; } }
        int IRosterEntry.Notability { get { return Notability; } set { Notability = value; } }
        int IRosterEntry.LastSeenTick { get { return LastSeenTick; } set { LastSeenTick = value; } }
        bool IRosterEntry.Dead { get { return Dead; } }
        bool IRosterEntry.PinnedByUs { get { return PinnedByUs; } set { PinnedByUs = value; } }
        void IRosterEntry.NoteEncounter(int tick, RoleTag role, string summary) { AddEncounter(new Encounter(tick, role, summary)); }

        // Called once, the first time this entry is discovered dead (roster
        // GameComponent decides "discovered", this entry only knows how to
        // collapse). Idempotent: a second call is a no-op so nothing can
        // clobber the one-line summary once written.
        public void MarkDead(int tick, string cause)
        {
            if (Dead) return;
            Dead = true;
            LastSeenTick = tick;
            string name = Pawn?.LabelShortCap ?? "unknown";
            DeadSummary = RM_RosterKernel.DeadSummary(name, Role, Grudge, Notability, cause);
        }

        public void ExposeData()
        {
            Scribe_References.Look(ref Pawn, "pawn");
            Scribe_References.Look(ref FactionAtEntry, "factionAtEntry");
            Scribe_Values.Look(ref Role, "role", RoleTag.FledRaider);
            Scribe_Collections.Look(ref Encounters, "encounters", LookMode.Deep);
            Scribe_Values.Look(ref Grudge, "grudge", 0);
            Scribe_Values.Look(ref Notability, "notability", 0);
            Scribe_Values.Look(ref LastSeenTick, "lastSeenTick", 0);
            Scribe_Values.Look(ref Dead, "dead", false);
            Scribe_Values.Look(ref PinnedByUs, "pinnedByUs", false);
            Scribe_Values.Look(ref KinOf, "kinOf");
            Scribe_Values.Look(ref DeadSummary, "deadSummary");

            if (Scribe.mode == LoadSaveMode.PostLoadInit && Encounters == null)
                Encounters = new List<Encounter>();
        }
    }
}
