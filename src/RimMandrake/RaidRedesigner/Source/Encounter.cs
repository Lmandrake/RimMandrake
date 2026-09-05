using Verse;

namespace RimMandrake.RaidRedesigner
{
    // One line in an OldFriendEntry's history — design/Jawa/proposals/
    // plot_mechanisms_wave.md §1.4: "the encounter list in one line each".
    // Deliberately just a tick + a role tag + free text; no mechanism reads
    // structured fields off this yet (that is Part 1's LLM dossier, out of
    // scope here) so there is nothing to over-model.
    public class Encounter : IExposable
    {
        public int Tick;
        public RoleTag Role;
        public string Summary;

        public Encounter()
        {
        }

        public Encounter(int tick, RoleTag role, string summary)
        {
            Tick = tick;
            Role = role;
            Summary = summary;
        }

        public void ExposeData()
        {
            Scribe_Values.Look(ref Tick, "tick", 0);
            Scribe_Values.Look(ref Role, "role", RoleTag.FledRaider);
            Scribe_Values.Look(ref Summary, "summary");
        }

        public override string ToString() => "[" + Role + " @" + Tick + "] " + Summary;
    }
}
