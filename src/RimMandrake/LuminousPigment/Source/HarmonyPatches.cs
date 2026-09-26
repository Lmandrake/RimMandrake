using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §2.3: RM_DeepfireRefining is hidden (CanStartNow false) until a
    // colonist has seen crowncarpet, when pressGate == Research. The spec's
    // second hook idea (hiding the entry from the research tab's own draw)
    // is flagged there as engine-UNMEASURED, with a documented fallback:
    // "a visible-but-locked project with a red 'needs a mat sighting' line
    // in its description." That fallback -- visible, locked, with a note
    // appended to its tooltip (ResearchProjectDef.GetTip(), RimSage-verified
    // to exist) -- is what ships here; nothing hides the tab entry.
    [StaticConstructorOnStartup]
    public static class HarmonyBootstrap
    {
        static HarmonyBootstrap()
        {
            Harmony harmony = new Harmony("mandrake.rm.luminouspigment");
            harmony.PatchAll(Assembly.GetExecutingAssembly());
        }
    }

    [HarmonyPatch(typeof(ResearchProjectDef))]
    [HarmonyPatch(nameof(ResearchProjectDef.CanStartNow), MethodType.Getter)]
    public static class Patch_ResearchProjectDef_CanStartNow
    {
        public static void Postfix(ResearchProjectDef __instance, ref bool __result)
        {
            if (!__result) return;
            if (__instance.defName != "RM_DeepfireRefining") return;
            if (LuminousPigmentSettings.pressGate != PressGate.Research) return;

            GameComponent_Deepfire gc = GameComponent_Deepfire.Instance;
            if (gc != null && !gc.matSeen)
            {
                __result = false;
            }
        }
    }

    [HarmonyPatch(typeof(ResearchProjectDef), nameof(ResearchProjectDef.GetTip))]
    public static class Patch_ResearchProjectDef_GetTip
    {
        public static void Postfix(ResearchProjectDef __instance, ref string __result)
        {
            if (__instance.defName != "RM_DeepfireRefining") return;
            if (LuminousPigmentSettings.pressGate != PressGate.Research) return;

            GameComponent_Deepfire gc = GameComponent_Deepfire.Instance;
            if (gc != null && !gc.matSeen)
            {
                __result += "\n\nLocked: needs a mat sighting. A colonist must see crowncarpet growing on a shore first.";
            }
        }
    }
}
