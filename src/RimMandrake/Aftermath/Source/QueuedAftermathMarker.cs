using RimWorld;
using Verse;

namespace RimMandrake.Aftermath
{
    // Vanilla's own IncidentQueue does not expose "who queued this and why",
    // so AftermathRuleRunner keeps its own small scribed ledger purely to
    // enforce doc §2.2's discipline rule ("max one queued aftermath per
    // faction and two total"). Pruned once fireTick has passed - a fired
    // incident's queue slot is gone either way, so keeping the marker after
    // that would only ever make room LESS available, never correctly track
    // "currently queued".
    public class QueuedAftermathMarker : IExposable
    {
        public Faction Faction;
        public int FireTick;

        public QueuedAftermathMarker()
        {
        }

        public QueuedAftermathMarker(Faction faction, int fireTick)
        {
            Faction = faction;
            FireTick = fireTick;
        }

        public void ExposeData()
        {
            Scribe_References.Look(ref Faction, "faction");
            Scribe_Values.Look(ref FireTick, "fireTick", 0);
        }
    }
}
