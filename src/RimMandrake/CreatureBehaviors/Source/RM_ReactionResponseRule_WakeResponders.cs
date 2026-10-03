using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 4: the shipped RM_CompPlantAlarm's
    // own behaviour, lifted onto the general path with NO behaviour change.
    // Every filter, the order they run in, the snapshot, the forceWake
    // Manhunter start and the one "network answers" message are byte-for-byte
    // what RM_CompPlantAlarm.TriggerAlarm did before this step (git history of
    // that file is the reference). The only additions are the general path's:
    //   - each woken responder spends 1 from the event's shared budget; the
    //     migrated alarm mints its event with int.MaxValue, so this never
    //     binds for the groves — the radius stays their only bound, exactly
    //     as before (spec step 4: "budget its existing radius");
    //   - a responder standing in a suppressed cell (step 5) does not answer.
    //     No suppression exists unless a counter-tool lays one, so a grove
    //     with no smoke on it behaves exactly as it did.
    //
    // Selection is "every tagged responder within radius of the origin", which
    // is why this is a response and not a propagation: nothing it wakes
    // becomes a source in turn (shipped behaviour: propagation none).
    public class RM_ReactionResponseRule_WakeResponders : RM_ReactionResponseRule
    {
        public float radius = 18f;

        /// <summary>Null = vanilla Manhunter (the shipped alarm's only response).</summary>
        public MentalStateDef mentalState;

        public string wokeMessage;

        public override void Respond(RM_ReactionEvent evt, Thing source)
        {
            int woke = 0;
            Map map = evt.Map;
            if (map == null)
            {
                return;
            }

            MentalStateDef state = mentalState ?? MentalStateDefOf.Manhunter;
            IntVec3 origin = evt.OriginCell;
            float radiusSq = radius * radius;

            // Snapshot: TryStartMentalState can trigger further reactions
            // (fleeing, aggro) that mutate the map's pawn list underneath us.
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || p.Downed)
                {
                    continue;
                }

                if ((p.Position - origin).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                if (!RM_ReactionResponders.Answers(p, evt.Tag))
                {
                    continue;
                }

                if (p.mindState == null || p.mindState.mentalStateHandler == null)
                {
                    continue;
                }

                if (p.InMentalState)
                {
                    continue;
                }

                if (RM_ReactionSuppression.IsSuppressed(map, p.Position))
                {
                    continue;
                }

                if (evt.RemainingBudget <= 0)
                {
                    break;
                }

                if (p.mindState.mentalStateHandler.TryStartMentalState(state, forceWake: true))
                {
                    evt.Spend(1);
                    woke++;
                }
            }

            if (woke > 0 && !wokeMessage.NullOrEmpty())
            {
                Messages.Message(wokeMessage, new TargetInfo(origin, map), MessageTypeDefOf.ThreatBig);
            }
        }
    }
}
