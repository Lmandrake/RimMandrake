using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 1. One of the mechanism's four
    // pluggable parts (design/RimMandrake/reaction_mechanism_spec.md): what an
    // event PROPAGATES to before its response runs. Wired straight into
    // RM_CompReactionSource so a real rule (same-kind-within-radius for the
    // plant swarm, step 2; responder-converges-inward for the ant hive, step 3)
    // slots in later without touching the comp.
    //
    // Abstract class rather than an interface — same reason CompProperties is a
    // class in this engine: XML polymorphism via Class= needs a base type, and
    // this assembly's own CompProperties_* pattern already establishes the
    // convention.
    public abstract class RM_ReactionPropagationRule
    {
        // Called once per trigger, before the response. Implementations spend
        // from `evt`'s shared budget for whatever they wake/notify — never a
        // budget of their own.
        public abstract void Propagate(RM_ReactionEvent evt, Thing source);
    }

    // GREENTIDE_WASP_SWARM_1 needs no propagation at all: "wasp propagation is
    // the wasps themselves" (the item's own words) — the spawn response IS the
    // spread. This is the explicit no-op, not an omitted step, and it is the
    // default on RM_CompProperties_ReactionSource so a gall needs no XML for it.
    public class RM_ReactionPropagationRule_None : RM_ReactionPropagationRule
    {
        public static readonly RM_ReactionPropagationRule_None Instance = new RM_ReactionPropagationRule_None();

        public override void Propagate(RM_ReactionEvent evt, Thing source)
        {
            // Intentionally empty.
        }
    }
}
