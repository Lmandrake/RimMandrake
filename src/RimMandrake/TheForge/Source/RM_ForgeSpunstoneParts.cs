using RimWorld;
using Verse;

namespace RimMandrake.TheForge
{
    // FORGE_SPUNSTONE_SOURCES_1: with its setting off, the floatstone door or the spunstone
    // hull (Defs/ThingDefs_Buildings/RM_SpunstoneParts.xml) leaves the architect menu at
    // startup (applies on the next launch). Already-built ones stay. Copied from Cauldron's
    // RM_VexxithDoorGate (5dc8af767).
    [StaticConstructorOnStartup]
    public static class RM_SpunstonePartsGate
    {
        static RM_SpunstonePartsGate()
        {
            Hide("RM_FloatstoneDoor", RM_TheForgeSettings.Active(RM_TheForgeSettings.floatstoneDoorEnabled));
            Hide("RM_SpunstoneHull", RM_TheForgeSettings.Active(RM_TheForgeSettings.spunstoneHullEnabled));
        }

        private static void Hide(string defName, bool enabled)
        {
            if (enabled)
            {
                return;
            }
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (def == null)
            {
                return;
            }
            // DesignationCategoryDef resolves its designator list in an ExecuteWhenFinished
            // queued at ResolveReferences, so this may run before OR after it: null the
            // category (covers before) and drop an already-built designator (covers after).
            DesignationCategoryDef cat = def.designationCategory;
            def.designationCategory = null;
            if (cat != null)
            {
                cat.AllResolvedDesignators.RemoveAll(d => d is Designator_Build b && b.PlacingDef == def);
            }
        }
    }
}
