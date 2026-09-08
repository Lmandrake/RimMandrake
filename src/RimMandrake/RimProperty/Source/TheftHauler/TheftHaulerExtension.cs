using Verse;

namespace RimMandrake.TheftHauler
{
    /// <summary>
    /// Marker DefModExtension: a pawn whose race ThingDef (or PawnKindDef,
    /// checked via race first — see FloatMenuOptionProvider_TheftHaulUninstall)
    /// carries this can order the RM_TheftHaulUninstall job against ANY
    /// Building, own-faction or not. No fields — this pass (BUILDING_THEFT_
    /// HAULER_1) does not implement carry-weight-scales-with-chassis (design/
    /// Jawa/wrecked_machines_resurrection.md's "carry weight scales with
    /// chassis" line is explicitly a later pass; hauling the resulting
    /// MinifiedThing already obeys the pawn's own vanilla carry capacity, no
    /// override needed for v1 to be correct). Deliberately generic — carries
    /// no Star Wars or Droidworks reference; see Patches/MuckrakerChassis_
    /// TheftHauler.xml for the one place this mod chooses which existing
    /// chassis gets marked.
    /// </summary>
    public class TheftHaulerExtension : DefModExtension
    {
    }
}
