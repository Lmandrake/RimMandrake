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
            RimMandrake.Shared.PatchApplier.Apply(harmony, Assembly.GetExecutingAssembly(), "RimMandrake.LuminousPigment");
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

    // DESIGN_PASS LP-2 (GLOW_TANK_LIQUID_FEED_1): a dry GlowTank pauses its crop. Cheap reject first: only the
    // cultured crowncarpet def is looked at, and only when it stands in a GlowTank.
    [HarmonyPatch(typeof(RimWorld.Plant), nameof(RimWorld.Plant.GrowthRate), MethodType.Getter)]
    public static class Patch_Plant_GrowthRate_GlowTank
    {
        private static ThingDef cultured;
        private static bool looked;

        public static void Postfix(RimWorld.Plant __instance, ref float __result)
        {
            if (__result <= 0f) return;
            if (!looked)
            {
                looked = true;
                cultured = DefDatabase<ThingDef>.GetNamedSilentFail("RM_CrowncarpetCultured");
            }
            if (cultured == null || __instance.def != cultured || !__instance.Spawned) return;
            if (__instance.Position.GetEdifice(__instance.Map) is Building_GlowTank tank && tank.Parched)
            {
                __result = 0f;
            }
        }
    }
}
