using System.Collections.Generic;
using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // QUICKTEST_POSTSETUP_CRASH_1 -- NOT a Ninefold feature. This lives here only
    // because Ninefold already loads a Harmony assembly patching this exact
    // method (Patch_ResearchCompleted, same file area) and a second project just
    // to hold one defensive fix was not worth another cold-load cycle tonight.
    //
    // THE BUG (verified against decompiled source, RimSage,
    // RimWorld/ResearchManager.cs:403-410):
    //
    //     public void FinishProject(ResearchProjectDef proj, ...)
    //     {
    //         if (proj.prerequisites != null)
    //             for (int i = 0; i < proj.prerequisites.Count; i++)
    //                 if (!proj.prerequisites[i].IsFinished)
    //                     FinishProject(proj.prerequisites[i], ...);   // recurse
    //         ...
    //         progress[proj] = proj.baseCost;   // marked finished ONLY after the loop
    //     }
    //
    // No cycle or visited-set guard anywhere. A self-referencing prerequisite
    // (proj.prerequisites contains proj itself) is unconditional infinite
    // recursion -> StackOverflowException -> uncatchable, silent process death
    // within seconds, right after a burst of real completions logs normally.
    //
    // WHY AN XML PATCH ALONE DID NOT FIX THIS (measured live, 2026-09-12):
    // `Patches/RRElectricityBasicsSelfPrereq_Fix.xml` (mandrake.rm.patches,
    // loads after petetimessix.researchreinvented.steppingstones) removes the
    // self-referencing <li> during the normal XML-patch pass. A fresh full
    // 592-mod restart with that patch deployed and verified in-mod-folder still
    // showed the LIVE resolved def with prerequisites == [RR_ElectricityBasics]
    // (jawa/get_defs), and start_debug_game_ready still crashed identically
    // (RimWorldWin64 gone, ConnectionResetError, same six-completions-then-silence
    // log shape). Whatever mechanism "Research Reinvented: Stepping Stones" uses
    // to build this self-reference (its own custom `RR.PatchOperationResearchPrereg`
    // PatchOperation, per QUICKTEST_POSTSETUP_CRASH_1.md) evidently re-applies, or
    // applies in the first place, at a point the ordinary per-mod XML patch pass
    // cannot out-order -- not traced further; not needed to, given the fix below.
    //
    // THE FIX: strip any self-referencing prerequisite the FIRST moment
    // FinishProject is entered for a def, before the recursive loop runs, no
    // matter which mod or mechanism put it there and no matter patch load order.
    // A research project cannot legitimately require itself, so this costs no
    // real content for any def, ever. Harmless no-op on every def that doesn't
    // have this bug (i.e. everything except RR_ElectricityBasics today).
    [HarmonyPatch(typeof(ResearchManager), nameof(ResearchManager.FinishProject))]
    public static class Patch_ResearchManager_NoSelfPrereq
    {
        [HarmonyPrefix]
        public static void Prefix(ResearchProjectDef proj)
        {
            List<ResearchProjectDef> prereqs = proj?.prerequisites;
            if (prereqs == null || prereqs.Count == 0) return;
            int removed = prereqs.RemoveAll(p => p == proj);
            if (removed > 0)
            {
                Log.Warning("[RimMandrake.Ninefold] QUICKTEST_POSTSETUP_CRASH_1 guard: "
                    + "stripped " + removed + " self-referencing prerequisite entr"
                    + (removed == 1 ? "y" : "ies") + " from " + proj.defName
                    + " (would otherwise infinite-recurse ResearchManager.FinishProject "
                    + "and crash the process silently).");
            }
        }
    }
}
