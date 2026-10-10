using System.Collections;
using System.Reflection;
using Verse;

namespace RimMandrake.StarWars.Armoury
{
    // SHIP_ALLOY_FORGE_1 — applies RSW_ArmourySettings.durasteelAlloyEnabled to the
    // alloy forge. Patches/RSW_AlloyForge_Durasteel.xml adds RSW_AlloyDurasteel
    // (steel + zersium -> RSW_Durasteel) to VFEFactory_AutomatedAlloyForge's
    // processor; with the toggle off this removes it from that list at startup.
    //
    // PipeSystem (VFE) types are not referenced by this assembly, so the process
    // def and the comp's `processes` list are reached by reflection on their XML
    // field names. Every lookup is silent-fail: no VFE Factory, or no
    // RSW_Durasteel yet (the patch is conditional on it), means nothing to do.
    [StaticConstructorOnStartup]
    public static class RSW_AlloyForgeDurasteel
    {
        static RSW_AlloyForgeDurasteel()
        {
            Apply();
        }

        public static void Apply()
        {
            if (RSW_ArmourySettings.durasteelAlloyEnabled) return;

            var processType = GenTypes.GetTypeInAnyAssembly("PipeSystem.ProcessDef");
            if (processType == null) return;
            var process = GenDefDatabase.GetDefSilentFail(processType, "RSW_AlloyDurasteel", false);
            var forge = DefDatabase<ThingDef>.GetNamedSilentFail("VFEFactory_AutomatedAlloyForge");
            if (process == null || forge == null || forge.comps == null) return;

            foreach (var props in forge.comps)
            {
                var f = props.GetType().GetField("processes",
                    BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                if (f == null) continue;
                var list = f.GetValue(props) as IList;
                if (list != null && list.Contains(process)) list.Remove(process);
            }
        }
    }
}
