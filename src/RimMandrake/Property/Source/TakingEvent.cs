using Verse;

namespace RimMandrake.Property
{
    // The event object at the center of the spine. Future verb code
    // (SETTLEMENT_VERBS_WAVE_1 — pickpocket, burglary, fencing, the
    // claim-fee gizmo — none of which this fabric builds) constructs one of
    // these and calls PropertyEngine.Fire. This mod fires none itself: no
    // Harmony hook auto-detects a vanilla pickup as a TakingEvent — that
    // wiring is verb-job territory. Result fields are filled in by Fire and
    // are readable afterward for logging/testing.
    public class TakingEvent
    {
        public readonly Thing Thing;
        public readonly ClaimantRef Actor;
        public readonly TakingAct Act;
        public readonly int Tick;

        // Filled in by PropertyEngine.Fire.
        public ClaimResolution? PriorClaim;
        public bool WasAuthorized;
        public System.Collections.Generic.List<Pawn> Witnesses;

        public TakingEvent(Thing thing, ClaimantRef actor, TakingAct act, int tick)
        {
            Thing = thing;
            Actor = actor;
            Act = act;
            Tick = tick;
        }
    }
}
