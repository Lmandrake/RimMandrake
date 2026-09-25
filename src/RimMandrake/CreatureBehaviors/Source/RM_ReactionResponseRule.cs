using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 1. The other pluggable part: what an
    // event's RESPONSE actually does. GREENTIDE_WASP_SWARM_1 needs "spawn a
    // bounded group" (RM_ReactionResponseRule_SpawnPawns, this pass); a later
    // step needs "wake existing responders to Manhunter" (the shipped
    // RM_CompPlantAlarm's own behaviour, migrated on its own item, NOT this
    // one) and "rally responders inward without berserking" (the ant hive).
    // Abstract class for the same XML-polymorphism reason as
    // RM_ReactionPropagationRule.
    public abstract class RM_ReactionResponseRule
    {
        // Called once per trigger, after propagation. `source` is the Thing
        // that rang the alarm (usually the same as evt.Origin). Map and origin
        // cell already live on `evt` — no need to pass them again. Implementations
        // draw from `evt`'s shared (already-propagation-reduced) budget for
        // whatever they do — never a budget of their own.
        public abstract void Respond(RM_ReactionEvent evt, Thing source);
    }
}
