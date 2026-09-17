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

        // AFTERMATH_DEAD_LETTERS_1: which rule queued this, so the payload's
        // own letterLabel/letterText can be sent when it actually lands
        // (Patch_PayloadLanded's postfix on IncidentWorker.TryExecute,
        // matched back here by faction + payloadIncidentDefName in
        // AftermathRuleRunner.OnPayloadLanded). Null-safe everywhere this is
        // read - an old save from before this field existed loads it as
        // null and simply never sends the baseline letter for that marker's
        // in-flight incident (housekeeping still prunes it on FireTick).
        public RM_AftermathRuleDef Def;

        public QueuedAftermathMarker()
        {
        }

        public QueuedAftermathMarker(Faction faction, int fireTick, RM_AftermathRuleDef def = null)
        {
            Faction = faction;
            FireTick = fireTick;
            Def = def;
        }

        public void ExposeData()
        {
            Scribe_References.Look(ref Faction, "faction");
            Scribe_Values.Look(ref FireTick, "fireTick", 0);
            Scribe_Defs.Look(ref Def, "def");
        }
    }
}
