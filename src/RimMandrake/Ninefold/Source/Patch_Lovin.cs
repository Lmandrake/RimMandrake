using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_ENGINE_M0_1 (Ishko/Oomo research pass, 2026-09-18).
    // divine_satiation_engine.md §3③: "sex/lovin' pleases him ('the passing
    // of waters between each other' -- every coupling is devotional)".
    // This is also the trigger first_contact_chains.md ③ names for Oomo's
    // first-contact SHOCK: "the first night two Jawa share a bunk." Neither
    // half of Oomo's ambient satiation nor his first-contact chain had an
    // event hook before this pass -- a genuine gap, not just a first-contact
    // one (see the FirstContactCorpus/GameComponent_Ninefold comments this
    // pass also updates).
    //
    // Verified against decompiled source (RimSage): the actual completion of
    // a lovin' act happens inside JobDriver_Lovin.MakeNewToils()'s second
    // toil, in an AddFinishAction anonymous delegate
    // (Source/RimWorld/JobDriver_Lovin.cs) -- not a named method, so not a
    // clean Harmony target. But that same delegate unconditionally calls
    // `Find.HistoryEventsManager.RecordEvent(new HistoryEvent(
    // HistoryEventDefOf.GotLovin, pawn.Named(...)))` (line 107) for EVERY
    // completed coupling, spouse or not -- the immediately following line
    // also raises the more specific GotLovin_Spouse/GotLovin_NonSpouse, so
    // filtering on the base GotLovin here catches both without double
    // counting (we ignore the spouse-specific pair entirely).
    // HistoryEventsManager.RecordEvent(HistoryEvent, bool = true)
    // (Source/RimWorld/HistoryEventsManager.cs) is public, has exactly one
    // overload, and is the same "history event ledger" choke point vanilla's
    // own ideoligion precepts read from (IdeoUtility.Notify_HistoryEvent
    // runs from inside this same call) -- a stable, well-trodden hook, not
    // a private toil internal.
    [HarmonyPatch(typeof(HistoryEventsManager), nameof(HistoryEventsManager.RecordEvent))]
    public static class Patch_Lovin
    {
        [HarmonyPostfix]
        public static void Postfix(HistoryEvent historyEvent)
        {
            if (historyEvent.def != HistoryEventDefOf.GotLovin) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Oomo, EventMagnitude.Small,
                "waters passed between two of you");

            // NINEFOLD_ENGINE_M0_1: Oomo's first-contact chain fires on this
            // same first-coupling trigger (first_contact_chains.md ③).
            comp.TryFirstContact(God.Oomo);
        }
    }
}
