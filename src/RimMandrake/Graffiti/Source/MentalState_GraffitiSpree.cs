using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Absorbed from Mlie.GraffitiMod's MentalState_GraffitiPaintingSpree
    // (compiled-only, no source shipped). No override needed - every vanilla
    // mental state that behaves this way (wander/act-until-recovery, driven
    // entirely by its ThinkTree's JobGiver rather than custom state logic)
    // ships an otherwise-empty stateClass subclass; a bare `MentalState`
    // cannot be assigned directly (every real MentalStateDef in vanilla
    // source declares its own, confirmed by reading MentalStates_Mood.xml).
    public class MentalState_GraffitiSpree : MentalState
    {
        // Whose work the spree went over, told once now rather than a message per mark as it happened.
        public override void PostEnd()
        {
            base.PostEnd();
            GraffitiSocial.SpreeEnded(pawn);
        }
    }
}
