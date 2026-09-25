using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 2 (HOSTILE_MOBILE_PLANTS_1). The
    // response a rooted ambusher itself needs, as opposed to
    // RM_ReactionResponseRule_SpawnPawns' "birth new pawns": there is nothing
    // to spawn here, the SOURCE is the pawn — disturbing (or being propagated
    // into by) a gallowroot should make THAT gallowroot itself go hostile, not
    // conjure another one. `source` must be a Pawn (the plant's own race is an
    // animal def per the item's own ruling: "these are animal defs... not
    // Plant defs") or this response no-ops.
    //
    // Reuses RM_MentalState_ScopedAggression exactly as GREENTIDE_WASP_SWARM_1's
    // spawn response does — content-blind, no new mental-state class needed:
    // hostile to evt.Instigator alone (never a map-wide manhunter flip),
    // self-ending once the target is far enough from where THIS pawn was
    // rooted when it woke. That anchor is `source.Position` at the moment this
    // runs (before any job/movement this tick), not evt.OriginCell — for a
    // neighbour woken several propagation hops from the original disturbance,
    // evt.OriginCell could be well outside its own reasonable chase range.
    //
    //   <response Class="RimMandrake.CreatureBehaviors.RM_ReactionResponseRule_ActivateSelf">
    //     <mentalState>RM_SwarmAggression</mentalState>
    //     <disengageRadius>15</disengageRadius>
    //     <budgetCost>1</budgetCost>
    //   </response>
    public class RM_ReactionResponseRule_ActivateSelf : RM_ReactionResponseRule
    {
        /// <summary>Mental state this pawn starts in. No default — an activate-self response with nothing to start in is a config error, same posture as RM_CompProperties_ReactionSource.response itself.</summary>
        public MentalStateDef mentalState;

        /// <summary>How far evt.Instigator must get from this pawn's own rooted position before it gives up. Only meaningful if mentalState's stateClass derives from RM_MentalState_ScopedAggression. INVENTED: 15.</summary>
        public float disengageRadius = 15f;

        /// <summary>Shared-budget cost to activate. INVENTED: 1 — same reasoning as RM_ReactionPropagationRule_SameKindWithinRadius.budgetPerNeighbor: the real size dial is the source comp's own eventBudget.</summary>
        public int budgetCost = 1;

        public override void Respond(RM_ReactionEvent evt, Thing source)
        {
            if (mentalState == null)
            {
                return;
            }

            Pawn pawn = source as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed)
            {
                return;
            }

            if (pawn.InMentalState || pawn.mindState?.mentalStateHandler == null)
            {
                return;
            }

            int granted = evt.Spend(budgetCost);
            if (granted < budgetCost)
            {
                return; // the shared budget is already spent — this pawn stays dormant
            }

            IntVec3 anchor = pawn.Position;

            bool started = pawn.mindState.mentalStateHandler.TryStartMentalState(
                mentalState,
                reason: null,
                forced: true,
                forceWake: true,
                causedByMood: false,
                otherPawn: evt.Instigator);

            if (started && pawn.MentalState is RM_MentalState_ScopedAggression state)
            {
                state.anchorCell = anchor;
                state.disengageRadius = disengageRadius;
            }
        }
    }
}
