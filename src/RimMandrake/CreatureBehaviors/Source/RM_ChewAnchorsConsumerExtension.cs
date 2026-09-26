using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_FAUNA_ROSTER_1 — the consumer-side half of RM_ChewableExtension.
    // RM_JobGiver_ChewAnchors is spliced into vanilla's shared Animal_PreWander
    // insertion tag (RM_ThinkTree_ChewAnchors.xml), which every wild/tame animal's
    // ThinkTree passes through — so without a per-race gate, EVERY animal on a
    // map with registered SenseWeb cells would try to chew anchors, not just the
    // one race meant to. Same shape as this assembly's other consumer-side
    // markers checked in C# rather than at the ThinkTree splice point (see
    // RimProperty's WildTheftExtension / JobGiver_RM_WildSteal precedent,
    // ThinkTreeDefs_AnimalSteal.xml's own header: "there is no XML per-species
    // hook at this splice point"). No fields: presence on the pawn's ThingDef
    // is the whole signal. RM_Quarrok (webwork_fauna_roster_2026-09-23.md row 1)
    // is the first and, at authoring time, only consumer race.
    public class RM_ChewAnchorsConsumerExtension : DefModExtension
    {
    }
}
