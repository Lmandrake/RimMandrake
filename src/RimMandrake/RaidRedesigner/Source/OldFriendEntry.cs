using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.RaidRedesigner
{
    // design/Jawa/proposals/plot_mechanisms_wave.md §1.4, verbatim shape:
    // "OldFriendEntry { Pawn pawn (Scribe_References), Faction factionAtEntry,
    // RoleTag role, List<Encounter> encounters, int grudge, int notability,
    // int lastSeenTick, bool dead }".
    public class OldFriendEntry : IExposable
    {
        public Pawn Pawn;
        public Faction FactionAtEntry;
        public RoleTag Role;
        public List<Encounter> Encounters = new List<Encounter>();
        public int Grudge;
        public int Notability;
        public int LastSeenTick;
        public bool Dead;

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
            DeadSummary = name + " (" + Role + ", grudge " + Grudge + ", notability " + Notability + ") — " + cause;
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
            Scribe_Values.Look(ref KinOf, "kinOf");
            Scribe_Values.Look(ref DeadSummary, "deadSummary");

            if (Scribe.mode == LoadSaveMode.PostLoadInit && Encounters == null)
                Encounters = new List<Encounter>();
        }
    }
}
