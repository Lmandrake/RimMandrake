using Verse;

namespace RimMandrake.AnimalTheft
{
    /// <summary>
    /// Marker DefModExtension: RIMPROPERTY_ANIMAL_THEFT_1's species gate for
    /// the WILD half of the owner's ask ("some wild animals" steal). A pawn
    /// whose race ThingDef carries this is eligible for JobGiver_RM_WildSteal
    /// (wired into the vanilla Animal think tree at the Animal_PreWander
    /// insertion hook — see Defs/AnimalTheft/ThinkTreeDefs_AnimalSteal.xml).
    /// No fields — same "deliberately generic, campaign-blind" shape as
    /// TheftHauler/TheftHaulerExtension.cs. Only Patches/AnimalTheft/
    /// RaccoonWildTheft.xml grants it (Core's Raccoon, per its own vanilla
    /// flavor text: "happy to break into your garbage container, or your
    /// kitchen, to eat almost anything"). This mod does not gate the wild
    /// route on trainability at all — that would be backwards, since wild
    /// animals below this mark are untrainable (Raccoon's own trainability
    /// is None) and the trained-pet route (RM_Steal, TrainableDef) is a
    /// SEPARATE, unrelated gate covering the "agile pets" half of the ask.
    /// </summary>
    public class WildTheftExtension : DefModExtension
    {
    }
}
