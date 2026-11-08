using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// A player colonist, undrafted, on a Pyrelands map. Gates RM_PyreEatBeforeFireDuty: vanilla's colonist tree runs emergency
    /// work (fighting fire in the home area) BEFORE "get food (only if starving)", which costs nothing where a fire is out in
    /// minutes. Here a burn can stand in the home area for most of a day: on map x a fresh colony left alone beat fire from day
    /// 2.2 to 3.1, food 0.20 -> 0.11 -> 0.05 -> 0.00, and the first colonist went down starving beside the last survival pack.
    /// Thirst already sits above the fire line (FlowWorks' drink giver is at Humanlike_PostDuty); this puts eating there too,
    /// at urgently hungry only, so a colonist breaks off for a meal and goes back to the fire.
    /// </summary>
    public class ThinkNode_ConditionalPyrelandsColonist : ThinkNode_Conditional
    {
        protected override bool Satisfied(Pawn pawn)
        {
            return PyrelandsMechanicsGate.On && pawn.IsColonist && !pawn.Drafted && pawn.Map?.Biome != null
                && pawn.Map.Biome.defName == "RM_Pyrelands";
        }
    }
}
