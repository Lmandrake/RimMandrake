using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1 (owner's own words, Drinker: "if it drains any
    // day-side races with normal warm iron blood, it becomes poisoned and
    // rapidly dies"). A marker on a RACE's ThingDef: this race's blood is
    // hydrocarbon (Deep-side), so draining it is SAFE for an
    // RM_CompFluidSacs carrier regardless of the victim's fleshType. Absent
    // = "warm iron blood" as far as the flesh-type list on the comp says.
    //
    //   <modExtensions>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_HydrocarbonBloodExtension" />
    //   </modExtensions>
    //
    // Attached to NOTHING yet — the Deeps races are wired by a later pass
    // (see the item). Carries no fields on purpose: presence is the whole
    // signal, and a race either has this blood or it does not.
    public class RM_HydrocarbonBloodExtension : DefModExtension
    {
    }
}
