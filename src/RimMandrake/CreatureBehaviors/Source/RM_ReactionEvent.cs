using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 1 (GREENTIDE_WASP_SWARM_1 proves it).
    // Spec: design/RimMandrake/reaction_mechanism_spec.md.
    //
    // The one decision the spec calls load-bearing: a disturbance creates ONE
    // event object carrying a SHARED budget, and every propagation/response step
    // spends from the SAME event rather than bounding itself. Ten sources each
    // "politely" granting their own cap composes into an unbounded total; a
    // shared, spendable budget is what makes the TOTAL the tunable number.
    //
    // Deliberately a plain class, not a Def or a Scribe-saved object: an event
    // lives and dies within a single trigger's call stack (build it, propagate,
    // respond, discard). Nothing here needs to survive a save.
    public class RM_ReactionEvent
    {
        /// <summary>The Thing whose disturbance created this event (the gall, the guardian plant).</summary>
        public readonly Thing Origin;

        /// <summary>The map the disturbance happened on.</summary>
        public readonly Map Map;

        /// <summary>Where the disturbance happened — usually Origin.Position, kept separately in case Origin is destroyed mid-event.</summary>
        public readonly IntVec3 OriginCell;

        // Free-form group identity, mirroring RM_CompPlantAlarm's tag —
        // unused by RM_ReactionPropagationRule_None, reserved for a future
        // same-kind/radius propagation rule (step 2) to group sources.
        public readonly string Tag;

        /// <summary>
        /// The pawn whose action rang the alarm, if any (PostPostApplyDamage's
        /// DamageInfo.Instigator, when it resolves to a Pawn — null for a
        /// harvest trigger or damage from a non-pawn source). A response that
        /// aims a reaction at "whoever did this" (RM_MentalState_ScopedAggression)
        /// reads it from here rather than re-deriving it.
        /// </summary>
        public readonly Pawn Instigator;

        public int RemainingBudget { get; private set; }

        public RM_ReactionEvent(Thing origin, Map map, IntVec3 originCell, string tag, Pawn instigator, int budget)
        {
            Origin = origin;
            Map = map;
            OriginCell = originCell;
            Tag = tag;
            Instigator = instigator;
            RemainingBudget = Mathf.Max(0, budget);
        }

        // Draws up to `amount` from the shared budget and returns how much was
        // actually granted (never more than what remained). A propagation rule
        // or a response calls this once for whatever it intends to do with its
        // share — never bounds itself independently of the event.
        public int Spend(int amount)
        {
            int granted = Mathf.Clamp(amount, 0, RemainingBudget);
            RemainingBudget -= granted;
            return granted;
        }
    }
}
