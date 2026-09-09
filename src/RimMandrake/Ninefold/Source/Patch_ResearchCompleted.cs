using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // design/Jawa/divine_satiation_engine.md:920: "Research pleases Ohm
    // (bold machine-advance) AND Ozzik (the pride of knowing) -- a shared
    // input, one of the few." Matrix ⑨ Ozzik: "DEEDS + (every advancement
    // feeds him regardless): research completed..."
    //
    // Verified against decompiled source (RimSage), not guessed:
    // `ResearchManager.FinishProject` (Source/RimWorld/ResearchManager.cs:403)
    // is the single call site every completed research project passes
    // through, for the player only -- ResearchManager is Find.ResearchManager,
    // there is no AI-faction instance to filter out.
    // [HarmonyPatch] binds by nameof(), same as the other four hooks --
    // Harmony errors at load if the signature moves.
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
            comp.ApplyDelta(God.Ohm, EventMagnitude.Small,
                "research completed (shared input): " + proj.defName);

            // NINEFOLD_ENGINE_M0_1: first_contact_chains.md ⑨ -- "the first
            // true reach... research completed at a real bench." The doc's
            // alternate trigger ("or the colony's first masterwork") is NOT
            // wired to Patch_ArtCreated here: that hook fires on every piece
            // of art regardless of quality, and using it would fire this
            // chain on the very first tiny sculpture rather than a genuine
            // masterwork -- too loose an approximation to ship.
            comp.TryFirstContact(God.Ozzik);
        }
    }
}
