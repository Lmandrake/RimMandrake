using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 3 (FEVERWOOD_ANT_HIVE_DUNGEON_1).
    // The hive rally's propagation: "responder -> responder, inward"
    // (reaction_mechanism_spec.md). Differs from
    // RM_ReactionPropagationRule_SameKindWithinRadius on exactly one axis —
    // WHO counts as a neighbour. Same-kind reads Thing.def (a gallowroot wakes
    // gallowroots); this reads the race's RM_AlarmResponderExtension tag
    // against the EVENT's tag, so every caste sharing a tag answers one alarm
    // (worker wakes queen, queen wakes worker) — the same tag grouping the
    // shipped RM_CompPlantAlarm already uses, so a content pack reuses the one
    // extension rather than learning a second.
    //
    // Same bounds as its sibling, because it is the same mechanism: every
    // neighbour woken is charged to the ONE shared event budget (evt.Spend),
    // hop-by-hop recursion runs through each neighbour's own
    // RM_CompReactionSource.TryActivateFromPropagation, and
    // evt.TryMarkActivated stops a corridor loop paying twice. A neighbour in
    // a suppressed cell (step 5) is skipped — the event does not pass through
    // smoke.
    //
    //   <propagation Class="RimMandrake.CreatureBehaviors.RM_ReactionPropagationRule_RespondersWithinRadius">
    //     <radius>9</radius>
    //     <budgetPerNeighbor>1</budgetPerNeighbor>
    //   </propagation>
    public class RM_ReactionPropagationRule_RespondersWithinRadius : RM_ReactionPropagationRule
    {
        /// <summary>Hop reach from the propagating responder. INVENTED: 9 — about one hive room plus its corridor mouth, so the alarm travels room to room rather than jumping the whole hive in one hop.</summary>
        public float radius = 9f;

        /// <summary>Shared-budget cost per neighbour woken. The source comp's eventBudget is the real dial.</summary>
        public int budgetPerNeighbor = 1;

        public override void Propagate(RM_ReactionEvent evt, Thing source)
        {
            if (evt.Map == null || source == null)
            {
                return;
            }

            float radiusSq = radius * radius;
            List<Pawn> pawns = new List<Pawn>(evt.Map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                if (evt.RemainingBudget < budgetPerNeighbor)
                {
                    break;
                }

                Pawn p = pawns[i];
                if (p == null || p == source || p.Dead || p.Downed || !p.Spawned)
                {
                    continue;
                }

                if ((p.Position - source.Position).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                if (!RM_ReactionResponders.Answers(p, evt.Tag))
                {
                    continue;
                }

                if (RM_ReactionSuppression.IsSuppressed(evt.Map, p.Position))
                {
                    continue;
                }

                RM_CompReactionSource comp = p.TryGetComp<RM_CompReactionSource>();
                if (comp == null || comp.HasHandled(evt))
                {
                    continue; // no comp to recurse through, or already reached by another path — spend nothing
                }

                if (evt.Spend(budgetPerNeighbor) < budgetPerNeighbor)
                {
                    break;
                }

                comp.TryActivateFromPropagation(evt);
            }
        }
    }

    // The tag match RM_CompPlantAlarm has always used, lifted out so the
    // general path and the migrated alarm cannot drift apart: a race with no
    // RM_AlarmResponderExtension (or a blank tag) never answers; a blank
    // event tag matches any responder; otherwise tags must be identical.
    public static class RM_ReactionResponders
    {
        public static bool Answers(Pawn p, string eventTag)
        {
            RM_AlarmResponderExtension ext = p?.def?.GetModExtension<RM_AlarmResponderExtension>();
            if (ext == null || ext.tag.NullOrEmpty())
            {
                return false;
            }
            return eventTag.NullOrEmpty() || ext.tag == eventTag;
        }
    }
}
