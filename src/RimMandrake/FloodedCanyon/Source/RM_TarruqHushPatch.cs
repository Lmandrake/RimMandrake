using HarmonyLib;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_GPT_ENRICHMENT_1 §2, beat 3 — "tarruq calls stop".
    //
    // The cast bible's mechanism verbatim: "an ambient call keyed to tarruq
    // presence, gated OFF by the flood map component's pre-chime phase — one
    // boolean read on machinery that exists." Pawn_CallTracker.TryDoCall
    // (private, read in RimSage 2026-10-01) is the only idle-call entry;
    // skipping it silences the idle call and nothing else (a hurt tarruq still
    // cries out — DoCall's aggressive path and wound/death sounds are not
    // routed through TryDoCall).
    //
    // The gate is live now; the call it gates is owed audio (the tarruq ships
    // with no soundCall of its own yet — CRACKEDLANDS_FIVE_BEATS_AUDIO_1).
    // ════════════════════════════════════════════════════════════════════
    [HarmonyPatch(typeof(Pawn_CallTracker), "TryDoCall")]
    public static class RM_TarruqHushPatch
    {
        public static bool Prefix(Pawn_CallTracker __instance)
        {
            Pawn pawn = __instance.pawn;
            if (pawn == null || pawn.def != RM_FloodedCanyonDefOf.RM_Tarruq || !pawn.Spawned)
            {
                return true;
            }
            RM_MapComponent_CanyonFlood flood = pawn.Map.GetComponent<RM_MapComponent_CanyonFlood>();
            return flood == null || !flood.TarruqSilenced;
        }
    }
}
