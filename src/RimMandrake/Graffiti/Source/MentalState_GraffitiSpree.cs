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
    }
}
