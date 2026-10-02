using HarmonyLib;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1 — the "mishandled" half of the
    // sap-sucker guild's refusal (fever_wood_deep_and_mud_2026-09-23.md §6n:
    // "they still trigger their refusal when frightened or mishandled").
    // RM_CompSapSuckerRefusal already ships the damage half.
    //
    // Seam (RimSage, decompiled 1.6, 2026-10-01):
    //   Verse.AI.Pawn_MindState
    //     internal bool CheckStartMentalStateBecauseRecruitAttempted(Pawn tamer)
    // Its ONLY caller is InteractionWorker_RecruitAttempt.Interacted, in the
    // animal/wild-man branch, on the FAILED roll (right after the
    // "TextMote_TameFail" mote). So this fires on every failed tame, and only
    // on a failed tame — never on a success, never on a prisoner recruit.
    //
    // Postfix, not prefix: the refusal is deterministic and independent of the
    // vanilla manhunter roll inside that method, so __result is deliberately
    // ignored — "Do not ship a random chance of refusal" (fauna roster §2).
    // The comp's own cooldown is shared with the damage trigger.
    [HarmonyPatch(typeof(Pawn_MindState), "CheckStartMentalStateBecauseRecruitAttempted")]
    public static class RM_Patch_SapSuckerMishandle
    {
        public static void Postfix(Pawn_MindState __instance, Pawn tamer)
        {
            if (!RM_FeverWoodSettings.sapSuckerMishandleRefusalEnabled)
            {
                return;
            }

            Pawn pawn = __instance?.pawn;
            if (pawn == null)
            {
                return;
            }

            pawn.GetComp<RM_CompSapSuckerRefusal>()?.NotifyMishandled(tamer);
        }
    }
}
