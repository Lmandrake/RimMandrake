using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 2 (HOSTILE_MOBILE_PLANTS_1): "plus
    // activates if others of its own kind activate nearby: swarm" — the
    // owner's own words on the hostile-mobile-plant ruling. First real
    // (non-None) propagation rule.
    //
    // "Same kind" is read literally as same ThingDef (Thing.def), not Props.tag
    // — a tag groups sources that share a RESPONSE (several different plant
    // species answering one alarm network, the shipped RM_CompPlantAlarm's own
    // use of tag), while "kind" here means the same species waking its own
    // neighbours. The two are independent axes and this rule only reads the
    // first.
    //
    // 🔴 The one decision everything else hangs on (REACTION_MECHANISM_GENERALISE_1's
    // own words): every neighbour this rule wakes is charged against the SAME
    // event's shared budget via evt.Spend — never a cap of its own. Ten
    // gallowroots each "politely" waking eight neighbours is exactly the
    // unbounded-chain failure mode the item names; this rule cannot produce it,
    // because RM_ReactionEvent.Spend never grants more than RemainingBudget no
    // matter how many neighbours are found.
    //
    // Recurses: each neighbour it wakes (via
    // RM_CompReactionSource.TryActivateFromPropagation) runs ITS OWN
    // propagation in turn, using the same event — that is what lets the swarm
    // spread hop by hop through a dense patch rather than reaching only the
    // first plant's own radius, and it is exactly as bounded as a single hop
    // because every hop still spends from the one shared pool.
    // evt.TryMarkActivated (called inside TryActivateFromPropagation) is what
    // stops a dense cluster looping back on itself.
    //
    //   <propagation Class="RimMandrake.CreatureBehaviors.RM_ReactionPropagationRule_SameKindWithinRadius">
    //     <radius>10</radius>
    //     <budgetPerNeighbor>1</budgetPerNeighbor>
    //   </propagation>
    public class RM_ReactionPropagationRule_SameKindWithinRadius : RM_ReactionPropagationRule
    {
        /// <summary>How far from `source` a same-def neighbour can be and still be woken. INVENTED: 10.</summary>
        public float radius = 10f;

        /// <summary>Shared-budget cost to wake ONE neighbour. INVENTED: 1 — the eventBudget on the source's own comp is the real dial (a content author tunes swarm SIZE there, not here).</summary>
        public int budgetPerNeighbor = 1;

        public override void Propagate(RM_ReactionEvent evt, Thing source)
        {
            if (evt.Map == null || source == null)
            {
                return;
            }

            float radiusSq = radius * radius;

            // Snapshot, same reasoning as RM_CompPlantAlarm.TriggerAlarm:
            // waking a neighbour can itself mutate the map's pawn list
            // (further spawns, deaths) underneath an in-progress scan.
            List<Pawn> pawns = new List<Pawn>(evt.Map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                if (evt.RemainingBudget < budgetPerNeighbor)
                {
                    break; // nothing left to spend on further neighbours this hop
                }

                Pawn p = pawns[i];
                if (p == null || p == source || p.Dead)
                {
                    continue;
                }

                if (p.def != source.def)
                {
                    continue; // "same kind" only — a different species never wakes from this
                }

                if ((p.Position - source.Position).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                RM_CompReactionSource comp = p.TryGetComp<RM_CompReactionSource>();
                if (comp == null)
                {
                    continue; // same species, but this individual carries no reaction source at all
                }

                int granted = evt.Spend(budgetPerNeighbor);
                if (granted < budgetPerNeighbor)
                {
                    break; // budget ran out between the check above and here
                }

                comp.TryActivateFromPropagation(evt);
            }
        }
    }
}
