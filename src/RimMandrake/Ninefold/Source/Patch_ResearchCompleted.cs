using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // design/Jawa/divine_satiation_engine.md, Matrix ⑨ Ozzik: "DEEDS +
    // (every advancement feeds him regardless): research completed..."
    //
    // Verified against decompiled source (RimSage), not guessed:
    // `ResearchManager.FinishProject` (Source/RimWorld/ResearchManager.cs:403)
    // is the single call site every completed research project passes
    // through, for the player only -- ResearchManager is Find.ResearchManager,
    // there is no AI-faction instance to filter out.
    // (No compile-time delegate proof here, unlike the other four hooks --
    // ResearchManager.FinishProject is an instance method on a sealed class
    // with no visible public constructor guarantee, and instantiating a
    // throwaway ResearchManager just to bind a delegate is not worth the
    // risk. [HarmonyPatch] with nameof() still catches an outright rename;
    // Harmony's own PatchAll logs a load-time error if the signature moves.)
    //
    // 🔴 FinishProject recurses into unfinished prerequisites (calls itself
    // per prerequisite before finishing `proj` itself), and has no
    // `IsFinished` guard at entry -- so a deep chain (a quest reward, dev-mode
    // finish, or ApplyKnowledge) fires this Postfix once per node completed,
    // not once per player action. The Prefix/__state pair below only applies
    // the delta for a project that actually flipped false->true this call,
    // so a re-entrant call on an already-finished project (Harmony can also
    // re-run a Postfix on recursive self-calls) doesn't double-count.
    [HarmonyPatch(typeof(ResearchManager), nameof(ResearchManager.FinishProject))]
    public static class Patch_ResearchCompleted
    {
        [HarmonyPrefix]
        public static void Prefix(ResearchProjectDef proj, out bool __state)
        {
            __state = proj != null && proj.IsFinished;
        }

        [HarmonyPostfix]
        public static void Postfix(ResearchProjectDef proj, bool __state)
        {
            if (proj == null || __state || !proj.IsFinished) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Ozzik, EventMagnitude.Large,
                "research completed: " + proj.defName);
        }
    }
}
